# Architecture - mylearnbase.com

**Created:** 2026-02-01 (Session 2)
**Revised:** 2026-02-02 (Session 2b)
**Status:** Active

---

## Overview

Personal website for documenting learning journeys, showcasing projects, and hosting interactive demos. Prioritizes authoring experience and low friction for publishing.

---

## Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | Zola | Mature SSG, fast builds (195ms), excellent docs, battle-tested |
| **Templating** | Tera (built into Zola) | Jinja2-like syntax, sufficient for static site needs |
| **Styling** | Serene theme | Minimal, dark mode, blog-focused; will cherry-pick features from Tabi/Abridge later |
| **Content** | Markdown + TOML frontmatter | Zola native format, editor-friendly, portable |
| **Static Hosting** | Cloudflare Pages | Free, global CDN, custom domain support, native Zola support |
| **Future Interactivity** | WASM islands (Dioxus/Leptos) | Self-contained demos embedded in static pages when needed |
| **Backend** | Deferred | Not needed for static site or client-side WASM demos |
| **Domain** | mylearnbase.com | Broad scope, flexibility for future topics beyond code |

---

## Content Organization

**Approach:** Zola's standard content structure with frontmatter metadata

```
content/
├── _index.md              # Homepage content
└── blog/
    ├── _index.md          # Blog section index
    ├── building-my-website-part-1.md
    ├── building-my-website-part-2.md
    └── some-other-post.md
```

**Frontmatter schema (TOML):**
```toml
+++
title = "Post Title"
slug = "post-title"           # Determines URL, never change once published
date = 2026-02-01
draft = false

[taxonomies]
tags = ["rust", "zola", "web"]
series = ["building-my-website"]  # Optional, for multi-part content

[extra]
series_order = 1                  # Optional, position in series
+++
```

**Why this approach:**
- `slug` decouples URL from filename and title — rename files or update titles without breaking links
- Series via taxonomies gives automatic series pages
- Standard Zola patterns = better docs and community support

---

## Project Structure

**Approach:** Standard Zola structure, minimal customization

```
mylearnbase/
├── content/
│   ├── _index.md
│   └── blog/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── blog.html
│   └── blog-page.html
├── sass/                  # Or static/css/ depending on theme
├── static/
│   └── wasm/              # Future: compiled WASM demos
├── themes/                # If using external theme
├── config.toml
└── README.md
```

---

## MVP Scope (Cycle 1)

**In scope:**
- Homepage
- Blog list page
- Individual post pages
- Series grouping
- Basic styling (via theme selection)
- RSS feed (built into Zola)
- Deploy pipeline to Cloudflare Pages

**Deferred:**
- Portfolio section
- Interactive demos (WASM islands)
- Monetization
- Comments
- Search (Zola has built-in, but defer setup)
- Analytics
- Tag pages (Zola generates automatically, but defer styling)

---

## Testing Strategy

| Type | Approach |
|------|----------|
| **Build validation** | `zola check` (links, references, config) |
| **Manual** | Click-through before deploys |
| **UI feedback** | Screenshots shared with LLM for design iteration |
| **Content validation** | `zola build` fails on invalid frontmatter |

---

## Deployment

**Build command:** `zola build`
**Output directory:** `public/`
**Host:** Cloudflare Pages (native Zola support, zero config)

Cloudflare Pages auto-detects Zola projects. No custom build commands needed.

---

## Future: WASM Interactivity

When interactive demos are needed (Cycle 2+), the approach is **additive, not a rewrite**.

**How it works:**
1. Create a separate Rust crate for demos (e.g., `demos/sorting-viz/`)
2. Compile to WASM using `wasm-pack` or `trunk`
3. Output `.wasm` + `.js` files to `static/wasm/`
4. Embed in specific posts via `<div>` + `<script>` tags
5. Zola serves these as static files — no backend needed

**Example embed in markdown:**
```markdown
Here's an interactive visualization:

<div id="sorting-demo"></div>
<script type="module">
  import init from '/wasm/sorting-demo.js';
  init();
</script>
```

**What stays unchanged:** Content, templates, URLs, hosting, build process (just adds WASM compilation step).

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| Dioxus SSG edge cases | - | - | - | **Realized & Resolved** — Pivoted to Zola |
| Design paralysis | High | Medium | Select theme in planning session; iterate with LLM feedback | Open |
| Zola learning curve | Medium | Low | Excellent docs, simpler than Dioxus; Tera is straightforward | Open |
| WASM integration complexity | Low | Medium | Defer until needed; well-documented when required | Open |
| Zola limitations | Low | Low | Very flexible for static sites; escape hatch is WASM or raw HTML | Open |
| Content workflow friction | Low | Medium | Monitor during first posts, adjust if needed | Open |
| Scope creep | Medium | Medium | Stick to MVP, defer features aggressively | Open |

---

## Architecture Revision History

### Session 2b (2026-02-02)

**Trigger:** PoC revealed Dioxus 0.7 SSG produces empty HTML shell, not pre-rendered content.

**Changes:**
| Aspect | Before | After | Rationale |
|--------|--------|-------|-----------|
| Framework | Dioxus 0.7 | Zola | Dioxus SSG broken; Zola validated, mature |
| Backend | Fly.io (future) | Deferred entirely | Not needed for static or client-side WASM |
| Future interactivity | Not defined | WASM islands | Self-contained demos, additive approach |
| Testing | Rust compiler + validation script | `zola check` + manual + LLM screenshots | Simpler toolchain |

**Validation:** `poc-zola/` demonstrates working Zola build with markdown + syntax highlighting in 195ms.

---

## Planning Notes

- ~~**Theme selection** required early in Session 3 to unblock UI work and mitigate design paralysis risk~~ ✓ Resolved: Serene
- **Theme evolution strategy:** Start with Serene to establish content workflow, then incrementally add features from Tabi and Abridge as needed (avoids decision paralysis)
