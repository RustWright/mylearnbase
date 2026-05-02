# mylearnbase post-system reset — plan

## Status
Final — ready for save-to-mylearnbase and approval.

## Context

This plan exits a long meta-conversation about how to write blog posts for mylearnbase, triggered when an attempt to draft a Cycle 2 retrospective for omni-me (using the `/create-post` skill) surfaced fundamental issues with the post system itself rather than just the drafts:

- The skill assumes every post is a build-from-scratch tutorial — wrong shape for retrospectives, decision logs, progress reports.
- Posts have drifted toward "polished tutorial for an unspecified audience" when the user's original goal was a personal lab notebook for future-self recall.
- LLM-drafted 5000-word tutorials are unfact-checkable in any reasonable time, leaving the user reading them superficially and not trusting what got published.
- First-person voice in posts conflates LLM-generated work with human authorship, which bothers the user when reading their own posts back.

Through ~14 turns the user converged on a five-form taxonomy (chronicle / cookbook / process / opinion / resources) plus two demo modes (embedded / standalone). The full taxonomy lives in private memory at `~/.claude/projects/-home-me-productive-learning-projects-omni-me/memory/project_blog_post_taxonomy.md` — referenced as the source of truth for format rules.

## How to read this plan

The plan splits into two layers:

- **Layer A — locked-in decisions.** Settled in this session; execute as-stated unless something genuinely surprising surfaces.
- **Layer B — proposed designs.** Starting points for discussion during the mylearnbase execution sessions. Refine each before implementing. The proposals are detailed enough to act as a prompt for that discussion, not as specifications to follow blindly.

