# Tasks - Cycle 2 (Post-System Reset)

**Created:** 2026-05-09 (Session 3)
**Objective:** Implement the five-form post system and supporting tools per `POST_SYSTEM_PLAN.md`.
**Source of truth:** `POST_SYSTEM_PLAN.md` — every task below points to a section there for detailed spec; if a task feels under-specified, the answer is in the plan.

Sequencing follows the natural dependency chain (later phases assume earlier phases have landed); deviations are fine where the dependency is genuinely absent. Open implementation knobs from the plan get resolved at task-execution time — not before.

---

## Phase 1 — Migration & directory setup

### 1. Delete superseded drafts
- [x] Remove `content/posts/2026-04-26-cycle-2-four-perspective-review.md`
- [x] Remove `content/posts/2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md`
- [x] Remove `content/posts/2026-04-26-omni-me-cycle-2-closing-sitting.md`
- [x] Confirm `grep -rn '@/posts/' content/` — actual: 12 → 10 (tasks.md noted "13 → 11"; drift was in baseline labeling, drop matches expected)

### 2. Create new section structure
- [x] `content/posts/logbook/_index.md` and `content/posts/logbook/omni-me/_index.md`
- [x] `content/posts/cookbook/_index.md`
- [x] `content/posts/workflows/_index.md`
- [x] `content/posts/opinions/_index.md`
- [x] `content/posts/resources/_index.md`
- [x] Each `_index.md` sets `outdate_alert` + `outdate_alert_days` per cross-form starting candidates (logbook 120, cookbook 365, workflows **180** [knob settled — LLM-referenced default; post-only category overrides per-page], opinions `outdate_alert = false` + placeholder days=180, resources 180)
- [x] `zola build` clean (9 pages, 7 sections, 0 warnings, 626ms); `zola check` clean (no broken links)

## Phase 2 — Theme template additions

### 3. Superseded-by banner
- [x] Add render block to `templates/post.html` (project-level override, not theme submodule) for `extra.superseded_by` (banner above outdate_alert, uses `get_page` to resolve to title + permalink). Frontmatter convention: `superseded_by` is a content-relative path like `posts/cookbook/foo.md`.
- [x] Smoke-test confirmed: banner renders with `callout warning` class, links auto-populate from target post

### 4. Demo shortcode
- [x] Create `templates/shortcodes/demo.html` — `<figure>` wrapper, `<iframe>` w/ `loading=lazy` + 1px themed border, optional `<figcaption>`, standalone-link
- [x] Default iframe height **480** (knob settled — matches plan example; per-call override available)
- [x] Smoke-tested 3 invocations against `static/demos/test/` placeholder: default-height + figcaption ✓, custom-height (240) + figcaption ✓, custom-height (200) + no figcaption ✓ — all rendered correctly

## Phase 3 — Tools package scaffold

### 5. `mylearnbase/tools/` Python package
- [x] `tools/pyproject.toml` with `[project.scripts]` entries for `cite`, `logbook`, `cookbook`, `workflows` (4 entries — knob settled: conversion exposed as `logbook publish` subcommand, not a 5th entry point, mirrors cookbook/workflows convention)
- [x] `src/mylearnbase_tools/` skeleton: `__init__.py`, `cite.py`, `logbook.py`, `cookbook.py`, `workflows.py` — each with argparse + stub handlers
- [x] Installed via `uv tool install --editable /home/me/productive_learning/projects/mylearnbase/tools` (4 executables on PATH)
- [x] Verified `--help` for all 4 top-level commands and subcommands (logbook init/what/why/scope/note/publish, cookbook init/publish, workflows publish)

### 6. Shared frontmatter helper (`_frontmatter.py`)
- [x] `read_keys(path, keys)` — line-based extraction with dotted-key support (`extra.outdate_alert_days`, `taxonomies.tags`); returns dict, missing keys absent
- [x] `write(path, fields_dict)` — accepts nested dict; renders top-level keys in canonical order, then `[taxonomies]` + `[extra]` tables; preserves any existing body
- [x] Round-trip sanity check on `2026-02-11-building-my-learnbase-mvp.md`: 7 keys across 3 sections (string/date/bool/int/array) match byte-for-byte after read→write→read

## Phase 4 — Core capture tools

