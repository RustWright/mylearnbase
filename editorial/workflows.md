# Authoring a workflows post

A workflows post describes a *prescriptive process* — how to do
something. The form sits between two readers and two locations: a
source doc in a project repo (read by an LLM at session start to keep
its behaviour consistent) and the rendered post on mylearnbase (read
by a human stranger or by future-you). Publishing a workflows post is
the one-way sync between those two locations.

The form has two categories, distinguished by who actually reads the
result in the future:

| Category | Future reader | Source location |
|---|---|---|
| **LLM-referenced** | An LLM at session start | Project repo (canonical) + synced post |
| **Personal-reference** | Future-you, occasionally | Post only |

Both categories may be authored collaboratively with an LLM. What
separates them is consumption: an LLM-referenced doc lives in a
project repo because that's where the LLM goes looking, and a
personal-reference doc lives only on mylearnbase because that's where
future-you goes looking.

## When to write a workflows post

Use this form when:

- You've just designed a process and the act of designing produced
  the artifact.
- You used an existing workflow, learned something, and want it
  updated. This is expected to be the most common case over time.

Don't use this form when:

- You just built a *feature*. (Use a *logbook* post.)
- You built an interactive demo to understand a concept. (Use a
  *concepts* post.)
- The take itself is the point. (Use an *opinions* post.)
- The value is mostly in pointing at external content. (Use a
  *resources* post.)

### LLM-referenced vs personal-reference

The clean signal: *does an LLM need to find this during work?*

- **Yes.** It's LLM-referenced. The source doc lives in the project
  repo so the LLM can read it at session start. The post on mylearnbase
  is a synced render — same content, second location.
- **No.** It's personal-reference. The source lives only as the post
  on mylearnbase. Future-you can read it when needed. There's no second
  reader and no second location.

LLM-referenced doesn't mean "about code" and personal-reference doesn't
mean "about non-code." A procedure for setting up a development
environment could be either: if the LLM uses it to bootstrap your
preferences, LLM-referenced; if it's a one-shot reference for
future-you when rebuilding a machine, personal-reference.

### Cadence

Workflows have no natural cadence. The publish trigger is "the doc
changed enough to warrant republishing," which depends on what kind of
work you're doing. Periods of exploration produce a lot of workflow
edits; periods of heads-down execution produce none. Treat the form
as elastic — there will be weeks with several republishes and months
with none.

### Boundary cases

The boundary case is a feature whose post wants to be a how-to. A
logbook entry describes what got built; the moment that description
starts narrating *how to reproduce it*, the post is drifting toward
workflows. The clean split: the *what-got-built* description belongs
in a logbook entry; the *how-to-build-something-similar* belongs in a
separate workflows post that cross-links.

## Install

The `workflows publish` tool ships in the same Python package as
`logbook` and `cite`. If you've already installed the tools to follow
the logbook authoring post on this site, `workflows` is already on
your PATH. If not, that post has the full install steps; the short
version is `uv tool install ./mylearnbase/tools` from a clone of this
repo.

`MYLEARNBASE_ROOT` discovery is identical to the other tools: the
env var wins, the default fallback is
`~/productive_learning/projects/mylearnbase`.

## The tool

The tool surface is one subcommand. Workflows has no `init`, no
capture-time commands, and no per-section append. The source doc is
the input, already authored in its natural location; the tool's only
job is to publish it.

### Mental model

Two locations, one publish boundary:

```
┌────────────────────────────────┐     ┌─────────────────────────────────┐
│ source doc                     │     │ mylearnbase repo                │
│ (project repo OR mylearnbase)  │     │                                 │
│                                │     │ content/posts/workflows/        │
│ <source-doc>.md ───────────────┼─────┼──►   <slug>.md                  │
│   (canonical for category 1;   │     │      (the rendered post)        │
│    same file for category 2)   │     │                                 │
│                                │     │  ↑ workflows publish writes here │
└────────────────────────────────┘     └─────────────────────────────────┘
            input                                publish-time tool
                                              (workflows publish — the boundary)
```

