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
├── _index.md                 # homepage: doors, dated Now line (see § Homepage and header)
├── projects/                 # /projects/ hub + one page per project (see § Projects below)
├── playground/_index.md      # /playground/ gallery of every demo (see § Interactive Demos)
├── resume/_index.md          # /resume/, canonical résumé; the PDF is generated from it
├── colophon/_index.md        # how the site is built
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

### Projects

`/projects/` is a section (`templates/projects.html`) whose pages each describe one project (`templates/project.html`). A project page carries only what cannot be derived — a description, `status` (`active` or `complete`; anything else fails the build), `period`, `stack`, `repo` — plus two pointers: `logbook`, a logbook section, and `posts`, a list of other posts. **Everything else on the page is derived from what is already published.** The write-up list is those pages merged and dated; the demos are every listed entry in `demos.json` whose parent post is one of those write-ups. There is no per-project demo list to go stale, and `get_page` / `get_section` fail the build on a renamed post rather than rendering a dead link.

**Pages rather than one data file**, because each project needs a URL a recruiter can link directly and room for a real description. The plan also argued search indexing; that no longer applies, since site search is deliberately posts-only.

**Only the lead demo of each write-up gets a tile** — the first demo in that post, in the author's order (`build-demo-index.py` records each demo's position). A project page is an overview and the Playground already shows everything; mylearnbase alone owns eight demos, which as eight tiles would bury the page's subject. A link gives the full count. Tiles are the same `templates/_demo_tile.html` partial the Playground uses, so the tile's decisions (live preview vs. poster, the stretched link, no size label) live in one place.

**Repositories are linked only if public.** The boids working repository is private; its page links the public export, `boids-flocking-sim`. Check visibility before adding a `repo`, since a name is not evidence.

The write-up/demo association is computed in both templates (the page renders it, the hub counts it). Tera macros cannot return values, so sharing it would mean a data file for three records; the rule is one comparison, commented in both places.

### Résumé

`/resume/` is one document for two media: the page at `templates/resume.html`, and the downloadable PDF, which `scripts/build-resume-pdf.sh` prints from that same page through `static/css/resume-print.css`. The two can never state different facts.

**The content is structured data in the section's front matter, not markdown prose.** Each degree, role, skill group, project and award is a record. The first version was markdown, and its PDF looked like a web page on paper — three pages, dates on their own line, company and role merged with a dash — because markdown renders a role as a heading followed by a separate date paragraph, and CSS cannot reliably put those on one line. Records let the template put the organisation over the role with dates right-aligned, which is the layout a résumé reader scans. `build.sh`'s drift check still hashes `content/resume/_index.md`, so it survived the change untouched.

**The print sheet designs a document rather than stripping a web page**, and it self-hosts its typeface (Source Sans 3, OFL, 63KB, loaded only when the sheet applies). The site's own font is a system stack, which headless Chrome resolves to whatever the generating machine has installed, so without a bundled font the PDF's typeface silently depended on who ran the script.

**`extra.canonical_url` exists because the PDF build must lie about `base_url`.** The generator overrides `base_url` with localhost so the page loads CSS from disk, and anything reading `base_url` inherits that: the first structured version printed "127.0.0.1:1187" as the site address with six localhost links in the PDF. Anything that names the site on paper reads `canonical_url` instead, the template fails the build if the two disagree, and the PDF script fails if a localhost address appears in either the extracted text or the raw `/URI` link annotations. Both checks are needed: a raw byte search cannot read the compressed page text, and `pdftotext` never shows link targets.

**Copy must work on paper.** Nothing in the résumé may say "this site" or "here"; a printed page has no here.

### Homepage and header

**The homepage routes by what a visitor came for, not by how the writing is filed.** Under the profile sit three doors (Projects, Playground, Résumé) and a quieter link to `/posts/`; then a dated "Now" line; then the five latest posts. The doors are a `doors` array in `content/_index.md` with `@/` paths, so a renamed destination fails the build. The post-form guide moved to `/posts/`, where the reader has already chosen to read. `content/posts/_index.md`'s `guide` array is now the only list of forms: `posts_aggregator.html` iterates it for which forms appear, their order, and the line describing each.

