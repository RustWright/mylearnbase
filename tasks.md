# Tasks - Cycle 1 (MVP)

**Created:** 2026-02-03 (Session 3)
**Objective:** Launch minimal viable blog with one post on mylearnbase.com

---

## Pending

### 1. Initialize Zola project with Serene theme
- [ ] Create new Zola project in project root
- [ ] Install Serene theme
- [ ] Verify `zola serve` works

### 2. Configure site settings
- [ ] Set site title, base URL (mylearnbase.com)
- [ ] Configure dark mode as default
- [ ] Set up series taxonomy for multi-part posts
- [ ] Configure RSS feed settings

### 3. Set up content structure
- [ ] Create homepage content (`content/_index.md`)
- [ ] Create blog section (`content/blog/_index.md`)
- [ ] Document frontmatter template for posts (reference for future writing)

### 4. Test aipack workflow
- [ ] Initialize aipack in project (`aip init`)
- [ ] Create prompt to generate blog post file with frontmatter
- [ ] Run preview (`write_mode: false`, `aip run pro@coder -s`)
- [ ] Review output
- [ ] Run write (`write_mode: true`)
- [ ] Document any issues encountered

**Note:** If aipack issues take too long to resolve, note them and proceed manually. Goal is to validate the workflow, not block on it.

### 5. Write first post content
- [ ] Draft "Building My Website Part 1" covering Sessions 1-2
- [ ] Structure: Reflections section (personal) + Tutorial steps (reproducible)
- [ ] Use session logs as source material
- [ ] Add to series taxonomy

### 6. Local verification
- [ ] Run `zola check` — no errors
- [ ] Verify dark mode works
- [ ] Verify blog list page shows post
- [ ] Verify series grouping works
- [ ] Verify RSS feed generates (`public/rss.xml`)
- [ ] Manual click-through of all pages

### 7. Deploy to Cloudflare Pages
- [ ] Push repo to GitHub (if not already)
- [ ] Connect repo to Cloudflare Pages
- [ ] Verify build succeeds
- [ ] Verify site accessible at Cloudflare preview URL

### 8. Connect custom domain
- [ ] Configure mylearnbase.com DNS in Cloudflare
- [ ] Add custom domain in Cloudflare Pages
- [ ] Verify HTTPS works
- [ ] Verify site accessible at https://mylearnbase.com

---

## In Progress

(none)

---

## Completed

(none)

---

## Notes

- **Theme strategy:** Start with Serene, cherry-pick features from Tabi/Abridge later
- **Content format (draft):** Reflections/commentary section at top, then tutorial steps — will formalize after testing with first post
- **aipack role:** Testing workflow this cycle; heavier use planned for Cycle 2+ (WASM demos, repetitive generation)
