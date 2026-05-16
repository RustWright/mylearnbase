+++
title = "From Shell to Ship: UI, Features, and Android"
slug = "from-shell-to-ship-ui-features-and-android"
aliases = ["/posts/from-shell-to-ship-ui-features-and-android/"]
date = 2026-04-11
draft = false

[taxonomies]
tags = ["rust", "dioxus", "tauri", "codemirror", "android", "wasm", "claude-code", "mobile-development", "ui"]
series = ["Building omni-me"]

[extra]
series_order = 4
+++

## Reflections

I'm writing this shortly after the reflection for the [companion post](@/posts/archive/2026-03-30-event-sourcing-sync-and-llm-pipeline.md), so I'll try not to repeat myself. What I do want to call out is how it felt to have a working MVP on my phone. I'd already built an app during the POC phase and verified it ran, but this was different — something buggy but *operational*, able to create notes, edit them, manage tasks, and sync it all between my phone and laptop. A very vague idea I've had for a long time is starting to feel real and achievable.

I still have a long way to go before I'd actually switch from my current Obsidian journaling habit to this. But over the next couple of months, I should be able to add the features I care about and polish them enough to feel comfortable making the switch. I was ambitious when defining the full scope, but ultimately there are three bare minimum things I need before I'd be happy switching over:

1. **Note-taking parity with Obsidian** — autosave and auto-sync, so I can start and stop across devices without thinking about it.
2. **A proper task/routine manager** — so I can stop tracking my to-do items in raw journal entries.
3. **A budgeting workflow** — I've tried several times to maintain a visible, well-documented budget and never managed to stick with it. I'm hoping that by the time this app is done, that'll no longer be true.

That said, moving this quickly makes me suspect there are hidden issues lurking in the codebase. My next two sessions will likely focus on a full audit to surface potential problems early, before the project grows and they get harder to fix. I'm not sure I'll write a post about that — unless I find something major that forces a significant change.

The other thing I need to figure out is a workable UI/UX workflow — one that won't make me prefer pulling out my teeth. I'll probably dedicate a whole session to researching what's already out there. Once I land on a decent UI and the app starts to look more polished, it'll feel all the more real. And more importantly, if I don't think carefully about how I'll interact with the app day-to-day, I'm more likely to get frustrated with myself later. If I do find a good UI/UX workflow, I can use it to improve mylearnbase as well.

I also can't end a reflection without touching on the broader question of understanding codebases that are written and managed with LLM help. I've been thinking about codebase visualization — tools that show how functions relate to each other, how data structures flow through the program, which functions process what data and where they're defined, or logic flow diagrams for key operations. Something like that has to already exist, and if it doesn't, how hard would it be to build for myself?

For any major project I'm working on, I'd love to have a single page dedicated to these kinds of visualizations. It's becoming clear that once I have a workable version of omni-me, there's a lot of work to do on mylearnbase — quizzes, visualizations, and whatever else I come up with — all working together toward the same goal: keeping me in the loop on the things I'm building with LLM assistance.

---

## Tutorial: Building the Visible Product — Dioxus UI, Journal, Routines, and Android Deployment

The [first post](@/posts/archive/2026-03-08-validating-a-rust-mobile-app-stack.md) in this series validated the technology stack. The [second post](@/posts/archive/2026-03-27-building-the-foundation-rust-workspace-and-infrastructure.md) built the infrastructure: workspace, database layer, server, and CI/CD. The [companion post](@/posts/archive/2026-03-30-event-sourcing-sync-and-llm-pipeline.md) covers the event sourcing engine, sync protocol, and LLM pipeline that sit underneath everything described here.

This post covers Phases 4 through 7 — the part where the project goes from a headless backend to something you can actually tap on. Four phases, completed across several working sessions:

1. **UI Shell + CodeMirror** — Dioxus app layout, tab navigation, CodeMirror 6 integration
2. **Journal/Notes** — creation, editing, search, LLM-powered analysis
3. **Routine Manager** — groups, items, daily checklist, completion history
4. **Integration + Polish** — tracing, sync wiring, settings screen, Android APK build

By the end, all 38 tasks from the cycle 1 task list are complete. The app runs on desktop and Android, with a full sync loop verified between devices over Tailscale.

### Assumptions

- **Previous posts:** You have read the [second post](@/posts/archive/2026-03-27-building-the-foundation-rust-workspace-and-infrastructure.md) and [companion post](@/posts/archive/2026-03-30-event-sourcing-sync-and-llm-pipeline.md) or are at least familiar with the workspace structure, SurrealDB schema, event store, and sync protocol.
- **Operating system:** Linux (Ubuntu, kernel 6.8, x86_64). macOS works for desktop; Android builds require the NDK.
- **Tooling:** Rust 1.85+, `wasm32-unknown-unknown` target, Dioxus CLI 0.7+, Tauri CLI 2.10+, Node.js 18+ (for CodeMirror bundling).
- **Android (Phase 7 only):** Java 17, Android SDK platform 35+, build-tools 35.0.1, NDK r28. See the [first post](@/posts/archive/2026-03-08-validating-a-rust-mobile-app-stack.md) for setup details.

