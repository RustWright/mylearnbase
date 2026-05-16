+++
title = "Building the Foundation: Rust Workspace, Database Layer, and CI/CD"
slug = "building-the-foundation-rust-workspace-and-infrastructure"
aliases = ["/posts/building-the-foundation-rust-workspace-and-infrastructure/"]
date = 2026-03-27
draft = false

[taxonomies]
tags = ["rust", "tauri", "dioxus", "surrealdb", "wasm", "mobile-development", "claude-code", "infrastructure", "project-setup"]
series = ["Building omni-me"]

[extra]
series_order = 2
+++

## Reflections

It's been a bit over two weeks since Phase 0 wrapped up. Part of the delay was a vacation, but the rest of it was me rethinking my entire methodology for running LLM-powered coding projects.

Working on projects where I have essentially zero domain knowledge, relying on the LLM to do the heavy lifting while I set the direction, has surfaced a constant tension. Part of me wants a firm grasp on everything happening in the codebase, to the point where I could recreate the project from scratch without the LLM's help. But there's another part that just wants to move fast and get to the point where I have a finished product that solves the problem I started the project for in the first place.

I think the answer is somewhere in the middle. If I can understand the project well enough to make small tweaks on my own without needing the LLM, but then trust it and stay out of its way when it's time to move; that's probably the right balance. Approaching every project with the mindset that I need to be able to rebuild the entire thing myself is asking for trouble and slowing things down.

That said, slow is fine when it comes to preserving alignment. I've seen the model run away with its own decisions, or get stuck in a troubleshooting loop where it's trying everything except the right thing. Keeping a human-dictated pace, where I know what each step is doing and can catch drift from my original intention, is worth the time cost.

Where the current system breaks down is the testing phase. My workflow currently requires me to manually write tests for everything, and a lot of that is boring boilerplate I'm not actually interested in. So I'm changing things up. The new plan: collaborate with the model to figure out which tests make sense, then have it write them — or have it create instructions so I can delegate the test writing to another model like Gemini or Grok.

But there's a second kind of testing I want to introduce, and this one is for me, not the code. I've always liked taking tests — I'm good at them, and the immediate feedback of "you understand this" or "you don't" is personally my preferred way to learn. So once we have a functional MVP, I want the model to write me two evaluations:

1. **A knowledge test** — true/false and multiple choice questions about the codebase. The number of questions scales with the size of the project.
2. **A practical test** — either the model intentionally introduces a bug for me to find and fix, or it gives me a task to modify a feature and I have to figure out how.

This changes my workflow from: initiation → research → planning → implementation → manual test writing (with planning through test writing repeating each cycle) — to: planning → implementation (repeating), then an examination phase after the MVP is complete. I may need to build a dedicated Claude skill for this.

The core tension I'm trying to resolve is wanting to move fast without getting in the model's way, while also making sure I don't get left behind in my own codebase. I've tried a few approaches so far, and this is the latest iteration.

---

## Tutorial: From POC to Production Workspace — Rust Monorepo, SurrealDB Schema, Axum Server, and CI/CD

The [previous post](@/posts/archive/2026-03-08-validating-a-rust-mobile-app-stack.md) in this series validated the technology stack with 5 proof-of-concept tests: Tauri v2, Dioxus WASM, SurrealDB embedded, CodeMirror 6, and Android APK deployment. Every POC passed. The stack works.

This post covers Phase 1: turning that pile of throwaway POC code into real project infrastructure. Four tasks were completed across two working sessions (March 25-26, 2026):

1. **Rust workspace scaffold** with 3 crates and a WASM frontend
2. **SurrealDB connection layer** with idempotent schema initialization
3. **Axum HTTP server** skeleton with health check and graceful shutdown
4. **GitHub Actions CI/CD** with parallel jobs and path-based filtering

By the end, the project has a clean monorepo structure, a database abstraction that hides SurrealDB from consumers, a server ready for API routes, and CI that runs in under 2 minutes on cache hits. The POC code is archived — not deleted — in case it is needed for reference.

### Assumptions

