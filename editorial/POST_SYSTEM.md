# Post-system authoring guide

How to author the five forms on mylearnbase. This v1 is a single document covering all five forms; each per-form section is structured to lift cleanly into its own `editorial/<form>.md` later, when authoring rhythms diverge enough to want separate docs.

Companion to `POST_SYSTEM_PLAN.md`. The plan explains *why* the system is shaped this way (decisions, considered alternatives, rationale); this doc explains *how to author* — imperative voice, concrete examples, prescriptive rules.

---

## The five forms at a glance

| Form | One-line job | Voice | Tool surface |
|---|---|---|---|
| **logbook** | Showboat a feature you just built | Descriptive | `logbook` (init/what/why/scope/note/exec/screenshot/tags/publish) |
| **cookbook** | Pull out a pattern worth reusing | Descriptive | `cookbook` (init/publish/tags) |
| **workflows** | Tell future-self/others/an LLM how to do something | Mixed (per post) | `workflows publish` (one-way sync from a source doc) |
| **opinions** | A personal take where the take is the point | User voice, full stop | No form-specific tool — write directly under `content/posts/opinions/` |
| **resources** | Curated external content worth pointing at | Descriptive bullets, opinion glue | No form-specific tool yet — write directly under `content/posts/resources/` |

**Decision rule when forms feel close:**

- If you're writing *about a feature you built* → logbook.
- If you're writing *about a pattern* (could apply to many features) → cookbook.
- If you're writing *steps someone should follow* → workflows.
- If you're writing *a take and the take is the point* → opinions.
- If the value is mostly *pointing at other things* → resources.

When two forms compete: pick one, cross-link the other. Don't try to merge.

---

## Shared baseline (applies to every form)

These rules cross every form. They live here so each per-form section doesn't repeat them. If/when per-form docs split out, this section either stays in a top-level overview file or moves to `editorial/_shared.md`.

### Anti-jargon

No project-internal terms in published prose. Specifically, *do not* write:

- "Cycle 2", "Phase 4", "Session 3" — meaningless to anyone reading a post six months from now, including future-you.
- Internal task IDs, sprint labels, milestone names that have no life outside this repo.
- Sentence structures that assume the reader has the project tree open.

Instead, anchor in **dateable concrete events**: "the work I did in early May", "after switching from Dioxus to Zola", "the second time I rebuilt the post-system tooling." Time anchors and event anchors survive process changes; jargon doesn't.

### Evidence must be runnable, not just citable

The "How do we know it works?" section of any form-with-evidence (mainly logbook; sometimes cookbook) **must contain at least one** of:

- A `showboat exec` block whose output is reproducible — verified by `showboat verify` at publish time.
- A `showboat image` screenshot of observable behavior.
- An externally-verifiable observation ("the live site at `mylearnbase.com` now responds with X").

`cite` blocks alone do not count. They are *where the code lives*, not *whether it works*. A post can be all `cite` and have nothing to verify.

### Scannable formatting

Prefer structured layouts when the content is enumerable:

- Lists over paragraphs when items are parallel.
- Tables over prose when the content has columns.
- Subheadings every ~250 words at most.
- Code blocks for anything that's literally code, even one-liners.

A wall-of-prose page reads as effort the user has to put in to extract the content. Scannable layouts let readers (including future-you scanning at 2am) find what they need fast.

### Zola escape rule

Source content that contains `{{ ... }}` or `{% ... %}` syntax must escape it before publish:

- `{{ x }}` → `{{/* x */}}`
- `{% x %}` → `{%/* x */%}`

This applies *even inside fenced code blocks* — Zola interprets shortcodes pre-Tera. `{% raw %}` does **not** bypass detection.

`workflows publish` does this automatically (and idempotently). For other forms, escape by hand or paste through a sed/regex pass before publishing.

### Draft semantics

