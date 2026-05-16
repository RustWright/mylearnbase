+++
title = "Four Code Reviews After Cycle 1"
slug = "post-cycle-code-reviews"
aliases = ["/posts/post-cycle-code-reviews/"]
date = 2026-04-15
draft = false

[taxonomies]
tags = ["code-review", "rust", "event-sourcing", "tauri", "security", "performance", "wasm", "omni-me"]
series = ["Building omni-me"]

[extra]
series_order = 5
+++

## Reflections

I honestly didn't think these code reviews would take this long or go this deep. I expected a few quick fixes, but instead it spanned several days, several maxed-out Claude sessions, and a lot of learning in between.

A recurring theme in my recent reflections is the tension between wanting to slow down, to actually learn, understand, and stay connected to my own codebase, and the pull to get the complete app out as quickly as possible. I keep imagining how useful it will be and wanting to get there sooner rather than later.

That said, taking the time to identify these issues and work through them slowly was genuinely valuable. It's become another tool in my approach as someone with very little professional coding experience trying to design and build ambitious projects outside my comfort zone. I'd like to keep up this habit, though the reviews themselves are expensive; the codebase is large enough that generating the initial review documents takes significant time and tokens.

Ideally, after a few more of these, I can run a meta-review to spot recurring patterns and things I can learn to control for before they happen, rather than catching them after the fact. I already export a log from every Claude session, and I plan to use those to identify recurring issues in my workflow and find ways to improve my [dev setup](@/posts/archive/2026-02-24-dev-setup-from-scratch.md).

But that's a project for later. Right now I want to get omni-me to the point where I'm comfortable switching from Obsidian to it for daily note-taking. I'm also looking forward to building a custom budgeting tool for tracking where my money goes and setting better goals. Until I have a working app, though, I don't think I'll be able to focus on anything else.

---

## Tutorial: Systematic Code Reviews for a Rust Project

The first four posts in this series followed a fast-paced MVP sprint: validate the stack, build infrastructure, wire up event sourcing and sync, build the UI, ship an Android APK. Cycle 1 was done. The codebase worked. But "works" and "works well" are different things, and after three weeks of building at maximum velocity with an AI coding assistant, there was a real question: what got missed?

Instead of jumping into Cycle 2 features, I paused to run four focused code reviews across the entire codebase. Each review targeted a specific dimension: security, performance, bloat and complexity, and logical inconsistencies. The process was interactive --- the AI generated an initial review document, then I went through every finding one by one, discussing each before deciding whether to fix it, defer it, or keep it as-is.

This tutorial walks through the methodology, highlights the most interesting findings and fixes, and distills the patterns that emerged.

### The review methodology

#### Why four separate reviews instead of one

A single "code review" tends to drift. You start looking at security, notice a performance issue, chase that down a refactoring rabbit hole, and end up with a scattered list of unrelated observations. Separating reviews by dimension creates focus. Each pass has a different lens:

- **Security:** What can an attacker do? What data leaks? What inputs are untrusted?
- **Performance:** What is unnecessarily slow or resource-heavy? What scales poorly?
- **Bloat and complexity:** What code exists but serves no purpose? What is over-engineered?
- **Logical inconsistencies:** Where do invariants break? Where does the code contradict its own design?

Each lens catches things the others miss. More importantly, findings from one review compound with findings from another --- a theme I'll return to later.

#### The fix/defer/keep framework

Not every finding needs to be fixed immediately. For each issue, I chose one of three dispositions:

- **Fix:** Address it now. The issue is either critical (security) or cheap enough that deferring creates more overhead than fixing.
- **Defer:** Acknowledge the issue, document why it is acceptable for now, and record the trigger condition for revisiting it. For example: "CORS is permissive, acceptable behind Tailscale, revisit when deploying to public VPS."
- **Keep:** The code is intentional. The finding is valid from the reviewer's perspective, but upon discussion it turns out the design was deliberate.

This framework prevents two failure modes: fixing everything (perfectionism that kills velocity) and ignoring everything (tech debt that compounds silently).

---

### Review 1: Security (8 findings)

The security review produced the most immediately critical fixes.

#### API key leaked in error responses

The most severe finding was a classic information disclosure bug. When an HTTP request to the Gemini API failed, the `reqwest` error included the full URL --- which contained the API key as a query parameter.

