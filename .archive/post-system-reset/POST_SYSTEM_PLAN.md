# mylearnbase post-system reset — plan

**Status:** Settled 2026-05-03; ready for execution.

## Context

This plan exits a long meta-conversation about how to write blog posts for mylearnbase, triggered when an attempt to draft a Cycle 2 retrospective for omni-me (using the `/create-post` skill) surfaced fundamental issues with the post system itself rather than just the drafts:

- The skill assumes every post is a build-from-scratch tutorial — wrong shape for retrospectives, decision logs, progress reports.
- Posts have drifted toward "polished tutorial for an unspecified audience" when the user's original goal was a personal lab notebook for future-self recall.
- LLM-drafted 5000-word tutorials are unfact-checkable in any reasonable time, leaving the user reading them superficially and not trusting what got published.
- First-person voice in posts conflates LLM-generated work with human authorship, which bothers the user when reading their own posts back.

Through ~14 turns the user converged on a five-form taxonomy — **logbook**, **cookbook**, **workflows**, **opinions**, **resources** — plus demo augmentation.

## Scope and tooling baseline

Multi-sitting effort. Sitting estimates are starting working values that grow or shrink to fit actual progress.

Tooling: use `showboat` as-is (no fork, no modifications) and build small new helpers:

- `cite` — captures `file:line` + line content + HEAD SHA + GitHub permalink, form-agnostic.
- `logbook` thin wrapper — provides sectioned-aware subcommands (`init`, `what`, `why`, `scope`, `note`).
- `cookbook init` — scaffolds a cookbook draft.
- `cookbook publish` — moves draft from project repo to mylearnbase, sets `date`, runs verification.
- `workflows publish` — syncs source-of-truth doc (or finished draft) into a mylearnbase post.
- conversion tool — turns a logbook capture into a Zola post (frontmatter, summary, image copy).

Implementation language: **Python** for all six tools. Locally available at `python3` (3.10.12 confirmed 2026-05-09). Frontmatter (TOML) handling uses a small hand-rolled helper — `tomllib` arrived in Python 3.11, so we don't have it, but our frontmatter schema is flat and known (the keys defined in the Cross-form frontmatter spec), so a ~30-line line-based reader/writer covers what we need with zero external dependencies. Rationale: Python's stdlib (`subprocess`, `pathlib`, `argparse`) covers everything else; one language across all tools reduces context switching.

**Distribution:** the tools must be invokable from any project repo (e.g., `omni-me/`, future projects), not just mylearnbase — `cite`, `logbook`, and `cookbook` get used during implementation work in whatever project is current. Tools are packaged as a single Python project at `mylearnbase/tools/` with multiple CLI entry points declared in `pyproject.toml`, and installed system-wide via `uv tool install`.

Project layout:

```
mylearnbase/tools/
├── pyproject.toml                 # package metadata + [project.scripts] entry points
├── src/mylearnbase_tools/
│   ├── __init__.py
│   ├── _frontmatter.py            # shared hand-rolled TOML helper
│   ├── cite.py                    # entry: `cite`
│   ├── logbook.py                 # entry: `logbook`
│   ├── cookbook.py                # entry: `cookbook`
│   ├── workflows.py               # entry: `workflows`
│   └── conversion.py              # entry: e.g. `logbook-publish`
```

`pyproject.toml` declares each tool under `[project.scripts]`. Install once with `uv tool install /path/to/mylearnbase/tools` — entry points become available on PATH from any working directory. Development uses `uv tool install --editable <path>` so source edits are picked up without reinstall.

Because tools run from any repo, every command must discover project context from `os.getcwd()` and `git remote get-url origin` rather than assuming a layout relative to the tool's source.

`uv` install (if not already present): `curl -LsSf https://astral.sh/uv/install.sh | sh` — single binary in `~/.local/bin`, no other dependencies.

**Eventual extraction:** when tools mature, extract `mylearnbase/tools/` to a standalone repo. The Python-package + uv-tool structure means the migration is `git filter-repo` plus switching users from `uv tool install <local-path>` to `uv tool install git+https://...`.

Capture commands must run in <10 seconds — if capture is laborious, the continuous-capture cadence collapses silently and posts revert to retrospectives. Python's startup overhead (~50–150ms) is well under this budget.

## Directory structure

Final tree under `content/posts/` after migration:

```
posts/
├── _index.md                          # existing, retained
├── <existing 9 published posts>.md    # untouched — URL continuity
├── logbook/
│   ├── _index.md
│   └── omni-me/
│       └── _index.md                  # per-project logbook index
├── cookbook/
│   └── _index.md
├── workflows/
│   └── _index.md
├── opinions/
│   └── _index.md
└── resources/
    └── _index.md
```

- Per-project subfolders only under `logbook/`. omni-me is the first; future projects each get their own subfolder when their work is logged.
- Cookbook / workflows / opinions / resources stay flat — over-organizing them prematurely costs more than it saves.
- Existing 9 published posts stay flat in `content/posts/`. URL continuity preserved; no `@/posts/` cross-link rewrites needed.
- Each new section gets an `_index.md` (Zola requires it for indexing/feeds). Each `_index.md` declares `outdate_alert` and `outdate_alert_days` per the Serene-theme requirement (the field must be present even when the alert is false). Per-section thresholds are listed below in Cross-form mechanisms.
- No new templates needed in v1 — `templates/post.html` renders all five forms generically. The one theme template addition is the superseded-by banner (see Cross-form mechanisms).

