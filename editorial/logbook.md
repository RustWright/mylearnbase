# Authoring a logbook entry

A logbook entry records a single feature you built — what it does, why
it was added, and how you know it works. The form exists to make that
capture lightweight, structurally consistent, and reliably
evidence-bearing: build cadence drives publication cadence. A feature
ships; you capture; you publish.

The form has two readers. Future-you is the primary audience —
scanning the post in eighteen months to remember what got built. A
stranger is the secondary audience — landing on the post from the
front page or a tag. The editorial criterion across both:
*useful + satisfying*. Future-you finds it useful; present-you felt
good writing it.

## When to write a logbook entry

Use this form when:

- You just built a feature you want to record.
- The work has a clear functional unit — one externally-observable
  thing the user can do, or one capability one part of the system can
  rely on from another.
- You can answer *"what does this feature do?"* in a paragraph without
  listing several unrelated changes.

Don't use this form when:

- You're writing a how-to or tutorial. (Use a *workflows* post.)
- You're explaining a code or design pattern as the post's primary
  content. (Use a *cookbook* entry.)
- The work covers several unrelated features. (Split into multiple
  logbook entries, one per feature.)
- The take itself is the point. (Use an *opinions* post.)
- You're curating external resources. (Use a *resources* post.)

The boundary case is a feature that's actually a *cluster* of small
features — half a dozen things that only make sense together. Treat
"one feature" as a judgment call. The clean signal: if §3 *("What does
this feature do?")* answers cleanly in one sentence, the cluster is
one feature; if §3 wants to be a list of unrelated items, it's
several, and the post should split.

**Cadence.** Continuous capture, frequent publish. Capture during or
right after the *final* commit for the feature. Multi-session features
defer the capture until the feature is functionally complete —
capturing while a feature is still in flight produces a story the
feature hasn't finished telling.

## Quick start

If you already have the tools installed and just want the flow, skip to
"The typical flow" below.

### Install

The tools are a Python package installed via [uv](https://docs.astral.sh/uv/).
If `uv` isn't already on your system:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the mylearnbase repo (the tools live alongside the site source):

```bash
git clone https://github.com/RustWright/mylearnbase.git
```

Install the tools onto your PATH:

```bash
uv tool install ./mylearnbase/tools
```

That installs four executables: `logbook`, `cite`, `cookbook`, `workflows`.
The logbook flow uses the first two; the others apply to sibling forms
covered by their own editorial docs.

One separate prerequisite: `showboat` ships as its own package.

```bash
uv tool install showboat
```

If that doesn't resolve, the project lives at
https://github.com/simonw/showboat — install per its own instructions.

`logbook publish` writes the published post into a sibling mylearnbase
clone. By default it looks in a fixed location; if your clone is
elsewhere, set the `MYLEARNBASE_ROOT` env to point at it:

```bash
export MYLEARNBASE_ROOT=/path/to/your/mylearnbase
```

For dev work where source edits should be picked up automatically
without reinstalling, add `--editable` to the tools install:

```bash
uv tool install --editable ./mylearnbase/tools
```

### The typical flow

Five stages, run from inside the project repo whose feature you're
documenting:

1. **Scaffold the capture** with `logbook init <project> <slug> --title "..."`.
   Writes a structured markdown file at `<repo>/logbook/_drafts/<slug>.md`.
2. **Fill the prose sections** with `logbook what`, `logbook why`, and
   optionally `logbook scope`. Each command appends text to the named
   section.
3. **Add evidence** to *"How do we know it works?"* with `logbook exec`
   (runnable code), `logbook screenshot` (existing images), and `cite`
   (commit-pinned code citations).
4. **Tag and add tail notes** with `logbook tags "..."` and optional
   `logbook note "- ..."` calls.
5. **Publish** with `logbook publish <slug>`. Converts the capture to a
   Zola post under `<mylearnbase>/content/posts/logbook/<project>/<slug>.md`,
   runs `showboat verify` and `zola check`, and copies any referenced
   images.

The published post is written with `draft = true` — review it, then
flip to `false` when ready to ship.

For the full command sequence with realistic content, see the worked
example at the end of this doc.

## The tools

### Mental model

Two locations, one publish boundary:

```
┌────────────────────────────────┐     ┌─────────────────────────────────┐
│ project repo (e.g., omni-me/)  │     │ mylearnbase repo                │
│                                │     │                                 │
│ logbook/_drafts/<slug>.md  ────┼─────┼──►  content/posts/logbook/      │
│   (the capture; gitignored)    │     │       <project>/<slug>.md       │
│                                │     │       (the published post)      │
│ ↑ capture tools write here     │     │  ↑ logbook publish writes here  │
└────────────────────────────────┘     └─────────────────────────────────┘
        capture-time tools                       publish-time tool
        (init, what, why, scope, note,           (publish — the boundary)
         exec, screenshot, tags, cite)
```

Capture-time tools run from the project repo's working directory and
discover the repo via `git rev-parse --show-toplevel`. They work from
any project repo, not just mylearnbase.

`logbook publish` is the only tool that touches mylearnbase. It resolves
the destination via `MYLEARNBASE_ROOT` (or the default fallback). The
flow is one-way: capture → publish. There's no edit-post-then-sync-back.
If you edit the published post directly, those edits live only in
mylearnbase.

### Scaffolding — `logbook init`

```
logbook init <project> <feature-name> --title "<post title>" [--force]
```

Writes the capture file at `<repo-root>/logbook/_drafts/<feature-name>.md`
with:

- A title block (`# <title>` + timestamp) written by `showboat init`.
- A metadata blockquote (`> Project:`, `> Slug:`, `> Tags: TBD`).
- Five empty `##` section headers in order: *What does this feature do?*,
  *Why was it added now?*, *What's in scope (and what's not)?*, *How do
  we know it works?*, *What's worth remembering or doing next?*.

`--title` is required. The slug is meant for the URL; the title is
meant for the post's H1, which is rarely the same shape.
*"OAuth login via Google"* is a title; *"oauth-login-google"* is a slug.

**Failure modes.** Capture already exists (exit 1 unless `--force`); not
in a git repo (exit 2); `showboat` not on PATH (exit 2).

### Filling prose — `logbook what`, `why`, `scope`, `note`

```
logbook what  <slug-or-path> "<text>"
logbook why   <slug-or-path> "<text>"
logbook scope <slug-or-path> "<text>"
logbook note  <slug-or-path> "<text>"
```

All four follow one pattern: read text (from arg or stdin), append it
to the named section's existing body.

| Command | Targets section |
|---|---|
| `what` | What does this feature do? |
| `why` | Why was it added now? |
| `scope` | What's in scope (and what's not)? |
| `note` | What's worth remembering or doing next? |

