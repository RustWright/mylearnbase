# Personal Website Project

**Status:** Active — **Cycle 2 closed 2026-05-16**
**Started:** 2026-01-31
**Current Phase:** Cycle 2 Session 4 — Per-form authoring sweep **COMPLETE** (5/5); resources landed 2026-05-14. `editorial/resources.md` written + published as `authoring-a-resources-post`. Walkthrough refinements: job statement sharpened to "future-you can find them in one place when the need arises"; author contribution framed as **implicit by curation-by-act** (not prose-per-bullet); sub-types collapsed 3 → 2 (question-driven dropped); Topic 4 (writing-well) skipped as standalone section — third consecutive form to do so. **Curiosity-log mechanism + Task 13 (`/create-post` skill rewrite) shipped 2026-05-15** — instructions in global `~/.claude/CLAUDE.md`; mylearnbase seeded with `cycle-2.md`; create-post skill is now a routing skill that prompts for form first and reads the relevant `editorial/<form>.md` as source of truth. Remaining Cycle 2 work: Task 15 (PROJECT_PROCESS + CLAUDE.md sync with cycle-close review pass), Task 14 sub-items (tagging strategy doc, home-page navigation), POST_SYSTEM.md v1 deletion, Phase 8 cycle close. Task 10 (real omni-me logbook entry) + first concepts post (hash demo) deferred — user opted for full scaffolding build over real-content validation.
**Domain:** mylearnbase.com

---

## Session 1: Project Initiation

### 1. Project Goals

1. **Blog/Learning Journal**
   - Document processes when working on projects of interest
   - Series-based posts (multi-part, connected content)
   - Useful as personal reference and for others to replicate

2. **Portfolio**
   - Showcase completed work
   - Host interactive demos where possible
   - Allow visitors to engage with projects directly

3. **Monetization**
   - Organic revenue generation
   - Goal: Cover maintenance costs at minimum
   - No specific strategy yet - intentionally keeping this low-pressure

### 2. Primary User

**Primary:** Myself
- As **creator**: Easy to write, upload content, and deploy demos
- As **consumer**: Easy to revisit and reference past work

**Secondary (later):** Other learners, potential employers/clients

**Design Priority:** Authoring experience first. If it's frictionless for me to create, I'll create consistently. If I can find my own content easily, others can too.

### 3. Success Criteria

**Core Metric:** Creation friction so low that weekly publishing feels inviting, not burdensome.

**6-Month Targets:**
- [ ] 10+ articles published
- [ ] 3 demo projects hosted and interactive
- [ ] $1/week steady revenue (modest by design)

**Mindset Goal:** Focus on creation joy. Let monetization be a quiet background metric. Avoid the excitement→disappointment cycle from past projects.

### 4. Timeline & Availability

- **MVP Target:** Live within 4 weeks
- **Urgency Driver:** SEO indexing takes time - start the clock early
- **Perfection Mindset:** Not required. Needs will evolve with use.

**Weekly Availability (~13 hours):**
- Weekdays: 1 hour/day (5 hours total)
- Weekends: 2 sessions × 2 hours × 2 days (8 hours total)

### 5. Why This Project Matters Now

**The Pain:**
- Lost projects scattered everywhere, abandoned or never started
- Can't find old files, can't recreate past work
- Barely remember what was learned - no compounding benefit

**The Vision:**
- Stop treating projects as random attempts to forget
- Create something that compounds over time
- Enable reflection on past learning

**The Timing:**
- University in ~7 months
- Expecting many ideas and learning opportunities
- Want to be ready to document and share - with the world and with future self

**Note to Future Self:**
> "Think of all the cool projects we've built or tried to build in the past - abandoned, never started, forgotten. Making this website is a statement to change that. Our future selves will thank us for the effort we're putting in now, no matter how difficult it may feel when things get hard."

---

## Session Checklist

- [x] Session 1: Initiation (2026-01-31)
- [x] Session 2: Architecture (2026-02-01)
- [x] Session 3: Planning - FAILED (2026-02-01) - PoC revealed Dioxus SSG broken
- [x] Session 2b: Architecture Revision (2026-02-02)
- [x] Session 3: Planning (Cycle 1) (2026-02-03)
- [x] Session 4: Implementation (Cycle 1) (2026-02-04 to 2026-02-08)
- [x] Session 5: Testing/Catchup (Cycle 1) (2026-02-11)
- [x] Session 6: Tooling (out-of-cycle) (2026-02-18)
- [x] Cycle 2 Session 4: Implementation — Phases 1-8 complete (2026-05-09 to 2026-05-16). Per-form **5/5** (logbook + concepts-v0 + workflows + opinions + resources) + cross-form tagging editorial (2026-05-16). Session F (2026-05-15 → 2026-05-16) shipped the entire scaffolding closeout: **curiosity-log mechanism**, **Task 13 `/create-post` skill rewrite**, **Task 15 PROJECT_PROCESS + CLAUDE.md structural sync** (re-canonicalized to `setup_files/`, all 4 mirrors synced, per-project CLAUDE.md restructured to point at PROJECT_PROCESS), **Task 14 sub-items** (tagging strategy doc + homepage navigation), **POST_SYSTEM.md v1 deletion**, **Phase 8 final verification + plan archive**. Task 10 + first concepts post (hash demo) deferred per user — editorial docs will validate on first organic use.

---

## Session Log

### Session 1 - Initiation (2026-01-31)
- Defined three-part goal: blog, portfolio, monetization
- Identified self as primary user with focus on authoring experience
- Set 6-month targets: 10 articles, 3 demos, $1/week
- Timeline: MVP in 4 weeks, ~13 hours/week available
- Captured motivation: compound learning, gift to future self, university prep

### Session 2 - Architecture (2026-02-01)

**Key Decisions:**

| Decision | Choice | Alternatives Considered | Deciding Factor |
|----------|--------|------------------------|-----------------|
| Framework | Dioxus 0.7 (Rust) | React, Astro, other SSGs | Learning goal + cross-platform potential |
| Hosting | Cloudflare Pages | GitHub Pages, Vercel, Netlify | Free, global CDN, future Workers option |
| Backend (future) | Fly.io | Railway, Shuttle.rs | Dioxus docs recommend, generous free tier |
| Domain | mylearnbase.com | mycodepath.com, myskilldeck.com | Flexibility for non-code topics in future |
| Content format | Markdown + YAML frontmatter | Database, CMS | Simplicity, editor-friendly, portable |
| Content structure | Flat files + metadata | Folder-based hierarchy | Flexibility to reorganize without breaking links |
| Project structure | Minimal, evolve as needed | Pre-defined components/pages dirs | Avoid premature organization |