- **Logbook**: `logbook publish` writes `draft = true`. Review the post, then flip to `false`. The logbook capture is rough notes; the published post deserves a review pass.
- **Cookbook**: `cookbook publish` writes `draft = false` by default. The cookbook capture has already been through the LLM-first-draft cycle and the prose is intentional. `--draft` opts back into review for a doubtful case.
- **Workflows**: `workflows publish` writes `draft = false` by default. The source doc *is* the canonical artifact; if it's ready for the source doc, it's ready to publish. `--draft` opts in for a sanity preview.
- **Opinions**: `draft = true` by default; flip to `false` only when ready. Living-in-draft for weeks or months is fine.
- **Resources**: `draft = false` once the annotations are accurate.

### Publish failure recovery

When publish writes the destination file *then* fails its post-write check (`zola check`, `showboat verify`), the orphan destination is **not** rolled back. If publish exits non-zero, also delete `content/posts/<form>/<slug>.md` before retrying. (Known limitation — atomic write is on the table for a future revision.)

### Use `--dry-run` before any republish (workflows)

Workflows republish replaces the body wholesale. `--dry-run` shows the diff against the current live post. Skipping it means re-publishing blind: you lose track of which paragraphs are new vs. already published. The diff is also a useful sanity check that the source doc didn't pick up unintended changes.

---

## Logbook

### When to use this form

You just built a feature. Even something small. The job is to record what it does, why it was added, and how you know it works — focused on *the feature*, not on the code patterns it uses. Code-pattern deep dives belong in cookbook.

Cadence: one capture per feature, captured during or right after the feature is functionally complete. Multi-session features defer the capture until the feature lands.

Captures live at `<repo-root>/logbook/_drafts/<slug>.md`, untracked (gitignored).

### Tools (mechanical)

| Command | Purpose |
|---|---|
| `logbook init <project> <feature-name> [--title T] [--force]` | Scaffold a fresh capture with the 7-section structure. Wraps `showboat init` for title block + showboat-id. |
| `logbook what <slug> "<text>"` | Append text to "What does this feature do?" |
| `logbook why <slug> "<text>"` | Append text to "Why was it added now?" |
| `logbook scope <slug> "<text>"` | Append text to "What's in scope (and what's not)?" (optional; section pruned at publish if empty) |
| `logbook note <slug> "<text>"` | Append text to "What's worth remembering or doing next?" (optional; pruned if empty) |
| `logbook exec <slug> <lang> [code] [--section "Header"]` | Run code via `showboat exec`, embed output as evidence (default section 6). |
| `logbook screenshot <slug> <image-path> [--section "Header"]` | Embed an image (already on disk) via `showboat image`. Capture mechanism is human + LLM; the tool is embed-only. |
| `logbook tags <slug> "tag1,tag2,tag3"` | Update the Tags line in metadata. |
| `cite <repo-relative-path>:<line>` | Append a commit-pinned permalink citation to the capture's "How do we know it works?" section (use `--section` to target elsewhere). Form-agnostic. |
| `logbook publish <slug> [--tags] [--draft] [--force] [--full-check] [--skip-verify]` | Convert capture → Zola post under `content/posts/logbook/<project>/<slug>.md`. Runs `showboat verify` (re-runs exec blocks for drift detection) and `zola check`. Auto-creates per-project `_index.md` if missing. |

Authoring flow (the typical happy path):

```
logbook init omni-me oauth-login-google
logbook what oauth-login-google "Users can log in with their Google account."
logbook why oauth-login-google "Per-user identity is the prerequisite for multi-device sync."
logbook scope oauth-login-google "In: Google OAuth + JWT issuance. Out: refresh tokens, other providers."
cite src/auth.rs:42
logbook exec oauth-login-google bash "cargo test auth::"
logbook screenshot oauth-login-google ~/Pictures/login-screen.png
logbook note oauth-login-google "The trait-bound JWT generation pattern might be a cookbook candidate."
logbook tags oauth-login-google "rust,auth,oauth"
logbook publish oauth-login-google
```

### Editorial requirements per section