This split exists because the planning session settled the shape of the work (what we're building, why, in what order), but the user wants to engage with the *specifics* (per-form skeletons, LLM/human split, validation rules, specific tool commands) interactively rather than have them pre-decided. Read each Layer B section as "here's a reasonable starting design — argue with it."

---

## Layer A — locked-in decisions

### A1. Scope and shape of the work

- **Option A (full tool work in scope).** Multi-sitting mylearnbase session expected, ~4 sittings totaling 6-10 hours of work.
- **Tool path:** fork showboat's Go codebase first to ship something usable sooner. Future Rust rewrite tracked as a separate plan.
- **Go installation required.** `command -v go` returns nothing; first step of the showboat sittings is `sudo apt install golang-go` (or tarball install).

### A2. Directory structure (committed)

Final tree under `content/posts/` after migration:

```
posts/
├── _index.md                          # existing, retained
├── <existing 8 published posts>.md    # untouched — URL continuity
├── chronicles/
│   ├── _index.md                      # new section
│   └── omni-me/
│       └── _index.md                  # per-project chronicle index
├── cookbook/
│   └── _index.md
├── processes/
│   └── _index.md
├── opinions/
│   └── _index.md
└── resources/
    └── _index.md
```

Decisions baked in:
- Per-project subfolders only under `chronicles/`. omni-me is the first; future projects each get their own subfolder when chronicled.
- Cookbook / processes / opinions / resources stay flat — over-organizing them prematurely costs more than it saves.
- Existing 8 published posts stay flat in `content/posts/`. URL continuity preserved; no `@/posts/` cross-link rewrites needed.
- Each new section gets an `_index.md` (Zola requires it for indexing/feeds).
- No new templates for v1 — `templates/post.html` renders all five forms generically.

### A3. Migration / cleanup (sitting 1)

1. Delete all three current drafts:
   - `content/posts/2026-04-26-cycle-2-four-perspective-review.md`
   - `content/posts/2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md`
   - `content/posts/2026-04-26-omni-me-cycle-2-closing-sitting.md`
2. Create new directories and `_index.md` files per A2.
3. `grep -rn '@/posts/' content/` — confirm same set of references minus the deleted drafts (none of the 8 published posts reference the deleted ones).
4. Verify Zola builds: `cd mylearnbase && zola serve --drafts`. Confirm 8 published posts resolve at original URLs; new section pages render as empty listings.

### A4. Sittings outline

- **Sitting 1** — directory restructure, `_index.md` files, draft post-skeleton scaffolds, migration of existing drafts, Zola build green. Includes Layer B1 discussion. ~1-2 hours.
- **Sitting 2** — Go install, fork showboat, build green, modify `verify` to emit permalinks, MVP `preflight` for chronicles. Includes Layer B2 discussion. ~2-3 hours.
- **Sitting 3** — Layer B3 build-out (whichever `extract-publishable` / `scaffold` / additional `preflight` work survives discussion). ~2-3 hours.
- **Sitting 4** — write a real first-published chronicle for omni-me end-to-end as smoke test (whatever omni-me work is current at that point — not a Cycle 2 retrospective). Update `/create-post` skill. Lock in `mylearnbase/POST_SYSTEM.md`. ~1-2 hours.

### A5. Plan storage location

Save this plan as `mylearnbase/POST_SYSTEM_PLAN.md` so the next mylearnbase session can reference it directly without re-loading the conversation context.

---

## Layer B — proposed designs (refine during execution)

Each proposal below is a reasonable starting point. **Discuss before implementing.** Don't treat these as final specs.

### B1. Per-form skeletons (proposed; refine in sitting 1)

Skeletons stored at `templates/post-skeletons/<form>.md`. Reference material the user copy-pastes when starting a post.

Proposed shapes (each to be refined in sitting 1 discussion):

- **Chronicle:** lede / topic-by-topic sections / "Queued for the next cycle". Voice: first-person on lede, "Queued", and explicit interpretation lines only. Project-by-project sectioning inspired by Willison weeknotes and DeVault status updates.
- **Cookbook:** framing paragraph / "Use when" / "The pattern" (code) / "When NOT to use" / "Why" / "See also". Decision-shape posts go here; preferred over ADR.
- **Process:** lede / "The shape" / "Phase 1..N" / "What this catches" / "What it costs" / "Variants". Human writes all prose; LLM scaffolds.
- **Opinion:** lede / "The setup" / "The claim" / "Why I think this is right" / "What I expect the strongest objection to be" / "What would change my mind". Each H2 has an HTML-comment writing prompt; human fills.
- **Resources:** lede / grouped link sections / "What I'm still looking for". Annotations are entirely human-written.

Each skeleton should also include:
- HTML-comment fences marking `<!-- HUMAN -->` vs `<!-- LLM-OK -->` regions (the boundary is part of B2's discussion).
- A validation reminder block at the bottom (HTML-commented).

**Open for sitting 1 discussion:** exact section headings per form, frontmatter fields needed, where to mark voice constraints, whether any form's skeleton is over-specified or under-specified.

### B2. LLM/human contribution split (proposed; refine in sitting 1)

| Form | LLM may draft | Human must write | Forbidden for LLM |
|---|---|---|---|
| Chronicle | Structured fact bullets, permalink generation, "what changed" lists, disposition tables | Lede, voice/interpretation lines, "Queued for next" prose, any first-person sentence | Lede prose, opinion sentences, any "I think"/"I felt" line |
| Cookbook | Pattern extraction from chronicle, "Use when"/"When NOT" bullets if grounded in chronicle, code-block formatting | Framing paragraph, "Why" section, "See also" curation | The "Why" section — load-bearing argument |
| Process | Phase-name suggestions, consistency checks against project docs, table-of-phases summary | All prose | Prose. LLM scaffolds, human writes. |
| Opinion | Header scaffolding, writing prompts as HTML comments, copy-edit pass after human content | All prose | All claim-stating sentences, supporting evidence, the steelman + response |
| Resources | Metadata extraction from URLs, de-dup against existing posts | Selection of resources, every annotation, grouping decisions | Annotations |

**Open for sitting 1 discussion:** is the "may draft" column too permissive anywhere? Where the line lives for cookbook (the "Why" being human-only is opinionated). Whether process/opinion really need such tight LLM constraints, or whether scoped LLM help is OK.

### B3. Accuracy / validation (proposed; refine in sitting 2-3)

| Form | Validation | When | Failure mode |
|---|---|---|---|
| Chronicle | Code references verified by `showboat verify`; permalinks resolve to HTTP 200; named things have hyperlink or inline parenthetical | Pre-publish | Block publish |
| Cookbook | Same as chronicle, plus source-chronicle backlink resolves | Pre-publish | Block publish |
| Process | Named phases/artifacts grep-checked against `PROJECT_PROCESS.md` and `project.md` | Pre-publish | Warn only |
| Opinion | All external URLs return 200; no bare references to private memory paths | Pre-publish | Block publish |
| Resources | Every link in body returns 200 | Pre-publish + monthly cron | Block publish for new posts; cron emails dead-link list |

Implementation idea: `scripts/preflight.sh <post-path>` detects form from directory and dispatches.

**Open for sitting 2-3 discussion:** which validations should actually block vs warn (block-publish discipline can become friction), whether monthly cron is worth setting up, whether the chronicle's "named things must have hyperlink" check is mechanically feasible or aspirational.

### B4. Showboat fork — specific commands (proposed; refine in sittings 2-3)

**Locked in (Layer A):** fork showboat to Go codebase living at `mylearnbase/tools/showboat-fork/`. True fork, not a submodule. Could be promoted to its own GitHub repo later if portfolio matters.

Proposed command surface (refine before implementing):

- **Keep as-is:** `init`, `note`, `exec`, `image`, `pop`.
- **Modify `verify`:** emit GitHub permalinks (resolve `git remote get-url origin` + commit SHA + matched file:line into a permalink URL). Block when working tree is dirty.
- **Modify `extract`:** split into `extract-log` (existing behavior) and `extract-publishable` (clean version with permalinks substituting grep results, archived log at `tools/showboat-fork/_logs/`).
- **Add `scaffold <form> <slug>`:** copy matching skeleton, fill date+slug, open in `$EDITOR`.
- **Add `note --section <name>`:** target a specific H2 in the chronicle.
- **Add `preflight <post-path>`:** form-aware validation wrapper.

Tests in Go's `testing` package: `verify_test.go`, `extract_test.go`, `scaffold_test.go`, `preflight_test.go`.

**Open for sitting 2-3 discussion:** which commands are MVP vs stretch (current proposal: sitting 2 ships `verify` + chronicle `preflight` only; sitting 3 ships the rest). Whether `scaffold` should be a Go subcommand or a bash script (lower bar). Whether `note --section` is worth the parsing complexity. Whether the dirty-tree block on `verify` is too strict.

### B5. Critical files to modify (proposed; concrete file list)

- `mylearnbase/content/posts/chronicles/_index.md`, `chronicles/omni-me/_index.md`, `cookbook/_index.md`, `processes/_index.md`, `opinions/_index.md`, `resources/_index.md` — six new section indexes
- `mylearnbase/templates/post-skeletons/{chronicle,cookbook,process,opinion,resources}.md` — five skeleton starters
- `mylearnbase/tools/showboat-fork/cmd/<verify,extract,scaffold,preflight>/main.go` — Go fork modifications
- `mylearnbase/scripts/preflight.sh` — form-aware dispatcher
- `~/.claude/commands/create-post.md` — rewritten skill (asks form first)
- `mylearnbase/POST_SYSTEM.md` — final user-facing rules doc, mirrors taxonomy memory

Files to delete: the three drafts named in A3.

### B6. Verification checklist (proposed; concrete success criteria)

- `zola build` succeeds with zero warnings.
- All 8 currently-published posts resolve at their original URLs.
- Five new section index pages render.
- `go install ./...` produces `~/go/bin/showboat` responding to `--help` with new subcommands.
- `showboat verify` runs against the smoke-test chronicle and produces valid GitHub permalinks for every code reference.
- `showboat preflight` exits 0 on the smoke-test chronicle, 1 on a deliberately broken copy.
- `showboat scaffold cookbook test-pattern` creates the expected file with correct frontmatter and structure.
- Smoke test (sitting 4): user authors one new chronicle entry end-to-end (`scaffold` → write → `verify` → `preflight` → flip `draft = false` → `zola build`).
- `grep -rn '@/posts/' content/` returns same set as before minus deleted drafts.
- `/create-post` invoked without args prompts for form selection; refuses LLM-drafted content for human-only sections.

---

## Memory updates needed (post-exit)

Save a feedback memory: when producing implementation plans, distinguish locked-in decisions (settled this session) from proposed designs (starting points for execution-session discussion). The current plan was over-specifying details that the user wanted to keep open.

## Save target

This plan file copies to `mylearnbase/POST_SYSTEM_PLAN.md` so the next mylearnbase session can start by reading it.