## Migration / cleanup

1. Delete the three superseded drafts:
   - `content/posts/2026-04-26-cycle-2-four-perspective-review.md`
   - `content/posts/2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md`
   - `content/posts/2026-04-26-omni-me-cycle-2-closing-sitting.md`
2. Create new directories and `_index.md` files per the directory structure above.
3. `grep -rn '@/posts/' content/` — pre-deletion baseline (2026-05-02): 13 lines. Expected after deletion: 11 lines (the 2 lines inside the four-perspective-review draft that point outward to a published post disappear with the file). Confirmed: zero published posts reference any of the three drafts.
4. Verify Zola builds: `cd mylearnbase && zola serve --drafts`. Confirm 9 published posts resolve at original URLs; new section pages render as empty listings.

---

## Cross-form mechanisms

These mechanisms apply across all five forms. Per-form sections below state only deltas from these defaults.

### Frontmatter spec

```toml
+++
title = "..."
slug = "..."
date = 2026-05-03           # original publish date; never changes
updated = 2026-05-15        # top-level Zola field; only set if post is edited post-publish
draft = false

[taxonomies]
tags = [...]                # tag-system rationalization is separate future work

[extra]
outdate_alert = true        # see _index.md defaults; per-page can override
outdate_alert_days = 120    # per-form starting values below
+++
```

### Filename convention

`mylearnbase/content/posts/<form>/<slug>.md`. No date prefix on new posts. The 9 existing published posts retain their date-prefixed filenames.

Logbook is the only form with a project subdirectory: `logbook/<project>/<slug>.md`.

### Date handling

- `date` = original publish date. Set once when the post is converted from draft to published. Never changes.
- `updated` = Zola's built-in top-level frontmatter field. Set manually when the post is edited post-publish. Serene's `templates/post.html:97-98` renders "Updated on `<date>`" when `updated` differs from `date`; the stale-banner JS at `main.js:88-101` computes days-elapsed from `updated` when present, falling back to `date`. A single `updated` bump therefore resets both the visible "Updated on" line and the stale-banner timer in one move.
- No edit-bump tool; manual update is fine. If real friction surfaces later, a git hook comparing last-modified to `date` is the small fix.

### Verification at publish

Baseline applies to every form:

- `zola check` — internal and external links.
- Human review pass — catches misattribution, overgeneralization, sequence errors that mechanical checks can't.

Per-form additions are listed inside each form's section below.

### Superseded-by banner

When a post has been replaced by a substantively different newer version (most common for resources, occasional for workflows, rare for logbook/cookbook/opinions):

- Frontmatter flag: `extra.superseded_by = "<slug-of-new-post>"`.
- Theme template addition (`themes/serene/templates/post.html`) renders a banner at the top of the post when this flag is set, linking to the new version.
- Old post stays accessible — preserves inbound links and historical reference.
- Same shape as documentation versioning warnings.

### `outdate_alert_days` starting candidates

The theme already supports `outdate_alert_days` per-section (via `_index.md`) and per-page (via `page.extra` override). The mechanism is uniform across forms; only the recommended starting values differ:

| Form | Starting candidate | Reasoning |
|---|---|---|
| Logbook | 120 days | Features age moderately fast |
| Cookbook | 365 days | Patterns and principles age slowly |
| Workflows (LLM-referenced, synced) | 180 days | Synced regularly via `workflows publish` |
| Workflows (post-only categories) | 365 days | Less likely to be reviewed |
| Opinions | unset (no banner) by default | Takes age unpredictably; judgment per post via `extra.outdate_alert_days` override |
| Resources | 180 days | Most decay-prone form (link rot, field evolution) |

Final values to be locked in during execution.

### Demo augmentation

**Definition:** Demos on mylearnbase are interactive client-side widgets readers can play with — reactive content embedded in a post. Distinct from `showboat exec` (record-and-verify of static terminal output) and from embedded media (video/GIF/screenshots).

**Scope:**

- *In scope*: pure client-side interactive widgets (HTML/JS/CSS, optionally WASM-compiled from any source language).
- *Out of scope*: backend-dependent demos (LLM API keys, databases, server-side processing); external-hosted iframes (Codespaces, hosted apps).
- Static media is **not** classified as demos — it is embedded media in posts and uses standard markdown image / `showboat image` mechanics.

**Embed pattern:** Custom Zola shortcode wrapping a same-origin iframe. Posts call:

```text
{{ demo(name="omni-me/calendar", height=480, caption="Switch month/year to see 5- vs 6-row rendering") }}
```

The shortcode renders a `<figure>` containing the iframe, a `<figcaption>` with the caption text, and an "open standalone" link to the same URL. Outer framing is uniform across posts; demo content keeps native styling (no theme CSS injected into iframes).

