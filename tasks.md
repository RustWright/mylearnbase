# Tasks - Cycle 1 (MVP)

**Created:** 2026-02-03 (Session 3)
**Completed:** 2026-02-11 (Session 5)
**Objective:** Launch minimal viable blog with one post on mylearnbase.com

---

## Completed

### 1. Initialize Zola project with Serene theme ✓
- [x] Create new Zola project in project root
- [x] Install Serene theme (git submodule)
- [x] Verify `zola serve` works

### 2. Configure site settings ✓
- [x] Set site title, base URL (mylearnbase.com)
- [x] Configure dark mode (toggle, respects system preference)
- [x] Set up series taxonomy for multi-part posts
- [x] Configure RSS feed settings

### 3. Set up content structure ✓
- [x] Create homepage content (`content/_index.md`)
- [x] Create blog section (`content/posts/_index.md`)
- [x] Document frontmatter template for posts (`.frontmatter-template.md`)

### 4. Test aipack workflow ✓
- [x] Initialize aipack in project (`aip init`)
- [x] Create prompt to generate blog post file with frontmatter
- [x] Run preview (`write_mode: false`) — worked correctly
- [x] Run write (`write_mode: true`) — file created successfully
- [x] No issues encountered; workflow validated

### 5. Write first post content ✓
- [x] "Building My Learn Base - MVP" (series order 1)
- [x] 12-step tutorial covering full project recreation
- [x] Reflections section written by human author
- [x] Established post format: reflections + reproducible tutorial
- [x] File naming convention: `YYYY-MM-DD-post-slug.md`

### 6. Local verification ✓
- [x] Run `zola check` — no errors
- [x] Verify dark mode toggle works
- [x] Verify blog list page shows post
- [x] Verify series page works (with proper display name)
- [x] Verify RSS feed generates (`public/posts/rss.xml`)
- [x] Verify outdate alert works (tested with old date)
- [x] Verify 404 page works
- [x] Fixed: series link on posts, series page formatting, descriptive back buttons

### 7. Deploy to Cloudflare Pages ✓
- [x] Push repo to GitHub (RustWright/mylearnbase, public, HTTPS)
- [x] Connect repo to Cloudflare Pages
- [x] Build command: `curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz | tar xz && ./zola build`
- [x] Verify build succeeds and site accessible

### 8. Connect custom domain ✓
- [x] Onboarded domain to Cloudflare (migrated nameservers from Porkbun)
- [x] Added custom domain in Cloudflare Pages
- [x] Verified HTTPS works
- [x] Site live at https://mylearnbase.com

---

## Session 5 Additions (not in original plan)

### 9. Codebase walkthrough ✓
- [x] Reviewed all project files with human author
- [x] Explained template override system, content structure, config

### 10. Project documentation (mdBook) ✓
- [x] Created mdBook documentation (12 pages, 4 sections)
- [x] GitHub Actions workflow for auto-deploy to GitHub Pages
- [x] Updated PROJECT_PROCESS.md with documentation phase

### 11. Polish & cleanup ✓
- [x] Enabled GitHub-style alerts (Serene v5.6.0+ feature)
- [x] Removed placeholder test post
- [x] Documented Zola template escaping gotcha

---

## Notes

- **Theme strategy:** Start with Serene, cherry-pick features from Tabi/Abridge later
- **Content format established:** Reflections/commentary (human-only) at top, then tutorial steps
- **aipack role:** Testing workflow this cycle; heavier use planned for Cycle 2+ (WASM demos, repetitive generation)
- **aipack workflow validated:** `pro@coder` with knowledge_globs pointing to frontmatter template works well (~$0.03/generation with gemini-pro)
- **Documentation:** mdBook at docs/, deployed to GitHub Pages (requires one-time Pages enablement in repo settings)
