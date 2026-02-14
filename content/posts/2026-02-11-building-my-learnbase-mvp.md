+++
title = "Building My Learn Base - MVP"
slug = "building-my-learnbase-mvp"
date = 2026-02-11
draft = false

[taxonomies]
tags = ["zola", "cloudflare", "web", "meta"]
series = ["Building My Learn Base"]

[extra]
series_order = 1
+++

## Reflections

I'm still figuring out what I want in this section, so these first few reflections might be a bit rough.

I made this website essentially for my future self. I noticed that I'd work on cool projects, but once I was done and on to the next thing, I'd forget most — if not all — of what I had worked on. That was actually kind of sad when I stopped to think about it.

If I'm able to stay motivated enough to keep documenting everything I work on, maybe some of this content will be useful to a few other people out there. That's the hope anyway. So if you're someone other than me reading this, it means it somehow worked.

This is the first official post. As you can see, each post will be structured with some commentary up top (which you can skip if you just want the tutorial).

The entire project was built with heavy facilitation from my current [Claude Code](https://docs.anthropic.com/en/docs/claude-code) setup, including Brave Search and Gemini CLI MCP servers. That setup might end up being the next series I write — I'll link to it here if I do.

I originally wanted to build this with [Dioxus](https://dioxuslabs.com/) and host the static files on AWS, since I've deployed Gatsby sites to S3 buckets before. But some proof-of-concept testing with Dioxus didn't give encouraging results, so rather than getting lost in design paralysis, I moved on to my fallback: Zola. I'm glad I did — the experience so far has been wonderful.

I still plan on using Dioxus in the future, but for desktop/mobile native apps or web applications that actually need a server.

That brings up another point: I went with an SSG partly for cost reasons. I don't expect to make money from this website — at least not anytime soon — and I didn't want to start with that goal in mind. Whenever I've approached projects that way in the past, I tend to get frustrated and give up early if returns don't come fast. So I'm treating this as a personal project, letting my interests dictate the pace and direction.

SSGs can be deployed on most CDNs for cheap or practically free, especially when starting out. And if I ever need server-side functionality, I can add it later without a rewrite.

---

## Tutorial: Recreating the MVP from Scratch

This tutorial walks through building the My Learn Base website from zero to a live, deployed site with documentation. Every step, file, and configuration is included — enough for a human or AI to reproduce the project without guesswork.

### What You'll End Up With

- A static blog site built with Zola, using the Serene theme
- Dark/light mode toggle, syntax highlighting, RSS feed
- Series and tag taxonomies for organizing posts
- Deployed to Cloudflare Pages with automatic builds on push
- Project documentation built with mdBook, deployed to GitHub Pages
- Custom domain with HTTPS

### Assumptions

- **Operating system:** Linux (tested on Ubuntu 22.04 LTS, x86_64)[^os]
- **Shell:** Bash
- **Accounts you'll need:** GitHub (free), Cloudflare (free tier)
- **Domain:** You have a domain name ready to use (this tutorial uses `mylearnbase.com`)

[^os]: macOS should work identically for all commands. Windows users should use WSL2.

---

### Step 1: Install Prerequisites

#### Zola (v0.22.1)

Zola is the static site generator. It's a single binary with no dependencies.

```bash
# Download and extract
curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz | tar xz

# Move to a directory in your PATH
sudo mv zola /usr/local/bin/

# Verify
zola --version
# Expected: zola 0.22.1
```

#### Git (v2.34+)

```bash
git --version
# If not installed: sudo apt install git
```

#### Rust / Cargo (for mdBook only)

Only needed if you want the documentation site. Skip if you only want the blog.

```bash
# Install Rust via rustup (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify
rustc --version
# Tested with: rustc 1.91.0
```

#### mdBook (v0.5.2)

```bash
cargo install mdbook

# Verify
mdbook --version
# Expected: mdbook v0.5.2
```

---

### Step 2: Create the Zola Project

```bash
mkdir mylearnbase
cd mylearnbase
git init
```

#### Install the Serene Theme

The theme is installed as a git submodule so it can be updated independently.

```bash
git submodule add https://github.com/isunjn/serene.git themes/serene
```

This creates a `.gitmodules` file automatically:

```
[submodule "themes/serene"]
	path = themes/serene
	url = https://github.com/isunjn/serene.git
```

At the time of writing, Serene is at version **v5.6.1** (commit `169763a`). You can pin to this exact version:

```bash
cd themes/serene
git checkout v5.6.1
cd ../..
```

---

### Step 3: Configure the Site (`zola.toml`)

Create `zola.toml` in the project root with the following content. This is the central configuration file — every setting is explained inline.

```toml
# Site configuration
base_url = "https://mylearnbase.com"
title = "My Learn Base"
description = "A personal learning journal and portfolio"
default_language = "en"
theme = "serene"
compile_sass = true
minify_html = false
build_search_index = false
generate_feeds = true
feed_filenames = ["rss.xml"]
taxonomies = [{ name = "tags" }, { name = "categories" }, { name = "series" }]

[markdown]
external_links_target_blank = false
external_links_no_follow = true
external_links_no_referrer = true
smart_punctuation = false

[markdown.highlighting]
style = "class"
light_theme = "github-light"
dark_theme = "catppuccin-mocha"

[slugify]
paths = "on"
taxonomies = "on"
anchors = "on"

[extra]
sections = [
  { name = "posts", path = "/posts", is_external = false },
]
blog_section_path = "/posts"

back_link_text = "Back"
force_theme = false

footer_copyright = "© 2026"
footer_credits = true

not_found_error_text = "404 Not Found"
not_found_recover_text = "« back to home »"

reaction = false
```

Key choices:
- **`theme = "serene"`** — tells Zola to look in `themes/serene/` for templates, sass, and static files
- **`style = "class"`** — uses CSS classes for syntax highlighting, enabling dynamic light/dark switching[^giallo]
- **Three taxonomies** — `tags`, `categories`, and `series` for grouping posts
- **`force_theme = false`** — allows the dark/light mode toggle

[^giallo]: When `style = "class"` is set, `zola build` auto-generates `giallo-light.css` and `giallo-dark.css` in `static/`. These provide the syntax colors for code blocks. You don't need to create them manually.

---

### Step 4: Create the Content Structure

#### Homepage (`content/_index.md`)

```bash
mkdir -p content/posts
```

Create `content/_index.md`:

```markdown
+++
template = "home.html"

[extra]
lang = "en"
name = "My Learn Base"
links = []
footer = false
recent = true
recent_max = 5
recent_more_text = "more posts »"
date_format = "%b %-d, %Y"
+++

A personal learning journal — documenting projects, experiments, and things I find interesting.
```

This uses Serene's `home.html` template. The `[extra]` fields are Serene-specific — `recent = true` displays the latest posts on the homepage.

#### Blog Section (`content/posts/_index.md`)

Create `content/posts/_index.md`:

```markdown
+++
title = "Posts"
description = "Learning journal and project documentation"
sort_by = "date"
template = "blog.html"
page_template = "post.html"
insert_anchor_links = "right"
generate_feeds = true

[extra]
lang = "en"
title = "Posts"
subtitle = "Learning journal and project documentation"
date_format = "%b %-d, %Y"
categorized = false
back_to_top = true
toc = true
comment = false
copy = true
outdate_alert = false
outdate_alert_days = 120
outdate_alert_text_before = "This article was last updated "
outdate_alert_text_after = " days ago and may be out of date."
+++
```

This file is not a post — it configures the entire `/posts/` section. `page_template = "post.html"` means every post in this directory automatically uses that template.

> [!IMPORTANT]
> The `outdate_alert_days` field must be present even when `outdate_alert = false`. Serene's templates reference it unconditionally, and omitting it causes a build error.

#### Frontmatter Template (`content/posts/.frontmatter-template.md`)

Create a reference template for future posts at `content/posts/.frontmatter-template.md`:

```markdown
# Post Frontmatter Template

Copy this to start a new post:

\```toml
+++
title = "Post Title"
slug = "post-title"           # Determines URL, never change once published
date = 2026-01-01
draft = false

[taxonomies]
tags = ["tag1", "tag2"]
series = ["series-name"]      # Optional, for multi-part content

[extra]
series_order = 1              # Optional, position in series
+++
\```

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| title | Yes | Post title (can change without breaking links) |
| slug | Yes | URL path — never change once published |
| date | Yes | Publication date (YYYY-MM-DD) |
| draft | No | Set `true` to hide from listings |
| updated | No | Last updated date |

## Taxonomies

| Taxonomy | Description |
|----------|-------------|
| tags | Topic tags (e.g., "rust", "zola", "web") |
| series | Multi-part post grouping |

## Extra (optional)

| Option | Description |
|--------|-------------|
| series_order | Position within a series (1, 2, 3...) |
```

The leading dot (`.`) in the filename hides it from Zola — it won't be processed as a page.

---

### Step 5: Create Template Overrides

Zola uses a layered override system: files in your project's `templates/` directory take priority over the theme's versions. This lets you customize without editing the theme.

```bash
mkdir -p templates/series templates/tags
```

We need 6 template files. The approach: copy each template from `themes/serene/templates/`, then make targeted modifications. The full file contents are available in the [project repository](https://github.com/RustWright/mylearnbase/tree/main/templates) and in the [project documentation](https://rustwright.github.io/mylearnbase/architecture/templates.html).

#### Overriding Theme Templates (4 files)

Copy these from the Serene theme and modify:

```bash
# Copy the originals
cp themes/serene/templates/blog.html templates/blog.html
cp themes/serene/templates/post.html templates/post.html
cp themes/serene/templates/tags/list.html templates/tags/list.html
cp themes/serene/templates/tags/single.html templates/tags/single.html
```

**Modifications to `templates/blog.html`:**

Change the back link to say "Home" instead of the generic theme text:

```html
<a id="back-link" href="...">← Home</a>
```

**Modifications to `templates/post.html`:**

1. Change the back link to `← Posts`
2. Add a **series link** block after the tags section. This is the most significant customization — Serene doesn't natively show series information on post pages. Add this block after the closing `</div>` of the `#tags` div:

```html
<div id="series-info" style="margin-top: 0.5em; font-size: 0.9em;">
  Part of series: <a href="/series/series-slug">Series Name</a>
</div>
```

The actual template uses Tera syntax to dynamically generate the series link from the post's taxonomy data. See the full file in the repository for the exact implementation.[^tera-escape]

**Modifications to `templates/tags/list.html`:**

Change the back link to `← Home`.

**Modifications to `templates/tags/single.html`:**

Change the back link to `← Tags`.

#### Creating Custom Series Templates (2 files)

Serene has no series templates — these are built from scratch, modeled after the tag templates:

- **`templates/series/list.html`** — Renders at `/series/`, lists all series names as links. Back link goes to Home.
- **`templates/series/single.html`** — Renders at `/series/<series-name>/`, lists all posts in a series with titles and dates. Back link goes to Posts.

Both follow the same pattern as the tag templates: extend `_base.html`, use the same CSS classes (`layout-list`, `post-list`, `tags`), and include the standard footer. Copy `templates/tags/list.html` and `templates/tags/single.html` as starting points and adjust the title, description, and variable names (`terms`/`term` stay the same since Zola uses these for all taxonomies).

[^tera-escape]: Tera template syntax (`{{/*..*/}}` and `{%/*...*/%}`) inside Zola markdown content requires special escaping, which makes it impractical to inline full template files in blog posts. This is a known Zola limitation — see the [shortcodes documentation](https://www.getzola.org/documentation/content/shortcodes/#shortcodes-without-body) for escape syntax details.

---

### Step 6: Verify Locally

```bash
zola serve
```

Open `http://127.0.0.1:1111` in your browser. Verify:

- [ ] Homepage loads with site description
- [ ] Dark/light mode toggle works
- [ ] Posts listing shows at `/posts/`
- [ ] Individual post pages render correctly
- [ ] Table of contents appears on posts
- [ ] Code blocks have syntax highlighting and a copy button
- [ ] Tags link to `/tags/<tag-name>/`
- [ ] Series link appears on post pages and links to `/series/<series-name>/`
- [ ] RSS feed is accessible at `/posts/rss.xml`
- [ ] 404 page works (visit any nonexistent URL)

---

### Step 7: Set Up Git & GitHub

#### `.gitignore`

Create `.gitignore`:

```
# Zola build output
public/

# Syntax highlighting CSS (auto-generated by zola build)
static/giallo-*.css

# mdBook build output
docs/book/

# Build outputs (future)
target/
dist/

# OS files
.DS_Store
Thumbs.db
```

Add any project-specific ignores as needed (e.g., `.log/`, `.archive/`, tooling directories).

#### Create the GitHub Repository

```bash
# Create repo on GitHub (requires GitHub CLI, or do this in the GitHub web UI)
gh repo create mylearnbase --public --source=. --remote=origin

# Or if you created the repo on GitHub's website:
git remote add origin https://github.com/YOUR_USERNAME/mylearnbase.git
```

#### Initial Commit

```bash
git add .
git commit -m "Initial site setup: Zola + Serene theme with series taxonomy"
git push -u origin main
```

---

### Step 8: Deploy to Cloudflare Pages

1. Log into the [Cloudflare dashboard](https://dash.cloudflare.com/)
2. Go to **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Select your GitHub repository
4. Configure the build:

| Setting | Value |
|---------|-------|
| Production branch | `main` |
| Build command | `curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz \| tar xz && ./zola build` |
| Build output directory | `public` |

5. Click **Save and Deploy**

> [!NOTE]
> **Why the custom build command?** As of early 2026, Cloudflare Pages no longer pre-installs Zola in its build environment. The command downloads the Zola binary directly before building. This adds ~3-5 seconds to each build.

---

### Step 9: Connect a Custom Domain

This assumes you have a domain registered with any registrar.

1. **Migrate DNS to Cloudflare** (if not already there):
   - In Cloudflare dashboard, go to **Websites** → **Add a site**
   - Enter your domain name
   - Cloudflare will provide nameservers — update these at your registrar[^dns]

2. **Add custom domain to Pages:**
   - Go to your Pages project → **Custom domains** → **Set up a custom domain**
   - Enter your domain (e.g., `mylearnbase.com`)
   - Cloudflare configures DNS automatically since it manages the domain

3. **Verify HTTPS:**
   - Visit `https://yourdomain.com` — should load with a valid certificate
   - Cloudflare provisions HTTPS automatically, but it may take a few minutes on first setup

[^dns]: DNS propagation can take up to 48 hours but usually completes within a few hours.

---

### Step 10: Set Up Project Documentation (mdBook)

#### Initialize

```bash
mdbook init docs --title "My Learn Base Documentation"
```

This creates:

```
docs/
├── book.toml
└── src/
    ├── SUMMARY.md
    └── chapter_1.md    ← Delete this, we'll replace it
```

#### Configure `docs/book.toml`

```toml
[book]
title = "My Learn Base Documentation"
authors = ["Your Name"]
language = "en"
src = "src"

[build]
build-dir = "book"
```

#### Write `docs/src/SUMMARY.md`

This file defines the sidebar navigation. Each entry is a link to a markdown file:

```markdown
# Summary

[Introduction](./introduction.md)

# Getting Started

- [Prerequisites](./getting-started/prerequisites.md)
- [Local Development](./getting-started/local-development.md)
- [Deployment](./getting-started/deployment.md)

# Architecture

- [Overview](./architecture/overview.md)
- [Content Structure](./architecture/content-structure.md)
- [Templates & Overrides](./architecture/templates.md)

# Guides

- [Writing a Post](./guides/writing-posts.md)
- [Creating a Series](./guides/creating-series.md)
- [Customizing the Theme](./guides/customizing-theme.md)

# Reference

- [Frontmatter Fields](./reference/frontmatter.md)
- [Site Configuration](./reference/config.md)
- [Cloudflare Deployment](./reference/cloudflare.md)
```

Create the directory structure and write the documentation pages. See the project's `docs/src/` directory for the full content of each page.

#### Build and Verify Locally

```bash
mdbook build docs
mdbook serve docs
# Opens at http://localhost:3000
```

---

### Step 11: Deploy Documentation to GitHub Pages

#### Create the GitHub Actions Workflow

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install mdBook
        uses: peaceiris/actions-mdbook@v2
        with:
          mdbook-version: 'latest'

      - name: Build documentation
        run: mdbook build docs

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/book

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{/* steps.deployment.outputs.page_url */}}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

#### Enable GitHub Pages

1. Go to your repository on GitHub → **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**

After pushing, the documentation will be available at `https://YOUR_USERNAME.github.io/mylearnbase/`.

---

### Step 12: Verify Everything

At this point you should have:

- [x] Zola site building locally with `zola serve`
- [x] Site deployed to Cloudflare Pages at your custom domain
- [x] Dark/light mode, syntax highlighting, RSS, series, tags all working
- [x] mdBook documentation building locally with `mdbook serve docs`
- [x] GitHub Actions workflow for auto-deploying docs to GitHub Pages

Push any remaining changes:

```bash
git add .
git commit -m "Complete MVP: site, documentation, and deployment pipelines"
git push
```

---

### Version Reference

All software versions used in this build:

| Tool | Version | Purpose |
|------|---------|---------|
| Zola | 0.22.1 | Static site generator |
| Serene | v5.6.1 (commit `169763a`) | Blog theme |
| mdBook | 0.5.2 | Documentation generator |
| Rust | 1.91.0 | Required for mdBook installation |
| Git | 2.34.1+ | Version control |
| Ubuntu | 22.04 LTS | Development OS |
