# UI Review Checklist

Design-quality + functional verification checklist for the mylearnbase site.
Modeled on `omni-me/ui-checklist.md`, content-shifted for a **static content site**.

Legend: `[ ]` not yet verified • `[x]` verified pass • `[!]` known issue/gap to fix

Last swept: 2026-06-14 (Sweep 3 — Cycle 3 Phase 2 SEO/AEO + Lighthouse)

---

## Test Environment

- **Local preview:** `zola serve` (serves at `http://127.0.0.1:1111`)
- **Static build:** `zola build` → `public/` (inspect rendered HTML directly)
- **Link check:** `zola check --skip-external-links`
- **SEO/AEO audit (one command):** `scripts/seo-audit.sh` — build + link check +
  root-resource checks + JSON-LD parse/`@type` across all pages + `<head>` social
  surface + Lighthouse SEO score (vs. a temp `zola serve`). Add `--online` to also
  POST pages to `validator.schema.org`. Exits non-zero on any failure (CI-friendly).
- **Visual audit:** headless screenshots via `google-chrome --headless --screenshot`
  at mobile / tablet / desktop widths (Playwright MCP if/when available).
- **Search (Pagefind):** `npx pagefind --site public` after build, then reload.
- **Themes:** test both light and dark (toggle persists via `sessionStorage`).

---

## Homepage (`/`)

- [x] Above-the-fold communicates what the site IS (tagline "I build things to learn — and write down how." + value-prop naming logbooks / workflows / interactive demos) — Sweep 2
- [x] Clear value proposition / hero — bold `#name`, tagline, value-prop paragraph — Sweep 2
- [x] Recent posts surface is scannable (title, form badge, date legible)
- [x] Social links present — GitHub + LinkedIn (`linkedin.com/in/efe-erhie`) both render in `#right` — Sweep 2
- [ ] Avatar / logo slot renders (placeholder acceptable until logo lands) — Phase 3
- [x] Theme toggle present and works
- [x] Visual hierarchy: eye lands on the most important thing first — Sweep 2 (hero → value-prop → guide → latest)
- [x] No awkward empty space / orphaned sections — "What you'll find here" guide fills the page; was sparse — Sweep 2
- [ ] Footer / copyright correct (homepage runs `footer = false`; verify on inner pages)

## Post page (`/posts/<form>/<slug>/`)

- [x] Readable line measure + line-height (long-form comfort)
- [ ] **Reading time** displayed (Tier 1 — `page.reading_time`) — _not yet built_
- [x] **Table of contents** for long posts — **Serene already ships this** (floating `<aside><nav>` of H2 anchors + back-to-top button on wide screens); verify nested H3 handling + mobile behavior, restyle if needed
- [ ] **Prev/next post navigation** (Tier 2) — _not yet built_
- [ ] **Reader controls: font-family picker + font-size adjust** (accessibility / far-sightedness) — _not yet built; new Cycle-3 feature_
- [ ] Code blocks render with syntax highlighting + copy button
- [ ] Callouts (`> [!NOTE]` etc.) render correctly
- [ ] `{{ demo() }}` shortcode iframes render (when present)
- [ ] KaTeX math renders (when `extra.math`)
- [ ] Mermaid diagrams render (when `extra.mermaid`)
- [ ] Series links + tags links resolve
- [ ] `superseded_by` banner renders when set
- [ ] Back-navigation label is descriptive

## List / aggregator pages

- [ ] `/posts/` split-by-form aggregator groups correctly (logbook / concepts / workflows / opinions / resources / archive)
- [ ] Each form section heading links to its section page
- [ ] Empty-form sections note "no content yet" gracefully
- [ ] Section pages (`/posts/logbook/` etc.) list their posts
- [ ] Tag landing + per-tag pages work

## Navigation & Search

