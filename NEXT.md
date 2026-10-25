# NEXT — mylearnbase

**Updated:** 2026-10-25 · Playground reworked to action-first toys (committed, NOT pushed: user reviews first).

## Next action
**Plan Cycle 7** (`0017`) once the user brings a batch of co-op postings (2026-10-16: collecting into the job-scan
inbox; `--level coop` was n=1, too thin to pick a lead role). DEADLINE = January co-op search. Collaborative cycle
fed by an omni-me + ~/life logbook push; core = route each visitor (esp. recruiters) to what fits, surface skills.
Source: `~/life/.../job_market/my_skills.csv`, curated subset only, no gaps. Ideas: skills map, `hero-flock`.

## Decisions in force
- **Archived posts** (user 2026-10-13): `post.html` shows an "Archived" callout for `posts/archive/`; current
  posts never recommend archived ones (one-way; archive stays in the TF-IDF corpus so idf doesn't shift).
- **Playground = action-first toys** (user 2026-10-13, tightened 2026-10-25): lands on a task with a goal,
  caption = the instruction; passive watching never qualifies. Independent of posts: a `toy()` call in
  `content/playground/_index.md` lists a demo no post embeds (names its post; validated like embeds), or an
  embed's `playground=true`. Today: Snake vs DQN, Boids herding, SVG build. Pendulum balance once its post ships.
- **Preview Playground**: `scripts/build-demo-index.py`, then `zola serve --drafts`; new heavy demo → posters `--prune`.
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
- **Christoffel post**: facts verified against the user's Spong PDF (2004 pre-print, 1st ed.); no section numbers.
- ⚠️ Résumé PDF 1 page, 0 slack (user 2026-10-19): `optional` records drop only if that fits it (build decides).
  Subtitle ≤ ~82 chars (QR). NO Selected Projects (any pick misfits someone). Never phone/address.
- `custom.css` = `sass/css/custom.scss`; `zola check` NOT in `build.sh`; theme v5.6.1. Deploy ~4 min, flaky: retry first.

## Do NOT re-survey
- Lighthouse (09-20): a11y/BP 100, perf 98, CLS 0. Noise: giallo warnings, `tag1`/`tag2` in tag grep, Pagefind "no <html>".
- Repo is PUBLIC. Old `.log/` transcripts (Gmail) stay in history (user 2026-10-16; purge dangles 48 gitlinks).
  Privacy guard runs in `.githooks/pre-commit` (`docs/.../local-development.md`). ⚠️ OTHER DEVICE: run its installer.

## Open threads
- Playground copy LLM-drafted 2026-10-13, user to edit. `tf-idf.md` ACM 403s. `0013` open. Card: W Print, 3.5×2in.
