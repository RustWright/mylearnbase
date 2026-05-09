+++
title = "Cycle 2 Implementation: Calendar, Templates, Obsidian Sync, and Auto-Save"
slug = "cycle-2-implementation-calendar-obsidian-sync-and-auto-save"
date = 2026-04-26
draft = true

[taxonomies]
tags = ["rust", "dioxus", "codemirror", "obsidian", "calendar", "tauri", "claude-code", "omni-me"]
series = ["Building omni-me"]

[extra]
series_order = 6
+++

## Reflections

<!-- This section is written by the human author — replace this with your thoughts -->

---

## Tutorial: Building Cycle 2 of omni-me

Cycle 1 produced a working personal-data app: event sourcing on SurrealDB, sync between devices, an LLM pipeline through Gemini, and a barebones UI. The four code reviews that closed Cycle 1 caught the rough edges. Cycle 2 was about taking the app from "compiles and runs" to "I would actually use this every day." That meant a calendar, a real journal flow, full bidirectional sync with my existing Obsidian vault, polished routines, and --- the piece that grew well beyond its original scope --- auto-save on every text surface.

This post covers the implementation work of Cycle 2: Session 5 in my project process, plus the auto-save piece that chronologically shipped during Session 6 but is structurally implementation. The code review that produced its own findings is covered in [Part 2: Cycle 2 Code Review](./2026-04-26-cycle-2-four-perspective-review.md).

### Assumptions

This post continues the omni-me series. If you have not read the earlier posts, the short version is: a Rust workspace with `core`, `server`, `tauri-app/src-tauri`, and `frontend` (a Dioxus crate compiled to `wasm32-unknown-unknown`), backed by SurrealDB, with CodeMirror 6 wired into Dioxus through direct JS interop in the same WebView (no Tauri IPC for editor state).

- **Primary OS:** Linux (Ubuntu, kernel 6.8, x86_64). All commands and paths in this post assume that.
- **Rust toolchain:** `rustup` with the `wasm32-unknown-unknown` target for Dioxus web/PWA, plus `aarch64-linux-android` for Android. Stable channel is fine.
- **Tauri / Dioxus / SurrealDB:** Tauri CLI v2.10.1, dioxus-cli 0.7.2, SurrealDB CLI installed locally.
- **Obsidian vault layout:** I use `YYYY-MM-DD-note.md` for daily notes. The import code recognises that and several variants.

> **macOS note:** the toolchain is identical. Replace `apt install` with `brew install` for system packages. Android NDK lives at `~/Library/Android/sdk/ndk/...` rather than `~/android-sdk/ndk/...`. Tauri's macOS desktop target works without any extra setup.

> **Windows note:** WSL2 is strongly recommended for the Rust + Tauri + Android workflow. Native Windows works for the desktop Tauri target, but Android cross-compilation is fragile. SurrealKV's embedded storage works fine under WSL2.

> **Disk usage warning:** Cycle 2 used parallel git worktrees, each with its own `target/` directory. Three worktrees built simultaneously consumed about 17GB. Keep an eye on free space, or thin the targets between sessions.

---

### Phase 0: Wiping Cycle 1 dev events

Before any new feature work, I needed a clean slate. Cycle 1 left scattered test events in the local SurrealKV file: half-formed routines, journal entries with placeholder dates, LLM processing results from earlier prompt versions. Carrying that into Cycle 2 would have made it impossible to tell whether weird behaviour came from new code or old data.

The interesting question for an event-sourced system is: **how do you reset state in an append-only store?**

The honest answer is: you do not "reset" the store. You delete the data file. The event log is the source of truth, and projections are derived from it. There is no schema migration, no "soft delete" event type, no compensating events. You blow away the database file, the next launch finds nothing, and the projections rebuild themselves from an empty event log.

```bash
# stop any running tauri / dx serve processes first
rm -rf ~/.local/share/omni-me/db.surrealkv/
```

