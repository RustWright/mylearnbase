# NEXT — mylearnbase

**Updated:** 2026-10-12 · Morning list DONE: efeerhie.com, `efe@` alias, résumé QR, Christoffel post, card.

## Next action
**Not chosen: ask the user.** Candidates, none picked: close Cycle 6 (`0016`, XS) then plan Cycle 7 (`0017`),
whose proposed core is the skills↔projects mapping (L, user's 2026-10-12 idea, not yet scoped); the open
threads below; standing ASD-STE100 (`0003`). Queue: `.omni/tasks.toml`.

## Decisions in force
- ⚠️ **Never "Engineer" as the user's title** (Ontario PEO; unlicensed, MB EIT lapsing, user 2026-10-12).
  Degree wording only: résumé subtitle, JSON-LD jobTitle, card. `build-card-pdf.sh` blocks the word.
- **efeerhie.com = 301** to mylearnbase.com (`http*://*efeerhie.com/*` → `https://mylearnbase.com/${3}`,
  proxied `AAAA 100::` at @ and www). The dashboard's "may not proxy `http`" warning is a FALSE alarm.
  Email Routing `efe@` → personal inbox, receive-only; the résumé PDF build fails on any other address.
- **QR codes from `scripts/build-qr.py`**, encoding `print_url`, decode-verified, NO quiet zone in the files:
  `site-qr.svg` (bare domain UPPERCASED → v1) on the résumé masthead → homepage ("Scan for projects & live
  demos", caption LEFT of it, zero added height); `resume-qr.svg` (`/resume/`, v3) on the card back → résumé.
- **Business card** `print/business-card/card.html` → `scripts/build-card-pdf.sh` → PDF (not deployed).
  3.5×2 + 0.125in bleed (industry standard; W Print publishes none, its free inspection checks). Front:
  name, full degree + UW (user's pick A), envelope/globe icons, OFFICIAL LinkedIn bug, blue, never recoloured.
- **Christoffel post** "Where the indices go in a Coriolis matrix", three standalone demos (`build/`,
  `predict/`, `check/`), shared `christoffel.{js,css}`, no WASM, self-sizing iframes. Facts verified against
  the user's Spong PDF (2004 PRE-PRINT of 1st ed.): cite without section numbers; book writes D(q).
- ⚠️ Résumé page 1 is FULL (`.rs-entry` is `break-inside: avoid`). Never phone/address.
- `custom.css` is `sass/css/custom.scss`; `zola check` NOT in `build.sh`; theme v5.6.1. A deploy can take
  ~4 min or fail transiently after `build.sh` succeeds: Retry the same commit before debugging.

## Do NOT re-survey
- Lighthouse on a post page (2026-09-20): a11y 100, BP 100, perf 98, CLS 0. `http.server` cache warnings and
  `giallo-dark.css` "unused CSS" are harness artifacts.
- `tag1`/`tag2`/`""` in the tag-inventory grep are example front matter INSIDE post bodies, not real tags.
- Zola minifies HTML: attribute quotes are stripped, so grep built pages without assuming `="`.

## Open threads
- TF-IDF `vector-space` demo opens "The last demo turned…": breaks the standalone-demo rule. One sentence.
- Deferred findings (3): `search.js` Pagefind double-mount; fixed ports unchecked in two scripts; 24/30 images
  lack width/height (CLS 0). ACM link in `tf-idf.md` 403s to curl. `0013` résumé polish open.
- The user orders the card at W Print themselves (double-sided, 3.5×2in); a reprint follows any URL change.
