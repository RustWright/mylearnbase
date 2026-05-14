+++
title = "Authoring an opinions post"
slug = "authoring-an-opinions-post"
date = 2026-05-14
draft = false
+++

An opinions post is a personal take where *the take itself is the
point* — not a feature, not a pattern, not a procedure. Length is
whatever the take needs. Voice is yours, full stop. Posts can live in
`draft = true` for weeks or months without that being workflow
failure.

The form has a unique optimization target: **willingness to post**.
Not length, not polish, not completeness. A half-polished take that
ships beats a fully-polished take that never does. The form is named
"opinions" rather than "essays" deliberately — to escape the
connotations (rigor, length, defensibility) that would raise the bar
past the point of usability.

This is also the form to use as a deliberate vehicle to grow as a
writer — not as a performance vehicle. The LLM's role here is
**thinking partner**, not first-drafter — it helps find the take
(Phase 1 prompting) and clean up the prose (Phase 6 mechanical), but
it does not write the post.

## When to write an opinions post

Use this form when:

- You have a take you want to put words to.
- A perspective has been simmering long enough that you want to write
  it down.
- An opinion surfaced while drafting another form and wants to be
  pulled out as standalone.
- An external trigger (article, conversation, mid-work frustration)
  prompted a reaction worth keeping.

Don't use this form when:

- The post is about a feature you built. (Use a *logbook* post.)
- The post is an interactive demo built to understand a concept. (Use
  a *concepts* post.)
- The post is a prescriptive procedure. (Use a *workflows* post.)
- The value is mostly in pointing at external content. (Use a
  *resources* post.)

Wherever the impetus to write comes from, the handling is the same:
seed → flesh into draft with LLM prompting (depth-dialed) → revise
into something you're willing to post.

## Author disciplines

Two practices live with the author, not with any LLM check. They're
not gates — just observational nudges as you build the writing habit.

- **Own the take.** First-person — "I think," "in my experience," "I
  suspect" — rather than hedging into "people often say" or "many
  would argue." If the take is yours, claim it.
- **Length follows the take.** A three-sentence take is fine; a
  two-thousand-word take is fine. Padding for the appearance of
  seriousness is the failure mode. So is truncating because the take
  feels too short to count.

Other writing-quality concerns (specificity, internal consistency,
overclaiming) live inside Phase 4's substantive feedback tiers, where
they're applied on request rather than carried as standing rules.

## The workflow

Seven phases, à la carte. You can enter at any phase and walk forward
from there. "Slow-refinement" and "fast-spontaneous" are convenient
labels for the all-phases and minimal-phases endpoints, but the real
shape is a spectrum.

| Phase | Activity | LLM role | Default or opt-in? |
|---|---|---|---|
| 1. Point-finding | Figure out what's being said and why | Prompting modes (provocation / multiple framings / mirror-and-probe); never first-drafter | Default available; skippable |
| 2. Structure pass | Talk through organization; output is an outline | Discussion partner | Default available; skippable |
| 3. Drafting | User writes the prose | Silent unless asked | — |
| 4. Substantive feedback | Tier 1 default-suggest; tiers 2/3 on request; tier 4 deferred | Reviewer per requested tier; user reworks the prose themselves | Tier 1 suggest-then-decide; tiers 2-4 on request |
| 5. Revision | User revises; can loop back to phase 4 | Silent unless asked | — |
| 6. Mechanical pass | Grammar, typos, awkward phrasing, broken links, title revisit (time-boxed) | Returns suggestions; on approval, implements directly | Default-on before publish |
| 7. Publish | Flip `draft = false`, run `zola check` | Tool-driven | — |

The asymmetry between Phase 4 and Phase 6 is deliberate. Substantive
feedback names observations the user has to act on themselves (their
voice, their judgment). Mechanical fixes are surface-level and
unambiguous once approved, so the LLM implements them directly —
faster, and not risky.

### Phase 1 — Point-finding

Phase 1 is the conversation that helps you figure out what you're
trying to say before drafting. Three prompting modes are in the
active toolkit.

