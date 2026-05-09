+++
title = "Cycle 2: Document-Then-Triage Code Review"
slug = "cycle-2-four-perspective-review"
date = 2026-04-26
draft = true

[taxonomies]
tags = ["code-review", "rust", "surrealdb", "testing", "claude-code", "omni-me"]
series = ["Building omni-me"]

[extra]
series_order = 7
+++

## Reflections

<!-- This section is written by the human author — replace this with your thoughts -->

---

## Tutorial: Document-Then-Triage Code Review

The [Cycle 1 review post](@/posts/2026-04-15-post-cycle-code-reviews.md) introduced a four-perspective review process: separate passes for security, performance, bloat, and logical inconsistencies, with a "fix / defer / keep" disposition framework. The process worked. It also revealed enough rough edges that I wanted to refine it before doing it again.

This post is about that refinement. Same four perspectives, same project (omni-me, the Rust/Tauri/Dioxus personal-data app this series has been chronicling), different process. The headline change: instead of generating a review document, walking through it, and then sitting down to fix things, Cycle 2 split the work into a document phase and a triage phase --- and the triage phase fixes things inline as each finding is decided, not in a batched session afterwards.

I also experimented with a mixed-model strategy: Opus 4.7 for the reviews where holding many invariants in your head pays off (security, logic), Sonnet 4.6 for the more pattern-matching reviews (performance, bloat). That experiment worked, with a calibration caveat I'll get to.

This is part 2 of a two-post series on Cycle 2. [Part 1](./2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md) covers the implementation work --- the calendar feature, the Obsidian import/export pipeline, auto-save. This post stays in its lane: the review process and the findings that came out of it.

### Assumptions

- Primary OS: Linux (Ubuntu 24.04, kernel 6.8, x86_64). Cross-platform note: the review process itself is OS-independent. You need Claude Code (or any equivalent agent loop) and a Rust toolchain to run `cargo test` and `cargo clippy`. macOS and Windows users should not have to adapt anything.
- Models: Claude Opus 4.7 for the security and logic reviews, Sonnet 4.6 for performance and bloat. Both via Claude Code.
- Codebase context from earlier posts: a Rust workspace with `core`, `server`, `tauri-app/src-tauri`, and `frontend` (Dioxus, compiles to WASM). Event-sourced data on SurrealDB. Text editing through CodeMirror 6, embedded in Dioxus via direct JS interop in the same WebView.
- The reviews directory (`reviews/`) is git-ignored on this project. Review documents live locally; only the resulting code changes are committed. This is deliberate --- I want the freedom to write candidly during review without it becoming a permanent artifact.

---

### What changed between Cycle 1 and Cycle 2

#### Document-then-triage instead of three coding phases

The Cycle 1 process was loosely "generate, decide, fix" --- I'd produce all four review documents, walk through each finding to choose fix/defer/keep, and then fixes would happen in their own session. That created a momentum problem.

The momentum problem: findings interact. A logic finding about a missing transaction can change how I want to triage a performance finding about query batching. A bloat finding about duplicated code can become moot once a logic finding forces a refactor that removes the duplication anyway. If I triage everything first and then fix everything, I'm forced to predict those interactions before I have the information to predict them well.

Cycle 2's flow:

- **Phase A (document):** Run all four reviews in parallel across separate Claude Code sessions. Output is four `reviews/2026-04-24-*.md` files, each enumerating findings for its dimension. No code changes yet.
- **Phase B (test-gap audit):** A separate fifth pass that proposes regression tests --- but only as a *proposal document*. No test code is written until I've triaged the proposals. ([Cycle 1 taught me](@/posts/2026-04-15-post-cycle-code-reviews.md) that letting an agent write tests speculatively produces a lot of plausible-looking noise.)
- **Triage (interleaved with fixing):** Walk through findings one at a time. Each finding is dispositioned (fix / defer / document / reject) on its own. When the disposition is "fix," the fix lands *in that step*, not batched at the end.

