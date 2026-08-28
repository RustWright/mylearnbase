+++
title = "Splitting a personal app into a public engine and a private overlay"
slug = "open-core-split"
date = 2026-08-28
draft = true

[taxonomies]
tags = ["architecture", "open-source", "privacy", "extensibility"]
+++

## What does this feature do?

omni-me is one application distributed across two repositories. The public one is the
whole app — journal, notes, routines, double-entry finances, the sync server, the Android
and desktop clients. What it does not contain is any code that knows the name of a bank.
Clone it, build it, run it, and it comes up as a working application with no configured
import sources and an empty account roster: nothing panics, nothing is stubbed, and the
test suite is the engine's own rather than a redacted subset of a larger one.

The institution-specific half lives in a separate private repository that depends on the
public one — never the reverse. It supplies concrete import drivers for real accounts and
the deployment configuration for one person's servers. That the dependency points one way
is the whole design: the public engine cannot be missing a piece the overlay supplies,
because the public engine never asks the overlay for anything.

The join between them is a seam of exactly one type. The server's entry point accepts a
caller-supplied factory that builds import sources out of the engine's runtime handles,
and calls it once at boot. The public binary passes a factory that reads a config file;
the private binary passes one that also constructs real bank adapters. Database,
projections, HTTP routes, the scheduler, the review inbox — all of it is the same code
running in both.

The public engine is bank-free, not import-free. It ships three generic source kinds: a
CSV reader, a REST poller, and a subprocess runner that shells out to an external helper
program and talks to it in one line of JSON. That last one is the extension point. A
driver for any institution is just a program that speaks the protocol — the engine spawns
it, sends a verb, and takes back transaction drafts. It never sees a credential, because
the helper reads its own.

## Why was it added now?

The project is a personal system, but it is also the subject of writing, and every feature
written about is described from a repository a reader can open. That only works if the
repository can in fact be opened. While import drivers for real accounts sat in the tree,
it could not be: the code named institutions, the fixtures named accounts, and a
credentials file sat one `.gitignore` line away from permanent history.

The split was scheduled ahead of the server deployment rather than after it, and that
ordering was the point rather than a convenience. A deployment pipeline's shape depends on
which artifact it deploys. If the container image builds from the public repository, the
workflow can live in the open and the box runs a generic engine; if it builds from the
overlay, the workflow has to live where the secrets already are. Designing the pipeline
first would have meant designing it against an undecided topology.

It was also treated as a one-way door. Moving code between repositories is easy; moving
*history* is not, and a repository that has once been public has been public. So the cut
was taken early — before daily use came to depend on the arrangement, and before anything
had been published from it — while getting the boundary wrong still cost only work.

## What's in scope (and what's not)?

In scope: relocating the bank adapters and their vendor driver out of the public tree; the
composition-root seam that replaced the function which used to build sources directly from
a credentials file; a public engine that boots with no configuration at all; a frozen
engine-to-helper subprocess protocol; three generic source kinds declared in a server-side
config file and editable from inside the app; interactive re-authentication, split so that
the code tracking *that* a source needs a new session is public while the code that knows
*how* to log in is private; and a neutral fictional account roster across every public
artifact — the engine's own mock data, the project trackers, and the already-published
posts.

Not in scope:

- **The private half is not shown here, and cannot be.** Every claim in this post about
  the overlay is a claim about something unpublished. What is checkable is the public
  side: that it builds, tests and runs with the overlay absent.
- **The boundary is guarded, not enforced.** A pre-commit hook scans staged additions
  against a gitignored pattern list. It runs on one machine, is skippable with
  `--no-verify`, and does nothing at all in a clone. It is a tripwire against
  absent-mindedness rather than a control.
- **Third-party plugins are a claim, not a demonstration.** The subprocess protocol is
  documented and frozen and the engine's side is tested against fake helpers, but no
  helper written by anyone else has ever run against it.
- **Nothing here is a licensing or governance position.** "Open core" describes where the
  code sits, not a product model — there is one user, and the private half is private
  because it holds one person's bank details, not because it is the paid tier.

## How do we know it works?

```bash
cargo test -p omni-me-core -p omni-me-server 2>&1 \
  | grep -E '^ +(Running|Doc-tests)|^test result:' \
  | sed -E 's/ \(target.*\)//; s/ 0 measured.*//'
```

```output
     Running unittests src/lib.rs
test result: ok. 617 passed; 0 failed; 1 ignored;
     Running tests/extraction_integration.rs
test result: ok. 0 passed; 0 failed; 5 ignored;
     Running tests/golden_reconcile.rs
test result: ok. 2 passed; 0 failed; 0 ignored;
     Running unittests src/lib.rs
test result: ok. 2 passed; 0 failed; 0 ignored;
     Running unittests src/main.rs
test result: ok. 0 passed; 0 failed; 0 ignored;
     Running tests/auth_integration.rs
test result: ok. 9 passed; 0 failed; 0 ignored;
     Running tests/blob_headers_integration.rs
test result: ok. 1 passed; 0 failed; 0 ignored;
     Running tests/sync_client_integration.rs
test result: ok. 6 passed; 0 failed; 0 ignored;
     Running tests/sync_integration.rs
test result: ok. 5 passed; 0 failed; 0 ignored;
     Running tests/sync_phase2_integration.rs
test result: ok. 1 passed; 0 failed; 0 ignored;
     Running tests/updates_integration.rs
test result: ok. 2 passed; 0 failed; 0 ignored;
   Doc-tests omni_me_core
test result: ok. 0 passed; 0 failed; 0 ignored;
   Doc-tests omni_me_server
test result: ok. 0 passed; 0 failed; 0 ignored;
```