---

### Phase 4: UI Shell + CodeMirror

This phase creates the app's visual skeleton — a tabbed layout with a rich text editor embedded inside.

#### Dioxus App Shell

The app uses a simple `Tab` enum to track which screen is visible. The `App` component renders a flex column that fills the viewport: a scrollable content area on top and a fixed bottom navigation bar.

```rust
#[derive(Clone, Copy, PartialEq)]
pub enum Tab {
    Journal,
    Routines,
    Settings,
}

#[component]
fn App() -> Element {
    let mut active_tab = use_signal(|| Tab::Journal);

    rsx! {
        div {
            style: "
                display: flex;
                flex-direction: column;
                height: 100vh;
                width: 100vw;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
                color: #1a1a2e;
                overflow: hidden;
            ",

            // Content area — scrollable
            div {
                style: "flex: 1; overflow-y: auto; padding: 16px; padding-bottom: 64px;",
                match *active_tab.read() {
                    Tab::Journal => rsx! { JournalPage {} },
                    Tab::Routines => rsx! { RoutinesPage {} },
                    Tab::Settings => rsx! { SettingsPage {} },
                }
            }

            // Bottom nav — fixed at bottom
            BottomNav {
                active: *active_tab.read(),
                on_switch: move |tab: Tab| {
                    active_tab.set(tab);
                },
            }
        }
    }
}
```

The layout is deliberately mobile-first: full viewport height, no margins, `overflow: hidden` on the root to prevent double scrollbars. The `padding-bottom: 64px` on the content area prevents content from being obscured by the fixed bottom nav.

The `BottomNav` component takes the current `Tab` and an `EventHandler<Tab>` for switching. Each tab button computes its own style based on whether it is active:

```rust
#[component]
pub fn BottomNav(active: Tab, on_switch: EventHandler<Tab>) -> Element {
    let tab_style = |tab: Tab| -> String {
        let is_active = active == tab;
        let bg = if is_active { "#16213e" } else { "transparent" };
        let color = if is_active { "#e94560" } else { "#8892a4" };
        let font_weight = if is_active { "600" } else { "400" };

        format!(
            "flex: 1; display: flex; align-items: center; justify-content: center;
             min-height: 48px; padding: 8px 0; border: none; background: {bg};
             color: {color}; font-size: 14px; font-weight: {font_weight};
             cursor: pointer; border-radius: 8px; transition: background 0.15s, color 0.15s;
             -webkit-tap-highlight-color: transparent;"
        )
    };

    rsx! {
        nav {
            style: "display: flex; align-items: center; gap: 4px; padding: 4px 8px;
                    background: #1a1a2e; border-top: 1px solid #16213e;
                    position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;",

            button {
                style: "{tab_style(Tab::Journal)}",
                onclick: move |_| on_switch.call(Tab::Journal),
                "Journal"
            }
            button {
                style: "{tab_style(Tab::Routines)}",
                onclick: move |_| on_switch.call(Tab::Routines),
                "Routines"
            }
            button {
                style: "{tab_style(Tab::Settings)}",
                onclick: move |_| on_switch.call(Tab::Settings),
                "Settings"
            }
        }
    }
}
```

The `-webkit-tap-highlight-color: transparent` is a mobile-specific detail — without it, Android WebView adds a blue flash on every button tap.

#### CodeMirror 6 Bundle + IPC Bridge

CodeMirror 6 is a JavaScript text editor. Dioxus compiles to WASM. Both run inside the same Tauri WebView. This is the key architectural insight for this phase: **Dioxus WASM and CodeMirror JS communicate via direct JavaScript interop, not Tauri IPC.** They share the same `window` object, the same DOM, and the same JavaScript runtime. Tauri IPC (`window.__TAURI__.core.invoke`) is only used for calls from the frontend to the Rust backend — never for editor communication.

The CodeMirror bundle is built with esbuild from a small entry point:

```javascript
import { EditorView, minimalSetup } from "codemirror";
import { markdown } from "@codemirror/lang-markdown";
import { EditorState } from "@codemirror/state";

let editorView = null;

window.createEditor = function (elementId, initialContent, onChange) {
  if (editorView) {
    editorView.destroy();
    editorView = null;
  }

  const parent = document.getElementById(elementId);
  if (!parent) {
    console.error("Editor container not found:", elementId);
    return;
  }

  const extensions = [minimalSetup, markdown(), EditorView.lineWrapping];

  if (typeof onChange === "function") {
    extensions.push(
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          const content = update.state.doc.toString();
          onChange(content);
        }
      })
    );
  }

  editorView = new EditorView({
    state: EditorState.create({
      doc: initialContent || "",
      extensions,
    }),
    parent,
  });
};

window.getEditorContent = function () {
  if (!editorView) return "";
  return editorView.state.doc.toString();
};

window.setEditorContent = function (content) {
  if (!editorView) return;
  editorView.dispatch({
    changes: { from: 0, to: editorView.state.doc.length, insert: content },
  });
};

window.destroyEditor = function () {
  if (editorView) {
    editorView.destroy();
    editorView = null;
  }
};
```

