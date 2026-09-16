# UI Review Checklist

Design-quality + functional verification checklist for the mylearnbase site.
Modeled on `omni-me/ui-checklist.md`, content-shifted for a **static content site**.

Legend: `[ ]` not yet verified • `[x]` verified pass • `[!]` known issue/gap to fix

Last swept: 2026-09-16 (Sweep 8, Cycle 6: audience routing, destination surfaces, motion, post descriptions)

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

- [x] Above-the-fold communicates what the site IS — Sweep 8: tagline "I build things to learn, then write down how." over the hero flock, then three intent doors (Projects / Playground / Résumé), all visible without scrolling at 375px. The old value-prop paragraph is now the `/posts/` subtitle.
- [x] Clear value proposition / hero — bold `#name`, tagline, value-prop paragraph — Sweep 2
- [x] Recent posts surface is scannable (title, form badge, date legible)
- [x] Social links present — GitHub + LinkedIn (`linkedin.com/in/efe-erhie`) both render in `#right` — Sweep 2
- [x] Avatar / logo slot renders — Sweep 5 (logo mark via `favicon.svg`; theme circle-crop overridden so the full mark shows)
- [x] Theme toggle present and works
- [x] Visual hierarchy: eye lands on the most important thing first — Sweep 8 (hero → doors → "browse every post" → Now line → Latest 5). The five-form guide moved to `/posts/`.
- [x] No awkward empty space / orphaned sections — Sweep 8 (removed the gap between doors and Now; doors, Now and Latest share one 15px inset)
- [ ] Footer / copyright correct (homepage runs `footer = false`; verify on inner pages)

## Post page (`/posts/<form>/<slug>/`)

- [x] Readable line measure + line-height (long-form comfort)
- [x] **Reading time** displayed (`page.reading_time`) — Sweep 7 (Cycle 4; "3 min read" on the concepts post, confirmed in browser)
- [x] **Table of contents** for long posts — **Serene already ships this** (floating `<aside><nav>` of H2 anchors + back-to-top button on wide screens); verify nested H3 handling + mobile behavior, restyle if needed
- [x] **Related-posts navigation** (content-based; replaces arbitrary chronological prev/next) — Sweep 7 (Cycle 5: TF-IDF `related.json` seam; renders "Related" links in browser on both single-section and multi-sibling posts; chronological fallback when the artifact is absent)
- [x] **Reader controls: font-family picker + font-size adjust** (accessibility / far-sightedness) — Sweep 4 (floating "Aa" panel on posts: size 14–28px, Sans/Serif/Mono/OpenDyslexic; `localStorage`-persisted; no-FOUC head script)
- [x] Code blocks render with syntax highlighting + copy button — Sweep 7 (highlight `class` spans + `#copy-cfg` data present; section default `copy = true`)
- [x] Callouts (`> [!NOTE]` etc.) render correctly — Sweep 7 (`github_alerts`; callout markup on the MVP archive post)
- [x] `{{ demo() }}` shortcode iframes render — Sweep 7 (same-origin iframe on the concepts + reader-controls posts; loads in browser with 0 console errors)
- [x] KaTeX math renders (when `extra.math`) — Sweep 8 (2026-09-16). Now exercised: *A Flock Is a Control Loop* sets `extra.math`. Three display equations render; **all three overflowed the reading column and widened the page** (doc `scrollWidth` 537 vs 375 viewport = 162px of lateral scroll) because KaTeX ships `.katex-display > .katex { white-space: nowrap }` while declaring no `overflow` on `.katex-display`. Fixed in `static/css/custom.css` (`overflow-x: auto` + scroll-shadow affordance); re-measured 367 ≤ 375, 0 vertical clipping, equation tails reachable, no shadows at 1280px where the equations fit.
- [ ] Mermaid diagrams render (when `extra.mermaid`) — wiring verified in `post.html`; **unexercised**: no current post sets `extra.mermaid`
- [x] Series links + tags links resolve — Sweep 7 (49 per-tag pages + 3 series pages + both landings build; `zola check` clean)
- [ ] `superseded_by` banner renders when set — banner wiring verified in `post.html`; **unexercised**: only documented in workflow prose, no live post sets it
- [x] Back-navigation — in-content back-link **removed** (Cycle 4); persistent header + browser Back cover navigation (rationale in `post.html` comment)

## List / aggregator pages

