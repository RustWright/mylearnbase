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
- [ ] Discover project context from `os.getcwd()` and `git remote get-url origin` — must work from any project repo
- [ ] Capture `file:line` + line content + HEAD SHA + GitHub permalink
- [ ] Append to capture file (location passed via flag or env)
- [ ] Decide working-tree-dirty policy (hard reject vs warning) — open knob

### 8. `logbook` thin wrapper
- [ ] `logbook init <project> <feature-name>` — template a fresh capture with the 7-section structure
- [ ] `logbook what <file> <text>` — fill section 3
- [ ] `logbook why <file> <text>` — fill section 4
- [ ] `logbook scope <file> <text>` — fill section 5 (optional)
- [ ] `logbook note <file> <text>` — fill section 7

### 9. Conversion tool (logbook capture → Zola post)
- [ ] Read capture, write frontmatter, optionally generate one-line summary
- [ ] Copy capture body + referenced images to `mylearnbase/content/posts/logbook/<project>/<slug>.md`
- [ ] Run `zola check` and `showboat verify` (when exec blocks present) before declaring success

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