```rust
// BEFORE: reqwest error includes the full URL
let response = self.client
    .post(&url)
    .json(&request)
    .send()
    .await
    .map_err(|e| LlmError::RequestFailed(e.to_string()))?;
```

The error message would contain something like `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIza...`. This string would flow into logs, error responses, and potentially the UI.

The fix uses `reqwest`'s `.without_url()` method to strip the URL from the error before converting it to a string:

```rust
// AFTER: URL stripped from error
let response = self.client
    .post(&url)
    .json(&request)
    .send()
    .await
    .map_err(|e| LlmError::RequestFailed(
        e.without_url().to_string()
    ))?;
```

One method call. The kind of thing that is obvious in hindsight but easy to miss when you're focused on getting the happy path working.

#### No payload validation on sync push

The sync push endpoint accepted whatever JSON was posted to it and appended it directly to the event store. There was no validation that the events had required fields, that the event types were recognized, or that the payload size was bounded.

This was actually three separate fixes:

1. **Payload validation.** A `validate_payload()` function checks that each event in a push request has a valid `event_type` (matched against the `EventType` enum), a non-empty `device_id`, and well-formed metadata.

2. **Size limits.** A 256KB maximum request body size and a 100 events per push cap prevent resource exhaustion. The client-side sync code was updated to chunk large batches accordingly.

3. **Atomic batch appending.** The original push handler called `append()` in a loop. If the fifth event out of ten failed, you'd have a partial write with no way to recover. The fix replaced this with an `append_batch` function that wraps the entire operation in a SurrealDB transaction:

```rust
pub async fn append_batch(
    db: &Surreal<Any>,
    events: &[Event],
) -> Result<(), EventStoreError> {
    let mut query = String::from("BEGIN TRANSACTION;\n");

    for event in events {
        query.push_str(&format!(
            "CREATE type::record('events', '{}') CONTENT {{
                event_type: '{}',
                device_id: '{}',
                payload: {},
                created_at: '{}'
            }};\n",
            event.id, event.event_type, event.device_id,
            serde_json::to_string(&event.payload)?,
            event.created_at,
        ));
    }

    query.push_str("COMMIT TRANSACTION;");
    db.query(query).await?;
    Ok(())
}
```

A note on SurrealDB transactions: the Rust SDK doesn't expose a session-level `db.begin()` / `db.commit()` API like traditional SQL databases. Instead, you wrap statements between `BEGIN` and `COMMIT` keywords. The SDK supports two approaches: composing a single multi-statement query string, or chaining `.query()` calls for better readability:

```rust
// Chained approach — each .query() appends to the same execution
db.query("BEGIN TRANSACTION")
    .query("CREATE account:one SET balance = 100")
    .query("UPDATE account:one SET balance += 50")
    .query("COMMIT TRANSACTION")
    .await?;
```

Our implementation builds the query string dynamically because each event needs unique parameter bindings (`$id_0`, `$id_1`, etc.), but for simpler cases the chaining approach is cleaner.

---

### Review 2: Performance (18 findings)

The performance review had the highest volume of findings. Most were small optimizations, but a few represented genuine algorithmic improvements.

#### Per-event, per-projection database updates

The projection rebuild system had an `apply_events()` function that, after applying each event, updated the `last_event_id` for every projection. With N events and P projections, this was N * P database writes just for bookkeeping:

```rust
// BEFORE: O(N*P) database writes
for event in &events {
    for projection in &self.projections {
        projection.apply(db, event).await?;
        self.update_last_event_id(db, projection.name(), &event.id).await?;
    }
}
```

The fix moves the checkpoint update to after the entire batch:

```rust
// AFTER: O(P) database writes for bookkeeping
for event in &events {
    for projection in &self.projections {
        projection.apply(db, event).await?;
    }
}
// Single update per projection after all events processed
for projection in &self.projections {
    if let Some(last_id) = last_event_ids.get(projection.name()) {
        self.update_last_event_id(db, projection.name(), last_id).await?;
    }
}
```

This is not a subtle optimization. For a projection rebuild of 500 events across 2 projections, it reduces bookkeeping writes from 1,000 to 2.

#### Regex compiled on every call

URL extraction from note text used `Regex::new()` inside the function body. Since the regex pattern is constant, this recompilation on every call is pure waste:

```rust
// BEFORE: compiled on every call
fn extract_urls(text: &str) -> Vec<String> {
    let re = Regex::new(r"https?://[^\s<>\]\)]+").unwrap();
    re.find_iter(text).map(|m| m.as_str().to_string()).collect()
}
```

The standard Rust pattern for this is `LazyLock` (stabilized in Rust 1.80):

```rust
// AFTER: compiled once, reused forever
use std::sync::LazyLock;

static URL_REGEX: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"https?://[^\s<>\]\)]+").unwrap()
});

fn extract_urls(text: &str) -> Vec<String> {
    URL_REGEX.find_iter(text).map(|m| m.as_str().to_string()).collect()
}
```

`LazyLock` initializes on first access and is safe to share across threads. Before its stabilization, the common alternative was the `lazy_static!` macro or `once_cell::sync::Lazy`, which `LazyLock` was modeled after.

#### Filtering in Rust instead of SQL

The sync pull handler fetched all events from a device and then filtered by timestamp in Rust:

```rust
// BEFORE: fetch everything, filter in Rust
let all_events: Vec<Event> = db.select("events").await?;
let filtered: Vec<Event> = all_events
    .into_iter()
    .filter(|e| e.device_id == device_id && e.created_at > since)
    .collect();
```

Replaced with a parameterized query that filters at the database layer:

```rust
// AFTER: filter at the database
let events: Vec<Event> = db.query(
    "SELECT * FROM events WHERE device_id = $device_id AND created_at > $since ORDER BY created_at"
)
    .bind(("device_id", device_id))
    .bind(("since", since))
    .await?
    .take(0)?;
```

This matters less at the current scale (hundreds of events) but would become a real problem as the event store grows.

---

### Review 3: Bloat and Complexity (19 findings)

This review focused on unnecessary code, redundant abstractions, and over-engineering. It also produced the most interesting discussions about what is "intentional complexity" versus actual bloat.

#### Replacing hand-written error types with thiserror

The codebase had five error types, each with manual `Display` and `Error` trait implementations. Around 80 lines of boilerplate:

```rust
// BEFORE: manual impl for every error type
#[derive(Debug)]
pub enum DbError {
    Connection(String),
    Query(String),
    NotFound(String),
}

impl std::fmt::Display for DbError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Connection(msg) => write!(f, "Database connection error: {msg}"),
            Self::Query(msg) => write!(f, "Database query error: {msg}"),
            Self::NotFound(msg) => write!(f, "Not found: {msg}"),
        }
    }
}

impl std::error::Error for DbError {}

// No source() implementation — error chain information is lost
```

With `thiserror`, each error type becomes a derive macro:

```rust
// AFTER: thiserror derives
use thiserror::Error;

#[derive(Debug, Error)]
pub enum DbError {
    #[error("Database connection error: {0}")]
    Connection(String),

    #[error("Database query error: {0}")]
    Query(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("SurrealDB error")]
    Surreal(#[from] surrealdb::Error),
}
```

The reduction in lines is nice, but the real win is the `#[from]` attribute. It generates two things: a `From<surrealdb::Error>` impl (so you can use `?` to convert errors automatically) and a `.source()` implementation that returns a reference to the wrapped error. The hand-written code was not implementing `.source()` at all, which meant error chain information was silently lost. Any logging or debugging tool that walks the `.source()` chain would hit a dead end at these error types.

#### The EventType debate

The `EventType` enum had 44 lines of manual `Display` and `FromStr` implementations. The initial finding flagged this as over-engineering --- why not just use `serde`'s built-in string serialization?

During discussion, it became clear this was intentional. The security review had just wired `EventType` into `validate_payload()`: incoming sync events are checked against the enum to reject unrecognized types. The architecture uses a layered approach --- strict validation at ingestion (the enum must match), but permissive handling at projection (unknown event types are silently skipped). This means new event types can be added to one device before the other device's code is updated, without breaking sync.

This was the clearest example of the Keep disposition. The code looked like bloat from one angle but served a real architectural purpose that only became visible in context.

#### Consolidating duplicate type definitions

The sync protocol types (`PushRequest`, `PushResponse`, `PullRequest`, `PullResponse`) were defined in three places: `core/src/sync/mod.rs`, `server/src/routes/sync.rs`, and `tauri-app/src-tauri/src/commands/sync.rs`. Each copy had slightly different field names and derive macros.

