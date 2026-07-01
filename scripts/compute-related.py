#!/usr/bin/env python3
"""Compute content-based "related posts" via TF-IDF + cosine similarity.

Reads every published post under content/posts/, builds a TF-IDF vector for
each (title and headings up-weighted), and writes the top-K most similar
neighbours per post to related.json at the repo root.

related.json is a BUILD ARTIFACT, treated like the Pagefind index:
  - build.sh runs this before `zola build`, so it is regenerated every build
    and never goes stale (it is gitignored, not committed).
  - templates/post.html reads it via load_data(required=false) to render the
    "Related" nav, and falls back to chronological order when it is missing
    (e.g. plain `zola serve` in dev) or a post is absent from it.

Design notes:
  - Pure standard library, no third-party deps, so it runs in Cloudflare's CI
    image with no `pip install` step.
  - Similarity is computed from TEXT ONLY (title + headings + body) and never
    from tags: the tagging strategy is deliberately volatile, so leaning on it
    for relatedness would make the nav churn whenever tags are reworked.
  - Keys and neighbour paths are content-relative POSIX paths INCLUDING the
    `index.md` for page bundles, e.g. "posts/logbook/mylearnbase/site-search/
    index.md" — this is exactly what Zola's page.relative_path / get_page expect.
  - The output records the shared terms that drove each match, so a future
    concepts post (or a sceptical human) can see *why* two posts are related.

The TF-IDF -> model2vec upgrade path (Cycle 5 Task 3 decision gate) stays a
drop-in: only `vectorize()`/`similarity()` change; the I/O contract above and
the JSON shape are the stable seam.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # scripts/ -> repo root
CONTENT = ROOT / "content" / "posts"
OUT = ROOT / "related.json"

# --- knobs (settle here, not in code paths) ---------------------------------
TOP_K = 4              # neighbours stored per post (post.html renders the top 2)
TITLE_WEIGHT = 3       # title tokens counted this many times
HEADING_WEIGHT = 2     # markdown heading tokens counted this many times
MIN_SCORE = 0.03       # drop neighbours at or below this cosine score
STEM_PLURALS = True    # collapse simple trailing-'s' plurals (tools -> tool)
TERMS_PER_PAIR = 4     # shared terms recorded per neighbour (interpretability)

STOPWORDS = {
    "a", "about", "above", "after", "again", "all", "also", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "could", "did", "do",
    "does", "doing", "done", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "him", "his", "how", "i", "if", "in", "into", "is", "it", "its", "just",
    "let", "like", "made", "make", "many", "me", "more", "most", "much", "my",
    "no", "nor", "not", "now", "of", "off", "on", "once", "one", "only", "or",
    "other", "our", "out", "over", "own", "per", "same", "she", "should", "so",
    "some", "still", "such", "than", "that", "the", "their", "them", "then",
    "there", "these", "they", "thing", "things", "this", "those", "through",
    "to", "too", "under", "until", "up", "use", "used", "using", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "why",
    "will", "with", "would", "you", "your", "yet", "get", "got", "into", "via",
    "want", "wanted", "need", "needed", "well", "way", "ways",
    # contraction fragments left behind after tokenizing (e.g. "I'll" -> "ll")
    "ll", "ve", "re", "im", "isn", "didn", "doesn", "don", "won", "wasn",
    "aren", "wouldn", "couldn", "shouldn", "hasn", "haven", "wont", "cant",
    # ordinal fragments: the regex can't start on a digit, so "19th"/"21st"
    # tokenize to just "th"/"st"/"nd"/"rd" — noise, not words.
    "th", "st", "nd", "rd",
}

TOKEN_RE = re.compile(r"[a-z][a-z0-9-]*[a-z0-9]|[a-z]")
FRONTMATTER_RE = re.compile(r"\A\s*\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.S)
TITLE_RE = re.compile(r'^\s*title\s*=\s*"(.*?)"', re.M)
DRAFT_RE = re.compile(r"^\s*draft\s*=\s*true\b", re.M)
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.M)
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
SHORTCODE_RE = re.compile(r"{[{%].*?[%}]}", re.S)
HTML_TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")     # [text](url) -> text
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")     # drop images entirely
URL_RE = re.compile(r"https?://\S+")


def stem(token: str) -> str:
    """Light plural collapse only. Protects -ss/-us/-is endings (class, dioxus,
    analysis) and maps -ies -> -y (dependencies -> dependency)."""
    if not STEM_PLURALS or len(token) <= 4:
        return token
    if token.endswith(("ss", "us", "is")):
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith("s"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    text = text.lower()
    out = []
    for m in TOKEN_RE.finditer(text):
        tok = m.group(0).strip("-")
        if len(tok) < 2 or tok in STOPWORDS:
            continue
        tok = stem(tok)
        if tok in STOPWORDS:
            continue
        out.append(tok)
    return out


def parse_post(path: Path) -> tuple[str, list[str]] | None:
    """Return (title, weighted token list) or None if the file should be skipped."""
    raw = path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.match(raw)
    frontmatter = fm_match.group(1) if fm_match else ""
    if DRAFT_RE.search(frontmatter):
        return None
    title_match = TITLE_RE.search(frontmatter)
    title = title_match.group(1) if title_match else path.stem

    body = raw[fm_match.end():] if fm_match else raw
    headings = " ".join(HEADING_RE.findall(body))

    body = IMAGE_RE.sub(" ", body)
    body = CODE_FENCE_RE.sub(" ", body)
    body = INLINE_CODE_RE.sub(" ", body)
    body = SHORTCODE_RE.sub(" ", body)
    body = LINK_RE.sub(r"\1", body)
    body = URL_RE.sub(" ", body)
    body = HTML_TAG_RE.sub(" ", body)

    tokens = tokenize(body)
    tokens += tokenize(headings) * HEADING_WEIGHT
    tokens += tokenize(title) * TITLE_WEIGHT
    return title, tokens


def discover_posts() -> list[Path]:
    posts = []
    for p in sorted(CONTENT.rglob("*.md")):
        if p.name == "_index.md":
            continue
        if any(part.startswith(".") for part in p.relative_to(ROOT).parts):
            continue  # skip dotfiles like .frontmatter-template.md
        posts.append(p)
    return posts


def build_vectors(docs: dict[str, Counter]) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """TF-IDF with sublinear tf and smoothed idf, L2-normalized per document."""
    n = len(docs)
    df: Counter = Counter()
    for counts in docs.values():
        df.update(counts.keys())
    idf = {term: math.log((1 + n) / (1 + d)) + 1.0 for term, d in df.items()}

    vectors: dict[str, dict[str, float]] = {}
    for key, counts in docs.items():
        vec = {t: (1.0 + math.log(c)) * idf[t] for t, c in counts.items()}
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        vectors[key] = {t: w / norm for t, w in vec.items()}
    return vectors, idf


def neighbours(key: str, vectors: dict[str, dict[str, float]], titles: dict[str, str]):
    base = vectors[key]
    scored = []
    for other, ovec in vectors.items():
        if other == key:
            continue
        # cosine == dot product (vectors are already L2-normalized)
        small, large = (base, ovec) if len(base) <= len(ovec) else (ovec, base)
        contrib = {t: small[t] * large[t] for t in small if t in large}
        score = sum(contrib.values())
        if score <= MIN_SCORE:
            continue
        terms = [t for t, _ in sorted(contrib.items(), key=lambda kv: kv[1], reverse=True)[:TERMS_PER_PAIR]]
        scored.append({"path": other, "title": titles[other], "score": round(score, 4), "terms": terms})
    scored.sort(key=lambda d: d["score"], reverse=True)
    return scored[:TOP_K]


def main() -> int:
    paths = discover_posts()
    docs: dict[str, Counter] = {}
    titles: dict[str, str] = {}
    for p in paths:
        parsed = parse_post(p)
        if parsed is None:
            continue
        key = p.relative_to(CONTENT.parent).as_posix()   # content-relative, incl. index.md
        title, tokens = parsed
        docs[key] = Counter(tokens)
        titles[key] = title

    vectors, _ = build_vectors(docs)
    related = {key: neighbours(key, vectors, titles) for key in docs}
    OUT.write_text(json.dumps(related, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Human-readable report (stdout; the JSON is the machine output).
    print(f"compute-related: {len(docs)} posts, "
          f"{sum(len(v) for v in docs.values())} weighted tokens, wrote {OUT.name}")
    if "--verbose" in sys.argv:
        for key in sorted(related):
            print(f"\n{titles[key]}\n  ({key})")
            for n in related[key]:
                print(f"    {n['score']:.3f}  {n['title']}")
                print(f"           shared: {', '.join(n['terms'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
