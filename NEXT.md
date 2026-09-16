# NEXT — mylearnbase

**Updated:** 2026-09-16 · Cycle 6. Parts 0, 1a–1d and 2 shipped: KaTeX fix, résumé, Projects, Playground,
demo back-links, homepage router + header nav + Now line.

## Next action
**First (user's call, 2026-09-16): remove em dashes from section subtitles/descriptions** in
`content/posts/{logbook,concepts,workflows,opinions,resources}/_index.md` and `logbook/omni-me/_index.md`.
No colons as stand-ins. Show the user the rewrites. **Then `3b` logo hover, `3c` door stagger-in.** Plan:
`~/.claude/plans/could-you-look-into-abstract-kahn.md`. Then Sweep 8 in `ui-checklist.md`, then cycle bookkeeping.

## Decisions in force
- **Homepage copy:** tagline "I build things to learn, then write down how." The old intro became the `/posts/`
  subtitle. Both chosen by the user 2026-09-16. Door copy follows the approved prototype.
- **Homepage = doors (Projects · Playground · Résumé) + quiet Posts link → Now line → Latest 5.** The form
  guide lives on `/posts/`; its `guide` array is the only list of forms (order + descriptions).
- **Now line: wording approved by the user** (2026-09-16). It is dated (`now_updated`) and `build.sh` warns after 90 days.
- **Header nav:** `phone = false` hides Posts below **575px (measured: the full row needs 505px)**; the mark
  replaces the wordmark there. Re-measure if a nav item is added. Tags is gone at every width.
- **Hero flock:** top band sized from `--hero-band`, not a percentage; pointer tracked on `window`, since the
  canvas sits under content. No click-through to the full demo (a background that navigates on tap is a trap).
- **Résumé is structured data**, one template for page and PDF; polish deferred by the user (2026-09-16).
- **Anything naming the site on paper reads `extra.canonical_url`**; build and PDF script both guard it.
- **Projects:** authored facts, derived evidence; copy approved. Link public repos only (never `boids-private`).
- **Playground:** heavy demos (>150KB) show content-addressed posters; rerun `capture-demo-posters.py`
  after changing one. `noindex` hides a demo from search and gallery (only `hero-flock`).
- **File sizes on downloads only. Search stays posts-only. `demos.json` is derived.**
- **No email on the résumé** until an efeerhie.com forwarding alias exists; **no phone/address ever.**
- **`themes/serene` is pinned** (`update = none`); restore with `git submodule update --init --checkout themes/serene`.

## Do NOT re-survey
- **Verified at 1280/375, both schemes:** KaTeX, flocks, PDF pipeline, demo chrome, Playground, Projects,
  homepage, `/posts/`, header (also 320px). Predator proven deterministically (pointer over a door changes
  the sim). SEO audit passes (Lighthouse SEO 100). Homepage perf 99–100; the flock costs 0ms TBT.
- ⚠️ Local testing: `python -m http.server` sends no `Cache-Control`; clear the browser cache after CSS edits.

## Open threads
- **Résumé polish, deferred:** page 2 ~40% full; "Best Graduating Student" listed twice; accent colour.
- **Demo/site theme mismatch, pre-existing:** demos follow `prefers-color-scheme`, the site has a toggle.
- **Cycle 5 never formally closed.** Close it, write Cycle 6 `tasks.md`, retire `mylearnbase-site-backlog.md`.