**Asset location:** `mylearnbase/static/demos/<project>/<demo-name>/` — self-contained directories. Each demo is a fully functional standalone page; the iframe just embeds it.

**Build workflow for non-JS-native projects (e.g., Rust + Dioxus):**

1. In the originating project, add a workspace member at `<project>/demos/<feature-name>/` — a minimal harness app (10–30 lines) that wraps the feature crate.
2. Build to WASM via the project's toolchain (`dx build --release --platform web` for Dioxus). Output is a self-contained `dist/`: `index.html`, JS shim, `.wasm`.
3. Transfer: `cp -r dist/* <mylearnbase>/static/demos/<project>/<demo-name>/`. Manual `cp` is the starting cadence; promote to `scripts/sync-demo.sh` if friction surfaces.
4. Embed via the shortcode in the post.

The build pipeline is project-specific (Dioxus, Yew, Leptos, TinyGo, Emscripten, etc.) but the **output contract is uniform**: a self-contained `dist/` directory copies into `static/demos/<project>/<name>/` and is reachable as a static page.

**Browser execution model:** All major browsers have run WASM natively since 2017. The non-WASM piece is a tiny JS shim (auto-generated by toolchains like Dioxus) that fetches and instantiates the `.wasm` module and wires up DOM bridge code. From the post's iframe perspective, JS-native and WASM demos are indistinguishable. Cloudflare Pages already serves `.wasm` with the correct `Content-Type: application/wasm` — no hosting work needed.

**Translation rule:** content-shaped, not form-shaped:

| Demo's job | Translation rule | Typical form |
|---|---|---|
| Faithful representation of a specific feature | No translation. Use the project's canonical language; WASM if needed. | Logbook (mostly) |
| Illustration of an abstract pattern | Translation OK. Pick the simplest path — typically JS/HTML. | Cookbook (mostly) |

The form-vs-purpose mapping is a heuristic, not a hard rule.

**Versioning model:** Demos are frozen at copy time — the dist files in `static/demos/...` don't auto-update if the project's source evolves. Same shape as the cite-with-permalink versioning settled for code references. If a newer demo is needed for a future post, copy fresh assets to a versioned path (`/demos/<project>/<name>/v2/`) and update only the posts that should track the new version.

**Tooling delta:**

- *New*: Zola shortcode `demo(name, height, caption)` — lives in `templates/shortcodes/demo.html`.
- *Convention*: project-side `<project>/demos/<feature>/` workspace members for non-JS-native projects.
- *Deferred*: `scripts/sync-demo.sh <project> <demo-name>` for build + copy. Promote from manual when manual gets tedious.

**Cross-form usage:**

- Logbook: most common — faithful-representation demos of implemented features.
- Cookbook: occasional — pattern-illustration demos for abstract concepts.
- Workflows / opinions / resources: rare; available but unusual.

**Open implementation knobs:**

- Default iframe height when the shortcode caller doesn't specify.
- Shortcode-level CSS (border, caption styling) integration with the Serene theme.
- Whether the (deferred) sync script gets a `--dry-run` flag.

---

## Logbook

### Form definition

A logbook entry's job is to **"showboat a feature."** It records and shows off a feature added to a project — answering what the feature does, why it was added, what's in scope, and how we know it works. Focus is on the feature, not on deep code analysis. Code-pattern deep dives belong in cookbook entries, which a logbook entry references rather than re-explains.

**One feature, one post.** Posts are short by virtue of scope (typically 200–800 words). Length is not optimized; the editorial criterion is "useful + satisfying."

### Originating activity & cadence

Logbook captures originate from implementation work. Cadence: continuous capture, frequent publish.

- During implementation: feature → commit → capture, repeat.
- Capture happens during or right after the implementation of each feature.
- Each capture becomes one short post.
- Multi-session features defer their capture until the feature is functionally complete and a final commit is made.

### Capture location & durability

Captures live in the project repo (e.g., inside `omni-me/`), untracked by default. They coevolve with the work but are not part of the project's source tree. Durable until consciously deleted. If captures ever feel valuable enough to track (lost-by-accident regret, sharing across machines), revisit by adding them to git.

This avoids needing to give LLMs cross-repo access to mylearnbase during normal implementation work — drafts stay in the project repo and are copied to mylearnbase only at the publish step.

### Capture structure

A logbook capture is a showboat document with these sections, in order:

| # | Section | Required? | Filled by |
|---|---|---|---|
| 1 | Title (showboat title block: feature name + timestamp) | yes | `logbook init <project> <feature-name>` |
| 2 | Metadata blockquote: `Project`, `Slug`, `Tags` (no `Commit` — see below) | yes | Auto-populated by `logbook init`; tags placeholder filled at conversion time |
| 3 | What does this feature do? | yes | `logbook what <file> <text>` (or stdin) |
| 4 | Why was it added now? | yes | `logbook why <file> <text>` |
| 5 | What's in scope (and what's not)? | optional | `logbook scope <file> <text>` (skip if unused; section disappears if empty) |
| 6 | How do we know it works? *(evidence)* | yes (non-empty) | `cite <file> <path:line>` (code refs with embedded commit SHA + permalink); `showboat exec <file> <lang> <code>` (runnable evidence); `showboat image <file> <path>` (screenshots); `showboat note <file> <text>` (inline commentary) |
| 7 | What's worth remembering or doing next? | optional | `logbook note <file> <text>` — also absorbs the role of the prior `EXTRACTS.md` doc (cookbook-candidate observations get noted here in context) |

