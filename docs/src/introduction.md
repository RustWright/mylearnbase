# My Learn Base

**Live site:** [mylearnbase.com](https://mylearnbase.com)
**Repository:** [github.com/RustWright/mylearnbase](https://github.com/RustWright/mylearnbase)

My Learn Base is a personal learning journal and portfolio site. It documents projects, experiments, and things I find interesting — serving both as a reference for my future self and a resource for others.

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Static site generator | [Zola](https://www.getzola.org/) | Converts markdown into HTML |
| Theme | [Serene](https://github.com/isunjn/serene) | Provides the visual design |
| Hosting | [Cloudflare Pages](https://pages.cloudflare.com/) | Serves the static site globally |
| Documentation | [mdBook](https://rust-lang.github.io/mdBook/) | This documentation |

## How It Works

The site is **fully static** — there's no server-side code running. The workflow is:

1. Write a post in markdown with TOML frontmatter
2. Zola combines the markdown with HTML templates and generates plain HTML/CSS/JS
3. Push to GitHub, which triggers Cloudflare Pages to rebuild and deploy

The result is a fast, secure site with zero hosting costs.

## Project Goals

1. **Blog/Learning Journal** — Document processes when working on projects, with series-based multi-part posts
2. **Portfolio** — Showcase completed work and host interactive demos (future)
3. **Monetization** — Organic revenue generation to cover maintenance costs (future)

## Design Priority

Authoring experience first. If it's frictionless to create content, content gets created consistently.
