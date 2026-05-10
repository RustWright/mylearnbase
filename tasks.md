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

### 7. `cite` (cross-form, used everywhere)
- [x] Discover repo via `git rev-parse --show-toplevel`; project context via `git remote get-url origin`; works from any GitHub-hosted repo
- [x] Capture `file:line` + line content + HEAD SHA + GitHub permalink (markdown citation block format: `[`path:line`](permalink) at `sha7`` + quoted line content)
- [x] Append to capture file (positional arg); creates parent dirs if needed; preserves prior content with blank-line separator
- [x] Knob settled: per-file dirty check (only the cited file blocks); `--allow-dirty` override; non-GitHub remotes degrade to no-permalink (file:line + SHA still recorded)
- [x] Verified end-to-end: clean cite produces real GitHub permalink (`RustWright/mylearnbase`); dirty rejected; `--allow-dirty` succeeds; bad ref formats and out-of-range lines fail with clear messages; **44ms total** (well under <10s budget)

### 8. `logbook` thin wrapper
- [x] `logbook init <project> <feature_name>` — writes capture template at `<repo-root>/logbook/_drafts/<slug>.md` (path knob settled: mirrors cookbook's `<project>/cookbook/_drafts/` layout). Title/timestamp/metadata blockquote auto-populated; sections 3-7 created empty.
- [x] `logbook what/why/scope/note <slug-or-path> [text]` — append to the named section (uses shared `_capture.append_to_section`); reads from stdin if text is omitted; bare slug resolves under `logbook/_drafts/`
- [x] `cite --section "How do we know it works?"` fills section 6 (cite stays form-agnostic; logbook tells it which section)
- [x] Smoke test: full init → what×2 (multi-append) → why → scope → cite → note×2 → published file structurally clean

### 9. Conversion tool — implemented as `logbook publish <slug>` subcommand
- [x] Reads capture, extracts metadata blockquote (Project/Slug/Tags), splits title block from body
- [x] Generates frontmatter via `_frontmatter.write` (title, slug, date=today, draft=true, tags from metadata if present)
- [x] Strips literal `TBD` from tags; prunes empty optional sections (e.g., scope when unused) via `_strip_empty_sections`
- [x] Writes to `<MYLEARNBASE_ROOT>/content/posts/logbook/<project>/<slug>.md` (env var with `~/productive_learning/projects/mylearnbase` fallback); creates dest dir; `--force` to overwrite
- [x] Runs `zola check` after write; failure aborts and prints output (non-zero exit). `showboat verify` deferred to when capture grows exec blocks (none in v1 captures).
- [x] **Auto-create per-project `_index.md`** when missing (mirrors `posts/logbook/omni-me/_index.md` shape, with `<project> Logbook` title/description); publish output notes the creation. Removes orphan-warning friction for first-time-per-project publishes.
- [x] Smoke-tested end-to-end on test-project/test-feature: 0 orphans, 8 sections after publish (auto-created the test-project section), back to 7 after cleanup.

## Phase 5 — End-to-end smoke test

### 10. Author one real logbook entry
- [ ] Pick whatever omni-me work is current at the time (NOT a Cycle 2 retrospective)
- [ ] Run the full cycle: `logbook init` → capture during work → conversion → `zola check` → flip `draft = false`
- [ ] Confirm published post renders correctly, links resolve, permalinks valid

This is also the validation that capture commands meet the <10 second friction budget. If they don't, that's a blocker for the cadence and gets fixed before Phase 6.

## Phase 6 — Remaining per-form tools

### 11. `cookbook init <slug>` and `cookbook publish <slug>`
- [ ] `init` scaffolds `<project>/cookbook/_drafts/<slug>.md` with the 6-section structure (optional `--from-logbook <slug>` for path-(b) origins)
- [ ] `publish` moves draft to `mylearnbase/content/cookbook/<slug>.md`, sets `date`, flips `draft = false`, runs `zola check` (+ `showboat verify` if exec blocks)
- [ ] Argument shape: pick from plan's open-knob candidates

### 12. `workflows publish <name>`
- [ ] First publish: prepend frontmatter, write to `mylearnbase/content/posts/workflows/<slug>.md`
- [ ] Republish: preserve `date`, set `updated = today`, replace body
- [ ] Handle Zola shortcode escaping in source content (`{{/*` `*/}}` for `{{ }}`, `{%/*` `*/%}` for `{% %}`)

## Phase 7 — Skill rewrite & final rules doc

### 13. Rewrite `~/.claude/commands/create-post.md`
- [ ] Prompt for form first (logbook / cookbook / workflows / opinions / resources)
- [ ] Refuse LLM-drafted content for human-only sections per per-form rules
- [ ] Route to the right per-form workflow

### 14. Author `mylearnbase/POST_SYSTEM.md`
- [ ] User-facing rules doc, mirrors the taxonomy
- [ ] Per-form quick-reference cards

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
