# Tasks — Cycle 5 (Incremental Polish)
See bottom for new notes!
**Created:** 2026-06-30 (Cycle 5 Planning)
**Objective:** A batch of "little things" that make the site better, no sweeping changes — refresh drifted project docs, give prev/next a content-based basis, ship the parked privacy page, and publish a content batch about the site itself.
**Source of truth:** the approved plan-mode plan (archived) holds the full rationale; this file is the working tracker. Open knobs get settled at task-execution time, not before.

Tasks are independent except where noted. Suggested order: Task 1 (doc, low-risk, warms up) → Task 3 (the design-bearing one) → Task 2 (sweep re-verifies Task 3) → Task 4 → Task 5 (logbook candidates depend on Tasks 3-4 having shipped).

---

## Task 1 — Refresh `architecture.md` ✅ DONE (2026-06-30)

The doc had drifted badly: untouched since 2026-02-02, it still described the **abandoned Dioxus stack**, a `blog/` + `config.toml` layout, and "search deferred." Rewritten to current reality.

- [x] Stack table: Zola 0.22.1 + Serene v5.6.1 (submodule) + Tera; Pagefind 1.5.2 search; Cloudflare Pages via `bash build.sh`; mdBook docs on GitHub Pages. Dioxus framing kept only in the Revision History.
- [x] Content organization: `content/posts/<form>/…` five-form post system (logbook nested per project; concepts / workflows / opinions / resources flat), `archive/`, taxonomies `tags` + `series` (`categories` removed in Cycle 3).
- [x] Template-override surface: documented the **full** owned set — also `blog.html` + `robots.txt` beyond the planned eight. Added `static/` detail (fonts/OpenDyslexic, img/og, llms.txt, generated `giallo-*.css`).
- [x] Kept the Risk Register (statuses updated) + Revision History; **appended** a Cycle-5 entry rather than deleting history.
- [x] Verified every claim against actual `zola.toml`, `templates/`, `build.sh`, `static/`, `content/`, `.github/workflows/`, and `.gitmodules`. Replaced the WASM section with an **Interactive Demos** section describing the real `{{ demo() }}` iframe mechanism; fixed the false "Cloudflare auto-detects, no build command" deployment claim.

## Task 2 — Verification sweep (Sweep 7) → update `ui-checklist.md` ✅ DONE (2026-06-30)

The checklist was last swept 2026-06-14 (Cycle 3), so it still marked reading-time / prev-next / search as "not yet built" even though all shipped in Cycle 4. Re-swept and brought current.