The first argument accepts a *path* (`./logbook/_drafts/foo.md`) or a
*bare slug* (`foo` — resolves to the standard location). Bare slug is
the typical usage from a project repo.

Empty text is refused. Calling against a slug whose capture doesn't
exist errors clearly.

Bullet syntax in §5 (scope) and §7 (note) is the author's responsibility
— pass `- ` as part of the text if the section should render as bullets.
The tool appends verbatim.

### Adding evidence — `cite`, `logbook exec`, `logbook screenshot`

Three tools, three evidence kinds. All three default to writing into §6
*(How do we know it works?)*.

**`cite`** — form-agnostic, cross-project.

```
cite <capture-file> <path:line> [--note "..."] [--section "..."] [--allow-dirty]
```

Records a code citation: parses `<path:line>`, captures the line
content, resolves the current `git rev-parse HEAD` for a commit SHA,
and synthesizes a GitHub permalink. Appends a markdown block — a linked
header, the cited line in a blockquote, and an optional `--note`
underneath.

Cite refuses to cite *dirty files* — the permalink would point at HEAD's
content, not what's locally staged, which would mislead a reader who
clicks through. `--allow-dirty` overrides; use sparingly and only with
a comment explaining why.

Unlike the logbook subcommands, `cite` takes an explicit path to the
capture file rather than a bare slug. The form-agnostic scope is what
drives this — cite can target any form's capture, so the path is what
disambiguates.

**`logbook exec`** — runs code, captures the result as evidence.

```
logbook exec <slug-or-path> <lang> [code] [--section "..."]
```

Wraps `showboat exec`. The exec is re-run at every publish via
`showboat verify`; non-deterministic content (timestamps, network calls,
single-use tokens) needs to be pinned or accompanied by `--skip-verify`
at publish time with a comment explaining why.