- [x] `/posts/` split-by-form aggregator groups correctly (logbook / concepts / workflows / opinions / resources / archive) — Sweep 1, re-confirmed Sweep 7 (builds clean). Sweep 8: each form heading carries its one-line guide description; headings were unstyled (browser-default blue, 15px out of line) and are now styled.
- [x] Each form section heading links to its section page — Sweep 1/7
- [x] Empty-form sections note "no content yet" gracefully — Sweep 1/7 (as of Sweep 8 only opinions is empty; 32 published: logbook 11, concepts 5, workflows 6, resources 1, archive 9)
- [x] Section pages (`/posts/logbook/` etc.) list their posts — Sweep 7 (9 sections build, 0 orphan)
- [x] Tag landing + per-tag pages work — Sweep 7 (`/tags/` + 49 per-tag pages; `/series/` + 3)

## Destination surfaces (Cycle 6)

- [x] **Résumé** `/resume/` (alias `/cv/`) — Sweep 8: one template renders page and PDF; PDF is 2 pages with the font embedded; print shows no screen chrome; `Person` JSON-LD parses; no email, phone or address, and both leak guards were proven to fire on a leaky build.
- [x] **Projects** `/projects/` + omni-me / mylearnbase / boids pages — Sweep 8: 1280/375, both schemes; every card link resolves.
- [x] **Playground** `/playground/` — Sweep 8: 11 tiles (`hero-flock` is `noindex`), 3 heavy tiles show content-addressed posters and open on click, 3→1 columns, 0 console errors, no sideways scroll, 11/11 links resolve.
- [x] **Demo back-links** — Sweep 8: standalone, 12/12 demos mount the bar with 0 errors and nothing covered; embedded, 10/10 iframes carry the script and render **no** bar. `build-demo-index.py` reports 12 on disk, 10 linked, 0 broken embeds.
- [x] **Motion** (front door and header chrome only) — Sweep 8, Chromium only: hero flock flees the pointer (density near it fell 64%) and pauses off-screen; logo spark turns on hover and `:focus-visible` with no clipping; doors stagger in, and hover lift still works after. Reduced motion: one static flock frame, no animations, no hover transforms. Untested: whether the door stagger shows after a speculation-rules prerender of `/`.

## Navigation & Search

- [x] Header/nav links resolve (no 404s) — Sweep 8 (`extra.nav` = Projects · Playground · Posts · Résumé, logo mark before the wordmark; all 12 homepage + header links 200). Below 575px the wordmark and Posts hide: the full row measured 505px, so 575px leaves slack, and the header fits at 320px.
- [ ] Active section visually distinguished — not tested this sweep
- [ ] Instant-nav (`class="instant"`) works without full reload — not tested this sweep
- [x] 404 page renders with recovery link — Sweep 7 (`404.html` builds with "back to home")
- [x] **Site search (Pagefind)** present, keyboard-accessible — Sweep 7 (Cycle 4; `search.js` + UI mount on pages; `bash build.sh` indexes 26 pages → `public/pagefind/`). Result-return requires the built index, so it is a **production / `bash build.sh`** feature, absent under bare `zola serve` (same dev/prod split as related-posts).

## Theme (light / dark)

- [x] Light mode: all text meets contrast; brand `--primary-color` legible on bg — screenshot-verified Sweeps 2–5 (not re-measured Sweep 7: the headless browser emulates `prefers-color-scheme: dark`)
- [x] Dark mode: parity; no unreadable elements — Sweep 7 (measured: body `#1c1c1c` on `#c1c1c1` text = **9.47:1**, exceeds WCAG AAA)
- [x] No flash of wrong theme (FOUC) on load — Sweep 4 pre-paint inline script (resolves theme before first paint); unchanged
- [x] Syntax-highlight CSS swaps with theme (giallo-light / giallo-dark) — Sweep 7 (`<link id=hl>` present; both `giallo-*.css` generated)
- [x] Toggle persists across navigation — Sweep 7 (`sessionStorage.theme` persisted across a navigation, confirmed in browser; per-session by Serene design)

## Responsive (folds in mobile-responsivity item)

