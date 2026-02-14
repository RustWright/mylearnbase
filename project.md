# Personal Website Project

**Status:** Active
**Started:** 2026-01-31
**Current Phase:** Cycle 1 Complete — Ready for Session 3 (Cycle 2)
**Domain:** mylearnbase.com

---

## Session 1: Project Initiation

### 1. Project Goals

1. **Blog/Learning Journal**
   - Document processes when working on projects of interest
   - Series-based posts (multi-part, connected content)
   - Useful as personal reference and for others to replicate

2. **Portfolio**
   - Showcase completed work
   - Host interactive demos where possible
   - Allow visitors to engage with projects directly

3. **Monetization**
   - Organic revenue generation
   - Goal: Cover maintenance costs at minimum
   - No specific strategy yet - intentionally keeping this low-pressure

### 2. Primary User

**Primary:** Myself
- As **creator**: Easy to write, upload content, and deploy demos
- As **consumer**: Easy to revisit and reference past work

**Secondary (later):** Other learners, potential employers/clients

**Design Priority:** Authoring experience first. If it's frictionless for me to create, I'll create consistently. If I can find my own content easily, others can too.

### 3. Success Criteria

**Core Metric:** Creation friction so low that weekly publishing feels inviting, not burdensome.

**6-Month Targets:**
- [ ] 10+ articles published
- [ ] 3 demo projects hosted and interactive
- [ ] $1/week steady revenue (modest by design)

**Mindset Goal:** Focus on creation joy. Let monetization be a quiet background metric. Avoid the excitement→disappointment cycle from past projects.

### 4. Timeline & Availability

- **MVP Target:** Live within 4 weeks
- **Urgency Driver:** SEO indexing takes time - start the clock early
- **Perfection Mindset:** Not required. Needs will evolve with use.

**Weekly Availability (~13 hours):**
- Weekdays: 1 hour/day (5 hours total)
- Weekends: 2 sessions × 2 hours × 2 days (8 hours total)

### 5. Why This Project Matters Now

**The Pain:**
- Lost projects scattered everywhere, abandoned or never started
- Can't find old files, can't recreate past work
- Barely remember what was learned - no compounding benefit

**The Vision:**
- Stop treating projects as random attempts to forget
- Create something that compounds over time
- Enable reflection on past learning

**The Timing:**
- University in ~7 months
- Expecting many ideas and learning opportunities
- Want to be ready to document and share - with the world and with future self

**Note to Future Self:**
> "Think of all the cool projects we've built or tried to build in the past - abandoned, never started, forgotten. Making this website is a statement to change that. Our future selves will thank us for the effort we're putting in now, no matter how difficult it may feel when things get hard."

---

## Session Checklist

- [x] Session 1: Initiation (2026-01-31)
- [x] Session 2: Architecture (2026-02-01)
- [x] Session 3: Planning - FAILED (2026-02-01) - PoC revealed Dioxus SSG broken
- [x] Session 2b: Architecture Revision (2026-02-02)
- [x] Session 3: Planning (Cycle 1) (2026-02-03)
- [x] Session 4: Implementation (Cycle 1) (2026-02-04 to 2026-02-08)
- [x] Session 5: Testing/Catchup (Cycle 1) (2026-02-11)

---

## Session Log

### Session 1 - Initiation (2026-01-31)
- Defined three-part goal: blog, portfolio, monetization
- Identified self as primary user with focus on authoring experience
- Set 6-month targets: 10 articles, 3 demos, $1/week
- Timeline: MVP in 4 weeks, ~13 hours/week available
- Captured motivation: compound learning, gift to future self, university prep

### Session 2 - Architecture (2026-02-01)

**Key Decisions:**