- [ ] Header/nav links resolve (no 404s) — all 6 `extra.sections` entries
- [ ] Active section visually distinguished
- [ ] Instant-nav (`class="instant"`) works without full reload
- [ ] 404 page renders with recovery link
- [ ] **Site search (Pagefind)** present, returns results, keyboard-accessible (`/` focus, arrows, enter, esc) — _not yet built_

## Theme (light / dark)

- [ ] Light mode: all text meets contrast; brand `--primary-color` legible on bg
- [ ] Dark mode: parity; no unreadable elements; images dimmed appropriately
- [ ] No flash of wrong theme (FOUC) on load
- [ ] Syntax-highlight CSS swaps with theme (giallo-light / giallo-dark)
- [ ] Toggle persists across navigation

## Responsive (folds in mobile-responsivity item)

- [ ] **Mobile (~375px):** no horizontal scroll; nav reflows; tap targets ≥ ~44px
- [ ] **Tablet (~768px):** layout adapts at `--homepage-max-width` boundary
- [ ] **Desktop (~1280px):** content max-width sensible, not stretched
- [ ] Homepage `#info` / `#links` / recent-list reflow cleanly
- [ ] Code blocks scroll horizontally rather than break layout
- [ ] Images / demos scale within viewport

## Accessibility

- [ ] Images have meaningful `alt` text
- [ ] Color contrast passes WCAG AA (text + interactive, both themes)
- [ ] Visible focus states on links/buttons/inputs
- [ ] Keyboard navigation reaches all interactive elements
- [ ] Heading order is logical (single h1, no skipped levels)
- [ ] Theme toggle + search have accessible labels
- [ ] Reader font-size control lets low-vision / far-sighted readers scale text without browser zoom (new Cycle-3 feature) — _not yet built_
- [ ] Font-family picker offers a readable serif/sans/mono/dyslexia-friendly choice, persisted across pages — _not yet built_

## Performance

- [ ] Images sized appropriately (no oversized assets)
- [ ] No layout shift on load (CLS)
- [ ] Fonts load without blocking / FOUT jank
- [ ] `minify_html` output is clean
- [ ] No console errors or warnings

## SEO / Social surface (cross-checks Phase 2/3)

- [x] `<title>` + `<meta name="description">` present and per-page correct — Sweep 3 (Lighthouse SEO `document-title` + `meta-description` pass)
- [x] **OpenGraph + Twitter cards** render — Sweep 3 (text-only: og:site_name/title/description/type/url/locale + twitter:card/title/description; `og:image` deferred to Phase 3)
- [x] **JSON-LD** structured data present + parses — Sweep 3 (`BlogPosting` on leaf posts, `WebSite` on home/sections; all valid JSON). _Schema-field validity pending external validator — see below._
- [x] `<link rel="canonical">` present — Sweep 3 (per-page `page.permalink` / `section.permalink`)
- [ ] Favicon resolves (no 404) — `[!]` currently missing (Phase 3)
- [x] `sitemap.xml`, `robots.txt`, `llms.txt` reachable at root — Sweep 3 (`robots.txt` now custom AI-welcoming + production `Sitemap:`; `llms.txt` served)
- [ ] **Privacy analytics** snippet present (Tier 2) — _not yet built_

> **Objective verification, Sweep 3:** Lighthouse SEO category = **100/100** (10/10 auto-checks)
> against the local `zola serve` build. Lighthouse marks `structured-data` (JSON-LD schema
> validity) as *not-applicable / manual* — it does not validate schema fields. That single gap
> needs Google's Rich Results Test / schema.org validator, which require a **public URL** →
> folds into Phase 4 (post-deploy). JSON *parse* validity + correct `@type` are confirmed locally.

---

## Gaps / fixes (running list)

Confirmed by Sweep 1 (2026-06-14):