**The "Now" line is the homepage's markdown body, and it is dated** (`now_updated`, printed as "Now · September 2026"). It is a claim about the present on a static page, the same failure mode as a résumé that says "present": true when written, false later, with nothing to say so. The printed date lets a reader judge it, and `build.sh` warns once it is 90 days old.

**The header is the real router, because most visitors land on a post and never see the doors.** `extra.nav` lists Projects · Playground · Posts · Résumé. On phones four items do not fit, so an item marked `phone = false` hides below 575px and the wordmark gives way to the logo mark. Posts is the item dropped because it is the one with other routes (the logo leads home to Latest, search finds any post, every post links related ones); the other three are reachable only from the header. Tags left the header at every width. **575px is measured, not a device guess:** the full row needs 505px of content width. Adding a nav item means measuring again. The mark is `static/img/logo.svg` inlined through `load_data`, so it takes `currentColor`; an `<img>` renders it black.

**Motion stays on the front door and the header; the reading surface stays still.** Two pieces, both pure CSS, and both written inside `@media (prefers-reduced-motion: no-preference)` so reduced motion has no rule to undo:

- **Logo hover** (and keyboard focus): the spark (`.logo-spark`) turns 15° and grows 10% while the base bar (`.logo-base`) widens 25%. Each shape needs `transform-box: fill-box`; SVG content otherwise transforms about the viewBox's top-left corner and the spark would swing off the mark. The transformed spark stays inside the 100×100 viewBox (checked on the painted outline, not the bounding box, which overstates a rotated shape), so the SVG's own clipping never cuts a tip.
- **Door stagger on load:** each door, then the Posts link, fades up 8px, 80ms apart. The fill mode is `backwards`: it holds the hidden first frame through each delay and then lets go. `both` would keep the last frame applied indefinitely, and an animation's value outranks the hover rule's `transform`, so the doors would stop lifting on hover. The largest paint on the homepage is the Now paragraph, which does not animate: Lighthouse is unchanged (99, LCP 1.8s, CLS 0).

### Page descriptions and the link-preview card

