# Content Structure

## Sections vs Pages

Zola has a two-level content system:

- **Sections** — defined by `_index.md` files. They set rules that apply to all pages within that directory.
- **Pages** — any other `.md` file. These are the actual content (blog posts, standalone pages).

```
content/
├── _index.md              ← Section: the homepage
└── posts/
    ├── _index.md          ← Section: configures the blog listing
    └── hello-world.md     ← Page: an individual post
```

The `_index.md` in `posts/` is not a post itself — it configures the entire section. Its `page_template = "post.html"` setting means every `.md` file in `content/posts/` automatically uses `post.html` as its template without you specifying it per post.

## Homepage (`content/_index.md`)

Uses the `home.html` template from Serene. Configured to show the 5 most recent posts. The markdown body after the frontmatter becomes the homepage description text.

Key settings:
- `recent = true` — shows recent posts
- `recent_max = 5` — limits how many
- `links = []` — no social links yet (can add GitHub, Twitter, etc.)

## Blog Section (`content/posts/_index.md`)

Configures how the blog listing and all posts behave:

- `sort_by = "date"` — newest posts first
- `template = "blog.html"` — the listing page template
- `page_template = "post.html"` — template for every post in this section
- `insert_anchor_links = "right"` — clickable `#` links appear beside headings
- `generate_feeds = true` — RSS feed for this section

The `[extra]` section controls Serene-specific features:
- `toc = true` — table of contents sidebar on posts
- `copy = true` — "copy" button on code blocks
- `outdate_alert = false` — staleness warning (disabled by default)

## Taxonomies

Taxonomies are Zola's grouping system. Three are configured:

| Taxonomy | Purpose | Example |
|----------|---------|---------|
| `tags` | Topic labels | `["rust", "zola", "web"]` |
| `categories` | Broad grouping | (not actively used yet) |
| `series` | Multi-part post sequences | `["Building My Website"]` |

When a post declares `tags = ["rust"]` in its frontmatter, Zola automatically:
1. Creates a page at `/tags/rust/` listing all posts with that tag
2. Creates a page at `/tags/` listing all tags

The same applies to series — `/series/building-my-website/` is auto-generated.

## File Naming

Post filenames don't affect URLs when a `slug` is set in frontmatter. The file `placeholder-test-post.md` with `slug = "hello-world"` produces the URL `/posts/hello-world/`.

This means you can rename or reorganize files without breaking links — the slug is what determines the URL.
