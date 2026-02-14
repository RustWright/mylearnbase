# Customizing the Theme

The site uses the [Serene](https://github.com/isunjn/serene) theme, installed as a git submodule. Customizations are made by **overriding** theme files, not editing the theme directly.

## The Override Pattern

Zola checks your project's directories first, then falls back to the theme:

```
templates/blog.html        ← Zola uses this (your override)
themes/serene/templates/blog.html  ← Ignored when override exists
```

To customize any theme template:
1. Find the original in `themes/serene/templates/`
2. Copy it to the same relative path in your project's `templates/`
3. Modify your copy

The theme's original stays untouched, so `git submodule update --remote` can pull theme updates without conflicts.

## Template Customization

### Modifying an Existing Template

Example: changing the back link text on the blog page.

1. The theme's `blog.html` has a generic back link
2. Copy `themes/serene/templates/blog.html` → `templates/blog.html`
3. Change the back link:
```html
<a id="back-link" href="{{ get_url(path="/") }}">← Home</a>
```

### Adding a New Taxonomy Template

Serene provides `tags/` templates but no `series/` templates. To add series support:

1. Create `templates/series/list.html` and `templates/series/single.html`
2. Model them after the existing `tags/` templates
3. Use the same `{% extends "_base.html" %}` pattern and CSS classes

The templates will automatically be used for URLs matching `/series/` and `/series/<name>/`.

## Style Customization

### SCSS Overrides

The `sass/` directory is currently empty. To override Serene's styles:

1. Find the SCSS file in `themes/serene/sass/`
2. Create a file with the same name in your `sass/` directory
3. Zola compiles yours instead of the theme's

### Inline Styles

For small, one-off tweaks, inline styles work in templates:
```html
<div id="series-info" style="margin-top: 0.5em; font-size: 0.9em;">
```

This is acceptable for minor additions but should be moved to SCSS as customizations grow.

## Theme Features (Controlled via Config)

These Serene features are toggled in `content/posts/_index.md` under `[extra]`:

| Feature | Setting | Current |
|---------|---------|---------|
| Table of contents | `toc` | `true` |
| Code copy button | `copy` | `true` |
| Comments (Giscus) | `comment` | `false` |
| Outdate alert | `outdate_alert` | `false` |

Site-wide features are in `zola.toml` under `[extra]`:

| Feature | Setting | Current |
|---------|---------|---------|
| Dark mode toggle | `force_theme = false` | Enabled |
| Emoji reactions | `reaction` | `false` |
| Footer credits | `footer_credits` | `true` |

## Updating the Theme

```bash
# Pull latest changes from Serene
git submodule update --remote themes/serene

# Test locally
zola serve

# If everything works, commit the submodule update
git add themes/serene
git commit -m "Update Serene theme"
```

> **Caution:** If Serene changes the structure of a template you've overridden, your override may break. Always test locally after updating.
