+++
title = "Event Sourcing, Sync Protocol, and the LLM Pipeline"
slug = "event-sourcing-sync-and-llm-pipeline"
date = 2026-04-11
draft = false

[taxonomies]
tags = ["rust", "event-sourcing", "surrealdb", "sync", "llm", "gemini", "claude-code", "mobile-development"]
series = ["Building omni-me"]

[extra]
series_order = 3
+++

## Reflections

It's been almost two weeks since the last post. The work covered here was actually completed right after the previous post — I finished it in a three-day stretch from March 27 to 30. But when it came time to sit down and write this reflection, I started overthinking it and let other things in my life take over.

The overall approach I described in the last post — getting out of the LLM's way to maintain development velocity — worked well. But there seems to be a weird conservation-of-effort effect at play: even after getting so much done so quickly, I let the project sit untouched for almost two weeks. I'll be picking it back up after releasing this article and its [companion post](@/posts/2026-03-30-from-shell-to-ship-ui-features-and-android.md) about the later phases of Cycle 1.

I'm still wrestling with how to stay knowledgeable about my own codebase. In the last post, I mentioned some overly complicated knowledge-test idea — a theory portion plus a practical portion — which sounds more and more daunting the more I think about it. But while proofreading this article, I realized I could get most of that value by leveraging what already exists: I asked myself whether I could just add quizzes to the mylearnbase project.

The idea is simple: since writing posts is already part of my development process, each post could feed into a quiz based on its content and the underlying code. The primary goal would be to help me — the person doing the development with LLM assistance — make sure I'm not getting left behind when I try to move quickly. I don't see a reason to keep quizzes private, so this would likely become a public feature of mylearnbase, with a quiz linked at the beginning or end of each post (or both). The format would be something automatically gradable — true/false, multiple choice, that sort of thing. I wonder if I can learn something from the quizzes attached to the Rust Book. These are all just ideas for now; I'll need to experiment to figure out the right implementation.

As for the practical side, I use a learning output style when working with Claude Code, which automatically pauses during development and prompts me to implement certain parts of the code myself. That'll have to do for now, unless I run into a situation where I understand the theory of how the codebase works but can't actually make changes.

---

## Tutorial: The Invisible Engine --- Event Store, Sync, and LLM Processing in Rust

The [previous post](@/posts/2026-03-27-building-the-foundation-rust-workspace-and-infrastructure.md) set up the workspace scaffold, the SurrealDB connection layer, the Axum server skeleton, and CI/CD. That was Phase 1 --- the skeleton. This post covers Phases 2 and 3: the event store, the sync protocol, the projection framework, and the LLM processing pipeline. None of this has a UI yet. It is the invisible engine that everything visible will eventually depend on.

Phase 2 builds the append-only event log, the projections that derive read-optimized views from those events, and the sync protocol that replicates events between devices. Phase 3 adds an LLM pipeline that processes journal notes through Gemini 2.0 Flash, extracting tags, mood, tasks, dates, and expenses via tool calling --- then records the results as events themselves, closing the loop.

By the end, the system has a complete write path (events), read path (projections), replication path (sync), and intelligence path (LLM pipeline). The UI layers that come next just need to call these.

### Assumptions

- **Previous post completed:** You have the Rust workspace with `core`, `server`, and `tauri-app/src-tauri` crates, SurrealDB connection layer, and Axum server skeleton from Phase 1.
- **Operating system:** Linux (tested on Ubuntu with kernel 6.8, x86_64). macOS should work with no changes for the core and server crates.
- **Rust:** Edition 2024 (1.85+) with `wasm32-unknown-unknown` target.
- **SurrealDB:** Version 3.x with the `kv-surrealkv` feature flag for embedded storage.
- **Gemini API key:** Required for the LLM pipeline section. The free tier of Gemini 2.0 Flash is sufficient.

---

### Phase 2: Event Store + Sync

#### Why event sourcing over CRUD

A traditional CRUD approach stores the current state of each entity. When you update a note, the previous version is gone. Event sourcing stores every change as an immutable event. The current state is derived by replaying events through projections.

For a personal life management app that syncs across devices, this has three concrete benefits:

1. **No conflict resolution.** When two devices create events offline, both events are valid. There is no "last write wins" problem because nothing is being overwritten. Events are appended, and projections reconcile the full history.
2. **Full audit trail.** Every edit, every completion, every LLM processing run is a permanent record. If a prompt version produces bad results, the events are still there and can be reprocessed.
3. **Decoupled read and write models.** The event log is optimized for writes (append-only). Projections create whatever read tables the UI needs. Adding a new view means adding a new projection, not restructuring the database.