The path is wherever the Tauri app's data directory points. On Linux this is `~/.local/share/<app-id>/`, on macOS it is `~/Library/Application Support/<app-id>/`, on Windows it is `%APPDATA%\<app-id>\`.

This is the operational benefit of event sourcing showing up in everyday workflow: there is exactly one place that holds canonical state, and resetting is a single rm. No migrations to revert, no foreign key cleanup, no projection-by-projection truncation.

Commit `1031e23`. After this, the parallel push could begin from a known-empty state.

---

### Phases 1, 2, 3: Three parallel worktree subagents

The next three phases were independent enough to parallelise. The plan from Session 4 had them on conflict-free file boundaries:

- **Phase 1** — events / sync improvements (touched `core/src/events/`, `core/src/sync/`)
- **Phase 2** — LLM pipeline upgrades (touched `core/src/llm/`)
- **Phase 3** — Notes UI infrastructure (touched `frontend/src/pages/notes/`)

I ran each phase as its own Claude Code worktree subagent on Opus 4.7. The mechanics looked roughly like this:

```bash
# in the omni-me repo root
git worktree add ../omni-me-phase1 main
git worktree add ../omni-me-phase2 main
git worktree add ../omni-me-phase3 main

# launch each in its own terminal with claude code
# (one Opus 4.7 agent per worktree, scoped to its phase brief)
```

Each worktree is a full repo clone with its own `target/` directory. That is what bought the parallelism: Cargo's build cache is per-target-dir, so three concurrent `cargo check` runs on the same workspace would normally fight over the lock file. Worktrees sidestep that.

The phases merged back into main as commits `48b3981`, `a0e407b`, and `8b80ea4`. Test count rose to 116 passing.

#### What three parallel Opus agents actually cost

This is the kind of thing I want to be honest about, because it informs when I would do it again.

- **Money:** roughly $40 in extra subscription usage on top of my normal monthly burn. Three agents holding context on a multi-crate Rust codebase with a lot of cross-file reads is expensive even when each agent is well-scoped.
- **Disk:** about 17GB of working copies plus build artifacts across the three worktrees. With Rust's per-target directory, each new worktree pays the full `target/` cost on first build.
- **Cognitive load:** I had to keep three subagents oriented and merge their work in a sensible order. The merges themselves were clean (the file boundaries held), but I was reading three plans simultaneously.

It paid off here because the three phases were genuinely independent and each was at least a couple of hours of real work. For routine feature work where dependencies between modules are unclear, or where each piece is short, sequential is cheaper and clearer. My default after this experiment is **sequential on a single mid-tier model unless I have an explicit reason to parallelise**.

---

### Phase 4: Calendar and Day view

After the parallel push, work moved back to single-threaded development on main. This is where the user-facing Cycle 2 features actually start showing up.

The Calendar page is a month grid: 7 columns (one per weekday) and 6 rows of cells. The Day view is what opens when you click a date: a CodeMirror editor pre-loaded with that date's journal entry, or an empty one if no journal exists yet.

#### Why 6 rows, not 5

A month always fits in at most 6 weeks of a Sunday-to-Saturday grid. Most months only need 5, but some need 6: a 31-day month that starts on Saturday or Sunday spills into the sixth row. If you only render 5 rows (35 cells), those months get truncated.

I caught this the boring way: I impulsively shrank the grid to 5 rows to "save vertical space" and a reviewer flagged the truncation later. The fix was to put the rationale in the docstring so future-me does not optimise it away again.

#### `build_month_cells` (Learn-by-Doing)

I wrote this function myself rather than letting the model produce it. The shape is simple --- 42 cells, each marked as in-month or out-of-month --- but the wrap-around arithmetic is the kind of thing I want to know I can do.