> **Architectural gap surfaced + addressed 2026-05-10:** initial Tasks-8/9 implementation reinvented section-tracking instead of wrapping showboat (plan lines 253, 307). Smoke-test symptom: section 6 was all `cite` blocks, no runnable evidence. **Reworked same day** to use showboat as the substrate: `logbook init` wraps `showboat init`, new `logbook exec` and `logbook screenshot` wrap `showboat exec` / `showboat image` via post-append section relocation, `logbook publish` runs `showboat verify` (with `--skip-verify` escape). `_capture.append_to_section` retained — it's the section-targeting layer logbook adds on top of showboat's structureless append model. See updated Tasks 8 and 9 below.

### 7. `cite` (cross-form, used everywhere)
- [x] Discover repo via `git rev-parse --show-toplevel`; project context via `git remote get-url origin`; works from any GitHub-hosted repo
- [x] Capture `file:line` + line content + HEAD SHA + GitHub permalink (markdown citation block format: `[`path:line`](permalink) at `sha7`` + quoted line content)
- [x] Append to capture file (positional arg); creates parent dirs if needed; preserves prior content with blank-line separator
- [x] Knob settled: per-file dirty check (only the cited file blocks); `--allow-dirty` override; non-GitHub remotes degrade to no-permalink (file:line + SHA still recorded)
- [x] Verified end-to-end: clean cite produces real GitHub permalink (`RustWright/mylearnbase`); dirty rejected; `--allow-dirty` succeeds; bad ref formats and out-of-range lines fail with clear messages; **44ms total** (well under <10s budget)

### 8. `logbook` thin wrapper (showboat-backed)
- [x] `logbook init <project> <feature_name>` — invokes `showboat init` for the title block + showboat-id, then appends our metadata blockquote + 7 section headers. Path: `<repo-root>/logbook/_drafts/<slug>.md`.
- [x] `logbook what/why/scope/note <slug-or-path> [text]` — append plain markdown text to the named section via `_capture.append_to_section`; reads from stdin if text omitted; bare slug resolves under `logbook/_drafts/`.
- [x] `logbook exec <slug> <lang> [code] [--section <header>]` — wraps `showboat exec` (which appends to end-of-file) and relocates the produced fenced blocks into the target section (default: section 6). Pipes stdout/stderr through. Returns the executed command's exit code.
- [x] `logbook screenshot <slug> <path> [--section <header>]` — wraps `showboat image`; relocates the showboat-generated image block into the target section. Capture mechanism stays human-driven (memory: `feedback_screenshots_guideline_driven`).
- [x] `cite --section "How do we know it works?"` still works for code-reference evidence; complements showboat exec/image as a different evidence kind.
- [x] Smoke test: init → what/why → exec (deterministic block) → screenshot (test PNG) → publish-with-verify clean → 194ms total publish.

### 9. Conversion tool — implemented as `logbook publish <slug>` subcommand
- [x] Reads capture, extracts metadata blockquote (Project/Slug/Tags), splits title block from body
- [x] Generates frontmatter via `_frontmatter.write` (title, slug, date=today, draft=true, tags from metadata if present)
- [x] Strips literal `TBD` from tags; prunes empty optional sections (e.g., scope when unused) via `_strip_empty_sections`
- [x] Writes to `<MYLEARNBASE_ROOT>/content/posts/logbook/<project>/<slug>.md` (env var with `~/productive_learning/projects/mylearnbase` fallback); creates dest dir; `--force` to overwrite
- [x] Runs `zola check` after write; failure aborts and prints output (non-zero exit).
- [x] **Auto-create per-project `_index.md`** when missing (mirrors `posts/logbook/omni-me/_index.md` shape, with `<project> Logbook` title/description); publish output notes the creation. Removes orphan-warning friction for first-time-per-project publishes.
- [x] **Friction fixes** (post-Phase-5 findings, applied 2026-05-10):
  - `--skip-external-links` on internal `zola check` by default (publish: 14.4s → 163ms, ~88× speedup); `--full-check` flag for paranoid mode.
  - `--tags "a,b,c"` flag on `publish` to fill tags inline at conversion time.
  - New subcommand `logbook tags <slug> "a,b,c"` to update the metadata blockquote in place.
