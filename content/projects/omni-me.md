+++
title = "omni-me"
description = "An offline-first personal app for notes, journaling, routines and finances, running on Android and Linux desktop from one Rust codebase on an event-sourced data model."
weight = 20

[extra]
# active | complete. Anything else fails the build (templates/project.html).
status = "active"
period = "March 2026 – present"
stack = ["Rust", "Tauri", "Dioxus", "SurrealDB", "axum"]
repo = "https://github.com/RustWright/omni-me"
logbook = "posts/logbook/omni-me/_index.md"
+++

A personal app for notes, journaling, routines and finances. It runs on Android and Linux desktop from a single Rust codebase and syncs through a self-hosted server. It is built for one person's daily use rather than as a product, so it favours durable data over onboarding a second user.

Every change is stored as an append-only event, and the app's current state is rebuilt from that log. The choice does real work. A projection bug is repaired by replaying the log, a schema change reinterprets history instead of migrating it, and syncing two devices becomes a matter of exchanging facts.

Finances are the larger half of the app, with double-entry bookkeeping over a plaintext ledger, receipt capture, bank statement import, reconciliation and budgeting. The logbook entries below document those features as they were built. Version 1.1 was released in September 2026, and the app is in daily use on a phone and a Linux desktop.
