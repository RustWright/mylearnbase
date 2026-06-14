# Zola Theme Research — Steal-List

**Research date:** 2026-06-14 (Cycle 3, Phase R)
**Goal:** identify features from other Zola themes worth porting into the Serene-based
mylearnbase site to make it better.
**Decision (2026-06-14):** adopt **Tier 1** (reading time, TOC, Pagefind search) +
**Tier 2** (prev/next nav, external-link indicator, privacy analytics). **Tier 3**
(Projects/portfolio page) deferred — revisit alongside the first concept demo.

## Method

Surveyed feature-rich, well-maintained Zola themes — primarily **tabi** (welpo; the
most feature-complete) and **abridge** (Jieiku; search-focused) — plus the
salif `zola-themes-collection` comparison. Ranked candidates by **value × effort for
mylearnbase specifically**, measured against what Serene already provides.

## Already have (confirm, don't rebuild)

- Series (custom `templates/series/`)
- KaTeX math + Mermaid diagrams (`post.html` / `home.html`)
- Code copy buttons (Serene `copy.svg`) — verify in audit
- Light/dark toggle with persistence
- RSS feed
- Featured/pinned posts (`post.extra.featured` already referenced in `home.html`)
- Archive + split-by-form aggregator (`posts_aggregator.html`, `archive/` section)

## Steal-list (ranked)

### Tier 1 — high value, low effort (recommend now)

| Feature | Source | Why for us | Effort | Fit |
|---|---|---|---|---|
| Reading time | tabi (native Zola `page.reading_time`) | sets expectation on long logbook/workflow posts | trivial | `post.html` one-liner |
| Table of contents | tabi (native Zola `page.toc`) | several posts are 400+ lines; needs in-page nav | low | `post.html` + CSS |
| **Site search (Pagefind)** | abridge / tabi | founding criterion "find your own content easily"; search is currently OFF (`build_search_index = false`) | low-med | post-build step + search UI element |

### Tier 2 — good value, low-med effort

| Feature | Source | Why for us | Effort | Fit |
|---|---|---|---|---|
| Prev/next post nav | tabi | keep readers moving through related content | low-med | `post.html` (Zola `page.earlier`/`later`) |
| External-link indicator | tabi | small polish; signals offsite links | low | CSS (Serene may already mark — verify) |
| Privacy analytics (GoatCounter / Plausible / Umami) | tabi | on-site visitor data; complements ahrefs + Search Console | med | head snippet + account |

### Tier 3 — portfolio-goal, higher effort (consider alongside concept demos)

| Feature | Source | Why for us | Effort | Fit |
|---|---|---|---|---|
| Projects/portfolio page (card grid + tag filter) | tabi | portfolio is mylearnbase's 2nd founding goal; pairs with concept demos | med-high | new template + content type |

### Skip for now (niche)

Webmentions, iine/like buttons, fediverse metadata, PWA/offline, multilingual,
per-page git-history links.

## Search decision (the headline)

**Recommendation: Pagefind**, not Zola's built-in elasticlunr.

- Pagefind indexes the **built HTML** after `zola build`, ships a prebuilt accessible
  search UI, and needs no hand-maintained index — current best practice for static sites.
- Zola elasticlunr needs `build_search_index = true` + a custom JS UI + per-language
  index handling: more moving parts for the same outcome.
- **Cost:** one extra build step (`npx pagefind --site public`) appended to the
  Cloudflare Pages build command — consistent with the existing pattern (the CF build
  already downloads Zola itself).
- **Cross-check:** because Pagefind reads rendered HTML, it correctly covers the
  nested/aggregated posts (`logbook/<project>/`) that a Zola-native index can be fiddly about.

## Notes / cross-references

- **OG/Twitter cards + canonical** are already Phase 2 — tabi confirms these are
  table-stakes; tabi's relative/absolute OG-path handling is a useful reference.
- **Analytics are complementary, not redundant:** ahrefs = off-site SEO/backlinks;
  Search Console = search-query data; GoatCounter/Plausible = on-site visitor behavior.
- **Comments (giscus)** are available via Serene's `_giscus_script.html` if ever
  wanted — not on the steal-list (low priority).

**Sources:** [tabi](https://github.com/welpo/tabi) · [tabi settings](https://welpo.github.io/tabi/blog/mastering-tabi-settings/) · [abridge](https://github.com/Jieiku/abridge) · [Pagefind](https://pagefind.app/docs/) · [Zola search docs](https://www.getzola.org/documentation/content/search/) · [salif zola-themes-collection](https://salif.github.io/zola-themes-collection/)