- **Operating system:** Linux (tested on Ubuntu with kernel 6.8, x86_64). macOS users should have no issues with the workspace and server tasks. Windows users should use WSL2.
- **Rust:** Installed via [rustup](https://rustup.rs/) with edition 2024 support (Rust 1.85+). The `wasm32-unknown-unknown` target must be added for the frontend (`rustup target add wasm32-unknown-unknown`).
- **Dioxus CLI:** Version 0.7+. Install with `cargo install dioxus-cli` or `cargo binstall dioxus-cli`.
- **Tauri CLI:** Version 2.10+. Install with `cargo install tauri-cli` or `cargo binstall tauri-cli`.
- **GitHub account:** For the CI/CD section. The workflow file is portable to other CI systems with minor changes.

---

### Task 1: Rust Workspace Scaffold

The POC phase produced standalone test projects — each with its own `Cargo.toml` and duplicate dependencies. The first real task is to reorganize everything into a Cargo workspace where crates share dependencies and compile together.

#### Target structure

```
omni-me/
  Cargo.toml              # workspace root
  core/                   # shared library (omni-me-core)
    Cargo.toml
    src/
      lib.rs
      db/
        mod.rs
        error.rs
  server/                 # Axum HTTP server (omni-me-server)
    Cargo.toml
    src/
      main.rs
  tauri-app/
    src-tauri/            # Tauri v2 native backend (omni-me-app)
      Cargo.toml
      src/
        lib.rs
        main.rs
      tauri.conf.json
    frontend/             # Dioxus WASM — NOT a workspace member
      Cargo.toml
      src/
        main.rs
    assets/js/            # placeholder for CodeMirror (Phase 4)
  .archive/poc/           # archived POC code
```

Three crates are workspace members: `core`, `server`, and `tauri-app/src-tauri`. The Dioxus frontend at `tauri-app/frontend/` is explicitly excluded. This distinction matters — it is the first gotcha.

#### Create the workspace root

Start with the root `Cargo.toml`:

```toml
[workspace]
members = ["core", "server", "tauri-app/src-tauri"]
exclude = ["tauri-app/frontend"]
resolver = "3"

[workspace.package]
version = "0.1.0"
edition = "2024"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
```

Key points:

- **`resolver = "3"`** is the new default for edition 2024. It changes how Cargo resolves feature flags across the dependency graph. If you are on an older edition, use `resolver = "2"`.
- **`workspace.package`** centralizes version and edition so individual crates inherit them with `version.workspace = true`.
- **`workspace.dependencies`** deduplicates common dependencies. Crates reference them as `serde = { workspace = true }` in their own `Cargo.toml`.

#### Gotcha 1: workspace.exclude is required for the WASM frontend

Cargo workspace discovery walks upward from any `Cargo.toml` it finds. When Dioxus CLI runs `cargo metadata` from inside `tauri-app/frontend/`, Cargo discovers the workspace root and tries to include the frontend as a member. But the frontend targets `wasm32-unknown-unknown` while the rest of the workspace targets the host platform. This conflict causes `dx build` to fail with confusing metadata errors.

The fix is `exclude = ["tauri-app/frontend"]` in the workspace root. This tells Cargo to treat the frontend as an independent project when commands are run from its directory, while still allowing the rest of the workspace to function normally.

Without this line, running `dx build --platform web` from the frontend directory will fail. The error message does not clearly point to the workspace conflict — it surfaces as a metadata resolution error that can send you down the wrong debugging path.

#### Create the core crate

```bash
mkdir -p core/src/db
```

`core/Cargo.toml`:

```toml
[package]
name = "omni-me-core"
version.workspace = true
edition.workspace = true

[dependencies]
surrealdb = { version = "3", features = ["kv-surrealkv"] }
tokio = { workspace = true }
thiserror = "2"

[dev-dependencies]
tempfile = "3"
```

`core/src/lib.rs`:

```rust
pub mod db;
```

The core crate is the shared library. Every other crate in the workspace depends on it. It owns the database layer, data types, and business logic. The server and Tauri app should never import `surrealdb` directly — they go through `omni_me_core::db`.

#### Create the server crate

```bash
mkdir -p server/src
```

`server/Cargo.toml`:

```toml
[package]
name = "omni-me-server"
version.workspace = true
edition.workspace = true

[dependencies]
omni-me-core = { path = "../core" }
axum = "0.8"
tokio = { workspace = true }
serde = { workspace = true }
serde_json = { workspace = true }
tower-http = { version = "0.6", features = ["cors", "trace"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
```

Note the `path = "../core"` dependency. Within a Cargo workspace, path dependencies are the standard way to link crates together.

#### Set up the Tauri app crate

The Tauri backend crate lives at `tauri-app/src-tauri/`:

`tauri-app/src-tauri/Cargo.toml`:

```toml
[package]
name = "omni-me-app"
version.workspace = true
edition.workspace = true

[lib]
name = "omni_me_app"
crate-type = ["staticlib", "cdylib", "rlib"]

[dependencies]
omni-me-core = { path = "../../core" }
tauri = { version = "2", features = [] }
serde = { workspace = true }
serde_json = { workspace = true }

[build-dependencies]
tauri-build = { version = "2", features = [] }
```

The `crate-type` includes `cdylib` for Android (JNI `.so` file), `staticlib` for static linking, and `rlib` for normal desktop Rust compilation. This was a gotcha discovered during the POC phase — if you skip `cdylib`, the Android build silently fails to produce the shared library.

#### Configure the Tauri frontend connection

`tauri-app/src-tauri/tauri.conf.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "omni-me",
  "version": "0.1.0",
  "identifier": "com.omni-me.app",
  "build": {
    "beforeDevCommand": "cd frontend && dx build --platform web --release",
    "beforeBuildCommand": "cd frontend && dx build --platform web --release",
    "frontendDist": "../frontend/target/dx/frontend/release/web/public"
  },
  "app": {
    "windows": [
      {
        "title": "omni-me",
        "width": 1024,
        "height": 768
      }
    ],
    "withGlobalTauri": true,
    "security": {
      "csp": null
    }
  }
}
```

#### Gotcha 2: Tauri's generate_context!() validates frontendDist at compile time

The `tauri::generate_context!()` macro in the Tauri crate reads `tauri.conf.json` at compile time and verifies that `frontendDist` points to a real directory. If the Dioxus WASM frontend has not been built yet, the Tauri crate will fail to compile with a path-not-found error.

This means the build order is strict: **Dioxus frontend first, then Tauri backend.** The `beforeDevCommand` and `beforeBuildCommand` settings handle this for `cargo tauri dev` and `cargo tauri build`, but if you run `cargo build` directly from the workspace root, the Tauri crate will fail unless the frontend output already exists.

This has implications for CI/CD — more on that in the CI section.

#### Gotcha 3: beforeDevCommand and frontendDist resolve from different base directories

This one is subtle. In `tauri.conf.json`:

- `beforeDevCommand` and `beforeBuildCommand` run from the **parent directory** of `src-tauri/` — in this case, `tauri-app/`.
- `frontendDist` resolves relative to **`src-tauri/` itself**.

So `cd frontend && dx build` in `beforeDevCommand` works because it runs from `tauri-app/`, where `frontend/` is a direct child. But `frontendDist` uses `../frontend/target/...` because it resolves from `tauri-app/src-tauri/`, one directory deeper.

If you assume both settings share the same base directory, you will get either a "command not found" error during the before-command or a "path not found" error from `generate_context!()`. The fix is to remember: commands run from the parent, paths resolve from src-tauri.

#### Set up the Dioxus frontend

`tauri-app/frontend/Cargo.toml`:

```toml
[package]
name = "frontend"
version = "0.1.0"
edition = "2024"

[dependencies]
dioxus = { version = "0.7", features = ["web"] }
wasm-bindgen = "0.2"
serde = { version = "1", features = ["derive"] }
```

The frontend has its own `Cargo.toml` with its own dependencies. It does not use `workspace = true` references because it is excluded from the workspace. This is intentional — it compiles to a different target.

`tauri-app/frontend/src/main.rs`:

```rust
use dioxus::prelude::*;

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    rsx! {
        h1 {"2026-03-24"}
        h2 {"What happened today? (Add as much detail as you want)"}
        div {
            "I woke up earlier than usual..."
        }
    }
}
```

This is deliberately minimal — a date heading, a writing prompt, and placeholder content. The layout mirrors an existing Obsidian daily journal workflow. The text editor (CodeMirror) will replace the static `div` in Phase 4. For now, the goal is just to verify the workspace compiles and the Tauri app launches with real content visible.

#### Archive the POC code

Rather than deleting the POC code, move it to an archive directory. It is useful reference material:

```bash
mkdir -p .archive/poc
git mv surrealdb-embedded .archive/poc/
git mv tauri-dioxus .archive/poc/
```

Using `git mv` preserves history. The archive directory is tracked in the repo but out of the way.

#### Verify the workspace builds

```bash
# Build workspace crates (core + server + tauri src-tauri)
# Note: this will fail if the frontend hasn't been built yet (Gotcha 2)
cd tauri-app/frontend && dx build --platform web --release && cd ../..
cargo build

# Or build just core + server (no frontend dependency)
cargo build -p omni-me-core -p omni-me-server
```

---

### Task 2: SurrealDB Connection Layer

With the workspace in place, the next step is the database abstraction in the core crate. This is the module that every other part of the system will use to interact with SurrealDB.

#### Design decisions

The connection layer follows three principles:

1. **Core owns the database type.** Consumers import `omni_me_core::db::Database`, never `surrealdb::Surreal<Db>` directly. This means SurrealDB is an implementation detail that can be swapped without changing the server or Tauri app.
2. **Schema initialization is idempotent.** Every call to `connect()` runs `init_schema()`, which uses `IF NOT EXISTS` on all definitions. The database can be opened repeatedly without errors or duplicate definitions.
3. **Errors are domain-typed.** A custom `DbError` enum wraps SurrealDB errors with context (connection, query, or schema failure).

#### Implement the error type

`core/src/db/error.rs`:

```rust
use std::fmt;

#[derive(Debug)]
pub enum DbError {
    Connection(String),
    Query(String),
    Schema(String),
}

impl fmt::Display for DbError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DbError::Connection(msg) => write!(f, "database connection error: {msg}"),
            DbError::Query(msg) => write!(f, "database query error: {msg}"),
            DbError::Schema(msg) => write!(f, "schema initialization error: {msg}"),
        }
    }
}

impl std::error::Error for DbError {}

impl From<surrealdb::Error> for DbError {
    fn from(err: surrealdb::Error) -> Self {
        DbError::Query(err.to_string())
    }
}
```

The `From<surrealdb::Error>` implementation allows using `?` in functions that return `Result<_, DbError>`. The three variants provide enough granularity to distinguish where a failure occurred without leaking SurrealDB internals.

#### Implement connect and schema initialization

`core/src/db/mod.rs`:

```rust
mod error;

pub use error::DbError;

use surrealdb::Surreal;
use surrealdb::engine::local::{Db, SurrealKv};

/// Re-exported database handle type. Consumers use this instead of
/// importing surrealdb directly.
pub type Database = Surreal<Db>;

const NAMESPACE: &str = "omni";
const DATABASE: &str = "main";

/// Connect to an embedded SurrealDB instance at the given path.
/// Creates the database file if it doesn't exist, selects namespace/db,
/// and initializes the schema.
pub async fn connect(path: &str) -> Result<Surreal<Db>, DbError> {
    let db = Surreal::new::<SurrealKv>(path)
        .await
        .map_err(|e| DbError::Connection(e.to_string()))?;

    db.use_ns(NAMESPACE)
        .use_db(DATABASE)
        .await
        .map_err(|e| DbError::Connection(e.to_string()))?;

    init_schema(&db).await?;

    Ok(db)
}
```

The `connect` function does three things in sequence: open the embedded SurrealKV store (creating the file if needed), select the namespace and database, and run schema initialization. If any step fails, it returns a descriptive `DbError`.

The `Database` type alias (`pub type Database = Surreal<Db>`) is the key abstraction. Every consumer crate uses this type without knowing it is backed by SurrealDB. If SurrealDB were replaced with SQLite tomorrow, only this module would change.

#### Define the event sourcing schema

```rust
async fn init_schema(db: &Surreal<Db>) -> Result<(), DbError> {
    db.query(
        "
        DEFINE TABLE IF NOT EXISTS events SCHEMAFULL;
        DEFINE FIELD IF NOT EXISTS event_type ON events TYPE string;
        DEFINE FIELD IF NOT EXISTS aggregate_id ON events TYPE string;
        DEFINE FIELD IF NOT EXISTS timestamp ON events TYPE datetime;
        DEFINE FIELD IF NOT EXISTS device_id ON events TYPE string;
        DEFINE FIELD IF NOT EXISTS payload ON events TYPE object FLEXIBLE;
        DEFINE INDEX IF NOT EXISTS idx_events_timestamp ON events FIELDS timestamp;
        DEFINE INDEX IF NOT EXISTS idx_events_aggregate ON events FIELDS aggregate_id;
        DEFINE INDEX IF NOT EXISTS idx_events_device ON events FIELDS device_id;

        DEFINE TABLE IF NOT EXISTS sync_state SCHEMAFULL;
        DEFINE FIELD IF NOT EXISTS device_id ON sync_state TYPE string;
        DEFINE FIELD IF NOT EXISTS last_sync_timestamp ON sync_state TYPE datetime;
        DEFINE INDEX IF NOT EXISTS idx_sync_device ON sync_state FIELDS device_id UNIQUE;
        ",
    )
    .await
    .map_err(|e| DbError::Schema(e.to_string()))?;

    Ok(())
}
```

Two tables:

- **`events`** — the core event store. Every user action (creating a note, completing a routine, logging an expense) becomes an immutable event. The `payload` field uses `TYPE object FLEXIBLE`, which allows arbitrary nested JSON-like data without pre-defining every possible field. The other fields (`event_type`, `aggregate_id`, `timestamp`, `device_id`) are strictly typed for reliable querying and indexing.
- **`sync_state`** — tracks the last sync timestamp per device. The unique index on `device_id` prevents duplicate device records.

The three indexes on `events` support the most common query patterns: "all events since timestamp X" (for sync), "all events for aggregate Y" (for reconstructing entity state), and "all events from device Z" (for debugging).

#### Gotcha 4: SurrealDB FLEXIBLE keyword position

In SurrealDB v3, the `FLEXIBLE` keyword goes **after** `TYPE`, not before:

```sql
-- Correct:
DEFINE FIELD payload ON events TYPE object FLEXIBLE;

-- Wrong (will error):
DEFINE FIELD payload ON events FLEXIBLE TYPE object;
```

This is a SurrealDB-specific syntax that differs from what you might expect based on SQL conventions. The error message when you get it wrong is not particularly helpful — it reports a parse error at an unexpected position.

#### Gotcha 5: SurrealKV holds exclusive file locks

SurrealKV uses exclusive file locks on its data directory. If you try to open the same database path twice — for example, running the server and a test binary simultaneously — the second process will fail with a lock error.

In development, this means:
- Stop the server before running tests that use the same database path
- Use `tempfile::tempdir()` in tests to get a unique path per test
- The Tauri app and server should use different database paths if running on the same machine

#### Write a test

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_connect_and_schema() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("test.db");

        let db = connect(path.to_str().unwrap()).await.unwrap();

        // Verify we can insert into the events table
        let result: Vec<surrealdb::types::RecordId> = db
            .query(
                "CREATE events CONTENT {
                    event_type: 'test_event',
                    aggregate_id: 'test-123',
                    timestamp: d'2026-03-24T12:00:00Z',
                    device_id: 'device-1',
                    payload: { key: 'value' }
                } RETURN id",
            )
            .await
            .unwrap()
            .take("id")
            .unwrap();

        assert_eq!(result.len(), 1);

        // Verify we can query it back
        let count: Option<usize> = db
            .query("SELECT count() AS total FROM events GROUP ALL")
            .await
            .unwrap()
            .take("total")
            .unwrap();

        assert_eq!(count, Some(1));
    }
}
```

The test uses `tempfile::tempdir()` to create an isolated database per test run. This avoids the file lock gotcha and ensures test independence. It inserts an event with all required fields and queries it back, validating both the schema definitions and the FLEXIBLE payload.

Run it:

```bash
cargo test -p omni-me-core
```

---

### Task 3: Axum Server Skeleton

The server is the sync hub. When the phone and desktop both run the app, they sync events through this server. For now, it just needs to start up, connect to the database, and serve a health check. The real API routes come in later phases.

#### Implement the server

`server/src/main.rs`:

```rust
use axum::{Router, Json, routing::get};
use omni_me_core::db::Database;
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use tokio::signal;

