+++
title = "Validating a Rust Mobile App Stack: Tauri + Dioxus + SurrealDB + CodeMirror"
slug = "validating-a-rust-mobile-app-stack"
date = 2026-03-08
draft = false

[taxonomies]
tags = ["rust", "tauri", "dioxus", "surrealdb", "codemirror", "android", "wasm", "proof-of-concept", "mobile-development", "claude-code"]
series = ["Building omni-me"]

[extra]
series_order = 1
+++

## Reflections

I don't think I'm alone in wanting one app to rule them all — a single tool for budgeting, note-taking, journaling, scheduling, task management, archiving, and more. There are probably great options out there for each individual category, but I haven't seen one that does everything well, at least not to my satisfaction. That's why I'm starting this project, and this series, to document my progress as I try to make it a reality.

My goal is to create what will probably become my most-used app. I'm going with a mobile-first approach to make it easy to integrate into my daily routine. Part of my motivation — and you can see this by reviewing the project file on GitHub, where I document my reasons for starting any project — is to get better control over my data.

I think it was Socrates, by way of Plato, who talked about "the unexamined life." I might be stretching the quote a bit, but now that we're entering an age where cheap, high-quality LLM reasoning is readily available, the only bottleneck is how quickly and easily you can collect, process, and use your own data to help yourself. So I had two choices: sit back and wait for someone else to build this app for me, or try something audacious and build it myself — without worrying about my data being auctioned off to the highest bidder, or a company going bankrupt and taking an application I'd built my personal development around with it.

For something this ambitious, the smart move would probably be to start slow — use a proven technology stack you've worked with before, then gradually add features. I didn't make the smart choice, but I'd argue I made the more fun one, and the one that would force me to learn and grow a lot more.

In the age of AI, I have a bit of (admittedly false) confidence, since I essentially just need to set a direction and verify the quality of the work, while allowing the LLM — in this case Claude Opus 4.6 via Claude Code — to handle a lot of the technical heavy lifting. Since I chose the riskier but potentially more rewarding setup, I needed to dedicate time upfront to make sure my core technology assumptions weren't baseless. Hence this post, documenting the steps it took to validate each piece of the stack.

The app's current name is omni-me. Creative, I know. I plan to make several future entries in this series as I build out the infrastructure and start adding useful modules. If someone other than future me is reading this before those come out — stay tuned.

---

## Tutorial: Validating the Full Stack With 5 Proof-of-Concept Tests

This tutorial walks through the proof-of-concept phase of building a Rust-based mobile app. Before writing any production code for "omni-me" (a personal life management app covering journaling, routines, budgeting, and more), I ran 5 targeted POC validations to confirm that every layer of the technology stack works end-to-end — including on a physical Android phone.

The stack under test:

- **Tauri v2** — native app shell (desktop + Android)
- **Dioxus 0.7** — Rust UI framework, compiled to WASM, running inside Tauri's WebView
- **SurrealDB v3** — embedded database with pure-Rust storage engine
- **CodeMirror 6** — JavaScript text editor, embedded in the same WebView as Dioxus
- **Claude Code** — Anthropic's AI coding CLI, used as the primary development tool throughout

Each POC is designed to validate one specific integration point. They build on each other: POC 1 runs standalone, POCs 2-4 layer incrementally inside the same Tauri project, and POC 5 deploys everything to Android.

The 7 gotchas discovered during this phase would have been painful to hit mid-build. That alone justified the time investment.

### Assumptions

