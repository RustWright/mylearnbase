# NEXT — mylearnbase

**Updated:** 2026-10-12 · efeerhie.com + `efe@` alias + résumé QR + Christoffel concepts post all shipped.

## Next action
**Business card** (user's morning list, last item): reuse `static/img/site-qr.svg`; needs UW print-centre
specs (size, bleed, file format) from the user or their site. Then close Cycle 6 (`0016`) and plan Cycle 7,
whose proposed core is the skills↔projects mapping (L). Not yet chosen: confirm order with the user.

## Decisions in force
- **Christoffel post** "Where the indices go in a Coriolis matrix" (user's title), all 7 editing.md passes.
  **Three standalone demos** (user, 2026-10-12): `build/` (watch C built), `predict/` (which three
  cells, cancellation), `check/` (indices vs no-indices, Ṁ−2C skew). Shared `christoffel.{js,css}`. **Each must
  stand alone** (own framing, no "the last demo"). **No WASM:** a 2×2 finite difference is the heaviest
  compute. Demos self-size their iframe via `frameElement` at ALL widths (+ border); verified 0px nested scroll.
  Cell scrollbars had TWO causes: 150px side columns (now 280px floor, 3-col at ≥1240) AND KaTeX's φ̇ accent
  overhanging 2px (span padding .25em). Sweep clean 375–1920. In-post the iframe is ≤736px, so always stacked.
- **Post facts verified against the user's Spong PDF** (`~/Downloads`, a 2004 PRE-PRINT of the 1st ed.): Eq.
  6.58 slot order, k = equation (6.60), Prop. 6.1 skew only for Christoffel C. Book writes D(q), not M; G is a
  VECTOR. Cite without section numbers. Link = authors' page `faculty.cc.gatech.edu/~seth/SHV/` (1st ed.).
  Tags `robotics`, `dynamics` only (user dropped `control-systems`); flock link cut as shoehorned.
- **Check demo** (mutation-tested): only Check 1 catches an index swap; zero velocity passes any C, so it says so.
- **efeerhie.com = 301** to mylearnbase.com (`http*://*efeerhie.com/*` → `https://mylearnbase.com/${3}`, proxied
  `AAAA 100::` at @ and www). Dashboard's "may not proxy `http`" warning is a FALSE alarm. Paper prints it.
- **One QR: `static/img/site-qr.svg`** from `scripts/build-qr.py`, `print_url` UPPERCASED → version 1, EC M,
  decode-verified, NO quiet zone in the file. Résumé: top-right masthead, 0.8in, captioned to its LEFT
  ("Scan for projects & live demos"), zero added height. Email = alias only; PDF build fails on any other.
- ⚠️ **Never "Engineer" as the user's title** (Ontario PEO; unlicensed, MB EIT lapsing, user 2026-10-12):
  degree wording only, on résumé, card, JSON-LD. ⚠️ Résumé page 1 is FULL. Never phone/address.
- `custom.css` is `sass/css/custom.scss`; `zola check` NOT in `build.sh`; theme v5.6.1. Failed deploy: Retry first.

## Do NOT re-survey
- Lighthouse on a post page (2026-09-20): a11y 100, BP 100, perf 98, CLS 0. `http.server` cache warnings and
  `giallo-dark.css` "unused CSS" are harness artifacts.
- `tag1`/`tag2`/`""` in the tag-inventory grep are example front matter INSIDE post bodies, not real tags.

## Open threads
- TF-IDF `vector-space` demo opens "The last demo turned…": breaks the standalone rule. One-sentence fix.
- Deferred findings (3): `search.js` Pagefind double-mount; fixed ports unchecked in two scripts; 24/30 images
  lack width/height (CLS 0). ACM link in `tf-idf.md` 403s to curl. `0013` résumé polish open.