- [x] **Mobile (~375px):** no horizontal scroll — Sweep 8 (2026-09-16): home 367 ≤ 375 **and a post re-measured at a true 375px viewport** (367 ≤ 375). ⚠️ **Methodology fix:** Sweep 7 recorded "post 1272 ≤ 1280" under this mobile item — a *desktop* measurement filed under the 375px check, so no post was ever measured narrow. That is precisely how the KaTeX overflow above survived a green sweep. When checking this item, confirm the viewport width in the evidence matches the heading. Nav reflows (Sweep 1).
- [x] **Tablet (~768px):** layout adapts at `--homepage-max-width` boundary — Sweep 1 (not re-tested Sweep 7; between the two measured widths)
- [x] **Desktop (~1280px):** content max-width sensible, not stretched — Sweep 7 (no overflow at 1280)
- [x] Homepage `#info` / `#links` / recent-list reflow cleanly — Sweep 1/2 (mobile home no overflow Sweep 7)
- [ ] Code blocks scroll horizontally rather than break layout — not specifically tested
- [x] Images / demos scale within viewport — Sweep 7 (demo iframe is `width:100%`; no overflow at 375px)

## Accessibility

- [x] Images have meaningful `alt` text — Sweep 7 (all 7 image-bearing posts; 0 `<img>` missing `alt`)
- [x] Color contrast passes WCAG AA (text + interactive) — Sweep 7 (dark mode 9.47:1 measured; light mode screenshot-verified Sweeps 2–5)
- [ ] Visible focus states on links/buttons/inputs — not tested this sweep (Serene default + `custom.css`)
- [ ] Keyboard navigation reaches all interactive elements — not tested this sweep
- [x] Heading order is logical (single h1, no skipped levels) — Sweep 7 (1 `<h1>` per post)
- [x] Theme toggle + search have accessible labels — Sweep 7 (`aria-label` on toggle, search, and reader-controls "Aa")
- [x] Reader font-size control lets low-vision / far-sighted readers scale text without browser zoom (new Cycle-3 feature) — Sweep 4 (14–28px, scopes `article.prose`)
- [x] Font-family picker offers a readable serif/sans/mono/dyslexia-friendly choice, persisted across pages — Sweep 4 (Sans/Serif/Mono + self-hosted OpenDyslexic; `localStorage`, applied site-wide on `.prose`)

## Performance

- [ ] Images sized appropriately (no oversized assets) — not measured this sweep
- [x] No layout shift on load (CLS) — Sweep 8, homepage only: Lighthouse perf 99, CLS 0, TBT 0, LCP 1.8s (the Now paragraph). A 0.0009 shift on `#text` was fixed with `flex-shrink: 0` on the avatar (CLS 0 in 5/5 runs). Motion changed nothing (3 runs each, identical). Post pages not measured.
- [x] Fonts load without blocking / FOUT jank — Sweep 4 (OpenDyslexic `font-display: swap`, loaded on demand)
- [x] `minify_html` output is clean — Sweep 7 (build clean with `minify_html = true`)
- [x] No console errors or warnings — Sweep 7 (concepts post in browser: **0 errors / 0 warnings** with header.js + reader-controls.js + search.js + demo iframe all live). Sweep 8: 0 errors on the homepage, `/playground/` and all 12 standalone demos.

## SEO / Social surface (cross-checks Phase 2/3)

- [x] `<title>` + `<meta name="description">` present and per-page correct — Sweep 3 (Lighthouse SEO `document-title` + `meta-description` pass). **Sweep 8:** "present" had hidden a real gap. No post set `description`, so every post fell back to the `/posts/` section's text. All 32 published posts now carry an authored one, chosen in one place (`_head_extend.html`), and `zola build` fails on a published post without one (`zola check` does not render templates, so it can't catch this). 35 post/project pages: unique descriptions, and search/og/twitter/JSON-LD agree.
- [x] **OpenGraph + Twitter cards** render — Sweep 3 (og:site_name/title/description/type/url/locale + twitter:card/title/description); **og:image + twitter:image wired Sweep 5** (1200×630 card, `summary_large_image`). Sweep 8: the card is rendered from source (`scripts/build-og-card.py`; `build.sh` warns when stale) and carries the new tagline.
- [x] **JSON-LD** structured data present + parses — Sweep 3 (`BlogPosting` on leaf posts, `WebSite` on home/sections; all valid JSON). Schema-field validity confirmed Sweep 6 — `validator.schema.org` returns **0 errors / 0 warnings** against the live site. Sweep 8: 148 blocks valid (BlogPosting 35 / WebSite 77 / BreadcrumbList 35 / Person 1); the audit allowlist learned `Person`.
- [x] `<link rel="canonical">` present — Sweep 3 (per-page `page.permalink` / `section.permalink`)
- [x] Favicon resolves (no 404) — Sweep 5 (SVG favicon + 16/32/180 PNGs + apple-touch; all 200)
- [x] `sitemap.xml`, `robots.txt`, `llms.txt` reachable at root — Sweep 3 (`robots.txt` now custom AI-welcoming + production `Sitemap:`; `llms.txt` served)
- [ ] **Privacy analytics** snippet present (Tier 2) — _not built_; a privacy/colophon page is Cycle-5 Task 4 (analytics *implementation* remains out of scope, disclosed there only if/when decided)

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
- `[x]` ~~**No reader font controls** (family picker + size adjust).~~ **Resolved Sweep 4** — floating "Aa" panel: 14–28px size + Sans/Serif/Mono/OpenDyslexic, `localStorage`-persisted, no-FOUC.
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

