+++
title = "Resources used to build mylearnbase"
slug = "building-mylearnbase"
date = 2026-06-30
draft = false

[taxonomies]
tags = ["zola", "static-sites", "tooling"]
+++

> The external tools and references behind this site: what each one does, and
> how it fits here.

## Site generator and theme

- **[Zola](https://www.getzola.org)** — the static site generator the whole
  site is built on. Single Rust binary, no plugin ecosystem to manage; Markdown
  in, HTML out. Its **[Tera](https://keats.github.io/tera/)** templating language
  is what every layout and shortcode here is written in.
  The [shortcodes documentation](https://www.getzola.org/documentation/content/shortcodes/)
  earned its own bookmark — it's where the rule that `{{/* */}}`-style escaping
  is needed inside code blocks finally became clear.
- **[Serene](https://github.com/isunjn/serene)** — the theme the design started
  from. Pulled in as a pinned git submodule and then heavily customized: the
  persistent header, site search, reader controls, and post chrome are all
  built on top of it rather than shipped by it.

## Hosting and deployment

- **[Cloudflare Pages](https://pages.cloudflare.com)** — builds and serves the
  site. The build command fetches Zola (it isn't pre-installed on the image),
  runs the build, then generates the search index. The free tier covers a
  static site of this size comfortably.

## Search

- **[Pagefind](https://pagefind.app)** — the in-browser search. It builds a
  chunked index at deploy time and queries it entirely client-side, so search
  works with no server and no third-party service. Chosen over Zola's built-in
  search index and over hosted options like Algolia.

## Reading experience

- **[OpenDyslexic](https://opendyslexic.org)** — the dyslexia-friendly typeface
  offered in the reader controls, alongside the default serif and a sans option.
- **[KaTeX](https://katex.org)** — renders math. Loaded from a CDN only on pages
  that actually contain math, so most pages pull nothing extra.
- **[Mermaid](https://mermaid.js.org)** — renders diagrams from text, on the
  same load-only-when-needed basis as KaTeX.
- **Syntax highlighting** — handled by Zola's built-in
  [syntect](https://github.com/trishume/syntect) engine in class mode, which
  emits a stylesheet at build time rather than highlighting in the browser.

## Documentation

- **[mdBook](https://rust-lang.github.io/mdBook/)** — generates the project's
  separate documentation site, deployed to GitHub Pages. Kept apart from the
  Zola site so build/process docs don't mix with published posts.

## Authoring tooling

- **[showboat](https://github.com/simonw/showboat)** — records terminal sessions
  and runs commands for verification. It's the substrate the project's own
  post-authoring tools are built on, so the posts about building this site can
  show real command output rather than hand-copied snippets.
- **[uv](https://docs.astral.sh/uv/)** — installs and runs those Python tools as
  standalone commands, so they work from any project, not just this one.

## SEO and audits

- **[Lighthouse](https://developer.chrome.com/docs/lighthouse/overview)** — the
  audit used to drive the SEO pass to 100/100 and to watch performance.
- **[ahrefs](https://ahrefs.com)** — site auditing; the health score moved from
  67% to 98% during the SEO work.
- **[Google Search Console](https://search.google.com/search-console/about)**
  and **[Bing Webmaster Tools](https://www.bing.com/webmasters)** — sitemap
  submission and index coverage for the two search engines.
- **[schema.org](https://schema.org)** — the vocabulary the site's JSON-LD
  structured data is written against (BlogPosting, WebSite, BreadcrumbList).

## Alternatives considered

What I compared before settling on Zola and Serene.

- **Choosing a generator and theme.** Compared options through the
  [Zola theme directory](https://www.getzola.org/themes/) and a community
  [Zola themes collection](https://salif.github.io/zola-themes-collection/),
  studied the [Serene demo](https://serene-demo.pages.dev/) and its
  [usage guide](https://github.com/isunjn/serene/blob/main/USAGE.md), and read
  [tabi's settings guide](https://welpo.github.io/tabi/blog/mastering-tabi-settings/)
  as a point of comparison before settling on Serene.
- **The Rust-fullstack detour (abandoned).** Before choosing a static
  generator I explored a server-rendered Rust stack:
  [Dioxus](https://dioxuslabs.com/), [Leptos' start-axum](https://github.com/leptos-rs/start-axum),
  and [cinnog](https://github.com/NiklasEi/cinnog) (a Leptos static-site tool),
  plus a scattering of r/rust threads and a Leptos-as-data-layer blog post. The
  proof-of-concept never justified its complexity for a content site, so the
  whole approach was dropped in favour of Zola.