```rust
// schematic; the real version lives in `frontend/src/pages/calendar/`
use chrono::{Datelike, Duration, NaiveDate, Weekday};

pub struct CalendarCell {
    pub date: NaiveDate,
    pub in_current_month: bool,
}

/// Returns 42 cells (6 rows x 7 cols) for the month containing `anchor`.
/// The first cell is the Sunday on or before the 1st of the month.
pub fn build_month_cells(anchor: NaiveDate) -> Vec<CalendarCell> {
    let first_of_month = anchor.with_day(1).expect("day 1 always valid");
    let weekday = first_of_month.weekday();
    // distance from Sunday, 0..=6
    let offset = weekday.num_days_from_sunday() as i64;
    let grid_start = first_of_month - Duration::days(offset);

    let target_month = anchor.month();
    (0..42)
        .map(|i| {
            let date = grid_start + Duration::days(i);
            CalendarCell {
                date,
                in_current_month: date.month() == target_month,
            }
        })
        .collect()
}
```

The render layer just iterates 42 cells, applies the `in_current_month` flag for styling, and lays them out with `grid-cols-7`. The grid is row-agnostic in CSS terms --- 42 cells in a 7-column grid always wraps to 6 rows --- so changing the row count requires no CSS update.

Test cases worth pinning down:

- A month that starts on Sunday (the first cell is the 1st, no leading days from the previous month).
- A month that starts on Saturday with 31 days (needs the full 6th row).
- February in a non-leap year (28 days, 5 rows used, 6th row is all next-month).
- February in a leap year (29 days, behaviour identical).

#### Day view wiring

Clicking a calendar cell pushes a route like `/day/2026-04-26`. The Day view component reads the date from the route, looks up the corresponding journal note (if any) via the notes projection, and hands that content to a CodeMirror instance.

The first version threw away the template if the user clicked Save without typing. That is the kind of behaviour you do not catch without exercising it, and it pointed at a CodeMirror integration pattern I had to learn the hard way --- covered in the next section.

Commit `957a4ce`.

---

### Phase 5: Journal templates and Obsidian import/export

This was the heaviest single phase. Three things in one: a journal template engine, an importer that reads an Obsidian vault and turns it into events, and an exporter that writes the projection back out as Obsidian-compatible markdown.

#### 5.1 — Journal template engine

`journal_template::render(date)` produces the starting content for a new journal entry: a YAML frontmatter fence with the date, a tags list, three reflection-property keys, and an H2 prompt header.

```rust
// schematic
pub fn render(date: chrono::NaiveDate) -> String {
    format!(
        "---\n\
         date: {date}\n\
         tags: [daily_note]\n\
         homework_for_life: \n\
         grateful_for: \n\
         learnt_today: \n\
         ---\n\
         \n\
         ## What happened today?\n\
         \n",
        date = date.format("%Y-%m-%d"),
    )
}
```

I wrote the template body myself --- it is the kind of thing that benefits from sitting with the format I will actually use every day, rather than accepting whatever the model produces.

One small detail: the original version emitted `tags` as a YAML block list (`- daily_note` on its own line). That looks fine in isolation but interacted badly with the projection that scans frontmatter for completion-state keys --- I changed it to inline `tags: [daily_note]` after a code review finding. Part 2 of this series goes into the parser interaction; for the implementation tutorial here, the takeaway is that the inline form is what shipped.

#### The CodeMirror priming subtlety

CodeMirror 6 does not fire `on_change` when its `initial_content` is loaded. That sounds obvious in retrospect, but it caused a real failure mode in the first version of the Day view.

The flow:

1. User clicks a calendar date with no existing journal.
2. Day view renders. It computes `journal_template::render(date)` and passes it as `initial_content` to the CodeMirror component.
3. CodeMirror displays the template.
4. User clicks Save without typing.
5. The Save handler reads from the `content` signal, which was never written because no `on_change` fired.
6. The save is empty. Template lost.

The fix is to prime the signal at the same time as `initial_content`:

```rust
// schematic — inside the DayView component
let initial = use_memo(move || journal_template::render(date()));
let content = use_signal(|| initial.read().clone());

// Pass *both* to CodeMirror:
//   - initial_content: what the editor displays on mount
//   - content: the signal the editor writes back to via on_change
rsx! {
    CodeMirrorEditor {
        initial_content: initial.read().clone(),
        content: content,
        on_change: move |new_text| {
            content.set(new_text);
        },
    }
}
```

When the user types, `on_change` overwrites `content` with the real text. When they do not type, `content` already holds the template. Either way, Save reads the right value.

This is a recurring pattern with CodeMirror integrations --- any time the editor is initialised with non-empty content that you later need to act on, prime the signal at construction time. Otherwise you have a hidden invariant: "this signal is only correct after the user has typed at least once."

#### 5.2 to 5.8 and 7.1 — Obsidian import and export

I keep my actual life data in an Obsidian vault. The whole point of omni-me is to replace that, eventually --- but only if it can read what I already have and write back out compatibly so I can keep using Obsidian as a fallback or alternative editor.

##### Backend layout

A new `core::import` module, with four submodules each owning one concern:

```text
core/src/import/
├── mod.rs
├── parser.rs       // splits frontmatter from body, parses YAML
├── walker.rs       // recursively walks vault directories
├── mapper.rs       // turns parsed files into NewEvent records
└── classifier.rs   // decides Journal vs Note from filename + frontmatter
```

A new dependency: `serde_yml` for YAML parsing. I picked it over `serde_yaml` because the latter is unmaintained as of this writing and `serde_yml` is a maintained fork with the same API surface.

The parser splits on the first `---` fence pair:

```rust
// schematic
pub struct ParsedFile {
    pub frontmatter: Option<serde_yml::Value>,
    pub body: String,
}

pub fn split_frontmatter_and_body(text: &str) -> ParsedFile {
    // If the file does not start with `---\n`, the whole file is body.
    let Some(rest) = text.strip_prefix("---\n") else {
        return ParsedFile { frontmatter: None, body: text.to_string() };
    };
    // Find the closing `\n---\n` (or `\n---` at EOF).
    if let Some(end) = rest.find("\n---") {
        let yaml = &rest[..end];
        let body_start = end + "\n---".len();
        let body = rest[body_start..]
            .strip_prefix('\n')
            .unwrap_or(&rest[body_start..])
            .to_string();
        let frontmatter = serde_yml::from_str(yaml).ok();
        return ParsedFile { frontmatter, body };
    }
    // No closing fence — treat as plain body.
    ParsedFile { frontmatter: None, body: text.to_string() }
}
```

##### `parse_date_prefix` for daily-note filenames

My vault names daily notes `2026-04-26-note.md`. I have seen other conventions: `2026-04-26.md`, `2026-04-26 note.md`, `2026-04-26_note.md`. The classifier needs to recognise all of them as Journal entries.

```rust
// schematic
pub fn parse_date_prefix(filename: &str) -> Option<chrono::NaiveDate> {
    // Strip the .md suffix
    let stem = filename.strip_suffix(".md")?;

    // The first 10 chars must be YYYY-MM-DD
    if stem.len() < 10 {
        return None;
    }
    let date_part = &stem[..10];
    let date = chrono::NaiveDate::parse_from_str(date_part, "%Y-%m-%d").ok()?;

    // After the date, allow either end-of-string or one of `-`, `_`, ` `
    let rest = &stem[10..];
    if rest.is_empty()
        || rest.starts_with('-')
        || rest.starts_with('_')
        || rest.starts_with(' ')
    {
        Some(date)
    } else {
        None
    }
}
```

The classifier uses this as the first signal for "is this a journal entry?". Frontmatter `tags: [daily_note]` is a secondary signal --- if either matches, the file becomes a Journal.

##### Tauri commands

Three commands across the import/export boundary:

- `preview_import(vault_path)` — walks the vault, parses every `.md` file, returns counts (total, accepted, rejected) plus a per-file disposition list. Nothing is written. The frontend uses this to show the user what will happen before they confirm.
- `commit_import(vault_path, ...)` — re-reads the vault and appends events. The re-read is deliberate: the preview's parsed structures could be hours old by the time the user confirms, and re-reading is cheap.
- `export_obsidian(vault_path)` — writes journals as `YYYY-MM-DD.md` (canonical form) and notes as slugified filenames into the chosen vault directory.

```rust
// schematic — tauri-app/src-tauri/src/commands/import_export.rs
#[tauri::command]
pub async fn preview_import(
    state: tauri::State<'_, AppState>,
    vault_path: String,
) -> Result<ImportPreview, String> {
    let path = std::path::PathBuf::from(vault_path);
    let report = core::import::preview(&path).map_err(|e| e.to_string())?;
    Ok(ImportPreview {
        total: report.total,
        accepted: report.accepted,
        rejected: report.rejected,
        files: report.dispositions,
    })
}
```

##### Frontend flow

Settings page, above the Danger Zone, two flows: `ImportFlow` and `ExportFlow`.

```text
frontend/src/pages/import_export/
├── mod.rs
├── import_flow.rs   // pick directory -> preview -> confirm -> commit
└── export_flow.rs   // pick directory -> confirm -> write
```

The import flow is a small state machine: idle → previewing → ready-to-commit → committing → done. Each transition is driven by a Tauri command response.

#### Clippy in the verification flow

Phase 5 is also when I started running `cargo clippy --all-targets` alongside `cargo check` and `cargo test` after every meaningful change. The workspace went from 19 warnings to 0 over this phase.

What worked: bucketing each warning into one of three actions.

- **Apply:** the obvious cases. Use `let-else` instead of nested `match`, drop a redundant `clone`, replace `.unwrap_or_else(|| Vec::new())` with `.unwrap_or_default()`. Just fix it.
- **Dead-code-apply:** clippy points at something that is genuinely unused (a leftover helper from a deleted feature). Remove it rather than `#[allow]`-ing it.
- **Deliberate idiom, allow with comment:** rare, but happens. Some patterns trip clippy by design --- for instance, a single-element loop you keep because the iterator interface clarifies intent, or a `_` pattern that documents an explicit ignore. `#[allow(clippy::lint_name)]` with a one-line comment explaining why.

What I avoided: `cargo clippy --fix --allow-dirty`. Blanket auto-fix is fine for trivial style lints but it can rewrite code in ways that change subtle semantics (especially around lifetimes and `into()` vs `from()` choices). Reviewing each warning is slower but does not generate spooky diffs.

Five commits across Phase 5: `e5a3515`, `e338cc5`, `e347ba4`, `4951b8a`, `22395f8`.

---

### Phase 6: Tier 2 routine UX

The routines feature already worked at the end of Cycle 1, but using it daily exposed friction that needed real polish. Phase 6 ran in three sittings.

#### Sitting A — data wipe and remove buttons

Two pragmatic items:

- A "wipe all routines" path in Settings (separate from the journal/notes data wipe — different aggregate, different confirmation).
- Per-routine remove buttons that emit a `routine_group_removed` event. The projection handler tombstones the row rather than deleting, so the event log stays consistent.

#### Sitting B — item edit form, duration picker, custom-N frequency

The item edit form is what made the feature feel real. Before this, modifying a routine meant deleting it and re-creating it, which lost completion history. After this, you edit name/duration/frequency in place and a `routine_item_modified` event records exactly what changed.

The duration picker has a small but interesting helper: how do you display "90 minutes" to the user? "90m" is unambiguous. "1h 30m" reads better but only if it is exact. "1h 33m" for 93 minutes is fine but "1h" for 60 minutes vs "60m" for 60 minutes is a styling choice. I went with the **exact-divisor policy**: show the hour-form only when the value divides cleanly into hours-plus-minutes, otherwise stay in minutes.