- [x] Ran `zola build` (26 pages / 0 orphan / 9 sections, clean), `zola check --skip-external-links` (clean), and `scripts/seo-audit.sh` (**ALL PASS, Lighthouse SEO 100/100**).
- [x] **Bonus harness fix:** `seo-audit.sh` JSON-LD check false-failed on 26 valid `BreadcrumbList` blocks (added Cycle 4) because its `@type` allowlist predated them. Taught it `BreadcrumbList`; audit green again (116 blocks valid, 0 parse failures). A stale gate trains you to ignore red, so this counts as verification-infrastructure repair.
- [x] Flipped now-shipped items to `[x]`: reading-time, Pagefind search, reader controls, breadcrumb JSON-LD, and the **Cycle-5 content-based prev/next** (verified in-browser: "Related" links resolve to each post's true TF-IDF top-2; chronological fallback renders when the artifact is absent).
- [x] Verified the genuinely-unchecked items via rendered-HTML grep + a Playwright browser pass (1280px + 375px, light/dark, console capture): copy button, callouts, demo iframes, series/tags pages (49 tags / 3 series), 404, theme persistence (`sessionStorage`), dark-mode contrast (**9.47:1**, exceeds AAA), no horizontal overflow, single h1, all images `alt`'d, aria-labels, **0 console errors/warnings**. Honestly left unchecked: KaTeX/Mermaid/`superseded_by` (wired but unexercised by content), focus-states/keyboard-nav/active-section/instant-nav, CLS, light-mode fresh measure.
- [x] Added a **Sweep 7** entry; bumped the "Last swept" line. Noted the benign Pagefind warning (redirect-alias stub).

## Task 3 — Prev/next redesign: content-based relatedness *(design-bearing)* ✅ DONE (2026-06-30)

Moved off chronological ordering. **Decision (settled):** content similarity behind a `related.json` seam, hand-built TF-IDF. Rejected: shared-tags (tagging is volatile) and author-curated (too manual). **The script uses title + headings + body text ONLY, never tags.**

- [x] **`scripts/compute-related.py`** (alongside `seo-audit.sh`; mylearnbase-specific, not the cross-project `tools/` package). Pure-Python stdlib, ~190 lines: reads post source under `content/posts/**` (strips frontmatter, code fences, shortcodes, links, HTML), tokenizes (lowercase, stopwords, light plural stemming that protects `-ss/-us/-is` and maps `-ies → -y`), sublinear-tf / smoothed-idf TF-IDF, cosine similarity, writes top-K (=4) neighbours per post → `related.json`. Title up-weighted ×3, headings ×2. Records the shared terms behind each match (interpretable; `--verbose` prints the full report). Skips `_index.md`, dotfiles (e.g. `.frontmatter-template.md`), and `draft = true`.
- [x] **`related.json` seam:** maps each post's content-relative path (incl. `index.md` for bundles, matching `page.relative_path`) → ranked neighbour list `[{path,title,score,terms}]`. Script speaks only paths + scores; template resolves path → live page via `get_page`, so URL/slug changes need no script change.
- [x] **Build integration (compute in CI):** added `python3 scripts/compute-related.py` to `build.sh` **before** `zola build`. Order: compute-related → `zola build` (reads `related.json` via `load_data`) → `pagefind`. `related.json` gitignored + regenerated each build (artifact, like the Pagefind index). Verified: full `bash build.sh` exits 0 end-to-end.
- [x] **Render:** `templates/post.html` now reads `load_data(path="related.json", required=false)`, looks up `page.relative_path`, renders the top 2 neighbours in the existing `<nav class="post-nav">` markup. `required=false` is the hinge that keeps dev (`zola serve`, no artifact) from erroring. **Chronological fallback** (the prior walk, byte-identical) when `related.json` is absent or a post has no entry — verified rendering "Adjacent posts" while related mode renders "Related". Old same-day-tie follow-up is now moot.
- [x] **Labels:** settled on **"Related"** (dropped the directional ←/→ and `rel="prev/next"` for related links, since relatedness is not sequential; chronological fallback keeps them).
- [x] **Decision gate:** inspected `related.json` on the real 26-post corpus. **Matches read STRONG, not weak — staying on TF-IDF, NOT upgrading to model2vec.** Evidence: `site-search` ↔ `how-search-works` mutually #1 (shared `pagefind/search/index/indexing`); omni-me financial features, omni-me Rust-dev archive, and workflows authoring posts each cluster correctly as #1/#2. Confirms the single-author / consistent-vocabulary hypothesis (`.curiosities/cycle-5.md` entry 1): little semantic-but-non-lexical signal left for embeddings to recover. model2vec path stays a documented drop-in (swap `vectorize`/`similarity`, flip to precompute-and-commit) if the corpus ever diversifies.

## Task 4 — Privacy / colophon page ✅ DONE (2026-06-30)

The parked Cycle-4 item. Shipped as a single combined **Colophon** page at `/colophon/`.

- [x] `content/colophon/_index.md` — a one-off Serene **prose section** (`template = "prose.html"`, the theme's standalone-page mechanism; `prose.html` keys on `section.*`, so a loose page wouldn't work). Two sections: **"How it's built"** (Zola/Tera, Serene, Pagefind, Cloudflare Pages, the `{{ demo() }}` iframes + TF-IDF "Related" links, mdBook) and **"Privacy"** (no analytics/tracking/cookies; only functional `localStorage`/`sessionStorage` prefs; search runs in-browser; the math/diagram CDN caveat; Cloudflare server logs; no consent banner needed under ePrivacy "strictly necessary").
- [x] Visible masthead via `[extra] title` + `[extra] subtitle` (Serene's `_section_title.html` renders the on-page `<h1>` from `extra.title`, **not** from the top-level `title` field — that one only feeds `<title>`/meta). Without `extra.title` the page rendered headless.
- [x] Wired into the **footer** (`templates/_footer.html`, `.left` group) via `get_url(path='@/colophon/_index.md')` so Zola validates the link at build. Appears on every content page's footer; **not** on the home landing (it has `footer = false` by theme design — reversible if home reachability is wanted).
- [x] Deliberately **no link** to the not-yet-existing Task-5 resources post (would break `zola check`); the page notes a fuller resources post is "in the works." When that post lands, add the link here.
- [x] Future cookieless-analytics decisions get disclosed here first (implementation still out of scope). Verified: `zola build` + `zola check --skip-external-links` clean; page renders at `/colophon/` with title, subtitle, both sections; footer link resolves; no `post-nav` (correct for a prose page).
- [x] **Follow-up fix (2026-06-30, user-reported):** the colophon's `← Back` button dumped readers to the home page. Root cause: the colophon is the first page to render through Serene's `prose.html`, which still calls `macros::back_link` — a path Cycle 4's site-wide back-link removal never touched (no prose page existed then). Fixed by adding a project `templates/prose.html` override (copy of theme minus the back-link line), matching the established no-back-link pattern. Diff vs theme is just the explanatory comment + the removed line; all future prose pages inherit the fix.

## Task 5 — Content batch

The posts flagged during planning. Route authoring via `/create-post`.

- [x] **Resources post — "Resources used to build mylearnbase" — PUBLISHED 2026-06-30.** First post in the `resources` section (`content/posts/resources/building-mylearnbase.md`, slug `building-mylearnbase`). Project-derived, by-act curation per `editorial/resources.md`: 7 sections of tools actually used (site generator + theme, hosting, search, reading experience, docs, authoring tooling, SEO/audits) plus an **"Alternatives considered"** section (theme/generator comparison + the abandoned Rust-fullstack PoC, sourced from the session logs, not invented). Factual/objective tone (user-confirmed: documents what was used + considered as a starting point for similar builds; voice lines deferred). Curation calls: excluded the self-authored `tools/` package (not *external*); kept showboat (`simonw/showboat`) + uv; `schema.org` filed under SEO, not "alternatives." All 26 external links verified 200; integrated into `related.json` (top neighbour: the MVP logbook post — relatedness on content alone) and Pagefind (27 pages). Colophon now links to it (the bidirectional-discoverability anchor; no single logbook post exists to back-link). Sync upkeep: relies on the section's 180-day `outdate_alert` banner (user choice, no memory/pointer machinery).
- [x] **Concepts post — "Measuring document similarity with TF-IDF" — PUBLISHED 2026-07-01.** `content/posts/concepts/tf-idf.md`, slug `tf-idf`. Three demos (ablation "why both TF and IDF"; whole-document comparison with contribution breakdown + neighbour ranking; bring-your-own-text) over a dense Wikipedia corpus, plus the two research framings with citations (near-orthogonality → read cosine as ranking, not magnitude; vocabulary mismatch → why embeddings exist). Bidirectional cross-links wired: the indexing post's closing forward-pointer and this logbook's §7 reciprocal both now link here. Author wrote "What clicked"; opening kept descriptive. Older hash-demo (`.curiosities/cycle-2.md`) remains a second concepts candidate.
- [x] **Logbook entry — "Content-based related posts" — PUBLISHED 2026-06-30.** First documentation of post-to-post navigation on the site (`content/posts/logbook/mylearnbase/related-posts/index.md`, slug `related-posts`, tags navigation/ux/frontend). Carries the arc: why relatedness over arbitrary chronology, the `related.json` seam, compute-in-CI build artifact, dev/prod chronological fallback; §7 plants the concepts-demo candidate (bidirectional cross-link deferred until that post exists). §6 = self-demonstrating (the post's own Related links resolve to Site search + Persistent site header, its two nearest `related.json` neighbours) + 4 commit-pinned cites (compute → build → render → fallback); no exec (the `--verbose` shared-terms table is corpus-dependent → would force permanent `--skip-verify`). Review corrections: §4 de-inflated to true history (chronological nav shipped 2026-06-25, replaced days later as arbitrary — no catalogue-growth/archive drama); embeddings moved §5 "Not in" → §7 (deferral, not permanent non-goal, per `editorial/logbook.md:522`: shape=§5, trajectory-with-revisit-trigger=§7); dangling "same-day tie" §7 bullet cut (internal-tracker-only referent). **Colophon + reading-time NOT logbooked** (fail the build-story half; → opinions form if anything). **Pattern held: reader-facing is necessary but not sufficient for meta-logbook.**
  - Follow-ups: the concepts demo (line above) is the confirmed next piece — user will export/compact first, then close the cycle after it. Bidirectional §7↔concepts cross-link to be wired when the demo ships.

---

## Notes

- **Subsumed follow-up:** the Cycle-4 "same-day prev/next tie" (`logbook publish` stamps date-only) is folded into Task 3 — once prev/next is relatedness-based, the date tie only matters in the chronological fallback.
- **Curiosities captured this cycle** (`.curiosities/cycle-5.md`): (1) lexical (TF-IDF) vs semantic (embeddings) similarity and why the gap shrinks on a single-author corpus; (2) where build-time computation should live (compute-in-CI vs precompute-and-commit) and how that flips when the algorithm changes.
- **Out of scope:** tagging-strategy rework (flagged volatile but not changing now; Task 3 deliberately avoids depending on tags); cookieless-analytics implementation (only disclosed in Task 4 if/when decided); process docs (`CLAUDE.md`, `PROJECT_PROCESS.md`).


- We need to make our own version of https://www.asd-ste100.org/about.html
- I'm still very frustrated with the basic writing quality of the log books and I want to try something new, 
- We don't need to adopt the entire manual but we should understand how and why it can improve AI writing quality, then adapt it to our needs
- Sometimes asking for an unreasonablu tight word, character or line count can also force the model to select words use better