- **Operating system:** Linux (tested on Ubuntu with kernel 6.8, x86_64). macOS should work for POCs 1-4 with minor differences noted below. Windows users should use WSL2.
- **Rust:** Installed via [rustup](https://rustup.rs/), with the `wasm32-unknown-unknown` target added (`rustup target add wasm32-unknown-unknown`).
- **Node.js:** v18 or later (needed for CodeMirror bundling and Dioxus CLI).
- **Dioxus CLI:** Install with `cargo install dioxus-cli`. Version 0.7 was used.
- **Android development (POC 5 only):** Java 17, Android SDK with platform 35+, build-tools, and NDK r28. Details in the POC 5 section.

---

### POC 1: SurrealDB Embedded Storage (kv-surrealkv)

**Goal:** Confirm that SurrealDB v3 can run as an embedded database with file-backed persistence, using a pure-Rust storage engine (no C/C++ FFI dependencies like RocksDB).

**Why this matters:** The app needs an embedded database that compiles cleanly for both desktop and Android. Any dependency on C/C++ FFI (like RocksDB) would complicate the Android cross-compilation toolchain. SurrealDB's `kv-surrealkv` feature flag uses SurrealKV, which is pure Rust.

#### Set up the project

```bash
cargo new surrealdb-embedded
cd surrealdb-embedded
```

Add dependencies to `Cargo.toml`:

```toml
[package]
name = "surrealdb-embedded"
version = "0.1.0"
edition = "2024"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
surrealdb = { version = "3.0.2", features = ["kv-surrealkv"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

The key feature flag is `kv-surrealkv`. This gives you file-backed embedded storage without pulling in any C dependencies.

#### Gotcha: SurrealDB v3 API changes

If you are coming from SurrealDB v2 documentation or tutorials, be aware of two breaking changes in v3:

1. **`SurrealValue` derive macro replaces serde.** Your data structs need `#[derive(SurrealValue)]` from `surrealdb::types::SurrealValue`, not `#[derive(Serialize, Deserialize)]`. The database layer has its own serialization now.
2. **`RecordId` moved.** Import it from `surrealdb::types::RecordId`, not from the crate root.

#### Write the test code

Create `src/main.rs` with two data structs — one for creating records (no ID field) and one for reading them back (with ID):

```rust
use surrealdb::Surreal;
use surrealdb::engine::local::SurrealKv;
use surrealdb::types::{RecordId, SurrealValue};

const DB_PATH: &str = "./poc_data";

#[derive(Debug, Clone, SurrealValue)]
struct Event {
    title: String,
    payload: String,
    timestamp: String,
}

#[derive(Debug, SurrealValue)]
struct EventRecord {
    id: RecordId,
    title: String,
    payload: String,
    timestamp: String,
}
```

Note the `SurrealValue` derive on both structs. The `Event` struct (without `id`) is used for `create` and `update` operations. The `EventRecord` struct (with `id: RecordId`) is used when reading records back, since SurrealDB always returns the record ID.

#### Gotcha: Empty table errors

SurrealDB's `db.select("table")` call errors when the table has never had any records — it does not return an empty `Vec`. This is different from what you might expect coming from SQL databases where `SELECT * FROM nonexistent_table` might just return empty results (or a clear "table not found" error).

The workaround is to seed the table with at least one record before querying, or use `DEFINE TABLE` to pre-declare it. In the POC code, a seed record is inserted at startup and deleted at the end:

```rust
#[tokio::main]
async fn main() -> surrealdb::Result<()> {
    println!("=== SurrealDB Embedded POC ===\n");

    // Connect to file-backed SurrealKV
    let db = Surreal::new::<SurrealKv>(DB_PATH).await?;
    db.use_ns("omni").use_db("poc").await?;

    // Seed the table so select() doesn't error on empty tables
    let seed: Option<EventRecord> = db
        .create(("events", "seed_event"))
        .content(Event {
            title: "seed_event".into(),
            payload: "{test: seed payload}".into(),
            timestamp: "test_time_stamp".into(),
        })
        .await?;
    dbg!(seed);

    // Check if data already exists (persistence test)
    let existing: Vec<EventRecord> = db.select("events").await?;

    if existing.len() < 2 {
        println!("No existing non-seed data found — first run.");
        println!("Running CRUD tests...\n");
        test_crud(&db).await?;
    } else {
        println!(
            "PERSISTENCE VERIFIED: Found {} events from previous run:",
            existing.len()
        );
        for event in &existing {
            println!("  - {} | {} | {}", event.title, event.payload, event.timestamp);
        }
        println!("\nData survived restart. POC PASSED.");
    }

    // Clean up the seed record
    let _: Option<Event> = db.delete(("events", "seed_event")).await?;

    Ok(())
}
```

The `test_crud` function exercises all four CRUD operations — create with auto-generated IDs, create with explicit IDs, select, update, and delete:

```rust
async fn test_crud(db: &Surreal<surrealdb::engine::local::Db>) -> surrealdb::Result<()> {
    // CREATE with auto-generated ID
    let _event1: Option<Event> = db
        .create("events")
        .content(Event {
            title: "test_title1".into(),
            payload: "{test: test payload1}".into(),
            timestamp: "test_time_stamp1".into(),
        })
        .await?;
    let existing: Vec<EventRecord> = db.select("events").await?;
    println!("After first insert: {} records\n", existing.len());

    // CREATE with explicit ID
    let _: Option<EventRecord> = db
        .create(("events", "event_record1"))
        .content(Event {
            title: "test_title_record".into(),
            payload: "{test: test payload3}".into(),
            timestamp: "test_time_stamp3".into(),
        })
        .await?;

    // READ specific record
    let record: Option<EventRecord> = db.select(("events", "event_record1")).await?;
    println!("Read back: {record:#?}\n");

    // UPDATE
    let _: Option<EventRecord> = db
        .update(("events", "event_record1"))
        .content(Event {
            title: "updated_test_title_record".into(),
            payload: "{test: updated test payload3}".into(),
            timestamp: "updated_test_time_stamp3".into(),
        })
        .await?;
    let updated: Option<EventRecord> = db.select(("events", "event_record1")).await?;
    println!("After update: {updated:#?}\n");

    // DELETE
    let _: Option<EventRecord> = db.delete(("events", "event_record1")).await?;
    let remaining: Vec<EventRecord> = db.select("events").await?;
    println!("After delete: {} records remaining\n", remaining.len());

    Ok(())
}
```

#### Run the two-run persistence test

The persistence validation requires running the binary twice:

```bash
# First run — creates data and writes to ./poc_data/
cargo run

# Second run — reads back persisted data
cargo run
```

On the first run, you should see the CRUD operations execute and print record counts at each step. On the second run, the output should say `PERSISTENCE VERIFIED` and list the events that survived the restart. This confirms that `kv-surrealkv` is writing durable data to disk at `./poc_data/`.

To reset and test again:

```bash
rm -rf ./poc_data
cargo run  # First run again
cargo run  # Should verify persistence again
```

**Result:** SurrealDB v3 with `kv-surrealkv` works as an embedded database with file persistence. CRUD operations behave as expected. No C/C++ dependencies in the build.

---

### POC 2: Tauri v2 Desktop With Dioxus WASM Frontend

**Goal:** Confirm that a Dioxus 0.7 app compiled to WASM runs correctly inside a Tauri v2 desktop window.

**Why this matters:** Dioxus and Tauri are both Rust, but they run in fundamentally different contexts. Tauri provides the native window and system access. Dioxus compiles to WASM and runs inside Tauri's WebView — essentially a browser engine (WebKitGTK on Linux, WebView2 on Windows, WKWebView on macOS). This POC confirms the two work together.

#### Install Linux system dependencies

On Debian/Ubuntu, Tauri v2 requires several system libraries for the WebView:

```bash
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev \
    libayatana-appindicator3-dev librsvg2-dev patchelf
```

On macOS, no additional system dependencies are needed — WKWebView is built into the OS. On Windows, WebView2 is typically pre-installed on Windows 10/11.

#### Create the project structure

The project has two separate Rust crates: the Dioxus frontend (compiles to WASM) and the Tauri backend (compiles to a native binary). They share a directory but have independent `Cargo.toml` files.

```
tauri-dioxus/
  frontend/          # Dioxus WASM app
    Cargo.toml
    src/main.rs
  src-tauri/         # Tauri native backend
    Cargo.toml
    src/lib.rs
    src/main.rs
    tauri.conf.json
  package.json       # For CodeMirror (POC 4)
```

#### Set up the Dioxus frontend

```bash
mkdir -p tauri-dioxus/frontend/src
cd tauri-dioxus/frontend
```

Create `frontend/Cargo.toml`:

```toml
[package]
name = "frontend"
version = "0.1.0"
edition = "2024"

[dependencies]
dioxus = { version = "0.7", features = ["web"] }
```

The `web` feature tells Dioxus to compile for the WASM target.

Create a minimal `frontend/src/main.rs`:

```rust
use dioxus::prelude::*;

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    let mut count = use_signal(|| 0);

    rsx! {
        div {
            style: "font-family: sans-serif; padding: 2rem;",
            h1 { "Dioxus + Tauri POC" }
            p { "Counter: {count}" }
            button { onclick: move |_| count += 1, "Increment" }
            button { onclick: move |_| count -= 1, "Decrement" }
        }
    }
}
```

Build the WASM output:

```bash
dx build --platform web
```

This produces the compiled frontend at `frontend/target/dx/frontend/debug/web/public/`, including `index.html` and the WASM bundle.

#### Set up the Tauri backend

Initialize Tauri in the project root:

```bash
cd ..  # back to tauri-dioxus/
cargo tauri init
```

The init wizard will ask for your app name and window title. The key file it generates is `src-tauri/tauri.conf.json`. Edit it to point at the Dioxus build output:

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "tauri-dioxus-poc",
  "version": "0.1.0",
  "identifier": "com.omni-me.poc",
  "build": {
    "beforeDevCommand": "cd frontend && dx build --platform web --release",
    "beforeBuildCommand": "cd frontend && dx build --platform web --release",
    "frontendDist": "../frontend/target/dx/frontend/release/web/public"
  },
  "app": {
    "windows": [
      {
        "title": "Tauri + Dioxus POC",
        "width": 800,
        "height": 600
      }
    ],
    "security": {
      "csp": null
    }
  }
}
```

#### Gotcha: devUrl takes priority over frontendDist

If your `tauri.conf.json` has a `devUrl` field (which `cargo tauri init` may add by default), it takes priority over `frontendDist` in debug builds. This means Tauri will try to connect to a dev server instead of loading your static WASM files, and you will get a blank window or connection refused error.

The fix is simple: remove the `devUrl` field entirely if you are serving static WASM files. Only use `devUrl` if you are running an actual dev server (like Vite or Trunk).

#### Run it

```bash
cargo tauri dev
```

You should see a native window open with the Dioxus counter app. Click the buttons to verify reactivity works. The WASM is being served as static files from the Dioxus build output.

**Result:** Dioxus 0.7 compiles to WASM and runs inside Tauri v2's WebView. The reactive counter works. No dev server needed.

---

### POC 3: Tauri IPC (Dioxus WASM to Rust Backend)

**Goal:** Confirm that the Dioxus frontend (running as WASM in the WebView) can call Rust functions on the Tauri backend via IPC.

**Why this matters:** Even though both sides are written in Rust, they run in completely different environments. The Dioxus code runs in a WASM sandbox inside the WebView. The Tauri code runs as a native binary. Communication between them must cross the JavaScript bridge — there is no direct Rust-to-Rust function call.

#### Add the Tauri command

In `src-tauri/src/lib.rs`, define a Tauri command and register it:

```rust
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello from Rust, {}! Tauri IPC works.", name)
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