The interleaving is the part that actually mattered. By the time I got to logic Warning #5 (about a missing transaction in `on_group_reordered`), I'd already fixed Critical #1 and Critical #2, and the context I'd built up while fixing them changed how I wanted to handle W5. It led to a written transaction policy across the whole codebase --- something I wouldn't have arrived at if I'd been ticking through pre-decided dispositions.

#### Mixed-model strategy

Cycle 1 ran all four reviews on Opus. That was expensive. Cycle 2 split:

- **Opus 4.7** for security and logic. These reviews require building counter-example reasoning, holding many invariants across files, and judging subtle ordering and causality. The model needs to ask "what state is the system in when this code runs, and is that the same state the code assumes?" --- a question Opus answers materially better.
- **Sonnet 4.6** for performance and bloat. These are closer to pattern matching: "is this allocation in a hot loop?", "is this duplicated logic?", "could this string concatenation be a `format!`?". Sonnet handles these well at a fraction of the cost.

The split held up. Sonnet found real performance wins and real bloat. But it also produced one calibration finding worth highlighting up front, because it's the kind of thing you only catch by checking.

**Sonnet over-counted twice in the bloat review.** Finding #1 claimed three sites duplicated an "append event then apply projection" pattern. When I greppped, the count was actually two --- the third was structurally different (`import.rs` uses a batched `append_batch` path that doesn't fit the same shape). Finding #2 misidentified a different computation as a duplicate of an existing function.

The lesson: **bloat reviews need a higher grep-tax than other tiers**. The reviewer's claims about repetition look the most concrete --- "these three files all have this pattern" --- but they're also the easiest to verify mechanically and the easiest to get wrong without verification. Before refactoring on a duplication claim, run the grep yourself.

I'll come back to this when we get to the bloat review section.

---

### Phase A: producing the four review documents

The setup: four parallel Claude Code sessions, each pointed at the same codebase with a different review prompt. Each session produces a single Markdown document under `reviews/` with a date prefix and the dimension name. The document structure is roughly:

```markdown
# Logic Review — 2026-04-24

## Critical

### #1: <short title>

**Where:** path/to/file.rs:LINE

**Finding:** <description of the bug>

**Why it matters:** <user-visible impact>

**Suggested fix:** <one or two options>

### #2: ...

## Warning

### #4: ...

## Info

### #8: ...
```

The Critical / Warning / Info tiers are the reviewer's first-pass severity guess. I don't take these as binding --- triage routinely promotes or demotes severity --- but they help me decide which findings to read first.

A few things that help the document phase produce useful output:

- **Don't ask for fixes in the document.** The reviewer's job here is to surface findings clearly. Fix design comes later, with my judgement and the broader codebase context in the loop. Asking for a fix in the same pass tends to anchor the reviewer on a particular solution and obscure the underlying bug.
- **Insist on file/line citations.** A finding without `path/to/file.rs:LINE` is a finding I have to go re-discover before I can triage it. That's wasted time.
- **Keep the tiers honest.** If I see a "Critical" that turns out to be a style preference, I push back in triage. If a "Warning" is actually a quietly-broken invariant, I promote it. The tiering is the reviewer's first guess, not a contract.

For Cycle 2, the four documents totalled around 35 findings across the four dimensions, plus 12 test-gap proposals from the separate audit pass.

---

### Triage walk-through: one representative finding per review

Rather than enumerate all 35 findings, I'm going to walk through one from each review end to end --- the bug, the fix, the regression test, the disposition rationale --- and then call out the patterns that show up across multiple findings.

#### Logic Critical #1: `Frequency::Monthly` silently skips short months

**The bug.** A routine scheduled monthly with anchor day 31 (or 30, or 29) would silently skip months that don't have that day. February 31 doesn't exist, so the next-due calculation would overshoot, and the routine wouldn't fire that month. The user would have no signal --- no error, no warning, just a missed habit.

