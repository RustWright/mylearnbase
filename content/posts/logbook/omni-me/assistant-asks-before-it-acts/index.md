+++
title = "The assistant asks before it acts"
slug = "assistant-asks-before-it-acts"
date = 2026-11-15
draft = false
description = "omni-me's assistant reads the whole app but changes nothing without a yes. Every change arrives as a suggestion, the journal is off limits, and irreversible actions always ask."

[taxonomies]
tags = ["rust", "llm", "event-sourcing", "dioxus"]
+++

## What does this feature do?

omni-me has an assistant that can read everything the app holds about one person: the
journal, notes, routines, the ledger and archived documents. It answers questions by
searching and reading those records, and it says which records an answer came from.

It cannot change any of them on its own. Every change it wants arrives as a suggestion,
with its reason, and nothing happens until the person accepts it. When a suggestion has a review
screen of its own, such as a change to the ledger, it waits there, and the rest wait in the
assistant's inbox.

There are two limitations placed on the assistant. It never suggests writing in the journal, which only the human author is permitted to edit. And any action that cannot be undone always asks, however often its suggestions
have been accepted before.

## Why was it added now?

By September 2026 omni-me held a journal, notes, routines, finances and a document archive
for one person, all in one event log. An assistant with reach across all of it was needed to help with organisation and performing specific tedious tasks, such as recalling a spending detail with its receipt, noticing a habit across journal entries, or checking in on progress.

Reach across a whole life is what makes such an assistant useful, and it is also what makes
an unrequested change costly. So the design started from the write path. The assistant
would read everything and write nothing directly. If the assistant reliably performs reversible tasks correctly and consistently it can be granted permission to skip the question for that specific action.

## What's in scope (and what's not)?

**In:**
- Suggestions for notes, routines, beliefs about the person, and ledger entries, labels and
  categories
- A daily check-in that starts a conversation on its own, marked as asked on the person's behalf
- Permission granted per kind of action, by the person only, and revocable at any time

**Not in:**
- Writing in the journal, even with approval. The journal is the one record with a single
  author, and that is a permanent boundary, not a stage.
- Permission for anything irreversible. Clearing a transaction against a statement has no
  undo, so it asks every time, and no setting can change that.
- Asking for its own permissions. No tool the assistant holds can request a grant.

## How do we know it works?

The demo is the real Assistant page, built for the browser with made-up data. The answers
are scripted and no model runs, but the inbox, the refusal and the permissions screen are
the app's own. One conversation has a suggestion waiting to be accepted or declined. In the
other, the assistant is asked to write in the journal and says it cannot. "What it may do
without asking" lists each kind of action with its record, and the one that cannot be undone
has no switch.

{{ demo(name="omni-me/assistant", height=640, caption="The Assistant page with made-up data. Answers are scripted; the inbox, the refusal and the permissions screen are the app's own.") }}

The rules the demo shows are enforced in code, and four tests pin them. One grants every
action and checks that each irreversible one is refused at the point the grant is written.
One checks that no action in the registry can produce a journal event. One checks that the
model, asking what it can do to a journal entry, is told nothing. And one hands the step that
turns a model's output into suggestions a journal write, and checks that nothing comes out.
All four passed with the rest of the core suite in CI at `8caa3ca`
([the run](https://github.com/RustWright/omni-me/actions/runs/43741030947)).

[`core/src/assistant/actions.rs:371`](https://github.com/RustWright/omni-me/blob/8caa3ca62596485b161918919d77473f0360b150/core/src/assistant/actions.rs#L371) at `8caa3ca`
> `pub const NEVER_PROPOSABLE: &[EventType] = &[`
>
> The four journal events, each listed by name, that no action may produce, so a fifth journal event added later fails a test instead of slipping past a pattern.

[`core/src/assistant/promotion.rs:171`](https://github.com/RustWright/omni-me/blob/8caa3ca62596485b161918919d77473f0360b150/core/src/assistant/promotion.rs#L171) at `8caa3ca`
> `if !action.reversible {`
>
> The grant refuses an irreversible action where the grant is written, so no later check can be routed around.

[`core/src/assistant/promotion.rs:382`](https://github.com/RustWright/omni-me/blob/8caa3ca62596485b161918919d77473f0360b150/core/src/assistant/promotion.rs#L382) at `8caa3ca`
> `async fn an_irreversible_action_cannot_be_granted() {`
>
> Runs over every action rather than a fixture, so a new irreversible action is covered on the day it is added.

A granted action still produces a real suggestion, which is then accepted automatically.
The record keeps the same suggestion and the same decision, noting the standing permission,
so it always says what was done and under whose authority.

## What's worth remembering or doing next?

- Progress during a long answer is a waiting animation today. Showing the real steps as
  they happen comes later.