Eleven test binaries, two empty doc-test runs, 645 passing tests — in a tree that contains
no bank adapter at all. The count matters less than the spread. Both `src/lib.rs` entries
are unit suites: the first is the domain core, whose 617 tests cover the event store and
its projections, ledger parsing and balance arithmetic, the budget engine, the query
layer, and every generic import source; the second is the server's own. `golden_reconcile`
is the single end-to-end guard on the money chain, taking a synthetic journal all the way
from parse through projection to computed balances. The three `sync_*` targets stand up a
real server and exchange events between two simulated devices, with one of the three
killing the server mid-flight to watch the queue retry and recover. The rest cover the
authenticated route surface, attachment-blob headers, and the app-update route.

The six skipped tests are the honest part of the picture. Five of them need a live model
endpoint, and the one ignored test in the core library needs a real mailbox and
credentials. Both are marked and left in the tree rather than deleted — a test that cannot
run unattended still records what was checked by hand.

```bash
cargo tree -p omni-me-server --depth 1 | sed "s#$PWD#.#"
```

```output
omni-me-server v0.1.0 (./server)
├── axum v0.8.8
├── chrono v0.4.44
├── infer v0.19.0
├── omni-me-core v0.1.0 (./core)
├── serde v1.0.228
├── serde_json v1.0.149
├── sha2 v0.10.9
├── thiserror v2.0.18
├── tokio v1.50.0
├── tower-http v0.6.8
├── tracing v0.1.44
├── tracing-subscriber v0.3.23
└── ulid v1.2.1
[dev-dependencies]
├── reqwest v0.12.28
└── tempfile v3.27.0
```

The split's central claim is about direction — the overlay depends on the engine, and the
engine depends on nothing private — and direction is not something to argue about, because
it is in the dependency graph. Thirteen direct dependencies: twelve public crates from
crates.io, and one path dependency pointing at `./core`, which is inside this same
repository. No git dependency, no private registry, no vendored source, nothing behind
credentials. A clone has everything it needs because there is nothing else to have.

```bash
cargo test -p omni-me-core --features auto-import --lib -- --test-threads=1 auto_import::subprocess:: 2>&1 | sed -n '/^running /,$p' | sed 's/ 0 measured.*//'
```

```output
running 10 tests
test auto_import::subprocess::tests::missing_command_is_not_configured ... ok
test auto_import::subprocess::tests::pull_maps_error_status_to_upstream_message ... ok
test auto_import::subprocess::tests::pull_needs_reauth_status_yields_needs_reauth_error ... ok
test auto_import::subprocess::tests::pull_projects_drafts_from_helper ... ok
test auto_import::subprocess::tests::pull_with_terse_ok_response_appends_nothing ... ok
test auto_import::subprocess::tests::reauth_error_status_carries_message ... ok
test auto_import::subprocess::tests::reauth_invalid_otp_status_yields_invalid_otp ... ok
test auto_import::subprocess::tests::reauth_ok_status_yields_active ... ok
test auto_import::subprocess::tests::reauth_sends_reauth_verb_with_otp_on_stdin ... ok
test auto_import::subprocess::tests::run_helper_sends_pull_verb_on_stdin ... ok

test result: ok. 10 passed; 0 failed; 0 ignored;

```

Where the bank adapters used to be, there is now a protocol, and these ten tests are its
engine-side half. Four are about the wire itself: that a scheduled tick leaves as exactly
`{"verb":"pull"}` on the helper's stdin, that a re-authentication carries its one-time
code in the same tagged shape, that a terse `{"status":"ok"}` still deserializes and
appends nothing, and that a source with no command configured reports itself unconfigured
instead of trying to spawn. Five map the helper's reported status onto the engine's own
error and authentication states — an expired session becomes a re-auth requirement rather
than a generic failure, a rejected code becomes a distinct `invalid_otp` outcome rather
than an error, and a helper's own message survives into the engine's error instead of
being flattened. The tenth checks that returned drafts reach the event log.

What the list does not contain is a test of any bank, and that is the point. The engine's
half of this protocol is fully specified without knowing what sits on the other end of the
pipe — which is why these tests can run against throwaway shell scripts standing in for
helpers, and why a private driver plugs into it without the engine changing.