- [x] **Showboat verify integrated** (2026-05-10 rework): publish runs `showboat verify` on the capture before writing the dest; verify failure aborts publish with the diff printed. `--skip-verify` flag for intentionally non-deterministic captures. Confirmed working: a `date -u` exec block correctly fails verify (timestamp drift); a `echo` exec block passes.
- [x] **Image copy at publish** (2026-05-10): `_copy_referenced_images` scans the body for `![alt](path)` markdown image references, copies local files from the capture dir to the dest dir alongside the post. Plan line 308: "copies the capture file + referenced images to mylearnbase/content/posts/logbook/<project>/<slug>.md."
- [x] Smoke-tested end-to-end on verify-happy-path/showboat-rework captures: 0 orphans, 8 sections after publish, images present in dest, back to 7 sections + 9 pages after cleanup.

## Phase 5 — End-to-end smoke test

### 10. Author one real logbook entry
- [ ] Pick whatever omni-me work is current at the time (NOT a Cycle 2 retrospective) — **deferred until showboat rework lands**, since current logbook impl produces structurally wrong evidence sections
- [ ] Run the full cycle: `logbook init` → capture during work → conversion → `zola check` → flip `draft = false`
- [ ] Confirm published post renders correctly, links resolve, permalinks valid

#### Findings from initial smoke test (2026-05-10, against Cycle 2 work — partial run, not the canonical entry)

- **Capture friction PASSES the <10s budget** by ~200×: each capture command (`init`, `what`, `why`, `scope`, `cite`, `note`, `tags`) runs in 40-50ms. Multi-cite sessions stay under 1 second cumulative.
- **Publish friction was 14.4s** (slow path: `zola check` with external link probing). Fixed in Task 9: default-skip external links → 163ms publish.
- **Architectural gap: showboat not integrated.** Surfaced via the test post's "How do we know it works?" section being all `cite` blocks (code locations) with no runnable evidence (no `showboat exec`, no `showboat image`). Symptom of the broader Tasks-8/9 substrate issue. Blocks completion of Task 10 — re-running the smoke test on real omni-me work has to wait for the showboat rework.
- **Editorial-standard gap.** The test post made me realize tools alone don't enforce content quality: the prose was full of project-internal jargon ("Cycle 2", "Phase 4") that won't survive process changes or external readers, formatting was wall-of-prose hard-to-scan, and the evidence-section conflated "where the code is" with "how we know it works." Fix: expand Task 14's scope (see Phase 7 below).

This is also the validation that capture commands meet the <10 second friction budget. Mechanical budget passed; real-content quality budget did not, and gets addressed via the showboat rework + editorial standard before Phase 6.

## Phase 6 — Remaining per-form tools