Captures follow this 7-section structure. Mechanically, sections 1+2 are the title block + metadata blockquote (auto-filled); sections 3-7 are the `## ` headers you fill.

**Section 1 — Title block** *(auto)*

The title is what showboat wrote at init time, derived from `<feature-name>` (e.g., `oauth-login-google` → "Oauth login google"). The title is published as the post's `# heading`, so prefer a feature-name slug that reads as a real phrase. Override with `--title` if the slug-derived version reads badly.

**Section 2 — Metadata blockquote** *(auto)*

Holds `Project`, `Slug`, `Tags`. Stripped at publish — never visible in the post.

**Section 3 — What does this feature do?** *(required)*

One paragraph or 3-5 sentences. Functional, externally-observable. Answer "if a stranger landed on this post, what would they say the feature is?"

- ✓ "Users can log in to omni-me using their Google account."
- ✗ "Implemented the OAuth integration we discussed last week."
- ✗ "Added support for Google authentication, addressing #142 from the backlog."

**Section 4 — Why was it added now?** *(required)*

The motivation. Anchor in dateable concrete events, not project-internal jargon.

- ✓ "Multi-device sync (planned for the next round of work) requires a stable per-user identity. OAuth was the prerequisite."
- ✗ "Cycle 3 priority called for it."

**Section 5 — What's in scope (and what's not)?** *(optional — pruned if empty)*

Two short lists. Useful when the feature's boundary is non-obvious or when you want to head off "but what about X?" questions.

```
In: Google OAuth flow, JWT issuance, /me endpoint.
Not in: refresh tokens, account deletion, other providers.
```

Skip if the feature's scope is obvious from section 3.

**Section 6 — How do we know it works?** *(required, non-empty)*

This is the section that fails most often. The bar:

- **Must include at least one** runnable `logbook exec` block, `logbook screenshot`, or external observable behavior.
- `cite` blocks complement evidence but do not substitute for it. They show *where the code lives*, not *whether it works*.
- Multiple evidence kinds is fine and often better. A test result + a screenshot + a citation is a strong section.
- Every exec block must pass `showboat verify` at publish time. If a block is intentionally non-deterministic (timestamps, network calls), either pin the non-determinism or pass `--skip-verify` with a comment explaining why.

Anti-pattern: section 6 that's all `cite` blocks. That's a tour of the source code, not evidence.

**Section 7 — What's worth remembering or doing next?** *(optional — pruned if empty)*

A holding pen for:

- Decisions that were considered and rejected, with the reasoning.
- "This might be a cookbook entry someday."
- Followups, known gaps, deliberate deferrals.

Keep it terse — bullets are fine. This section absorbs the role of an `EXTRACTS.md` doc: cookbook-candidate observations get noted here in context.

### Anti-patterns (logbook)

- Project-jargon-heavy prose ("In this cycle we added X to address Y from Z"). Strip the meta-vocabulary; tell the story of the feature.
- Section 6 with no runnable evidence — only `cite` blocks.
- A title that's a slug fragment ("oauth-login-google") rather than a real phrase ("OAuth login via Google"). Use `--title` to override.
- Multi-feature captures. One feature per capture. If two features landed together, split or pick the one that's the post.

---

## Cookbook

### When to use this form

You noticed a *pattern* worth pulling out — something that could apply across features or projects. Two valid paths to a cookbook entry:

- **Path (b) — Logbook-derived.** While drafting a logbook entry, you recognize a pattern that deserves its own attention. Pull it out as a sibling cookbook entry.
- **Path (c) — Question-driven.** A problem was hard to figure out, OR has been solved/reused several times, OR is clearly useful to a stranger working on the same problem. Any one trigger is sufficient.

Reflection-driven origination (setting aside time to mine logbooks for patterns) is not a path — judged unrealistic.

Captures live at `<repo-root>/cookbook/_drafts/<slug>.md`, untracked (gitignored). Path-(b) captures sit beside their originating logbook capture. Cross-project references are fine because `cite` permalinks are commit-pinned regardless of where the cookbook draft lives.