const DB_PATH: &str = "surreal_data/server.db";
const LISTEN_ADDR: &str = "0.0.0.0:3000";

#[derive(Clone)]
struct AppState {
    db: Arc<Database>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "omni_me_server=debug,tower_http=debug".into()),
        )
        .init();

    let db = omni_me_core::db::connect(DB_PATH)
        .await
        .expect("failed to connect to SurrealDB");

    let state = AppState { db: Arc::new(db) };

    let app = Router::new()
        .route("/health", get(health))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(LISTEN_ADDR)
        .await
        .expect("failed to bind");

    tracing::info!("listening on {LISTEN_ADDR}");

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("server error");
}

async fn health() -> Json<serde_json::Value> {
    Json(serde_json::json!({ "status": "ok" }))
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    tracing::info!("shutdown signal received, starting graceful shutdown");
}
```

Walking through the key design choices:

#### AppState with Arc

Axum requires that router state implements `Clone`. The `Database` type (SurrealDB handle) is not cheap to clone, so it is wrapped in `Arc<Database>`. The `AppState` struct derives `Clone`, which clones the `Arc` pointer — not the database handle itself.

```rust
#[derive(Clone)]
struct AppState {
    db: Arc<Database>,
}
```

Notice the import: `use omni_me_core::db::Database`. The server does not import `surrealdb` directly. It does not need to know what `Database` is backed by. This is the abstraction boundary from the core crate doing its job.

#### Middleware layers

Two tower-http layers are added:

- **`CorsLayer::permissive()`** allows all origins, methods, and headers. This is deliberately loose for development — the Dioxus frontend running in the Tauri WebView makes requests to localhost. In production, this gets locked down to specific origins.
- **`TraceLayer::new_for_http()`** logs every request automatically, including method, path, status code, and response time. Combined with the tracing subscriber, you get structured logs without adding logging code to each handler.

#### Graceful shutdown

The `shutdown_signal` function handles both `Ctrl+C` (interactive use) and `SIGTERM` (systemd/Docker). This matters because the server will eventually run on a VPS managed by systemd. When systemd sends `SIGTERM` during a restart or shutdown, the server needs to finish in-flight requests before exiting rather than dropping connections.

```rust
tokio::select! {
    _ = ctrl_c => {},
    _ = terminate => {},
}
```

`tokio::select!` waits for whichever signal arrives first. On macOS, `SIGTERM` handling works the same way. On Windows, you would replace the Unix signal handler with `tokio::signal::windows::ctrl_close()`.

#### Test it

```bash
cargo run -p omni-me-server
```

In another terminal:

```bash
curl http://localhost:3000/health
# {"status":"ok"}
```

You should also see structured trace output in the server terminal showing the request details and timing.

---

### Task 4: CI/CD With GitHub Actions

With three crates in the workspace, CI needs to build and test them on every push. But there is a catch: the Tauri app cannot be built without the Dioxus frontend already compiled (Gotcha 2 from the workspace section). This drives the CI design toward two separate, parallel jobs.

#### The workflow file

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  build-and-test:
    name: Build & Test (Workspace)
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'pull_request' ||
      contains(toJSON(github.event.commits.*.modified), 'core/') ||
      contains(toJSON(github.event.commits.*.modified), 'server/') ||
      contains(toJSON(github.event.commits.*.added), 'core/') ||
      contains(toJSON(github.event.commits.*.added), 'server/') ||
      contains(toJSON(github.event.commits.*.modified), 'Cargo') ||
      contains(toJSON(github.event.commits.*.added), 'Cargo')

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable

      - name: Cache cargo
        uses: Swatinem/rust-cache@v2

      - name: Run tests
        run: cargo test -p omni-me-core -p omni-me-server

      - name: Build release
        run: cargo build --release -p omni-me-core -p omni-me-server

  build-frontend:
    name: Build Frontend (WASM)
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'pull_request' ||
      contains(toJSON(github.event.commits.*.modified), 'tauri-app/frontend/') ||
      contains(toJSON(github.event.commits.*.added), 'tauri-app/frontend/')

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: wasm32-unknown-unknown

      - name: Cache cargo
        uses: Swatinem/rust-cache@v2
        with:
          workspaces: tauri-app/frontend
          cache-bin: false

      - name: Install dioxus-cli
        uses: cargo-bins/cargo-binstall@main
      - name: Binstall dx
        run: cargo binstall dioxus-cli --no-confirm --force

      - name: Build frontend
        working-directory: tauri-app/frontend
        run: dx build --platform web --release
```

