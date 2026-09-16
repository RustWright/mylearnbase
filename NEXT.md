# NEXT — mylearnbase

**Updated:** 2026-09-16 · Cycle 6 (audience routing) opened. KaTeX fix + résumé shipped; hero flock approved.

## Next action
**Build the destination surfaces in order: `1d` demo back-links → `1c` Playground → `1b` Projects hub.**
Then `Part 2` (homepage router + header nav) — **last, necessarily**: Zola validates internal links at
build and the router points at all three. Plan: `~/.claude/plans/could-you-look-into-abstract-kahn.md`.

## Decisions in force
- **Hero flock approved.** Treatment **top band**; opacity **0.2**; hero **hugs its content** (no
  min-height). Gutters was rejected: its percentage mask *relocates* onto the text edges below ~760px.
  Prototype at `/demos/mylearnbase/hero-flock/`.
- **Header nav.** Desktop `Projects · Playground · Posts · Résumé`; **phones drop Posts** + use the
  logo mark (41px slack at 375px vs 77px overflow with four). Reason is redundancy, not importance:
  Posts has three other routes. **Tags leaves at every width.** Logo hover = task `3b`.
- **Résumé: HTML is canonical.** PDF generated from it by `scripts/build-resume-pdf.sh`, run **locally
  and committed**; `build.sh` warns on drift via `static/resume/.source-hash`.
- **No email on the résumé** until a forwarding alias exists on **efeerhie.com** (parked; Cloudflare
  Email Routing); LinkedIn carries contact. **No phone, no address, ever. No Memberships section** —
  the EGM membership lapses end of 2026 and a "present" claim on a static document rots.
- **Playground lives at `/playground/`**; demo *files* stay at `/demos/…`.
- **`themes/serene` is pinned** (`update = none`). SessionStart no longer fast-forwards it and warns on
  drift; restore with `git submodule update --init --checkout themes/serene` (**`--checkout` required**).

## Do NOT re-survey
- **KaTeX overflow: fixed and verified** (162px lateral scroll → none, 3 equations, scroll-shadow
  added). Numbers in `ui-checklist.md` Sweep 8. Don't re-measure.
- **Flock calibration is settled:** count derives from world area, and **units-per-pixel (`K=1.25`) is
  the fixed quantity**, not world width — 81 boids/megapixel at 1280px, 80 at 375px. Rationale inline in
  `static/js/hero-flock.js` + `architecture.md § Interactive Demos`.
- **PDF generation is solved.** Chrome headless prints against *screen* media, so print rules sit
  unconditionally in `static/css/resume-print.css` with the `media` attribute as the switch; the build
  must pass `--base-url` or it pulls CSS from production.

## Open threads
- 🔴 **`content/posts/opinions/skip-the-boilerplate.md` untracked in a PUBLIC repo.** `draft = true`, so
  unpublished — but SessionEnd will commit and push the raw markdown to GitHub. **Unresolved.**
- **Cycle 5 never formally closed** though every `tasks.md` task is done. Close it; write Cycle 6 tasks.
- **Homepage "Now" line — approved, not built**; lands with Part 2. Deferred: ASD-STE100 + voice work.