#### Event store data model

The core data model has two structs: `Event` (a persisted event with a generated ID) and `NewEvent` (an event to be appended, with an optional ID).

```rust
/// A persisted event with a generated ID.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: String,
    pub event_type: String,
    pub aggregate_id: String,
    pub timestamp: DateTime<Utc>,
    pub device_id: String,
    pub payload: serde_json::Value,
}

/// An event to be appended — supply an ID to preserve it, or leave as None to auto-generate.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NewEvent {
    #[serde(default)]
    pub id: Option<String>,
    pub event_type: String,
    pub aggregate_id: String,
    pub timestamp: DateTime<Utc>,
    pub device_id: String,
    pub payload: serde_json::Value,
}
```

Key design choices:

- **`id` is a ULID** (Universally Unique Lexicographically Sortable Identifier), auto-generated on append if not provided. ULIDs sort chronologically, which makes time-range queries on the event log efficient without a secondary index.
- **`aggregate_id`** groups events that belong to the same entity (e.g., all events for note `note-abc`).
- **`device_id`** identifies which device produced the event. This is critical for sync --- when pulling events from the server, a device filters out its own events to avoid duplicates.
- **`payload` is `serde_json::Value`** --- a flexible JSON blob whose shape depends on the `event_type`. Typed payload structs validate the shape on append, but the storage layer stays schemaless.

The optional `id` field on `NewEvent` exists for sync. When a device pulls events from the server, those events already have IDs assigned by the originating device. The receiving device preserves those IDs to maintain global uniqueness.

#### EventStore trait

The event store has three operations: append, query by time, and query by aggregate.

```rust
/// Event store trait — append-only event log.
#[async_trait]
pub trait EventStore: Send + Sync {
    /// Append a new event, generating a ULID for the id.
    async fn append(&self, event: NewEvent) -> Result<Event, EventError>;

    /// Get all events since a given timestamp, optionally excluding a specific device.
    async fn get_since(
        &self,
        since: DateTime<Utc>,
        exclude_device: Option<&str>,
    ) -> Result<Vec<Event>, EventError>;

    /// Get all events for a given aggregate, ordered by timestamp.
    async fn get_by_aggregate(&self, aggregate_id: &str) -> Result<Vec<Event>, EventError>;
}
```

`get_since` accepts an `exclude_device` parameter because the sync pull endpoint needs to return all events *except* those the requesting device already has (its own events). This keeps the query at the database level rather than filtering in application code.

The `SurrealEventStore` implementation uses `INSERT ... ON DUPLICATE KEY UPDATE id = id` for idempotent appends --- if an event with the same ID already exists (from a sync), the insert is silently ignored:

```rust
self.db
    .query(
        "INSERT INTO events {
            id: type::record('events', $id),
            event_type: $event_type,
            aggregate_id: $aggregate_id,
            timestamp: type::datetime($timestamp),
            device_id: $device_id,
            payload: $payload
        } ON DUPLICATE KEY UPDATE id = id",
    )
    .bind(("id", id.clone()))
    .bind(("event_type", event.event_type.clone()))
    .bind(("aggregate_id", event.aggregate_id.clone()))
    .bind(("timestamp", ts_str))
    .bind(("device_id", event.device_id.clone()))
    .bind(("payload", event.payload.clone()))
    .await
    .map_err(|e| EventError::Store(e.to_string()))?;
```

The `ON DUPLICATE KEY UPDATE id = id` is a no-op update --- it satisfies SurrealDB's requirement for an update clause without actually changing anything. This makes append idempotent, which is essential for the sync protocol where the same event may arrive more than once.

#### Event type registry

Every event has a string `event_type` field. The `EventType` enum provides compile-time validation and a `FromStr`/`Display` roundtrip:

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EventType {
    NoteCreated,
    NoteUpdated,
    NoteLlmProcessed,
    RoutineGroupCreated,
    RoutineItemAdded,
    RoutineItemCompleted,
    RoutineItemSkipped,
    RoutineGroupModified,
}
```

Each variant maps to a snake_case string (`NoteCreated` -> `"note_created"`). The string representation is what gets stored in the database, and the enum is used in Rust code for pattern matching.

Each event type has a corresponding typed payload struct:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NoteCreatedPayload {
    pub raw_text: String,
    pub date: chrono::NaiveDate,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NoteLlmProcessedPayload {
    pub note_id: String,
    pub prompt_version: String,
    pub model: String,
    pub derived: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoutineItemCompletedPayload {
    pub item_id: String,
    pub group_id: String,
    pub date: chrono::NaiveDate,
    pub completed_at: chrono::DateTime<chrono::Utc>,
}
```

