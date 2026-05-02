# Extraction queue

Candidates flagged in chronicles for possible extraction into cookbook entries, process posts, or other future content. This file is **not published** — it lives outside Zola's `content/` directory specifically so toggling `draft = false` on a post can never accidentally release it.

Format: each entry has a hook (one sentence), an optional embed/demo idea, and a back-link to the chronicle that flagged it. Clear an entry when it gets extracted into a real post (replace with a link to the published extraction).

---

## From: omni-me Cycle 2 closing sitting (2026-04-26)

### Cookbook candidate — month-grid 6×7 vs 5×7
**Hook:** A reviewer told me to trim my month grid from 6×7 to 5×7. They were wrong. The cases where 35 cells aren't enough are the cases I wasn't looking at while building.
**Embed idea:** WASM widget rendering October 2026 in both layouts so the truncation is visible. Side-by-side comparison ideal.
**From:** `2026-04-26-omni-me-cycle-2-closing-sitting.md`

### Cookbook candidate — bloat reviews need a grep-tax
**Hook:** Sonnet 4.6 over-counted "duplicate sites" twice in 9 findings. Verifying repetition claims before refactoring is non-optional — the cost of extracting an "abstraction" with one real caller is permanent.
**From:** `2026-04-26-omni-me-cycle-2-closing-sitting.md`

### Process post candidate — when test-gap audits earn their place
**Hook:** When the audit runs after fix cycles, most of the gap demand is already absorbed by inline regression tests in the fix commits. The residual value is absence-of-behavior assertions — things that should *not* be accepted, which fix-driven tests don't naturally produce.
**From:** `2026-04-26-omni-me-cycle-2-closing-sitting.md`