- `[!]` **Homepage has no hero / value-prop** — site name "My Learn Base" renders as plain text, same weight as nav; nothing communicates *learning journal + portfolio + interactive concept demos*. (Phase 1)
- `[!]` **Homepage is sparse / unfinished-feeling** — on desktop the content occupies the top third; large dead space below the recent-posts list. (Phase 1)
- `[!]` **No avatar / logo** — `section.extra.avatar` unset, slot empty. (Phase 1 placeholder → Phase 3 real logo)
- `[!]` **Homepage social links empty** (`links = []`) — no LinkedIn. (Phase 1)
- `[!]` **Recent-posts list lacks variety/differentiation** — all 5 are `[logbook]`; the concepts differentiator isn't teased; form badges are plain text, not visually distinct. (Phase 1)
- `[!]` **Reading time absent** on post pages. (Tier 1)
- `[!]` **Prev/next post nav absent.** (Tier 2)
- `[!]` **No reader font controls** (family picker + size adjust) — new Cycle-3 accessibility feature.
- `[!]` Favicon files referenced in `_base.html` but absent → **3× 404** (`favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`). (Phase 3)
- `[x]` ~~No OpenGraph/Twitter cards; no JSON-LD; no canonical.~~ **Resolved Phase 2 (Sweep 3)** — all present + verified; `og:image` waits on Phase 3.
- `[x]` ~~`llms.txt` 404; `robots.txt` is Zola's bare default.~~ **Resolved Phase 2 (Sweep 3)** — custom AI-welcoming `robots.txt` + `llms.txt` both served.
- `[!]` Site search disabled / not present (`build_search_index = false`). (Tier 1 — Pagefind)

Corrections to prior assumptions:

- `[x]` **TOC already exists** (Serene `<aside><nav>`) — reclassified from "build" to "verify/restyle".
- `[x]` **Responsive works** — mobile (375px) reflows nav to two rows, no horizontal scroll, recent-post dates stack above titles; tablet/desktop fine.
- `[x]` `sitemap.xml`, `rss.xml`, `robots.txt` all reachable (200).
- `[x]` Split-by-form aggregator (`/posts/`) groups correctly and renders "No posts in this form yet" gracefully for empty forms (concepts/opinions/resources).

---

## Verification Sweeps

### Sweep 1 — 2026-06-14 (Cycle 3 Phase 0 baseline)

**Method:** `zola build` (22 pages, 0 orphan, 8 sections — clean) + `zola check
--skip-external-links` (clean). `zola serve` + headless-Chrome screenshots of
homepage / post / aggregator at 375 / 768 / 1280px. Status-code probes for
favicon / robots / llms / sitemap / rss. Grep of rendered post HTML for
TOC / reading-time / prev-next markers.

**Homepage (`/`)**
- `[x]` Theme toggle present (sun icon), nav links all render, recent-posts list scannable (title · form-badge · date).
- `[x]` Responsive: nav reflows on mobile, no horizontal scroll, date/title stack cleanly.
- `[!]` No hero/value-prop · `[!]` sparse / dead space below fold · `[!]` no avatar/logo · `[!]` social links empty · `[!]` recent list is all-logbook, no differentiation.

**Post page (`/posts/logbook/omni-me/budget-setup-progress/`)**
- `[x]` Readable measure + line-height; code blocks syntax-highlighted (dark theme).
- `[x]` TOC `<aside>` of H2 anchors + back-to-top button render on wide screens.
- `[!]` No reading time · `[!]` no prev/next nav · `[!]` no reader font controls.
- _TODO_ verify copy-button, callouts, KaTeX/Mermaid on a post that uses them; verify TOC on mobile + with H3s.

**Aggregator (`/posts/`)**
- `[x]` Split-by-form grouping correct (logbook / concepts / workflows / opinions / resources / archive); empty forms show graceful "No posts in this form yet".

**Root resources**
- `[x]` `sitemap.xml` 200 · `rss.xml` 200 · `robots.txt` 200 (bare default).
- `[!]` favicon ×3 → 404 · `[!]` `llms.txt` → 404.

