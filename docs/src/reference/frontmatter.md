# Frontmatter Fields

Every post requires a TOML frontmatter block between `+++` markers at the top of the file.

## Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | String | Post title (displayed on page and in listings) | `"Hello World"` |
| `slug` | String | URL path segment — **never change once published** | `"hello-world"` |
| `date` | Date | Publication date | `2026-02-04` |

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `draft` | Boolean | `false` | Set `true` to hide from listings and feeds |
| `updated` | Date | — | Last updated date (shown if different from `date`) |
| `description` | String | — | Used for meta description tag (SEO) |
| `summary` | String | — | Short summary, used in meta tags if set |

## Taxonomies

Declared under `[taxonomies]`:

| Field | Type | Description |
|-------|------|-------------|
| `tags` | Array of strings | Topic labels |
| `series` | Array of strings | Multi-part post grouping |
| `categories` | Array of strings | Broad categories (not actively used) |

```toml
[taxonomies]
tags = ["rust", "zola", "web"]
series = ["Building My Website"]
```

## Extra Fields

Declared under `[extra]`:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `series_order` | Integer | — | Position within a series (1, 2, 3...) |
| `toc` | Boolean | (inherits from section) | Override table of contents for this post |
| `comment` | Boolean | (inherits from section) | Override comments for this post |
| `outdate_alert` | Boolean | (inherits from section) | Override outdate alert for this post |
| `outdate_alert_days` | Integer | (inherits from section) | Override days threshold |
| `math` | Boolean | `false` | Enable KaTeX math rendering |
| `mermaid` | Boolean | `false` | Enable Mermaid diagrams |
| `featured` | Boolean | `false` | Highlight in post listings |
| `copy` | Boolean | (inherits from section) | Override code copy button |

## Full Example

```toml
+++
title = "Building My Website — Part 1"
slug = "building-my-website-part-1"
date = 2026-02-10
draft = false

[taxonomies]
tags = ["rust", "zola", "web"]
series = ["Building My Website"]

[extra]
series_order = 1
+++
```

## Notes

- The `slug` determines the URL: `/posts/<slug>/`. Changing it after publication breaks existing links.
- The `title` can be changed freely — it doesn't affect URLs.
- Fields under `[extra]` that say "inherits from section" get their default from `content/posts/_index.md`. You only need to set them per-post if you want to override the section default.
