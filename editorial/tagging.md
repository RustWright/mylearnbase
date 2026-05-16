# Tagging strategy

A cross-form editorial doc — tagging applies the same way to every form.
Per-form authoring guides (`logbook.md`, `concepts.md`, `workflows.md`,
`opinions.md`, `resources.md`) cover what each form contains; this doc
covers how each post gets tagged.

## What tagging is for

The test: *future-you looking for a specific past post should be able to
narrow it down by intersecting two or three tags.* If `rust` + `wasm` +
`mobile-development` returns the three posts that fit, the system is
working. If it returns 30 unrelated posts, the tags are too broad. If it
returns zero, the tags are too narrow or inconsistent.

Tagging is **topic-anchored, form-agnostic**. A logbook entry about Rust
and a concepts post about Rust both use `rust`. The form is conveyed by
the URL path (`/posts/logbook/...` vs `/posts/concepts/...`); the tag axis
is for cross-cutting topical discovery.

## Style conventions

| Rule | Example | Anti-example |
|---|---|---|
| Lowercase only | `rust` | `Rust`, `RUST` |
| Kebab-case for multi-word | `mobile-development`, `event-sourcing` | `mobile_development`, `mobile development`, `MobileDev` |
| Singular over plural | `api`, `database` | `apis`, `databases` |
| Concrete over abstract | `tauri`, `dioxus`, `wasm` | `framework`, `frontend` |
| No project names | `rust`, `auth` (for an omni-me post about Rust auth) | `omni-me`, `mylearnbase` (the project path conveys this) |
| No form names | `rust`, `meta` | `logbook`, `concepts`, `workflows` |
| No version numbers | `rust`, `zola` | `rust-1.91`, `zola-0.22` |

## Decision rules

**Reuse first.** Before introducing a new tag, run:

```bash
grep -rh '^tags = ' /home/me/productive_learning/projects/mylearnbase/content/posts/ | \
  tr ',' '\n' | tr -d '[]"' | sort -u | head -50
```

If a near-match already exists, use the existing one. **Ambiguity gets
resolved in conversation, not in a catalog.** If the grep surfaces two
plausible near-synonyms (e.g., `ui` vs `ui-development`), the LLM
surfaces the choice to the user and they decide together. No canonical
aliases table is maintained — the decision is made at post-creation time
based on which framing the current post genuinely fits.

**Per-post bar: 3-7 tags.** Fewer than 3 typically means the post isn't
tagged at the right level of specificity. More than 7 typically means
tags are being used as keyword spam rather than intersectional axes.
Outliers are fine occasionally; they shouldn't be the norm.

**Opinion-form caveat.** Opinions posts can be short (the take is the
point) but cover wide-reaching territory — a 200-word take might
legitimately deserve many tags if the opinion crosses domains. Other
opinion posts will be narrow and focused with few tags. The 3-7 range
is a default, not a constraint; opinion posts in particular should pick
the count that matches the *scope* of the take, not the *length* of the
prose.

**Splitting an existing tag.** If a tag covers two genuinely distinct
concepts that future-you would want to disambiguate, split it at the
moment you notice. No central record needed — the next time the LLM
greps for current tags, both forms will surface.

## Anti-patterns

- **Placeholder tags shipped.** `tags = ["tag1", "tag2"]` from the
  frontmatter template, never replaced. Read the frontmatter before
  flipping `draft = false`.
- **One-off tags with nothing to cluster into.** Tagging a post `quantum`
  when nothing else on the site touches quantum computing means the tag
  doesn't earn its keep — it doesn't enable intersection. Either skip it
  or be prepared for it to be a one-off for a long time. (One-offs are
  fine when the author expects future posts to join; they're noise when
  the author doesn't.)
- **All-caps tags.** `SQL`, `API` — Zola slugifies them, so they reach
  the URL as `sql` and `api`. The frontmatter just reads wrong.
- **Project names as tags.** Project-specific routing (logbook's
  per-project subdirs, post slugs) conveys the project. Tagging
  `omni-me` would only be useful if the user expected to find that tag
  on posts *outside* the project's path — which doesn't happen.
- **Form names as tags.** The URL conveys the form. `tags = ["logbook"]`
  on a logbook entry is pure noise.
- **Tags as keyword spam.** Resist the urge to add tags for every word
  the post mentions. Tags are intersectional axes, not search keywords.

## When this doc gets edited

- A style convention changes (very rare).
- An anti-pattern surfaces from lived experience — log it here so the
  next session catches it.

This doc does **not** get edited when a new tag is created or when a
near-synonym is picked over an alternative. Those decisions live in post
frontmatter and in the conversation that produced them. The doc stays
stable; the tag inventory drifts organically; ambiguity gets resolved
case-by-case.