**`logbook screenshot`** — embeds an existing image.

```
logbook screenshot <slug-or-path> <image-path> [--section "..."]
```

Wraps `showboat image`. The image must already exist on disk; this tool
is embed-only. Capturing the screenshot is a human-in-the-loop step —
choosing *which* shot reflects what the feature does.

### Metadata — `logbook tags`

```
logbook tags <slug-or-path> "tag1, tag2, tag3"
```

Rewrites the `> Tags:` line in the capture's metadata blockquote. Fails
if the capture wasn't initialized through `logbook init` (and so has no
Tags line). Tiny tool, one job.

### Publishing — `logbook publish`

```
logbook publish <slug-or-path> [--slug "..."] [--tags "..."] [--force]
                                [--full-check] [--skip-verify]
```

The publish-time boundary. Five steps in order:

1. **Verify.** Runs `showboat verify` against the capture, re-running
   every embedded exec block and diffing the output. If output drifted
   (the feature broke; the code is non-deterministic), publish refuses.
   `--skip-verify` opts out for documented exceptional cases.
2. **Parse.** Extracts the metadata blockquote (Project, Slug, Tags),
   the title block, and the section bodies.
3. **Compute destination.** `<mylearnbase>/content/posts/logbook/<project>/<slug>.md`.
   If the project's `_index.md` doesn't exist yet, scaffold it with the
   standard section frontmatter — this is how new project sub-sections
   come into existence.
4. **Prune empty optional sections** (§5 scope, §7 notes) so they don't
   render as empty headers. The three required sections (§3 *what*,
   §4 *why*, §6 *evidence*) refuse publish if empty — a structural
   integrity check.
5. **Write the post.** Frontmatter (`title`, `slug`, `date = today`,
   `draft = true`, optional `taxonomies.tags`) followed by the body.
   Any locally-referenced images in the body are copied to the
   destination directory alongside the post.

Then `zola check` (skipping external links by default for speed;
`--full-check` includes them).

**Reviewing the draft.** Preview with `zola serve --drafts` from inside
the mylearnbase repo, then flip the frontmatter to `draft = false` when
ready to ship.

**One rough edge worth knowing:** `zola check` runs *after* the
destination file is written. If `zola check` fails (broken internal
link, malformed shortcode), the orphan destination is not rolled back.
Delete the file by hand before retrying.

## The capture's seven sections

The capture file has seven sections, in order. Sections 1 and 2 (title
+ metadata) are auto-filled by `logbook init`. Sections 3–7 are the
`##` headers you fill.

### What each section is doing for the post

| # | Section | Required? | What question it answers |
|---|---|---|---|
| 1 | Title block *(auto)* | yes | "Which feature is this post about?" |
| 2 | Metadata blockquote *(auto; stripped at publish)* | yes | (machine-readable; never rendered) |
| 3 | What does this feature do? | yes | "If I landed here cold, what is this thing?" |
| 4 | Why was it added now? | yes | "What chain of causes made this worth building at this point?" |
| 5 | What's in scope (and what's not)? | optional | "What did you deliberately *not* do, so I'm not confused when X is missing?" |
| 6 | How do we know it works? | yes | "Why should I believe this actually works?" |
| 7 | What's worth remembering or doing next? | optional | "What did you almost forget? What's leftover?" |

### Why the ordering

Four non-obvious choices about how the sections sit relative to each
other:

**What-then-why, not why-then-what.** A journalistic ordering would
lead with motivation (*"we needed identity, so OAuth"*). The logbook
leads with identity (*"users can log in with Google"*) and then
explains motivation. The reason: future-you scans by section header.
*"What does this feature do?"* is the recognition cue. *"Why was it
added now?"* is the context cue. Recognition before context.

**Scope is optional, not required.** Many features have obvious
boundaries — a button does what the button does. Forcing a scope
section creates filler. Scope earns its place when the feature's edges
are non-obvious (multi-provider feature with one provider in;
multi-platform feature with one platform in).

**Evidence has structural rules; the other required sections don't.**
§6 has editorial rules about *what counts* as evidence — covered in
*Writing each section well*. The other required sections (§3, §4) must
be non-empty but don't constrain what kind of content fills them.

