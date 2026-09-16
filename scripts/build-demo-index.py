#!/usr/bin/env python3
"""Derive the demo -> parent-post mapping and write static/demos/_shared/demos.json.

Every demo under static/demos/ is embedded by exactly one post, through an
existing `demo(name=..., caption=..., height=...)` shortcode call. That call
already carries everything a gallery or a back-link needs: which post owns the
demo, a hand-written caption that reads as "what you can do here", and the
height the author judged the demo needs. So the mapping is DERIVED from the
content, never hand-authored.

Why derived: a hand-written mapping (data/demos.toml and friends) goes stale the
moment a demo moves or a post is renamed, and it goes stale SILENTLY — the back
-link still renders, it just points somewhere wrong. Deriving it means the file
cannot disagree with the posts, and the mismatches become a build-time report
instead of a reader's 404.

demos.json is a BUILD ARTIFACT on the related.json model: gitignored, rebuilt by
build.sh before every `zola build`, and read by consumers that tolerate its
absence (templates via load_data(required=false); demo-chrome.js via a fetch
whose failure is caught). A plain `zola serve` therefore works without it.

Two consumers, one file:
  1. templates/playground.html  — builds the gallery.
  2. static/demos/_shared/demo-chrome.js — injects the standalone back-link bar.

The second is why post URLs are resolved HERE rather than left as content paths
for Tera's get_page() to resolve (the related.json approach). Runtime JavaScript
has no access to Zola's page graph, so the URL has to be in the file.

Resolving URLs in Python means duplicating Zola's routing rule, which is the
risky part of this script. Two things keep it honest:
  - Every post in this repo declares an explicit `slug =`, so the rule is just
    "section directories + slug" with no title-slugification guesswork.
  - `--verify <dir>` re-reads the emitted file after `zola build` and asserts
    every URL exists in the built output. Derivation that drifts fails the
    build loudly instead of shipping back-links that 404.

  Usage:
    python3 scripts/build-demo-index.py            # generate
    python3 scripts/build-demo-index.py --verify public   # assert, post-build
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # scripts/ -> repo root
CONTENT = ROOT / "content" / "posts"
DEMOS = ROOT / "static" / "demos"
OUT = DEMOS / "_shared" / "demos.json"
POSTERS = ROOT / "static" / "img" / "demos"

# Directories under static/demos/ that are not demos.
NOT_A_DEMO = {"_shared"}

# Above this many bytes a demo is "heavy": the gallery must not preview it live,
# and it needs a captured poster instead. ONE rule decides both, here, so adding
# a demo never means making a per-demo judgment call — the build measures it and
# scripts/capture-demo-posters.py captures whatever came out heavy.
#
# Derived from measurement, and the gap it sits in is enormous: the nine light
# demos top out at 26KB, while the three heavy ones are 588-610KB (two WASM
# bundles and one 564KB search corpus).
HEAVY_BYTES = 150_000

# Anything landing inside this band of the threshold is reported rather than
# silently bucketed. Nothing does today; the point is that the first demo to
# land in the gap prompts a look at the number instead of inheriting it.
NEAR_THRESHOLD = (HEAVY_BYTES // 2, HEAVY_BYTES * 2)

# A demo page carrying this is a design artifact rather than a reader-facing
# demo. One switch, two consequences: out of search results, and out of the
# gallery. It still gets a demos.json entry, so its back-link bar works.
NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', re.I)

FRONTMATTER_RE = re.compile(r"\A\s*\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.S)
TITLE_RE = re.compile(r'^\s*title\s*=\s*"(.*?)"', re.M)
SLUG_RE = re.compile(r'^\s*slug\s*=\s*"(.*?)"', re.M)
DATE_RE = re.compile(r"^\s*date\s*=\s*(\S+)", re.M)
DRAFT_RE = re.compile(r"^\s*draft\s*=\s*true\b", re.M)

# Matches a live shortcode call, one per line.
#
# GREEDY argument capture is deliberate. Captions contain parentheses — the
# TF-IDF post's caption reads "...by raw count (TF), by rarity ... (IDF)..." —
# so a non-greedy `\((.*?)\)` stops at the first inner ")" and silently drops
# every argument after it, including the caption and the height. Greedy runs to
# the last ")" before the closing braces, which is the real end of the call.
#
# The escaped form `{{/* demo() */}}` (used in the workflows posts, which
# document the shortcode rather than invoke it) is excluded for free: after
# "{{" this pattern requires optional whitespace then "demo", and the escape
# puts "/*" there instead.
CALL_RE = re.compile(r"\{\{-?\s*demo\((.*)\)\s*-?\}\}")

# Splits a shortcode argument list on top-level commas only, so a comma inside
# a quoted caption does not split the arguments.
ARG_RE = re.compile(r'(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|[^,]+?)(?=\s*,\s*\w+\s*=|\s*$)')

# The <title> of the demo page itself — a better gallery tile label than the
# path, and already written by whoever built the demo.
HTML_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)


def parse_args(arglist: str) -> dict:
    """Parse `name="x", height=900, wide=true` into a dict of Python values."""
    out = {}
    for key, raw in ARG_RE.findall(arglist):
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            out[key] = raw[1:-1].replace('\\"', '"')
        elif raw in ("true", "false"):
            out[key] = raw == "true"
        else:
            try:
                out[key] = int(raw)
            except ValueError:
                out[key] = raw
    return out


def post_url(md: Path, slug: str) -> str:
    """Zola's URL for a post file: section directories under content/posts + slug.

    Page bundles (a directory holding index.md) contribute their PARENT as the
    section path, because the bundle directory is the page, not a section.
    Verified against the built output for both shapes:
      content/posts/concepts/tf-idf.md                      -> /posts/concepts/tf-idf/
      content/posts/logbook/mylearnbase/reader-controls/index.md
                                                            -> /posts/logbook/mylearnbase/reader-controls/
    """
    holder = md.parent.parent if md.name == "index.md" else md.parent
    section = holder.relative_to(CONTENT).as_posix()
    section = "" if section == "." else section + "/"
    return f"/posts/{section}{slug}/"


def collect_posts() -> tuple[list[dict], list[str]]:
    """Every demo() call in content/posts, resolved to its parent post."""
    calls, problems = [], []
    for md in sorted(CONTENT.rglob("*.md")):
        if md.name.startswith("."):          # .frontmatter-template.md
            continue
        text = md.read_text(encoding="utf-8")
        fm = FRONTMATTER_RE.match(text)
        if not fm:
            continue
        head, body = fm.group(1), text[fm.end():]

        found = CALL_RE.findall(body)
        if not found:
            continue

        slug_m = SLUG_RE.search(head)
        title_m = TITLE_RE.search(head)
        if not slug_m:
            problems.append(f"{md.relative_to(ROOT)}: embeds a demo but has no slug =")
            continue

        is_draft = bool(DRAFT_RE.search(head))
        date_m = DATE_RE.search(head)
        # enumerate: the order demos appear in the post is the author's own
        # narrative order, and the gallery and project pages both follow it.
        for position, arglist in enumerate(found):
            args = parse_args(arglist)
            if "name" not in args:
                problems.append(f"{md.relative_to(ROOT)}: demo() call with no name=")
                continue
            calls.append({
                "name": args["name"].strip("/"),
                "caption": args.get("caption", ""),
                "height": args.get("height", 480),
                "wide": bool(args.get("wide", False)),
                "post_url": post_url(md, slug_m.group(1)),
                "post_title": title_m.group(1) if title_m else slug_m.group(1),
                "post_date": (date_m.group(1) if date_m else ""),
                "post_draft": is_draft,
                "source": md.relative_to(ROOT).as_posix(),
                "position": position,
            })
    return calls, problems


def collect_demos() -> dict[str, dict]:
    """Demo directories on disk -> title, byte weight, and listed/heavy flags."""
    out = {}
    for index in sorted(DEMOS.rglob("index.html")):
        name = index.parent.relative_to(DEMOS).as_posix()
        if name.split("/")[0] in NOT_A_DEMO:
            continue
        html = index.read_text(encoding="utf-8", errors="replace")
        m = HTML_TITLE_RE.search(html)
        # Whole-bundle weight, because the gallery's question is "what does
        # previewing this cost a visitor", and that is the WASM blob or the
        # corpus, not the HTML.
        size = sum(f.stat().st_size for f in index.parent.rglob("*") if f.is_file())
        out[name] = {
            "title": m.group(1).strip() if m else name,
            "bytes": size,
            "heavy": size >= HEAVY_BYTES,
            "listed": not NOINDEX_RE.search(html),
            "hash": dir_hash(index.parent),
        }
    return out


def dir_hash(d: Path) -> str:
    """Content hash of a demo bundle, used to content-address its poster.

    Covers file paths as well as bytes, so a renamed or deleted file changes the
    hash too. Demos are self-contained bundles, so this is the whole input to
    what a screenshot of the demo would show.
    """
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(d).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


def poster_name(name: str, digest: str) -> str:
    """Poster filename for a demo bundle. The hash is IN the filename on purpose.

    A poster is therefore only ever found when it was built from exactly the
    bytes currently on disk. Edit a demo and the expected file stops existing,
    so the gallery silently falls back to the drawn card and the build says the
    poster needs recapturing. A stale screenshot cannot be displayed — which is
    stronger than the résumé PDF's hash check, where drift warns but the stale
    file still ships. Changing the filename also busts any CDN cache for free.
    """
    return f"{name.replace('/', '-')}.{digest}.webp"


def generate() -> int:
    calls, problems = collect_posts()
    on_disk = collect_demos()

    by_name: dict[str, dict] = {}
    duplicates = []
    for c in calls:
        if c["name"] in by_name:
            duplicates.append(f"{c['name']}: also embedded by {c['source']}")
            continue
        by_name[c["name"]] = c

    broken = sorted(c["name"] for c in calls if c["name"] not in on_disk)
    orphans = sorted(n for n in on_disk if n not in by_name)
    draft_parented = sorted(n for n, c in by_name.items() if c["post_draft"])

    entries = []
    for name, meta in on_disk.items():
        call = by_name.get(name)
        entry = {
            "name": name,
            "url": f"/demos/{name}/",
            "title": meta["title"],
            "caption": call["caption"] if call else "",
            "height": call["height"] if call else 480,
            "wide": call["wide"] if call else False,
            "bytes": meta["bytes"],
            "heavy": meta["heavy"],
            "hash": meta["hash"],
            # Set only when the hash-named file is actually on disk, so the
            # template needs no staleness logic of its own: a poster it can see
            # is current by construction, and its absence means "draw the card".
            "poster": (f"/img/demos/{poster_name(name, meta['hash'])}"
                       if (POSTERS / poster_name(name, meta["hash"])).exists() else None),
            "listed": meta["listed"],
            "position": call["position"] if call else 0,
            "post": None,
        }
        # A draft parent is deliberately omitted rather than flagged. demos.json
        # is served publicly, so recording an unpublished post's title and URL
        # would leak it; and the link would 404 anyway. The consumer sees an
        # entry with no parent and renders brand-only chrome.
        if call and not call["post_draft"]:
            entry["post"] = {
                "url": call["post_url"],
                "title": call["post_title"],
                "date": call["post_date"],
            }
        entries.append(entry)

    # Newest parent first; parentless demos last. The gallery may re-sort, but
    # a deterministic order keeps the artifact diffable.
    # Within a post, keep the order the demos appear in it. Sorting by name here
    # (as this once did) showed the SVG post's demos as build/path/scale when the
    # post tells them as scale/path/build, and would make "the lead demo of a
    # post" — what the project pages show — an alphabetical accident.
    entries.sort(key=lambda e: (e["post"] is None, -_date_key(e), e["position"], e["name"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Two shapes of the same records. `demos` is the flat lookup demo-chrome.js
    # needs (pathname -> entry); `groups` is the gallery's render order. The
    # redundancy is deliberate and safe precisely because the file is generated:
    # the two views are written from one list in one pass and cannot disagree.
    OUT.write_text(
        json.dumps({"demos": entries, "groups": build_groups(entries)}, indent=2) + "\n",
        encoding="utf-8",
    )

    linked = sum(1 for e in entries if e["post"])
    heavy = sum(1 for e in entries if e["heavy"])
    unlisted = sum(1 for e in entries if not e["listed"])
    postered = sum(1 for e in entries if e["poster"])
    print(f"Demo index: {len(entries)} demos on disk, {linked} linked to a published post, "
          f"{heavy} heavy ({postered} with a current poster), {unlisted} unlisted.")

    # A heavy demo with no current poster still renders — it falls back to the
    # drawn card — so this has to be said out loud or it is invisible.
    needs_poster = sorted(e["name"] for e in entries
                          if e["heavy"] and e["listed"] and not e["poster"])
    near = sorted(f"{e['name']} ({_size_label(e['bytes'])})" for e in entries
                  if NEAR_THRESHOLD[0] <= e["bytes"] <= NEAR_THRESHOLD[1])

    for label, items in (
        ("BROKEN EMBED (post references a demo that does not exist)", broken),
        ("duplicate embed (a demo embedded by more than one post)", duplicates),
        ("orphan (demo on disk that no post embeds)", orphans),
        ("draft parent (demo shown without a back-link)", draft_parented),
        ("no current poster — run scripts/capture-demo-posters.py", needs_poster),
        (f"near the {HEAVY_BYTES // 1024}KB heavy threshold — worth reviewing the cutoff", near),
        ("frontmatter", problems),
    ):
        for item in items:
            print(f"  {label}: {item}")

    if broken:
        # Fail: a post on the live site renders an empty iframe, Zola cannot see
        # it (the shortcode builds the src at render time), and nothing else in
        # the pipeline will ever notice. Orphans and draft parents are expected
        # states, so they only warn.
        print("error: broken demo embeds — fix the name= or add the demo.", file=sys.stderr)
        return 1
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


def _size_label(n: int) -> str:
    return f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{round(n / 1024)} KB"


def build_groups(entries: list[dict]) -> list[dict]:
    """Gallery rows, one per parent post.

    The gallery groups rather than laying every tile in one flat grid because
    the collection is lopsided: two posts own three demos each. Flat, the page
    opens with three near-identical SVG tiles followed by three near-identical
    TF-IDF tiles, and reads as repetition. Grouped, each post reads as one idea
    approached from several angles — which is what it is.

    Unlisted demos are dropped here rather than filtered in the template, so
    "noindex" means one thing in one place.
    """
    order: list[str] = []
    groups: dict[str, dict] = {}
    for e in entries:
        if not e["listed"]:
            continue
        key = e["post"]["url"] if e["post"] else ""
        if key not in groups:
            groups[key] = {
                "title": e["post"]["title"] if e["post"] else "No write-up yet",
                "url": e["post"]["url"] if e["post"] else None,
                "demos": [],
            }
            order.append(key)
        groups[key]["demos"].append(e)
    order.sort(key=lambda k: k == "")      # stable: the parentless row goes last
    return [groups[k] for k in order]


def _date_key(entry: dict) -> int:
    # [:10] because Zola dates may carry a time ("2026-06-25T12:00:00", as the
    # site-search post does), and int() on the whole string raises.
    d = (entry.get("post") or {}).get("date", "")[:10]
    return int(d.replace("-", "")) if d[:4].isdigit() else 0


def verify(built: Path) -> int:
    """Assert every URL in demos.json resolves in the built site."""
    if not OUT.exists():
        print(f"error: {OUT.relative_to(ROOT)} missing — run without --verify first.", file=sys.stderr)
        return 1
    entries = json.loads(OUT.read_text(encoding="utf-8"))["demos"]
    missing = []
    for e in entries:
        for label, url in (("demo", e["url"]), ("post", (e["post"] or {}).get("url"))):
            if not url:
                continue
            if not (built / url.strip("/") / "index.html").exists():
                missing.append(f"{e['name']}: {label} URL {url} not in {built}/")
    if missing:
        print("error: demos.json points at URLs the build did not produce:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("       The back-links would 404. Check post_url() against Zola's routing.", file=sys.stderr)
        return 1
    print(f"Verified: all {len(entries)} demo entries resolve in {built}/.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        sys.exit(verify(Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "public"))
    sys.exit(generate())