The fix moved the canonical definitions to `core/src/sync/mod.rs` and had the server and Tauri backend crate import from there. The frontend copy had to stay separate --- the Dioxus frontend compiles to `wasm32-unknown-unknown` in its own workspace, so it can't import from the core crate directly. That duplication is structural, not laziness. But the three backend copies had no such excuse and were already starting to drift.

---

### Review 4: Logical Inconsistencies (11 findings)

The final review looked for places where the code contradicted its own design assumptions. This produced the most complex fix in the entire review process.

#### Non-deterministic projection rebuilds

Projection handlers were generating random ULIDs for completion records:

```rust
// BEFORE: random ID breaks rebuild idempotency
fn handle_routine_completed(db: &Surreal<Any>, event: &Event) -> Result<()> {
    let completion_id = ulid::Ulid::new().to_string();
    db.query("CREATE type::record('completions', $id) CONTENT { ... }")
        .bind(("id", completion_id))
        .await?;
    Ok(())
}
```

In an event-sourced system, projections must be deterministic functions of the event stream. If you rebuild projections by replaying events, random IDs mean every rebuild creates different records, causing duplicate completions (or errors from ID collisions, depending on the insert strategy).

The fix derives the completion ID from the event ID:

```rust
// AFTER: deterministic ID derived from event
let completion_id = format!("comp-{}", event.id);
```

Now replaying the same event always produces the same completion record. Rebuilds are idempotent.

#### LLM results not synced back to local projections

This was the most involved fix. When a note was processed through the LLM pipeline, the server would call Gemini, parse the tool-call results, create new events (tags extracted, summary generated, etc.), and append them to the event store. But these new events were never replayed through the local projections on the server.

The result: the LLM would correctly extract tags from a note, the events would be stored, but if you queried the note's tags from the server immediately after processing, you'd get nothing. The projections hadn't seen the new events. The tags would only appear after the next sync cycle pulled them down and triggered a projection rebuild.

The fix added a `sync_back_after_llm()` function that replays the newly created events through the local projections immediately after LLM processing. But there's a design subtlety: what if this replay fails? The LLM processing itself succeeded --- the events are stored, the user's note was processed. Failing the entire request because the local projection update hiccuped would be wrong.

This led to implementing a **warnings-in-result pattern**:

```rust
#[derive(Serialize)]
pub struct ProcessNoteResponse {
    pub success: bool,
    pub events_created: usize,
    pub warnings: Vec<String>,
}

pub async fn process_note_llm(
    db: &Surreal<Any>,
    note_id: &str,
    gemini: &GeminiClient,
) -> Result<ProcessNoteResponse, LlmError> {
    // ... LLM processing, event creation ...

    let mut warnings = Vec::new();

    // Sync back to local projections — non-fatal
    if let Err(e) = sync_back_after_llm(db, &new_events).await {
        warnings.push(format!(
            "LLM processing succeeded but local sync failed: {e}. \
             Data will appear after next sync cycle."
        ));
    }

    Ok(ProcessNoteResponse {
        success: true,
        events_created: new_events.len(),
        warnings,
    })
}
```

On the frontend, non-empty warnings render as a yellow banner below the success message. The user always sees their LLM results; sync issues are surfaced as actionable information rather than being silently swallowed or causing a false failure.

This pattern sits between Rust's standard `Result<T, E>` (which forces binary success/failure) and silently ignoring errors. It's useful whenever you have a primary operation that succeeded plus a secondary operation that might fail independently.

#### The timezone problem

All eight `Utc::now()` calls in the frontend used UTC for user-facing dates. For someone in UTC+2, a note created at 11:00 PM local time would be stamped as 1:00 AM the next day in UTC. The journal page would file it under the wrong date.

The fix was comprehensive. On the backend, the server auto-detects the system timezone using the `iana-time-zone` crate, persists it to a file, and exposes get/update commands through Tauri. On the frontend, a `UserDate` newtype wraps all date construction:

```rust
use chrono_tz::Tz;

/// A date that is always in the user's local timezone.
/// All constructors require a &Tz, making it impossible
/// to accidentally use UTC for display dates.
pub struct UserDate(chrono::NaiveDate);

impl UserDate {
    pub fn today(tz: &Tz) -> Self {
        let now = chrono::Utc::now().with_timezone(tz);
        Self(now.date_naive())
    }

    pub fn from_ymd(year: i32, month: u32, day: u32, _tz: &Tz) -> Self {
        Self(chrono::NaiveDate::from_ymd_opt(year, month, day)
            .expect("invalid date"))
    }
}
```