**Tail notes (§7) carry what would otherwise be a separate file.**
Cookbook candidates noted in §7 sit in context with the feature that
surfaced them, rather than collecting in a separate registry. Same for
considered-and-rejected alternatives, deferrals, and known gaps — they
stay where they came up.

## Writing each section well

The quality bar for each section, with worked examples. The required
sections (§3, §4, §6) carry the most editorial weight; the optional
sections (§5, §7) get most of their value from the discipline to
*skip* them when they aren't doing work. The title (§1) is short but
easy to get wrong.

Worked examples use OAuth login via Google as the running feature for
continuity. The shapes generalize to any feature.

### §1 — Title

Auto-derivation from the slug produces results like *"Oauth login
google"* roughly four times out of five. `--title` is required at init
for that reason.

**✓ Good titles** read as real phrases someone might say:

- *"OAuth login via Google"*
- *"Calendar adaptive row rendering"*
- *"Five-form post system reset"*

**✗ Bad titles:**

- *"Oauth login google"* — slug-fragment-shaped. Add the linking word
  (*"via"*), fix the capitalization (*"OAuth"*).
- *"Adding Google OAuth to omni-me"* — names the *act of working on
  it*, not the feature.
- *"Auth"* — too terse, could be anything.
- *"Implementation log: OAuth via Google for omni-me cycle 3"* —
  project-jargon stuffing.

**Quality bar.** Reads as a real phrase; names the feature, not the
act of working on it; concrete enough to disambiguate from similar
features without repeating §3; jargon-free.

**Practical test.** Picture the title in a list of front-page posts.
Does it tell a reader what the post is about, or does it look like a
placeholder someone forgot to update?

### §3 — What does this feature do?

**✓ Good:**

> Users can log in to omni-me using their Google account. The first
> time someone authenticates, a user record is created and a JWT is
> issued; subsequent logins return a JWT for the existing record. The
> JWT identifies the user on every request to `/me`.

What works: externally observable (what a *user* experiences, plus
what other parts of the system can rely on). Self-contained — a
reader who skips the rest of the post still knows what shipped.
Specific enough to disambiguate (*"auto-creates the user record on
first login"* rules out the alternative where pre-provisioned accounts
are required).

**✗ Bad (project-internal scaffolding):**

> Implemented the OAuth integration we discussed last week. Added the
> `GoogleAuthProvider` trait, wired up `/auth/google` via the OAuth2
> crate, and made sure `JwtClaims` holds the user ID. Should be ready
> for downstream consumers.

Why it fails: opens with vocabulary that only exists inside an internal
conversation (*"we discussed last week"*), drowns the description in
implementation details that belong in cite blocks under §6, ends in
deadline-shaped language. Future-you in eighteen months reads this and
still doesn't know what the feature *does* — only what was *touched*.

**✗ Bad (terse to the point of useless):**

> Added Google login.

Why it fails: technically accurate; tells the reader nothing. Are
accounts auto-created? Is this the only auth method? Does the session
persist? You'd have to read the rest of the post to recover the shape
§3 was supposed to provide.

**Quality bar.** Externally observable; self-contained; specific
enough to disambiguate plausible alternatives; jargon-free.

**Practical test.** Hand §3 to someone with no project context. If
they can describe the feature in their own words after reading just
that paragraph, §3 is doing its job. If they have to ask what
`JwtClaims` is, it isn't.

### §4 — Why was it added now?

**✓ Good:**

> Multi-device sync was the goal for this stretch of work — laptops
> and phones needed to converge on the same data. That required a
> stable per-user identity, which the standalone-mode app didn't have
> (everything was local-only). OAuth was the smallest step that gave
> us per-user identity without taking on password storage ourselves.

What works: a chain of causes — goal → constraint → choice. Each step
is grounded in *this project's actual state at that moment*. The "now"
is answered specifically.

**✗ Bad (internal-vocabulary scaffolding):**

> Cycle 3 priority. Identified during the architecture review in
> Phase 2 as a prerequisite for the M2 milestone.

Why it fails: every load-bearing noun is meaningless outside the
project's process vocabulary. Strip out *"Cycle 3,"* *"Phase 2,"* and
*"M2 milestone"* — the sentence collapses into *"we agreed it was a
priority."* The actual reason was never written down.

**✗ Bad (universal-truth reasoning):**

