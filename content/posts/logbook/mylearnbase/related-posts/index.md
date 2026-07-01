+++
title = "Content-based related posts"
slug = "related-posts"
date = 2026-06-30
draft = false

[taxonomies]
tags = ["navigation", "ux", "frontend"]
+++

## What does this feature do?

At the foot of every post, up to two "Related" links point to the posts closest
in content to the one you are reading. "Closest in content" is measured from the
words each post uses, with each post's title and headings counted more heavily
than its body, so the links lead to posts on the same subject rather than to
whichever post happened to be published just before or after. When no similarity
data is available, the two slots fall back to the nearest posts by date, labelled
"Previous" and "Next" instead of "Related".

## Why was it added now?

The post-to-post navigation had only just been added, and its first version was
chronological: it linked to the posts nearest by date within the same section.
Chronological adjacency is arbitrary, though. The post that happens to sit next
to this one by date is not necessarily about anything related to it, so a reader
who reaches the end of a post is handed two links chosen by calendar accident
rather than by subject.

Content relatedness is what those links were reaching for in the first place: at
the end of a post, the most useful thing to offer is more on the same subject.
Replacing the ordering was a natural follow-up while the navigation was still
fresh, and it was cheap to do because the site already carried a small Python
tooling setup, so similarity could be computed from post text with the standard
library alone, with no new dependencies to install in the build.

## What's in scope (and what's not)?

**In:** relatedness computed from each post's own text, the top two matches shown
under every post, and a chronological fallback when no match data is present.

**Not in:**

- Shared-tags relatedness. Tempting, but the tagging on this site is deliberately
  loose and gets reworked; leaning on it would make the Related links churn every
  time tags change. Similarity is computed from the prose only, never from tags.
- Hand-picked related links. Choosing neighbours by hand does not scale as the
  catalogue grows, and it is exactly the manual step this feature removes.

## How do we know it works?

The quickest check is the bottom of this very post: the two "Related" links there
were produced by this feature, from the text of this post and its neighbours.
Follow one and you land on a post that shares its subject, not one that merely
shares a publication week.

The pieces that make that happen:

[`scripts/compute-related.py:179`](https://github.com/RustWright/mylearnbase/blob/908f9306b37dc80e2259c98e4d1db596b8085769/scripts/compute-related.py#L179) at `908f930`
> `        score = sum(contrib.values())`
>
> Each post becomes a vector of its words, weighted so rarer, more distinctive words count for more and a post's title and headings count more than its body. Two posts' relatedness is the overlap of those vectors (a cosine score). It is computed from text only, never from tags, so reworking tags never disturbs the Related links.

[`build.sh:30`](https://github.com/RustWright/mylearnbase/blob/908f9306b37dc80e2259c98e4d1db596b8085769/build.sh#L30) at `908f930`
> `python3 scripts/compute-related.py`
>
> Relatedness is computed once at build time, just before the site is generated, and written to related.json. That file is a build artifact regenerated on every deploy, the same treatment the search index gets, so it never goes stale and is never committed.

[`templates/post.html:177`](https://github.com/RustWright/mylearnbase/blob/908f9306b37dc80e2259c98e4d1db596b8085769/templates/post.html#L177) at `908f930`
> `    {%- set related_map = load_data(path="related.json", required=false) -%}`
>
> The template reads the precomputed related.json rather than computing anything itself. required=false is deliberate: when the file is absent (a plain local preview), the read yields nothing instead of failing the build. This is the seam that lets the scoring method change without touching the template.

[`templates/post.html:179`](https://github.com/RustWright/mylearnbase/blob/908f9306b37dc80e2259c98e4d1db596b8085769/templates/post.html#L179) at `908f930`
> `    {%- if related_map and page.relative_path in related_map -%}`
>
> The one decision the template makes: if related.json loaded and this post has an entry, render its Related links; otherwise fall through to the chronological Previous/Next walk below. That guard is why a post missing from the data, or a preview with no data at all, still gets working navigation.

## What's worth remembering or doing next?

- The related-posts data is a build artifact, regenerated from scratch on every
  deploy and never committed, the same way the search index is. A plain local
  `zola serve` does not regenerate it, so previews show the chronological
  "Previous/Next" fallback rather than the real Related links; run the full build
  to see them.
- A meaning-based upgrade (static embeddings) is the planned next step if the
  word-overlap matches ever start reading weak on the real catalogue. Right now
  they read fine, so it stays on word overlap. Revisit when the catalogue grows
  more varied in vocabulary.
- How this actually works, why comparing the words two posts share is enough to
  call them related, and why that holds up better for a single author than it
  would across many, is a strong candidate for an interactive concepts demo. The
  similarity script already records the specific shared words behind each match,
  which is most of the raw material such a demo would visualize.