The `validate_payload` function attempts to deserialize the JSON payload into the expected typed struct for the given event type. If deserialization fails, the event is rejected before it reaches the store:

```rust
pub fn validate_payload(
    event_type: &EventType,
    payload: &serde_json::Value,
) -> Result<(), super::store::EventError> {
    let result = match event_type {
        EventType::NoteCreated => {
            serde_json::from_value::<NoteCreatedPayload>(payload.clone()).map(|_| ())
        }
        EventType::NoteLlmProcessed => {
            serde_json::from_value::<NoteLlmProcessedPayload>(payload.clone()).map(|_| ())
        }
        // ... other variants
    };

    result.map_err(|e| {
        super::store::EventError::Validation(format!(
            "invalid payload for {event_type}: {e}"
        ))
    })
}
```

This gives the system a flexible storage layer (JSON payloads) with strict validation at the boundary.

#### Projection framework

Events are the source of truth. Projections are the read model --- they transform the event stream into query-optimized tables that the UI can read directly.

The `Projection` trait defines the interface:

```rust
/// A projection transforms events into read-optimized views.
#[async_trait]
pub trait Projection: Send + Sync {
    /// Human-readable name for this projection.
    fn name(&self) -> &str;

    /// Schema version — bump when the projection logic changes.
    fn version(&self) -> u32;

    /// Apply a single event to this projection's read tables.
    async fn apply(&self, event: &Event, db: &Database) -> Result<(), EventError>;

    /// Initialize any tables/indexes this projection requires.
    async fn init_schema(&self, db: &Database) -> Result<(), EventError>;
}
```

Each projection owns its read tables. `init_schema` creates them with `DEFINE TABLE IF NOT EXISTS`, and `apply` handles one event at a time --- the projection inspects the event type and decides whether to act or ignore it.

The `ProjectionRunner` orchestrates the lifecycle:

```rust
pub struct ProjectionRunner {
    db: Database,
    projections: Vec<Box<dyn Projection>>,
}
```

It provides three operations:

- **`init_all()`** --- initializes all projection schemas and creates a `projection_versions` tracking table that records each projection's name, version, and the ID of the last event it processed.
- **`apply_events(&[Event])`** --- feeds a batch of events through all projections in order, updating the `last_event_id` cursor after each event.
- **`rebuild()`** --- wipes the read tables, fetches all events from epoch, and replays them. This is the nuclear option for when a projection's logic changes and the read tables need to be regenerated from scratch.

The version tracking in `projection_versions` exists for future use --- when a projection's `version()` changes, the runner can detect the mismatch and trigger a rebuild automatically.

#### Notes projection

The `NotesProjection` maintains a `notes` read table. It listens for three event types:

```rust
async fn apply(&self, event: &Event, db: &Database) -> Result<(), EventError> {
    match event.event_type.as_str() {
        "note_created" => self.on_note_created(event, db).await,
        "note_updated" => self.on_note_updated(event, db).await,
        "note_llm_processed" => self.on_note_llm_processed(event, db).await,
        _ => Ok(()), // Ignore events this projection doesn't care about
    }
}
```

`on_note_created` inserts a new row with `raw_text`, `date`, empty `tags`, and null `summary`/`mood` fields. `on_note_updated` overwrites the `raw_text`. The interesting one is `on_note_llm_processed`, which extracts the LLM-derived data from the event payload and updates the note's read table:

```rust
async fn on_note_llm_processed(&self, event: &Event, db: &Database) -> Result<(), EventError> {
    let derived = &event.payload["derived"];
    let tags: Vec<String> = derived["tags"]
        .as_array()
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let summary = derived["summary"].as_str().map(String::from);
    let mood = derived["mood"].as_str().map(String::from);

    let note_id = event.payload["note_id"]
        .as_str()
        .unwrap_or(&event.aggregate_id)
        .to_string();
    let ts = event.timestamp.to_rfc3339();

    db.query(
        "UPDATE type::record('notes', $note_id) SET
            tags = $tags,
            summary = $summary,
            mood = $mood,
            updated_at = type::datetime($ts)",
    )
    .bind(("note_id", note_id))
    .bind(("tags", tags))
    .bind(("summary", summary))
    .bind(("mood", mood))
    .bind(("ts", ts))
    .await
    .map_err(|e| EventError::Projection(e.to_string()))?;

    Ok(())
}
```