This is the worst kind of bug because it fails silently. The whole point of a routine system is "this nudges me when I forget"; if the nudge itself goes missing, the user only finds out by independently noticing they haven't been nudged.

**The fix.** Introduce a `last_day_of_month` helper that uses chrono's "biggest valid day wins" pattern: when the requested anchor day exceeds the month's length, clamp to the last valid day of the month.

```rust
use chrono::{Datelike, NaiveDate};

fn last_day_of_month(year: i32, month: u32) -> u32 {
    // Find the first day of the next month, then step back one day.
    // This handles all month lengths (28/29/30/31) without a lookup table
    // and gets leap years for free via chrono's calendar logic.
    let next_month_first = if month == 12 {
        NaiveDate::from_ymd_opt(year + 1, 1, 1)
    } else {
        NaiveDate::from_ymd_opt(year, month + 1, 1)
    };
    next_month_first
        .expect("month + 1 is always valid for a valid (year, month)")
        .pred_opt()
        .expect("first-of-month minus one day is always valid")
        .day()
}
```

Then in the next-due calculation, the anchor day is `min(requested_day, last_day_of_month(year, month))`.

I wrote this helper myself rather than taking the model's suggestion --- a "Learn-by-Doing" pattern I've been using through this project where I write the load-bearing logic by hand to internalise it. The agent provided the surrounding scaffolding and the regression tests.

**Regression tests added.**

- Short-month clamp: a routine anchored to day 31 in January correctly clamps to 28 (or 29) in February.
- Leap-year Feb 29: 2024 and 2028 give 29, non-leap years give 28.
- Century rule: 2100 is *not* a leap year (divisible by 100, not by 400), 2000 *is* (divisible by 400). The "every-400" rule is exactly the kind of edge case a fix-by-feel approach gets wrong, so it's worth locking in.
- Exhaustive month-length check: a parameterised test that walks every (year, month) in a range and asserts the helper matches the expected length.

**Pattern worth highlighting: triaging one finding can surface a separate, undocumented assumption elsewhere.** While fixing this, I noticed that the Daily Flow consistency visualizer hard-codes a 7-day window. That assumption was reasonable in Cycle 1 --- everything was daily back then. Cycle 2 added Weekly, Biweekly, Monthly, and Custom-N frequencies. A 7-day window now produces wrong consistency numbers for non-daily routines: a weekly routine done every week looks "1 of 7 days complete" instead of "1 of 1 windows complete." Trip-wire surfaced. Filed for Cycle 3.

The general shape: when you fix a finding in domain X, you've just spent the time to load the domain's invariants into your head. Use that loaded context to look around for related assumptions before you put it down. It's the cheapest time you'll ever have to find adjacent bugs.

#### Logic Critical #2: journal template's YAML list breaks the frontmatter parser

**The bug.** The journal template was emitting `tags` as a YAML block list:

```yaml
---
date: 2026-04-25
tags:
  - daily_note
homework_for_life: ...
grateful_for: ...
learnt_today: ...
---
```

The parser (`notes_projection::extract_frontmatter_properties`) walks lines looking for `key: value` pairs. The line `- daily_note` is not a `key: value` pair --- it's a YAML list item --- and the parser was treating that as the end of the frontmatter. Result: it never saw the three reflection-property keys below the list. `is_complete` always returned `false`, so the auto-close-journal-at-end-of-day logic never fired.

This is the same shape of bug as the Monthly one: silent failure of a behaviour that's only visible in its absence. If you don't actively look for the auto-close to happen, you won't notice it isn't happening.

**Two fix options on the table.**

- **Option A (template change):** emit `tags: [daily_note]` inline instead of as a block list. The parser handles inline values fine. Quick fix, doesn't require parser work.
- **Option B (parser hardening):** change `extract_frontmatter_properties` to skip non-`key: value` lines (including YAML list continuations) instead of terminating. Bigger change, but it would also handle whatever else users might put in their frontmatter.