**Provocation** *(default opener)* — LLM proposes an extreme version
of your own argument. Same direction, pushed along whatever dimension
is in play, until it twists into something you didn't mean. You react
against it; what you keep is your actual position, and what you
reject locates where the absurd version stops matching your stake.

Provocation is the default opener because reacting to a distortion of
your own take forces examination of what you actually believe more
reliably than reflecting on flat substance.

Crucially: *provocation is not a counter-argument*. The LLM should
not draft an opposing position. If the proposed extreme version
disagrees with your direction, it has misread the mode.

**Mirror-and-probe** *(the consolidator)* — you share raw thoughts;
the LLM restates ("what I'm hearing is...") and asks one focused
follow-up; iterate. Used after provocation or multiple-framings to
consolidate the resulting pushback into a clearer position.

**Multiple framings** *(branching alternative to provocation)* — the
LLM offers three candidate angles for what you might be getting at;
you pick the closest, refuse them all, or use one as a springboard.
Useful when the seed is too thin to provoke against, or when the
take has branched and you want help organizing.

**Default chain for a Phase 1 session:**

```
session start
    |
    v
Provocation        <- forces reactive examination
    |
    v
Mirror-and-probe   <- consolidates the pushback into a clearer position
    |
    v
[pause - user picks next]
    |       |
    v       v
Provocation    Multiple framings
    |       |
    v       v
Mirror-and-probe (in both branches)
    |
    v
[iterate; pause between cycles]
    |
    v
Summary on request    <- LLM restates the user's opinions clearly
    |
    v
End of Phase 1
```

Properties of the chain:

- **Pause-and-ask** between cycles — the LLM doesn't pick the next
  mode unilaterally.
- **Mirror-and-probe is the consolidator** after each provocation or
  framings move, not a standalone opener.
- **Summary on request closes Phase 1.** When you feel like you've
  thought through the take cleanly, ask for a summary — the LLM
  restates the surfaced opinions back to you in a clear list. That
  list is Phase 1's terminal output, ready for Phase 2 (structure) or
  Phase 3 (drafting) to pick up.

**Direct interrogative questions ("what's the point of this?") are
explicitly off-limits.** They trigger school-essay defences and
shut down thinking. Use the three named modes; nothing flatter.

### Phase 2 — Structure pass

Talk through how to organize the take. Output is an outline. Skip if
the structure is obvious from the Phase 1 summary or if the take is
short enough that scaffolding is overhead.

### Phase 3 — Drafting

You write. The LLM is silent unless asked. This is the form's
non-negotiable rule: the take is yours, in your voice, written by you.
The LLM never first-drafts opinion prose.

### Phase 4 — Substantive feedback

You share a draft and request the tier you want. Tier definitions:

**Tier 1 — default suggest.** When you share a draft, the LLM asks if
you want Tier 1 feedback. You decide per-post. The Tier 1 set:

- **Clarity** — can the LLM restate the central claim in one
  sentence? If not, what's blurry?
- **Internal consistency** — do later paragraphs contradict earlier
  ones?
- **What's missing** — is there an obvious counterargument or piece
  of context the post doesn't acknowledge?

**Tier 2 — on request.**

- **Steelman** — the strongest version of the opposing view. You
  decide whether your take survives.

Tier 2 is on-request specifically because steelmanning too early
shuts an embryonic take down before it forms.

**Tier 3 — demonstrate on a single paragraph on request.**

- **Specificity gap** — pick a vague claim; suggest a concrete
  example or counterexample.
- **Overclaiming / underclaiming** — flag where the claim is stronger
  or weaker than the evidence supports.
- **Emotional truth** — does the prose feel lived or hollow?

Tier 3 is paragraph-scoped because applying these to a whole post is
overload; applying them to one paragraph lets you carry the lesson
forward to the rest yourself.

**Tier 4 — deferred.**

- **Voice authenticity** — needs a corpus of opinion posts to
  compare against. Revisit once around five posts exist.
- **Audience match** — needs an actual audience. Revisit when there
  are readers.

