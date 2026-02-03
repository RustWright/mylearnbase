# Personal Website Project

**Status:** Active
**Started:** 2026-01-31
**Current Phase:** Ready for Session 3 - Planning (Cycle 1)
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
- [ ] Session 3: Planning (Cycle 1)
- [ ] Session 4: Implementation (Cycle 1)
- [ ] Session 5: Testing/Catchup (Cycle 1)

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