Four functions are exposed on `window`: `createEditor`, `getEditorContent`, `setEditorContent`, and `destroyEditor`. The `EditorView.lineWrapping` extension was added later in Phase 7 after testing on mobile — without it, long lines scroll horizontally, which is unusable on a phone. Line numbers were removed for the same reason (they waste horizontal space on narrow screens).

The bundle is produced with:

```bash
npx esbuild assets/js/editor.js --bundle --outfile=assets/js/editor.bundle.js --format=iife
```

#### IPC Bridge: Tauri + CodeMirror

The Dioxus frontend needs two kinds of foreign function interface: Tauri IPC for backend commands, and direct JS calls for the editor. Both are declared in a single bridge module using `wasm_bindgen`:

```rust
use wasm_bindgen::prelude::*;

// Tauri IPC — calls into the Rust backend
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = ["window", "__TAURI__", "core"], js_name = invoke)]
    pub fn tauri_invoke(cmd: &str, args: JsValue) -> js_sys::Promise;
}

// CodeMirror interop — calls into the JS editor (same WebView)
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_name = createEditor)]
    pub fn js_create_editor(
        element_id: &str,
        initial_content: &str,
        on_change: Option<&js_sys::Function>,
    );

    #[wasm_bindgen(js_name = getEditorContent)]
    pub fn js_get_editor_content() -> String;

    #[wasm_bindgen(js_name = setEditorContent)]
    pub fn js_set_editor_content(content: &str);

    #[wasm_bindgen(js_name = destroyEditor)]
    pub fn js_destroy_editor();
}
```

The Tauri bindings use `js_namespace` to reach `window.__TAURI__.core.invoke`. The CodeMirror bindings use `js_name` to reach the global functions defined in the bundle. Both resolve at runtime in the same WebView context.

On top of the raw `tauri_invoke` binding, a pair of typed helper functions handle serialization and deserialization:

```rust
async fn invoke<T: serde::de::DeserializeOwned>(
    cmd: &str,
    args: &impl serde::Serialize,
) -> Result<T, String> {
    let args_js =
        serde_wasm_bindgen::to_value(args).map_err(|e| format!("serialize args: {e}"))?;
    let promise = tauri_invoke(cmd, args_js);
    let result = wasm_bindgen_futures::JsFuture::from(promise)
        .await
        .map_err(|e| format!("{e:?}"))?;
    serde_wasm_bindgen::from_value(result).map_err(|e| format!("deserialize result: {e}"))
}

async fn invoke_unit(cmd: &str, args: &impl serde::Serialize) -> Result<(), String> {
    let args_js =
        serde_wasm_bindgen::to_value(args).map_err(|e| format!("serialize args: {e}"))?;
    let promise = tauri_invoke(cmd, args_js);
    wasm_bindgen_futures::JsFuture::from(promise)
        .await
        .map_err(|e| format!("{e:?}"))?;
    Ok(())
}
```

Every Tauri command gets a typed wrapper. For example, note creation:

```rust
pub async fn invoke_create_note(raw_text: &str, date: &str) -> Result<NoteListItem, String> {
    #[derive(serde::Serialize)]
    struct Args<'a> {
        raw_text: &'a str,
        date: &'a str,
    }
    invoke("create_note", &Args { raw_text, date }).await
}
```

The inline `Args` struct pattern keeps the serialization contract local to each function, avoiding a shared args module that would couple unrelated commands together.

#### Editor Dioxus Wrapper

The `Editor` component wraps CodeMirror in a Dioxus-friendly interface with `initial_content`, `on_change`, and `read_only` props:

```rust
#[component]
pub fn Editor(
    initial_content: String,
    on_change: EventHandler<String>,
    #[props(default = false)] read_only: bool,
) -> Element {
    let mut editor_ready = use_signal(|| false);

    use_effect(move || {
        let initial = initial_content.clone();

        spawn(async move {
            let window = web_sys::window().expect("no window");
            let document = window.document().expect("no document");

            // Create <script> element for the editor bundle
            let script = document
                .create_element("script")
                .expect("failed to create script element");
            script
                .set_attribute("src", "/assets/js/editor.bundle.js")
                .expect("failed to set script src");

            // Wait for the script to load via a Promise
            let promise = js_sys::Promise::new(&mut |resolve, _reject| {
                let resolve_clone = resolve.clone();
                let onload = Closure::once_into_js(move || {
                    resolve_clone.call0(&JsValue::NULL).unwrap();
                });
                script
                    .dyn_ref::<web_sys::HtmlElement>()
                    .expect("script is not HtmlElement")
                    .set_onload(Some(onload.unchecked_ref()));
            });

            let body = document.body().expect("no body");
            body.append_child(&script).expect("failed to append script");

            wasm_bindgen_futures::JsFuture::from(promise)
                .await
                .expect("script load failed");

            // Create a JS callback for onChange
            let on_change_closure = Closure::wrap(Box::new(move |content: String| {
                on_change.call(content);
            }) as Box<dyn Fn(String)>);

            let on_change_fn = on_change_closure
                .as_ref()
                .dyn_ref::<js_sys::Function>()
                .expect("closure is not a Function")
                .clone();

            // Leak the closure so it stays alive for the editor's lifetime.
            // Cleanup happens via destroyEditor().
            on_change_closure.forget();

            js_create_editor(EDITOR_CONTAINER_ID, &initial, Some(&on_change_fn));
            editor_ready.set(true);
        });
    });

    use_drop(move || {
        js_destroy_editor();
    });

    rsx! {
        div {
            style: "width: 100%; min-height: 300px; border: 1px solid #ddd;
                    border-radius: 8px; overflow: hidden; background: #fff;",

            if !*editor_ready.read() {
                div {
                    style: "padding: 16px; color: #888; font-size: 14px;",
                    "Loading editor..."
                }
            }

            div { id: EDITOR_CONTAINER_ID, style: "width: 100%; min-height: 300px;" }
        }
    }
}
```

A few things worth noting about this component:

- The script is loaded dynamically inside `use_effect` rather than in the HTML template. This ensures the editor bundle is only loaded when the component mounts, not on every page load.
- `Closure::wrap` creates a Rust-to-JS callback for the `onChange` handler. The `.forget()` call intentionally leaks the closure — it needs to stay alive for the entire lifetime of the editor, and cleanup happens in `use_drop` when `destroyEditor()` removes the listener.
- The `editor_ready` signal gates the "Loading editor..." placeholder. Until the script loads and `createEditor` finishes, the user sees a loading state instead of an empty box.

---

### Phase 5: Journal/Notes

With the shell and editor in place, the journal feature connects them to the event-sourced backend.

#### Note Creation Flow

The flow is: user taps "+ New Note" -> `JournalView` switches to `NewNote` -> `Editor` component mounts -> user types -> taps "Save" -> `invoke_create_note` sends the text to the Tauri backend -> backend appends a `NoteCreated` event -> projection updates the notes table -> list refreshes.

The `JournalView` enum drives all navigation within the journal tab:

```rust
#[derive(Clone, PartialEq)]
enum JournalView {
    List,
    NewNote,
    EditNote(String),
    Search,
}
```

The page component uses this enum with pattern matching to render the appropriate sub-view:

```rust
#[component]
pub fn JournalPage() -> Element {
    let mut view = use_signal(|| JournalView::List);
    let mut notes = use_signal(Vec::<NoteListItem>::new);
    let mut error_msg = use_signal(|| None::<String>);

    let _load = use_future(move || async move {
        match bridge::invoke_list_notes().await {
            Ok(list) => notes.set(list),
            Err(e) => error_msg.set(Some(e)),
        }
    });

    let refresh_notes = move || {
        spawn(async move {
            match bridge::invoke_list_notes().await {
                Ok(list) => { notes.set(list); error_msg.set(None); }
                Err(e) => error_msg.set(Some(e)),
            }
        });
    };

    rsx! {
        div {
            style: "max-width: 720px; margin: 0 auto;",
            match &*view.read() {
                JournalView::List => rsx! {
                    NoteListView {
                        notes: notes.read().clone(),
                        on_new: move |_| view.set(JournalView::NewNote),
                        on_edit: move |id: String| view.set(JournalView::EditNote(id)),
                        on_search: move |_| view.set(JournalView::Search),
                    }
                },
                JournalView::NewNote => rsx! {
                    NoteEditorView {
                        note_id: None,
                        initial_content: String::new(),
                        on_save: move |_| { view.set(JournalView::List); refresh_notes(); },
                        on_cancel: move |_| view.set(JournalView::List),
                    }
                },
                // ... EditNote and Search views follow the same pattern
            }
        }
    }
}
```

On the backend, `create_note` generates a ULID, appends a `NoteCreated` event, runs the event through projections, then queries the projection table to return the created note:

```rust
#[tauri::command(rename_all = "snake_case")]
pub async fn create_note(
    state: State<'_, AppState>,
    raw_text: String,
    date: String,
) -> Result<NoteRow, String> {
    tracing::info!(date = %date, len = raw_text.len(), "create_note");
    let note_id = ulid::Ulid::new().to_string();

    let event = NewEvent {
        id: None,
        event_type: EventType::NoteCreated.to_string(),
        aggregate_id: note_id.clone(),
        timestamp: Utc::now(),
        device_id: state.device_id.clone(),
        payload: serde_json::json!({
            "raw_text": raw_text,
            "date": date,
        }),
    };

    let event = state.event_store.append(event).await.map_err(|e| e.to_string())?;
    state.projections.apply_events(&[event]).await.map_err(|e| e.to_string())?;

    queries::get_note(&state.db, &note_id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Note created but not found in projection".to_string())
}
```

The pattern of "append event, apply to projections, query projection" repeats across every write command in the app. The [companion post](@/posts/archive/2026-03-30-event-sourcing-sync-and-llm-pipeline.md) explains why this design was chosen.

#### Note Editing

Editing uses the same `NoteEditorView` component as creation, but with `note_id: Some(id)` and `initial_content` populated from the existing note. The save handler detects whether this is a new note or an update:

```rust
let result = if let Some(id) = note_id {
    bridge::invoke_update_note(&id, &text).await
} else {
    let today = chrono::Utc::now().format("%Y-%m-%d").to_string();
    bridge::invoke_create_note(&text, &today).await.map(|_| ())
};
```

#### Note List View

Notes are grouped by date: Today, Yesterday, and Older. The grouping function compares each note's `date` field against the current UTC date:

```rust
fn render_grouped_notes(notes: &[NoteListItem], on_edit: EventHandler<String>) -> Element {
    let today = chrono::Utc::now().format("%Y-%m-%d").to_string();
    let yesterday = (chrono::Utc::now() - chrono::Duration::days(1))
        .format("%Y-%m-%d")
        .to_string();

    let mut today_notes = vec![];
    let mut yesterday_notes = vec![];
    let mut older_notes = vec![];

    for note in notes {
        if note.date == today {
            today_notes.push(note.clone());
        } else if note.date == yesterday {
            yesterday_notes.push(note.clone());
        } else {
            older_notes.push(note.clone());
        }
    }

    rsx! {
        if !today_notes.is_empty() {
            NoteGroup { label: "Today".to_string(), notes: today_notes, on_edit }
        }
        if !yesterday_notes.is_empty() {
            NoteGroup { label: "Yesterday".to_string(), notes: yesterday_notes, on_edit }
        }
        if !older_notes.is_empty() {
            NoteGroup { label: "Older".to_string(), notes: older_notes, on_edit }
        }
    }
}
```

Each `NoteCard` shows the first 80 characters as a preview, plus tags and mood if the note has been LLM-processed.

#### LLM Trigger

The "Process with AI" button appears only on saved notes (not during creation). It sends the note content to the server for LLM processing:

```rust
if !is_new {
    button {
        style: "padding: 8px 12px; background: #6b5b95; color: white; border: none;
                border-radius: 6px; cursor: pointer; font-size: 14px;",
        disabled: *processing.read(),
        onclick: {
            let nid = note_id_for_llm.clone();
            move |_| {
                let nid = nid.clone();
                processing.set(true);
                llm_error.set(None);
                spawn(async move {
                    if let Some(id) = nid {
                        match bridge::invoke_process_note_llm(&id).await {
                            Ok(result) => llm_result.set(Some(result)),
                            Err(e) => llm_error.set(Some(e)),
                        }
                    }
                    processing.set(false);
                });
            }
        },
        if *processing.read() { "Processing..." } else { "Process with AI" }
    }
}
```

The server handles all LLM communication (Gemini Flash via tool calling), extracts tags, mood, tasks, dates, and expenses, then returns the structured result. The `LlmResultsDisplay` component renders each category with appropriate styling. All LLM calls go through the server — the Tauri client never talks to Gemini directly. This is a deliberate architectural decision explained in the [companion post](@/posts/archive/2026-03-30-event-sourcing-sync-and-llm-pipeline.md).

#### Search

Search uses substring matching on the backend. The design decision for empty queries was intentional: an empty query returns blank results rather than showing all notes. The frontend enforces this before even making the call:

```rust
on_query_change: move |q: String| {
    search_query.set(q.clone());
    if q.trim().is_empty() {
        search_results.set(vec![]);
    } else {
        spawn(async move {
            if let Ok(results) = bridge::invoke_search_notes(&q).await {
                search_results.set(results);
            }
        });
    }
},
```

The backend has the same guard:

```rust
#[tauri::command(rename_all = "snake_case")]
pub async fn search_notes(
    state: State<'_, AppState>,
    query: String,
) -> Result<Vec<NoteRow>, String> {
    if query.trim().is_empty() {
        return Ok(vec![]);
    }
    queries::search_notes(&state.db, &query).await.map_err(|e| e.to_string())
}
```

---

