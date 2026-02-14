# Templates & Overrides

The project overrides 6 template files from the Serene theme. Some are modifications of existing theme templates; others are entirely new.

## Override vs Custom

| Template | Type | What it does |
|----------|------|-------------|
| `templates/blog.html` | Override | Blog listing page — changed back link to "Home" |
| `templates/post.html` | Override | Individual post — added series link display |
| `templates/tags/list.html` | Override | All tags page — changed back link to "Home" |
| `templates/tags/single.html` | Override | Single tag page — changed back link to "Tags" |
| `templates/series/list.html` | **Custom** | All series page — no theme equivalent exists |
| `templates/series/single.html` | **Custom** | Single series page — no theme equivalent exists |

## `blog.html` — Post Listing

Renders at `/posts/`. Lists all posts with title and date.

**Key customization:** The back link says `← Home` instead of the theme's generic text, so users know where they're navigating.

The template supports two display modes controlled by `section.extra.categorized`:
- `categorized = false` (current) — flat list of posts sorted by date
- `categorized = true` — posts grouped by their first category

## `post.html` — Individual Post

The most complex template. It handles:

1. **Syntax highlighting CSS** — loads `giallo-light.css` or `giallo-dark.css` based on theme
2. **KaTeX math** — only loaded when `page.extra.math = true` (keeps pages lightweight)
3. **Table of contents** — auto-generated sidebar from h2/h3 headings
4. **Back-to-top button** — appears on scroll
5. **Back navigation** — `← Posts` link
6. **Post metadata** — publish date, update date, tags with links
7. **Series link** — "Part of series: Building My Website" with clickable link
8. **Outdate alert** — configurable warning for old posts
9. **Post content** — the rendered markdown
10. **Reactions & comments** — both disabled currently

**The series link (lines 117-124) is the most significant customization.** Serene doesn't natively display series information on posts. This block checks if a post has a `series` taxonomy and renders a link to the series listing page.

```html
{% if page.taxonomies.series is defined %}
<div id="series-info" style="margin-top: 0.5em; font-size: 0.9em;">
  {% for s in page.taxonomies.series -%}
  {% set series_slugify = s | slugify -%}
  Part of series: <a class="instant" href="{{ config.base_url ~ '/series/' ~ series_slugify }}">{{ s }}</a>
  {%- endfor %}
</div>
{% endif %}
```

## `series/` — Fully Custom Templates

Serene has tag templates but no series templates. These were created from scratch, modeled after the tag templates:

- **`series/list.html`** — Renders at `/series/`. Shows all series names as links.
- **`series/single.html`** — Renders at `/series/building-my-website/`. Lists all posts in a specific series with titles and dates.

Both use the same Tera template inheritance (`{% extends "_base.html" %}`), block structure, and CSS classes as the theme's tag templates so they blend in visually.

## `tags/` — Modified Theme Templates

These override Serene's tag templates with one change: **descriptive back navigation**.

- `tags/list.html`: back link goes `← Home` (instead of generic)
- `tags/single.html`: back link goes `← Tags` (instead of generic)

## Static Assets

| File | Purpose |
|------|---------|
| `static/giallo-light.css` | Syntax highlighting colors for light mode |
| `static/giallo-dark.css` | Syntax highlighting colors for dark mode |

These exist because `zola.toml` sets `style = "class"` for syntax highlighting. Zola wraps code tokens in CSS classes, and these stylesheets provide the colors. The Serene theme's JavaScript swaps between them when the user toggles dark/light mode.

## `sass/` — Style Overrides

Currently empty (contains only `.gitkeep`). To override Serene's styles, create `.scss` files here matching the theme's sass file names. Zola compiles yours instead of the theme's.
