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

The repo includes a pre-commit hook at `.githooks/pre-commit` that automatically sets the `updated` frontmatter field on any modified post. The hook runs on every commit and does the following:

1. Finds staged `.md` files in `content/posts/` that were modified (ignores `_index.md`)
2. Reads each file's last-modified date from the filesystem
3. Skips the file if that date matches the original `date` field (i.e. no update needed)
4. Inserts an `updated` field after `date` if one doesn't exist, or updates it if it does
5. Re-stages the file so the new frontmatter is included in the commit

The template already handles the display — if `updated` exists and differs from `date`, it renders "Updated on [date]" next to the publish date.

To enable the hook, configure git to use the tracked `.githooks/` directory:

```bash
git config core.hooksPath .githooks
```

This only needs to be run once per clone.

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
