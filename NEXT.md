# NEXT — mylearnbase

**Updated:** 2026-09-16 · Cycle 6. KaTeX, résumé (restructured), demo back-links, Playground, Projects shipped.

## Next action
**`Part 2`: homepage router + header nav + "Now" line.** Every destination it links to now exists
(`/projects/`, `/playground/`, `/resume/`), which is why it had to come last: Zola validates internal
links at build. Then `3b`/`3c` motion. Plan: `~/.claude/plans/could-you-look-into-abstract-kahn.md`.
**Discuss with the user first, in Part 2:** the em dashes in `content/_index.md` — the tagline
(`bio`, line 10: "I build things to learn — and write down how.") and the intro at line 29. It bugs them.

## Decisions in force
- **Résumé is structured data** (records in `content/resume/_index.md` front matter), rendered by one
  template as both the page and the PDF. Chosen over a print-only stylesheet because markdown cannot put
  dates on the role's line. User: "good enough for now" (2026-09-16); further polish is deliberately deferred.
- **Anything naming the site on paper reads `extra.canonical_url`, never `base_url`** — the PDF build
  overrides `base_url` with localhost. The build fails if the two disagree; the PDF script fails on any
  localhost address in the PDF's text *or* its link annotations (each check is blind to the other).
- **Résumé copy must work on paper**: no "this site", no "here". PDF typeface is bundled Source Sans 3.
- **Projects: authored facts, derived evidence.** `status` is `active`|`complete` or the build fails.
  One lead demo per write-up. **Project copy read and approved by the user** (2026-09-16). Link a repo
  only if public: boids links `boids-flocking-sim`, never `boids-private`.
- **Playground:** light demos preview live, heavy (>150KB, measured) show a content-addressed poster with
  the play button over it; rerun `capture-demo-posters.py` after changing a heavy demo. A tile opens the
  standalone demo. `noindex` keeps a demo out of search *and* the gallery (only `hero-flock`).
- **File sizes on downloads only.** **Site search stays posts-only.** **`demos.json` is derived.** **Header nav.** Desktop `Projects · Playground · Posts · Résumé`; **phones drop Posts**, use the logo
  mark. **Tags leaves at every width.** Logo hover is `3b`. Hero flock: top band, opacity 0.2.
- **No email on the résumé** until a forwarding alias exists on **efeerhie.com**; **no phone/address ever.**
- **`themes/serene` is pinned** (`update = none`); restore with `git submodule update --init --checkout themes/serene`.

## Do NOT re-survey
- **KaTeX, flocks, PDF pipeline, demo chrome, Playground, Projects: verified** at 1280/375, both schemes.
  Résumé PDF 2 pages, leak guards proven to fire. SEO audit passes (148 JSON-LD valid, Lighthouse 100).
- ⚠️ Local testing: `python -m http.server` sends no `Cache-Control`; clear the browser cache after CSS edits.

## Open threads
- **Résumé polish, deferred by the user** so as not to get bogged down: page 2 is ~40% full (one page
  means cutting ~a third); "Best Graduating Student" is listed twice; accent colour (site blue vs old red).
- **Demo/site theme mismatch, pre-existing:** demos follow `prefers-color-scheme`, the site has its own toggle.
- **Cycle 5 never formally closed** though every `tasks.md` task is done. Close it, write Cycle 6.