### Tools (mechanical)

| Command | Purpose |
|---|---|
| `cookbook init "<title>" [--slug] [--from-logbook PROJECT/SLUG] [--force]` | Scaffold a fresh capture. Title is positional; slug auto-derived; `--from-logbook PROJECT/SLUG` pre-fills section 6 with a Zola-resolvable backlink. |
| `cookbook tags <slug> "tag1,tag2,tag3"` | Update the Tags line. |
| `cite <repo-relative-path>:<line>` | Form-agnostic — append a code citation to the active section by editing. (Cookbook has no per-section append commands; the prose is intentional and written by hand.) |
| `cookbook publish <slug> [--tags] [--draft] [--force] [--full-check] [--skip-verify]` | Convert to Zola post under `content/posts/cookbook/<slug>.md` (flat, no per-project subdir). Runs `showboat verify` and `zola check`. |

After `init`, the capture is yours to fill — the manual-prose sections (2, 4, 5) are the substance of the form. No per-section append commands exist by design: cookbook prose is intentional, not running-notes.

### Editorial requirements per section

The 6-section structure:

**Section 1 — Title + one-line summary blockquote** *(required)*

Title is the post's identity (and the cookbook entry's name when other forms link to it). The summary is a single blockquote immediately after the metadata, reading as the first thing in the published post.

- The summary should let a reader who has just clicked the title decide in one sentence whether to keep reading.
- ✓ "When a family of CLI tools share substrate, extract those helpers into a shared module before the second tool starts duplicating them."
- ✗ "Some thoughts on shared modules in CLI codebases."

Replace the init placeholder. Don't ship with the placeholder text.

**Section 2 — The situation** *(required)*

When does this pattern apply? Describe the recurring shape of the problem — concretely enough that a reader can recognize "yes, that's where I am right now." 2-4 paragraphs.

Descriptive prose follows the LLM-first-draft cycle: LLM drafts → user edits → LLM grammar pass → user finalizes.

**Section 3 — The pattern** *(required)*

What's the move? This is the section where `cite` blocks earn their place (pointing at canonical examples in code), and `showboat exec` blocks are valid *when* the pattern's effect is observable in terminal output (record-and-verify, not interactive demo).

Frame the pattern with prose; show the pattern with code/output.

**Section 4 — Why it works** *(required)*

The principle. *Why* does the pattern hold? When you can name the principle, the pattern survives translation to contexts it wasn't first observed in. LLM-first-draft cycle.

**Section 5 — When this breaks down** *(optional — pruned if empty)*

Antipatterns, edge cases, scopes where the pattern stops applying. Often the most useful section to a reader who's about to misuse the pattern. LLM-first-draft cycle.

Skip if the pattern doesn't have clean failure modes worth naming.

**Section 6 — Where it shows up** *(optional — pruned if empty)*

A growing list of cross-references to logbook entries (or other cookbook entries, workflows, opinions, resources) that exemplify the pattern. Path-(b) origins start with at least one entry (the originating logbook). Path-(c) origins start thin or empty and grow.

Cross-references between forms are bidirectional: when a logbook entry uses an existing cookbook pattern, link from logbook → cookbook *and* (manually, for now) update cookbook section 6.

### Anti-patterns (cookbook)

- Publishing with the init summary placeholder still in place (`"One-line summary of the pattern goes here..."`). The summary is the most-read sentence in the post.
- Section 3 ("The pattern") that's pure code, no prose framing. The cite/exec is the *evidence*; the framing is the pattern's identity.
- Section 4 ("Why it works") that paraphrases section 3. The principle has to be more general than the pattern.
- Letting `--from-logbook` placeholder ship as a TODO. Either replace it with a real Zola link before publish or strip the line.

---

## Workflows

### When to use this form

A workflow describes a **prescriptive process** — how to do something. Three categories, based on whether the workflow needs to be read by an LLM during work:

