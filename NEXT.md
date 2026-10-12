# NEXT — mylearnbase

**Updated:** 2026-10-12 · efeerhie.com 301 + `efe@` alias live; résumé QR (captioned) + email shipped.

## Next action
**Christoffel concepts post** (user-chosen order, 2026-10-12): domain ✓ → résumé QR ✓ → Christoffel → business
card. `0013` résumé polish still open. Skills↔projects mapping = proposed core of Cycle 7 (L), after closing
Cycle 6 (`0016`). Phone scan passed (user, 2026-10-12); the caption came from their test, a bare code reads as noise.

## Decisions in force
- **efeerhie.com = 301 redirect, NOT a second copy** (user, 2026-10-12; the bar shows mylearnbase.com). Zone on
  the same Cloudflare account, Porkbun → `jihoon`/`ligia`. Proxied `AAAA @` + `AAAA www` → `100::`; Redirect
  Rule wildcard `http*://*efeerhie.com/*` → `https://mylearnbase.com/${3}`, 301, query kept. Verified: apex,
  www, http, deep path, query all 1 hop. The dashboard's "may not proxy `http`" warning is a FALSE alarm (it
  reads `http` as the hostname); never create the record it offers. Print material points at efeerhie.com.
- **Christoffel demo: recommend NO Rust/WASM** (47 KB single HTML, KaTeX only, already site-loaded; a
  wasm-bindgen bundle would be larger). Not yet confirmed by the user. Cleanup list is in `tasks.md` § Notes.
- **One QR for all paper: `static/img/site-qr.svg`** from `scripts/build-qr.py`, encoding `print_url`
  (zola.toml) UPPERCASED → version 1 (21×21), EC M, decode-verified. **No quiet zone in the SVG**: each
  placement leaves ≥4 modules of white. Résumé: absolute, top-right masthead, 0.8in, zero added height, captioned
  "Scan for projects & live demos" (user's pick) to its LEFT, never below (that gap is the quiet zone).
  Paper prints efeerhie.com; PDF hrefs stay canonical. JSON-LD lifts mailto into `email`, not `sameAs`.
- ⚠️ **Page 1 of the résumé is FULL** (unchanged by the QR). `.rs-entry` is `break-inside: avoid`. Email =
  the alias only (build guard enforces); never phone/address.
- **`custom.css` lives at `sass/css/custom.scss`** (emitted at the same URL, minified). `zola check` NOT in
  `build.sh`: external links would couple deploys to other people's uptime. Theme pinned v5.6.1.
- **Experience entries may carry `roles`** (title/date pairs, newest first): Antec, both real titles, org once.
- **A Cloudflare deploy can fail transiently AFTER `build.sh` succeeds:** Retry the same commit first.

## Do NOT re-survey
- **Lighthouse on a post page, 2026-09-20: a11y 100, BP 100, perf 98, CLS 0.** Cache/latency/render-blocking
  warnings come from `python3 -m http.server`; the 78KB "unused CSS" is `giallo-dark.css`. Clean on review:
  `hero-flock.js`, `header.js`, `tools/src/`. `build.sh` verified in-tree, fresh clone, and on Cloudflare.

## Open threads
- **Deferred findings (3):** `search.js` double-mounts Pagefind if the overlay closes mid-load (cache the
  promise); `build-resume-pdf.sh` + `capture-demo-posters.py` bind fixed ports unchecked; 24/30 images lack
  width/height (CLS 0). ACM link in `tf-idf.md` 403s to curl; unverified.
- Business card: needs UW print centre specs (size, bleed, format) from the user or their site.