| Decision | Choice | Alternatives Considered | Deciding Factor |
|----------|--------|------------------------|-----------------|
| Framework | Dioxus 0.7 (Rust) | React, Astro, other SSGs | Learning goal + cross-platform potential |
| Hosting | Cloudflare Pages | GitHub Pages, Vercel, Netlify | Free, global CDN, future Workers option |
| Backend (future) | Fly.io | Railway, Shuttle.rs | Dioxus docs recommend, generous free tier |
| Domain | mylearnbase.com | mycodepath.com, myskilldeck.com | Flexibility for non-code topics in future |
| Content format | Markdown + YAML frontmatter | Database, CMS | Simplicity, editor-friendly, portable |
| Content structure | Flat files + metadata | Folder-based hierarchy | Flexibility to reorganize without breaking links |
| Project structure | Minimal, evolve as needed | Pre-defined components/pages dirs | Avoid premature organization |

**MVP Scope:** Homepage, blog list, post pages, series grouping, basic styling, RSS, deploy pipeline. Deferred: portfolio, demos, monetization, comments, search.

**Testing Strategy:** Rust compiler + manual testing + content validation script. E2E deferred.

**Risks Reviewed:** Dioxus SSG maturity (mitigated), markdown processing (resolved), Cloudflare compatibility (resolved), workflow friction (monitor), scope creep (discipline).

**Proof-of-concept required:** Validate Dioxus + markdown + SSG + Cloudflare Pages works before full build.

**Standing review item:** Evaluate code structure refactoring needs each cycle.

### Session 3 - Planning (FAILED) (2026-02-01)

**Intended:** Begin cycle 1 planning with task breakdown.

**Actual:** User correctly insisted on PoC validation before planning. This revealed a critical blocker.

**PoC Results:**

| Component | Status | Finding |
|-----------|--------|---------|
| Dioxus dev server | WORKS | Serves app correctly |
| Dioxus fullstack/router | WORKS | Server functions execute |
| Dioxus SSG (`dx bundle --ssg`) | **BROKEN** | Outputs empty shell, no pre-rendered content despite `/static_routes` endpoint working |
| Zola SSG | WORKS | 195ms build, full pre-rendered HTML with markdown + syntax highlighting |

**Root Cause:** Dioxus 0.7 SSG feature appears non-functional or undocumented requirements exist. The `--ssg` flag doesn't trigger pre-rendering despite correct setup per documentation.

**Impact:** Dioxus cannot fulfill the SSG requirement for zero-cost hosting on Cloudflare Pages. Architecture revision required.

**Options Identified:**
1. **Zola (pure SSG)** - Mature, fast, native Cloudflare support
2. **Leptos SSG** - Experimental, not fully tested
3. **Hybrid (Zola + Rust WASM)** - Static content via Zola, interactive features via Dioxus/Leptos islands

**Decision:** Return to Session 2 for architecture revision before proceeding with planning.

**Artifacts:**
- `poc/` - Failed Dioxus SSG attempt (can be deleted)
- `poc-zola/` - Successful Zola SSG validation

### Session 2b - Architecture Revision (2026-02-02)

**Trigger:** Dioxus SSG PoC failed — framework decision invalidated.

**Key Decisions:**

| Decision | Original | Revised | Rationale |
|----------|----------|---------|-----------|
| Framework | Dioxus 0.7 | Zola | Dioxus SSG broken; Zola validated, mature |
| Backend | Fly.io (future) | Deferred entirely | Not needed for static site or client-side WASM |
| Future interactivity | Not defined | WASM islands (additive) | Self-contained demos embed into static pages |
| Testing | Rust compiler + validation script | `zola check` + manual + LLM screenshots | Simpler toolchain |

**Clarifications:**
- WASM islands are static files served by Cloudflare — no backend required
- Future interactivity is additive, not a rewrite
- Design paralysis identified as key risk — mitigate via theme selection in planning

**Note for Session 3:** Include theme selection as early task to unblock UI work.

### Session 3 - Planning (Cycle 1) (2026-02-03)

**Theme Decision:** Serene
- Dark mode support (required)
- Minimal, blog-focused
- Strategy: Start with Serene, cherry-pick features from Tabi/Abridge later

