+++
title = "Persistent site header"
slug = "site-header"
date = 2026-06-25
draft = false

[taxonomies]
tags = ["ux", "navigation", "frontend"]
+++

## What does this feature do?

Every page now carries a slim header bar pinned to the top of the viewport.
It holds the site wordmark (which links home), three navigation links —
**Posts**, **Logbook**, **Tags** — the light/dark theme toggle, and a search
button. The bar is *scroll-aware*: it sits in place at the top of a page, tucks
up out of view as you scroll down into an article, and drops back into view the
instant you scroll up — so the navigation is always one small gesture away
without taking up room while you read. Before this, the only path between
sections ran back through the home page.

## Why was it added now?

The immediate trigger was the next feature on the list — site search — which
needed somewhere to put its trigger, and there was nowhere to put it. The theme
this site runs on is deliberately header-light: no site-wide navigation at all,
just a "← Back" link on posts and the theme toggle tucked into the footer. That
was livable while the site was small, but it meant the only way between sections
was back through the home page, and it left controls like the toggle — and now a
search button — with no natural home. A persistent header was the smallest thing
that fixed all three at once: it gives every page navigation, it gives the toggle
and search a fixed place to live, and it had to exist before search could be
wired in. So it was built first, as its own step.

## What's in scope (and what's not)?

In: a single slim header on every page, carrying the wordmark, Posts / Logbook /
Tags, the theme toggle, and the search trigger, with the reveal-on-scroll-up /
tuck-on-scroll-down behavior. Folded in alongside it: the home page lost its
redundant in-page navigation row (the header now carries navigation, and the
home page's guide cards remain as the richer on-page discovery surface), and the
theme toggle moved out of the footer into the header so that exactly one of it
exists site-wide.

Not in: an exhaustive nav. The header lists only the populated top-level
surfaces — the not-yet-filled forms (concepts, opinions, resources) and the
lightly-used series stay off the bar that follows you everywhere, though they
remain linked from the home page. And no hamburger or drawer menu: three links
fit comfortably, including on mobile, so there is nothing to collapse.

## How do we know it works?

The simplest proof is the page you're reading: the header is at the top of it
right now. Scroll down into the text and it tucks away; scroll back up and it
returns. The wordmark takes you home, Posts / Logbook / Tags resolve to those
sections, and the toggle flips light and dark with the choice persisting between
pages.

The handful of lines behind that:

[`templates/_base.html:40`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/templates/_base.html#L40) at `19c11d9`
> `  <header id="site-header" class="site-header">`
>
> The header is the first child of `<body>` in a project override of the theme's base template. The theme ships no site-wide header, so adding one meant owning _base.html — and placing it here is what makes it appear on every page.

[`static/js/header.js:29`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/static/js/header.js#L29) at `19c11d9`
> `    if (y > lastY) {`
>
> The entire reveal/tuck behavior reduces to this one comparison of the current scroll position against the previous one: scrolling down hides the bar, scrolling up shows it. Everything around it is refinement — a requestAnimationFrame throttle, an always-show zone near the top, and a small delta that ignores jitter.

[`static/css/custom.css:272`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/static/css/custom.css#L272) at `19c11d9`
> `  transform: translateY(-100%);`
>
> Tucking is a single CSS transform. The script only toggles an .is-hidden class; CSS does the motion — and a prefers-reduced-motion block turns this transform into a no-op, so readers who opt out of motion get a header that is simply always visible.

## What's worth remembering or doing next?

- The search button shipped here as an inert, hidden stub and was wired up in
  its own step — see [Site search](@/posts/logbook/mylearnbase/site-search/index.md).
- **Workflows** is intentionally absent from the nav for now: it has posts but
  is reachable through Posts, and the bar reads better at three links. Promote it
  if it grows or the nav earns a fourth slot.
- Owning `templates/_base.html` is the standing cost of the header. The theme is
  pinned at v5.6.1, so any future theme bump means re-merging the header (and the
  search overlay) into the new base template by hand.
- The scroll-direction reveal pattern — comparing successive scroll positions
  inside a `requestAnimationFrame` throttle — could make a small concepts demo on
  its own.