#### Two parallel jobs, not one

The workspace job (`build-and-test`) builds and tests `omni-me-core` and `omni-me-server` using explicit `-p` flags. It does **not** build the Tauri app crate. Why? Because `cargo build` without `-p` flags would try to compile all workspace members, including `omni-me-app` (the Tauri crate), which would fail — `generate_context!()` needs the frontend built first, and the frontend is not part of this job.

The frontend job (`build-frontend`) installs Dioxus CLI and builds the WASM output independently. These two jobs run in parallel since they have no dependency on each other.

A future improvement would be a third job that builds the full Tauri app by running the frontend job first, then compiling the Tauri crate. For now, the two independent jobs catch the most common breakages.

#### Path-based filtering

Each job has an `if` condition that checks which files changed:

```yaml
if: >
  github.event_name == 'pull_request' ||
  contains(toJSON(github.event.commits.*.modified), 'core/') ||
  contains(toJSON(github.event.commits.*.modified), 'server/') ||
  ...
```

This means:
- **Pull requests** always run both jobs (full CI on PRs)
- **Pushes to main** only run a job if its relevant files changed

If you push a commit that only touches `tauri-app/frontend/`, the workspace job is skipped. If you push a commit that only touches `core/`, the frontend job is skipped. Edits to root `Cargo.toml` or `Cargo.lock` trigger the workspace job since dependency changes could break anything.

