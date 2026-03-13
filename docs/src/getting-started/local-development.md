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

## Set Up Git Hooks

The repo includes a pre-commit hook that automatically sets the `updated` frontmatter field on any modified post. To enable it, configure git to use the tracked `.githooks/` directory:

```bash
git config core.hooksPath .githooks
```

This only needs to be run once per clone. After that, any time you commit a change to a post in `content/posts/`, the hook will insert or update the `updated` date in the frontmatter based on the file's last modified time. The template displays this as "Updated on [date]" next to the publish date.

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
