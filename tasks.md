# Tasks - Cycle 1 (MVP)

**Created:** 2026-02-03 (Session 3)
**Objective:** Launch minimal viable blog with one post on mylearnbase.com

---

## Pending

### 5. Write first post content — DEFERRED
Deferred to post-Session 5. Placeholder post created for pipeline verification.

### 7. Deploy to Cloudflare Pages — DONE (moved to completed)

### 8. Connect custom domain — DONE (moved to completed)

---

## In Progress

(none)

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

## Notes

- **Theme strategy:** Start with Serene, cherry-pick features from Tabi/Abridge later
- **Content format (draft):** Reflections/commentary section at top, then tutorial steps — will formalize after testing with first post
- **aipack role:** Testing workflow this cycle; heavier use planned for Cycle 2+ (WASM demos, repetitive generation)
- **aipack workflow validated:** `pro@coder` with knowledge_globs pointing to frontmatter template works well for generating posts (~$0.03/generation with gemini-pro)