This saves CI minutes on a project where SurrealDB alone pulls ~270 crates and takes 6+ minutes to build from scratch.

#### Dependency caching with rust-cache

`Swatinem/rust-cache@v2` caches the `target/` directory and `~/.cargo/registry/` between CI runs. On a cache hit, the workspace build drops from 6+ minutes to under 2 minutes.

For the frontend job, note the `workspaces: tauri-app/frontend` setting. This tells rust-cache where to find the `target/` directory, since the frontend is not in the workspace root.

#### Gotcha 6: rust-cache cleans the cargo bin directory

This one cost multiple CI iterations to diagnose. The `Swatinem/rust-cache` action, by default, caches and restores `~/.cargo/bin/`. Sounds helpful, but it also **cleans** that directory between runs to keep the cache fresh. This means:

1. First CI run: `cargo binstall dioxus-cli` installs the `dx` binary to `~/.cargo/bin/`
2. rust-cache saves `~/.cargo/bin/` (including `dx`) to the cache
3. Second CI run: rust-cache restores its cache, but the clean step removes `dx`
4. `cargo binstall` checks `~/.cargo/.crates.toml`, sees `dx` is "already installed," and skips the install
5. `dx build` fails: command not found

The cache metadata says `dx` is installed, but the binary is gone. Two fixes are needed together:

