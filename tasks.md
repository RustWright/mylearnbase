# Tasks — Cycle 6 (Audience Routing)
See bottom for new notes!
**Created:** 2026-09-16, written from the plan after implementation (the cycle ran from the plan-mode plan, `~/.claude/plans/could-you-look-into-abstract-kahn.md`, as Cycles 3 and 4 did).
**Objective:** A homepage that routes a visitor by intent within one screen (recruiter, project browser, explorer), three destination surfaces worth arriving at, and enough motion that the site reads as built rather than generated. Two fixes joined on the way: KaTeX overflow and missing post descriptions.
**Design record:** `architecture.md` (Projects, Résumé, Homepage and header, Page descriptions, Interactive Demos, Deployment). Verification: `ui-checklist.md` Sweep 8.

Order that held: KaTeX → flock prototype (review gate) → résumé → projects → demo back-links → playground → homepage + header → logo and door motion → descriptions. The homepage came last among the structural work because Zola validates the internal links it adds.

---

## Task 0 — KaTeX narrow-screen overflow ✅ DONE (2026-09-16)
- [x] `.katex-display` scrolls internally with a scroll-shadow cue (`static/css/custom.css`). Measured 162px of lateral page scroll at 375px before, none after.
- [x] Methodology fix in `ui-checklist.md`: Sweep 7 had filed a 1280px measurement under the 375px row.

## Task 1 — Résumé `/resume/` ✅ DONE
- [x] Structured front matter, one template for page and PDF (`scripts/build-resume-pdf.sh`, 2 pages, embedded font), `Person` JSON-LD, `/cv/` alias, drift warning in `build.sh`.
- [x] Privacy: no email until an efeerhie.com alias exists, never phone or address; leak guards fail the PDF build.

## Task 2 — Projects hub `/projects/` ✅ DONE
- [x] omni-me, mylearnbase and boids pages: authored facts, derived write-ups and demos. Public repos only.

## Task 3 — Demo index + standalone back-links ✅ DONE
- [x] `scripts/build-demo-index.py` derives `demos.json`; broken embeds fail the build, orphans and draft parents warn.
- [x] `demo-chrome.js` in all 12 demos: bar when standalone, nothing when embedded.

## Task 4 — Playground `/playground/` ✅ DONE
- [x] Tiles grouped by post; light demos preview live, heavy demos show content-addressed posters (`scripts/capture-demo-posters.py`).

## Task 5 — Homepage router + header ✅ DONE
- [x] Doors (Projects / Playground / Résumé), dated Now line, Latest 5; form guide moved to `/posts/`.
- [x] Nav Projects · Playground · Posts · Résumé; Posts hides below 575px (measured).

## Task 6 — Motion ✅ DONE
- [x] Hero flock (`static/js/hero-flock.js`, a port of the boids rules; pointer is the predator).
- [x] Logo hover and door stagger, pure CSS behind `prefers-reduced-motion: no-preference`. Approved by the user.

## Task 7 — Post descriptions ✅ DONE
- [x] One description chain in `_head_extend.html`; a published post without `description` fails `zola build`.
- [x] Publish tools take, keep and require `--description`; `_frontmatter.py` quote round-trip fixed.
- [x] All 32 published posts backfilled (LLM drafts, user approved). Front-matter template, `/create-post` and editorial guides updated.
- [x] Link-preview card rendered from source (`scripts/build-og-card.py`), drift-checked.

## Task 8 — Verification Sweep 8 ✅ DONE
- [x] Recorded in `ui-checklist.md`, including the Cloudflare theme-pin failure and its fix (`099d03d`).

## Task 9 — Cycle bookkeeping ✅ DONE (2026-09-16)
- [x] `tasks.md` reset to Cycle 6; `project.md` Cycle 6 entry; `architecture.md` revision history.
- [x] Site-backlog memory note retired (both items shipped).
- [x] Cycle 5 closed 2026-09-16: no code review (user decision), no curiosity survivors.
- [x] `.omni/tasks.toml` moved to cycle 6.

---

## Notes

- **Carried from Cycle 5:** all five Cycle 5 tasks shipped (doc refresh, Sweep 7, TF-IDF related posts, colophon, content batch). Their detail is in `project.md` and git history.
- **Open, unscheduled:** the 12 standalone demo pages have no meta description; the front-matter template body describes the old post format; résumé polish (page 2 ~40% full, a duplicated award line, accent colour); demos follow `prefers-color-scheme` while the site has a toggle.
- **Out of scope this cycle:** the ASD-STE100 writing standard below, and the editorial-voice initiative.


- We need to make our own version of https://www.asd-ste100.org/about.html
- I'm still very frustrated with the basic writing quality of the log books and I want to try something new, 
- We don't need to adopt the entire manual but we should understand how and why it can improve AI writing quality, then adapt it to our needs
- Sometimes asking for an unreasonablu tight word, character or line count can also force the model to select words use better