#### Gotcha: withGlobalTauri must be explicitly enabled

In Tauri v1, the `window.__TAURI__` object was automatically available in the WebView. In Tauri v2, you must opt in by adding `"withGlobalTauri": true` to the `app` section of `tauri.conf.json`:

```json
{
  "app": {
    "withGlobalTauri": true,
    "windows": [{ "title": "Tauri + Dioxus POC", "width": 800, "height": 600 }],
    "security": { "csp": null }
  }
}
```

Without this flag, `window.__TAURI__` is `undefined`. If your WASM code tries to call `window.__TAURI__.core.invoke()`, it will panic — and panics in WASM are unrecoverable. The entire WASM runtime crashes, the page goes blank, and you see nothing useful in the console. This is one of the more dangerous gotchas because the failure mode gives almost no diagnostic information.

#### Call the Tauri command from WASM

Add IPC dependencies to `frontend/Cargo.toml`:

```toml
[dependencies]
dioxus = { version = "0.7", features = ["web"] }
wasm-bindgen = "0.2"
wasm-bindgen-futures = "0.4"
js-sys = "0.3"
web-sys = { version = "0.3", features = ["Window"] }
serde = { version = "1", features = ["derive"] }
serde-wasm-bindgen = "0.6"
```

In `frontend/src/main.rs`, declare the JavaScript binding and create a wrapper function:

```rust
use dioxus::prelude::*;
use serde::Serialize;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = ["window", "__TAURI__", "core"], js_name = invoke)]
    fn tauri_invoke(cmd: &str, args: JsValue) -> js_sys::Promise;
}

async fn invoke_greet(name: &str) -> Result<String, String> {
    #[derive(Serialize)]
    struct GreetArgs<'a> {
        name: &'a str,
    }
    let args = serde_wasm_bindgen::to_value(&GreetArgs { name })
        .map_err(|e| e.to_string())?;
    let result = wasm_bindgen_futures::JsFuture::from(tauri_invoke("greet", args))
        .await
        .map_err(|e| format!("{e:?}"))?;
    result.as_string().ok_or_else(|| "Non-string response".into())
}
```

The `#[wasm_bindgen]` extern block tells the Rust-to-WASM compiler that `tauri_invoke` is a JavaScript function living at `window.__TAURI__.core.invoke`. The `invoke_greet` wrapper serializes the arguments using `serde-wasm-bindgen` and awaits the returned Promise.

Wire it into the Dioxus component:

```rust
#[component]
fn App() -> Element {
    let mut count = use_signal(|| 0);
    let mut ipc_result = use_signal(|| String::from("(not called yet)"));

    rsx! {
        div {
            style: "font-family: sans-serif; padding: 2rem;",
            h1 { "Dioxus + Tauri POC" }

            // Counter
            p { "Counter: {count}" }
            button { onclick: move |_| count += 1, "Increment" }
            button { onclick: move |_| count -= 1, "Decrement" }

            hr {}

            // IPC test
            h2 { "IPC Test" }
            button {
                onclick: move |_| {
                    spawn(async move {
                        match invoke_greet("Dioxus").await {
                            Ok(msg) => ipc_result.set(msg),
                            Err(e) => ipc_result.set(format!("ERROR: {e}")),
                        }
                    });
                },
                "Call Rust greet()"
            }
            p { "Result: {ipc_result}" }
        }
    }
}
```