- **Category 1 — LLM-referenced.** Source-of-truth doc lives in a project repo (e.g., `PROJECT_PROCESS.md`); the LLM reads it at session start. The mylearnbase post is a synced render. Examples: project process docs, agent operating rules.
- **Category 2 — Coding-related, not LLM-referenced.** Procedure for human readers (and future-you). Post on mylearnbase only. Example: *"How I onboard to a new codebase."*
- **Category 3 — Non-coding personal.** Personal practice. Post on mylearnbase only. Example: *"How I run a weekly review."*

Two valid origination paths:

- **(a) Design-of-new-workflow** — building a new process from scratch. The act of designing produces the artifact.
- **(c) Refinement-of-existing-workflow** — had a workflow, used it, learned something, updating it. Expected to be the most common path over time.

Documentation-of-long-standing-existing-practice-from-scratch is judged unrealistic and dropped as a path.

### Tools (mechanical)

| Command | Purpose |
|---|---|
| `workflows publish <source-doc-path> [--slug] [--title] [--draft] [--dry-run] [--full-check]` | One-way sync: read source doc, escape Zola shortcodes (idempotently), strip H1, write to `content/posts/workflows/<slug>.md`. First publish writes fresh frontmatter; republish preserves `date` + sets `updated = today` + replaces body + preserves `taxonomies`/`extra`. |

Workflow publishing covers Category 1. Categories 2 + 3 are drafted directly under `content/posts/workflows/<slug>.md` — no tool involvement.

Authoring flow (Category 1):

```
# Edit PROJECT_PROCESS.md in your project repo until the doc is current.
workflows publish ~/path/to/PROJECT_PROCESS.md --dry-run    # preview the diff
workflows publish ~/path/to/PROJECT_PROCESS.md              # publish
```

`--dry-run` is the recommended habit before any republish.

### Editorial requirements per section

**Category 1 (synced from a source doc):** structure = whatever the source doc has. The doc is canonical and must read as a standalone post; the tool does not reformat. If the source doc reads poorly as a standalone post, **fix the source doc**, not the post.

This is a non-trivial discipline: the doc serves two readers (the LLM at session start, the human reader of the published post) and must work for both. When in doubt, optimize for the human reader — the LLM is more forgiving of stylistic choices than a stranger landing from the front page.

**Categories 2 + 3 (drafted directly):** starting template — refine from real use:

| # | Section | Required? |
|---|---|---|
| 1 | Title + one-line summary | yes |
| 2 | When I use this (trigger / situation) | yes |
| 3 | The procedure (ordered steps) | yes |
| 4 | Why this shape (reasoning behind the choices) | yes |
| 5 | Variations / when to deviate | optional |
| 6 | Origin / how it evolved | optional |

Per-section voice:

- **LLM-heavy** when the workflow describes a practice that emerged through LLM collaboration (e.g., a process for working with an LLM). Descriptive prose; LLM-first-draft cycle.
- **User-first** when the workflow describes a personal practice. Opinion prose.
- **Section-by-section dictation** (lazy mode): user describes shape per-section, LLM writes the prose, user edits.

### Anti-patterns (workflows)

- Editing the published post directly when there's a source doc. The next republish will overwrite your edits. **Always edit the source doc.**
- Blind republish without `--dry-run`. You lose track of which paragraphs are new vs. previously-published.
- Category 1 source doc that reads as project-internal scaffolding ("see Phase 4 of Cycle 2 for context"). The doc must read as standalone. If it doesn't, the post won't either.
- Workflows posted with no real-use refinement — the procedure was invented but never followed. Path (a) is valid but only when the act of designing produced the procedure; speculative procedures are not workflows.

---

## Opinions

### When to use this form

An opinions entry is a personal take where **the take itself is the point**. Not a feature (logbook), not a pattern (cookbook), not a procedure (workflows). Length is whatever the take needs. Voice is yours, full stop. Posts can live in `draft = true` for weeks or months without that being workflow failure.

This is the form you use as a deliberate vehicle to grow as a writer. **The optimization target is willingness to post**, not completeness or polish.

