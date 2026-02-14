# Local Development

## Clone the Repository

```bash
# Clone with submodules (important — the theme is a submodule)
git clone --recurse-submodules https://github.com/RustWright/mylearnbase.git
cd mylearnbase
```

If you already cloned without `--recurse-submodules`:
```bash
git submodule update --init
```

## Run the Dev Server

```bash
zola serve
```

This starts a local server at `http://127.0.0.1:1111` with **live reload** — any changes to content, templates, or styles automatically rebuild and refresh the browser.

## Project Structure

```
mylearnbase/
├── zola.toml              # Site configuration
├── content/               # Markdown content (what you write)
│   ├── _index.md          # Homepage
│   └── posts/
│       ├── _index.md      # Blog section config
│       └── *.md           # Individual posts
├── templates/             # Template overrides (customizations)
├── themes/serene/         # Serene theme (git submodule — don't edit)
├── sass/                  # SCSS style overrides (currently empty)
├── static/                # Static files copied as-is to output
├── public/                # Build output (gitignored)
└── docs/                  # This documentation (mdBook)
```

## Build for Production

```bash
zola build
```

Output goes to `public/`. This is what gets deployed to Cloudflare Pages.

## Check for Errors

```bash
zola check
```

Validates internal links, external links, and configuration without building the full site.