The LLM processing result is stored as an event (`note_llm_processed`), which the projection then applies to the read table. This means the LLM's output is both an immutable event in the log and a materialized view in the notes table. If the LLM processing improves and notes need reprocessing, the old `note_llm_processed` events remain in the log as a record of what the previous model version produced.

#### Routines projection

The `RoutinesProjection` is more complex because it manages three read tables: `routine_groups`, `routine_items`, and `routine_completions`.

```rust
async fn apply(&self, event: &Event, db: &Database) -> Result<(), EventError> {
    match event.event_type.as_str() {
        "routine_group_created" => self.on_group_created(event, db).await,
        "routine_item_added" => self.on_item_added(event, db).await,
        "routine_item_completed" => self.on_item_completed(event, db).await,
        "routine_item_skipped" => self.on_item_skipped(event, db).await,
        "routine_group_modified" => self.on_group_modified(event, db).await,
        _ => Ok(()),
    }
}
```

A key design decision: daily reset is implicit. There is no "reset all completions" event at midnight. Instead, the UI queries completions filtered by today's date:

```sql
SELECT * FROM routine_completions WHERE date = '2026-03-30'
```

If no completions exist for today, all items show as incomplete. This eliminates the need for a scheduler or cron job to reset state --- the date filter handles it naturally. Completions for previous days remain in the table, providing a history of what was completed when.

The `on_group_modified` handler demonstrates a pattern for partial updates. The event payload contains a `changes` object with only the fields that changed, plus an optional `justification`:

```rust
async fn on_group_modified(&self, event: &Event, db: &Database) -> Result<(), EventError> {
    let group_id = event.payload["group_id"]
        .as_str()
        .unwrap_or(&event.aggregate_id)
        .to_string();

    let changes = &event.payload["changes"];
    if let Some(name) = changes.get("name").and_then(|v| v.as_str()) {
        let name = name.to_string();
        db.query(
            "UPDATE type::record('routine_groups', $group_id) SET name = $name",
        )
        .bind(("group_id", group_id.clone()))
        .bind(("name", name))
        .await
        .map_err(|e| EventError::Projection(e.to_string()))?;
    }
    // ... frequency, time_of_day handled similarly

    // Always update the updated_at timestamp
    db.query(
        "UPDATE type::record('routine_groups', $group_id) SET updated_at = type::datetime($ts)",
    )
    .bind(("group_id", group_id))
    .bind(("ts", ts))
    .await
    .map_err(|e| EventError::Projection(e.to_string()))?;

    Ok(())
}
```

Each changed field is applied individually. This is intentional --- the event records exactly what changed, and the projection applies exactly those changes. No guessing about default values or null fields.

#### Sync server endpoints

The server exposes two endpoints under `/sync`: push (device sends events to server) and pull (device requests events from server).

```rust
/// Request body for POST /sync/push
#[derive(Debug, Deserialize)]
pub struct PushRequest {
    pub device_id: String,
    pub events: Vec<NewEvent>,
}

/// Response for POST /sync/push
#[derive(Debug, Serialize)]
pub struct PushResponse {
    pub count: usize,
}

/// Request body for POST /sync/pull
#[derive(Debug, Deserialize)]
pub struct PullRequest {
    pub device_id: String,
    pub since: DateTime<Utc>,
}

/// Response for POST /sync/pull
#[derive(Debug, Serialize)]
pub struct PullResponse {
    pub events: Vec<Event>,
    pub sync_timestamp: DateTime<Utc>,
}
```

The push handler iterates over incoming events and appends each one. Failed individual appends are logged but do not fail the entire request --- partial success is acceptable because the idempotent append means the client can safely retry:

```rust
async fn push_handler(
    State(state): State<AppState>,
    Json(body): Json<PushRequest>,
) -> Json<PushResponse> {
    let store = SurrealEventStore::new((*state.db).clone());
    let mut count = 0;

    for event in body.events {
        match store.append(event).await {
            Ok(_) => count += 1,
            Err(e) => {
                tracing::warn!("failed to append event during push: {e}");
            }
        }
    }

    Json(PushResponse { count })
}
```

