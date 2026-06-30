# Architecture - mylearnbase.com

**Created:** 2026-02-01 (Session 2)
**Revised:** 2026-06-30 (Cycle 5 — brought back in line with the live site)
**Status:** Active

---

## Overview

Personal website for documenting learning journeys, showcasing projects, and hosting interactive demos. Prioritizes authoring experience and low friction for publishing. The site is built around a five-form **post system** (logbook / concepts / workflows / opinions / resources) authored through cross-project tooling.

---

## Technology Stack

| Layer | Choice | Rationale / notes |
|-------|--------|-------------------|
| **Static site generator** | Zola 0.22.1 | Mature SSG, fast builds, single binary, excellent docs |
| **Templating** | Tera (built into Zola) | Jinja2-like; drives all custom templates |
| **Theme** | Serene v5.6.1 (`themes/serene` git submodule, `isunjn/serene`) | Minimal, dark-mode-capable base; heavily overridden (see Project Structure) |
| **Content** | Markdown + TOML frontmatter | Zola-native, editor-friendly, portable |
| **Search** | Pagefind 1.5.2 | Static post-build index over rendered HTML. Zola's `build_search_index = false`; Pagefind replaces native search |
| **Interactive demos** | `{{ demo() }}` shortcode → same-origin iframe | Self-contained bundles under `static/demos/`. Replaces the original WASM-islands plan (never built) |
| **Hosting** | Cloudflare Pages via `bash build.sh` | Free, global CDN, custom domain. The script owns the whole pipeline (Cloudflare does not auto-run Zola or Pagefind) |
| **Docs** | mdBook → GitHub Pages (Actions) | Project documentation in `docs/`, deployed separately from the site |
| **Cross-project tooling** | Python (`tools/`, `uv tool install`) | `logbook` / `cookbook` / `workflows` / `cite` post-system commands, runnable from any repo |
| **Domain** | mylearnbase.com | Broad scope, flexibility for future topics beyond code |

---

## Content Organization

**Approach:** a single `content/posts/` tree, partitioned by **post form**. Logbook is nested one level deeper, per project; the other four forms are flat.

```
content/
├── _index.md                 # homepage content
└── posts/
    ├── _index.md             # /posts aggregator (transparent section)
    ├── logbook/              # dev logs, nested per project
    │   ├── mylearnbase/
    │   └── omni-me/
    ├── concepts/             # interactive-demo-driven explainers
    ├── workflows/            # repeatable how-to writeups
    ├── opinions/             # short argued positions
    ├── resources/            # curated resource collections
    └── archive/              # historical / pre-system content
```

**Taxonomies:** `tags` and `series` only. `categories` was removed in Cycle 3. Series powers the multi-part "Building My LearnBase" arc via the custom `templates/series/` templates (the theme ships none).

**Frontmatter schema (TOML):**
```toml
+++
title = "Post Title"
slug = "post-title"            # URL-stable; set once, never change after publish
date = 2026-06-27
draft = false

[taxonomies]
tags = ["zola", "web"]
series = ["Building My LearnBase"]   # optional, multi-part content

[extra]
# optional per-post overrides: toc, copy, math, mermaid, reaction,
# superseded_by, outdate_alert, lang, series_order
+++
```

**Why this approach:**
- `slug` decouples URL from filename and title, so files/titles can change without breaking links.
- Form-based directories let each form carry its own `_index.md` defaults (date format, TOC, copy buttons) and keep authoring guides in `editorial/` aligned 1:1 with content folders.
- Logbook nests per project because it documents multiple projects; the analytical forms are single-stream, so they stay flat.

---

## Project Structure

The project overrides a focused slice of the Serene theme rather than forking it. Anything in `templates/` here shadows the submodule's copy.

```
mylearnbase/
├── content/                      # see Content Organization
├── templates/                    # project overrides on top of Serene
│   ├── _base.html                # page shell, header nav
│   ├── home.html                 # homepage + form guide cards
│   ├── blog.html                 # section listing
│   ├── post.html                 # single post (prev/next, TOC, reader controls)
│   ├── posts_aggregator.html     # /posts cross-form index
│   ├── _head_extend.html         # JSON-LD structured data, verification meta
│   ├── _footer.html
│   ├── robots.txt
│   ├── series/{list,single}.html # custom — theme ships no series templates
│   ├── tags/{list,single}.html
│   └── shortcodes/demo.html      # {{ demo() }} iframe embed
├── static/
│   ├── js/                       # header.js, reader-controls.js, search.js
│   ├── css/custom.css
│   ├── demos/<project>/<name>/   # self-contained interactive demos (concepts, mylearnbase)
│   ├── fonts/                    # OpenDyslexic (reader-controls typeface)
│   ├── img/                      # favicons, logo, og-default.png (social cards)
│   ├── llms.txt                  # crawl guidance for AI agents
│   └── giallo-*.css              # syntax-highlight CSS (generated; gitignored)
├── scripts/
│   └── seo-audit.sh              # SEO/meta audit (compute-related.py lands in Cycle 5 Task 3)
├── themes/serene/                # git submodule, v5.6.1
├── docs/                         # mdBook source → GitHub Pages (docs/book/ gitignored)
├── tools/                        # cross-project Python tooling (pyproject.toml + uv)
├── editorial/                    # per-form authoring guides
├── build.sh                      # Cloudflare build pipeline
├── zola.toml                     # site config (NOT config.toml)
└── public/                       # build output (gitignored)
```

