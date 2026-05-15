+++
title = "Authoring a resources post"
slug = "authoring-a-resources-post"
date = 2026-05-14
draft = false
+++

A resources post packages a curated set of external content (articles,
tools, books, repos) so future-you can find them in one place when the
need arises. The motivating scenario: future-you remembers doing a
similar project before and wants the consolidated entry point — not
digging through old repos, browser history, or project files.

Author contribution is **implicit by curation-by-act**. The act of
having used a resource during a project, or having saved a bookmark
deliberately, is what earns the entry's place on the list. The LLM
helps gather, organize, and format the curated set into a clean post;
it does not supply the set.

## When to write a resources post

Two paths fit the form today:

- **Project-derived.** At project completion, bundle the external
  resources you used during the work. Bidirectional backlink with the
  project's logbook post is what makes this path land — future-you
  can arrive from either the project side or the topic side.
- **Collection-driven.** A bookmarks folder has accumulated enough on
  one topic that distilling it into a post would be more useful than
  scrolling through the folder later.

Don't use this form when:

- The post is about a feature you built. (Use a *logbook* post.)
- The post is an interactive demo built to understand a concept. (Use
  a *concepts* post.)
- The post is a personal take on something you read. (Use an
  *opinions* post.)
- The post is a prescriptive procedure or process doc. (Use a
  *workflows* post.)

## Tools

No form-specific tool. Draft directly at:

```
mylearnbase/content/posts/resources/<slug>.md
```

Cross-form tools that apply:

- `zola check` — load-bearing for resources because the form is mostly
  links. Caught at general site discipline; no per-form call-out
  needed.
- `cite` — rare. Available if a single entry needs a file:line code
  reference inside an external repo.

## Section structure

| # | Section | Required? | Notes |
|---|---------|-----------|-------|
| 1 | Title + frontmatter | yes | Title names the curated set. |
| 2 | One-line summary blockquote | yes | Names what the list is gathered around. Read-state legend folds in here when markers are used. |
| 3 | Category structure (`##` subheadings) | optional | Use when natural sub-groupings exist; flat list otherwise. |
| 4 | Annotated entries | yes | Per-bullet structure below. |
| 5 | Cross-references to logbook | soft convention for project-derived | Bidirectional discoverability when both posts exist. Not gated at publish time. |
| 6 | Superseded-by banner | automatic | Rendered when `extra.superseded_by` is set. |

**Frontmatter (form-specific minimum):**

```
+++
title = "Weather APIs"
date = 2026-05-14
draft = true

[taxonomies]
tags = ["weather", "apis"]
+++
```

`updated` and `extra.superseded_by` get added later if/when they
apply.

**Per-bullet structure (§4):**

Each entry has two layers, both light:

- **Descriptive line** — what the resource is, what it does, what's
  in it. LLM-first-draft per the 4-step descriptive-prose cycle (LLM
  drafts → user revises → LLM grammar pass → user final). One line
  usually suffices.
- **Optional context line** — short "what to look for," "how it
  landed during the project," "this one was painful to set up," "docs
  were better than the alternatives." User-flavored, fully
  discretionary. If just the link is enough, just the link.

**Read-state markers** (when used, locked in for cross-post
consistency):

- **✓** — Read carefully; annotation reflects what was taken from it.
- **~** — Skimmed only; annotation is a surface impression.
- **?** — Saved but unread; annotation is "why I saved it."

Include markers when items have **mixed** read-states (typical for
collection-driven). Skip them when all items share a state (typical
for project-derived — everything's been used). Legend goes inline in
the §2 summary blockquote when markers are used.

## Anti-patterns

- **Annotation paraphrases the title.** The descriptive line restates
  what the URL already says, adding nothing past the link itself.
  Tighten to what the resource actually does, what's distinctive, or
  what's inside it.
- **List items the author hasn't actually engaged with.** If the post
  is filled out by an LLM with suggestions you haven't read, used, or
  chosen to save, the form's curation floor collapses. Entries come
  from lived use or lived bookmarking, not from LLM-generated reading
  lists.
- **Unmarked mixed read-states.** When the list mixes things you've
  actually read with things saved-for-later, readers (including
  future-you) can't tell what carries epistemic weight. Use the
  markers when states vary.
- **Vendor-marketing-tone annotations.** "An industry-leading library
  for high-performance async I/O…" When annotations sound like the
  vendor's own copy, they've lost the author voice that earns the
  form. The LLM-first descriptive cycle most often produces this; the
  user-edit pass catches it.

## End-to-end walkthrough

The project-derived and collection-driven paths share most of the
work; only the trigger and §5 backlink differ.

### Project-derived path

1. **Trigger.** Project completion or cycle close, with the
   recognition that a meaningful set of external resources got used
   during the work.
2. **Gather.** Pull URLs from the project's logbook post §6 (cited
   links and external observables), browser history from the work
   period, or wherever the resources lived during the project.
3. **Draft.** Create `content/posts/resources/<slug>.md` directly.
   Write the frontmatter from the form-specific minimum above.
4. **LLM gather / organize / format.** Hand the URL set to the LLM
   with the post's intent (e.g., "resources from the SunCheck weather
   project"). LLM produces: §2 summary blockquote, §3 category
   structure if natural groupings exist, §4 annotated entries with
   descriptive lines per item.
5. **User edit pass.** Catch vendor-marketing tone, trim
   title-paraphrase lines, drop items that shouldn't be on the list,
   add optional context lines where there's something worth saying.
6. **§5 cross-references — bidirectional.** Add a link to the
   project's logbook post in the resources post; then edit the
   logbook post to link back to the resources post. Both directions
   or neither — a unidirectional link leaves one of the two future-you
   entry points dark.
7. **Publish.** `zola check`, flip `draft = false`, commit.

### Collection-driven path

Same shape, with four divergences:

- **Trigger** is critical mass in a bookmark folder, not project
  completion.
- **Gather** pulls from the bookmark folder, not the logbook post.
- **Read-state markers** likely needed in §4 since states vary; legend
  goes inline in §2.
- **§5 cross-references** typically absent (no anchoring logbook post).
