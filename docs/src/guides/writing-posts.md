# Writing a Post

## Quick Start

1. Create a new `.md` file in `content/posts/` using the naming convention `YYYY-MM-DD-post-slug.md`
2. Add the frontmatter (see template below)
3. Write your content in markdown
4. Run `zola serve` to preview
5. Push to GitHub to deploy

### File Naming Convention

Post files use a date prefix for easy chronological sorting:

```
content/posts/2026-02-11-building-my-learnbase-mvp.md
content/posts/2026-03-15-some-other-post.md
```

The date in the filename is for your convenience only — the `slug` field in frontmatter controls the actual URL, and the `date` field controls sort order. The filename itself doesn't affect the published site.

## Frontmatter Template

Copy this to start a new post:

```toml
+++
title = "Post Title"
slug = "post-title"
date = 2026-01-01
draft = false

[taxonomies]
tags = ["tag1", "tag2"]
series = ["Series Name"]      # Optional

[extra]
series_order = 1              # Optional, position in series
+++
```

See [Frontmatter Fields](../reference/frontmatter.md) for the full field reference.

## Writing Tips

### Headings

Use `##` (h2) and `###` (h3) for section headings. These automatically appear in the table of contents sidebar. Don't use `#` (h1) — the post title is already rendered as h1 by the template.

### Code Blocks

Fenced code blocks with language hints get syntax highlighting:

````markdown
```rust
fn main() {
    println!("Hello, world!");
}
```
````

A "copy" button appears automatically on code blocks (controlled by the `copy = true` setting in the blog section config).

### Images

Place images in the same directory as the post or in `static/`:

```markdown
![Alt text](image.png)
```

Images in `static/` are referenced from the site root: `![Alt text](/images/photo.png)`.

### Drafts

Set `draft = true` in frontmatter to hide a post from listings and feeds. It won't appear on the site but will still be accessible by direct URL during local development.

### Escaping Tera Template Syntax

If you write a post that includes Tera template code (e.g., documenting how your templates work), you must escape the `{{ }}` and `{% %}` syntax. Zola processes these as shortcodes/template directives even inside markdown code blocks.

**Escape rules:**
- Use `{{/*` and `*/}}` instead of `{{` and `}}`
- Use `{%/*` and `*/%}` instead of `{%` and `%}`

For posts with many template code blocks, it may be more practical to describe the changes and link to the full files in the repository rather than inlining the entire template content.

See the [Zola shortcodes documentation](https://www.getzola.org/documentation/content/shortcodes/#shortcodes-without-body) for details.

## Content Format

Posts follow a two-part format:

1. **Reflections/commentary** at the top — what you learned, why it matters, personal takeaways
2. **Tutorial-style steps** below — reproducible instructions others (or an AI) can follow

### Reflections Section

The reflections section is **always written by the human author**. When an LLM or AI tool is helping to generate or scaffold a post, the reflections section should be left blank with a placeholder comment for the author to fill in later:

```markdown
## Reflections

<!-- TODO: Write reflections/commentary section -->
```

This section is where the personal voice lives — it's not something that should be generated.

### Tutorial Section

The tutorial section should be detailed enough that a human or AI could follow the steps to reproduce the project from scratch. Include exact commands, file contents, version numbers, and assumptions about the environment.

This format is informal and will evolve with use.

## Using aipack for Post Generation

The [aipack](https://github.com/nickelpack/aipack) tool can generate post files from prompts. The `pro@coder` agent with `knowledge_globs` pointing to the frontmatter template works well for scaffolding posts.

```bash
# Preview (dry run)
aip run pro@coder -f "Create a blog post about X" --write_mode false

# Write the file
aip run pro@coder -f "Create a blog post about X" --write_mode true
```

Cost: approximately $0.03/run with Gemini Pro.