**MVP Scope:** Homepage, blog list, post pages, series grouping, basic styling, RSS, deploy pipeline. Deferred: portfolio, demos, monetization, comments, search.

**Testing Strategy:** Rust compiler + manual testing + content validation script. E2E deferred.

**Risks Reviewed:** Dioxus SSG maturity (mitigated), markdown processing (resolved), Cloudflare compatibility (resolved), workflow friction (monitor), scope creep (discipline).

**Proof-of-concept required:** Validate Dioxus + markdown + SSG + Cloudflare Pages works before full build.

**Standing review item:** Evaluate code structure refactoring needs each cycle.

### Session 3 - Planning (FAILED) (2026-02-01)

**Intended:** Begin cycle 1 planning with task breakdown.

**Actual:** User correctly insisted on PoC validation before planning. This revealed a critical blocker.

**PoC Results:**

| Component | Status | Finding |
|-----------|--------|---------|
| Dioxus dev server | WORKS | Serves app correctly |
| Dioxus fullstack/router | WORKS | Server functions execute |
| Dioxus SSG (`dx bundle --ssg`) | **BROKEN** | Outputs empty shell, no pre-rendered content despite `/static_routes` endpoint working |
| Zola SSG | WORKS | 195ms build, full pre-rendered HTML with markdown + syntax highlighting |

**Root Cause:** Dioxus 0.7 SSG feature appears non-functional or undocumented requirements exist. The `--ssg` flag doesn't trigger pre-rendering despite correct setup per documentation.

**Impact:** Dioxus cannot fulfill the SSG requirement for zero-cost hosting on Cloudflare Pages. Architecture revision required.

**Options Identified:**
1. **Zola (pure SSG)** - Mature, fast, native Cloudflare support
2. **Leptos SSG** - Experimental, not fully tested
3. **Hybrid (Zola + Rust WASM)** - Static content via Zola, interactive features via Dioxus/Leptos islands

**Decision:** Return to Session 2 for architecture revision before proceeding with planning.

**Artifacts:**
- `poc/` - Failed Dioxus SSG attempt (can be deleted)
- `poc-zola/` - Successful Zola SSG validation

### Session 2b - Architecture Revision (2026-02-02)

**Trigger:** Dioxus SSG PoC failed — framework decision invalidated.

**Key Decisions:**

| Decision | Original | Revised | Rationale |
|----------|----------|---------|-----------|
| Framework | Dioxus 0.7 | Zola | Dioxus SSG broken; Zola validated, mature |
| Backend | Fly.io (future) | Deferred entirely | Not needed for static site or client-side WASM |
| Future interactivity | Not defined | WASM islands (additive) | Self-contained demos embed into static pages |
| Testing | Rust compiler + validation script | `zola check` + manual + LLM screenshots | Simpler toolchain |

**Clarifications:**
- WASM islands are static files served by Cloudflare — no backend required
- Future interactivity is additive, not a rewrite
- Design paralysis identified as key risk — mitigate via theme selection in planning

**Note for Session 3:** Include theme selection as early task to unblock UI work.

### Session 3 - Planning (Cycle 1) (2026-02-03)

**Theme Decision:** Serene
- Dark mode support (required)
- Minimal, blog-focused
- Strategy: Start with Serene, cherry-pick features from Tabi/Abridge later

**Task Breakdown:** 8 tasks created in `tasks.md`
1. Initialize Zola + Serene
2. Configure site settings
3. Set up content structure
4. Test aipack workflow (validate tooling early)
5. Write first post ("Building My Website Part 1")
6. Local verification
7. Deploy to Cloudflare Pages
8. Connect custom domain

**Content Format (draft):** Posts will have reflections/commentary section at top, followed by tutorial-style reproducible steps. Will formalize after testing with first post.

**aipack:** Will test with simple task to validate workflow; heavier use deferred to Cycle 2+.

### Session 4 - Implementation (Cycle 1) (2026-02-04 to 2026-02-08)

**Completed 7 of 8 tasks** (Task 5 intentionally deferred):

| Task | Status | Notes |
|------|--------|-------|
| 1. Initialize Zola + Serene | ✓ | Git submodule, zola 0.22.1 |
| 2. Configure site settings | ✓ | Dark mode toggle, RSS, series/tags/categories taxonomies |
| 3. Set up content structure | ✓ | Homepage, posts section, frontmatter template |
| 4. Test aipack workflow | ✓ | pro@coder validated with Gemini Pro (~$0.03/run) |
| 5. Write first post | Deferred | Writing tutorial post after Session 5 when full process is documented |
| 6. Local verification | ✓ | All features verified including outdate alert, 404, series pages |
| 7. Deploy to Cloudflare Pages | ✓ | Custom build command (Zola not pre-installed on CF) |
| 8. Connect custom domain | ✓ | mylearnbase.com live, HTTPS working |

**Key decisions made during implementation:**
- Series taxonomy uses proper-case names in frontmatter (auto-slugified for URLs)
- Template overrides for descriptive back navigation ("Posts", "Home", "Tags" instead of generic "Back")
- Series link added to individual post pages
- `.log/` removed from public repo tracking
- aipack quick-reference guide created for future sessions

**Issues encountered:**
- Serene templates require certain `[extra]` fields even when features are disabled (outdate_alert_days)
- Cloudflare Pages no longer auto-installs Zola; manual download in build command required
- CSS missing on preview URL due to base_url mismatch (resolved by custom domain)

**Site live at:** https://mylearnbase.com

### Session 5 - Testing/Catchup (Cycle 1) (2026-02-11)

**Four phases completed:**

**Phase A — Codebase Walkthrough:**
- Walked through every file in the project: zola.toml, content structure, all 6 template overrides, static assets, theme submodule
- Identified how Serene's override system works and where each customization lives

**Phase B — Documentation (mdBook):**
- Chose mdBook over plain markdown, MkDocs, or Docusaurus for Rust ecosystem alignment and simplicity
- Created full documentation site: 12 pages across 4 sections (Getting Started, Architecture, Guides, Reference)
- Set up GitHub Actions workflow for auto-deployment to GitHub Pages
- Updated PROJECT_PROCESS.md to include documentation as formal Phase C in Session 5

