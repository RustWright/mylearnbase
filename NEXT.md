# NEXT — mylearnbase

**Updated:** 2026-10-13 · Playground = toy shelf; archived posts marked + out of Related (both committed).

## Next action
**Plan Cycle 7** (`0017`). Proposed core, user's idea, NOT scoped: map skills to projects so the résumé
shows which project exercises which skill. Candidate: front-door logbook entry embedding orphan `hero-flock`.

## Decisions in force
- **Archived posts** (user 2026-10-13): `post.html` shows an "Archived" callout for `posts/archive/`; current
  posts never recommend archived ones (one-way; archive stays in the TF-IDF corpus so idf doesn't shift).
- **Playground = toys only** (user 2026-10-13): a demo is listed only if its embed has `playground=true`
  (`build_groups` filters; flat `demos` list keeps all for back-links/projects). Test: fun having read
  nothing. Today: boids flock, Snake bot, SVG build-your-own. NOT naive-vs-grid, TF-IDF, enso, Christoffel.
- **`build.sh` sizes every local `<img>`** (`scripts/size-images.py`): author plain Markdown images, never
  hand-add dimensions. PDF/poster scripts refuse a busy port.
- ⚠️ **Never "Engineer" as the user's title** (Ontario PEO; unlicensed, MB EIT lapsing, user 2026-10-12).
  Degree wording only: résumé subtitle, JSON-LD jobTitle, card. `build-card-pdf.sh` blocks the word.
- **efeerhie.com = 301** to mylearnbase.com (`http*://*efeerhie.com/*` → `https://mylearnbase.com/${3}`,
  proxied `AAAA 100::` at @ and www). The dashboard's "may not proxy `http`" warning is a FALSE alarm.
  Email Routing `efe@` → personal inbox, receive-only; the résumé PDF build fails on any other address.
- **QR codes from `scripts/build-qr.py`**, encoding `print_url`, decode-verified, NO quiet zone in the files:
  `site-qr.svg` (domain UPPERCASED → v1) on the résumé masthead → homepage; `resume-qr.svg` (`/resume/`, v3)
  on the card back → résumé.
- **Business card** `print/business-card/card.html` → `scripts/build-card-pdf.sh` → PDF; 3.5×2 + 0.125in bleed.
- **Christoffel post**: three standalone demos, shared `christoffel.{js,css}`, no WASM. Facts verified
  against the user's Spong PDF (2004 PRE-PRINT of 1st ed.): cite without section numbers; book writes D(q).
- ⚠️ Résumé page 1 is FULL (`.rs-entry` is `break-inside: avoid`). Never phone/address.
- `custom.css` is `sass/css/custom.scss`; `zola check` NOT in `build.sh`; theme v5.6.1. A deploy can take
  ~4 min or fail transiently after `build.sh` succeeds: Retry the same commit before debugging.

## Do NOT re-survey
- Lighthouse on a post page (2026-09-20): a11y 100, BP 100, perf 98, CLS 0. Cache/giallo warnings = harness.
- `tag1`/`tag2`/`""` in the tag grep = example front matter in post bodies. Zola strips attribute quotes.
- Pagefind "has no <html> element" on old `/posts/<slug>/` URLs = alias redirect pages, expected.

## Open threads
- Playground page copy (description/subtitle) was LLM-drafted 2026-10-13; user to edit.
- ACM link in `tf-idf.md` 403s to curl (unverified, left). `0013` résumé polish open.
- The user orders the card at W Print themselves (double-sided, 3.5×2in); a reprint follows any URL change.