Rebuild and run:

```bash
cd frontend && dx build --platform web && cd ..
cargo tauri dev
```

Click "Call Rust greet()" and you should see "Hello from Rust, Dioxus! Tauri IPC works." appear below the button.

**Result:** WASM-to-native IPC works via `window.__TAURI__.core.invoke()`. The `wasm-bindgen` extern pattern is clean and type-safe on the Rust side. Just remember `withGlobalTauri: true`.

---

### POC 4: CodeMirror 6 in the WebView

**Goal:** Confirm that CodeMirror 6 (a JavaScript text editor) can run alongside Dioxus WASM in the same WebView, with bidirectional communication.

**Why this matters:** The app needs a real text editor for journaling and note-taking. CodeMirror provides markdown syntax highlighting, vim keybindings, and a mature editing experience that would take months to reimplement in pure Rust/WASM. Since it is JavaScript and Dioxus WASM both run in the same WebView, they can communicate directly through global JS functions — no Tauri IPC needed for this path.

#### Install and bundle CodeMirror

From the project root:

```bash
npm init -y
npm install codemirror @codemirror/lang-markdown @codemirror/state @codemirror/view esbuild
```

Create `assets/js/editor.js`:

```javascript
import { EditorView, basicSetup } from "codemirror";
import { markdown } from "@codemirror/lang-markdown";
import { EditorState } from "@codemirror/state";

let editorView = null;

window.createEditor = function (elementId, initialContent) {
  const parent = document.getElementById(elementId);
  if (!parent) {
    console.error("Editor container not found:", elementId);
    return;
  }

  editorView = new EditorView({
    state: EditorState.create({
      doc: initialContent || "",
      extensions: [basicSetup, markdown()],
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
    changes: {
      from: 0,
      to: editorView.state.doc.length,
      insert: content,
    },
  });
};
```