```rust
// schematic — frontend/src/components/duration.rs
pub fn split_minutes_for_display(total_minutes: u32) -> (u32, u32) {
    // Returns (hours, minutes) for display. If the value doesn't split
    // cleanly we still produce hours/minutes, but the *caller* decides
    // whether to render "Xh Ym" or just "Nm" based on whether the input
    // was an exact multiple — see the `Display` impl below.
    let hours = total_minutes / 60;
    let minutes = total_minutes % 60;
    (hours, minutes)
}

pub fn format_duration(total_minutes: u32) -> String {
    let (h, m) = split_minutes_for_display(total_minutes);
    if h == 0 {
        format!("{m}m")
    } else if m == 0 {
        format!("{h}h")
    } else {
        format!("{h}h {m}m")
    }
}
```

I wrote `split_minutes_for_display` myself. The function looks trivial, but the policy decision (exact-divisor vs always-split) is the kind of micro-design choice that I want to internalise rather than delegate.

The custom-N frequency parser handles the case where neither "daily" nor "weekly" fits --- a routine you do every 3 days, every 5 days, every 10 days. The frontend renders a small numeric input that produces `Frequency::Custom(N)`, and the parser accepts strings like `custom:5`. The valid range is `[2, 31]`: anything above 31 days is not really habit-shaped and belongs in a future calendar-task feature instead.

#### Sitting C — drag-to-reorder on Daily Flow

The Daily Flow page lists today's routines in display order. Reordering by drag-and-drop is the kind of UX that feels obvious until you write the insertion logic.

The asymmetric semantic worth calling out: **dropping above a group inserts before it; dropping below inserts after.** That matches the visual mental model --- you push the existing element away in the direction you came from. It also avoids the "off-by-one" feeling where dropping at index N and getting index N+1 feels broken.

```rust
// schematic — frontend/src/pages/daily_flow/reorder.rs
pub fn reorder_groups_after_drop(
    groups: &[GroupId],
    dragged: GroupId,
    target: GroupId,
    drop_position: DropPosition, // Above | Below
) -> Vec<GroupId> {
    // Remove the dragged item from its current position
    let without_dragged: Vec<GroupId> = groups
        .iter()
        .filter(|g| **g != dragged)
        .copied()
        .collect();

    let target_idx = without_dragged
        .iter()
        .position(|g| *g == target)
        .expect("target must be in groups");

    let insert_idx = match drop_position {
        DropPosition::Above => target_idx,        // before target
        DropPosition::Below => target_idx + 1,    // after target
    };

    let mut result = without_dragged;
    result.insert(insert_idx, dragged);
    result
}
```

I wrote `reorder_groups_after_drop` myself. The asymmetry is the whole insight: removing the dragged element first means `target_idx` already accounts for whatever shift would otherwise need a fudge factor. Above = target_idx, below = target_idx + 1. No special case for "dragged was originally above target, so subtract one." The remove-then-insert framing dissolves it.

The drop-position itself is computed in the JS layer from the cursor's Y position relative to the target row's vertical midpoint. That gets passed to Dioxus via a custom event, the Rust side runs `reorder_groups_after_drop`, and emits a `routine_group_reordered` event. The projection handler updates the `display_order` field on each affected row.

Sub-tasks 6.1 to 6.5 and 6.7 to 6.9 landed in this phase. Task 6.6 (undo complete/skip) was already implemented in an earlier sitting.

Commit `3e4076a`.

---

### Phase 7.3: Notes search clear button

A small UX improvement worth covering as a clean example of progressive enhancement on a Dioxus form.

The Notes page has a search input. Cycle 1 had a working filter but no way to clear the query other than backspacing. Cycle 2 added an X button that clears the input when clicked, plus an Escape-to-clear keyboard shortcut.