**Task Breakdown:** 8 tasks created in `tasks.md`
1. Initialize Zola + Serene
2. Configure site settings
3. Set up content structure
4. Test aipack workflow (validate tooling early)
5. Write first post ("Building My Website Part 1")
6. Local verification
7. Deploy to Cloudflare Pages
8. Connect custom domain

**Content Format (draft):** Posts will have reflections/commentary section at top, followed by tutorial-style reproducible steps. Will formalize after testing with first post.

**aipack:** Will test with simple task to validate workflow; heavier use deferred to Cycle 2+.

### Session 4 - Implementation (Cycle 1) (2026-02-04 to 2026-02-08)

**Completed 7 of 8 tasks** (Task 5 intentionally deferred):

| Task | Status | Notes |
|------|--------|-------|
| 1. Initialize Zola + Serene | ✓ | Git submodule, zola 0.22.1 |
| 2. Configure site settings | ✓ | Dark mode toggle, RSS, series/tags/categories taxonomies |
| 3. Set up content structure | ✓ | Homepage, posts section, frontmatter template |
| 4. Test aipack workflow | ✓ | pro@coder validated with Gemini Pro (~$0.03/run) |
| 5. Write first post | Deferred | Writing tutorial post after Session 5 when full process is documented |
| 6. Local verification | ✓ | All features verified including outdate alert, 404, series pages |
| 7. Deploy to Cloudflare Pages | ✓ | Custom build command (Zola not pre-installed on CF) |
| 8. Connect custom domain | ✓ | mylearnbase.com live, HTTPS working |

**Key decisions made during implementation:**
- Series taxonomy uses proper-case names in frontmatter (auto-slugified for URLs)
- Template overrides for descriptive back navigation ("Posts", "Home", "Tags" instead of generic "Back")
- Series link added to individual post pages
- `.log/` removed from public repo tracking
- aipack quick-reference guide created for future sessions

**Issues encountered:**
- Serene templates require certain `[extra]` fields even when features are disabled (outdate_alert_days)
- Cloudflare Pages no longer auto-installs Zola; manual download in build command required
- CSS missing on preview URL due to base_url mismatch (resolved by custom domain)

**Site live at:** https://mylearnbase.com

### Session 5 - Testing/Catchup (Cycle 1) (2026-02-11)

**Four phases completed:**

**Phase A — Codebase Walkthrough:**
- Walked through every file in the project: zola.toml, content structure, all 6 template overrides, static assets, theme submodule
- Identified how Serene's override system works and where each customization lives

**Phase B — Documentation (mdBook):**
- Chose mdBook over plain markdown, MkDocs, or Docusaurus for Rust ecosystem alignment and simplicity
- Created full documentation site: 12 pages across 4 sections (Getting Started, Architecture, Guides, Reference)
- Set up GitHub Actions workflow for auto-deployment to GitHub Pages
- Updated PROJECT_PROCESS.md to include documentation as formal Phase C in Session 5

**Phase C — First Post Written:**
- "Building My Learn Base - MVP" — series order 1 of "Building My Learn Base"
- 12-step tutorial detailed enough for human or AI to recreate the entire project from scratch
- Captures exact versions: Zola 0.22.1, Serene v5.6.1, mdBook 0.5.2, Rust 1.91.0
- Reflections section written by human author
- Established post format convention: reflections (human-only) + tutorial (reproducible steps)
- File naming convention adopted: `YYYY-MM-DD-post-slug.md`

**Phase D — Cleanup & Polish:**
- Enabled GitHub-style alerts (`> [!NOTE]`, `> [!IMPORTANT]`) via Serene v5.6.0+ support
- Removed placeholder test post
- Documented Zola template escaping gotcha in docs and project memory

**Key learnings captured:**
- Zola processes `{{ }}` / `{% %}` even inside code blocks — escape with `{{/*` `*/}}` syntax
- `{% raw %}` does NOT work (shortcode detection runs before Tera)
- For template-heavy posts, describe changes + link to repo rather than inline full templates

**Cycle 1 Status:** All 8 tasks complete. MVP live at https://mylearnbase.com