### Phase 6: Routine Manager

The routine system is the second major feature module. It uses the same event-sourced backend pattern as notes but introduces a more complex data model: groups contain items, and items have daily completions.

#### Group CRUD

A routine group has a name, frequency (daily/weekly/custom), and time of day (morning/afternoon/evening). The `RoutineView` enum manages navigation:

```rust
#[derive(Clone, PartialEq)]
enum RoutineView {
    DailyChecklist,
    GroupList,
    GroupDetail(String),
    AddGroup,
    EditGroup(String),
}
```

The default view is `DailyChecklist` — what you see when you tap the Routines tab. The "Manage" button takes you to `GroupList`, where you can add, view, or edit groups.

Creating a group uses a form with text input for the name and dropdowns for frequency and time of day. The `AddGroupView` component validates that the name is non-empty before enabling the save button:

```rust
button {
    style: "padding: 8px 16px; background: #4a6fa5; color: white; ...",
    disabled: *saving.read() || name.read().trim().is_empty(),
    onclick: move |_| {
        saving.set(true);
        spawn(async move {
            let n = name.read().clone();
            let f = frequency.read().clone();
            let t = time_of_day.read().clone();
            match bridge::invoke_create_routine_group(&n, &f, &t).await {
                Ok(_) => on_save.call(()),
                Err(e) => save_error.set(Some(e)),
            }
            saving.set(false);
        });
    },
    if *saving.read() { "Saving..." } else { "Save" }
}
```

#### Item Management

Items belong to groups. Each item has a name, estimated duration in minutes, and an order number. The `GroupDetailView` shows a group's items with an inline form for adding new ones:

```rust
div {
    style: "margin-top: 12px; display: flex; gap: 8px; align-items: center;",
    input {
        style: "flex: 1; padding: 8px 10px; border: 1px solid #ddd; ...",
        r#type: "text",
        placeholder: "New item name",
        value: "{new_item_name}",
        oninput: move |e| new_item_name.set(e.value()),
    }
    input {
        style: "width: 50px; padding: 8px 6px; ...",
        r#type: "number",
        placeholder: "min",
        value: "{new_item_duration}",
        oninput: move |e| new_item_duration.set(e.value()),
    }
    button {
        disabled: *adding.read() || new_item_name.read().trim().is_empty(),
        onclick: { /* invoke_add_routine_item */ },
        "Add"
    }
}
```

The order is automatically assigned based on the current item count, keeping items in insertion order.

#### Daily Checklist

The daily checklist is the main view of the Routines tab. It groups routines by time of day (Morning, Afternoon, Evening) and shows each group's items as a checklist:

```rust
for tod in &["morning", "afternoon", "evening"] {
    {
        let tod_groups: Vec<_> = groups.iter()
            .filter(|g| g.time_of_day == *tod)
            .cloned()
            .collect();
        if !tod_groups.is_empty() {
            let label = match *tod {
                "morning" => "Morning",
                "afternoon" => "Afternoon",
                _ => "Evening",
            };
            rsx! {
                div {
                    style: "margin-bottom: 20px;",
                    h3 { style: "font-size: 13px; font-weight: 600; color: #888;
                          text-transform: uppercase;", "{label}" }
                    for group in tod_groups {
                        ChecklistGroup { group, date: today.clone() }
                    }
                }
            }
        }
    }
}
```

Each `ChecklistGroup` loads its items and today's completions, then renders three states per item:

- **Not done** — an empty checkbox button and a "Skip" button
- **Completed** — green checkmark, text struck through
- **Skipped** — gray dash, dimmed text

The progress indicator shows `done_count/total` in the group header:

```rust
let done_count = items_read.iter()
    .filter(|item| completions_read.iter().any(|c| c.item_id == item.id))
    .count();
let total = items_read.len();

// In the header:
span { style: "font-size: 13px; color: #888;", "{done_count}/{total}" }
```

Daily reset is implicit — there is no cron job or scheduled task. The checklist queries completions filtered by today's date. When the date changes, the query returns no completions for the new day, and all items appear unchecked. Completion events from previous days remain in the event store and are visible in the history view.

Completions are tracked by appending `RoutineItemCompleted` or `RoutineItemSkipped` events. Each completion event carries the item ID, group ID, and date:

```rust
#[tauri::command(rename_all = "snake_case")]
pub async fn complete_routine_item(
    state: State<'_, AppState>,
    item_id: String,
    group_id: String,
    date: String,
) -> Result<(), String> {
    let event = NewEvent {
        id: None,
        event_type: EventType::RoutineItemCompleted.to_string(),
        aggregate_id: ulid::Ulid::new().to_string(),
        timestamp: Utc::now(),
        device_id: state.device_id.clone(),
        payload: serde_json::json!({
            "item_id": item_id,
            "group_id": group_id,
            "date": date,
            "completed_at": Utc::now().to_rfc3339(),
        }),
    };

    let event = state.event_store.append(event).await.map_err(|e| e.to_string())?;
    state.projections.apply_events(&[event]).await.map_err(|e| e.to_string())?;
    Ok(())
}
```