The pull handler uses the `exclude_device` parameter on `get_since` to filter out the requesting device's own events. The device already has those --- sending them back would be wasted bandwidth:

```rust
async fn pull_handler(
    State(state): State<AppState>,
    Json(body): Json<PullRequest>,
) -> Json<PullResponse> {
    let store = SurrealEventStore::new((*state.db).clone());

    let events = store
        .get_since(body.since, Some(&body.device_id))
        .await
        .unwrap_or_else(|e| {
            tracing::warn!("failed to get events during pull: {e}");
            vec![]
        });

    let sync_timestamp = Utc::now();

    Json(PullResponse {
        events,
        sync_timestamp,
    })
}
```

The `sync_timestamp` in the response is the server's current time at the moment of the pull. The client stores this and uses it as the `since` parameter for the next pull, ensuring no events are missed between syncs.

#### Sync client

The `SyncClient` lives in the core crate and performs a full sync cycle: pull remote events, then push local events.

```rust
pub struct SyncClient {
    server_url: String,
    device_id: String,
    http: reqwest::Client,
}
```

The `sync()` method implements the pull-then-push flow:

```rust
pub async fn sync(&self, db: &Database) -> Result<SyncResult, SyncError> {
    let store = SurrealEventStore::new(db.clone());
    let last_sync = self.get_last_sync_timestamp(db).await?;

    // 1. Pull remote events
    let pull_resp = self.pull_events(&last_sync).await?;
    let pulled = pull_resp.events.len();

    // 2. Append pulled events locally, preserving their server-assigned IDs
    for event in &pull_resp.events {
        let new_event = NewEvent {
            id: Some(event.id.clone()),
            event_type: event.event_type.clone(),
            aggregate_id: event.aggregate_id.clone(),
            timestamp: event.timestamp,
            device_id: event.device_id.clone(),
            payload: event.payload.clone(),
        };
        store
            .append(new_event)
            .await
            .map_err(|e| SyncError::Local(e.to_string()))?;
    }

    // 3. Update sync timestamp after successful pull (before push).
    let new_timestamp = pull_resp.sync_timestamp;
    self.update_last_sync_timestamp(db, &new_timestamp).await?;

    // 4. Gather local events since last sync (by this device only)
    let local_events = self.get_local_events_since(&store, &last_sync).await?;
    let pushed = local_events.len();

    // 5. Push local events to server
    if !local_events.is_empty() {
        self.push_events(&local_events).await?;
    }

    Ok(SyncResult {
        pulled,
        pushed,
        pulled_events: pull_resp.events,
    })
}
```

**Why pull-before-push matters.** If the client pushed first, the server's timestamp would advance past the new events. On the subsequent pull, those events would be excluded by the `since` filter. By pulling first, the client gets a clean `sync_timestamp` from the server, updates its local cursor, and then pushes. The server sees the push as new events that will be included in other devices' future pulls.

The `SyncResult` includes the `pulled_events` vector so the caller can feed those events through the `ProjectionRunner` to update local read tables:

```rust
#[derive(Debug)]
pub struct SyncResult {
    pub pulled: usize,
    pub pushed: usize,
    pub pulled_events: Vec<Event>,
}
```

The sync timestamp is stored locally per device in a `sync_state` table. On the first sync, when no `sync_state` record exists, the client uses epoch (`1970-01-01T00:00:00Z`) as the `since` parameter, pulling the entire event history.

---

### Phase 3: LLM Pipeline

#### Why LLM processing is server-side only

All LLM calls go through the server. The Tauri client never contacts Gemini directly. There are three reasons:

1. **API key security.** Embedding an API key in a mobile app binary is a non-starter.
2. **Reprocessing.** When prompts improve, the server can reprocess existing notes without requiring a client update.
3. **Resource constraints.** The phone should not be burning battery and bandwidth on LLM API calls when it can send a lightweight event to the server and let it handle the processing asynchronously.

#### Deterministic pre-processor

Before any note hits the LLM, it passes through a deterministic pre-processor. This stage extracts data that can be matched exactly with regex --- currently just URLs:

```rust
/// Result of deterministic pre-processing on raw text.
/// Only extracts data that requires exact matching (URLs).
/// Fuzzy data (dates, amounts, entities) is handled by the LLM.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PreprocessResult {
    pub urls: Vec<String>,
}

/// Run all deterministic pre-processing extractors on the given text.
pub fn preprocess(text: &str) -> PreprocessResult {
    PreprocessResult {
        urls: extract_urls(text),
    }
}
```

**Why pre-process before the LLM?** URLs need exact extraction. An LLM might hallucinate a URL or subtly alter one. The regex extractor pulls URLs verbatim and passes them to the prompt as pre-extracted context. The LLM does not need to extract URLs --- it just gets told what they are.

Dates, monetary amounts, and other fuzzy data are intentionally *not* pre-processed. The original design included regex extractors for dates and currencies, but those were removed. Phrases like "about 15 bucks," "next Tuesday," or "~R200" require interpretation that regex cannot do reliably. The LLM handles all fuzzy extraction via tool calling, which is covered below.

The `extract_urls` function handles edge cases like trailing punctuation and parenthesized URLs:

```rust
fn extract_urls(text: &str) -> Vec<String> {
    let re = Regex::new(r#"https?://[^\s\)\]>,;"']+"#).expect("valid url regex");
    re.find_iter(text)
        .map(|m| {
            let url = m.as_str();
            url.trim_end_matches(|c: char| matches!(c, '.' | '!' | '?' | ','))
                .to_string()
        })
        .collect()
}
```

#### LlmClient trait and GeminiClient

The `LlmClient` trait abstracts the LLM provider:

```rust
#[async_trait]
pub trait LlmClient: Send + Sync {
    /// Generate a plain text completion from the given prompt.
    async fn complete(&self, prompt: &str) -> Result<String, LlmError>;

    /// Generate a structured JSON completion conforming to the given JSON Schema.
    async fn complete_json(
        &self,
        prompt: &str,
        schema: &Value,
    ) -> Result<Value, LlmError>;

    /// Generate a completion that may include tool calls.
    async fn complete_with_tools(
        &self,
        prompt: &str,
        tools: &[ToolDef],
    ) -> Result<LlmResponse, LlmError>;
}
```