### 11. `cookbook init` and `cookbook publish`
- [x] `init <title> [--slug SLUG] [--from-logbook PROJECT/SLUG] [--force]` scaffolds `<repo-root>/cookbook/_drafts/<slug>.md` (knob settled: title-primary positional, slug auto-slugified, --slug override — per-form deviation from logbook's slug-primary shape, justified by cookbook titles being public-facing and higher-stakes). Wraps `showboat init` for the title block + showboat-id; appends metadata blockquote (Slug/Tags/optional From-logbook) + summary blockquote + 5 section headers (sections 2-6 of the 6-section structure; section 1 is the title+summary). `--from-logbook` pre-fills section 6 with a Zola-resolvable backlink if value contains `/`, else a TODO placeholder.
- [x] `publish <capture> [--slug] [--tags] [--draft] [--force] [--full-check] [--skip-verify]` runs `showboat verify` (default on, mirrors logbook), splits metadata/title/body, writes to `<MYLEARNBASE_ROOT>/content/posts/cookbook/<slug>.md` (flat, no per-project subdir — unlike logbook). Default `draft = false` per plan (cookbook captures are polished by publish time); `--draft` opt-in for review. Copies referenced images, strips empty optional sections (5 + 6), runs `zola check`.
- [x] Shared substrate extracted: `_shared.py` holds `run_showboat`, `repo_root`, `mylearnbase_root`, `zola_check`, `copy_referenced_images`, `strip_empty_sections`, `read_text_arg`. Logbook updated to import from `_shared` (no behavior change; round-trip help + module load verified).
- [x] `cookbook tags <slug-or-path> "a,b,c"` for in-place tags edit (mirrors logbook).
- [x] Smoke test end-to-end on a throwaway pattern ("Shared module for cross-form CLI helpers"): init → 4 manual section fills → tags update → publish round-trip in **181ms** (zola check internal-only). Full site build clean (10 → 9 after cleanup, 0 orphans, 519ms). `--draft` flag correctly flips to draft=true. Empty optional section ("When this breaks down") correctly pruned at publish.
- [x] `.gitignore`: added `logbook/_drafts/` and `cookbook/_drafts/` (plan said "untracked by default" but never gitignored — session-end `git add -A` would otherwise track them; precedent set by Phase-3 `__pycache__` gitignore).
- [x] Editorial signals collected — see "Editorial signals collected" section below.

### 12. `workflows publish <source-doc-path>`
- [x] Argument shape settled: `<source-doc-path>` positional (knob), `--slug`/`--title` overrides. Source doc is the input; title from H1, slug auto-slugified. Different from cookbook's title-positional because workflows is a sync operation, not a draft creation.
- [x] **First publish:** read source, extract H1 as title, strip H1 from body, escape Zola shortcodes, render frontmatter (title, slug, date=today, draft default false), write to `<MYLEARNBASE_ROOT>/content/posts/workflows/<slug>.md`. 163ms.
- [x] **Republish:** detects existing post; preserves `date` (read via `_frontmatter.read_keys`), sets `updated = today`, preserves `taxonomies.tags` + `extra.outdate_alert_days` if present, replaces body. Confirmed with a backdated date (2026-02-01) — date survives, updated reflects today.
- [x] **Zola shortcode escape:** `{{ x }}` → `{{/* x */}}`, `{% x %}` → `{%/* x */%}`. Lookahead/lookbehind in regex makes it **idempotent** — already-escaped pairs are skipped on re-runs (verified: a doc with both raw and pre-escaped pairs escapes only the raw ones).
- [x] **`--dry-run`** prints a unified diff against the current dest (or against empty for first publish). Useful for previewing changes when the source doc is large.
- [x] **`_frontmatter.render(fields)`** added (factored out of `write`) so workflows can compose frontmatter without round-tripping to disk. Avoided the `/dev/shm` hack from the first draft.
- [x] Smoke-tested on real `PROJECT_PROCESS.md` (262-line doc, no shortcodes to escape) + synthetic doc with both inline and code-block Tera syntax. Both clean. Site build: 9 → 10 pages → 9 after cleanup, 0 orphans throughout.

## Phase 7 — Skill rewrite & final rules doc

### 13. Rewrite `~/.claude/commands/create-post.md`
- [ ] Prompt for form first (logbook / cookbook / workflows / opinions / resources)
- [ ] Refuse LLM-drafted content for human-only sections per per-form rules
- [ ] Route to the right per-form workflow

### 14. Author per-form docs in `editorial/` (POST_SYSTEM.md is the seed)
- [x] **v1 seed landed 2026-05-10** at `editorial/POST_SYSTEM.md` — 512 lines, all five forms, structured uniformly (*When to use* → *Tools* → *Editorial per section* → *Anti-patterns*). Designed as reference material for the per-form sessions, not as the final destination.
- [ ] **Per-form rollout sequence** (separate fresh-context sessions, planned 2026-05-10):
  1. `editorial/logbook.md` — first, because Task 10 depends on it
  2. `editorial/cookbook.md`
  3. `editorial/workflows.md`
  4. `editorial/opinions.md`
  5. `editorial/resources.md`
- [ ] Each per-form session pulls the corresponding section from `editorial/POST_SYSTEM.md` v1, refines for that form's lived authoring rhythm, and decides whether the v1 section is replaced with a pointer or removed entirely.
- [ ] We also need a project document that can be referenced when creating new tags because the current strategy for creating tags randomly is creating an incoherent and confused tagging system
- [ ] The current home page has no way to access any of the new type of posts other than direct url entry

### 15. Update PROJECT PROCESS to incorporate the new workflows to support content creation
- [ ] Update and sync all project process documents, Omni me version is currently the most up to date, all others need to match it
- [ ] Add updates that allow easy use of the new workflows, examples are
  - Identifying potential features to log during the planning stage of each cycle so the question is clear when it comes to write the post itself, if something is enough of a feature or not
  - Specify how to make frequent commits, and then when you get to the commit that lands a feature there can be a pause to quickly make the first draft of the capture, if needed certain UI tests that need screenshots can be saved till later and batched so as not to slow down other development
  - Code reviews can identify cookbook entries or other pieces of code that are worth pulling out
  - Code reviews also allow for time to review and see if there are any features worth turning into a demo, depending on how cool it is, and how well it works within the limitations of the demo implementation process
  - Reference the editorial standard on how to use each tool and the quality of content in each section, we should have links to the files, right now since everything is local I'm fine with just pointing to it across the file system boundary, but maybe we should point to a fetchable remote repo link eventually
- [ ] Decide which sort of updates are needed in the shared files like the Claude.md to make the new post content clear and not just recorded in memory files

## Phase 8 — Cycle close

### 15. Final verification sweep
- [ ] Every item in plan's "Execution surface > Verification criteria" passes
- [ ] `zola build` zero warnings; `zola check` clean
- [ ] All 9 originally-published posts resolve at original URLs
- [ ] `/create-post` (no args) prompts for form selection

### 16. Archive plan
- [ ] Move `POST_SYSTEM_PLAN.md` → `.archive/post-system-reset/POST_SYSTEM_PLAN.md`

---

## Notes

- **Where to start (open):** Phase 1 is the natural first move (cheap, unblocks everything else). Phase 2 and Phase 3 are independent; either can run before the other. Phase 4 depends on Phase 3.
- **Open knobs:** treat them as decisions made when the task lands, not in advance. Each one is small enough to settle in-session.
- **Smoke test gate:** Phase 5 is a real go/no-go on the friction budget. If capture is laborious, fix that before cookbook + workflows are built — same friction issue would only get worse.
- **Cross-project tools:** `cite`, `logbook`, `cookbook`, `workflows` are designed to run from *any* project repo, not just mylearnbase. Test from inside `omni-me/` (or another project repo) before declaring done.

---

## Carry-forward to next session

Sequencing decision (user 2026-05-10, corrected): **tooling → docs → real content.** Mechanical tooling first surfaces editorial signals the user couldn't predict up front; the doc gets drafted with those signals in hand; real content follows the doc. Authoring real content before the doc exists would regenerate the same quality issues already identified.

Order:

1. **Phase 6 — cookbook init/publish + workflows publish.** *(2026-05-10: Tasks 11 + 12 both landed ✓. Phase 6 complete.)*
2. **Phase 7 Task 14 v1 seed — `editorial/POST_SYSTEM.md`.** *(2026-05-10 landed ✓. Single document covering all five forms, designed as reference material for per-form sessions.)*
3. **Per-form authoring sessions** *(fresh context each; cookbook → concepts redesign happened 2026-05-11):*
   - Session A: `editorial/logbook.md` *(2026-05-11 ✓ — published as `authoring-a-logbook-entry`)*
   - Session B: `editorial/concepts.md` *(2026-05-11 ✓ — rough/lightweight v0; **form was redesigned from cookbook during this session**, see project.md log)*
   - Session C: `editorial/workflows.md` *(2026-05-13 ✓ — published as `authoring-a-workflows-post`; tool extended with `--supersede-from` + image copy)*
   - Session D: `editorial/opinions.md`
   - Session E: `editorial/resources.md`
4. **Phase 7 Task 13 — `/create-post` skill rewrite.** Built after the remaining per-form docs exist. Prompt for form first, route to per-form workflow. Form list updated: logbook / concepts / workflows / opinions / resources (cookbook removed).
5. **Phase 5 Task 10 — real-omni-me logbook entry.** Built once `editorial/logbook.md` is validated by first real use. The canonical first logbook entry, validating the full chain on real content.
6. **First concepts post — hash demo.** Identified as first candidate during the 2026-05-11 redesign session. Build after the curiosity-log mechanism is shipped and after at least one cycle of curiosity capture has surfaced surviving candidates (the hash curiosity is already known to survive; the mechanism just needs to exist to format it).
7. **Curiosity-log mechanism.** Provisional shape: `<project-repo>/.curiosities/<cycle-id>.md`, gitignored in submodule, parent-synced like `.log/`. LLM appends during cycle work; cycle-close session reviews. Design + ship before first concepts post.
8. **Phase 8 — cycle close.** Final verification sweep, archive plan.

### Cookbook → concepts redesign (2026-05-11)

The "cookbook" form as defined in `POST_SYSTEM.md` v1 (pull out a pattern worth reusing, with code + recognition story as evidence) failed the *satisfying* half of the *useful + satisfying* criterion for this author's workflow. Root cause: heavy LLM reliance for implementation means the pattern itself was rarely the author's intellectual contribution, and the LLM-as-recognizer also dissolves the "I noticed I was doing this twice" trigger. Result: a form that may have fired near-zero times if kept as-is.

**Reframe.** Replace cookbook with **concepts** — interactive demos built to help the author understand something they didn't grasp. The intellectual ownership shifts from "I recognized this pattern" to "I designed this demo to teach me this concept." The latter is LLM-resilient: the LLM can write the code, but choosing what makes the concept teach is the author's work.

**Implications carried forward** (not done in the redesign session):

- `POST_SYSTEM.md`'s cookbook section is stale. The user said "don't care; may delete after all per-form editorials are made." No action this session.
- The `cookbook init/publish` tools (Phase 6) are left in place but unused for concepts. Repurpose-or-retire is downstream.
- `editorial/logbook.md` §6 needs a small addition: interactive demos count as a fourth evidence type (alongside cite, showboat exec, showboat image, external observable). Logbook portfolio demos fold into logbook via this addition rather than living as a separate form. Update queued for after workflows/opinions/resources sessions.
- The provisional sections of `editorial/concepts.md` (5 sections: stake, curiosity moment, demo, what clicked, cross-refs) are starting points; the first real concepts post will reshape them.

The redesign happened entirely in Topic 1 of what was originally planned as a 6-topic walkthrough. Topics 2-6 were skipped because the form was redefined, not documented — prescriptive editorial rules in the abstract would be premature for a form authored zero times.

### Editorial signals collected (running notes for Task 14)

Anything the user comments on about post quality, sample content, or what looks wrong/right during Phase 6 build-and-test. Add inline as bullets with date + context.

- 2026-05-10 (smoke test on Phase-4 work): jargon-heavy prose ("Cycle 2", "Phase 4") meaningless to future-self or external readers. Anchor in dateable concrete events instead.
- 2026-05-10: section 6 evidence was all `cite` blocks; user noted those are *where to look*, not *whether it works*. Real evidence = runnable exec, screenshot, or observable behavior.
- 2026-05-10: wall-of-prose formatting was hard to scan; prefer structured/bulleted layouts when content is enumerable.
- 2026-05-10 (cookbook smoke test): publish doesn't roll back on `zola check` failure — orphan files land in the dest dir even when publish exits non-zero. Same issue exists in logbook publish. Friction signal, not a blocker; could fix via write-temp-then-move, deferred. Editorial implication: include a "if publish fails, also delete `content/posts/<form>/<slug>.md`" step in POST_SYSTEM.md until the tool rolls back automatically.
- 2026-05-10 (cookbook smoke test): `--from-logbook` placeholder is a **friction-positive** safety net — pre-fills a Zola link target that `zola check` validates at publish time, so a forgotten backlink fails loudly rather than silently. Worth noting in POST_SYSTEM.md as a deliberate authoring discipline pattern, not a bug.
- 2026-05-10 (architecture): cookbook destinations are flat (`content/posts/cookbook/<slug>.md`), logbook destinations are per-project nested (`content/posts/logbook/<project>/<slug>.md`). Reason: cookbook patterns are cross-project by definition; per-project subdirs would imply the pattern belongs to one project. Worth documenting in POST_SYSTEM.md so the asymmetry is intentional, not accidental.
- 2026-05-10 (workflows): Category 1 workflows (LLM-referenced docs) have *two* canonical locations now — the source-of-truth in the project repo (read by the LLM at session start) and the rendered post on mylearnbase (read by humans + future-self). The user's prose discipline should treat the project-repo doc as the source — edits flow doc → post, never post → doc. Worth flagging in POST_SYSTEM.md: "edit the doc, then republish; never edit the post directly because the next republish will overwrite."
- 2026-05-10 (workflows): the dry-run/diff output is genuinely useful for a sync tool — gives the user a "what would change?" preview when an upstream doc is large. Worth surfacing in POST_SYSTEM.md as a recommended habit before each republish. Anti-pattern: blind republish without diff review, which loses sight of which paragraphs are new vs. which were already published.
- 2026-05-10 (workflows): three forms now use the same shared `_shared.py` substrate. Each form's per-form module is ~150-250 lines (logbook 580 because of capture subcommands, cookbook 270, workflows 200). Per-form modules feel right-sized; further extraction (e.g., a `_publish_base` mixin) would obscure the actual differences. Hold on extraction until a 4th form joins.
