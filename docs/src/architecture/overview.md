# Architecture Overview

## The Data Flow

When you run `zola build` (or push to GitHub, triggering Cloudflare), this is what happens:

```
1. Zola reads zola.toml for configuration
2. Scans content/ for all .md files
3. Parses frontmatter (TOML between +++) and body (markdown)
4. For each page: picks the right template, injects the content
5. Auto-generates taxonomy pages (/tags/meta/, /series/building-my-website/)
6. Compiles sass/ into CSS
7. Copies static/ files as-is to the output
8. Writes everything to public/
```

The output is entirely static HTML, CSS, and JS — no server-side processing at request time.

## The Override System

Zola has a layered file resolution system. When it needs a template or stylesheet, it checks:

1. **Your project's files first** (`templates/`, `sass/`)
2. **The theme's files second** (`themes/serene/templates/`, `themes/serene/sass/`)

If you place a file in your project with the same name and path as one in the theme, yours wins. This is how you customize behavior without editing the theme directly — and it means theme updates won't overwrite your changes.

## Template Inheritance

Every page template follows a chain:

```
Your template (e.g., templates/blog.html)
    └── extends → Theme's _base.html
                      └── defines blocks: {% block content %}, {% block title %}, etc.
```

The base template (`_base.html` from Serene) provides the HTML skeleton — `<head>`, navigation, dark mode toggle, scripts. Your templates fill in specific `{% block %}` sections with page-specific content.

## Technology Decisions

| Decision | Choice | Alternatives Considered | Deciding Factor |
|----------|--------|------------------------|-----------------|
| Framework | Zola | Dioxus 0.7, Leptos, Astro | Dioxus SSG was broken; Zola validated and mature |
| Theme | Serene | Tabi, Abridge | Minimal, dark mode, blog-focused |
| Hosting | Cloudflare Pages | GitHub Pages, Vercel, Netlify | Free, global CDN, future Workers option |
| Content format | Markdown + TOML | Database, CMS | Simplicity, editor-friendly, portable |
| Future interactivity | WASM islands | Full SPA rewrite | Additive approach, no rewrite needed |

## Future: WASM Islands

When interactive demos are needed, the approach is additive:

1. Create a separate Rust crate for each demo (e.g., `demos/sorting-viz/`)
2. Compile to WASM
3. Output `.wasm` + `.js` files to `static/wasm/`
4. Embed in posts via `<div>` + `<script>` tags
5. Zola serves these as static files — no backend needed

The existing site structure, URLs, and deployment pipeline stay unchanged.
