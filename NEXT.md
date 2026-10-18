# NEXT — mylearnbase

**Updated:** 2026-10-18 · Shipped `what-the-snake-bot-was-missing` + `projects/snake.md` (repo `snake-dqn`).

## Next action
**Plan Cycle 7** (`0017`) once the user brings a batch of co-op postings (2026-10-16: collecting into the job-scan
inbox; `--level coop` was n=1, too thin to pick a lead role). DEADLINE = January co-op search. Collaborative cycle
fed by an omni-me + ~/life logbook push; core = route each visitor (esp. recruiters) to what fits, surface skills.
Source: `~/life/.../job_market/my_skills.csv`, curated subset only, no gaps. Ideas: skills map, `hero-flock`.

## Decisions in force
- **Archived posts** (user 2026-10-13): `post.html` shows an "Archived" callout for `posts/archive/`; current
  posts never recommend archived ones (one-way; archive stays in the TF-IDF corpus so idf doesn't shift).
- **Playground = toys only** (user 2026-10-13): a demo is listed only if its embed has `playground=true`
  (`build_groups` filters; flat `demos` list keeps all for back-links/projects). Test: fun having read
  nothing. Today: boids flock, Snake bot, SVG build-your-own. NOT naive-vs-grid, TF-IDF, enso, Christoffel.
- **`build.sh` sizes every local `<img>`** (`scripts/size-images.py`): author plain Markdown images, never
  hand-add dimensions. PDF/poster scripts refuse a busy port.
- ⚠️ **Never "Engineer" as the user's title** (protected title in Canada, user 2026-10-12).
  Degree wording only: résumé subtitle, JSON-LD jobTitle, card. `build-card-pdf.sh` blocks the word.
- **efeerhie.com = 301** to mylearnbase.com (`http*://*efeerhie.com/*` → `https://mylearnbase.com/${3}`,
  proxied `AAAA 100::` at @ and www). The dashboard's "may not proxy `http`" warning is a FALSE alarm.
  Email Routing `efe@` → personal inbox, receive-only; the résumé PDF build fails on any other address.
- **QR codes from `scripts/build-qr.py`** (`print_url`, decode-verified, no quiet zone): `site-qr.svg` (domain
  UPPERCASED → v1) on résumé masthead → homepage; `resume-qr.svg` (`/resume/`, v3) on card back → résumé.
- **Business card** `print/business-card/card.html` → `scripts/build-card-pdf.sh` → PDF; 3.5×2 + 0.125in bleed.
- **Christoffel post**: three standalone demos, shared `christoffel.{js,css}`, no WASM. Facts verified
  against the user's Spong PDF (2004 PRE-PRINT of 1st ed.): cite without section numbers; book writes D(q).
- ⚠️ Résumé page 1 is FULL (`.rs-entry` is `break-inside: avoid`). Never phone/address.
- `custom.css` = `sass/css/custom.scss`; `zola check` NOT in `build.sh`; theme v5.6.1. Deploy ~4 min, flaky: retry first.

## Do NOT re-survey
- Lighthouse on a post page (2026-09-20): a11y 100, BP 100, perf 98, CLS 0. Cache/giallo warnings = harness.
- Expected noise: `tag1`/`tag2`/`""` in tag grep (example front matter); Pagefind "no <html>" (alias redirects).
- Repo is PUBLIC. Old `.log/` transcripts (Gmail) stay in history (user 2026-10-16; purge dangles 48 gitlinks).
  Privacy guard runs in `.githooks/pre-commit` (`docs/.../local-development.md`). ⚠️ OTHER DEVICE: run its installer.

## Open threads
- Playground copy LLM-drafted 2026-10-13, user to edit. `tf-idf.md` ACM 403s to curl. `0013` open. User
  orders the card at W Print (double-sided, 3.5×2in); a reprint follows any URL change.