**Phase C — First Post Written:**
- "Building My Learn Base - MVP" — series order 1 of "Building My Learn Base"
- 12-step tutorial detailed enough for human or AI to recreate the entire project from scratch
- Captures exact versions: Zola 0.22.1, Serene v5.6.1, mdBook 0.5.2, Rust 1.91.0
- Reflections section written by human author
- Established post format convention: reflections (human-only) + tutorial (reproducible steps)
- File naming convention adopted: `YYYY-MM-DD-post-slug.md`

**Phase D — Cleanup & Polish:**
- Enabled GitHub-style alerts (`> [!NOTE]`, `> [!IMPORTANT]`) via Serene v5.6.0+ support
- Removed placeholder test post
- Documented Zola template escaping gotcha in docs and project memory

**Key learnings captured:**
- Zola processes `{{ }}` / `{% %}` even inside code blocks — escape with `{{/*` `*/}}` syntax
- `{% raw %}` does NOT work (shortcode detection runs before Tera)
- For template-heavy posts, describe changes + link to repo rather than inline full templates

**Cycle 1 Status:** All 8 tasks complete. MVP live at https://mylearnbase.com

### Session 6 - Tooling (2026-02-18)

**Out-of-cycle session** — not part of the standard cycle flow.

**Goal:** Reduce friction for creating new blog posts from any Claude Code session, regardless of which project is active.

**What was built:**
- Global Claude Code slash command: `~/.claude/commands/create-post.md`
- Invoked as `/create-post [topic]` from any project, any session
- Uses a 3-phase pattern:
  1. **Phase 1 (interactive):** Gathers topic, checks `.log/` for session history, asks which logs to reference
  2. **Phase 2 (subagent):** Delegates writing to a clean-context Task subagent — no context bleed from current project
  3. **Phase 3 (summary):** Reports created file path, metadata, and next steps
- Posts created as `draft = true` with human-only Reflections placeholder
- Gracefully handles missing project files (no `project.md`, `tasks.md`, or `.log/` required)

