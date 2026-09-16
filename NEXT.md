# NEXT — mylearnbase

**Updated:** 2026-09-16 · Cycle 6. Parts 0–4 of the plan shipped: KaTeX fix, résumé, Projects, Playground, demo
back-links, homepage router + header, hero flock, logo hover + door stagger, post descriptions + preview card.

## Next action
**Sweep 8 in `ui-checklist.md`**, recording the Cycle 6 verification already done (see "Do NOT re-survey"; no
re-run needed). **Then cycle bookkeeping:** close Cycle 5 per `PROJECT_PROCESS.md` § Cycle Closure (every Cycle 5
task is done), write the Cycle 6 `tasks.md` from the plan, update `project.md`'s session log, and delete the
`mylearnbase-site-backlog.md` memory note plus its `MEMORY.md` line. Plan: `~/.claude/plans/could-you-look-into-abstract-kahn.md`.

## Decisions in force
- **Copy approved by the user (2026-09-16):** tagline, `/posts/` subtitle, Now line, form copy, all 32 descriptions.
- **Descriptions:** chosen once in `_head_extend.html`. A published page without one fails the build (drafts fall
  back). Publish tools take `--description`, keep it, and refuse before writing. `zola check` does NOT catch it.
- **Link-preview card** is rendered from source (`scripts/build-og-card.py` + `og-card.html`); `build.sh` warns stale.
- **Homepage = doors → Now line → Latest 5**; form guide on `/posts/`. **Header:** Posts hides below 575px (measured).
- **Motion only on the front door and header chrome**, inside `prefers-reduced-motion: no-preference`; approved by
  the user. Door stagger fill is `backwards` (`both`/`forwards` kill the hover lift). Flock: no click-through.
- **Résumé is structured data**, one template for page and PDF. Anything naming the site on paper reads
  `extra.canonical_url` (guarded). **Projects:** authored facts, derived evidence; public repos only (never `boids-private`).
- **Playground:** heavy demos show content-addressed posters (rerun `capture-demo-posters.py` after changing
  one); `noindex` hides a demo (only `hero-flock`). File sizes on downloads only; search posts-only.
- **No email on the résumé** until an efeerhie.com forwarding alias exists; **no phone/address ever.**
- **`themes/serene` is pinned** (`update = none`); restore with `git submodule update --init --checkout themes/serene`.

## Do NOT re-survey
- **Verified:** KaTeX, flocks, PDF, demo chrome, Playground, Projects, homepage, `/posts/`, header, motion
  (1280/375, both schemes, reduced motion, Lighthouse 99/CLS 0). 35 post/project pages: unique descriptions,
  search/og/twitter/JSON-LD agree. Gate proven (fails build, drafts exempt). Tools tested in a scratch site.
  SEO audit passes (Lighthouse SEO 100). Editorial guides republished and in sync with their posts.
- ⚠️ Minified HTML omits `</head>`. `http.server` sends no `Cache-Control`. Extra Playwright contexts need `bringToFront()`.

## Open threads
- **`~/.dotfiles` uncommitted:** `claude/commands/create-post.md` (description guidance, this session) plus a
  `claude/settings.json` change that predates it. Hooks don't commit dotfiles; the user's call (`/sync-dotfiles`).
- **Standalone demo pages (12) have no meta description** (static HTML). **Front-matter template body** still
  describes the old Reflections/Tutorial post format.
- **Résumé polish, deferred:** page 2 ~40% full; "Best Graduating Student" listed twice; accent colour.
- **Demo/site theme mismatch, pre-existing:** demos follow `prefers-color-scheme`, the site has a toggle.