No `Commit` field in metadata: each `cite` call records the commit at the moment of citation, so multi-commit features carry multiple SHAs naturally. The cite-embedded commits in section 6 are the source of truth for "when each piece of code was true."

Sample rendered capture (illustrative):

```markdown
# OAuth login via Google
*2026-05-03T15:30:00Z*

> Project: omni-me
> Slug: oauth-login-google
> Tags: TBD

## What does this feature do?

Users can log in to omni-me using their Google account.

## Why was it added now?

Multi-device sync (Cycle 3 priority) requires a stable per-user identity.
OAuth was the prerequisite for storing per-user data on the server.

## What's in scope (and what's not)?

In: Google OAuth flow, JWT issuance, /me endpoint.
Not in: refresh tokens, account deletion, other providers.

## How do we know it works?

[cite block: src/auth.rs:42 — login handler permalink at SHA abc1234]
[showboat exec: cargo test auth:: → 4 tests passed]
[showboat image: login_screen.png]

## What's worth remembering or doing next?

Considered passwordless email magic-links — rejected for now (more
infra). Refresh tokens deferred to Cycle 4. The trait-bound JWT
generation pattern might be worth a cookbook entry.
```

### Tooling delta

- `cite` (cross-form helper) — used heavily here for code references.
- `logbook` thin wrapper — provides `init`, `what`, `why`, `scope`, `note` subcommands wrapping `showboat note` with section-targeting. `init` templates a fresh capture file with the structure above.
- conversion tool — turns a capture into a Zola post: writes frontmatter, optionally generates a summary, copies the capture file + referenced images to `mylearnbase/content/posts/logbook/<project>/<slug>.md`.

### Verification at publish (additions to baseline)

- `showboat verify` — re-runs any embedded exec blocks and diffs output.
- Permalinks captured by `cite` are commit-pinned at capture time and immutable.

### Cross-form interaction

