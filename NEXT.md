# NEXT — mylearnbase

**Updated:** 2026-09-20 · Résumé edits + code review + visitor-experience audit; **4 of 7 findings applied**.

## Next action
**Not chosen: ask the user.** (1) The 3 deferred findings below. (2) Cycle 6 Phase D, then Cycle 7 planning
(`0017`). Standing item ASD-STE100 (`0003`), queue `.omni/tasks.toml`. `13355f9` is deployed and verified live.

## Decisions in force
- **`custom.css` now lives at `sass/css/custom.scss`.** `compile_sass` mirrors folder structure, so it emits
  `public/css/custom.css` at the SAME URL, minified (gzipped 11,516 → 4,192, verified rule-for-rule equivalent);
  `resume-print.css` stays in `static/`. **`zola check` deliberately NOT in `build.sh`**: it hits external
  links, coupling deploys to other people's uptime.
- **Zola shortcodes links pinned to the `v0.22.1` GitHub tag**, the version `build.sh` pins: the page exists at
  no getzola.org URL and no branch tip. `compute-related.py` heading placement is explained at its own line.
- **An experience entry may carry `roles` (title/date pairs, newest first) instead of `role` + `dates`:** a
  promotion names the org ONCE, titles stacked. Antec uses it, the other three keep single-`role`, and it
  carries **both titles with real dates** (user, 2026-09-20: final-title-only rejected as dishonest, repeating
  the org rejected too). Bullets NOT split by title. **Interests** section shipped, their word choice.
- **A Cloudflare deploy can fail transiently AFTER `build.sh` succeeds.** 2026-09-20: build green in 6s, then a
  35-min hang in its own "Validating asset output directory" stage, ending in the build time limit; a manual
  Retry of the SAME commit succeeded. Retry first, do not debug the build: the Cloudflare build log is the only
  artifact that tells this apart from a real failure, and live-site polling cannot.
- ⚠️ **Page 1 of the résumé is FULL: y=750 of 758 usable.** Any Education/Experience addition pushes a whole
  entry over (`.rs-entry` is `break-inside: avoid`); cutting Antec's test-equipment bullet buys two lines back.
  2026-09-16 handoff holds: no email until a forwarding alias exists, no phone/address, theme pinned v5.6.1.

## Do NOT re-survey
- **Lighthouse on a POST page, 2026-09-20: a11y 100, best-practices 100, perf 98, CLS 0.** Closes
  `ui-checklist.md`'s focus-states and CLS/image-sizing gaps; not yet written there. Automated a11y catches ~1/3.
- **Harness artifacts, not findings:** cache-lifetime / latency / render-blocking warnings come from
  `python3 -m http.server` sending no cache headers; the 78KB "unused CSS" is `giallo-dark.css`, which must
  preload. Clean on review: `hero-flock.js`, `header.js`, `tools/src/`. `build.sh` verified 3 ways: in-tree, in
  a FRESH `--recurse-submodules` clone of `13355f9`, and on Cloudflare itself (6s, all stages green).

## Open threads
- **Deferred findings (3).** `search.js` double-mounts Pagefind if the overlay closes inside the load window
  (cache the promise, not the boolean); `build-resume-pdf.sh` + `capture-demo-posters.py` bind fixed ports
  unchecked, asserting only negatives, so a wrong-page PDF would pass; 24 of 30 images lack width/height, left
  because CLS measured 0. **ACM link** in `tf-idf.md` 403s to curl even with a browser UA; unverified, left.