**Fix 1: `cache-bin: false`** tells rust-cache to leave `~/.cargo/bin/` alone:

```yaml
- name: Cache cargo
  uses: Swatinem/rust-cache@v2
  with:
    workspaces: tauri-app/frontend
    cache-bin: false
```

**Fix 2: `--force` on binstall** forces reinstallation even if `.crates.toml` thinks it is already present:

```yaml
- name: Binstall dx
  run: cargo binstall dioxus-cli --no-confirm --force
```

Either fix alone is insufficient. Without `cache-bin: false`, the cache still interferes. Without `--force`, a stale `.crates.toml` from a previous cache prevents reinstallation.

#### Gotcha 7: No system dependencies needed for core + server

Early versions of the CI workflow installed `libwebkit2gtk-4.1-dev`, `libgtk-3-dev`, and other Tauri system dependencies. These are only needed to compile the Tauri crate (`omni-me-app`). Since the workspace job only builds `omni-me-core` and `omni-me-server` with explicit `-p` flags, these dependencies are unnecessary and were removed.

This reduces the CI setup time and avoids `apt-get` commands that occasionally fail due to mirror availability.

---

### Decisions Made During Phase 1

Two infrastructure decisions were made during this phase that affect future work:

**VPS deferred.** The original plan was to deploy the Axum server to a DigitalOcean droplet during Phase 1. DigitalOcean rejected the payment method (prepaid card). Rather than fighting payment issues, the decision was made to develop locally and go straight to Hetzner CX22 (~4.50 EUR/month) when features are stable enough to justify a VPS. For now, the server runs on localhost.