**A page's description is chosen in exactly one place, `templates/_head_extend.html`,** and feeds `<meta name="description">`, `og:description`, `twitter:description` and the JSON-LD `description` alike. No template fills the theme's `desc` block any more. Two chains used to exist and disagreed: `post.html` (the theme's) fell back to the `/posts/` section's description on every post, because it looks up `config.extra.blog_section_path` rather than the post's own form, while `_head_extend.html` fell back to `config.description`. Until September 2026 no post had a description of its own, so all of them shipped one of those two generic lines, and nothing reported it.

- **Branch order:** page, then taxonomy, then section. The taxonomy branch must come before `section` because the tag and series templates set a local `section` (the `/posts/` one) for layout config. Tag pages read "Posts on My Learn Base tagged “rust”"; list pages "Every tag used on My Learn Base."
- **A published page without `description` fails the build** (`throw` in the page branch). Fail rather than warn: this gap is introduced by an edit, unlike résumé drift or a stale Now line, which decay with time. Drafts fall back to `config.description`, so `zola serve --drafts` still previews one. A page never borrows its section's description, because a section describes a collection. **`zola check` does not catch it** (verified: it does not render templates); `zola build` and `zola serve` do.
- **The publish tools own the field too.** `logbook publish` and `workflows publish` take `--description`, keep it on republish (it lives on the post, not in the capture or source doc), and refuse before writing when a non-draft post would have none. `_frontmatter.py` unescapes basic strings on read; before that, a preserved value containing `"` gained backslashes on every republish.

**The link-preview card (`static/img/og-default.png`) is rendered from the site, not drawn once.** It used to be a one-off PNG with no source, so it kept the old tagline after the homepage changed. `scripts/build-og-card.py` fills `scripts/og-card.html` with `zola.toml`'s title and `canonical_url` host, `content/_index.md`'s `bio`, and `static/img/logo.svg`, screenshots it with headless Chrome, and writes the filled document's hash to `static/img/.og-card-hash`. `build.sh` runs it with `--check` and warns when the hash no longer matches. Local and committed for the same reason as the résumé PDF (no browser guaranteed in CI). The template's sizes were measured off the original card, which it reproduces to within a pixel; it names "DejaVu Sans" and the script refuses to render without that font rather than fall back silently.

---

## Project Structure

The project overrides a focused slice of the Serene theme rather than forking it. Anything in `templates/` here shadows the submodule's copy.

```
mylearnbase/
├── content/                      # see Content Organization
├── templates/                    # project overrides on top of Serene
│   ├── _base.html                # page shell, header nav
│   ├── home.html                 # homepage: hero flock, doors, Now line, Latest
│   ├── blog.html                 # section listing
│   ├── post.html                 # single post (prev/next, TOC, reader controls)
│   ├── posts_aggregator.html     # /posts cross-form index + form guide
│   ├── _head_extend.html         # the one description chain, OG/Twitter, JSON-LD, verification meta
│   ├── _footer.html
│   ├── robots.txt
│   ├── series/{list,single}.html # custom — theme ships no series templates
│   ├── tags/{list,single}.html
│   └── shortcodes/demo.html      # {{ demo() }} iframe embed
├── static/
│   ├── js/                       # header.js, reader-controls.js, search.js, hero-flock.js
│   ├── css/custom.css
│   ├── demos/<project>/<name>/   # self-contained interactive demos (concepts, mylearnbase)
│   ├── fonts/                    # OpenDyslexic (reader-controls typeface)
│   ├── img/                      # favicons, logo, og-default.png (rendered by scripts/build-og-card.py)
│   ├── llms.txt                  # crawl guidance for AI agents
│   └── giallo-*.css              # syntax-highlight CSS (generated; gitignored)
├── scripts/
│   ├── compute-related.py        # TF-IDF related posts → related.json (runs in build.sh)
│   ├── build-demo-index.py       # derived demo index → demos.json (runs in build.sh)
│   ├── build-resume-pdf.sh       # résumé page → committed PDF (local)
│   ├── capture-demo-posters.py   # Playground posters for heavy demos (local)
│   ├── build-og-card.py          # og-card.html → og-default.png (local; --check runs in build.sh)
│   └── seo-audit.sh              # SEO/meta audit
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

### The demo index — a derived mapping

`scripts/build-demo-index.py` walks the `demo()` shortcode calls in `content/posts/` and the demo directories in `static/demos/`, and writes `static/demos/_shared/demos.json`. It is a build artifact on the `related.json` model: gitignored, regenerated by `build.sh` before every `zola build`, and read by consumers that tolerate its absence.

**The mapping is derived rather than authored** because every fact it needs is already in the source: each demo is embedded by exactly one post, and that call already carries the caption, the height, and (through the post) the title and URL. A hand-written mapping would drift the moment a demo moved or a post was renamed, and it would drift *silently* — the link still renders, it just points somewhere wrong.

The script also reports what the site has never checked: **broken embeds** (a post naming a demo that does not exist) fail the build, because Zola cannot see them — the shortcode builds the iframe `src` at render time, so the result is an empty iframe on a published page and nothing else in the pipeline notices. **Orphans** and **draft-parented demos** only warn; both are legitimate states.

**Post URLs are resolved in Python, which duplicates Zola's routing** — the risky part. Runtime JavaScript has no access to Zola's page graph, so the URL has to be in the file rather than left as a content path for `get_page()` to resolve (the `related.json` approach). Two things keep the duplication honest: every post here declares an explicit `slug`, so the rule is just "section directories + slug"; and `build.sh` runs the script again after the build with `--verify public`, asserting every emitted URL exists in the output. A derivation that drifts fails the build instead of shipping back-links that 404.

### Standalone demo chrome

The same `index.html` is served two ways: iframed into its post, and on its own URL. Standalone it was a dead end — the demos deliberately load none of the site's CSS, so there was no chrome to extend and no link to anything.

`static/demos/_shared/demo-chrome.js`, one `<script defer>` line in each demo page, injects a bar carrying the site mark and a named destination ("Read how this works: *<post title>* →"). Copy that names the destination is the point; play → read is the conversion the Playground depends on.

**The load-bearing condition is `window.self !== window.top`.** Inside the iframe the script returns immediately, because there the bar would point at the page the reader is already on. Both halves need testing: checking only the standalone case would miss a bar duplicated into every embedded demo on the site.

**Push or float, decided by measurement.** The bar normally offsets the page (fixed bar plus padding on `<html>`) so it covers nothing. But a demo that sets `overflow: hidden` on `body` is declaring that it manages its own viewport — `how-search-works` pins a 100vh column that way — and offsetting that pushes its bottom row past the fold **with no way to scroll to it**. Where the page cannot scroll, the bar overlays as a corner pill instead. The choice is re-made on resize rather than hardcoded per demo, so a demo that drops its fixed-viewport model on narrow screens gets the better treatment there for free.

**A draft parent is omitted from `demos.json` entirely**, not flagged. The file is served publicly, so recording an unpublished post's title and URL would leak it, and the link would 404 anyway. The consumer sees an entry with no parent and renders brand-only chrome.

### The Playground

`/playground/` (`content/playground/_index.md` + `templates/playground.html`) is the gallery of every reader-facing demo, rendered from `demos.json`. The path is not `/demos/`: Zola copies `static/demos/` verbatim into `public/demos/`, so a section there would emit an `index.html` into a directory the static copier owns. The demo *files* stay at `/demos/…`, so no published post link changed.

**Light demos preview live; heavy demos show a captured still.** The ready-made `boids_*.gif` files the plan proposed as posters are 393-695KB each, *heavier than the 533KB WASM bundle they would have stood in for*, so they were never an option. A live preview cannot go stale and costs 9-26KB for each of the nine light demos. The three heavy ones (588-610KB) get a poster, because an empty card is the wrong reward for finding the best demos on the site.

**One rule decides both, and nothing is decided per demo.** `heavy` is derived from measured byte weight in `build-demo-index.py`; `scripts/capture-demo-posters.py` reads that flag rather than carrying a list. Adding a demo means running the build and the capture script — never making a judgment call. The threshold is reported on when a demo lands near it, so the first one in the gap prompts a look at the number rather than inheriting it.

**Posters are content-addressed, which is why there is no staleness check anywhere.** The filename carries a hash of the demo bundle that produced it (`concepts-how-search-works.90742d1843ef.webp`), and `demos.json` sets `poster` only when that exact file exists. Edit a demo and the expected filename stops existing: the tile falls back to the drawn card and the build reports that a poster needs recapturing. **A stale screenshot cannot be displayed.** That is strictly stronger than the résumé PDF's `.source-hash`, where drift warns but the stale file still ships — the difference being that here a working fallback exists. Cache-busting comes free.

Capture uses Chrome headless plus Pillow, both already required by the PDF pipeline. `--virtual-time-budget` fast-forwards the page clock so the shot is deterministic rather than racing a real sleep, which matters because two of these demos are WASM apps that mount into an empty div and then need their simulation to settle. `?poster=1` suppresses the back-link bar, which would otherwise be baked into the thumbnail. A capture with too few distinct colours is rejected rather than written, because a blank poster looks broken where the fallback card does not.

The preview is rendered at ~2.4× the tile's width and scaled down (`width: calc(100% / 0.42)` with a matching `transform: scale(0.42)`), so the thumbnail shows each demo's *desktop* layout in miniature rather than its narrow-screen fallback. That is what makes it read as a preview instead of a cramped embed.

**Heavy demos are derived, not listed.** Above 150KB a demo gets a drawn card and loads nothing until opened. The threshold sits in a wide gap: the light demos top out at 26KB, the heavy three are 588-610KB (two WASM bundles and a 564KB search corpus). Anything landing between those is a new situation worth a look rather than a silent bucketing.

**Clicking a tile opens the standalone demo** rather than activating an iframe in place. Demos are built for 600-900px of width and a grid tile is ~350px, so in-place activation would give the cramped version of the experience. Opening the real page also makes the standalone chrome load-bearing: gallery → demo → post is the route, and the bar is the return leg. The link is painted over the whole tile with `.pg-link::after`, because an `<a>` may not contain an `<iframe>` (interactive content) and so cannot wrap the tile directly.

**Sizes are stated on downloads, never on page links.** A heavy tile does not say "601 KB". "Heavy" exists to protect the *gallery's* weight — no 600KB demo loads on scroll — and once a visitor clicks, it is an ordinary page load, which nobody thinks of in bytes. The flock post itself loads 2.2MB of GIFs unlabelled, so a label on the tile would have warned about the cheaper route to the same demo. Downloads are the exception, because someone saving a file does think about what they are getting: the résumé's button reads "Download PDF (65 KB)". Zola has no template function that reads a file size, so `build.sh` measures every `static/**/*.pdf` into a gitignored `download-sizes.json` keyed by site URL — measured from the file being deployed, so it cannot disagree with what ships, and absent under a bare `zola serve`, where the button falls back to plain "Download PDF".

**Grouped by parent post, because the collection is lopsided.** Two posts own three demos each and five own one, so a flat grid opens with three near-identical SVG tiles and then three near-identical TF-IDF tiles. Grouping reads as one idea explored from several angles — and single-demo groups get a horizontal tile so they fill their row instead of leaving two dead cells under a heading.

**Known gap, pre-existing:** demos follow `prefers-color-scheme` while the site has its own theme toggle, so a visitor who toggles the site away from their OS setting sees light demos on a dark page. This already affects demos embedded in posts; the Playground only makes it visible eight tiles at once. Fixing it means teaching nine demo stylesheets a theme attribute, since a media query cannot be overridden from the host page.

### The homepage hero flock

`static/js/hero-flock.js` is the one interactive that is **not** an iframe demo: it renders directly onto a canvas behind the homepage hero, with the pointer acting as the predator.

It is a hand port of the flocking rules from the boids project's Rust core (`demo/boids-core/src/lib.rs`) — cohesion, separation, velocity-matching alignment, wall repulsion, and `flee` — running the tuned parameters from that project's `config.py`. It is the same simulation the *A Flock Is a Control Loop* post is about, not a lookalike.

**Why a re-implementation rather than embedding the real demo.** The shipped flock is a 533KB WASM bundle. That is a reasonable cost for a page a reader chose to open and an unreasonable one for a front door. The rules themselves are about forty lines, so re-implementing is cheaper and more honest than either embedding the bundle or faking the motion. The port is ~4.7KB gzipped, roughly 112× smaller.

**The parameters are a cross-repo dependency with no automated guard.** They originate in `~/life/masters_planning/projects/01_boids`, which is a separate repository and not a submodule here. It does not exist on the Cloudflare build machine, so there is no point in the build where both copies are in scope and no check can compare them. Retuning a rule there leaves this file silently stale. A comment in `hero-flock.js` is the only control, which is why that one is written to be hard to delete casually.

**Two calibration decisions worth not undoing**, both recorded inline:

- **Density, not count.** `POPULATION = 100` is tuned for a 1600×1200 world. A wide hero has roughly a third of that area, so carrying the number across triples the density and the flock collapses into a static separation lattice. The count is derived from world area instead.
- **Units-per-pixel is the fixed quantity** (`K = 1.25`), not the world width. Fixing the world width instead makes zoom a function of viewport width — 3px boids on a phone against 12px on a laptop. Holding `K` fixed keeps boid size, rule radii, and boids-per-pixel identical at every width; the world dimensions follow from the canvas. Measured: 81 boids/megapixel at 1280px, 80 at 375px.

Accessibility and cost: `prefers-reduced-motion: reduce` paints one settled frame and never starts the animation loop; the loop also stops on `visibilitychange` and when an `IntersectionObserver` reports the canvas off-screen.

**On the homepage** the canvas is full-bleed behind the profile and doors, clipped to a **top band**: solid above the text, faded out before the doors. The band is measured from the hero's top padding (`--hero-band`), not as a percentage of the hero as the prototype did. The hero is much taller on a phone, where the doors stack, and a percentage band grows with it until the flock sits over the text. Three wiring decisions:

- **The pointer is tracked on `window`, bounds-checked against the canvas.** The canvas sits behind content, so its own events stop wherever text or a door covers it, and the predator would vanish exactly over the doors. Touch is ignored, since a finger dragging to scroll is not hovering.
- **A `ResizeObserver` on the canvas, not a window resize listener.** The hero's height also changes when its content reflows, and a bitmap that no longer matches its box renders stretched.
- **The script is deferred.** Measured with Lighthouse (mobile, 4× CPU throttle), the flock costs 0ms of blocking time. The homepage scores 99–100 with or without it; the 0.1s first-paint difference from the old homepage comes from its added markup and CSS.

The design-review prototype stays at `/demos/mylearnbase/hero-flock/`, marked `noindex`, with the treatment switcher that chose the band.

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
