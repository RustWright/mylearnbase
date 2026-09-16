# NEXT — mylearnbase

**Updated:** 2026-09-16 · Cycle 6 (Audience Routing) implementation complete and deployed (`099d03d`); Sweep 8
recorded; Cycle 5 closed. Tracker `tasks.md`, queue `.omni/tasks.toml`, history `project.md`.

## Next action
**Not chosen yet: ask the user.** Derived from state, not priority: Cycle 6 is still open (hub `0016`, XS: Phase D
only; no curiosities were logged, so just the logbook-demo question), then Cycle 7 planning (`0017`). The biggest
standing item is the user's ASD-STE100 writing standard (`0003`, notes at the foot of `tasks.md`).

## Decisions in force
- **Cycle 5 closed with no code review, and none is scheduled** (user, 2026-09-16). That choice was made for
  Cycle 5; ask before assuming it for Cycle 6. Cycle 5 curiosities: no survivors (`0006` cut).
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
- **`themes/serene` is pinned to v5.6.1 by its recorded commit.** `pinned = true` in `.gitmodules` only stops the session
  hook fast-forwarding it. **Never `update = none`:** clones obey it, so Cloudflare built without the theme.

## Do NOT re-survey
- **Sweep 8 is the verification record** (`ui-checklist.md`): KaTeX, résumé/PDF, Projects, Playground, demo chrome,
  homepage, header, motion, descriptions, SEO audit (148 JSON-LD, Lighthouse SEO 100), homepage perf 99 / CLS 0.
- **Live site checked after the fix deploy:** home, `/resume/`, `/projects/`, `/playground/`, a post, the card.
- ⚠️ Minified HTML omits `</head>` and puts `content` before `name`. Extra Playwright contexts need `bringToFront()`.
- ⚠️ `PROJECT_PROCESS.md` has no "§ Cycle Closure"; closing a cycle is Session 6 (Phases A–D).

## Open threads
- All queued in `.omni/tasks.toml`: demo-page meta descriptions (`0011`), stale front-matter template body (`0012`),
  résumé polish (`0013`, deferred by the user), demo theme toggle (`0014`), untested checklist rows (`0007`, `0008`).
- **Untested:** whether the door stagger shows after a speculation-rules prerender of `/`.
