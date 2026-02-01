# Architecture - mylearnbase.com

**Created:** 2026-02-01 (Session 2)

---

## Overview

Personal website for documenting learning journeys, showcasing projects, and hosting interactive demos. Prioritizes authoring experience and low friction for publishing.

---

## Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | Dioxus 0.7 (Rust) | Learning goal, cross-platform potential, SSG support |
| **Styling** | TailwindCSS | Built-in Dioxus support, utility-first approach |
| **Content** | Markdown + YAML frontmatter | Flexible, editor-friendly, standard pattern |
| **Markdown Processing** | `gray-matter` + `dioxus-markdown` or `dangerous_inner_html` | Documented approach, used by Dioxus homepage |
| **Static Hosting** | Cloudflare Pages | Free, global CDN, custom domain support, no vendor lock-in for static files |
| **Backend (future)** | Fly.io | For interactive demos when needed, Dioxus-recommended |
| **Domain** | mylearnbase.com | Broad scope, flexibility for future topics beyond code |

---

## Content Organization

**Approach:** Flat files with frontmatter metadata (not folder-based hierarchy)

```
/content/posts/
  building-my-website-part-1.md
  building-my-website-part-2.md
  some-other-post.md
```

**Frontmatter schema:**
```yaml
---
title: "Post Title"
slug: "post-title"           # REQUIRED - determines URL, never change once published
date: 2026-02-01
tags: ["rust", "dioxus", "web"]
series: "series-name"        # optional
series_order: 1              # optional, position in series
draft: false
---
```

**Why this approach:**
- `slug` decouples URL from filename and title — rename files or update titles without breaking links
- Files can be renamed/reorganized without breaking relationships
- Series defined by metadata, not folders
- Maximum flexibility for future changes

---

## Project Structure

**Approach:** Start minimal, refactor as patterns emerge

```
mylearnbase/
├── src/
│   └── main.rs           # Start here, split files as needed
├── content/
│   └── posts/            # Markdown files
├── assets/
│   ├── styles/
│   └── images/
├── Cargo.toml
├── Dioxus.toml
└── README.md
```

**Standing review item:** Evaluate need for `components/` and `pages/` directories each cycle as codebase grows.

---

## MVP Scope (Cycle 1)

**In scope:**
- Homepage
- Blog list page
- Individual post pages
- Series grouping
- Basic styling
- RSS feed
- Deploy pipeline to Cloudflare Pages

**Deferred:**
- Portfolio section
- Interactive demos
- Monetization
- Comments
- Search
- Analytics
- Tag pages

---

## Testing Strategy

| Type | Approach |
|------|----------|
| **Type safety** | Rust compiler + `dx build` |
| **Manual** | Click-through before deploys |
| **Content validation** | Script to validate frontmatter (fields exist, dates valid) |
| **E2E (Playwright)** | Deferred until stable features exist |

---

## Deployment

**Static site (MVP):**
- Build: `dx build --release --ssg`
- Host: Cloudflare Pages
- Custom build command handles Rust/Dioxus CLI installation

**Backend (future):**
- Fly.io with Docker
- Only when interactive demos require server-side functionality

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dioxus SSG edge cases | Low-Medium | Medium | Build in release mode, join Discord for support, proof-of-concept validates early |
| Markdown processing | Low | Low | Clear path: `gray-matter` + `dioxus-markdown` / `dangerous_inner_html` |
| Cloudflare Pages compatibility | Low | Low | Confirmed working, custom build command documented |
| Content workflow friction | Low | Medium | Monitor during first posts, adjust if needed |
| Scope creep | Medium | Medium | Stick to MVP, defer features aggressively |

---

## Proof-of-Concept (Start of Cycle 1)

Before building full site, validate:
1. Create minimal Dioxus project
2. Parse markdown file with frontmatter using `gray-matter`
3. Render content with `dioxus-markdown` or `dangerous_inner_html`
4. Build with `dx build --release --ssg`
5. Deploy to Cloudflare Pages

Success = proceed with full MVP. Failure = reassess before investing more time.

---

## Future Considerations

- Portfolio section with interactive demos (Cycle 2+)
- Fly.io backend when demos need server functionality
- Consider `components/` and `pages/` structure as codebase grows
- Monetization strategy (intentionally deferred, low priority)