### Sweep 4 — 2026-06-14 (Cycle 3 — reader controls: text size + typeface)

**Changes shipped** (`static/css/custom.css`, `static/js/reader-controls.js`,
`static/fonts/opendyslexic-{400,700}.woff2`, `templates/_head_extend.html`,
`templates/post.html`):
- Floating **"Aa"** control on post pages (bottom-left — the theme's `#back-to-top`
  owns bottom-right). Toggle button + popover panel with **Text size** (A− / readout /
  A+, 14–28px, step 2) and **Typeface** (Sans / Serif / Mono / OpenDyslexic, 2×2 grid).
- Typography scoped to `article.prose` (size via `--reader-font-size`; family via a
  `data-reader-font` attribute on `<html>` → font stacks live only in CSS, no JS map).
- Prefs persist in `localStorage`; an inline `_head_extend.html` script applies them
  **before paint** (no flash of default text), mirroring the theme's dark-mode pattern.
- **OpenDyslexic** self-hosted (SIL OFL), `font-display: swap`, loaded **on demand** —
  0 bytes for readers who don't select it.
- Progressive enhancement: markup ships `[hidden]`; the control reveals itself only
  when `reader-controls.js` runs. No-JS / no-prefs visitors get the theme default.

**Verification method + results:**
- `zola build` clean; control present on posts, **absent on home** (correct scoping);
  post-JS DOM confirms the control is revealed (`hidden` removed).
- Headless-Chrome screenshots: panel open with Serif @ 24px (light), default "Aa"
  button in dark mode, and OpenDyslexic @ 22px — all render correctly.
- Overlap check: scrolled-post screenshot confirmed the "Aa" (bottom-left) and the
  theme's `#back-to-top` (bottom-right) no longer collide.
- `scripts/seo-audit.sh` re-run: **ALL PASS**, Lighthouse SEO still 100/100 — no
  regression from the new inline head script or `@font-face`.

**Open / future:**
- Italic / bold-italic OpenDyslexic faces not bundled (400 + 700 only); fine for body
  reading. Add if emphasis-heavy posts need it.
- Control is post-page only. Lift into a base template if it's wanted site-wide.

### Sweep 5 — 2026-06-14 (Cycle 3 Phase 3 — logo, favicon, OG image)

**Logo design (process recorded):** brief = curiosity/learning (primary) + technology/
creativity (secondary) + a "base" nod (stretch); *not* developer-coded. Diverged across
3 directions (spark / orbit / arc), converged on the **spark**, refined 4 ways to fix
"generic," landed on **rising spark grounded on a base** ("spark of curiosity rising
from a base" / reads as a spinning top — "stability in motion"). Judged at 16px and in
a browser-tab + OG-card mock before committing any files.

**Assets shipped** (`static/img/`): `logo.svg` (canonical, `currentColor` → theme-adaptive
for inline use), `favicon.svg` (explicit brand blue + `prefers-color-scheme` dark variant),
`favicon-16x16.png` / `favicon-32x32.png` (transparent), `apple-touch-icon.png` (180, opaque
white bg per iOS), `og-default.png` (1200×630 share card: mark + wordmark + tagline + URL).
Rasterized via headless Chrome (no system rasterizer present).

**Wiring** (`templates/_head_extend.html`): SVG favicon `<link>` added (PNG fallbacks already
in theme `_base.html`); `og:image` (+ width/height/alt) and `twitter:image` wired to the
share card; `twitter:card` upgraded `summary` → `summary_large_image`.

**Verification:** `zola build` clean; all six assets resolve **200** (favicon 404s gone);
emitted `<head>` carries absolute image URLs; `scripts/seo-audit.sh` **ALL PASS**, Lighthouse
SEO still **100/100**.

**Open / future:**
- Homepage avatar — **added** (logo mark via `favicon.svg`, theme circle-crop overridden).
- `og:image` is one default card for all pages; per-post share images are a possible later add.
- Real social-unfurl + Rich Results checks need a public URL → Phase 4 (post-deploy).

### Sweep 6 — 2026-06-14 (Cycle 3 Phase 4 — registration, promotion + ahrefs triage)

**Registration & promotion (user-driven, browser/dashboard side):**
- Google Search Console — URL-prefix property, HTML-tag verification (token in
  `zola.toml [extra].google_site_verification`, emitted via `_head_extend.html`),
  `sitemap.xml` submitted → **success** (indexing will take time, as expected).
- Bing Webmaster Tools — imported from GSC, smooth.
- ahrefs — site added, verified via GSC.
- LinkedIn — OG card **rendered correctly** when the URL was shared (validates the
  Phase-3 `og:image` + Phase-2 OG tags end-to-end on a real unfurl).

**First ahrefs audit = 67.** User exported every red-triangle issue; triaged to root causes:

- `[x]` **47 non-canonical pages** (the dominant issue) — every `/tags/*` and `/series/*`
  canonicalized to `/posts/`. Root cause: the custom taxonomy templates set a local
  `section` var for layout, which made `_head_extend`'s `section.permalink` resolve to
  `/posts/`. **Fix:** prefer Tera's `current_url` global (authoritative rendered URL, not
  shadowed by the local `set`) for canonical + og:url. One-line universal fix; all page
  types now self-canonical. Verified live.
