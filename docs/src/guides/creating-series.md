# Creating a Series

Series group related posts into a multi-part sequence. They're implemented using Zola's taxonomy system.

## How to Add a Post to a Series

In the post's frontmatter, add the series name and order:

```toml
[taxonomies]
series = ["Building My Website"]

[extra]
series_order = 1
```

- **Series name** uses proper case in frontmatter (e.g., "Building My Website"). Zola auto-slugifies it for URLs → `/series/building-my-website/`.
- **`series_order`** determines the position within the series (1, 2, 3...).

## What Zola Generates Automatically

When at least one post references a series, Zola creates:

| Page | URL | Content |
|------|-----|---------|
| Series index | `/series/` | Lists all series names |
| Series detail | `/series/building-my-website/` | Lists all posts in that series |

These pages use the custom templates in `templates/series/`.

## What Appears on Post Pages

The `post.html` template checks if a post belongs to a series and displays:

> Part of series: [Building My Website](/series/building-my-website/)

This appears below the post's tags, linking readers to the full series listing.

## Creating a New Series

No configuration is needed — just use a new series name in a post's frontmatter:

```toml
[taxonomies]
series = ["New Series Name"]
```

Zola automatically creates the taxonomy pages. The series will appear on `/series/` as soon as at least one published (non-draft) post references it.

## Series Name Conventions

- Use proper case: `"Building My Website"` not `"building-my-website"`
- Keep names consistent across posts — exact string match is required
- The URL slug is auto-generated: `"Building My Website"` → `/series/building-my-website/`