The key design choice is that `UserDate` constructors require a `&Tz` parameter even when they don't use it computationally (like `from_ymd`). This is a deliberate API decision: it makes the timezone dependency visible at every call site, so a developer cannot construct a `UserDate` without having resolved the timezone first.

The timezone is stored in a Dioxus `Signal<Tz>` at the app level. When the user changes their timezone in Settings, every page that uses `UserDate` reactively updates. The `chrono-tz` crate was chosen specifically because it is pure Rust and compiles to WASM without issues --- a critical requirement for the Dioxus frontend.

---

### Patterns and takeaways

#### Cross-review synergies

Findings from different reviews reinforced each other in unexpected ways:

- The security review added payload validation using the `EventType` enum. The bloat review then flagged `EventType` as over-engineered dead code. During discussion, the security fix proved it was neither dead nor bloat --- it was load-bearing.
- The security review identified the need for atomic batch appending. The performance review independently found that the per-event append loop was wasteful. The fix (transaction-wrapped batch operations) satisfied both concerns simultaneously.
- The bloat review consolidated duplicate type definitions. The logical consistency review found that the drift between those duplicates was already causing subtle serialization differences.

Running reviews in sequence, with each building on the previous one's findings, produces better results than running them independently.

#### Type-level enforcement over convention

The `UserDate` newtype is a textbook example of making invalid states unrepresentable. The alternative --- adding a comment that says "always use the user's timezone, not UTC" --- is a convention. Conventions are violated. Type constraints are enforced by the compiler.

The same principle appears in the `EventType` validation: instead of trusting that sync clients will only send valid event types (a convention), the push handler rejects unrecognized types at ingestion (enforcement).

#### Event sourcing correctness requires determinism

Random generation inside projection handlers (ULIDs, timestamps, UUIDs) breaks the fundamental contract of event sourcing: that replaying the same events produces the same state. Any value that appears in projected state must be either (a) copied from the event payload or (b) derived deterministically from event data.

This is easy to state as a rule, but easy to violate in practice. `Ulid::new()` and `Utc::now()` are convenient, and they work fine until the first rebuild. The discipline is to treat every projection handler as a pure function of its input event.

#### When to keep "problematic" code

Not every finding is a bug. The `EventType` enum, `Closure::forget()` for wasm-bindgen callbacks, and the idempotent INSERT pattern in SurrealDB were all flagged as potential issues. All three were kept after discussion revealed they were intentional. The value was not in changing the code but in documenting *why* it exists --- future-me (or a future contributor) now has rationale, not just implementation.

---

### The numbers

Across all four reviews:

| Disposition | Count | Percentage |
|---|---|---|
| Fixed | 28 | 50% |
| Deferred | 18 | 32% |
| Kept | 10 | 18% |
| **Total** | **56** | **100%** |

Half the findings were fixed immediately. A third were documented deferrals with clear trigger conditions. The remaining fifth were confirmed as intentional architecture.

The most impactful fixes by category:

- **Security:** API key leak, payload validation, atomic transactions
- **Performance:** Projection checkpoint batching, static regex, SQL-layer filtering
- **Bloat:** thiserror conversion, type consolidation
- **Logical consistency:** Deterministic IDs, LLM sync-back, timezone system

---

### Running your own structured reviews

If you want to apply this process to your own project:

1. **Pick your dimensions.** Security, performance, bloat, and logical consistency worked for this codebase. A web frontend might substitute "accessibility" for "logical consistency." A library might add "API ergonomics."

2. **One dimension at a time.** Resist the urge to combine. The focus of a single lens is what catches things a general review misses.

3. **Decide before fixing.** For every finding, explicitly choose fix, defer, or keep. Write down the rationale. "Defer" without a documented trigger condition is just "ignore."

4. **Review in sequence, not in parallel.** Later reviews benefit from earlier fixes. The security fixes informed the bloat review. The performance fixes enabled the consistency review.

5. **Budget time for discussion.** The value is not in the list of findings --- it is in understanding each one well enough to make a confident disposition decision. Going slowly through findings is not inefficiency; it is where the learning happens.
