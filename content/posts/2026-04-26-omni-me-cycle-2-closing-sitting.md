+++
title = "omni-me Cycle 2 — closing sitting"
slug = "omni-me-cycle-2-closing-sitting"
date = 2026-04-26
draft = true

[taxonomies]
tags = ["omni-me", "code-review", "rust", "chronicle"]
series = ["omni-me chronicle"]
+++

This is the first chronicle post for [omni-me](https://github.com/RustWright/omni-me), my Rust/Tauri/Dioxus personal-data app. It drops you at the end of Cycle 2 — earlier sittings of the cycle weren't chronicled, so the lead-up isn't here. For background on what a "cycle" is and how the project is structured, see the [project process doc](https://github.com/RustWright/omni-me/blob/main/PROJECT_PROCESS.md).

The closing sitting wrapped up the bloat review, triaged the test-gap audit, and surfaced one bug I'd nearly shipped.

## Bloat review — 9 findings, 7 commits

Each cycle ends with four code reviews — security, logic, performance, bloat — run in parallel using different models. Sonnet 4.6 ran the bloat review and flagged 9 candidates. Final disposition:

- **Extract — 1.** The "append event then apply projection" pattern that every backend command performs got lifted into one call: [`commands/shared.rs::append_and_apply`](https://github.com/RustWright/omni-me/blob/main/tauri-app/src-tauri/src/commands/shared.rs#L11). The reviewer claimed three duplicated sites; the real number was two.
- **Inline fix or rename — 4.** Lifted one duplicate computation, dropped a stale `last_sync_timestamp` shim, split the frontmatter-key list into schema-native vs Obsidian-reflection-property keys, and added a [`From<&Event> for NewEvent`](https://github.com/RustWright/omni-me/blob/main/core/src/events/store.rs#L43) conversion so callers stop hand-writing it.
- **Defer — 2.** Both were "extract this" suggestions for code with one private caller. Single-caller "abstractions" are usually noise.
- **Reject — 1.** A "duplicate counts" claim that turned out to be load-bearing. The frontend reads them, tests lock them in.
- **Surfaced something else entirely — 1.** The calendar bug below.

A carryover commit also cleaned three pre-existing `cargo clippy --all-targets` errors that `cargo check` had been letting through.

## The calendar truncation bug I almost shipped

The most embarrassing finding. While building the [month-grid calendar](https://github.com/RustWright/omni-me/blob/main/tauri-app/frontend/src/pages/journal.rs#L536) last week, I'd impulsively trimmed the grid from 6×7 (42 cells) to 5×7 (35 cells) on the logic that "31 days fit in 35 cells." The reviewer flagged the sixth row as bloat: "you have a row that's always empty."

It isn't. A month that starts on Saturday or Sunday and has 31 days doesn't fit in 35 cells — it needs the sixth row. February 2026 hides this, May 2026 hides this, but October 2026 starts on a Thursday with 31 days and ends in the sixth row. It would have been silently truncated.

The 6×7 grid is restored. The docstring on `build_month_cells` spells out why.

The shape of mistake worth flagging: when you "simplify" something based on the cases you happen to be looking at, name the cases you didn't check. The trim was wrong because I never enumerated months — I just looked at the current one. Three tests would have caught it: exhaustive month-length, Saturday-start-31-days, Sunday-start-31-days. None existed.

## Sonnet over-counted twice

Worth recording. Sonnet 4.6 was the bloat reviewer and it over-counted "duplicate sites" twice across the 9 findings.

The first claim said three sites duplicated the append-and-apply pattern; the third was structurally different — a batched path used only by the Obsidian-import flow, which calls a separate batch-write API. The second claim identified a different computation as a duplicate when it wasn't.

Both errors were caught by grepping the codebase before refactoring. Bloat reviews need a higher grep-tax than other tiers — claims about repetition look mechanical but are easy to get wrong, and the cost of acting on a false positive (extracting an "abstraction" with one real caller) is permanent.

## Test-gap audit — most of the work was already done

A separate pass at the end of each cycle checks what regression coverage is missing. It produced 12 proposals. Triaging each against the current codebase, only 1 of the 10 live proposals survived — the rest had been shadow-fulfilled by inline regression tests added during fix-cycle commits earlier in the session.

Rough breakdown of where the absorption happened: three new tests came with the monthly-frequency anchor clamp, three with the routine-reordering transaction policy, three with the custom-frequency bound tightening, and four with the mid-severity security fixes.

The one survivor is a parser-strictness test for [`Frequency::parse`](https://github.com/RustWright/omni-me/blob/main/core/src/routines.rs#L73) covering case sensitivity, surrounding whitespace, and leading whitespace on `custom:N` (which would defeat the `starts_with("custom:")` guard). It's an absence-of-behavior assertion — none of the fix-cycle commits would have produced it naturally.

Insight worth keeping: when the test-gap audit runs *after* fix cycles, most of the gap demand is absorbed by inline tests in the fix commits. The audit's residual value is catching what fix-driven tests don't generate — assertions that something should *not* be accepted.

## Queued for the next cycle

Cycle 2 had a Planning session at the start, and most of what landed went through it cleanly. What surfaced mid-cycle and didn't, queued for Cycle 3's Planning to triage:

- **Daily Flow consistency visualizer.** The per-routine progress bar on the home screen hard-codes a 7-day window. That was fine in Cycle 1 when every routine was daily. Cycle 2 added Weekly, Biweekly, Monthly, and Custom-N frequencies. The visualizer still computes "7-day completion %" for routines that fire monthly — frontend↔backend contract drift.
- **Auto-save status reporting.** Auto-save shipped in Cycle 2. The buffer-flush pipeline emits a [`BufferEvent::FlushFailed`](https://github.com/RustWright/omni-me/blob/main/core/src/sync/buffer.rs#L50) signal on errors but no consumer listens for it yet — surfacing failures in the UI status bar is the next step.
- **Configurable directory generation** — currently hard-coded; should be a setting.
- **Seconds duration unit** — was on the Cycle 2 task list but deferred.

Pattern across these: each is a cross-track integration item (one feature affects another). The shape matches the auto-save wiring, which was scoped during Cycle 2's Planning but never made it into a task. Cycle 3's Planning could try an explicit cross-track check: for each new feature, ask "what existing feature does this make wrong?"