After feedback, you do the rework. The LLM stays silent unless asked.

### Phase 5 — Revision

You revise. You can loop back to Phase 4 with a revised draft if you
want another round. The LLM is silent unless asked.

### Phase 6 — Mechanical pass

The LLM produces a list of mechanical issues:

- Grammar and typos
- Awkward phrasing at the sentence level (not structural)
- Broken or missing links
- **Title revisit** — a low-stakes glance: does the working title
  still fit the finished post? If nothing obviously better surfaces
  in a minute or two, ship the working title. Title perfectionism is
  a willingness-to-post killer dressed up as craft.

You approve or reject each item (or batch-approve). The LLM
implements the approved fixes directly. This is the one phase where
the LLM modifies the post for you — because mechanical fixes are
surface-level and unambiguous once approved.

### Phase 7 — Publish

Flip `draft = false`. Run `zola check`.

## Entry points

Common entry points into the phase sequence:

| Entry | Triggered when | Subsequent phases |
|---|---|---|
| Phase 1 | You have a seed, no draft yet | 1 → 2 → 3 → 4 → 5 → 6 → 7 (full slow) |
| Phase 3 | Take is clear, want to draft solo first | 3 → 4 → 5 → 6 → 7 |
| Phase 4 | Have a draft, want it reviewed | 4 → 5 → 6 → 7 |
| Phase 6 | Have a finished draft, just want polish | 6 → 7 (fast-spontaneous) |
| Phase 7 | Ready to ship as-is | 7 only |

The LLM figures out which entry point you're at via:

1. **You declare.** "Want feedback on this draft" → Phase 4. "Just
   check typos before I publish" → Phase 6. "Help me think through
   this" → Phase 1. Most sessions land here cleanly.
2. **LLM asks if ambiguous.** When you share an artifact without
   context, one short disambiguation question: "Where do you want to
   enter — point-finding, substantive feedback, or mechanical pass?"
3. **Inference from artifact shape.** A seed sentence → Phase 1. A
   finished-looking draft + "ready to publish" → Phase 6.

## Anti-patterns

1. **Optimizing for polish over willingness.** The form's
   optimization target is willingness to post; the failure mode is
   polishing past the point of shipping. Half-polished that ships
   beats fully-polished that doesn't.
2. **LLM first-drafting the prose.** The take is yours. The LLM helps
   find it (Phase 1) and clean it up (Phase 6). It does not write it.
3. **Treating `draft = true` as workflow failure.** Posts living in
   draft for weeks or months is the slow flow working as intended,
   not a stuck workflow.
4. **Steelmanning an embryonic take.** Phase 4 Tier 2 is on-request
   because steelmanning too early kills a take before it forms.
5. **Agonizing over the title.** Phase 6 title revisit is a time-boxed
   glance. If no obviously-better title surfaces in a minute or two,
   ship the working title.
6. **Adding school-essay scaffolding when the take doesn't need it.**
   Intro / thesis / three body paragraphs / conclusion is the
   structure school taught — and the connotation the form was named
   away from. Some takes need structure; many don't. Forcing
   scaffolding onto a short take is a hedge against feeling exposed
   by brevity.

## Worked example

A full slow-refinement walk-through on a single seed, followed by
two compressed variants showing entry at Phase 3 and Phase 6.

The example seed is intentionally low-stakes and not a real take —
substitute your own when running this for real.

### Slow refinement (Phase 1 → 7)

**Seed:** *I think people overrate the productivity boost from a
second monitor.*

**Phase 1 — Point-finding:**

