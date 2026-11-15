+++
title = "The document archive"
slug = "document-archive"
date = 2026-11-15
draft = false
description = "omni-me's archive keeps documents with metadata fields that record their source. The user's corrections survive every later re-read by a parser or model."

[taxonomies]
tags = ["rust", "event-sourcing", "llm", "dioxus"]
+++

## What does this feature do?

omni-me keeps an archive of documents, such as a scanned lease, a bank statement, a tax
notice or an email. The archive contains both the document and related metadata fields.
Using the document text, a document can be found related to a specific topic, and a
document can be found if its metadata matches specific conditions.

Each metadata field records where its value came from, which is a parser, a model or the
user. It also records whether the value has been checked. A value counts as checked when
the user entered it, or when it agrees with other figures printed in the same document,
such as a statement's closing balance.

The user can correct a field with the document open beside it. The correction stays in
place no matter how many times a parser or model reads the document again.

## Why was it added now?

On 11 September 2026, work on finance resumed with six open threads. All six threads were blocked by the 
fact that omni-me had no way to store a document that was not a transaction. The code that reads documents could
already handle any kind of document, but its output could only hold transactions. The
archive was made as a solution to that problem with every document now landing there, including emails and bank
statements.

Metadata fields are allowed to come from a model, because a model can read documents that
no parser understands. Each of those fields is marked as coming from a model, because of
an earlier failure in the project. A model once put "HAND WASH" in a currency field, and
the amounts on the same record still added up correctly. Every check at the time looked
only at the numbers, so none of them noticed that the currency was not a currency.

## What's in scope (and what's not)?

**In:**
- Any file, stored exactly as it arrived. Its text is kept as well, and scans without text
  get a transcription later.
- Metadata fields from parsers, models and the user, each recording its source and
  whether it has been checked.
- Corrections and removals by the user, which a later parser or model run cannot undo.
- A list of email senders that are never archived.

**Not in:**
- An inbox. Emails can be read in the archive, but nothing there is marked as waiting for
  a reply.
- A confidence score for model fields. Nothing could test whether such a score was
  accurate, so a field only records whether it was checked.

## How do we know it works?

The demo below is the real Archive page from the app, built to run in the browser with
made-up documents. Open the notice of assessment. The PDF appears beside two metadata
fields that a model read, and both are marked as unchecked. Change the tax year and save
it. The field is now marked as yours and as checked, and it stays that way after you go
back to the list and open the document again.

{{ demo(name="omni-me/archive", height=640, caption="The Archive page with made-up documents. Open the notice of assessment and correct a field.") }}

The demo cannot show a parser or model reading the document again, because that only
happens on the server. There, a function called `merge_fields` decides what happens to the
new values. It compares the new fields with the existing ones, one field at a time, and
keeps the value from the higher-ranked source. The user ranks above a parser, and a parser
ranks above a model. The simpler rule would be to always keep the newest value. Under that
rule, every improved prompt or rescanned page would replace the user's corrections without
any warning.

[`core/src/events/documents_projection.rs:363`](https://github.com/RustWright/omni-me/blob/8caa3ca62596485b161918919d77473f0360b150/core/src/events/documents_projection.rs#L363) at `8caa3ca`
> `fn merge_fields(existing: Vec<DocumentField>, incoming: Vec<DocumentField>) -> Vec<DocumentField> {`
>
> The comparison is greater-than-or-equal, not greater-than. When both values come from the same source, the newer one wins. This is what lets the user correct the same field twice. With greater-than, the second save would appear to work but change nothing.

Five tests check this behaviour. A model run after the user's correction leaves the
correction in place. It is tested both on the function alone and again through the database. A second
correction of the same field replaces the first. A field the user removed stays removed,
and a later run cannot bring it back. Fields that a later run does not mention are left as
they were. All five passed, along with the rest of the core tests, in the automated test
run on GitHub at `8caa3ca`
([the run](https://github.com/RustWright/omni-me/actions/runs/43741030947)).

[`core/src/events/documents_projection.rs:952`](https://github.com/RustWright/omni-me/blob/8caa3ca62596485b161918919d77473f0360b150/core/src/events/documents_projection.rs#L952) at `8caa3ca`
> `fn a_model_rerun_never_overwrites_a_human_correction() {`
>
> This test checks the one claim the demo cannot show, using the real `merge_fields` function.

## What's worth remembering or doing next?

- There is only one lasting copy of each document file today, on the server. A second,
  off-site copy is planned.