- `[x]` **`/categories/` 404** — vestigial `categories` taxonomy declared but unused
  (apparent "uses" were post *prose*, not frontmatter). **Fix:** removed from `zola.toml`.
- `[x]` **www 522 + http→https** — the `www` CNAME was proxied through Cloudflare but
  attached to nothing (no Pages custom domain, no redirect) → edge got the request, found
  no origin, timed out (522). **Fix (user, Cloudflare dashboard):** two template Redirect
  Rules — http→https and www→apex. `www` now 301s to the apex; 522 gone.
- `[~]` **Accepted residue (user opted not to fix):** Cloudflare email-obfuscation
  (`/cdn-cgi/l/email-protection`) flagged as a broken link; one orphan
  `/posts/logbook/omni-me/`. Cloudflare-layer artifacts / minor; canonical tags already
  force the apex.

**Result:** repo fixes deployed via Cloudflare CI/CD; **second ahrefs crawl = 98%**, most
real issues cleared. `validator.schema.org` returns 0 errors / 0 warnings on the live JSON-LD.

**Verdict → Cycle 3 closed.** Site is public-ready and discoverable: registered across
GSC / Bing / ahrefs, LinkedIn-shareable with a correct OG card, Lighthouse SEO 100/100,
self-canonical on every page type.

### Sweep 7 — 2026-06-30 (Cycle 5 — post-Cycle-4 feature catch-up + content-based prev/next)

**Why:** the checklist predated Cycle 4, so it still marked reading-time / prev-next /
search as "not yet built" though all shipped, and Cycle 5 had just replaced chronological
prev/next with content-based relatedness (Task 3). This sweep re-verifies the new prev/next,
catches the checklist up on Cycle-4 features, and runs the standard audit.

**Method:** `zola build` (26 pages / 0 orphan / 9 sections, clean) + `zola check
--skip-external-links` (clean) + `scripts/seo-audit.sh` + rendered-HTML grep for functional
markers + a Playwright browser pass (`zola serve`) on the concepts post and homepage at
1280px and 375px, light/dark, with console capture.

**Audit harness fix (`scripts/seo-audit.sh`):** the JSON-LD check false-failed on 26 valid
`BreadcrumbList` blocks (added in Cycle 4) because its allowlist was `{BlogPosting, WebSite}`,
written in Cycle 3. Taught the check `BreadcrumbList`; audit now passes. **116 JSON-LD blocks
valid** (BlogPosting 26 / WebSite 64 / BreadcrumbList 26), 0 parse failures. **Lighthouse SEO
still 100/100** on home + a sample post.

**Cycle-4 features verified (flipped to `[x]`):**
- Reading-time ("3 min read" on the concepts post, in browser).
- Pagefind search present (`search.js` + UI; `bash build.sh` indexes 26 pages). Result-return
  is a production/`build.sh` feature, not present under bare `zola serve` (no index).
- Code copy button, callouts (`github_alerts`), `{{ demo() }}` iframes (load with 0 console errors).
- Reader controls (from Sweep 4), breadcrumb JSON-LD (the harness fix above).