**Verdict → Phase 1 scope:** the homepage is functionally sound but *thin*. "Better"
= give it an identity (hero/value-prop naming the 3 things the site is), fill the
empty space with deliberately surfaced + differentiated content, add avatar/logo
slot, and populate social links. Reader-experience adds (reading time, font
controls) land on the post template. Search + SEO are their own phases.

### Sweep 2 — 2026-06-14 (Cycle 3 Phase 1 — homepage rework, "Build-and-document" framing)

**Changes shipped** (`content/_index.md`, `templates/home.html`, new
`static/css/custom.css`, new `templates/_head_extend.html`):
- Bold hero (`#name` styled — had no theme rule) + tagline (`bio`) + value-prop body.
- New data-driven **"What you'll find here"** guide (`section.extra.guide`) — each
  form linked with a one-line description; surfaces `concepts` even while empty.
- **"Latest"** heading added to the recent-posts block; spacing fix
  (`.layout-list .guide-title { margin-top }`) to separate it from the guide.
- GitHub social link wired (`https://github.com/RustWright`).
- `_head_extend.html` override created (loads `custom.css`; will also host Phase-2 SEO tags).

**Result:** `zola build` clean (22/0/8); homepage fills the viewport at 1280px with
minimal dead space; mobile (375px) reflows cleanly (guide grid collapses to single
column via `@media (max-width:425px)`).

**Still open on homepage:**
- `[x]` LinkedIn link — added (`https://www.linkedin.com/in/efe-erhie`).
- `[ ]` Avatar/logo slot — Phase 3 (placeholder or real logo).
- `[ ]` Light-mode visual confirm — custom CSS uses only theme variables + mode-independent
  props, so adaptation is by-construction; confirm in a real browser toggle.
- `[ ]` Form-badge differentiation in "Latest" (all `[logbook]` today; cosmetic — revisit
  when more forms have posts).

### Sweep 3 — 2026-06-14 (Cycle 3 Phase 2 — SEO/AEO plumbing + objective audit)

**Changes shipped** (new `templates/_head_extend.html` SEO body, `zola.toml [extra]`
author/verification keys, new `templates/robots.txt`, new `static/llms.txt`):
- Per-page `<link rel=canonical>`, OpenGraph (`og:site_name/title/description/type/url/locale`),
  Twitter card (`summary`) — context-aware via `page`/`section`/neither `is defined` guards.
- JSON-LD: `BlogPosting` on leaf posts (headline/url/dates/description/author), `WebSite`
  on home + section pages. All blocks emitted with `| json_encode | safe`.
- `robots.txt` → custom: general `Allow: /` + explicit welcome for GPTBot/ClaudeBot/
  PerplexityBot/Google-Extended/CCBot + production `Sitemap:` line.
- `llms.txt` → AEO summary with absolute post URLs + GitHub/LinkedIn/RSS.
- Verification `<meta>` slots (`google-site-verification`, `msvalidate.01`) gated on
  non-empty `[extra]` keys → emitted only once Phase 4 pastes the tokens.

**Verification method + results:**
- `zola build` clean (22 pages / 0 orphan / 8 sections).
- JSON-LD: extracted every `ld+json` block from `public/`, parsed with Python's `json` —
  **all valid**, correct `@type` per page kind, correct field values (verified dates, author URL).
- `robots.txt` renders the production `Sitemap:` URL; `llms.txt` served (200).
- **Lighthouse SEO category = 100/100** (`npx lighthouse --only-categories=seo` against
  `zola serve`); 10/10 automated audits pass.

**Known residue (not Phase-2 failures):**
- `og:image` / `twitter:image` intentionally deferred to Phase 3 (needs the share card).
- JSON-LD *schema-field* validity (vs. JSON-parse validity) needs Google Rich Results Test /
  schema.org validator — both require a public URL → Phase 4 post-deploy check.
- Favicon 404s persist (Phase 3, logo-dependent).
