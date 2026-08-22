# Editing a post draft (the revision passes)

Once the author has a full draft down, it goes through a fixed sequence of
revision passes. Run all of them, in order, proactively. The author should not
have to ask for each pass by name. What they approve is the *content* of each
pass, not whether the pass happens.

This doc was distilled from editing the CP-4 logbook post *Two Languages, Two
Bottlenecks*. Notes tagged *(CP-4)* are worked examples from that first run.

## Stance

The prose and all technical content belong to the author. You edit, you do not
ghost-write the substance. Fix clarity, structure, and correctness; preserve the
author's voice, their deliberate flourishes, and their technical precision. When
you propose a rewrite you are tightening the author's sentence, not swapping in
your own.

These are learning-series posts that publish only as showcases for a technical
hiring audience. That bar is what makes the accuracy and clarity passes matter.

## Scaffolding the draft (before any editing)

If the author is starting cold, do not hand them a blank screen. Give a light
beat-spine plus pointers to where the author already said each beat in their own
words (mine the session logs). Label every pointer honestly:

- `[YOURS]` only for things the author originated themselves.
- `[OWN IT]` for concepts that were taught or scaffolded, or captured by you in a
  curiosity log. The author re-derives these in their own words. Never dress up a
  model-taught explanation, or a curiosity-log line you wrote, as the author's
  own thinking. If the author cannot re-derive an `[OWN IT]`, that is the signal
  to shore it up before it ships.
- `[FACT]` for measured numbers, stated as measured.

The scaffold is an outline, not a quote bank. The author writes loosely from it,
then you edit.

## Workflow for each pass

1. Read the whole draft for that pass's concern.
2. Present findings as concrete before/after proposals, grouped by beat or theme.
3. The author approves, denies, or rewords each.
4. Implement only what is approved, via exact-match replacement with a count
   assertion so nothing mis-applies.
5. Move to the next pass.

One pass at a time. Do not dump all passes at once (the author cannot respond to
everything in one go). But do move through the whole sequence without waiting to
be prompted for each.

Objective errors (typos, grammar, a factual slip, a missing space) can be applied
directly and reported, the same class as a typo sweep. Everything stylistic is
proposed first.

## The passes, in order

1. **Accuracy.** Verify every claim against the real data. Fetch the actual chart
   or benchmark numbers; do not trust memory. Catch label swaps, overstated
   claims, and wrong numbers. Flag anything you cannot verify.
   *(CP-4: the grid was mislabelled O(n^2) in two places; "faster at all scales"
   was only true inside the tested range and was requalified.)*

2. **Terminology consistency.** One term, one meaning, across the whole post, and
   consistent with the central figure's framing.
   *(CP-4: "vectorization" was doing double duty for both the interpreter-escape
   win and the layout win; it was pinned to the first, and the second was renamed
   "SoA memory layout".)*

3. **Figure integration and interlinks.** Every figure earns a prose pointer
   where it lands. For a progressive-reveal chart, each beat nods to what just
   appeared. Wire interlinks to related posts in both directions (this post to the
   prior one, and a forward pointer added into the prior one). Do not leave
   figures as orphans beside the text.

4. **Flow and transitions.** Each beat opens on its point, not a windup. Cut
   filler openers ("As mentioned previously and repeated several times...", "It's
   important to call out the fact that..."). A beat should not re-argue what the
   previous beat already settled.

5. **Brevity and trimming.** Cut wordy sentences and redundancy. Tighten the
   closing so the thesis lands.

6. **Clarity and run-ons (the thorough one).** Read every single sentence. Split
   run-ons, fix comma splices, fix tense shifts, fix awkward phrasings. Go beat by
   beat. This is the pass most easily under-done. A handful of targeted trims is
   NOT this pass. If the author opens the draft and the very first sentence is a
   run-on, this pass was skipped.

7. **Typo and grammar sweep.** Objective errors. Apply directly and report.

## House style (hard rules)

- No em dashes. Use periods and commas.
- No colons standing in for a banned em dash ("setup: payoff", "claim:
  elaboration"). Split into two sentences. Colons only for genuine lists or
  definitions.
- Preserve the author's deliberate flourishes *(CP-4: "no matter what, every,
  single, time.")*.
- Preserve technical precision the author wrote (shape annotations, exact terms).
- Follow the author's spelling. They use UK spelling (behaviour, neighbour,
  centre).

## Verification discipline

- Apply each edit as an exact-match string replacement with a count assertion, so
  a silent mismatch fails loudly instead of mis-editing the file.
- After any pass with a hard rule, re-check by grep (for example, zero em dashes
  and zero sentence-colons left in the prose).

## Handoff to deploy (after the prose is clean)

Convert to the target form's markdown plus frontmatter and real section headings;
render the figures (extract clean standalone SVGs from any preview artifacts, and
produce any progressive-reveal chart subsets); wire the interlinks and any code
deep-links; ship the demos with the post; do the single irreversible step (for
example flipping a repo public) last, and confirm with the author right before it.