```
You: I think people overrate the productivity boost from a second
     monitor.

LLM (provocation, opening):
  Extreme version: there is no productivity gain from second monitors
  at all. The entire dual-monitor industry is performative theater.
  Every developer who claims a real benefit is rationalizing a $300
  desk-decoration purchase into a productivity tool. Push back.

You: No - I do think there's a real gain, just smaller than the hype.
     The marketing acts like 5x productivity, when realistically it's
     maybe 5-10% for tasks that actually need two surfaces.

LLM (mirror-and-probe):
  What I'm hearing is that you accept the gain is real but reject the
  magnitude that's marketed - the take is about the gap between
  marketed and actual gains, not about second monitors being useless.
  Is that closer?

You: Yes, and also that for a lot of devs the gain is zero because
     they don't actually use both screens - one becomes a Slack and
     distraction parking lot.

LLM (pause):
  Take is sharpening. Two threads have surfaced: (1) the magnitude
  gap between marketing and real gains, (2) for many devs the second
  screen becomes a distraction sink. Next: another provocation,
  multiple framings to organize these, or summary?

You: summary

LLM (summary - closes Phase 1):
  Your opinions so far:
  1. Second monitors provide a real but modest gain (~5-10%), well
     below the marketed promise.
  2. The benefit materializes only when tasks genuinely use two
     surfaces.
  3. For many developers, the second screen becomes a Slack and
     distraction parking lot - zero or negative value.
  4. The marketing-vs-reality gap is the actual story you want to
     tell.
```

**Phase 2 — Structure pass:** discuss organization, output an
outline. (Content varies per take; skipped here for space.)

**Phase 3 — Drafting:** you write the prose. LLM silent.

**Phase 4 — Substantive feedback:**

```
You: [shares draft]

LLM: Want Tier 1 feedback (clarity, internal consistency, what's
     missing)?

You: yes

LLM (Tier 1):
  - Clarity: the central claim restates as "second-monitor
    productivity gains are real but marketed at roughly 5x reality."
    That sentence isn't in the draft - consider adding it explicitly
    in the lede.
  - Internal consistency: paragraph 2 says "many devs get zero
    benefit"; paragraph 4 says "everyone gets some benefit from a
    second screen for code review." Reconcile.
  - What's missing: no acknowledgement of why the marketing-vs-reality
    gap exists - is it pure marketing, or do devs self-deceive after
    purchase?
```

You decide which observations to act on, then rework the prose
yourself.

**Phase 5 — Revision:** you revise. LLM silent.

**Phase 6 — Mechanical pass:**

```
LLM: Mechanical review:
  - 3 typos: para 2 "definately" -> "definitely"; para 5 "thier" ->
    "their"; para 6 missing closing quote.
  - 1 awkward phrasing: "the productivity that is gained when one is
    using two screens" -> "the productivity gained from two screens."
  - All links resolve.
  - Title revisit (low-stakes glance): working title is
    "second-monitor-take." Quick alternatives:
    "What Two Monitors Actually Give You" or
    "The Dual-Monitor Productivity Gap." Pick one or keep working
    title - don't agonize.

You: approve all typo and phrasing fixes; keep working title.

LLM: [implements the approved fixes directly in the post]
```

**Phase 7 — Publish:** flip `draft = false`, run `zola check`.

### Variant: entry at Phase 3 (clear-idea-then-feedback)

You have a clear take and want to draft solo before involving the
LLM. Open the file, write the post, then enter the workflow at
Phase 4 by sharing the draft and saying "ready for substantive
feedback." Continues through Phase 5, 6, 7 normally.

### Variant: entry at Phase 6 (mechanical-only)

You have a finished draft and just want polish before publish. Share
the draft with "just need mechanical review." LLM produces the
mechanical-issue list as in Phase 6 above; you approve/reject; LLM
implements; you publish.

## Optional starter template

```markdown
+++
title = "..."  # working title - revisit before publish, don't agonize
slug = "..."
date = ...
draft = true
[taxonomies]
tags = []
+++

<!-- Pre-writing modes (optional; ask the LLM for one or several,
     or skip entirely):
  Provocation        - LLM proposes an extreme version of your own
                       argument; you push back to find your actual
                       position. Recommended opener.
  Multiple framings  - LLM offers candidate angles; you pick closest.
  Mirror-and-probe   - LLM restates and probes; you iterate.
-->

[your post starts here]
```

The HTML comments are visible while drafting and invisible if the
post is rendered without them being removed — the lowest-bar
scaffolding the form has.