Three methods cover the three interaction patterns: plain text, structured JSON (using Gemini's `responseMimeType: "application/json"` with a schema), and tool calling. The trait is object-safe --- no generics --- so it can be used as `Box<dyn LlmClient>` or `&dyn LlmClient` throughout the codebase. Swapping Gemini for another provider means implementing this trait.

The `GeminiClient` implements this trait against the Gemini 2.0 Flash API (free tier). It includes built-in rate limiting:

```rust
const MIN_REQUEST_INTERVAL: Duration = Duration::from_millis(40);

pub struct GeminiClient {
    api_key: String,
    model: String,
    base_url: String,
    http: reqwest::Client,
    last_request: Arc<Mutex<Instant>>,
}
```

Every request checks the elapsed time since the last request. If less than 40ms has passed, the client sleeps for the difference. This prevents hitting Gemini's rate limit during batch processing (e.g., when processing multiple notes after a sync pull).

The tool definitions are converted to Gemini's `functionDeclarations` format before being sent:

```rust
fn tool_defs_to_gemini(tools: &[ToolDef]) -> Value {
    let declarations: Vec<Value> = tools
        .iter()
        .map(|t| {
            json!({
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            })
        })
        .collect();

    json!([{ "functionDeclarations": declarations }])
}
```

#### Tool calling framework

The tool calling framework defines tools as JSON Schema objects and parses the LLM's tool call responses into typed structs:

```rust
/// Definition of a tool that the LLM can call.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolDef {
    pub name: String,
    pub description: String,
    /// JSON Schema object describing the tool's parameters.
    pub parameters: Value,
}

/// A single tool call made by the LLM.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub name: String,
    pub arguments: Value,
}

/// Response from an LLM that may be plain text, tool calls, or structured JSON.
#[derive(Debug, Clone)]
pub enum LlmResponse {
    Text(String),
    ToolCalls(Vec<ToolCall>),
    Structured(Value),
}
```

The default tool set for note processing includes five tools:

```rust
pub fn default_note_tools() -> Vec<ToolDef> {
    vec![
        ToolDef {
            name: "create_tag".to_string(),
            description: "Create a tag for categorizing the note".to_string(),
            parameters: json!({
                "type": "object",
                "properties": {
                    "tag": { "type": "string", "description": "The tag name to apply" }
                },
                "required": ["tag"]
            }),
        },
        ToolDef {
            name: "extract_task".to_string(),
            description: "Extract an actionable task from the note".to_string(),
            parameters: json!({
                "type": "object",
                "properties": {
                    "description": { "type": "string", "description": "Description of the task" },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level of the task"
                    }
                },
                "required": ["description", "priority"]
            }),
        },
        // assess_mood, extract_date, extract_expense follow the same pattern
    ]
}
```

The LLM can call each tool as many times as needed in a single response. A journal entry mentioning three topics gets three `create_tag` calls. An entry mentioning a purchase and a bill gets two `extract_expense` calls. The `interpret_tool_calls` function collects all calls into a structured result:

```rust
fn interpret_tool_calls(response: LlmResponse) -> Result<ParsedToolCalls, PipelineError> {
    match response {
        LlmResponse::Text(text_response) => Ok(ParsedToolCalls {
            tags: vec![],
            mood: None,
            tasks: vec![],
            dates: vec![],
            expenses: vec![],
            summary: Some(text_response),
        }),
        LlmResponse::ToolCalls(tool_call_vec) => {
            let mut tags = Vec::new();
            let mut tasks = Vec::new();
            let mut dates = Vec::new();
            let mut expenses = Vec::new();
            let mut mood: Option<MoodAssessment> = None;

            for tc in tool_call_vec {
                match tc.name.as_str() {
                    "create_tag" => {
                        tags.push(require_str(&tc.arguments, "tag", "create_tag")?);
                    }
                    "assess_mood" => {
                        mood = Some(MoodAssessment {
                            mood: require_str(&tc.arguments, "mood", "assess_mood")?,
                            confidence: require_f64(
                                &tc.arguments, "confidence", "assess_mood"
                            )?,
                        });
                    }
                    // extract_task, extract_date, extract_expense handled similarly
                    _ => {} // Unknown tools are silently ignored
                }
            }

            Ok(ParsedToolCalls { tags, mood, tasks, dates, expenses, summary: None })
        }
        // ...
    }
}
```

If the LLM returns a plain text response instead of tool calls (which happens occasionally), it is captured as a `summary`. This is a graceful degradation --- no tags, mood, or tasks are extracted, but the response is not lost.

#### Prompt versioning

Every LLM call is tracked with metadata that records which prompt template and model produced the result:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CallMetadata {
    pub prompt_name: String,
    pub prompt_version: String,
    pub model: String,
    pub timestamp: chrono::DateTime<Utc>,
}
```

Prompts are defined as static templates with variable substitution:

```rust
pub static NOTE_PROCESS_V1: PromptTemplate = PromptTemplate {
    name: "note_process_v1",
    version: "2.0.0",
    template: "You are a personal life assistant. Analyze the following journal entry \
and use the provided tools to extract all relevant structured data. Call each tool as \
many times as needed.\n\nExtract:\n- Tags: topic categories (use create_tag for each)\n\
- Mood: overall emotional tone (use assess_mood once)\n- Tasks: any actionable items \
mentioned (use extract_task for each)\n- Dates: any dates or time references ... \
(use extract_date for each)\n- Expenses: any spending, costs, or financial amounts ... \
(use extract_expense for each)\n\nPre-extracted URLs (exact matches): {urls}\n\n\
Journal entry:\n{raw_text}",
    description: "Process a journal entry to extract tags, mood, tasks, dates, and expenses",
};
```

The `PromptRegistry` manages named templates and renders them against a JSON context:

```rust
pub struct PromptRegistry {
    templates: HashMap<&'static str, PromptTemplate>,
}

impl PromptRegistry {
    pub fn render(&self, name: &str, context: &serde_json::Value) -> Result<String, LlmError> {
        let template = self.get(name).ok_or_else(|| {
            LlmError::ParseError(format!("Unknown template: {name}"))
        })?;

        let ctx_map = context.as_object().ok_or_else(|| {
            LlmError::ParseError("Render context must be a JSON object".to_string())
        })?;

        let mut result = template.template.to_string();
        for (key, value) in ctx_map {
            let placeholder = format!("{{{{{key}}}}}");
            let replacement = match value {
                serde_json::Value::String(s) => s.clone(),
                serde_json::Value::Null => "".to_string(),
                other => other.to_string(),
            };
            result = result.replace(&placeholder, &replacement);
        }

        Ok(result)
    }
}
```

The metadata is stored inside the `note_llm_processed` event as `prompt_version: "note_process_v1@2.0.0"`. If the prompt is updated to version 3.0.0 later, all notes processed with 2.0.0 are identifiable and can be selectively reprocessed.

#### Note processing pipeline

The full pipeline ties everything together. The `process_note` function is the entry point:

```rust
pub async fn process_note(
    note_id: &str,
    raw_text: &str,
    device_id: &str,
    llm: &dyn LlmClient,
    event_store: &dyn EventStore,
) -> Result<NoteProcessingResult, PipelineError> {
    // Step 1: Deterministic pre-processing (URLs only)
    let preprocessed = preprocess::preprocess(raw_text);

    // Step 2: Build prompt from template
    let registry = PromptRegistry::new();
    let context = json!({
        "urls": preprocessed.urls,
        "raw_text": raw_text,
    });
    let prompt = registry.render("note_process_v1", &context)?;

    // Step 3: Call LLM with tools
    let tools = default_note_tools();
    let response = llm.complete_with_tools(&prompt, &tools).await?;

    // Step 4: Parse tool calls into structured result
    let result_data = interpret_tool_calls(response)?;

    // Step 5: Emit note_llm_processed event
    let payload = NoteLlmProcessedPayload {
        note_id: note_id.to_string(),
        prompt_version: format!("{}@{}", template.name, template.version),
        model: model_name.to_string(),
        derived,
    };

    event_store
        .append(NewEvent {
            id: None,
            event_type: EventType::NoteLlmProcessed.to_string(),
            aggregate_id: note_id.to_string(),
            timestamp: Utc::now(),
            device_id: device_id.to_string(),
            payload: serde_json::to_value(&payload)?,
        })
        .await?;

    Ok(result)
}
```

The result struct captures everything the pipeline extracted:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NoteProcessingResult {
    pub tags: Vec<String>,
    pub mood: Option<MoodAssessment>,
    pub tasks: Vec<ExtractedTask>,
    pub dates: Vec<ExtractedDate>,
    pub expenses: Vec<ExtractedExpense>,
    pub summary: Option<String>,
    pub urls: Vec<String>,
    pub metadata: CallMetadata,
}
```

The pipeline closes the loop: a `note_created` event triggers LLM processing, which produces a `note_llm_processed` event, which the `NotesProjection` applies to update the notes read table with tags, mood, and summary. The event log captures the full history --- the original text, the LLM's interpretation, and the metadata about which model and prompt version produced that interpretation.

---

### Gotchas

1. **`SurrealValue` derive needed for `.take()`** --- SurrealDB v3 query results require structs to derive `SurrealValue`, not just serde's `Deserialize`. The `EventRow` struct in the event store uses `#[derive(Debug, SurrealValue)]` with `surrealdb::types::SurrealValue`. Attempting to use `#[derive(Deserialize)]` alone compiles fine but fails at runtime when calling `.take()` on the query response.

2. **`surrealdb::types::Value` with `into_json_value()` for flexible payload fields** --- The `EventRow` stores the payload as `surrealdb::types::Value` (SurrealDB's native value type), not `serde_json::Value`. To convert it to JSON for the `Event` struct, you call `.into_json_value()`. Attempting to store the payload directly as `serde_json::Value` in a `SurrealValue`-derived struct causes a type mismatch. The correct pattern is:
    ```rust
    #[derive(Debug, SurrealValue)]
    struct EventRow {
        // ...
        payload: DbValue,  // surrealdb::types::Value
    }

    impl TryFrom<EventRow> for Event {
        fn try_from(row: EventRow) -> Result<Self, Self::Error> {
            let payload = row.payload.into_json_value();
            // ...
        }
    }
    ```

3. **`type::record()` replaces `type::thing()`** --- SurrealDB v3 renamed `type::thing()` to `type::record()`. All SurrealQL queries that create or reference specific records use `type::record('table', $id)`. If you are following v2 tutorials or documentation, search-and-replace `type::thing` with `type::record`.

4. **`surrealdb-core` compilation OOMs with parallel builds on less than 8GB RAM** --- The SurrealDB core crate is extremely memory-intensive to compile. On machines with less than 8GB of RAM, parallel compilation can cause an out-of-memory kill. The workaround is to limit Cargo to sequential compilation: set `CARGO_BUILD_JOBS=1` as an environment variable, or add `[build] jobs = 1` to `.cargo/config.toml`. CI environments with shared runners are especially susceptible to this.
