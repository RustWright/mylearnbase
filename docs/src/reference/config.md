# Site Configuration

All site configuration lives in `zola.toml` at the project root.

## Core Settings

```toml
base_url = "https://mylearnbase.com"
title = "My Learn Base"
description = "A personal learning journal and portfolio"
default_language = "en"
theme = "serene"
```

| Field | Purpose |
|-------|---------|
| `base_url` | Used to generate all absolute URLs (RSS, sitemaps, canonical links) |
| `title` | Browser tab title, RSS feed title |
| `description` | Default meta description for pages that don't set their own |
| `theme` | Which theme directory to use (under `themes/`) |

## Build Settings

```toml
compile_sass = true
minify_html = false
build_search_index = false
generate_feeds = true
feed_filenames = ["rss.xml"]
```

| Field | Purpose | Current |
|-------|---------|---------|
| `compile_sass` | Compile `.scss` files into CSS | Enabled |
| `minify_html` | Compress HTML output | Disabled (easier to debug) |
| `build_search_index` | Generate client-side search index | Disabled |
| `generate_feeds` | Generate RSS/Atom feeds | Enabled |
| `feed_filenames` | Output filenames for feeds | `rss.xml` |

## Taxonomies

```toml
taxonomies = [{ name = "tags" }, { name = "categories" }, { name = "series" }]
```

Each entry tells Zola to look for this field in post frontmatter and auto-generate listing pages. Each taxonomy needs matching templates in `templates/<taxonomy_name>/`.

## Markdown Processing

```toml
[markdown]
external_links_target_blank = false
external_links_no_follow = true
external_links_no_referrer = true
smart_punctuation = false
```

| Field | Purpose |
|-------|---------|
| `external_links_target_blank` | Open external links in new tab |
| `external_links_no_follow` | Add `rel="nofollow"` to external links (SEO) |
| `external_links_no_referrer` | Add `rel="noreferrer"` to external links (privacy) |
| `smart_punctuation` | Convert `"quotes"` to curly quotes, `--` to em dash |

## Syntax Highlighting

```toml
[markdown.highlighting]
style = "class"
light_theme = "github-light"
dark_theme = "catppuccin-mocha"
```

`style = "class"` means code tokens get CSS classes instead of inline styles. This enables dynamic light/dark switching via the CSS files in `static/` (`giallo-light.css`, `giallo-dark.css`).

## URL Slugification

```toml
[slugify]
paths = "on"
taxonomies = "on"
anchors = "on"
```

Controls automatic URL-safe conversion. With all set to `"on"`:
- `/posts/My Post Title` → `/posts/my-post-title`
- Series "Building My Website" → `/series/building-my-website`
- `## My Heading` → `#my-heading`

## Theme-Specific Settings (`[extra]`)

```toml
[extra]
sections = [{ name = "posts", path = "/posts", is_external = false }]
blog_section_path = "/posts"
back_link_text = "Back"
force_theme = false
footer_copyright = "© 2026"
footer_credits = true
not_found_error_text = "404 Not Found"
not_found_recover_text = "« back to home »"
reaction = false
```

These are not read by Zola itself — they're a contract between your templates and the Serene theme. The theme's templates check these values with `{% if config.extra.reaction %}` style conditionals.

| Field | Purpose |
|-------|---------|
| `sections` | Navigation menu entries |
| `blog_section_path` | Tells Serene where the blog section lives |
| `force_theme` | Lock to light or dark (false = allow toggle) |
| `footer_copyright` | Copyright text in footer |
| `footer_credits` | Show "Powered by Zola & Serene" |
| `reaction` | Enable emoji reactions on posts |