Two design choices that made it feel polished:

- The X **only renders when the query is non-empty**. An empty input has no clutter.
- The X sits **inside the input's right padding** (`pr-10` in Tailwind), absolutely positioned, so it does not overlap with the typed text.

```rust
// schematic — frontend/src/pages/notes/search.rs
let mut query = use_signal(String::new);

rsx! {
    div { class: "relative",
        input {
            class: "w-full pl-3 pr-10 py-2 ...",
            r#type: "text",
            placeholder: "Search notes...",
            value: "{query}",
            oninput: move |evt| query.set(evt.value()),
            onkeydown: move |evt| {
                if evt.key() == Key::Escape {
                    query.set(String::new());
                }
            },
        }
        if !query.read().is_empty() {
            button {
                class: "absolute right-2 top-1/2 -translate-y-1/2 \
                        text-gray-400 hover:text-gray-600",
                onclick: move |_| query.set(String::new()),
                "X"
            }
        }
    }
}
```

The conditional render is the point: progressive enhancement means the X exists when it has a job to do and disappears when it does not. Compare to a perpetually-rendered button with `disabled={query.is_empty()}` --- functional, but visually noisier.

---

### Auto-save (the unscoped piece)

This is the largest single behavioural change in late Cycle 2, and it shipped during Session 6 rather than Session 5. Structurally it is implementation work, so it belongs here.

#### How it ended up in this phase

Cycle 2's plan included "debounced auto-save" as a scoped item, but the cross-track integration was never tasked. I had a `tasks.md:72` comment to myself --- "future auto-save wiring" --- which is the kind of thing past-self does that present-self has to clean up. The performance review surfaced it as item 5, and I decided to ship it inline rather than defer to Cycle 3.

#### The pattern

The shared piece lives in `frontend/src/timer.rs`:

```rust
// schematic
pub const AUTOSAVE_DEBOUNCE_MS: u32 = 1000;

pub async fn sleep_ms(ms: u32) {
    // wasm-bindgen-futures based timer; details depend on the runtime
    gloo_timers::future::TimeoutFuture::new(ms).await;
}
```

The debounce + cancel logic lives at each integration site (journal, notes), but the shape is identical:

```rust
// schematic — inside the journal Day view
let content = use_signal(String::new);
let last_saved_content = use_signal(String::new);
let save_generation = use_signal(0u64);

use_effect(move || {
    // Read content reactively — this effect re-runs on every keystroke.
    let current = content.read().clone();

    // peek() avoids creating a reactive dependency on last_saved_content.
    // If we used .read() here, every save would update last_saved_content,
    // which would re-trigger this effect, which would save again ... feedback loop.
    if current == last_saved_content.peek().clone() {
        return;
    }

    // Bump the generation counter. Older in-flight saves see they're stale
    // and bail before writing.
    let mut gen = save_generation.write();
    *gen += 1;
    let my_gen = *gen;
    drop(gen);

    spawn(async move {
        sleep_ms(AUTOSAVE_DEBOUNCE_MS).await;

        // If a newer keystroke fired during our sleep, abort.
        if *save_generation.peek() != my_gen {
            return;
        }

        // Re-read current content at save time — it may have moved on
        // even within the debounce window.
        let to_save = content.peek().clone();
        match save_journal(date, &to_save).await {
            Ok(_) => {
                last_saved_content.set(to_save.clone());
                // Tell CodeMirror this content is "clean" — but only if
                // it still matches what's in the editor. Otherwise we'd
                // mark dirty content as clean.
                mark_clean_if_matches(&to_save);
            }
            Err(e) => {
                tracing::warn!("autosave failed: {e}");
            }
        }
    });
});
```

Three details that took me a while to get right:

1. **`peek()` versus `read()` on `last_saved_content`.** `read()` establishes a reactive dependency. If I `read()` it inside the effect, then writing to it after a successful save (`last_saved_content.set(...)`) re-fires the effect, which compares again, sees equality, returns --- but the re-fire still costs a render and made my dev tools spam. `peek()` reads without subscribing. That breaks the feedback loop cleanly.

2. **Generation counter for cancellation.** Without it, every keystroke spawns a future that sleeps then saves. If you type 10 characters in quick succession, you get 10 saves --- one per keystroke after their respective debounce windows. With the counter, only the latest one survives.

3. **The `markClean` skip-if-stale guard.** CodeMirror tracks "is the document clean (matches last saved state)?" via `markClean()`. After a successful save, you want to mark the editor clean so the close-tab-without-saving warning behaves correctly. But if the user typed during the save round-trip, the editor's current content is no longer what got saved, and calling `markClean()` would lie. The guard checks that the editor's current content still matches what was saved before marking.

#### Two integration paths

**Journal (commit `9bb9e3c`) --- option (i):** auto-save handles both the create and the update for a given date. If no journal exists for `2026-04-26` yet, the first auto-save creates it; subsequent auto-saves update it. The journal aggregate is keyed by date, so there is no separate "id capture" step.

**Notes (commit `a93d2a4`) --- option (ii):** manual create on first save, auto-update afterward. Notes get a fresh ULID at creation time, and the create-vs-update split is meaningful (you do not want two notes from the same draft session). I capture `local_note_id` in a signal at create time and use that for subsequent updates.

```rust
// schematic — notes auto-save
let local_note_id = use_signal(|| None::<String>);

let on_save = move |content: String| async move {
    if let Some(id) = local_note_id.peek().clone() {
        update_note(&id, &content).await
    } else {
        let id = create_note(&content).await?;
        local_note_id.set(Some(id.clone()));
        Ok(())
    }
};
```

That capture step also fixed a pre-existing duplicate-create bug. Without `local_note_id`, every re-fire of the create effect inserted a second row for the same draft session. Capturing the id at first save and reading it on subsequent saves makes the second-fire a no-op for create and a normal update for the existing row.

#### What I did and did not verify

I ran `cargo check`, `cargo clippy`, and walked through the code paths carefully. I did **not** run `dx serve` and exercise the auto-save manually before merging. I accepted that risk explicitly --- the next phase of Cycle 3 is daily use, which will exercise auto-save constantly, and any runtime bugs surface fast under that load.

This is a real trade-off worth naming. Skipping the live exercise saved an hour or so of fiddling. If auto-save had a runtime hang, I would lose more than that recovering from it. I made the call because the static checks passed and the patterns were ones I had implemented before in similar shape. I would not skip the live test for the first auto-save in a new codebase.

Commits across the auto-save sub-phase: `185548f`, `c9af143`, `9bb9e3c`, `a93d2a4`, `ab7e50c`, `d4e81ac`, `9a55ab5`. Parent submodule sync: `12e9b9f`.

---

### What's next

This was the implementation half of Cycle 2. [Part 2: Cycle 2 Code Review](./2026-04-26-cycle-2-four-perspective-review.md) covers the Session 6 four-perspective review of everything described here --- security, performance, bloat, and logical consistency, the same lens framework I used at the end of Cycle 1.

After that, Cycle 3. The plan is to start with an explicit Session 4 (Planning) before any implementation, to avoid the "scoped but never tasked" trap that auto-save fell into during Cycle 2. The Cycle 3 backlog already has a few items waiting: a frequency-aware redesign of the Daily Flow consistency visualiser (which still assumes a 7-day window even though Cycle 2 added Weekly, Biweekly, Monthly, and Custom frequencies), a release-build compile error in `editor.rs`, and a few smaller architectural cleanups.

The day-to-day goal for Cycle 3 is more boring and more important than any of that: actually use omni-me as my primary journal and routine tracker, in place of Obsidian, and let real use surface the next round of issues.
