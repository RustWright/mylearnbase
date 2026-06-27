# Authoring a concepts post

A concepts post centers an **interactive demo** built to help the
author understand a concept they didn't yet grasp. The post is the
artifact of that understanding-by-building. Where a logbook entry
says *"here's the feature I built,"* a concepts post says *"here's
something I didn't understand; here's the demo I built to come to
understand it; here's what clicked when I did."*

The form is new and still finding its shape. This doc is deliberately
**rough and lightweight**: enough to author with, not enough to be
prescriptive. One concepts post now exists, *How indexing can make
search faster* (`content/posts/concepts/how-search-works.md`). Notes
below tagged *(first post)* are what building it taught. With n=1,
treat them as observations, not laws.

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

These are starting points, not requirements. The first post has
begun pressure-testing them (see the *(first post)* notes):

| # | Section | What it carries |
|---|---|---|
| 1 | Title (+ optional stake) | The concept; optionally one personal line on why it was worth a demo |
| 2 | The curiosity moment | Where the question came from; link the logbook entry or project context if applicable |
| 3 | The demo | Interactive, front and center, with a line of setup before and a "what to notice" after |
| 4 | What clicked *(optional)* | What you understood after building it. Include only if something genuinely did; cut it rather than force a takeaway |
| 5 | Where this shows up *(optional)* | Cross-refs: related logbook entries, other concepts posts, external resources |

The spine is the title, the curiosity moment, and the demo. The
stake, "what clicked," and "where this shows up" are all optional.
There is no "anti-patterns" or "when this breaks down" section;
concepts posts are educational, not prescriptive.

*(first post)* The first post shipped without a stake line and
without "what clicked." Its honest answer to "what clicked" was *not
much, about indexing itself* (building the demo was the satisfying
part), so the section was cut rather than padded. A forced reflection
reads flat; an absent one reads fine.

**Who drafts which section.** Descriptive and framing prose (the demo
setup, "where this shows up") the LLM can draft first. The
voice-bearing sections (the stake, the curiosity moment, what
clicked) are the author's to draft first; the LLM polishes but never
invents the author's experience or takeaway. *(first post)* The
polish pass on the curiosity section quietly introduced claims the
author hadn't made and a punctuation habit (heavy em-dashes) the
author wouldn't use. Watch for both: better a plain honest sentence
than a borrowed one.

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

**What the first post taught about making a demo teach** *(first post)*:

- **Pose an objective; don't ship open controls.** An open sandbox has
  no first move, and a cold reader who lands on the page needs a reason
  to touch it. The search demo used a mission ladder (find a common
  word, scale to the whole book, hunt a word that isn't there, then
  "was the index even worth building?"). The objective also forces the
  reader to *do the slow way themselves*, which is the only way the
  payoff lands.
- **The contrast is the teaching.** Put the naive way and the clever
  way side by side and let the reader run both. Feeling the slow way is
  what makes the fast way mean anything. Count the honest cost
  (operations, not wall-clock seconds) so the comparison stays fair
  across devices.
- **Stage freely, but name the staging.** The search demo paces the
  scan so it's watchable (real JS finishes in milliseconds) and uses a
  toy index, not Pagefind's real ranking and chunking. The prose says
  so. A simplification you're honest about teaches; one you hide lies.
- **Data prep is part of the work.** Sourcing a real public-domain
  corpus (Project Gutenberg) and verifying the "ghost" word was truly
  absent (grep returns nothing) was authoring effort, not setup. Real
  material feels different from toy sentences.
- **Comparative demos need room and a notice.** A side-by-side demo
  breaks out wider than the reading column (`demo(wide=true)`) and
  carries its own "works best on a wider screen" note that the demo
  detects and shows itself, rather than baking the caveat into the post
  prose. One-dimensional demos ship universal. The breakout, the
  TOC-dodging, and the self-sizing-on-mobile mechanics live in
  `static/css/custom.css` and the demo's own JS.

## The curiosity log mechanism

Shape (shipped 2026-05-15; used to seed the first concepts post):

- **Location.** A project-local file, `<project-repo>/.curiosities/cycle-<N>.md`.
  Gitignored in the project submodule (same pattern as
  `.log/`); synced via the parent `productive_learning` repo so it
  survives session resets without ending up in the project's public
  history.
- **Append shape.** LLM adds entries during cycle work as it notices
  curiosity surfaces. Rough format: `- [date] <one-line curiosity; what triggered it>`.
- **Review pass.** A dedicated cycle-close session walks the file
  end-to-end and decides what survives.

*(first post)* The trigger model held: a curiosity logged during
Cycle 4 (Zola search turning out to be more than a switch) survived
cycle-close review and became this post. The log works as the
low-cadence on-ramp it was meant to be.

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

## A worked example (the first real post)

The first concepts post grew from a Cycle-4 curiosity: adding search
to this site, assuming Zola's built-in search would be a trivial
switch, and finding out that "built-in search" is really a data
structure that somebody builds and ships.

> **Title.** How indexing can make search faster
>
> **Concept.** The inverted index, framed as a transferable principle:
> *pre-arrange your data around the question you'll ask, so future
> queries are cheap.* Search is just the easiest place to see it; the
> same shape is a database index, a hash map, a cache, a memoized
> function.
>
> **Demo.** A mission ladder over the real text of *The Adventures of
> Sherlock Holmes* (one sentence per "document"), racing a
> top-to-bottom scan against an index lookup: the mechanic on a few
> lines, then scale on the full book, then a word that isn't there (a
> paced wait that ends in "nothing found"), then a break-even slider
> showing when the index's up-front build cost pays off.
>
> **What shipped.** Title, curiosity moment, demo, and "where this
> shows up." No stake line and no "what clicked," for the reasons in
> the section table above.

Two demo ideas sit in the backlog for future cycles: *what hashes
actually do* (the original v0 sketch for this doc), and a
**ranking-by-rarity / relevance** demo that this post's closing
forward-pointer gestures at (once you've found the matches, which
come first?). The ranking demo depends on this one having landed
first.

## What's still rough about this doc

The logbook editorial doc walked six topics in depth: section-by-
section quality bars, anti-patterns, multiple worked examples,
practical tests per section. This doc still doesn't, on purpose.

Concepts has now been authored once. That seeds the *(first post)*
notes above; it doesn't justify writing detailed rules in the
abstract that may not survive post two. The intent stays the same:
give an LLM in another session enough context to *start* an authoring
conversation, not enough to constrain it. Keep iterating as more
concepts posts ship.