**Design decisions:**
- Chose global slash command over MCP server (simpler, sufficient)
- Subagent delegation over inline execution (clean context for writing)
- Interactive gathering stays in main conversation (subagents can't ask questions mid-run)

### Cycle 2 Session 4 - Implementation (partial) (2026-05-09 to 2026-05-10)

**Goal:** Execute the post-system reset per `POST_SYSTEM_PLAN.md` — five-form taxonomy (logbook/cookbook/workflows/opinions/resources) + supporting tools.

**Phases 1-4 landed cleanly (commits `1e30f14`, `bd0d924`, `185265a`, `a09a15d`, `c5a55cb`):**

- **Phase 1 — Section migration:** Deleted 3 superseded drafts. Created 5 form-section `_index.md` files plus `logbook/omni-me/` sub-section. Fixed unanchored `resources/` rule in `.gitignore` that was matching the new Zola section path. Build clean (9 pages, 7 sections).
- **Phase 2 — Theme additions:** Added `extra.superseded_by` banner to project-level `templates/post.html` override (uses `get_page` to auto-resolve title + permalink). Created `templates/shortcodes/demo.html` for self-contained iframe demos with optional caption + standalone link. Default iframe height settled at 480 (per plan example); knob noted in tasks.md.
- **Phase 3 — Tools scaffold:** Greenfield Python package at `tools/` with hatchling backend; 4 entry points (`cite`, `logbook`, `cookbook`, `workflows`) installed via `uv tool install --editable`. Conversion exposed as `logbook publish` subcommand (4 entries, not 5). `_frontmatter.py` hand-rolled TOML reader/writer (Python 3.10 has no `tomllib`); round-trip byte-perfect on a real post. Added Python bytecode ignore to `.gitignore` after the first commit accidentally tracked `__pycache__`.
- **Phase 4 — Capture + publish tools:** `cite` produces commit-pinned GitHub permalinks with per-file dirty check + `--allow-dirty` override; 44ms total per call. `logbook init/what/why/scope/note/publish` end-to-end working; auto-creates per-project `_index.md` on first publish to a new project (corrected after user pushed back on my misframing of "Phase 1 already created it"). Friction fixes added post-Phase-5 findings: `--skip-external-links` on internal `zola check` by default (publish 14.4s → 163ms), `--tags "a,b,c"` flag, `logbook tags <slug> "a,b,c"` subcommand for in-place metadata edit.

**Phase 5 surfaced two gaps that defer Task 10 to next session:**

1. **Showboat not integrated.** The plan was explicit ("A logbook capture is a showboat document", "logbook thin wrapper... wrapping showboat note with section-targeting"); the implementation reinvented section-tracking from scratch (`_capture.append_to_section`) instead. Symptom: smoke-test post's "How do we know it works?" was all `cite` blocks, no `showboat exec` runnable evidence, no `showboat image` screenshot capability. User caught it. Memory saved (`feedback_wrap_existing_tools.md`).
2. **Editorial standard not defined.** Tools mechanically work but produce content that fails the editorial bar: project-internal jargon ("Cycle X / Phase Y") that won't survive process changes or external readers, wall-of-prose formatting, and section-6 evidence conflated with code citations. Single-doc decision: expand Task 14 (`POST_SYSTEM.md`) to include per-form per-section quality criteria + anti-patterns; designed as a living doc.

**Both gaps + the showboat rework + a real Task-10 redo carry forward to next session** (see `tasks.md` "Carry-forward to next session"). The smoke-test artifact (a draft logbook post about the Phase-4 tools) was deleted — re-authoring on the fixed substrate is cleaner than retrofitting.

**Showboat rework landed same session** (after the user pushed back on stopping at the diagnosis): `logbook init` now wraps `showboat init`, new `logbook exec` and `logbook screenshot` subcommands wrap `showboat exec` / `showboat image` via post-append section relocation, `logbook publish` runs `showboat verify` (with `--skip-verify` escape) and copies referenced images to the destination. Confirmed working: a `date -u` exec block correctly fails verify (timestamp drift caught), a deterministic `echo` block passes; full publish round-trip in 194ms with verify on. Memory saved for future sessions: `feedback_wrap_existing_tools.md` (don't reinvent showboat-style tools), `feedback_screenshots_guideline_driven.md` (capture stays human + LLM, not auto-tool).

**Continuation 2026-05-10 (later same day, commits `fd538f3`, `6085732`):**

- **Phase 6 Task 11 — `cookbook init/publish`.** Title-primary positional `<title>` (per-form deviation from logbook's `<slug>`-primary, justified by cookbook titles being public-facing). `--slug` auto-slugified with override; `--from-logbook PROJECT/SLUG` pre-fills section 6 with a Zola-resolvable backlink. Wraps `showboat init` + `showboat verify` (parity with logbook). Flat destination (`content/posts/cookbook/<slug>.md`) — no per-project subdir, unlike logbook. Default `draft = false` per plan; `--draft` opts into review. Cross-form helpers extracted into `_shared.py` (run_showboat, repo_root, mylearnbase_root, zola_check, copy_referenced_images, strip_empty_sections, read_text_arg); logbook refactored to import from `_shared`. Smoke-tested in 181ms; orphan-publish failure mode confirmed (zola check runs after dest write — manual cleanup required on failure). Added `logbook/_drafts/` and `cookbook/_drafts/` to `.gitignore` (plan said "untracked by default" but never gitignored — same precedent as the Phase-3 `__pycache__` add).
- **Phase 6 Task 12 — `workflows publish`.** One-way sync from a source markdown doc (e.g., `PROJECT_PROCESS.md`) to `content/posts/workflows/<slug>.md`. `<source-doc-path>` positional knob; `--slug`/`--title` overrides. First publish writes fresh frontmatter; republish preserves `date`, sets `updated = today`, replaces body, preserves `taxonomies` + `extra`. Zola shortcode escape (`{{ x }}` → `{{/* x */}}`, `{% x %}` → `{%/* x */%}`) made **idempotent** via lookahead/lookbehind — re-publishing an already-escaped doc is a no-op. `--dry-run` prints unified diff; recommended habit before every republish. `_frontmatter.render(fields) → str` extracted from `write()` so the dry-run path doesn't round-trip to disk. Smoke-tested on real PROJECT_PROCESS.md (262 lines) + synthetic Zola-escape test; 163ms publish; verified date preservation with backdated `2026-02-01`.
- **Phase 7 Task 14 v1 seed — `editorial/POST_SYSTEM.md`.** 512-line document covering all five forms with uniform per-form structure (*When to use* → *Tools* → *Editorial per section* → *Anti-patterns*). Designed as reference material for the per-form authoring sessions, not as the final destination.

**Per-form rollout sequence locked 2026-05-10:** separate fresh-context sessions in order — logbook, cookbook, workflows, opinions, resources. Each session produces `editorial/<form>.md`. Memory updated (`project_post_system_doc_may_split.md`). Task 13 (`/create-post` skill rewrite) and Phase 5 Task 10 (real-omni-me logbook entry) follow `editorial/logbook.md`.

### Per-form authoring (1/5): logbook (2026-05-10 to 2026-05-11)

**Goal:** First per-form authoring session — produce `editorial/logbook.md` as a standalone authoring guide and publish it as a workflow post.

**Process:** Walked through Topics 1-6 (why exists, how tools work, section purposes, quality writing with good/bad examples, anti-patterns, end-to-end walk-through), one topic per turn with synthesis-then-react loops. Drafted `editorial/logbook.md` section-by-section after Topics 1-6 converged. Verbosity pass at the end trimmed the `draft = true` mention in section 3 and reworded the §6 soft-ordering rule to acknowledge the pairing-rule exception.

**Tool changes during the walkthrough (hand-verified):**
- `_shared.strip_empty_sections` accepts `required_headers` and raises `ValueError` if any required section is empty.
- `logbook publish` passes `[SECTION_WHAT, SECTION_WHY, SECTION_EVIDENCE]` and refuses to publish if any are empty (caught before destination write).
- `logbook init` `--title` is mandatory; auto-derivation dropped (produced bad titles ~4/5 of the time).
- User reinstall needed: `uv tool install --reinstall ./tools` (or `--editable`).

**Publish:** First real publish failed on a broken `@/posts/cookbook/...` Zola link in a §7 cross-form-link example. Orphan destination cleaned up; example blocks converted to fenced code blocks (syntax teaching) and non-link notation (`[screenshot: foo.png]`) for §6 image references. Second publish clean.

**Final state:**
- `editorial/logbook.md`: 7-section editorial doc, publish-quality voice.
- `content/posts/workflows/authoring-a-logbook-entry.md`: live; `draft = false`, `date = 2026-05-11`.

**Memory entries saved for next-session continuity:**
- `project_logbook_arc_complete.md`
- `feedback_editorial_examples_no_live_markdown.md`
- `feedback_per_form_walkthrough_rhythm.md`

**Carry-forward:** cookbook is the next per-form session (fresh context). Then workflows → opinions → resources. Task 13 (skill rewrite) and Task 10 (real omni-me logbook entry) follow.

### Per-form authoring (2/5): cookbook → concepts redesign (2026-05-11)

**Goal:** Second per-form authoring session — produce `editorial/cookbook.md` as a standalone authoring guide and publish it as a workflow post.

**Actual outcome:** Topic 1 (when to use this form) surfaced that cookbook as defined would not survive the user's LLM-heavy workflow. The user articulated that prompting an LLM to implement a pattern doesn't create authentic intellectual ownership of that pattern, and posting it on mylearnbase would feel cheap. The trigger model (logbook §7 callouts, "I'm doing this twice" recognition) also dissolves when the LLM is doing the recognition.

After exploring direction-setting reframes (rejected as another rhetorical move) and the structural option of dropping the form entirely, the user proposed a third path: **elevate demos into a form-level identity, centered on building interactive demos to come to understand concepts.** The author contribution is the design judgment about what teaches the concept — survivable under heavy LLM use.

**Form redesign:**

- **New form name (provisional):** concepts. Replaces cookbook in the five-form taxonomy.
- **Job:** Build an interactive demo to help the author (and reader) understand a concept the author didn't fully grasp.
- **Trigger:** Cycle-close review of a curiosity log — LLM-tracked during cycle work, reviewed at cycle close, survivors become candidates.
- **Cadence:** Lower than cookbook ever was. Zero per cycle is a normal outcome.
- **Distinction from logbook portfolio demos:** Same `{{ demo() }}` shortcode, different role. Logbook demo = evidence-of-feature; concepts demo = teaching-instrument.

**Artifacts written this session:**

- `editorial/concepts.md` — rough/lightweight v0. Intentionally less prescriptive than `editorial/logbook.md` because the form has zero real posts; the first concepts post (hash demo) will pressure-test the doc and drive its v1. Not yet published as a workflow post (waiting until form has been validated in practice).
- `editorial/logbook.md` updates — added `{{ demo() }}` as a fourth evidence type in §6 (so logbook portfolio demos fold into logbook); swapped all 13 cookbook references for concepts/demo equivalents; rethemed the §7 worked-example note from "trait-bound JWT pattern → cookbook" to "JWT signature verification → concepts demo." Republished cleanly via `workflows publish` (date preserved, updated = 2026-05-11, zola check clean).
- `tasks.md` carry-forward updated with the redesign, the new per-form sequence (workflows next, then opinions, resources), the curiosity-log mechanism design+ship task, and the first concepts post (hash demo) task.

**First concepts post candidate:** A demo explaining what hash functions do (SHA-256 vs SHA-512, avalanche effect, simulated upload-validation handshake), sourced from the user's omni-me upload-validation work where they realized mid-implementation they didn't understand hashes.

**Implications carried forward (not done in session):**

- POST_SYSTEM.md v1's cookbook section is stale; user said don't care, may delete after all per-form editorials are done.
- The `cookbook init/publish` tools (Phase 6) are left in place but unused for concepts. Repurpose-or-retire is downstream.
- The curiosity-log mechanism is provisional shape only — design + ship before first concepts post.

**Memory entries saved:**

- `project_cookbook_to_concepts_redesign.md` (new)
- `feedback_form_design_requires_author_contribution.md` (new — the load-bearing design principle)
- `project_curiosity_log_mechanism.md` (new — the provisional trigger mechanism)
- `project_logbook_arc_complete.md` (updated — now reflects 2/5 progress)
- `project_logbook_vs_cookbook.md` (deleted — superseded by the redesign)

**Carry-forward:** workflows is the next per-form session (fresh context). Then opinions → resources. Curiosity-log mechanism + first concepts post (hash demo) follow. Task 13 (skill rewrite) and Task 10 (real omni-me logbook entry) still queued.

### Per-form authoring (3/5): workflows (2026-05-13)

**Goal:** Third per-form authoring session — produce `editorial/workflows.md` as a standalone authoring guide and publish it as a workflow post.

**Process:** Topics 1-6 walkthrough per the locked rhythm. Two structural decisions surfaced during Topic 1 and reshaped the form's framing:

1. **Binary category split, not ternary.** POST_SYSTEM v1's three categories (LLM-referenced / coding-not-LLM / non-coding-personal) collapsed to two — LLM-referenced and personal-reference — when the user identified that the load-bearing axis is **who reads it in the future**, not whether it's code-related. Both categories can be LLM-collaborative in authoring; consumption is what splits them.
2. **Cat 1 has dual-reader pressure; Cat 2 doesn't.** Cat 1's source doc serves an LLM at session start AND a stranger on mylearnbase; the editorial discipline is "make it work for both, optimize for the human in conflicts." Cat 2's only future reader is future-self.

**Tool changes (Topic 2 surfaced and landed same session):**

- `workflows publish --supersede-from <old-slug>` — net-new operation. Writes new post at new slug + adds `extra.superseded_by` banner to the old post. Both pass `zola check` together.
- `_frontmatter.read_all(path)` — new helper (factored from `read_keys` via a shared `_parse_block_flat`); returns the full nested-dict shape that `render` consumes. Used by the supersession edit on the old post.
- `--slug` semantics tightened: error if `--slug` differs from auto AND a post exists at the auto-slug (orphan prevention). Error message names the fix.
- Image copy added (parity with logbook/cookbook publish) — referenced local images copied to dest dir.
- 9 hand-verified test cases covering first publish, vanilla republish, supersession happy path, three supersession error paths, slug-mismatch orphan prevention, dry-run with supersession note, and existing real post unaffected. Committed `ca69ad4`.

**Editorial decisions (Topics 3-5):**

- **Cat 1 section template:** none prescribed. Initial draft included a descriptive "long-form Cat 1 docs converge on this arc" table — user judged unhelpful and asked it removed. Final stance: "structure follows the source doc," full stop.
- **Cat 2 section template:** deferred pending first real Cat 2 post. Same pattern as concepts — don't prescribe before lived data exists. Memory `feedback_form_design_requires_author_contribution.md` is the load-bearing principle.
- **Jargon rule refinement:** the anti-jargon rule has a finer edge for workflows. When a doc *defines* its process vocabulary, those terms are content (Cycle, Session, Phase as defined in `PROJECT_PROCESS.md`). What stays jargon: *instance references* ("we decided this in Cycle 2 Session 3") and inherited-vocab-without-redefinition ("the M2 milestone" with no anchor). Saved as `feedback_jargon_rule_defines_vs_instances.md`.
- **Writing-well ↔ anti-patterns overlap:** because workflows has no per-section structure, the doc-level "writing well" and form-level "anti-patterns" sections collided at the same level. User flagged the redundancy; anti-patterns trimmed from 7 entries to 2 (Speculative workflow + Trying to rename when intent is supersede). Saved as `feedback_per_form_section_overlap.md` for the next per-form sessions.

**Final state:**

- `editorial/workflows.md`: ~410-line editorial doc.
- `content/posts/workflows/authoring-a-workflows-post.md`: live; `draft = false`, `date = 2026-05-13`.
- Site: 11 pages, 7 sections, 0 orphans, clean.

**Carry-forward:** opinions is the next per-form session (fresh context). Then resources. Curiosity-log mechanism + first concepts post (hash demo) follow. Task 13 (skill rewrite) and Task 10 (real omni-me logbook entry) still queued. Open mechanism question from this session: where the "sync-after-edit-source" reminder lives (source doc / `/create-post` skill / `CLAUDE.md`) — deferred to Task 13 or Task 15. Duplicate-source-docs hygiene is a known sharp edge that needs a meta-process fix (Task 15).

### Per-form authoring (4/5): opinions (2026-05-14)

**Goal:** Fourth per-form authoring session — produce `editorial/opinions.md` as a standalone authoring guide and publish it as a workflow post.

**Process:** Topics 1-6 walkthrough per the locked rhythm. Each topic synthesized POST_SYSTEM v1's 10-day-old opinion-section content + relevant memory entries, pressure-tested against current intent, and locked.

**Topic 1 lock:** willingness-to-post / writing-practice / take-is-the-point framing all still hold. **Dropped** the three origination paths (reactive / reflective / cross-form spillover) from the editorial doc — user identified they don't change handling, so enumerating them was scaffolding not structure.

**Topic 2 lock:** 7-phase workflow table stays canonical. Added title concern via two micro-additions inside existing phases — Phase 1 / starter template annotates "working title is fine"; Phase 6 adds "title revisit (low-stakes glance, time-box it)" as a default-on sub-step of the mechanical pass. No new phase number.

**Topic 3 lock — significant corrections:**

- *Tier 1 substantive feedback mechanism:* LLM **suggests** "want Tier 1 feedback?" on draft share; user accepts or declines per-post. Threads the willingness-to-post needle between auto-critique-pressure and full silence. Tiers 2/3/4 stay request-only.
- *Provocation reframed from opposing-position to extreme-same-direction:* the LLM should propose the user's own argument pushed to absurdity along its existing dimension, not a counter-argument. Memory `feedback_opinions_prompting_modes.md` corrected.
- *Default chain locked:* provocation-first opener, mirror-and-probe consolidates, pause-and-ask between cycles, iterate (provocation→mirror OR multiple-framings→mirror), summary on request closes Phase 1.
- *Letters (C/D/F) dropped:* user pointed out they were misleading without A/B/E. Use names only.

**Topic 4 lock — structural cleanup:**

- *No standalone "Writing Well" section.* The three of four proposed concerns (own the take / length follows take / voice / specificity) overlapped with Phase 4 tier definitions and Phase 6 mechanical checks. Resolution: define each tier/pass check at its application site (Phase 4 tier definitions inline; Phase 6 checklist inline). One definition, no catalog drift.
- *Author disciplines:* slim subsection (own the take + length follows take) for the non-LLM-checkable items.
- *Anti-patterns:* form-level only, no Writing-Well-in-reverse.

**Topic 5 lock:** 6 anti-patterns (user dropped 2 of my initial 8 — running-all-modes and provocation-ceiling — because the chain's "user picks next" already prevents both organically).

**Topic 6 lock — two refinements:**

- *Mechanical pass implements approved fixes directly.* Asymmetry vs. Phase 4: substantive feedback requires user voice/judgment (user reworks prose); mechanical fixes are surface-level and unambiguous once approved (LLM implements). Phase 6 is the one phase where LLM modifies the post.
- *Fast/slow reframed as entry-point spectrum, not binary.* Phases are à la carte; user enters at any phase and walks forward. LLM detects entry point by user-declaration / one-question-ask-if-ambiguous / artifact-inference.

**Publish:** Dry-run clean; published in one shot (no orphan, no zola check failures). Site: 12 pages, 7 sections, 0 orphans.

**Final state:**

- `editorial/opinions.md`: 445 lines (449 → 445 after verbosity pass dropped re-enumerated origination paths + four minor restatements).
- `content/posts/workflows/authoring-an-opinions-post.md`: live; `draft = false`, `date = 2026-05-14`.

**Memory entries saved/updated:**

- `feedback_opinions_prompting_modes.md` (rewritten — corrected provocation to extreme-same-direction; added default chain; dropped letter labels)
- `project_logbook_arc_complete.md` (updated — now reflects 4/5 progress)

**Carry-forward:** resources is the final per-form session (fresh context). Curiosity-log mechanism + first concepts post (hash demo) follow. Task 13 (skill rewrite) and Task 10 (real omni-me logbook entry) still queued.

### Per-form authoring (5/5): resources (2026-05-14)

**Goal:** Final per-form authoring session — produce `editorial/resources.md` as a standalone authoring guide and publish it as a workflow post.

**Process:** Topics 1-6 walkthrough per the locked rhythm. User's repeated framing throughout: "resources is the form I'm least worried about." Topics ran through quickly; Topic 4 (writing-well) skipped entirely as standalone section — third consecutive form to do so (workflows trimmed, opinions dropped, resources skipped).

**Topic 1 lock — POST_SYSTEM v1 reframed:**

- Job sharpened: "**future-you can find them in one place when the need arises**" — motivating scenario is future-you remembering doing a similar project and wanting the consolidated entry point.
- Author contribution is **implicit by curation-by-act** — having used a resource during a project, or saved a bookmark deliberately, IS the curation. LLM does the surface work (gather, organize, format).
- Sub-types: 3 → 2 (project-derived + collection-driven; question-driven dropped because LLM-curated answers would fail the by-act floor).
- Dropped: path-priority ranking (predictive without data), cadence framing (not worth real estate), single-resource boundary question (premature).

**Topic 2 lock:** no form-specific tool (same as opinions). Draft directly at `content/posts/resources/<slug>.md`. `zola check` + `cite` apply as general cross-form tools; no per-form call-out needed. Bookmark-import and `--supersede-from` parallel intentionally absent from the doc.

**Topic 3 lock — three corrections from v1:**

- Sections 7 → 6 (read-state legend dropped as standalone section; folded into §2 summary blockquote when used).
- §5 cross-references to logbook: **soft convention** (not publish-time gate) for the project-derived path.
- Per-bullet structure: descriptive line (LLM-first) + optional context line, fully discretionary with no floor. User stance: "if there's nothing important to be said, then there's nothing to be said other than providing the link."

**Topic 4 skipped** as standalone section (confirmed pattern from `feedback_per_form_section_overlap`).

**Topic 5 lock — four anti-patterns:** title-paraphrase / no-lived-curation / unmarked-mixed-states / vendor-marketing-tone. V1's "no opinion glue" anti-pattern dropped (contradicted Topic 3 lock); "forgetting to bump `updated`" dropped (cross-form hygiene, not per-form).

**Topic 6 lock:** project-derived 7-step walkthrough (trigger → gather → draft → LLM organize → user edit → bidirectional backlink → publish). Collection-driven documented as four divergences from project-derived. Worked example skipped on user request. Frontmatter shape kept inline (no init tool means doc must spell it out).

**Publish:** Dry-run clean; one-shot publish. Doc 165 lines (184 → 165 after verbosity pass cut decorative intro paragraph, cadence-anxiety paragraph, non-existent-tool callouts, and final recap line; plus typo fix).

**Final state:**

- `editorial/resources.md`: 165 lines.
- `content/posts/workflows/authoring-a-resources-post.md`: live; `draft = false`, `date = 2026-05-14`.

**Memory entries saved/updated:**

- `feedback_author_contribution_by_act.md` (new — refinement of `feedback_form_design_requires_author_contribution` covering the by-act-vs-by-prose temporal distinction)
- `project_logbook_arc_complete.md` (updated — arc closed, 5/5 complete; renamed to "all-five-per-form-editorial-arcs-complete")
- `feedback_per_form_section_overlap.md` (updated — resources confirmed pattern across 3 of 5 forms)

**Carry-forward:** Per-form authoring sweep is **complete**. Remaining Cycle 2 work:

- Task 13 — `/create-post` skill rewrite. Form list locked at logbook / concepts / workflows / opinions / resources.
- Task 10 — real omni-me logbook entry. Canonical first logbook entry; validates the full chain on real content.
- Curiosity-log mechanism — design + ship before first concepts post.
- First concepts post (hash demo) — after curiosity-log mechanism is live.
- Phase 8 — cycle close: verification sweep + archive POST_SYSTEM_PLAN.md.
- POST_SYSTEM.md v1 deletion (now unlocked).

### Cycle 2 Session F: Scaffolding sweep (2026-05-15) — curiosity-log + Task 13

**Goal:** Build structural scaffolding for remaining Cycle 2 carry-forward items. User opted to skip the planned validation passes (Task 10 + hash-demo concepts post) — editorial docs will validate on first real use rather than via deliberate dry-runs.

**Curiosity-log mechanism shipped:**

**What landed:**

- `~/.claude/CLAUDE.md` (symlinked from `~/.dotfiles/claude/CLAUDE.md`) — added *Curiosity Capture* section: triggers, location (`<project-repo>/.curiosities/<cycle-id>.md`), cycle-id resolution (grep `Cycle \d+` from project.md, highest match; fallback `current.md` — handles both mylearnbase's `Current Phase:` and omni-me's `Status:` header conventions and img_gen's no-project.md case), entry format, self-bootstrap behavior. Fires in any project session (user picked global-not-conditional placement).
- `~/.claude/CLAUDE.md` Step 2 of session-end protocol — extended to copy `.curiosities/*` → `<parent>/curiosities/<project-name>/` alongside existing log-copy.
- `mylearnbase/.gitignore` — added `.curiosities/` (parallel to `.log/`).
- `mylearnbase/.curiosities/cycle-2.md` — seeded with header + format reminder + 1 backfilled entry (hash curiosity from omni-me upload validation, already documented in `editorial/concepts.md` worked sketch).
- Omni-me bootstrap deferred — happens lazily on first append per the self-bootstrap rule. Not pre-modifying that repo from inside mylearnbase.

**Task 13 — `/create-post` skill rewrite shipped:**

- File: `~/.dotfiles/claude/commands/create-post.md` (symlinked from `~/.claude/commands/create-post.md`). 106 lines, replacing the 100-line single-form Reflections-+-Tutorial pattern from Session 6 (2026-02-18).
- New shape: **routing skill**, not content-generation skill. Old subagent-delegation pattern dropped — most forms (logbook/concepts/opinions/resources) operate in the main conversation now where iteration is the point.
- Phase 1 prompts for form. Phase 2 reads `editorial/<form>.md` as source of truth. Phase 3 anchors per-form tools + non-negotiables (each form section names what the LLM does NOT draft — opinions' take, logbook §7 voice-bearing, resources without lived curation). Phase 4 surfaces tag-drift awareness. Phase 5 verification + form-specific summary.
- Cookbook removed from form list; concepts replaces it per the 2026-05-11 redesign. Original Task 13 spec said "logbook / cookbook / workflows / opinions / resources"; lived state is "logbook / concepts / workflows / opinions / resources."

**Decisions locked this session:**

- Cycle-id rule: highest `Cycle \d+` match in `project.md`. Survives both projects' header conventions and any future drift.
- Detection threshold: bias toward capturing ("false positives cheap, missed captures unrecoverable"). Cycle-close review filters resolved/faded ones.
- Self-bootstrap: LLM creates `.curiosities/` + adds gitignore entry on first append in any project. Zero per-project setup needed.

**Carry-forward changes:**

- Task 10 (real omni-me logbook entry) — deferred per user.
- First concepts post (hash demo) — deferred per user. Hash curiosity preserved in `cycle-2.md` for when the user revisits.
- Cycle-close review pass workflow — design lands in Task 15 (PROJECT_PROCESS + CLAUDE.md sync).
- Memory entry `project_curiosity_log_mechanism.md` flips from "provisional, not yet implemented" → "shipped" at session end.

Remaining Cycle 2 scaffolding queue: Task 14 sub-items (tagging strategy doc, home-page navigation), POST_SYSTEM.md v1 deletion, Phase 8 verification sweep + archive plan.

### Cycle 2 Session F (cont'd): Task 15 shipped (2026-05-16)

**PROJECT_PROCESS + CLAUDE.md structural sync + post-system integration.**

- All four `PROJECT_PROCESS.md` copies now identical (329-line canonical at `setup_files/PROJECT_PROCESS.md`; 331-line mirrors at root, `projects/mylearnbase/`, `projects/omni-me/` with MIRROR banners). Re-established setup_files as the canonical per user direction; omni-me had been the lived master during Cycle 2 drift.
- Post-system additions in canonical: Session 4 planning trigger identification, Session 5 capture cadence at feature-landing commits, Session 6 **Phase D** (cycle-close curiosity review + portfolio-demo identification — both are discovery work, not fix code), End-of-Session step 7 (parent-sync `.curiosities/` alongside `.log/`), new top-level **Post System** section with form-to-trigger table.
- `.curiosities/` added to Project Documentation Structure section with explicit gitignore/parent-sync semantics (also clarified the same for `.log/`, which was implicit before — user caught the gap during the propagation pass).
- **Structural fix to CLAUDE.md drift class** (user chose path 2 of 3 when offered light-touch vs structural vs defer). Per-project `mylearnbase/CLAUDE.md` and `omni-me/CLAUDE.md` no longer duplicate end-of-session steps — they point to `PROJECT_PROCESS.md` § End-of-Session Protocol as the single source of truth. Eliminates the failure mode that left mylearnbase/CLAUDE.md on the old 5-session model (Session 4 = Implementation) while omni-me/CLAUDE.md had moved to 6-session (Session 5 = Implementation). Parent `productive_learning/CLAUDE.md` "Sessions 1-5" → "Sessions 1-6".
- Published `content/posts/workflows/project-development-process.md` via `workflows publish setup_files/PROJECT_PROCESS.md`. Zola check clean.

**Remaining Cycle 2 scaffolding queue:** Task 14 sub-items (tagging strategy doc, home-page navigation), POST_SYSTEM.md v1 deletion, Phase 8 verification sweep + archive plan.

### Cycle 2 Session F (cont'd): Task 14 sub-items shipped (2026-05-16)

**Tagging strategy doc + homepage navigation.**

- `editorial/tagging.md` (148 lines): style conventions, decision rules, anti-patterns. Cross-form (not per-form), so lighter than logbook.md (950 lines) but heavier than concepts.md v0 (200 lines). Two user-driven design corrections during drafting:
  1. **No canonical aliases table.** Initial draft included an aliases table for tracking resolved synonyms. User pushed back: that creates an update treadmill (every new tag triggers a doc edit + workflow republish). Resolved by dropping the table entirely — ambiguity gets resolved in conversation at post-creation time, no central catalog.
  2. **Opinion-form caveat on the 3-7 tag bar.** User flagged that opinion posts can legitimately span many tags (short prose, wide-reaching take). Per-post bar reframed: 3-7 is a default scope-matched count, not a length-matched constraint.
- Discovery hooks: `/create-post` Phase 4 references `editorial/tagging.md` first, then the existing grep. `PROJECT_PROCESS.md` § Post System lists `tagging.md` in the editorial source-of-truth list (cross-form companion to the five per-form docs).
- Published as `content/posts/workflows/tagging-strategy.md`. PROJECT_PROCESS.md republished from `setup_files/` (tags `["post-system", "meta", "process"]` preserved by `workflows publish` republish path; `updated = 2026-05-16` set automatically).
- **Bulk tag fixes** (3 posts; user shifted to fix-now after seeing the small scope): `ui-development` → `ui` in `autonomous-ui-development-with-playwright-mcp.md` (real drift); `authoring-a-workflows-post.md` got tags `["post-system", "meta"]`; `project-development-process.md` got `["post-system", "meta", "process"]`. Two suspected drifts (`apis` and `dev-setup`) turned out to be phantoms — `apis` was a code-block example in the resources authoring post, `dev-setup` vs `project-setup` is a legitimate distinction.
- **Homepage navigation v1:** `zola.toml` `[extra].sections` expanded from 1 to 6 entries (`posts` first, then forms in cadence order: logbook → workflows → resources → opinions → concepts).
- **Homepage iteration (after local preview review):** user caught that the concepts nav link 404'd (orphan cookbook section never renamed during 2026-05-11 redesign) and that the home recent-posts widget surfaced only pre-Cycle-2 archive posts as "recent" (theme default pulls only top-level pages). Five fixes landed in sequence:
  1. Created `content/posts/concepts/_index.md`; removed orphan `content/posts/cookbook/` section.
  2. Overrode `templates/home.html` to aggregate recent posts across all subsections (top-level + form sections + one nested level for `logbook/<project>/`).
  3. Added form-badge `[<form>]` after each post title on home recent list so post type is visible at-a-glance.
  4. Moved 9 pre-Cycle-2 top-level posts to `content/posts/archive/` via `git mv`; added `aliases = ["/posts/<slug>/"]` to each (Zola generates JS+meta-refresh redirect pages, preserving original URLs). Internal cross-links between archived posts rewritten from `@/posts/<file>.md` to `@/posts/archive/<file>.md` (sed; 10 link rewrites across 5 posts).
  5. Rebuilt `/posts/` as a split aggregator (`templates/posts_aggregator.html`) — shows recent posts grouped by form (logbook / concepts / workflows / opinions / resources / archive), each section heading linking to its section page, with empty-form noting when there's no content yet.
- Final site state: 15 pages, 8 sections, 0 orphans, `zola check` clean. Old URLs resolve via aliases. Home + /posts/ both show meaningful recent-activity surfaces.

**Remaining Cycle 2 scaffolding queue:** POST_SYSTEM.md v1 deletion, Phase 8 verification sweep + archive plan.

### Cycle 2 Session F (cont'd): cycle close (2026-05-16)

**POST_SYSTEM.md v1 deletion + Phase 8 final sweep + plan archive.**

- `editorial/POST_SYSTEM.md` deleted (30 KB, 512 lines). Six editorial docs supersede it: 5 per-form (`logbook`, `concepts`, `workflows`, `opinions`, `resources`) + 1 cross-form (`tagging`). The v1 seed served its purpose as reference material for the per-form authoring sweep; per-form docs are now the source of truth.
- `POST_SYSTEM_PLAN.md` moved to `.archive/post-system-reset/POST_SYSTEM_PLAN.md` via `git mv` (preserves history).
- **Phase 8 verification passes:**
  - `zola build` clean: 15 pages, 7 sections, 0 orphans
  - `zola check --skip-external-links` clean: 0 broken links
  - All originally-published top-level posts (pre-Cycle-2-reset) resolve at original URLs (7 confirmed; the plan's "9" was off by 2 due to the 3 deleted in Phase 1 leaving 7, plus the MVP post = 7 still present at original paths)
  - `/create-post` (no args) prompts for form selection — verified in skill Phase 1

**Cycle 2 closed.**

Cycle 2 summary across all sessions:
- Phases 1-8 complete (section migration → theme additions → tools scaffold → core capture tools → smoke test → remaining per-form tools → editorial sweep → cycle close)
- Cookbook form redesigned as concepts mid-cycle (2026-05-11) — first major form definition pivot
- Six editorial docs shipped (5 per-form + tagging)
- 7-step end-of-session protocol consolidated into PROJECT_PROCESS.md (single source of truth) with curiosity-log + parent-sync integration
- `/create-post` skill rewritten as a router
- Five tools (`cite`, `logbook`, `cookbook`, `workflows`) shipped, cross-project, plus showboat integration
- Homepage navigation surfaces all five forms

Cycle 3 entry point: open. Likely candidates per memory: real-content validation (the deferred Task 10 omni-me logbook entry; first concepts post hash-demo) once the user has lived use of the system, or omni-me work continues with the new post system in play.