---

## MVP Scope (Cycle 1, historical baseline)

The Cycle 1 launch target. Recorded here for trajectory; most "deferred" items have since shipped in later cycles.

**Shipped in Cycle 1:** homepage, section/post pages, series grouping, theme styling, RSS feed, Cloudflare Pages deploy.

**Originally deferred, since shipped:** search (Pagefind, Cycle 4), interactive demos (`{{ demo() }}` iframe, Cycle 4), tag pages (styled), reading-time / reader controls / sticky header (Cycle 4).

**Still deferred:** portfolio section, monetization, comments (giscus wired but off), analytics.

---

## Testing Strategy

| Type | Approach |
|------|----------|
| **Build validation** | `zola build` (fails on invalid frontmatter / broken refs), `zola check --skip-external-links` |
| **SEO / meta** | `scripts/seo-audit.sh`, Lighthouse SEO, Search Console / Bing Webmaster |
| **UI sweep** | `ui-checklist.md` — periodic manual verification sweeps across viewports + light/dark |
| **UI feedback** | Screenshots shared with LLM for design iteration |

---

## Deployment

**Build command (Cloudflare Pages → Settings → Builds & deployments):** `bash build.sh`
**Output directory:** `public/`
**Host:** Cloudflare Pages

Cloudflare does **not** pre-install Zola or run a post-build step, so `build.sh` owns the whole pipeline:

1. Fetch Zola v0.22.1 if it isn't already on `PATH` (reused locally, downloaded in CI).
2. `zola build` → `public/`.
3. `npx pagefind --site public` → search index in `public/pagefind/`.

Running `bash build.sh` locally reproduces production output exactly, including the Pagefind index that a plain `zola serve` cannot generate (so search is a prod-only feature in dev). mdBook docs deploy independently via GitHub Actions to GitHub Pages.

---

## Interactive Demos

Demos are **reactive reader experiences** embedded in otherwise-static pages. Each demo is a self-contained static bundle (its own HTML/JS/CSS) under `static/demos/<project>/<name>/`, embedded with:

```
{{ demo(name="omni-me/calendar", height=480, caption="optional", wide=false) }}
```

`templates/shortcodes/demo.html` renders a lazy, same-origin `<iframe>` plus an "Open standalone" link. `wide=true` breaks the demo out of the reading column for spatial/comparative interactives.

**Why iframes, not WASM islands (the original plan):** an iframe isolates each demo's JS/CSS from the page and from sibling demos, needs no compile step or extra toolchain, and serves as a plain static file. The central design tension is that the demos are genuinely reactive content living inside a static-site build; the iframe boundary is what reconciles the two.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| Dioxus SSG edge cases | - | - | Pivoted to Zola | **Resolved** (Session 2b) |
| Design paralysis | High | Medium | Adopt Serene, iterate with LLM feedback | **Resolved** — Serene adopted, heavily customized |
| Zola learning curve | Medium | Low | Strong docs; Tera straightforward | **Resolved** — comfortable across 5 cycles |
| WASM integration complexity | Low | Medium | Defer until needed | **Moot** — superseded by iframe demos |
| Content workflow friction | Low | Medium | Monitor; built the post-system tooling to reduce it | Mitigated |
| Scope creep | Medium | Medium | Cycle-based scoping; defer aggressively | Open (managed) |

---

## Architecture Revision History

### Cycle 5 (2026-06-30)

**Trigger:** Doc had drifted since 2026-02-02 and described a different site (abandoned Dioxus framing, `blog/` + `config.toml` layout, "search deferred").

**Changes:**
| Aspect | Before | After |
|--------|--------|-------|
| Content layout | `content/blog/` | `content/posts/<form>/` five-form system + `archive/` |
| Config file | `config.toml` | `zola.toml` |
| Search | "deferred" | Pagefind 1.5.2 (shipped Cycle 4) |
| Interactivity | WASM islands (Dioxus/Leptos) | `{{ demo() }}` same-origin iframe shortcode |
| Deployment | "Cloudflare auto-detects Zola, no build command" | `bash build.sh` owns fetch + build + Pagefind index |
| Docs | not mentioned | mdBook → GitHub Pages via Actions |
| Templates | `base/index/blog/blog-page.html` | overridden surface incl. custom `series/` + `tags/`, `shortcodes/demo.html` |

### Session 2b (2026-02-02)

**Trigger:** PoC revealed Dioxus 0.7 SSG produces an empty HTML shell, not pre-rendered content.

**Changes:**
| Aspect | Before | After | Rationale |
|--------|--------|-------|-----------|
| Framework | Dioxus 0.7 | Zola | Dioxus SSG broken; Zola validated, mature |
| Backend | Fly.io (future) | Deferred entirely | Not needed for static or client-side demos |
| Future interactivity | Not defined | WASM islands | (Later superseded by iframe demos, Cycle 4) |
| Testing | Rust compiler + validation script | `zola check` + manual + LLM screenshots | Simpler toolchain |

**Validation:** `poc-zola/` demonstrated a working Zola build with markdown + syntax highlighting.