> Authentication is a fundamental concern for any modern web
> application. Adding OAuth ensures we meet user expectations and
> provides a foundation for future features.

Why it fails: doesn't anchor in *this project at this time*. Paste it
into any project's blog and it still works — a sign the reasoning
isn't real. The "why now" is unanswered; it's been replaced with
"why ever."

**Quality bar.** A causal chain; anchored in this project's concrete
state at the time; explains the *trigger* (what made this the next
thing), not the abstract value; no internal-vocabulary scaffolding.

**Practical test.** Replace the feature name in §4 with a different
feature name. If the paragraph still reads as a valid justification,
§4 is too generic. If it stops making sense (e.g., *"ORM was the
smallest step that gave us per-user identity"* — nonsense), §4 is
doing its job.

### §5 — What's in scope (and what's not)?

Three expression shapes, each picked by how much each item needs to
carry:

| Shape | When to use |
|---|---|
| **Inline labels** | 3–6 items per side, all simple |
| **Bulleted with clauses** | Items benefit from a clarifying parenthetical or rationale |
| **Prose paragraph** | Boundary reasoning is itself worth stating |

**✓ Good — inline (the default for simple lists):**

> In: Google OAuth flow, JWT issuance, /me endpoint.
> Not in: refresh tokens, account deletion, other providers, session revocation.

**✓ Good — bulleted (when items need clauses):**

> **In:**
> - Google OAuth flow (full code-grant; not implicit)
> - JWT issuance with 24h expiry
> - /me endpoint for current-user identity
>
> **Not in:**
> - Refresh tokens — deferred; 24h is acceptable for the multi-device use case
> - Account deletion — no flow yet
> - Other providers (Apple, Microsoft) — postponed; the pattern validates with one

**✓ Good — prose (when reasoning is the substance):**

> This covers the Google OAuth code-grant flow, JWT issuance, and the
> /me endpoint that uses the JWT to identify the requester. It
> deliberately skips refresh tokens (the 24h JWT life is acceptable
> here), other providers (one is enough to validate the pattern), and
> session revocation (JWT expiry serves the same role for now).

**✗ Bad (too vague to head off questions):**

> In: OAuth login. Not in: everything else.

Doesn't preempt any specific question. A reader still has to ask
*"does this support Apple?"* — which is what scope was supposed to
answer.

**✗ Bad (defensive padding):**

> Not in: this isn't a full identity solution, doesn't replace your
> existing user system, isn't designed to scale to enterprise,
> doesn't handle compliance, doesn't include MFA, isn't SSO, doesn't
> ship telemetry, doesn't support SAML.

Lists every conceivable thing the feature *isn't*. Scope is for near
neighbors, not for the universe. An exhaustive "not in" list
communicates anxiety, not boundaries.

**✗ Bad (forced when obvious):**

> In: a button that says "Log out". Not in: a button that says
> anything else.

§5 is optional. If the feature's edges are already clear from §3,
leave scope empty — `logbook publish` strips empty optional sections.

**Quality bar.** Near neighbors only; parallel structure; honest
brevity (typically 1–4 items per side); skipping is valid.

**Practical test.** Imagine a reader who just finished §3. What's the
first *"but what about..."* they'd ask? If scope answers that, it's
earning its place. If it answers questions no one would ask, it's
padding.

### §6 — How do we know it works?

The publish step refuses to ship if §6 is empty. The rules below
cover what counts as *evidence* once it's non-empty.

The evidence types and what each one is for:

| Tool | What it proves | When to reach for it |
|---|---|---|
| `logbook exec` | The code runs and produces the output it claimed | Tests, scripts, anything with deterministic terminal output |
| `logbook screenshot` | The feature presents the way it claims | UI features, rendered output, error states |
| External observable | The feature is live and reachable | Deployed endpoints, public artifacts |
| `cite` | *Where* the code lives, with commit pinning | Always usable; never sufficient alone |

**✓ Good (multi-evidence):**

> The auth-handler tests pass — happy path, invalid token, missing
> claims, and first-time-user JWT issuance:
>
> [showboat exec: `cargo test auth::` → 4 passed; 0 failed]
>
> [cite: tests/auth.rs:1 — auth-handler tests at SHA abc1234]
> > `mod auth_tests { ... }`
>
> The login round-trip works end to end:
>
> [screenshot: login-screen.png]
> [screenshot: signed-in.png]
>
> [cite: src/auth.rs:42 — google_login handler at SHA abc1234]
> > `pub async fn google_login(req: Request) -> Result<Json<TokenResponse>>`
>
> The JWT is issued at the tail of this function — the line that
> turns "Google said yes" into "omni-me knows who you are."

Three evidence types, each doing something different. The exec proves
the tests pass (objective). The screenshots prove the user-facing
flow works (observable). The citations point at load-bearing lines
with *prose explaining why those lines matter* — without the prose,
*"src/auth.rs:42"* is a coordinate, not a citation.

**The pairing rule (mandatory).** When the exec is a test invocation,
pair it with prose naming what the tests cover *or* a citation to
the test code. The exec proves the tests pass; the prose or cite
makes the test surface visible. Without either, *"4 passed"* is a
number with no way to interpret it.

The granularity of the prose ladders with the test surface's size:

| Test surface | What "pair with prose" looks like |
|---|---|
| Small (a handful of tests) | Name the specific scenarios |
| Medium (a dozen-ish tests) | Name the categories |
| Large (extensive coverage) | Name the surface and point at the load-bearing subset |

When the suite is genuinely too big to summarize at any finer
granularity than "the whole suite," the cite alone is enough — link
to the test module's top-of-file and let the reader navigate from
there.

**✗ Bad (citation-only tour):**

> [cite: src/auth.rs:42]
> [cite: src/auth.rs:67]
> [cite: src/jwt.rs:12]

A reader walks away knowing where the code lives but not whether it
works. The post passes the publish check, but it's a tour of the
source, not evidence.

**✗ Bad (decoration, not evidence):**

> [screenshot: vscode-window.png — VS Code with auth.rs open]
> [screenshot: terminal-screenshot.png — tests passing in my terminal]
> The build is green on CI.

The screenshots show *tooling*, not the feature. A VS Code window
proves nothing about authentication. A static screenshot of a passing
test run is strictly weaker than the runnable exec block. *"Build
is green on CI"* is an external observable but unverifiable from the
post — no link, no commit reference.

**✗ Bad (non-reproducible exec):**

> [showboat exec: `curl http://localhost:8080/auth/google?code=abc123`]
> Returns a JWT.

Requires localhost, depends on a single-use OAuth code that expires,
and the prose (*"returns a JWT"*) describes what *should* happen
instead of what showboat captured. `showboat verify` will refuse
this on the next publish.

**Quality bar.**

1. At least one of runnable exec, observable screenshot, or external
   observable — never citations alone.
2. Each evidence element earns its place. A screenshot of *tooling*
   doesn't prove the feature works; a screenshot of *the feature*
   does.
3. Exec blocks must be deterministic. They re-run on every publish
   via `showboat verify`.
4. When exec is a test invocation, pair it with prose or cite (the
   pairing rule).
5. Citations carry prose. *"src/auth.rs:42"* is a coordinate;
   *"src/auth.rs:42 — the JWT is issued here"* is a citation.

**Soft ordering within §6.** Not a rule, but the natural progression
is exec (and its paired cite) → screenshot → cite. From most-objective
(*"the code runs and outputs X"*) to most-static (*"the code lives at
this address"*). The ordering tells a reader: *here's the test result;
here's how it looks; here's where it lives.*

**Practical test.** Cover the section header and read just the
evidence. Does it answer *"does this feature work?"* If a reader
only learns where the code lives, the section is a tour of source
code, not evidence — and the section isn't doing its job, even if
`logbook publish` accepts it.

### §7 — What's worth remembering or doing next?

**✓ Good:**

> - Considered passwordless email magic-links instead. Rejected — more
>   infra (email sender, link expiry, abuse prevention) for marginally
>   better UX. Revisit if Google's terms become a problem.
> - The trait-bound JWT generation pattern might be a cookbook entry.
> - Refresh tokens deferred — 24h JWT lifetime is acceptable for the
>   multi-device use case. Revisit if re-auth friction surfaces.
> - Missing test: "user changes their Google email mid-session." Low
>   priority; on the next sweep.

Each bullet does one thing — a rejected alternative with the reason,
a cookbook candidate, a deferral with its revisit trigger, a known
gap with its priority. Future-you walks in knowing where the unsaid
bits are.

**✗ Bad (stale TODOs):**

> - TODO: improve security
> - TODO: more tests
> - TODO: maybe refactor later

Each bullet is a token gesture with no decision content. *"Maybe
later"* tells future-you nothing it didn't already assume.

**✗ Bad (project-internal-only):**

> - See Linear ticket #1234 for next steps.
> - Discussed in the 2026-04-30 standup.

Pointers future-you can't follow. Standups don't persist; ticket
links require system context.

**✗ Bad (forced empty):**

> - Nothing to note.
> - No followups at this time.

§7 is optional. If the feature genuinely had no deferrals or rejected
alternatives, leave §7 empty and let `logbook publish` strip it.
*"Nothing to note"* is louder than silence.

**Quality bar.** Each bullet does one thing — decision rejected (with
reason), cookbook candidate, deferral (with revisit trigger), known
gap (with priority). Skipping is valid.

**Cross-form link patterns.** When a cookbook candidate noted in §7
later becomes a real cookbook entry, the §7 bullet is updated manually
with a Zola internal link:

```markdown
- The trait-bound JWT generation pattern is now its own cookbook
  entry: [trait-bound JWT generation](@/posts/cookbook/trait-bound-jwt-generation.md).
```

Or, when the discovery narrative isn't worth preserving:

```markdown
- See [trait-bound JWT generation](@/posts/cookbook/trait-bound-jwt-generation.md)
  for the JWT issuance pattern.
```

The cookbook entry's *"Where it shows up"* section gets a
corresponding manual link back. Bidirectional updates are the
author's discipline.

## Form-level anti-patterns

Section-level anti-patterns are covered in *Writing each section
well*. The three below are *form-level* — they affect the whole post
rather than a single section, and they fall outside any one section's
quality bar.

### Tutorial drift

**Signal.** §3 or §4 starts narrating *process*. *"First, register
your app at console.cloud.google.com. Then wire the trait..."* The
post reads as how-to-build-this-yourself rather than what-got-built —
imperative voice, step-by-step structure, an implied reader who's
going to follow along.

**Why it fails.** A logbook entry is a *description of an artifact*,
not a guide for reproducing it. The usefulness-to-future-you criterion
breaks — future-you doesn't need to be re-taught how to build
something they already built.

**Corrective.** Rewrite descriptively. *"Users can log in with
Google"* not *"First, register your app."* How-to guidance, when it
surfaces, belongs in a *workflows* post.

### Sprint-summary drift

**Signal.** §3 reads as a list — *"Added the login page, the JWT
issuer, the /me endpoint, and fixed a navbar bug."* Title is a date
or sprint label. Evidence in §6 spans unrelated codebase areas.

**Why it fails.** One feature, one post. A logbook whose §3 is a list
is a sprint summary in a logbook costume. The form's questions don't
have coherent answers when the post covers several features.

**Corrective.** Split. The "what does this feature do?" question
failing to answer cleanly is itself the signal that a split is
needed. Each feature gets its own post.

### Project-jargon throughout

**Signal.** Cross-section: §3 says *"Cycle 2 priorities,"* §4
references *"the M2 milestone,"* §7 points at *"Linear ticket
#1234."* Each section is inheriting the author's working vocabulary
rather than the reader's. Same root cause, multiple surfaces.

**Why it fails.** Strip the jargon and the prose collapses. The shape
was scaffolded by process-vocabulary; without it there's no actual
content.

**Corrective.** Anchor in dateable concrete events. *"The work I did
in early May"* instead of *"Cycle 2."* *"After switching to Zola
from Dioxus"* instead of *"Phase 4."* Time anchors and event anchors
survive process changes; jargon doesn't.

## A worked example end-to-end

OAuth login via Google, captured in `omni-me/` and published to
mylearnbase.

### The commands

Run from the project repo's working directory:

```bash
cd ~/projects/omni-me

# 1. Scaffold the capture
logbook init omni-me oauth-login-google \
  --title "OAuth login via Google"

# 2. Fill §3 — What does this feature do?
logbook what oauth-login-google \
  "Users can log in to omni-me using their Google account. The first
   time someone authenticates, a user record is created and a JWT is
   issued; subsequent logins return a JWT for the existing record.
   The JWT identifies the user on every request to /me."

# 3. Fill §4 — Why was it added now?
logbook why oauth-login-google \
  "Multi-device sync was the goal for this stretch of work — laptops
   and phones needed to converge on the same data. That required a
   stable per-user identity, which the standalone-mode app didn't
   have. OAuth was the smallest step that gave us per-user identity
   without taking on password storage ourselves."

# 4. Fill §5 — Scope
logbook scope oauth-login-google \
  "In: Google OAuth flow, JWT issuance, /me endpoint.
   Not in: refresh tokens, account deletion, other providers, session revocation."

# 5. Fill §6 — Evidence (exec + paired cite + cite + screenshot)
logbook exec oauth-login-google bash "cargo test auth::"

cite logbook/_drafts/oauth-login-google.md tests/auth.rs:1 \
  --section "How do we know it works?" \
  --note "Auth handler tests — happy path, invalid token, missing claims, first-time-user JWT issuance."

cite logbook/_drafts/oauth-login-google.md src/auth.rs:42 \
  --section "How do we know it works?" \
  --note "google_login handler — the JWT is issued at the tail of this function."

logbook screenshot oauth-login-google ~/Pictures/login-screen.png

# 6. Fill §7 — Notes (bullets passed as text)
logbook note oauth-login-google \
  "- Considered passwordless email magic-links instead. Rejected — more
     infra (email sender, link expiry, abuse prevention) for marginally
     better UX. Revisit if Google's terms become a problem."

logbook note oauth-login-google \
  "- The trait-bound JWT generation pattern might be a cookbook entry."

# 7. Metadata
logbook tags oauth-login-google "rust, auth, oauth"

# 8. Publish
logbook publish oauth-login-google
```

### The capture before publish

`~/projects/omni-me/logbook/_drafts/oauth-login-google.md`:

```markdown
# OAuth login via Google

*2026-05-10T15:30:00Z by Showboat 0.6.1*
<!-- showboat-id: 4f97e4a7-... -->

> Project: omni-me
> Slug: oauth-login-google
> Tags: rust, auth, oauth

## What does this feature do?

Users can log in to omni-me using their Google account. The first
time someone authenticates, a user record is created and a JWT is
issued; subsequent logins return a JWT for the existing record. The
JWT identifies the user on every request to /me.

## Why was it added now?

Multi-device sync was the goal for this stretch of work — laptops
and phones needed to converge on the same data. That required a
stable per-user identity, which the standalone-mode app didn't have.
OAuth was the smallest step that gave us per-user identity without
taking on password storage ourselves.

## What's in scope (and what's not)?

In: Google OAuth flow, JWT issuance, /me endpoint.
Not in: refresh tokens, account deletion, other providers, session revocation.

## How do we know it works?

[showboat exec block: bash "cargo test auth::" → 4 passed; 0 failed]

[`tests/auth.rs:1`](https://github.com/me/omni-me/blob/abc1234/tests/auth.rs#L1) at `abc1234`
> `mod auth { ... }`
>
> Auth handler tests — happy path, invalid token, missing claims, first-time-user JWT issuance.

[`src/auth.rs:42`](https://github.com/me/omni-me/blob/abc1234/src/auth.rs#L42) at `abc1234`
> `pub async fn google_login(req: Request) -> Result<Json<TokenResponse>>`
>
> google_login handler — the JWT is issued at the tail of this function.

[showboat image block: login-screen.png]

## What's worth remembering or doing next?

- Considered passwordless email magic-links instead. Rejected — more infra (email sender, link expiry, abuse prevention) for marginally better UX. Revisit if Google's terms become a problem.

- The trait-bound JWT generation pattern might be a cookbook entry.
```

### The published post

`~/projects/mylearnbase/content/posts/logbook/omni-me/oauth-login-google.md`:

```toml
+++
title = "OAuth login via Google"
slug = "oauth-login-google"
date = 2026-05-10
draft = true

[taxonomies]
tags = ["rust", "auth", "oauth"]
+++
```

The body is the capture's §3 through §7, in order. Two side effects:

- `login-screen.png` is copied alongside the post at
  `content/posts/logbook/omni-me/login-screen.png`.
- If `content/posts/logbook/omni-me/_index.md` didn't exist, it's
  auto-created with the standard section frontmatter — first-time
  setup for a new project's logbook sub-section.