Three origination paths, all valid:

- **(a) Reactive** — born from external triggers (article, conversation, frustration mid-work).
- **(b) Reflective** — born when a perspective has been simmering long enough to write down.
- **(c) Cross-form spillover** — surfaces while drafting another form, pulled out as standalone.

### Tools (mechanical)

No form-specific tool. Draft directly at `mylearnbase/content/posts/opinions/<slug>.md`. Cross-form tools that apply:

- `cite` — for citations to code or artifacts the opinion references.
- `zola check` — at publish time.

The optional starter template (frontmatter + an HTML-comment menu of phase-1 prompting modes) lives at the bottom of this section.

### Editorial requirements

Opinions don't have a section-by-section template — structure is whatever the take wants. The editorial discipline is at the **workflow phase** level, not the section level.

The seven workflow phases:

| Phase | Activity | LLM role | Default or opt-in? |
|---|---|---|---|
| 1. Point-finding | Figure out what's being said and why | Prompting modes (C / D / F); never first-drafter | Default available; skip in spontaneous flow |
| 2. Structure pass | Talk through organization; output is an outline | Discussion partner | Default available; skip in spontaneous flow |
| 3. Drafting | User writes | Silent unless asked | — |
| 4. Substantive feedback | Tier 1 default; tiers 2/3 opt-in | Reviewer per category | Tier 1 default; tier 2/3 opt-in |
| 5. Revision | User revises; loops with phase 4 if desired | Silent unless asked | — |
| 6. Mechanical pass | Grammar, typos, awkward phrasing, broken links | Returns suggestions; user accepts/rejects | Default-on before publish |
| 7. Publish | Flip `draft = false`, run `zola check` | Tool-driven | — |

Two flows are both legitimate:

- **Slow-refinement:** journal/notes accumulate → eventually show to LLM for point-finding → first stab at writing → iterate. Use all phases. `draft = true` for as long as needed.
- **Fast-spontaneous:** think → write → mechanical pass → publish. Skip phases 1, 2, 4 if you know what you want to say.

**Phase 1 prompting modes** (used independently or in combination):

- **(C) Mirror-and-probe** — you share raw thoughts; LLM restates and asks one follow-up; iterate.
- **(D) Multiple framings** — LLM offers three candidate angles for what you might be getting at; you pick closest or none.
- **(F) Provocation** — LLM proposes a strong/wrong/extreme version of the position; you react and find your own definition of "right" by articulating why the proposed version is wrong.

**Direct interrogative questions ("what's the point of this?") explicitly do not work** — they trigger school-essay defenses. Avoid that style.

**Phase 4 substantive feedback** — what's offered and when:

- **Tier 1 (default):** Clarity check, internal consistency, what's missing.
- **Tier 2 (on request):** Steelman.
- **Tier 3 (demonstrate on request):** Specificity gap, overclaiming/underclaiming, emotional truth — applied to a single paragraph as a demonstration.
- **Tier 4 (deferred):** Voice authenticity (revisit once enough posts establish a baseline voice), audience match (revisit when there's an actual audience).

### Anti-patterns (opinions)

- Optimizing for polish over willingness. Half-polished opinions that ship beat fully-polished opinions that don't.
- LLM first-drafting the prose. The take is yours; the LLM helps find it (phase 1) and clean it up (phase 6). It does not write it.
- Treating `draft = true` as a workflow failure. Living in draft is the form's normal state.
- Steelmanning an embryonic take. Tier 2 (steelman) is on-request because steelmanning too early shuts the take down before it forms.

### Optional starter template

```markdown
+++
title = "..."
slug = "..."
date = ...
draft = true
[taxonomies]
tags = []
+++

<!-- Pre-writing modes (optional; ask the LLM for one or several, or skip):
  (C) Mirror-and-probe — share something raw; LLM restates and probes
  (D) Multiple framings — light idea; LLM offers candidate angles
  (F) Provocation — LLM proposes a "wrong" position; you react against it
-->

[your post starts here]
```

The HTML comments are visible while drafting and invisible if rendered without removal — lowest-bar scaffolding.

---

## Resources

### When to use this form

A resources entry **curates external content** (articles, tools, books, repos) with annotations that make each entry useful. The value is mostly in pointing to something else, not in the post's own prose.

Three idiomatic sub-types — same skeleton, situational decorations:

- **Project-derived** — bundle of resources used during a specific project; bidirectional cross-link with the project's central logbook post.
- **Collection-driven** — bookmarks-grown list, often with mixed read-states; uses read-state markers.
- **Question-driven** — written answer to "what should I read on X?"; preserved for reuse; optional context line in summary.

Originating paths:

- **(a) Collection-driven** — primary path. Browser bookmarks accumulate; critical mass triggers a post.
- **(b) Question-driven** — secondary. External prompt drives the post.
- **(c) Project-derived** — secondary. At project completion, bundle the resources used.

When an existing post needs work:

- **Minor maintenance** (link rot, small additions/removals) — edit in place, bump `updated`.
- **Major drift / supersede** — content goal has drifted enough that a new post is warranted. Publish new post, banner the old one with `extra.superseded_by` pointing to the new.

### Tools (mechanical)

No form-specific tool yet. Draft directly at `mylearnbase/content/posts/resources/<slug>.md`. Cross-form tools that apply:

- `zola check` — load-bearing for resources; links break.
- `cite` — rare for resources but available.

Bookmark-folder import is deferred — promote only if manual drudgery surfaces.

### Editorial requirements per section

| # | Section | Required? |
|---|---|---|
| 1 | Title + frontmatter | yes |
| 2 | One-line summary blockquote | yes |
| 3 | Read-state marker legend | optional (include when read-state varies) |
| 4 | Categorized sections (or one flat list) | optional |
| 5 | Annotated entries | yes |
| 6 | Cross-references to logbook | required for project-derived; optional otherwise |
| 7 | Superseded-by banner | rendered automatically when `extra.superseded_by` is set |

**Section 2 — One-line summary blockquote:** names the post for what it is. For collection-driven posts with mixed read-states, mention that ("a mix of read and saved-for-later"). For question-driven, name the originating question.

**Section 5 — Annotated entries:** per-bullet two-mode split:

- **Descriptive part** — what the resource is, what it does. LLM-first-draft cycle.
- **Opinion part** — why it earned its place on this list, why this one over alternatives. User-first.

Both parts often sit in the same bullet — the descriptive-vs-opinion distinction is **bullet-level** for resources, not form-level.

**Read-state markers** (when used — locked in for cross-post consistency):

- **✓** — Read carefully; annotation reflects what was taken from it.
- **~** — Skimmed only; annotation is a surface impression.
- **?** — Saved but unread; annotation is "why I saved it."

Markers preserve recommendation integrity by disclosing epistemic weight per item. Optional when all items share a read-state (typical for project-derived and question-driven).

### Anti-patterns (resources)

- Annotations that just paraphrase the resource's title. The annotation has to add something — why it matters, what to look for, how it landed.
- Unmarked mixed-read-state lists. A reader can't tell what carries epistemic weight.
- Section 5 with no opinion glue. The "why it earned its place" line is what distinguishes a resources post from a list of bookmarks anyone could've made.
- Forgetting to bump `updated` after a minor maintenance edit.

---

## What's not in this v1

- **Per-form authoring rhythms** — when each form is most naturally written (post-feature, post-session, post-reading, etc.). Will emerge from use; document once observed.
- **Cross-form linking conventions** — `cite` vs. Zola internal links vs. inline references. Mostly tooled correctly already; document if convention drift surfaces.
- **Editorial signals from real authoring** — this doc covers the signals collected during the tooling build (see `tasks.md` "Editorial signals collected"). New signals from Task 10 onward should be folded in.

When per-form authoring diverges enough that this doc starts feeling unwieldy, split: each per-form section is structured to lift into `editorial/<form>.md` with no rewriting.