#### Editing Groups

The `EditGroupView` component loads the current group's properties and sends a `modify_routine_group` command with a JSON `changes` object:

```rust
let changes = serde_json::json!({
    "name": *name.read(),
    "frequency": *frequency.read(),
    "time_of_day": *time_of_day.read(),
});
bridge::invoke_modify_routine_group(&gid, &changes, None).await;
```

This emits a `RoutineGroupModified` event with the changes payload. The projection handler applies the diff to the group record.

#### History

The `GroupDetailView` includes a 7-day history grid that provides a visual summary of completion status. It builds a grid with items as rows and the last 7 days as columns:

```rust
#[component]
fn HistoryGrid(items: Vec<RoutineItem>, history: Vec<CompletionEntry>) -> Element {
    let today = chrono::Utc::now().date_naive();
    let days: Vec<String> = (0..7)
        .rev()
        .map(|i| (today - chrono::Duration::days(i)).format("%Y-%m-%d").to_string())
        .collect();

    // For each item and day, look up the completion
    for item in &items {
        for day in &days {
            let completion = history.iter().find(|c| c.item_id == item.id && c.date == *day);
            let (bg, label) = match completion {
                Some(c) if c.skipped => ("#e0e0e0", "\u{2014}"),
                Some(_) => ("#4caf50", "\u{2713}"),
                None => ("#f5f5f5", ""),
            };
            // render colored cell
        }
    }
}
```

Green cells for completed, gray for skipped, light background for not done. The grid uses CSS Grid with `grid-template-columns: 120px repeat(7, 1fr)` to align the item name column with the day columns.

---

### Phase 7: Integration + Polish

The final phase ties everything together, fixes rough edges, and gets the app running on Android.

#### Tracing

The Tauri app initializes `tracing-subscriber` with environment-based filtering at startup:

```rust
pub fn run() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "omni_me_app=debug".into()),
        )
        .init();

    tauri::Builder::default()
        .setup(|app| {
            // ...
        })
```

Every command logs at least its entry point. Write commands use `tracing::info!` with structured fields:

```rust
tracing::info!(date = %date, len = raw_text.len(), "create_note");
```

Read commands use `tracing::debug!` to reduce noise. Failures log at `tracing::warn!`. This made debugging sync issues significantly easier — you can see exactly which events are being appended and applied.

#### Editor Fixes

Two CodeMirror adjustments were made after mobile testing:

1. **`EditorView.lineWrapping` added** — without this, long lines overflow horizontally and require side-scrolling, which is impractical on a phone.
2. **`lineNumbers` removed** — on a 360px-wide mobile screen, line numbers consume valuable horizontal space for no real benefit in a note-taking context.

These are single-line changes in the extensions array:

```javascript
const extensions = [minimalSetup, markdown(), EditorView.lineWrapping];
```

#### Sync Wiring

The `trigger_sync` command creates a `SyncClient`, runs the sync protocol (pull then push), and then applies pulled events through projections:

```rust
#[tauri::command(rename_all = "snake_case")]
pub async fn trigger_sync(state: State<'_, AppState>) -> Result<SyncStatus, String> {
    let server_url = state.server_url.read().await.clone();
    let client = SyncClient::new(server_url, state.device_id.clone());

    let result = client.sync(&state.db).await.map_err(|e| e.to_string())?;

    // Apply pulled events through projections so they become visible in the UI
    if !result.pulled_events.is_empty() {
        tracing::info!(pulled = result.pulled, "applying pulled events to projections");
        state.projections.apply_events(&result.pulled_events).await.map_err(|e| {
            tracing::warn!(error = %e, "projection apply after sync failed");
            e.to_string()
        })?;
    }

    Ok(SyncStatus { pulled: result.pulled, pushed: result.pushed })
}
```

The critical detail here is `apply_events`, not `init_all`. When events are pulled from the server, they need to be processed incrementally through the projection handlers — not by replaying the entire event store. Using `init_all` after a sync would re-read every event from the beginning, which is wasteful and can cause duplicate projection entries if the projection handlers are not idempotent for all event types.

#### Settings Screen

The settings page shows device ID (read-only), server URL (editable), and a "Sync Now" button:

```rust
#[component]
pub fn SettingsPage() -> Element {
    let mut server_url = use_signal(|| String::new());
    let mut device_id = use_signal(|| String::new());
    let mut sync_status = use_signal(|| None::<String>);

    use_future(move || async move {
        if let Ok(info) = bridge::invoke_get_sync_info().await {
            server_url.set(info.server_url);
            device_id.set(info.device_id);
        }
    });

    // ...
}
```