**Cycle-5 prev/next verified:** the new "Related" nav renders content-based links in a real
browser — concepts post → "Site search" + "Building the Foundation…"; financial-health post →
"Account list" + "Budget setup" (each post's true TF-IDF top-2). Chronological fallback renders
"Adjacent posts" when `related.json` is absent. See `tasks.md` Task 3 + `project.md`.

**Browser pass results (Playwright, my `zola serve`):**
- Console: **0 errors / 0 warnings** on the concepts post (header.js + reader-controls.js +
  search.js + demo iframe all live).
- No horizontal overflow at 1280px (1272 ≤ 1280) or 375px (home 367 ≤ 375).
- Dark mode contrast **9.47:1** (`#1c1c1c` bg / `#c1c1c1` text), exceeds WCAG AAA.
- Theme toggle writes `sessionStorage.theme` and persists across navigation.
- Single `<h1>` per post; all 7 image-bearing posts have `alt` text (0 missing); `aria-label`s
  on theme toggle / search / reader controls.

**Known-benign:** `bash build.sh` Pagefind warns `"/posts/autonomous-ui-development-with-playwright-mcp/"
has no <html> element` — that URL is a Zola **redirect-alias stub** (538-byte `<title>Redirect</title>`
shell), expected to lack `<html>`. The real archive page renders fine.

**Still open (not regressions, just not exercised/measured this sweep):** KaTeX + Mermaid
(wired in `post.html`, no current post sets `extra.math`/`extra.mermaid`); `superseded_by` banner
(wired, only documented in workflow prose); active-section highlight + instant-nav; visible
focus states + keyboard nav; light-mode fresh contrast measurement (headless browser emulates
dark); CLS / image-sizing (Lighthouse performance category not run).

**Verdict:** site is healthy. All Cycle-4 features confirmed live, the Cycle-5 content-based
prev/next verified in-browser, the SEO audit is green again (harness drift fixed), and no
regressions. `ui-checklist.md` is current as of Cycle 5.

### Sweep 8 — 2026-09-16 (Cycle 6: audience routing, destination surfaces, motion, post descriptions)

**Why:** Cycle 6 rebuilt the front door around visitor intent (recruiter, project browser,
explorer), added three destination surfaces, fixed KaTeX overflow, added motion, and made post
descriptions mandatory. Each part was verified as it shipped; this entry records those results
rather than re-running them.

**Method:** `bash build.sh` (compute-related, demo index, résumé and preview-card drift checks,
Zola, Pagefind) + `zola check --skip-external-links` + `scripts/seo-audit.sh` + Playwright on
`zola serve` at 1280px and a true 375px viewport, light and dark, with console capture +
Lighthouse performance on `/` (3 to 5 runs per variant).

**Results:**
- **KaTeX overflow found and fixed.** The first narrow measurement of a post found 162px of lateral
  scroll from three display equations (see the Post page and Responsive rows, and the methodology
  note on the 375px row).
- **New surfaces verified:** résumé + PDF, Projects, Playground, demo back-links in both contexts,
  motion with reduced motion honoured. Details in "Destination surfaces".
- **Homepage and header:** doors above the fold at 375px, header fits at 320px, 12/12 links 200.
- **Descriptions:** every published post has its own; the build gate fails a published post
  without one and exempts drafts (both proven).
- **Audit:** 148 JSON-LD blocks valid, Lighthouse SEO 100/100 on home and a sample post.
  Homepage perf 99, CLS 0.

**Found after the sweep (deploy, not UI):** four pushes on 2026-09-16 failed on Cloudflare.
Marking `themes/serene` with `update = none` (meant only for the session hook) made every clone,
Cloudflare's included, skip the theme. Replaced with a hook-only `pinned = true` key; a fresh
clone plus full `build.sh` passed before pushing, and the deploy of `099d03d` succeeded.

**Known-benign:** Pagefind lists every redirect-alias stub (`/cv/` and the archive aliases) as
having no `<html>` element, as in Sweep 7.

**Still open:** Mermaid and `superseded_by` (wired, unexercised); active-section highlight and
instant-nav; focus states and keyboard nav beyond the logo; light-mode fresh contrast measurement;
image sizing; CLS on post pages; the 12 standalone demo pages have no meta description.

**Verdict:** healthy and current as of Cycle 6. Every new surface verified at both widths and in
both schemes, no regressions in the audit, and the site is deployed.