I picked Option A. The rationale isn't "Option A is smaller" (although it is). It's that the journal-editor properties UI is on my [rework backlog](https://example.invalid/rework). I'm planning a substantial overhaul of how reflection properties are entered and displayed. Investing in parser hardening for code that's slated for replacement doesn't pay back; the work would be thrown away.

**Regression test added.** A cross-crate test, `notes_projection::tests::is_complete_recognizes_journal_template_when_filled`, with a hard-coded filled-template fixture (date, inline tags, all three reflection properties populated). The fixture pins the template's actual on-disk shape, so if a future template change accidentally reintroduces the block-list problem, this test fails.

**Pattern worth highlighting: when two fix options exist, prefer the one whose risk-shape doesn't depend on code paths slated for rework.** Option A is robust against the upcoming editor rework because the template can change shape independently. Option B would couple the fix to the parser; if the parser gets rewritten as part of the rework, the fix would need to migrate too.

#### Logic Warning #5: SurrealDB transaction policy

**The finding.** `on_group_reordered` runs N updates --- one per group whose `display_order` field changes when the user drags a group to a new position. There's no transaction. If the third update fails, you're left with rows half-reordered, which is worse than the original state.

I started to write the fix --- wrap the N updates in `BEGIN ... COMMIT` --- and then stopped to ask a more general question. **How many `db.query` sites are there in the codebase, and how many use transactions?**

A grep gave the answer: 26 `db.query` sites, 1 transaction. That's a policy gap, not a one-off bug.

**The policy I adopted.**

- **Default: single-statement, no transaction.** SurrealDB statements are atomic at the statement level. If a single UPDATE or CREATE fails, it fails atomically. No transaction needed.
- **Multi-statement coupled writes: wrap in `BEGIN ... COMMIT`.** If two or more statements only make sense if they all land --- like reordering groups, where the new ordering is meaningless if only some of the updates succeeded --- wrap them. Example: the `on_group_reordered` fix below.
- **Multiple SETs on the same row: collapse into one UPDATE with conditional SETs.** This was the most surprising part of the policy for me. If you find yourself writing three sequential UPDATEs against the same row, the right answer is usually one UPDATE with conditional SETs --- the same pattern that `append_batch` uses. Atomic by construction; no transaction overhead.

**The two fixes that came out of this.**

```rust
// on_group_reordered: dedup by group_id (last write wins via HashMap)
// then wrap N updates in a single BEGIN/COMMIT.
let mut by_group: HashMap<String, GroupReorder> = HashMap::new();
for reorder in incoming {
    by_group.insert(reorder.group_id.clone(), reorder);
}

let mut query = String::from("BEGIN TRANSACTION;\n");
for reorder in by_group.values() {
    query.push_str(&format!(
        "UPDATE type::record('groups', '{}') SET display_order = {};\n",
        reorder.group_id, reorder.display_order,
    ));
}
query.push_str("COMMIT TRANSACTION;");
db.query(query).await?;
```

The dedup is defensive: if the same group appears twice in the incoming reorder (UI bug, race, whatever), the second one wins instead of producing two updates that both run.

```rust
// on_item_modified: collapse three conditional UPDATEs into one statement
// with conditional SETs. Mirrors append_batch's pattern but single-statement.
let query = "
    UPDATE type::record('items', $id)
    SET title = $title WHERE $title_changed
    SET description = $description WHERE $description_changed
    SET frequency = $frequency WHERE $frequency_changed
";
// (schematic — actual SurrealDB syntax for conditional SETs differs)
```

The `on_item_modified` fix had a side-effect I didn't expect: it closed a Cycle 1 regression. The original Cycle 1 fix --- "use the modified-fields list to skip unchanged updates" --- had only landed on `on_group_modified`. The `on_item_modified` handler had been left out of that fix. Triaging Warning #5 forced me to look at both handlers, and the regression became visible.

**Pattern worth highlighting: review triage is an opportunity to audit whether earlier 'fixes' actually shipped to all the places they should have.** A fix that only lands in one of two parallel handlers isn't really a fix --- it's a half-fix masquerading as a complete one. Looking for the symmetric site of an earlier fix is a cheap audit that tends to find real bugs.

**Regression tests added.** Three for the policy: a dedup test (same group reordered twice → only one update emitted), a combined-fields test (an item modification with all three fields changed → one statement, all three SETs), and a no-recognised-changes noop test (modification with only fields the handler doesn't track → zero queries).

#### Logic Critical #3: SyncBuffer drains before append

**The bug.** `SyncBuffer::do_flush` was draining its in-memory queue *before* calling `append_batch`. If `append_batch` failed --- network blip, database error, anything --- those events were already gone from the queue. Silently dropped. To make it worse, `flush_loop` was discarding the `Result` via `let _`, so there was no signal anywhere that events had been dropped.

**Already fixed.** The actual ordering bug had been fixed earlier in Cycle 2 (commit `c32c990`, in the "M2" milestone). What this Critical wanted from Session 6 was the **failure-path tests** that lock in the correct ordering. The fix had landed; the regression guard hadn't.

**The infrastructure refactor.** Writing failure-path tests required a mock that returns errors deterministically. The existing code had `Inner.store: SurrealEventStore` --- a concrete type. You can't make a concrete type fail on demand without poking at the database, which is fragile.

The fix: switch `Inner.store` to `Arc<dyn EventStore + Send + Sync>`. The trait was already `#[async_trait]` and was already being used in the dyn-style elsewhere (`llm/pipeline.rs` had been holding a `Box<dyn EventStore>` for months). One-line type change, plus `Arc::new(...)` at the production call site.

A new `ScriptedStore` mock with a pre-canned response queue and an optional `tokio::sync::Notify` gate let me write tests like:

```rust
#[tokio::test]
async fn flush_does_not_drain_on_append_error() {
    let store = ScriptedStore::new()
        .with_response(Err(EventStoreError::Disconnected))
        .build();

    let buffer = SyncBuffer::new(store.clone());
    buffer.push(some_event()).await;

    // First flush: append fails. Event should still be in the queue.
    let result = buffer.flush().await;
    assert!(result.is_err());
    assert_eq!(buffer.queue_len().await, 1);
}
```

Five new tests for `SyncBuffer` failure paths. All passing. Clippy clean. Tauri builds clean.

**Subagent experiment outcome --- worth sharing honestly.** I delegated the test-writing to a Sonnet 4.6 subagent. Sonnet produced a correct seam (the `Arc<dyn EventStore>` change), a correct mock (`ScriptedStore`), and 2 of 5 correct tests. The other 3 had runtime-semantics bugs:

- One test mis-counted `Notify` releases --- it assumed `notify_one` called twice would release two waiters, when in fact `Notify` coalesces.
- Two tests assumed `tokio::sync::broadcast::Receiver` ordering that the type doesn't guarantee under contention.

The tests passed sometimes. They hung sometimes. They flaked when run under load. The kind of bug that ships and then bites three weeks later when CI gets noisy.

**Lesson: don't hand test-writing to cheaper models without review.** Test code that looks right and runs once doesn't mean test code that's actually correct. Tests assert ordering and concurrency invariants that are exactly the kind of thing cheaper models handle worst. Either keep tests on Opus, or have Opus review the cheaper model's output before committing.

---

### Performance review: the auto-save derail

The performance review (Sonnet 4.6, 18 findings) produced the largest implementation work of Session 6 --- but not from a finding that started out looking large.

**Item 5** flagged `is_complete` as expensive. It byte-scans the whole journal text looking for the three reflection properties. The original disposition: "no action needed." `is_complete` is only called at journal-close time, which happens once per day. A byte-scan of a 5KB journal at end-of-day is not a performance problem.

Then I noticed something while writing up the disposition: Cycle 2 was about to add **auto-save**. That was scoped in `project.md` but the cross-track integration had never been tasked --- a planning miss from Session 4. With auto-save, `is_complete` stops being a once-a-day operation. Every keystroke on the journal would trigger a byte-scan of the entire journal text. At 60 keystrokes a minute on a long journal, that's a real cost.

The disposition flipped from "no action needed" to "fix." Item 5's fix landed in commit `ab7e50c` --- caching the scan result and invalidating the cache only when the relevant text region changes.

**Pattern worth highlighting: a review item's disposition is a function of *current* code paths. If you're about to add a new code path that touches the same code, re-evaluate.** Disposition is not a permanent label --- it's a snapshot of "given today's call sites, is this worth fixing?" New call sites can change the answer.

(Auto-save itself shipped during this triage. It's covered in [Part 1](./2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md). The summary: 1-second keystroke debounce, generation counter for cancel-on-newer-keystroke, `peek()` to avoid feedback loops, skip-if-stale `markClean` guards. Worked first try in walkthrough; I haven't yet exercised it under heavy use.)

A second thing surfaced during the auto-save work: an untracked release-build compile error. The Cycle 1 read-only editor fix had only landed on the debug `cfg` branch, not the production `cfg` branch. The production branch still calls `editor_options(journal_mode)` with one argument when the function now requires two. A compile error in the release build, invisible during development. Filed in `project_known_bugs.md` for Cycle 3.

**Pattern worth highlighting: fixes that branch on `cfg` need both branches updated, and CI should build both configurations.** This codebase doesn't yet have release-build CI; that's another Cycle 3 item.

---

### Bloat review: verifying the duplication claim

The bloat review (Sonnet 4.6, 9 findings) is where the calibration finding I mentioned at the top showed up.

**Finding #1.** "Three sites duplicate an 'append event then apply projection' pattern. Extract to a shared helper."

**Verification.** I greppped for the pattern. The actual count was 2, not 3. The third site the reviewer flagged was `import.rs`, which uses a batched `append_batch` path --- structurally different from the single-event path the other two sites use. Forcing them into a shared helper would have been a real refactor, not a clean extraction.

I extracted the real-N=2 pattern into `commands::shared::append_and_apply`. Commit `1dff52d`. The third site stayed as-is.

**Finding #2.** "This computation is duplicated in two places."

**Verification.** The two computations were similar but not the same. One computed `total / accepted` (for an import preview banner); the other computed `accepted / total` (for a different status line). Same numerator and denominator, different ratio. Not a duplicate.

What I did extract: the *count* of duplicates-found was being computed twice in the import preview path. Lifted that single computation up. Smaller change than the reviewer proposed, but a real improvement.

**The remaining 7 findings were dispositioned across the rest of the bloat review.** Three were straightforward extractions; two were deferred (single private callers, not worth abstracting yet); one was rejected (the reviewer wanted to merge two const arrays via a new dependency, when a `pub use` re-export from the same module did the same job with no dep change); one surfaced a calendar bug --- a 6×7 grid had been impulsively trimmed to 5×7 some commits earlier, which truncated months that span 6 calendar weeks. Restoring 6×7 fixed the visual bug.

**The general pattern.** Sonnet's bloat findings need a higher grep-tax than its other findings. The structure of a bloat finding makes it look the most concrete --- "these N files have this pattern" --- but the model is making a similarity judgement, and similarity is exactly the kind of judgement that's easy to get subtly wrong.

If the reviewer claims duplication, run the grep. If the count is right, look at the surrounding code to confirm the duplicate sites really are duplicates (same shape, same callers, same lifecycle). If they're not, decide whether to extract the real-N pattern or leave it alone. Don't refactor on a claim you haven't verified.

---

### Phase B: the test-gap audit, and the yield problem

Cycle 1 ran a test-gap audit and added 9 locked-in tests --- a real win. Cycle 2's audit produced 12 proposals. During triage, **9 of the 10 live proposals had already been superseded by inline regression tests added during the four reviews.**

The breakdown:

- Logic Critical #1 (Monthly clamp) added 3 tests during its fix.
- Logic Warning #4 (Custom frequency bound tightening) added 3 tests during its fix.
- Logic Warning #5 (transaction policy) added 3 tests during its fix.
- Security Medium #1 added 4 tests during its fix.

The test-gap audit had produced proposals for many of these scenarios. By the time I got to triaging the audit, those proposals were already shadowed by tests in the codebase.

**The one survivor.** A parser-strictness test for `Frequency::parse` --- specifically:

- Reject uppercase variants ("WEEKLY", "Weekly") to lock in case-sensitivity.
- Reject surrounding whitespace ("  weekly  ") to lock in trim-strictness.
- Reject leading whitespace on `custom:N` (" custom:7"), which would otherwise defeat the `starts_with("custom:")` guard.

Why this one survived: it's an **absence-of-behaviour test**. It asserts that the parser *should not* accept these inputs. None of the fix-driven tests would have produced this --- a fix-driven test asserts the bug is fixed, not that adjacent inputs are still rejected.

**The general insight: test-gap-last sequencing causes most regression-test demand to be absorbed by inline fix commits. The audit's residual value is catching absence-of-behaviour assertions --- tests that something should *not* be accepted, which fix-driven tests don't typically generate.**

This shifts how I'm planning to run the audit next cycle. The audit's primary output isn't "tests for things we just fixed" --- it's "tests for things the code rejects, that we'd notice if it ever stopped rejecting." A small, focused list of those is worth more than a long list that mostly duplicates fix-driven tests.

---

### Patterns that emerged across the four reviews

Four threads kept showing up across findings.

**Silent failures are the worst class of bug.** Logic Critical #1 (Monthly skipping months), Critical #2 (auto-close not firing), and Critical #3 (events silently dropped) all share a shape: the system fails to do something it should do, and produces no signal. The user finds out by independently noticing the absence. These bugs are also the hardest to catch in development because there's nothing to look at --- the failure is the absence of a thing happening. Reviews catch them disproportionately well because the reviewer is reading code with "what could go wrong here?" loaded.

**Triage as cross-section audit.** Three different findings led to discovering separate problems via the same mechanism: while loading a domain's invariants into my head to triage one finding, looking around surfaced an adjacent issue. Logic Critical #1 surfaced the Daily Flow visualizer's 7-day window assumption. Logic Warning #5 surfaced both a transaction-policy gap and a Cycle 1 regression in `on_item_modified`. Performance Item 5 surfaced the auto-save planning miss. The pattern: when you've paid the cost of loading a piece of the codebase into working memory, look around before you put it down.

**Disposition is not permanent.** Performance Item 5 flipped from "no action needed" to "fixed" because a new call site changed the cost calculus. Logic re-checks from Cycle 1 included one re-check that revealed a "PARTIAL FIX" annotation was understated --- the original fix had been a two-layer no-op (Rust embedded the wrong field; JS read the wrong field; CodeMirror happily accepted input). Dispositions are snapshots, not labels. New context can change them, and re-checks against earlier fixes are worth the time.

**Mixed-model strategy works with calibration.** Opus on logic and security; Sonnet on performance and bloat. The split saved real money. The calibration: bloat findings from Sonnet need the duplication claim verified by grep before refactoring. Once that grep-tax is paid, Sonnet's bloat output is good. Without it, you'll occasionally refactor on a claim that wasn't true.

---

### Numbers from Cycle 2

Across the four reviews and the test-gap audit:

| Disposition | Count |
|---|---|
| Fixed | ~22 |
| Documented (kept as-is, with rationale recorded) | ~5 |
| Deferred to Cycle 3 | ~6 |
| Rejected (reviewer claim was wrong on inspection) | ~2 |

Cycle 3 backlog items that came out of this review specifically:

- Daily Flow consistency visualizer needs a frequency-aware redesign (filed during Logic Critical #1 triage).
- `BufferEvent::FlushFailed` consumer wiring into a status reporter (so dropped-event signals reach the UI).
- Re-queue cap overshoot edge case in `SyncBuffer`.
- Release-build compile error on the editor's read-only fix branch (`editor.rs:179`).
- `auto_close_scheduler.rs::AppState.event_store` could move to `Arc<dyn EventStore>` for parity with the SyncBuffer refactor.
- Configurable `FORCE_GENERIC_DIRS` for the import path.
- Seconds duration unit (Phase 7.2 deferred from Cycle 2).
- Cycle 3 needs an explicit Planning session before implementation (Session 4 was implicit in Cycle 2; the auto-save planning miss is one of the costs).

---

### Running this process on your own project

If you want to adapt this:

1. **Pick four dimensions.** Security, performance, bloat, logical inconsistencies are a good default for a Rust backend. Frontends might substitute accessibility for one of these. Libraries might add API ergonomics.

2. **Document phase first, then triage phase.** Generate all four review documents before fixing anything. Don't let the model jump to fixes inside a review document --- ask only for findings with file/line citations. Anchoring on a fix obscures the underlying bug.

3. **Triage findings inline with fixing.** When you decide "fix," do the fix in that step, including the regression test. Don't batch fixes for a later session. The interaction between findings is information you only have during triage.

4. **Mix models.** Use the more capable model for reviews that require holding many invariants and judging causality (logic, security). Use the cheaper model for reviews that are closer to pattern matching (performance, bloat). Verify cheaper-model claims that have the structure "N sites do X" before refactoring.

5. **Sequence the test-gap audit last, but don't expect high yield from it.** Most regression-test demand will already be satisfied by inline fix commits. The audit's value is catching absence-of-behaviour assertions, which fix-driven tests don't typically generate. A short, focused audit with that framing produces more value than a long one trying to cover everything.

6. **Re-check earlier fixes.** Dispositions change as the code around them changes. A finding that was "no action needed" three months ago may not be true today. Cycle 2 found a Cycle 1 fix that was a two-layer no-op until the re-check.

7. **Review-as-audit, not just review-as-bug-finding.** Most of the highest-value moves in this cycle came from triage surfacing adjacent assumptions, not from the original finding itself. The transaction policy, the calendar bug restoration, the Cycle 1 regression in `on_item_modified` --- all of those came from the loaded context of triaging something else.

---

### Closing thoughts

The document-then-triage flow felt right. Generating the four documents in parallel up front gives me a complete picture before any fix decision. Walking through findings one at a time, with the fix landing inline, lets each decision inform the next. Cycle 1's batched-fix flow was workable; Cycle 2's interleaved flow was better.

The mixed-model strategy held up. The split saved real money on the volume-heavy reviews (performance, bloat) without sacrificing quality on the high-stakes ones (security, logic). The calibration finding --- Sonnet over-counts duplication in bloat reviews --- is a known cost I can plan around, not a reason to abandon the split.

The test-gap audit was a smaller win than Cycle 1 because the inline-fix flow had already absorbed most of the regression-test demand. That's a feature of the new flow, not a bug; the audit's residual value is genuine, just narrower than I'd assumed.

What I'm taking into Cycle 3: the explicit planning session that Cycle 2 skipped, the trip-wire findings filed above, and one process tweak --- I want to run a meta-review at the start of Cycle 3 looking at the four review documents from Cycles 1 and 2 side by side, to see which finding patterns recur. If certain shapes of bug keep showing up, that's a signal to add a hook earlier in the implementation flow rather than catching them in review.

[Part 1: Cycle 2 Implementation](./2026-04-26-cycle-2-implementation-calendar-obsidian-sync-and-auto-save.md) covers the feature work that this review was reviewing.