The three global functions (`createEditor`, `getEditorContent`, `setEditorContent`) are the entire API surface between CodeMirror and Dioxus. They are deliberately simple — mount the editor, read from it, write to it.

Bundle it with esbuild:

```bash
npx esbuild assets/js/editor.js --bundle --outfile=assets/js/editor.bundle.js --format=iife
```

This produces a single `editor.bundle.js` file (~590KB with markdown support) that can be loaded with a `<script>` tag.

#### Copy the bundle into the Dioxus build output

The bundled JS file needs to be served alongside the Dioxus WASM output. Copy it into the assets directory of the Dioxus build:

```bash
mkdir -p frontend/target/dx/frontend/release/web/public/assets/js/
cp assets/js/editor.bundle.js frontend/target/dx/frontend/release/web/public/assets/js/
```

You will need to repeat this copy after each `dx build`. In a real project, you would automate this in the `beforeDevCommand` or a build script.

#### Call CodeMirror from Dioxus WASM

Declare the JavaScript bindings in `frontend/src/main.rs`:

```rust
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_name = createEditor)]
    fn js_create_editor(element_id: &str, initial_content: &str);

    #[wasm_bindgen(js_name = getEditorContent)]
    fn js_get_editor_content() -> String;

    #[wasm_bindgen(js_name = setEditorContent)]
    fn js_set_editor_content(content: &str);
}
```

These bindings are simpler than the Tauri IPC ones — no namespace needed, since the functions are directly on `window`. This is because CodeMirror and Dioxus WASM share the same JavaScript global scope within the WebView.

Load the script dynamically and initialize the editor using `use_effect`:

```rust
let mut editor_ready = use_signal(|| false);

use_effect(move || {
    spawn(async move {
        let document = web_sys::window().unwrap().document().unwrap();
        let script = document.create_element("script").unwrap();
        script.set_attribute("src", "/assets/js/editor.bundle.js").unwrap();

        // Wait for script to load via a Promise
        let promise = js_sys::Promise::new(&mut |resolve, _reject| {
            let resolve_clone = resolve.clone();
            let onload = Closure::once_into_js(move || {
                resolve_clone.call0(&JsValue::NULL).unwrap();
            });
            script
                .dyn_ref::<web_sys::HtmlElement>()
                .unwrap()
                .set_onload(Some(onload.unchecked_ref()));
        });

        let body = document.body().unwrap();
        body.append_child(&script).unwrap();

        // Wait for the script to load
        wasm_bindgen_futures::JsFuture::from(promise).await.unwrap();

        // Initialize the editor
        js_create_editor("editor-container", "# Hello from CodeMirror!\n\nType here...");
        editor_ready.set(true);
    });
});
```

This pattern — dynamically creating a `<script>` element and waiting for its `onload` callback via a JavaScript Promise — is necessary because the editor bundle is not available at WASM compile time. The `editor_ready` signal gates the UI buttons so they cannot be clicked before initialization completes.

Add the editor UI to the component:

```rust
// Editor container — CodeMirror mounts here
div {
    id: "editor-container",
    style: "border: 1px solid #ccc; min-height: 150px; margin-bottom: 1rem;",
}

// Editor controls
div {
    button {
        onclick: move |_| {
            let content = js_get_editor_content();
            editor_content.set(content);
        },
        disabled: !editor_ready(),
        "Read Editor Content"
    }
    button {
        onclick: move |_| {
            js_set_editor_content(
                "# Content set from Dioxus!\n\nThis was injected via WASM -> JS interop."
            );
        },
        disabled: !editor_ready(),
        "Set Editor Content"
    }
}
```

Rebuild and run:

```bash
cd frontend && dx build --platform web && cd ..
# Copy the CodeMirror bundle
cp assets/js/editor.bundle.js frontend/target/dx/frontend/debug/web/public/assets/js/
cargo tauri dev
```

