# Authoring a concepts post

A concepts post centers an **interactive demo** built to help the
author understand a concept they didn't yet grasp. The post is the
artifact of that understanding-by-building. Where a logbook entry
says *"here's the feature I built,"* a concepts post says *"here's
something I didn't understand; here's the demo I built to come to
understand it; here's what clicked when I did."*

The form is new and still finding its shape. This doc is deliberately
**rough and lightweight** — enough to start authoring with, not
enough to be prescriptive. Expect substantial revision after the
first real concepts post exists.

## What concepts is for

The form fires when **two conditions** hold at once:

1. A specific concept came up in real project work that you don't
   fully understand.
2. You suspect building a small interactive demo would be how you'd
   come to understand it — better than reading docs or asking the
   LLM to explain in prose.

The interactive demo is the centerpiece, not a decoration. Without
one, this isn't a concepts post — it's likely an opinions post (if
the take is the point), a resources post (if pointing at others'
explanations is the value), or notes worth keeping unpublished. The
interactivity is what makes the form earn its place; it's also what
makes the form authentically the author's even when the LLM writes
the underlying code. Choosing *what makes the concept teach* is the
author's intellectual work, and it can't be outsourced.

**Decision rule among the forms:**

- *About a feature you built* → logbook.
- *Steps someone should follow* → workflows.
- *A concept you needed to understand, where an interactive demo is
  the teaching instrument* → concepts.
- *A take and the take is the point* → opinions.
- *Pointing at external content with annotations* → resources.

## When to write a concepts post

The trigger model is **cycle-close review of a curiosity log**, not
spontaneous publication.

The mechanism:

- **During a cycle**, the LLM notes concepts that come up — things
  the user asks questions about, things the user says "I don't
  really get how this works" out loud about, things the LLM
  half-explains and moves past. These accumulate in a project-local
  curiosity log (see below).
- **At cycle close**, after code reviews and the cycle's logbook
  entries are squared away, a dedicated session walks the curiosity
  log. Which entries still hold attention? Which still feel
  unfinished? Which lend themselves to demo-ing?
- **Survivors become concepts candidates.** Most curiosities will not
  survive — they got resolved during the cycle, or interest faded.
  That's expected. **A cycle that produces zero concepts candidates
  is a normal cycle.** This form has low cadence by design.

If a concept survives review and the author has the time, the next
move is an iterative demo-build session — LLM and author going back
and forth until the demo feels clean enough to satisfy the original
curiosity. The post is written around the resulting demo.

## What concepts is NOT for

- **Generic pattern aggregation.** *"Here's the singleton pattern"*
  with no project anchor is a Wikipedia article, not a concepts
  post. The genuine confusion-to-understanding journey is what makes
  the post earn its place.
- **Forced posts.** If no concept survives cycle-close review, no
  post fires. Don't manufacture a curiosity to fill the slot.
- **Posts without a real demo.** If the concept doesn't yield to
  interactivity — if the explanation is genuinely best in prose —
  it isn't a concepts post. Use opinions or workflows instead.
- **Posts where the click never happened.** The *satisfying* half of
  the *useful + satisfying* criterion fails. Sit on the draft until
  understanding arrives, or drop the candidate. Shipping a demo that
  didn't teach the author is dishonest to both readers and future-
  self.

## The shape of a concepts post

These are starting points, not requirements. The first real concepts
post will pressure-test them:

| # | Section | What it carries |
|---|---|---|
| 1 | Title + one-line stake | The concept; what made you build a demo for it |
| 2 | The curiosity moment | Where the question came from; link to the logbook entry or project context if applicable |
| 3 | The demo | Interactive, front and center |
| 4 | What clicked | What you understood after building it; what misunderstandings you held before |
| 5 | Where this shows up *(optional)* | Cross-refs — related logbook entries, other concepts posts, external resources |

Sections 1–4 are required; section 5 is optional. There is no
"anti-patterns" or "when this breaks down" section like cookbook had
— concepts posts are educational, not prescriptive.

## The demo

Two cross-form notes:

- **Same shortcode as logbook portfolio demos.** Logbook uses
  `{{ demo() }}` to embed an interactive artifact as
  *evidence-that-the-feature-works*. Concepts uses the same shortcode
  for the demo as *teaching-instrument*. Different jobs; same
  mechanism. A reader of a logbook demo plays with it to verify;
  a reader of a concepts demo plays with it to learn.
- **Build iteratively.** The demo-build is LLM-and-author back and
  forth. The LLM writes most of the code; the author chooses what to
  expose, what to hide, what interactions surface the concept's hard
  part. The decisions about *what makes this teach* are the author's
  — that's the part the LLM cannot do, and it's where the intellectual
  ownership lives.

## The curiosity log mechanism

Provisional shape (refine when first implemented):

- **Location.** A project-local file — likely `<project-repo>/.curiosities/<cycle-id>.md`
  or similar. Gitignored in the project submodule (same pattern as
  `.log/`); synced via the parent `productive_learning` repo so it
  survives session resets without ending up in the project's public
  history.
- **Append shape.** LLM adds entries during cycle work as it notices
  curiosity surfaces. Rough format: `- [date] <one-line curiosity; what triggered it>`.
- **Review pass.** A dedicated cycle-close session walks the file
  end-to-end and decides what survives.

This mechanism hasn't shipped yet. The first concepts cycle will
likely surface refinements to all three points above.

## Where it lives

Concepts posts live at `<mylearnbase>/content/posts/concepts/<slug>.md`.
No form-specific tooling exists yet — author directly under that path.
The demo's static assets (HTML / JS / WASM / images) go in
`<mylearnbase>/static/demos/<slug>/` and are embedded via the
`{{ demo() }}` shortcode.

The `cookbook` tools (`cookbook init`, `cookbook publish`, etc.) were
built around an earlier form definition that doesn't apply here.
They're left in place but unused for concepts posts; whether to
repurpose or retire them is a downstream decision.

## A worked sketch (not yet real)

The first concepts candidate, identified during the design
conversation that produced this doc:

> **Title.** What hashes actually do (a demo)
>
> **Stake.** Built an upload-validation feature for omni-me that
> hashes a file's bytes with SHA-256 on the client and re-verifies
> on the server. Realized mid-implementation that "what a hash
> actually is" wasn't something I understood — just that this is
> what one does for upload integrity. Built this demo to come to
> understand them properly.
>
> **Demo modes (sketch).**
>
> - An input box where typing produces the live SHA-256 hash.
> - SHA-256 vs SHA-512 side-by-side on the same input.
> - The avalanche effect — change one character, watch the whole
>   hash transform.
> - A simulated client→server handshake mirroring the omni-me
>   upload-validation feature.
>
> **What clicked (anticipated).** Before the demo, hashes lived in
> my head as "compression with a checksum vibe." After: a fixed-size
> summary where small input differences produce uncorrelated
> outputs, and reversal is not a design goal but the *opposite* of
> the design goal.

This is a sketch, not a real post. When it gets built, expect this
editorial doc to update with what the authoring rhythm actually felt
like — that's the point of having a rough doc rather than a
prescriptive one.

## What's deliberately rough about this doc

The logbook editorial doc walked six topics in depth — section-by-
section quality bars, anti-patterns, multiple worked examples,
practical tests per section. This doc doesn't.

The reason: prescriptive editorial assumes the form has been
authored enough times to know what its rules are. Concepts has been
authored zero times. Writing detailed rules in the abstract would
manufacture editorial constraints that may not survive contact with
the first real post.

The intent of this v0 is to give an LLM in another project session
enough context to *start* an authoring conversation — not enough to
constrain it. Iterate after the first hash-demo post is real.