The device ID is generated once (ULID) and persisted to a file in the app data directory. The server URL defaults to `http://localhost:3000` and can be changed to point at a remote server. Both values are loaded at startup via a `load_or_create` helper:

```rust
fn load_or_create(app_data: &Path, filename: &str, default_fn: impl FnOnce() -> String) -> String {
    let path = app_data.join(filename);
    if let Ok(val) = std::fs::read_to_string(&path) {
        let val = val.trim().to_string();
        if !val.is_empty() {
            return val;
        }
    }
    let val = default_fn();
    let _ = std::fs::write(&path, &val);
    val
}
```

The database is stored in the OS app data directory (`~/.local/share/com.omni-me.app/` on Linux) rather than inside `src-tauri/`. This prevents Tauri's file watcher from triggering infinite rebuild loops when SurrealKV writes its LOCK and WAL files during development.

#### Android APK Build

Building for Android uses:

```bash
cargo tauri android build --debug
```

Two gotchas surfaced during Android builds:

**Absolute `frontendDist` path.** Tauri's Android build process resolves the frontend assets path differently than the desktop build. A relative path like `../frontend/dist` works on desktop but fails silently on Android — the APK gets built but loads a blank screen because no assets are included. The fix is an absolute path in `tauri.conf.json`.

**Disk space.** A full Rust build targeting multiple architectures (desktop x86_64, WASM, plus all four Android ABIs) consumes enormous amounts of disk. On a 115GB drive, this filled the disk and caused cryptic build failures. The solution is to target only the architecture you need:

```bash
cargo tauri android build --debug --target aarch64
```

This builds for ARM64 only (which covers the vast majority of modern Android phones) and avoids building for armv7, x86, and x86_64.

A third issue: **surrealdb-core compilation is extremely memory-intensive**. With parallel Rust builds on a machine with less than 8GB of RAM, the compiler can OOM during surrealdb-core's macro expansion. Limiting parallelism with `CARGO_BUILD_JOBS=2` or building with `--jobs 2` avoids this.

#### Tailscale Sync

For phone-to-desktop sync testing, Tailscale provides a mesh VPN that makes both devices accessible to each other on a private network. The Android phone points its server URL at the desktop's Tailscale IP, and sync works over the encrypted tunnel without exposing any ports to the public internet. No auth is needed on the sync endpoints because the network itself is trusted — this is acceptable for a single-user app behind Tailscale but is explicitly flagged as a Cycle 2 item to address before any multi-user or public deployment.

#### SurrealKV Stability Bug

A stability issue was discovered during extended testing: SurrealKV panics with a "commit queue overflow" error after approximately 24 hours of continuous server uptime. When this happens, the database connection becomes corrupted — the server continues returning HTTP 200 responses, but all write operations silently fail. The push handler in the sync endpoint was swallowing this error, making it look like events were being accepted when they were actually being dropped.

This is logged as a known issue for Cycle 2 investigation. The workaround is restarting the server periodically or before any important sync operations.

---

### Gotchas

1. **Dioxus and CodeMirror share the same WebView.** They communicate via direct JS interop (`wasm_bindgen` extern bindings to `window` functions), not Tauri IPC. This is a common source of confusion — Tauri IPC is only for frontend-to-backend communication.

2. **`frontendDist` must be an absolute path for Android builds.** Relative paths work on desktop but produce blank-screen APKs on Android. No error is shown during the build.

3. **Multi-target Rust builds consume disk rapidly.** Building for desktop, WASM, and all four Android architectures on a small drive will fill it. Target a single Android architecture with `--target aarch64`.

4. **surrealdb-core can OOM during compilation on machines with less than 8GB RAM.** Limit build parallelism with `CARGO_BUILD_JOBS=2`.

5. **Pulled events must go through `apply_events`, not `init_all`.** After a sync pull, the new events need to be processed incrementally by the projection handlers. Calling `init_all` replays the entire event store, which is wasteful and can cause issues with non-idempotent projections.

6. **SurrealKV panics with "commit queue overflow" after extended uptime (~24h).** The database connection silently breaks — writes fail but the server keeps running. The push handler was swallowing this error. Restart the server as a workaround.

---

### What's Next

Cycle 1 is complete. All 38 tasks across 7 phases are done. The app runs on desktop and Android, with a verified sync loop between devices over Tailscale.

The Cycle 2 backlog includes:

- **Auth on sync endpoints** — currently deferred because the app runs behind Tailscale, but required before any broader deployment.
- **UI testing workflow** — screenshot-based testing proved painful during Cycle 1. Needs research into better approaches for testing Dioxus WASM UIs.
- **Delete and edit for routine items** — groups can be edited but individual items cannot be deleted or reordered yet.
- **SurrealKV stability** — the commit queue overflow issue needs root-cause analysis. May require upgrading SurrealDB, switching storage backends, or adding connection health checks.