For LLM-referenced workflows, the source doc lives in the project repo
(it's what the LLM reads at session start). For personal-reference,
the source doc IS the post — drafted directly under
`mylearnbase/content/posts/workflows/<slug>.md`, no second location.

The flow is one-way: source → post. There's no edit-post-then-sync-back.
If you edit the published post directly, those edits are wiped on the
next republish, because the body is replaced wholesale every time.

### Publishing — `workflows publish`

```
workflows publish <source-doc-path> [--slug] [--title] [--draft]
                                    [--dry-run] [--supersede-from]
                                    [--full-check]
```

| Flag | Purpose |
|---|---|
| `--title` | Override the title extracted from the source doc's H1. Rarely needed. |
| `--slug` | Override the auto-slugified slug. Honored on first publish; treated as identity on republish (mismatched values trigger orphan-prevention error). |
| `--draft` | Publish as `draft = true`. Default is `false` — the source doc is the canonical artifact, so if it's ready for the source, it's ready to publish. |
| `--dry-run` | Print the unified diff against the current published post (or against empty for a first publish). No write. |
| `--supersede-from <old-slug>` | Treat this publish as superseding an existing post. Writes the new post + adds an `extra.superseded_by` banner to the old post. |
| `--full-check` | Run `zola check` with external link probing (slow). Default skips external links. |

### Three modes, detected automatically

The tool distinguishes three modes by comparing the source doc's title
to existing posts:

| Mode | Trigger | Behaviour |
|---|---|---|
| **First publish** | No post exists at the destination slug | Writes fresh frontmatter (`title`, `slug`, `date = today`, `draft = false`) |
| **Republish** | Post exists at the destination slug | Preserves `date`, `draft`, `taxonomies.tags`, `extra.outdate_alert_days`; sets `updated = today`; replaces body wholesale |
| **Supersession** | `--supersede-from <old-slug>` is passed; new slug differs from old | Writes new post (first-publish frontmatter); reads old post; adds `extra.superseded_by = "posts/workflows/<new-slug>.md"`; writes back |

The asymmetry between first-publish and republish is what makes
`taxonomies.tags` a legitimate post-side hand-edit: the source doc has
no tag concept; tags are added to the post after first publish, and
the tool preserves them across every subsequent republish. That's the
*only* post-side hand-edit that survives.

### Automatic transformations

Two transformations run over the source doc's body before write:

- **H1 stripping.** Zola renders `title` as the post's `<h1>`. If the
  source doc's `# Heading` stayed in the body, the rendered post would
  show two H1s. The tool strips the first `# Heading` line (and the
  blank line after).
- **Zola shortcode escape.** Zola interprets `{{ ... }}` and
  `{% ... %}` as shortcodes, even inside fenced code blocks. The tool
  escapes both patterns automatically using Zola's literal-output
  escape syntax, so example shortcodes in the source doc render as
  visible text rather than being interpreted. `{% raw %}` doesn't
  bypass detection — the escape has to be explicit. The transformation
  is idempotent: already-escaped pairs aren't escaped again.

### Image copy

Image references in the source doc body (markdown `![alt](path)`) are
copied to the destination directory alongside the post. Local paths
relative to the source doc are resolved; HTTP/HTTPS URLs and absolute
paths are skipped.

This matters more for personal-reference workflows (a *"how I set up
my dev environment"* post that wants screenshots) than for
LLM-referenced ones (which rarely include images).

### What the tool does NOT do

A handful of operations are deliberately absent:

- **No `init` command.** The source doc already exists, either as the
  LLM-referenced doc in a project repo or as the personal-reference
  post being drafted in mylearnbase. There's nothing to scaffold.
- **No per-section append.** The source doc is being authored in its
  natural location with whatever tools fit (LLM in conversation, an
  editor); the tool doesn't reach into the source.
- **No `showboat verify`.** Workflow source docs are prose, not
  runnable artifacts. There are no exec blocks to re-run for drift
  detection. (Logbook and cookbook have it; workflows doesn't.)
- **No atomic write.** If `zola check` fails after the dest is
  written, the orphan post stays. Cleanup is manual: delete
  `content/posts/workflows/<slug>.md` before retrying.

### Failure modes

- **Source doc missing** — exit 1. The tool can't infer what you
  meant; pass an existing path.
- **No H1 in source doc + no `--title`** — exit 1. The title has to
  come from somewhere; either add a `# Heading` to the source or pass
  `--title` explicitly.
- **`--slug` differs from auto and a post exists at the auto-slug**
  — exit 1 with an orphan-prevention message. The fix is in the
  message: pass `--supersede-from <auto-slug>` to supersede, or remove
  `--slug` to keep the auto-derived value.
- **`--supersede-from` post doesn't exist** — exit 1.
- **`--supersede-from` equals the new slug** — exit 1 ("superseding in
  place is incoherent").
- **`--supersede-from` and the new slot already has a post** — exit 1.
  Either the publish was already run, or the new slug is colliding
  with an unrelated post. Manual triage required.
- **`zola check` fails** — exit 1; orphan destination *not* rolled
  back. Delete by hand before retrying.

## What a workflows post looks like

Workflows posts don't have a prescribed section structure. The two
categories handle this differently.

### LLM-referenced — structure follows the source doc

The source doc's natural shape leads. A `PROJECT_PROCESS.md` is shaped
by what the process is; a `CLAUDE.md` agent rules doc is shaped by
what the rules are. The tool reformats nothing.

### Personal-reference — no template, yet

Personal-reference workflows have no prescribed structure. The
section shape emerges from first real authoring; until at least one
personal-reference post exists, the template is whatever the procedure
wants.

This is deliberate. Speculative editorial structure becomes debt the
first time real authoring contradicts it. The pattern across forms on
this site has been to defer prescriptive section content until lived
data exists.

## Writing well at the doc level

Workflows resists tight per-section editorial rules — different
workflows serve wildly different purposes, and the form's structure is
deliberately loose. What carries weight instead is a handful of
doc-level disciplines. They apply across whatever shape the source doc
takes.

### Dual-reader pressure (LLM-referenced only)

The LLM-referenced source doc serves two readers: the LLM that reads
it at session start, and a human stranger who lands on the rendered
post. Both have to be able to use it.

The disciplines that fall out:

- **LLM tolerates prose; humans don't tolerate cryptic.** A doc that
  reads as a bare rulebook (*"do X when Y; otherwise Z"*) works for
  the LLM but loses the stranger. Add the narrative connective tissue
  that makes the rules readable.
- **Humans tolerate narrative; LLMs lose load-bearing rules in it.**
  A doc that's all conversational story loses the LLM's ability to
  pick out what's structural. The load-bearing rules need to be
  flagged — lists, tables, explicit headings.
- **When the readers' needs conflict, optimize for the human.** LLMs
  are more forgiving of stylistic choices than a stranger landing cold
  from the front page.

**✗ Bad (LLM-only voice):**

```
Rule: never commit without running tests.
Rule: never push --force.
Rule: PR titles must use [scope] prefix.
```

A rulebook with no shape. The LLM follows it. A stranger has no idea
why these are the rules, when each one applies, or what the costs are
of violating them.

**✗ Bad (human-only voice):**

```
Generally we try to keep our process healthy by running the tests
before committing, and we try not to push --force unless it's really
necessary, and PR titles should usually have some kind of prefix...
```

A stranger can read it. The LLM has to guess which sentences are rules
versus suggestions versus stories. Hedge words (*"generally,"
"usually," "try not to"*) dissolve the load-bearing edges.

**✓ Good:**

```
### Commit discipline

- Run tests before every commit. Pre-commit hook will refuse a commit
  that doesn't.
- Never push `--force` to main; force-pushes are allowed on feature
  branches only.
- PR titles use a `[scope]` prefix (e.g., `[auth]`, `[infra]`).

The pre-commit hook is the enforcement layer for the first rule;
the other two are author discipline.
```

Rules are explicit and scannable. The closing line names which rule
is tool-enforced and which is convention — useful for both readers.

### Edit the source, not the post

For LLM-referenced workflows, every republish replaces the body
wholesale. Edits made to the published post are wiped on the next
publish. The only legitimate post-side hand-edit is `taxonomies.tags`
(preserved by the tool); everything else has to flow source → post.

The lived shape: the LLM often drafts and maintains the source doc
based on your feedback in conversation. You evaluate; the LLM
modifies; the next republish brings the change to the post.

For personal-reference workflows, the source doc IS the post, so this
discipline doesn't apply — there's no second location to drift from.

### Project-jargon discipline

The shared anti-jargon rule says: no project-internal terms in
published prose. For workflows, this rule has a finer edge.

When a workflows post *defines* its process vocabulary, those terms
are content, not jargon. `PROJECT_PROCESS.md` says *"each Cycle has
Sessions 1-5"* — Cycle and Session are the process being defined; the
doc gives them meaning. A stranger reading the post learns the
vocabulary from the doc.

What's still jargon:

- **Instance references** — *"we decided this in Cycle 2 Session 3."*
  The vocabulary is defined but the *specific instance* is opaque.
  Strip the instance and the sentence either still works or reveals
  there was no underlying point.
- **Inherited vocabulary without redefinition** — *"the M2 milestone"*
  in a post that never defines M2. The reader has no anchor.

| Use | Verdict |
|---|---|
| Defining the vocabulary the doc is about, with explanation | ✓ Content |
| Referring to specific instances of that vocabulary | ✗ Jargon |
| Inheriting another doc's vocabulary without redefining | ✗ Jargon |

**✗ Bad (instance reference, no defining context):**

```
This pattern emerged from feedback in Cycle 2 Session 3, and after
the M2 review we knew it had to ship before Phase 4.
```

Strip the jargon and the sentence collapses into *"this pattern
emerged from feedback we knew it had to ship eventually."* The
load-bearing nouns were all internal.

**✓ Good (vocabulary defined, no instance leak):**

```
This pattern emerged during a planning session when we realised the
procedure had a missing step. The fix landed in the next
implementation pass.
```

The vocabulary the workflow defines (planning session, implementation
pass — if these are defined elsewhere in the doc) survives. The
specific *which* session has been replaced with the *kind* of session,
which is what the reader actually needs.

### Supersession-vs-republish judgment

Republish replaces the post in place. Supersession creates a new post,
keeps the old one alive with a *"superseded by..."* banner. The
choice between them depends on whether the old version is worth
keeping findable.

Use **republish** when:

- The change is incremental — typos, clarifications, new section
  additions, paragraph reshuffling.
- The old version's URL holds no independent value; a reader landing
  on the post should see the current state.
- You're maintaining a living doc that's expected to evolve.

Use **supersession** when:

- The change is large enough that the old version is genuinely a
  different doc.
- Inbound links to the old URL should keep working but should also
  tell readers a newer version exists.
- You want the rendered site to preserve the history of the form's
  evolution.

A useful test: would future-you, reading the old version, want to
know a newer version exists? If yes, supersede. If the old version
would just confuse, republish.

### `--dry-run` before each republish

Source docs grow; republishes replace the body wholesale. Without a
diff, you can't tell what's new in this republish vs. what was already
published. `--dry-run` prints a unified diff against the current post.

The habit is small (one extra command) and the value scales with the
size of the source doc. For a multi-hundred-line doc with a few
paragraphs changed, the diff is the only way to verify the change
landed cleanly and didn't accidentally pick up unintended edits.

### Sync after editing the source

This is a discipline open question, not a settled rule. After editing
the source doc, the post on mylearnbase is stale until the next
`workflows publish`. There's no automatic sync.

The risk: the LLM (or you) edits the source doc during a session,
moves on to other work, and never publishes. The post on mylearnbase
drifts from the source. Where the reminder mechanism lives — in the
source doc, in the `/create-post` skill, or in `CLAUDE.md` — is
unsettled. For now, the practical version is: any session that edits
an LLM-referenced source doc should end with a `workflows publish`.

### Duplicate-source hygiene

When the source doc has copies across multiple project repos (a real
situation today with `PROJECT_PROCESS.md` mirrored in several
projects), publishing from the wrong copy regresses the canonical
version. Before each republish of a multi-copy doc, identify the
canonical one — usually the most recently edited — and publish from
that. The longer-term fix (single canonical location, automated
mirror) lives outside the editorial doc.

## Form-level anti-patterns

The doc-level disciplines above cover most of what can go wrong. Two
form-level failure modes don't fit cleanly into any single discipline
and are worth naming separately.

### Speculative workflow

A workflow published before it's actually been run is a proposal, not
a workflow. The design-from-scratch path is only valid when the design
was followed at least once — the first run is what catches the gaps
the design didn't anticipate.

Signal: the doc reads as how-it-should-work, with no anchor in
how-it-actually-worked-when-tried.

Corrective: run the workflow at least once before publishing the post.
If the first run surfaces gaps, fix them in the source doc before
publishing — the gap-finding is part of the design.

### Trying to rename when the intent is supersede

The tool catches the common version of this with an orphan-prevention
error: passing `--slug` to a doc whose existing post is at a different
slug raises *"this would orphan the post at &lt;old-slug&gt;."* The
error message names the fix.

The deeper question is *which fix* is right. Almost always, "rename"
isn't what you meant. The reasons to genuinely rename are narrow: a
slug typo nobody linked to externally, a structural directory move.
Otherwise, large-enough content drift wants `--supersede-from`; small
drift wants the slug to stay.

Signal: the orphan error fires and your first instinct is to *force*
the rename. Step back and ask: do you want both posts findable
(supersede), or do you want the old URL gone (rename — rare)?

## A worked example end-to-end

This very doc is an LLM-referenced workflow post. The example below
walks through three publish moments against it. Some commands are
real (first publish and the supersession step are illustrative; the
republish step has been run multiple times during this doc's
authoring).

The source doc lives at `editorial/workflows.md` in the mylearnbase
repo. (For LLM-referenced workflows that originate in another project
repo, replace the path; the tool runs the same way.)

### Step 1 — First publish

```bash
workflows publish editorial/workflows.md --dry-run    # preview
workflows publish editorial/workflows.md              # land it
```

The dry-run shows a diff against an empty current post (since none
exists yet) — effectively the full text of what's about to land.
The publish writes the post and runs `zola check`:

```
content/posts/workflows/authoring-a-workflows-post.md
  published: title = 'Authoring a workflows post', slug = 'authoring-a-workflows-post'
  date = 2026-05-13
  draft = false
  zola check: clean (internal links only)
```

What landed:

- `content/posts/workflows/authoring-a-workflows-post.md` — the new
  post, with frontmatter `title`, `slug`, `date = today`,
  `draft = false`, and the body as the source doc with H1 stripped
  and any Zola shortcodes escaped.
- Any local images referenced in the body would be copied alongside;
  this doc has none.

### Step 2 — Refinement republish

A week later, the doc has accumulated edits: a paragraph clarifying
the dual-reader discipline, a new anti-pattern, a tweak to the
worked example. Republish:

```bash
workflows publish editorial/workflows.md --dry-run    # diff preview
workflows publish editorial/workflows.md              # republish
```

The dry-run prints the unified diff between the current post and the
new content — what's actually changing. The publish:

```
content/posts/workflows/authoring-a-workflows-post.md
  republished: title = 'Authoring a workflows post', slug = 'authoring-a-workflows-post'
  date = 2026-05-13  updated = 2026-05-20
  draft = false
  zola check: clean (internal links only)
```

What changed:

- `date` is unchanged from the first publish — preserved automatically.
- `updated` is set to today.
- `taxonomies.tags`, if any had been hand-added after the first
  publish, would survive untouched.
- The body is replaced wholesale with the new source.

### Step 3 — Supersession

Months later, the doc has drifted enough that calling it the same
post would be misleading: the form's section structure changed, the
tool surface has new commands, a whole framing was rewritten. The
old post is still useful as a historical record but shouldn't be
the front-line reference.

The author renames the source doc's H1 to *"Authoring a workflows
post (revised)"* and runs:

```bash
workflows publish editorial/workflows.md \
  --supersede-from authoring-a-workflows-post
```

Output (illustrative):

```
content/posts/workflows/authoring-a-workflows-post-revised.md
  published (superseding): title = 'Authoring a workflows post (revised)', slug = 'authoring-a-workflows-post-revised'
  date = 2026-05-13
  draft = false
  superseded: content/posts/workflows/authoring-a-workflows-post.md now banners → authoring-a-workflows-post-revised
  zola check: clean (internal links only)
```

What changed:

- A new post landed at `authoring-a-workflows-post-revised.md` with
  fresh frontmatter (`date = today`, no `updated`).
- The old post at `authoring-a-workflows-post.md` had `extra.superseded_by`
  added to its frontmatter, pointing at the new post. Its body is
  unchanged.
- Readers landing on the old URL see a banner above the post body
  pointing at the revised version. Inbound links keep working.
- Both posts pass `zola check` together.

### The frontmatter at each step

After step 1:

```toml
+++
title = "Authoring a workflows post"
slug = "authoring-a-workflows-post"
date = 2026-05-13
draft = false
+++
```

After step 2 (republish):

```toml
+++
title = "Authoring a workflows post"
slug = "authoring-a-workflows-post"
date = 2026-05-13
updated = 2026-05-20
draft = false
+++
```

After step 3 (the old post, with the banner added):

```toml
+++
title = "Authoring a workflows post"
slug = "authoring-a-workflows-post"
date = 2026-05-13
updated = 2026-05-20
draft = false

[extra]
superseded_by = "posts/workflows/authoring-a-workflows-post-revised.md"
+++
```

The new post (created by step 3) has fresh first-publish frontmatter
at a new slug; the chain is built one link at a time. If a future
revision supersedes the revised post, that revision's publish will
update the revised post's frontmatter — never the original's. Readers
walking from `authoring-a-workflows-post` to its successor and onward
follow the chain through banners.