**Local mobile testing via Tailscale.** Without a VPS, phone-to-desktop sync testing uses Tailscale, a mesh VPN that assigns stable IPs to devices on the same network. The desktop runs the Axum server, and the phone (running the Tauri Android app) connects to it over the Tailscale mesh. No port forwarding or public IP needed.

---

### Summary

Phase 1 converted POC experiments into a working project foundation:

| Task | What Was Built | Key File(s) |
|------|---------------|-------------|
| Workspace scaffold | 3-crate Cargo workspace with excluded WASM frontend | `Cargo.toml` |
| SurrealDB layer | Connection, schema init, error types, Database type alias | `core/src/db/mod.rs`, `core/src/db/error.rs` |
| Axum server | Health endpoint, CORS, tracing, graceful shutdown | `server/src/main.rs` |
| CI/CD | Two parallel GitHub Actions jobs with path filtering and caching | `.github/workflows/ci.yml` |

Seven gotchas were documented:

1. `workspace.exclude` required for WASM frontend (dx build metadata conflict)
2. `generate_context!()` validates `frontendDist` at compile time (build order matters)
3. `beforeDevCommand` and `frontendDist` resolve from different base directories
4. SurrealDB `FLEXIBLE` goes after `TYPE`, not before
5. SurrealKV holds exclusive file locks (cannot open same path twice)
6. `rust-cache` cleans `cargo/bin`, breaking `dx` installation across runs
7. System dependencies not needed for core + server CI jobs

The POC code is archived at `.archive/poc/`. The project is ready for Phase 2: event sourcing implementation, LLM integration, and the first real UI work.

---

### Version Reference

| Tool | Version | Purpose |
|------|---------|---------|
| Rust | 1.85+ (edition 2024, resolver 3) | Language toolchain |
| Tauri | 2.x | Native app shell |
| Dioxus | 0.7 | UI framework (WASM) |
| SurrealDB | 3.x (kv-surrealkv) | Embedded database |
| Axum | 0.8 | HTTP server framework |
| tower-http | 0.6 | CORS + tracing middleware |
| GitHub Actions | ubuntu-latest | CI/CD runner |
| Swatinem/rust-cache | v2 | Cargo dependency caching |
| cargo-binstall | latest | Fast binary installation |
