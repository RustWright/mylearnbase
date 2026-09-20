# NEXT — mylearnbase

**Updated:** 2026-09-20 · Résumé edits + code review + visitor-experience audit; **4 of 7 findings applied**.

## Next action
**Not chosen: ask the user.** (1) The 3 deferred findings below, all low-urgency. (2) Close Cycle 6 Phase D, then
Cycle 7 planning (`0017`). Biggest standing item is still ASD-STE100 (`0003`). Queued: `0011`, `0012`, `0013`,
`0014`, `0007`, `0008` (`.omni/tasks.toml`).

## Decisions in force
- **`custom.css` now lives at `sass/css/custom.scss`.** `compile_sass` mirrors folder structure, so it emits
  `public/css/custom.css` at the SAME URL, minified (gzipped 11,516 → 4,192 bytes, verified rule-for-rule
  equivalent). `resume-print.css` stays in `static/`, print-only. **`zola check` deliberately NOT in `build.sh`**
  (reversing my own earlier suggestion): it hits external links, coupling deploys to other people's uptime.
- **Zola shortcodes links pinned to the `v0.22.1` GitHub tag.** The page was removed from upstream Zola after
  0.22.1, so it exists at no getzola.org URL and no branch tip. That tag is also what `build.sh` pins.
- **`compute-related.py` extracts headings after code fences, before inline-code.** Why, and the cost of moving
  it either way, is in the comment above that line.
- **An experience entry may carry `roles` (title/date pairs, newest first) instead of `role` + `dates`:** a
  promotion names the org ONCE, titles stacked. Antec uses it; the other three keep single-`role`.
- **Antec: both titles, real dates each** (user, 2026-09-20). They rejected final-title-only as dishonest and
  rejected repeating the org. Bullets are NOT split by title. **Interests** section shipped (their word choice).
- ⚠️ **Page 1 of the résumé is FULL: y=750 of 758 usable.** Any Education/Experience addition pushes a whole
  entry over (`.rs-entry` is `break-inside: avoid`). Cutting Antec's test-equipment bullet buys two lines back.
- 2026-09-16 handoff holds: no email until a forwarding alias exists, no phone/address ever, theme pinned v5.6.1.

## Do NOT re-survey
- **Lighthouse on a POST page, 2026-09-20: a11y 100, best-practices 100, perf 98, CLS 0.** Closes
  `ui-checklist.md`'s focus-states and CLS/image-sizing gaps; not yet written there. Automated a11y catches ~1/3.
- **Harness artifacts, not findings:** cache-lifetime / latency / render-blocking warnings come from
  `python3 -m http.server` sending no cache headers. Likewise the 78KB "unused CSS": `giallo-dark.css` must
  preload or the toggle flashes. Clean on review: `hero-flock.js`, `header.js`, `tools/src/`.
- `bash build.sh` end to end after all four fixes: clean, 12/12 demo back-links, 32 pages indexed. Résumé PDF
  rebuilt after the CSS move, still 2 pages, passing its assertions.

## Open threads
- **Deferred findings (3).** `search.js` double-mounts Pagefind if the overlay closes inside the load window
  (cache the promise, not the boolean); `build-resume-pdf.sh` + `capture-demo-posters.py` bind fixed ports
  unchecked and assert only negatives, so a wrong-page PDF would pass; 24 of 30 images lack width/height, left
  because CLS measured 0. **ACM link** in `tf-idf.md` 403s to curl even with a browser UA; unverified, left.