- A logbook entry that uses a code or design pattern worth highlighting in its own right *links* to a cookbook entry rather than re-explaining the pattern.
- The "What's worth remembering or doing next?" section (#7) is the natural place to flag "this might be worth a cookbook entry later" without leaving the capture.
- Cookbook entries link back to the logbook entries that exemplify the pattern.

### Open implementation knobs

- Exact friction-minimization design for capture commands (single command + flags vs. many small commands; TUI vs. CLI; editor integration).
- Conversion tool's internal shape (single module versus multiple modules sharing helpers); packaging is settled (entry point in the tools package).
- `PROJECT_PROCESS.md` Session 4 amendment to incorporate the per-feature capture cadence.
- Where the workflow doc lives: `POST_SYSTEM.md`, `PROJECT_PROCESS.md`, both with cross-refs.

---

## Cookbook

### Form definition

A cookbook entry's job is to **pull out a pattern** worth remembering and reapplying. It answers: what the pattern is, the situation that calls for it, why it works, when it breaks down, and where it shows up. Cross-links bidirectionally with logbook entries that use the pattern. Length is whatever the pattern needs — short is fine, long is fine when the pattern earns it.

### Originating activity & cadence

Two paths (reflection-driven origination — setting aside time to mine logbook entries for patterns — was judged unrealistic and is not a path):

- **Path (b) — Logbook-derived**: while drafting a logbook entry, recognize a pattern that deserves attention but can't share focus with the feature. Pull it out as a sibling cookbook entry, publish on its own cadence.
- **Path (c) — Question-driven**: born when a problem was hard to figure out, OR has been solved/reused several times, OR is clearly useful to a stranger working on the same problem. Any one of those three triggers is sufficient.

### Capture location & durability

Captures live in the originating project repo, untracked by default, at `<project>/cookbook/_drafts/<slug>.md`. Path-(b) captures sit beside their originating logbook capture; path-(c) captures originate in whichever project surfaced the question. Cross-project references are not a problem because `cite` produces commit-pinned permalinks regardless of where the cookbook draft itself lives.

The draft only moves to mylearnbase at publish time, mirroring the logbook flow.

### Capture structure

A cookbook capture is a markdown document with these sections, in order:

| # | Section | Required? | Filled by |
|---|---|---|---|
| 1 | Title + one-line summary blockquote | yes | `cookbook init <slug>` writes the scaffold + frontmatter; user writes the summary by hand (tight prose, no LLM ventriloquism risk because it's just a recap) |
| 2 | The situation | yes | Manual prose — descriptive, follows the LLM-first-draft cycle |
| 3 | The pattern | yes | `cite <file> <line>` for code references; `showboat exec` only when the pattern's effect is observable in terminal output (record-and-verify, not interactive demo); manual prose for framing |
| 4 | Why it works | yes | Manual prose — the principle. LLM-first-draft + user edit |
| 5 | When this breaks down | optional | Manual prose — antipatterns, boundaries. LLM-first-draft + user edit |
| 6 | Where it shows up | optional, grows | Initial: scaffold pre-fills with originating logbook entry (path-b) or starts thin/empty (path-c). Source-code occurrences via `cite`. Grows post-publish — see deferred xref tool |

### Tooling delta

- `cookbook init <slug>` — thin wrapper around `mkdir + write template`, parallel to `logbook init`. Creates the scaffold in `<project>/cookbook/_drafts/<slug>.md` with the 6-section structure and frontmatter stub. For path-(b) origins, accepts an optional `--from-logbook <slug>` arg to pre-fill the back-link in section 6.
- `cookbook publish <slug>` — moves the draft from project repo to `mylearnbase/content/cookbook/<slug>.md`, sets `date`, flips `draft = false`, runs `zola check` and `showboat verify` if the doc has exec blocks.
- `cite` — already form-agnostic; produces permalinks regardless of which form is consuming it.

Tools deferred (revisit if friction surfaces):

- `cookbook xref add <slug> <logbook-entry>` — for growing section 6 after publish. For now: edit the file by hand and bump `updated`.

### Prose drafting workflow

Cookbook entries summarize/describe external patterns; manual-prose sections (2, 4, 5) follow the LLM-first-draft cycle:

1. LLM drafts the section
2. User revises where opinions differ
3. LLM does a grammar / issues pass on the user-revised text
4. User does a final review and decides whether to publish

There is no personal voice to ventriloquize — the content is descriptive. Opinion-shaped posts (essays/opinions) do not use this cycle.

### Verification at publish (additions to baseline)

- `showboat verify` — when the doc has exec blocks.

### Cross-form interaction

- A cookbook entry first drafted in path-(b) origin gets a back-link in section 6 to the originating logbook entry at draft time.
- New logbook entries that *later* use an existing cookbook pattern do not auto-update the cookbook's section 6 — accepted limitation. Detection relies on user memory + pattern recognition. The deferred `cookbook xref add` tool would close this gap mechanically; for now, manual updates are tolerable.

### Open implementation knobs

- `cookbook init` argument shape — slug-only is insufficient because the title can't be reverse-derived. Candidates: `cookbook init <title>` (slug auto-derived via slugify), `cookbook init <slug> <title>` (both explicit), or `cookbook init <title> --slug <slug>` (title primary, slug overridable).
- `cookbook xref add` design — revisit only if back-linking friction surfaces in real use.
- Whether cookbook entries need their own series taxonomy or stay as a flat content section.

---

## Workflows

### Form definition

A workflows entry is a **prescriptive process** — it tells a reader (future-self, others, or an LLM at session start) how to do something. Three categories based on whether the workflow needs to be referenced by an LLM during session work:

- **Category 1 — LLM-referenced**: source-of-truth lives as a doc in the project repo (e.g., `PROJECT_PROCESS.md`); the post on mylearnbase is a synced render of that doc. The doc is what the LLM reads at session start.
- **Category 2 — Coding-related, not LLM-referenced**: post on mylearnbase only. No parallel doc. Example: *"How I onboard to a new codebase."*
- **Category 3 — Non-coding personal**: post on mylearnbase only. Example: *"How I run a weekly review."*

Length is whatever the workflow needs. Voice depends on whether the workflow describes emergent practice (descriptive prose, LLM-first cycle) or personal practice (opinion prose, user-first).

### Originating activity & cadence

Two paths:

- **Path (a) — design-of-new-workflow**: building a new process from scratch (e.g., the POST_SYSTEM design). The act of designing produces the artifact; publishing renders it.
- **Path (c) — refinement-of-existing-workflow**: had a workflow, used it, learned something, updating it. Expected to be the most common path over time.

Path (b) — "documentation of long-standing existing practice from scratch" — judged unrealistic and dropped.

### Capture location & sync model

**Category 1**: source-of-truth doc lives in the project repo. Mylearnbase post is a word-for-word render with frontmatter prepended. Sync via `workflows publish` (automated). The doc is canonical for both LLM and human readers; the post is the published view.

**Categories 2 + 3**: drafted directly in `mylearnbase/content/posts/workflows/`. No parallel doc.

### Capture structure

**Category 1**: structure = whatever the source doc has. The doc is canonical and must read as a standalone post; the tool does not reformat. If the source doc reads poorly as a standalone post, that's a doc-quality issue, not a tooling issue.

**Categories 2 + 3** (starting template — refine from real use):

| # | Section | Required? |
|---|---|---|
| 1 | Title + one-line summary | yes |
| 2 | When I use this *(trigger / situation)* | yes |
| 3 | The procedure *(ordered steps)* | yes |
| 4 | Why this shape *(reasoning behind the choices)* | yes |
| 5 | Variations / when to deviate | optional |
| 6 | Origin / how it evolved | optional |

### Tooling delta

`workflows publish <name>` — new tool:

| Trigger | Tool action |
|---|---|
| First publish | Read source doc (category 1) or finished draft (categories 2/3) → prepend frontmatter (title, slug, `date = today`, `draft = false`, taxonomies, extra) → write to `mylearnbase/content/posts/workflows/<slug>.md` |
| Republish | Read source doc → read existing post's frontmatter → preserve `date` → set `updated = today` → replace body |

Reused: `cite` (form-agnostic permalinks), `showboat` primitives if needed.

Edge case for implementation: if source doc contains Zola shortcode syntax (`{{ }}` or `{% %}`), the tool must escape using `{{/*` and `*/}}` for `{{ }}`, and `{%/*` and `*/%}` for `{% %}`. (Zola processes shortcodes inside markdown code blocks too, and `{% raw %}` does not work because shortcode detection happens before Tera.)

### Prose drafting workflow

Per-post judgment based on content:

- **LLM-heavy** when the workflow describes a practice that emerged through LLM collaboration (descriptive prose, follows the LLM-first-draft cycle from cookbook).
- **User-first** when the workflow describes a personal practice (opinion prose).
- **Section-by-section dictation** (lazy mode): user describes shape per-section, LLM writes the prose, user edits.

### Verification at publish (additions to baseline)

- For category 1, the source doc is the verification basis — if the doc is wrong, the post is wrong.

### Cross-form interaction

- A workflow post may cite cookbook patterns or reference logbook entries that exemplify a step.
- Cookbook entries occasionally reference workflows but typically point the other direction (workflow → cookbook).

### Open implementation knobs

- `workflows publish` argument shape (similar to cookbook init knob — slug alone is insufficient because the title can't be reverse-derived).
- Whether to add a `--dry-run` flag to the publish tool for review before writing.

---

## Opinions

### Form definition

An opinions entry is a personal take, perspective, or reflection where **the take itself is the point** — not a feature (logbook), not a pattern (cookbook), not a procedure (workflows). Length is whatever the take needs; voice is the user's, full stop. Posts can live in `draft = true` for weeks or months without that being workflow failure.

This is the form the user is using as a deliberate vehicle to grow as a writer. The workflow's optimization target is **willingness to post**, not completeness or polish.

### Originating activity

All three paths are valid (no narrowing):

- **(a) Reactive** — born from external triggers (article, conversation, frustration mid-work).
- **(b) Reflective** — born when a perspective has been simmering long enough to write down.
- **(c) Cross-form spillover** — surfaces while drafting another form, pulled out as standalone.

### Capture location & flows

Drafted directly in `mylearnbase/content/posts/opinions/<slug>.md`. No parallel doc.

Two legitimate flows, both supported:

- **Slow-refinement**: ideas collected in journal/notes over time → eventually shown to LLM for point-finding/structure → first stab at writing → iterative refinement. `draft = true` for as long as needed.
- **Fast-spontaneous**: think → write → mechanical pass → publish.

### Workflow phases

| Phase | Activity | LLM role | Default or opt-in? |
|---|---|---|---|
| 1. Point-finding | Figure out what's being said and why | Prompting modes (C/D/F); never first-drafter | Default available; skipped in spontaneous flow |
| 2. Structure pass | Talk through organization; output is an outline, not prose | Discussion partner | Default available; skipped in spontaneous flow |
| 3. Drafting | User writes | Silent unless asked | — |
| 4. Substantive feedback | Tier 1 default; Tier 2/3 opt-in | Reviewer for categories explicitly requested | Tier 1 default, others opt-in |
| 5. Revision | User revises; loops with 4 if desired | Silent unless asked | — |
| 6. Mechanical pass | Grammar, typos, awkward phrasing, broken markdown/links | Returns suggestions; user accepts/rejects | Default-on before publish |
| 7. Publish | Flip `draft = false`, run `zola check` | Tool-driven | — |

The mechanical pass (phase 6) is the safest LLM intervention in the form — pure surface-level — and is the one place where LLM involvement is unambiguously additive. Default-on.

### LLM prompting modes (phase 1)

Three modes — used independently or in combination:

- **(C) Mirror-and-probe** — user shares raw thoughts; LLM restates and asks one follow-up; iterate.
- **(D) Multiple framings** — LLM offers three candidate angles for what the user might be getting at; user picks closest or none.
- **(F) Provocation** — LLM proposes a strong/wrong/extreme version of the position; user reacts and finds own definition of "right" by articulating why the proposed version is wrong.

The asymmetry between (D) and (F) is intentional: (D) approaches from "what's right" (pick from offered options); (F) approaches from "what's wrong" (react against a position). Both lead to clarity through different mental paths.

**Direct interrogative questions ("what's the point of this?") explicitly do not work** — they trigger school-essay defenses. Avoid that style.

### Substantive feedback tiers (phase 4)

| Tier | Categories | Behavior |
|---|---|---|
| 1 — Default | Clarity check, internal consistency, what's missing | Offered when a draft exists; user opts in to use them |
| 2 — On request | Steelman | Available when explicitly asked; depends on how developed the take is |
| 3 — Demonstrate later | Specificity gap, overclaiming/underclaiming, emotional truth | Apply on a single paragraph as a demonstration when user wants to learn what they look like in practice |
| 4 — Deferred | Voice authenticity, audience match | Not offered now. Promotion conditions named below — revisit when conditions are met |

**Category definitions** (what the LLM actually looks for and outputs when each is requested):

- **Clarity check** — finds places where the prose is ambiguous or where a reader could plausibly misread the user's intent. Output: a list of flagged phrasings with the alternative readings that prompted the flag.
- **Internal consistency** — checks whether the arguments hang together. Surfaces contradictions, unsupported leaps, or claims that pull against each other within the post.
- **What's missing** — surfaces questions a reader would naturally ask after reading the post that the post doesn't address. Useful for finding holes the user didn't notice.
- **Steelman** — names the *strongest* counterargument to the user's position and asks whether the post addresses it or needs to. The "strongest" framing is load-bearing — weak strawmen are not acceptable output. Tier 2 rather than default because steelmanning an embryonic take can shut it down before it forms.
- **Specificity gap** *(Tier 3 — demonstrate)* — flags places where the prose is general or abstract and a concrete example would land harder. When the user requests a demonstration, the LLM applies this to a single paragraph and shows the suggested change.
- **Overclaiming / underclaiming** *(Tier 3 — demonstrate)* — flags places where the user is saying more than they actually believe (overclaim) or hedging more than necessary (underclaim). Both distort the take in opposite directions. Demonstrated on a single paragraph on request.
- **Emotional truth** *(Tier 3 — demonstrate)* — flags places where the prose feels sanitized or where the user appears to be underplaying actual stakes or feelings around the topic. The user may choose to acknowledge or keep hidden — judgment per post. Demonstrated on a single paragraph on request.
- **Voice authenticity** *(Tier 4 — deferred)* — would check whether the prose sounds like the user versus generic LLM-flavored content. Deferred as premature: the user does not yet have a corpus that establishes a baseline voice to compare against. **Promotion condition:** enough opinion posts exist that a recognizable voice can be sampled. Revisit at that point.
- **Audience match** *(Tier 4 — deferred)* — would check whether the framing is tuned for a specific reader. Currently unwelcome because the user has no readership and the question would distract or freeze the writing process rather than help it. **Promotion condition:** the user has developed an actual audience (or has a specific reader in mind for a particular post) and *wants* the framing to be tuned for them. Revisit at that point.

### Tooling delta

No new form-specific tools. Reused: `zola check`, optionally `cite` if the opinion references code or other artifacts. The draft sits in `content/posts/opinions/<slug>.md`.

### Template

Optional starter template — frontmatter + an HTML-comment menu of phase-1 modes (rather than direct prompts, which were rejected):

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

### Verification at publish (additions to baseline)

- Mechanical pass (phase 6) is the substantive verification step for the form.
- No external evidence verification — opinions are personal positions, not evidence-based claims.

### Cross-form interaction

- Opinions may reference logbook entries ("the work that prompted this take") or cookbook patterns.
- Logbook tail-comments (the "what's worth remembering" section) can promote into standalone opinion posts when a thought is load-bearing on its own.

### Open implementation knobs

- Refining the prompting-modes list once tried in real drafts.
- Exact mechanics for switching modes mid-conversation.
- Whether the template should evolve to include mode-specific scaffolding (e.g., a "(F) start" template that has the LLM's provocation pasted inline).

---

## Resources

### Form definition

A resources entry curates external content (articles, tools, books, repos) with annotations that make each entry useful to a reader. The value is mostly in pointing to something else, not in the post's own prose.

The form has three idiomatic sub-types — same skeleton, situational decorations:

- **Project-derived**: bundle of resources used during a specific project; bidirectional cross-link with project's closing/central logbook post.
- **Collection-driven**: bookmarks-grown list, often with mixed read-states; uses read-state markers.
- **Question-driven**: written answer to "what should I read on X?"; preserved for reuse; optional context line in summary.

### Originating activity

- **(a) Collection-driven** — primary path. Browser bookmarks accumulate; critical mass triggers a post.
- **(b) Question-driven** — secondary. External prompt drives the post.
- **(c) Project-derived** — secondary. At project completion, bundle the resources used.

A fourth scenario splits into two paths instead of being a fresh-post originator:

- **(d.i) Minor maintenance** — link rot, small additions/removals → edit in place, bump `updated`.
- **(d.ii) Major drift / supersede** — content goal has drifted enough that a new post is warranted → publish new post, banner the old one with `extra.superseded_by` pointing to the new.

### Capture location & mechanism

Drafts directly in `mylearnbase/content/posts/resources/<slug>.md`, regardless of sub-type. No parallel doc.

Capture mechanism: **manual** as starting cadence (open bookmarks, copy URLs+titles into markdown, annotate). A bookmark-folder import tool is deferred — promote only if real friction surfaces.

### Capture structure

| # | Section | Required? | Notes |
|---|---|---|---|
| 1 | Title + frontmatter | yes | `resources init <title>` for scaffold (deferred to execution) |
| 2 | One-line summary blockquote | yes | Names the post for what it is — including read-state mixture for collection-driven, originating prompt for question-driven |
| 3 | Read-state marker legend | optional | Include when read-state varies (mostly collection-driven) |
| 4 | Categorized sections (or one flat list) | optional | Topical grouping when many items |
| 5 | Annotated entries | yes | Link + descriptive note + (optional) "why it's here" line |
| 6 | Cross-references to logbook | required for project-derived; optional otherwise | Bidirectional with project's closing/central logbook post |
| 7 | Superseded-by banner | rendered automatically when `extra.superseded_by` is set | See Cross-form mechanisms |

### Read-state markers

When a list contains items at mixed read-states, use these markers (locked in for cross-post consistency):

- **✓** — Read carefully; annotation reflects what was taken from it.
- **~** — Skimmed only; annotation is a surface impression.
- **?** — Saved but unread; annotation is "why I saved it."

Markers preserve the integrity of recommendations by disclosing epistemic weight per item. Optional when all items share a read-state (typical for project-derived and question-driven posts).

### Annotation drafting workflow

Per-bullet two-mode split:

- **Descriptive part** — what the resource is, what it does → LLM-first-draft cycle, user edits.
- **Opinion part** — why it earned its place on the list, why I picked this one → user-first.

These two parts often sit in the same bullet; the descriptive-vs-opinion distinction is *bullet-level* for resources, not form-level.

### Tooling delta

- Reused: `zola check` (link checking, especially important for resources), `cite` (rare for resources but available).
- New tooling deferred to execution sittings:
  - `resources init <title>` — scaffold creation parallel to other init commands.
  - Bookmark-folder import — only if manual drudgery surfaces.

### Frontmatter delta

The user explicitly declined a separate `extra.last_reviewed` field — `updated` is sufficient as the single date lever. Fewer levers when one will do.

### Verification at publish (additions to baseline)

- `zola check` for links — particularly load-bearing for resources.
- Verify each marker matches actual read-state, annotations remain accurate.

### Cross-form interaction

- **Project-derived posts**: bidirectional cross-link with the closing/central logbook post for the project. The exact mechanism for "which logbook entry serves as the project's center" is a knob — for now, "the most-recently-published logbook post for the project" is the implicit identifier; could become an explicit artifact if real friction surfaces.
- **Collection-driven and question-driven**: typically no cross-form references, but may cite an opinion or cookbook entry if relevant.

### Open implementation knobs

- `resources init` argument shape (similar to cookbook/workflows init knobs).
- Bookmark-folder import tool design (if/when promoted from deferred).
- Mechanism for identifying a project's "closing/central" logbook post — implicit-by-recency for now; revisit if it becomes confusing.

---

## Execution surface

This section consolidates the artifacts the work touches and the verification criteria. Execution sequencing belongs in `tasks.md` (created in cycle Session 3).

### Files to create

- `mylearnbase/content/posts/logbook/_index.md`
- `mylearnbase/content/posts/logbook/omni-me/_index.md`
- `mylearnbase/content/posts/cookbook/_index.md`
- `mylearnbase/content/posts/workflows/_index.md`
- `mylearnbase/content/posts/opinions/_index.md`
- `mylearnbase/content/posts/resources/_index.md`
- `mylearnbase/templates/shortcodes/demo.html` — Zola shortcode for embedded demos
- `mylearnbase/POST_SYSTEM.md` — final user-facing rules doc, mirrors the taxonomy

### Files to modify

- `mylearnbase/themes/serene/templates/post.html` — add superseded-by banner rendering
- `~/.claude/commands/create-post.md` — rewritten skill (asks form first; refuses LLM-drafted content for human-only sections)

### Files to delete

The three superseded drafts in `content/posts/`:

- `2026-04-26-cycle-2-four-perspective-review.md`
- `2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md`
- `2026-04-26-omni-me-cycle-2-closing-sitting.md`

### New tooling

- `cite` — code reference + permalink helper (cross-form)
- `logbook` thin wrapper — `init`, `what`, `why`, `scope`, `note` subcommands
- `cookbook init <slug>` and `cookbook publish <slug>`
- `workflows publish <name>` — sync source doc → mylearnbase post
- conversion tool — capture → Zola post

### Verification criteria

- `zola build` succeeds with zero warnings.
- `zola check` returns clean (no broken internal or external links across all posts and section indexes).
- All 9 currently-published posts resolve at their original URLs.
- Five new section index pages render.
- New helpers respond to `--help` and produce expected outputs.
- `cite` produces valid GitHub permalinks for code references.
- Smoke test: user authors one new logbook entry end-to-end (capture → convert → `zola check` → publish).
- `grep -rn '@/posts/' content/` returns 11 lines (13 baseline minus the 2 lines inside the deleted draft).
- `/create-post` invoked without args prompts for form selection; refuses LLM-drafted content for human-only sections.

---

## Save target

**During execution:** plan lives at `mylearnbase/POST_SYSTEM_PLAN.md` so any mylearnbase session can reference it directly without re-loading the conversation context.

**Post-execution:** archive to `mylearnbase/.archive/post-system-reset/POST_SYSTEM_PLAN.md`. Mirrors the parent repo's `productive_learning/.archive/` convention. The subfolder leaves room for future archived plans without flat-piling. The durable rules doc is `POST_SYSTEM.md` (created during execution); the plan itself is execution scaffolding and need not stay in the working tree once the system is in place.