[`server/src/lib.rs:90`](https://github.com/RustWright/omni-me/blob/76b61f26128359452c1005ce1c7707cf284b47a8/server/src/lib.rs#L90) at `76b61f2`
> `pub type SourceBuilder = Box<dyn FnOnce(SourceCtx) -> SourceFuture + Send>;`
>
> The entire public/private seam, in one line. `run` takes a factory rather than building sources itself, so the public binary and the private one differ by what they pass here and by nothing else. `FnOnce` because it is called exactly once at boot; boxed so the concrete source types never appear anywhere in the engine's own signatures.

[`server/src/main.rs:35`](https://github.com/RustWright/omni-me/blob/76b61f26128359452c1005ce1c7707cf284b47a8/server/src/main.rs#L35) at `76b61f2`
> `        source_builder: Box::new(config_sources),`
>
> What the public binary puts in that seam: a builder that reads a server-side config file and constructs generic sources from whatever it declares. With no file, or an empty one, it returns none — the server still boots, serves and syncs, with auto-import simply idle. The overlay's binary calls the same `run` with a factory of its own.

[`core/src/auto_import/subprocess.rs:65`](https://github.com/RustWright/omni-me/blob/76b61f26128359452c1005ce1c7707cf284b47a8/core/src/auto_import/subprocess.rs#L65) at `76b61f2`
> `pub enum HelperRequest {`
>
> The entire vocabulary the engine speaks to an import driver: fetch what is new, or re-authenticate with this one-time code. What matters is the field that is absent — there is no place to put a credential. The helper reads its own secrets, so no code path exists by which a bank password could reach the public engine. The boundary is structural rather than a rule somebody has to keep remembering.

The suite and the dependency graph cover the structure. What neither can show is that the
public engine is still an application rather than a husk with the interesting parts cut
out, and that is what the screens are for. These are the browser build against a mocked
backend — the institution names are fictional and the sources are fixtures, but the panel,
the states and the controls are the real components.

Everything an import source is, seen from inside the app:


![The Auto-Import Sources settings panel: a Configured sources list holding one CSV source named my-checking, badged Healthy, reading /data/imports/checking.csv into Assets:MyBank:Checking with Edit and Remove controls; beneath it a Running now list of five sources — globepay healthy with no new events, northwind-sync degraded on an expired session with an amber Reconnect needed callout and button, imap-receipts never run, imap-meridian-aed degraded on a failed decryption, and my-checking healthy — each row carrying Pause and Fetch now.](./oc-sources.png)

The configured list holds one generic CSV source, editable and removable in place. The
running list shows sources in every state the engine distinguishes — ticking cleanly,
never yet run, degraded on a decryption failure, and one whose session has expired and is
asking to be reconnected with a code entered here rather than over SSH. Nothing on this
screen knows what any of these sources actually talk to.

Adding one, with the subprocess type selected — the extension point rendered as a form:


![The Add source form: Name and Type side by side with Type set to Subprocess helper, then a Command field and a space-separated Args field, each showing a greyed placeholder example; a note that the source is saved to the server's sources.toml and applied live, above Save and Cancel buttons.](./oc-add-source.png)

## What's worth remembering or doing next?

- **The expensive part of a split like this is the inversion, and it had already been
  paid.** The bank adapters were behind an object-safe trait with a generic registry
  before anyone proposed separating them, so the cut came down to a single un-inverted
  function that built sources straight from a credentials file. Replacing it took one type
  alias and one struct field. The lesson runs backwards from the way it is usually told:
  the abstraction was not built in anticipation of the split — the split was cheap because
  the abstraction already existed for unrelated reasons.
- **Separate repositories mean separate lockfiles, and lockfiles drift apart.** The
  overlay's freshly-resolved lockfile picked a newer SurrealDB minor than the engine's,
  which dragged in a dependency that would not compile on the toolchain at all. The fix
  was pinning both repositories to the same version, which means they must now be bumped
  together or the overlay floats again. Nothing enforces that but a note in two READMEs.
- **Isolation was demonstrated by an outage rather than asserted.** A smoke test against
  the real configuration ran five sources at once; the bank one discovered its session had
  expired weeks earlier, fell back to a login, hit a one-time-code prompt and backed off
  exponentially — while the other four ticked clean. A failure contained in front of you
  is better evidence than a test that no failure escapes.
- **That same first smoke run caught what no unit test could.** A config file still
  pointed its `driver_script` at the path the driver had just been moved out of. The side
  effects of a migration live in configuration, not in code, and nothing that compiles
  will tell you about them.
- **Making the code bank-free did not make the repository bank-free.** The names outlived
  the code by a week — still in the mock data, still in tracker prose, still legible in
  screenshots inside posts that had already been published. Deleting code is a `git rm`;
  removing an identity is an audit of every artifact the project has ever emitted. That
  pass was taken fix-forward: one coherent fictional roster applied consistently
  everywhere, and roughly twenty commit-pinned permalinks re-pointed at a
  post-sanitization snapshot instead of rewriting history.
- **Deferred: enforcement that survives a clone.** The privacy guard should run in CI on
  the public repository, where it cannot be skipped and does not depend on one machine's
  hook directory. The trigger is a second contributor, or the first `--no-verify` that
  turns out to have been load-bearing.
- **Deferred: making the lockstep pin a mechanism.** Today it is prose. The trigger is the
  next SurrealDB bump, which is the first moment the note has to be obeyed by someone who
  did not write it.
