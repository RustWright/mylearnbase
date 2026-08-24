# Claude Code Instructions

This project follows the structured process defined in `PROJECT_PROCESS.md` (mirror of `setup_files/PROJECT_PROCESS.md`; the canonical source lives there).

## Session Management

**Session start:**

1. Re-verify live state (`git status`, read what you'll touch). Git sync itself is automatic (SessionStart hook) — don't run it by hand. Inherit decisions already agreed in prior sessions; don't re-derive settled context.
2. Read `project.md` to find current state and next session. Confirm with user before proceeding.
3. If resuming mid-session, also read `tasks.md` and `architecture.md` for context.

**Session end:** Logging and git sync are **automatic** (the session hooks — see `~/.claude/CLAUDE.md` § Session Sync): the transcript is rendered into `.log/`, `.log/` + `.curiosities/` are synced to the parent, and work is committed + pushed. Your only end-of-phase job is the content updates in `PROJECT_PROCESS.md` § End-of-Session Protocol — update `project.md`'s session log and `tasks.md`. No `/export`, no manual parent-sync.

**Session model:** Six-session process per `PROJECT_PROCESS.md` § Process Flow (Initiation → Research → Architecture → Planning → Implementation → Code Review). The AI role per session is documented in `PROJECT_PROCESS.md` § AI's Role. **Historical note:** mylearnbase Cycles 1 and 2 used the older 5-session model (Session 1 init, 2 arch, 3 planning, 4 impl, 5 testing); `project.md` preserves that numbering for those cycles as historical record. New cycles follow the 6-session model.

## Current Project State

- Check `project.md` Session Checklist for completed sessions.
- Check the Status / Current Phase field at the top of `project.md` for project state.
- If `tasks.md` exists, check for in-progress work.

## Post System (mylearnbase-specific)

mylearnbase is the home of the **post system** referenced by `PROJECT_PROCESS.md` § Post System. Per-form editorial guides live in `editorial/`:

- `editorial/logbook.md`, `editorial/concepts.md`, `editorial/workflows.md`, `editorial/opinions.md`, `editorial/resources.md`

The slash command `/create-post` routes to the right form. Tools (`logbook`, `cookbook`, `workflows`, `cite`) are installed via `uv tool install` from `tools/` and are cross-project (work from any repo).

## Key Files

- `project.md` — Persistent tracker, decision summaries, session log
- `architecture.md` — Technical decisions with rationale
- `tasks.md` — Current cycle's task list (reset each cycle)
- `editorial/` — Per-form authoring guides for the post system
- `tools/` — Cross-project Python tooling (logbook / cookbook / workflows / cite)
- `content/`, `templates/`, `static/`, `theme/`, `zola.toml` — Zola site
- `docs/` — mdBook documentation (deployed via GitHub Actions to GitHub Pages)
- `.log/` — Raw conversation exports (gitignored here; parent-synced)
- `.curiosities/` — Cycle-scoped curiosity captures (gitignored here; parent-synced)