You should see a CodeMirror editor with markdown highlighting. "Read Editor Content" pulls the current text out of CodeMirror into a Dioxus signal. "Set Editor Content" pushes new text from Dioxus into CodeMirror. Both directions work.

**Result:** CodeMirror 6 runs alongside Dioxus WASM in the same WebView. Direct JS function calls work for both reading and writing editor content. No Tauri IPC needed for this communication path.

---

### POC 5: Android APK

**Goal:** Confirm that the entire stack — Tauri shell, Dioxus WASM frontend, Tauri IPC, and CodeMirror — runs on a physical Android phone via a sideloaded APK.

**Why this matters:** Desktop success does not guarantee mobile success. Android loads Rust code via JNI as a shared library (`.so`), not as a standalone binary. The WebView is Android's built-in WebView (Chromium-based), which may behave differently from desktop WebKitGTK. This POC validates the full path from Rust compilation to running on hardware.

#### Install Android toolchain prerequisites

You need Java 17 specifically — not Java 11, which some older Tauri tutorials reference. The Android Gradle plugin used by Tauri v2 requires it.

```bash
# Install Java 17 (Debian/Ubuntu)
sudo apt install openjdk-17-jdk

# Verify
java -version
# Expected: openjdk version "17.x.x"
```

Install the Android SDK. The easiest path is [Android Studio](https://developer.android.com/studio), but you can also use the command-line tools only. You need:

- **Platform SDK:** API level 35 and 36
- **Build tools:** Latest version
- **NDK:** r28 (version 28.x.x)

Set the environment variables:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export NDK_HOME="$ANDROID_HOME/ndk/28.0.13004108"  # adjust version
export PATH="$ANDROID_HOME/platform-tools:$PATH"
```

Add the Android Rust targets:

```bash
rustup target add aarch64-linux-android armv7-linux-androideabi \
    i686-linux-android x86_64-linux-android
```

#### Gotcha: mobile_entry_point is required

On desktop, Tauri starts from `main()` in `src-tauri/src/main.rs`. On Android, there is no `main()` — the Rust code is loaded as a shared library via JNI. Tauri needs a function annotated with `#[tauri::mobile_entry_point]` to serve as the entry point.

In `src-tauri/src/lib.rs`, add:

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn mobile_entry_point() {
    run();
}
```

The `#[cfg_attr(mobile, ...)]` attribute means this annotation only applies when compiling for mobile targets. On desktop, the function exists but is just a regular function.

#### Gotcha: Cargo.toml crate-type

For Android, the Tauri crate must produce a C-compatible dynamic library (`.so`). Add `cdylib` and `staticlib` to the crate types in `src-tauri/Cargo.toml`:

```toml
[lib]
name = "tauri_dioxus_poc"
crate-type = ["staticlib", "cdylib", "rlib"]
```

- `cdylib` — produces the `.so` file that Android loads via JNI
- `staticlib` — needed for some static linking scenarios
- `rlib` — the default Rust library type, keeps `cargo tauri dev` (desktop) working

#### Initialize the Android project

```bash
cargo tauri android init
```

This generates `src-tauri/gen/android/` with a full Gradle project, including the JNI bridge code.

#### Gotcha: Frontend assets need manual copy for Android

Tauri's `frontendDist` path resolution in `tauri.conf.json` works for desktop builds but does not resolve correctly for Android Gradle builds. The Android build expects frontend assets at a specific location within the generated Gradle project.

You need to manually copy the frontend build output:

```bash
# Build the frontend for release
cd frontend && dx build --platform web --release && cd ..

# Copy to the Android assets directory
cp -r frontend/target/dx/frontend/release/web/public/* \
    src-tauri/gen/android/app/src/main/assets/
```

This includes `index.html`, the WASM bundle, and any JS assets (like the CodeMirror bundle). You need to redo this copy after any frontend changes before rebuilding the APK.

#### Build the APK

```bash
cargo tauri android build
```

This triggers a Gradle build that:
1. Cross-compiles the Rust code for Android ARM architectures
2. Packages the `.so` files into the APK
3. Bundles the frontend assets
4. Produces an APK at `src-tauri/gen/android/app/build/outputs/apk/`

#### Note: wasm-opt SIGABRT warning

During the build, you may see `wasm-opt` crash with a SIGABRT error related to a DWARF version mismatch. This is a known issue with certain `wasm-opt` versions and is non-fatal — the WASM output is still valid and functional. The APK will build successfully despite this warning.

#### Install on a physical device

Enable USB debugging on your Android phone (Settings > Developer Options > USB Debugging), connect via USB, and install:

```bash
adb install src-tauri/gen/android/app/build/outputs/apk/universal/release/app-universal-release.apk
```

Or use `cargo tauri android dev` with the phone connected for a faster iteration cycle.

#### What to verify on the phone

1. **App launches** — the Tauri WebView loads and renders the Dioxus UI
2. **Counter works** — increment/decrement buttons update the displayed count (Dioxus reactivity in WASM)
3. **IPC works** — "Call Rust greet()" button returns the greeting from native Rust (WASM to native via `__TAURI__`)
4. **CodeMirror works** — the editor loads, accepts text input, and the "Read/Set Editor Content" buttons work (JS interop within WebView)

**Result:** All four features worked on a physical Samsung Galaxy S21 5G. The APK was sideloaded successfully. The counter, IPC, and CodeMirror editor all functioned identically to the desktop version.

---

### Summary of Results

All 5 POCs passed on both desktop (Linux) and Android:

| POC | What Was Validated | Result |
|-----|--------------------|--------|
| 1. SurrealDB Embedded | File-backed storage with kv-surrealkv, CRUD operations, persistence across restarts | Pass |
| 2. Tauri + Dioxus | Dioxus WASM running inside Tauri's WebView, reactive UI | Pass |
| 3. Tauri IPC | WASM-to-native Rust communication via window.__TAURI__.core.invoke() | Pass |
| 4. CodeMirror | JS text editor alongside Dioxus WASM, bidirectional content sync | Pass |
| 5. Android APK | All of the above running on a physical phone via sideloaded APK | Pass |

### Gotchas Discovered

Seven issues were found that would have been painful to discover mid-build:

1. **SurrealDB v3 uses `SurrealValue` derive macro** — not serde's `Serialize`/`Deserialize`. Most documentation and examples online still reference v2.
2. **Empty table errors** — `db.select("table")` errors on tables with no records instead of returning an empty Vec. Seed records or `DEFINE TABLE` needed.
3. **`withGlobalTauri` is opt-in in Tauri v2** — without it, `window.__TAURI__` is undefined and WASM panics are unrecoverable (blank page, no error).
4. **`devUrl` overrides `frontendDist` in debug builds** — remove `devUrl` from `tauri.conf.json` if you are serving static WASM files.
5. **`mobile_entry_point` annotation required** — Android loads Rust as a `.so` via JNI, not as a binary with `main()`.
6. **Android asset path resolution** — Tauri's `frontendDist` does not resolve for Gradle builds. Frontend files need manual copy to `gen/android/app/src/main/assets/`.
7. **`wasm-opt` SIGABRT** — crashes with a DWARF version mismatch but is non-fatal. The build succeeds.

No fallbacks were needed. The architecture — Tauri v2, Dioxus 0.7 (WASM), SurrealDB v3 (embedded), and CodeMirror 6 — is validated for both desktop and mobile.

---

### Version Reference

| Tool | Version | Purpose |
|------|---------|---------|
| Rust | 1.85+ (edition 2024) | Language toolchain |
| Tauri | 2.x | Native app shell |
| Dioxus | 0.7 | UI framework (WASM) |
| SurrealDB | 3.0.2 | Embedded database |
| CodeMirror | 6.0.2 | Text editor (JS) |
| esbuild | 0.27.3 | JS bundler |
| Android SDK | Platform 35+36 | Mobile target |
| Android NDK | r28 | Native compilation |
| Java | 17 | Gradle build system |
