+++
title = "Reader text-size & typeface controls"
slug = "reader-controls"
date = 2026-06-24
draft = false

[taxonomies]
tags = ["ux", "accessibility", "frontend"]
+++

## What does this feature do?

On any post, a reader can change how the article body reads. A floating
"Aa" button at the bottom-left of the page opens a small panel with two
controls: **text size**, which steps the body type from 14px to 28px, and
**typeface**, which switches the reading surface between Sans, Serif, Mono,
and **OpenDyslexic** — a face whose weighted letterforms help some dyslexic
readers track a line. The change applies instantly and only to the article
body; the navigation, header, and footer are left alone. The choice is
remembered in the browser, so it survives moving between posts and closing
the tab, and it's applied before the page paints — a far-sighted reader who
has set a larger size never sees a flash of small text that then jumps.

## Why was it added now?

Once the site went public, the work shifted from "does it exist" to "is it
comfortable to actually read." A reading-experience pass turned up an
obvious gap: the body text was a single fixed size in a single typeface.
That's fine for most visitors and a real barrier for a far-sighted reader,
with nothing to offer anyone who simply reads more easily in a different
face. A per-reader override of size and typeface, scoped to the reading
surface, was the smallest change that removed the barrier — and because it
runs entirely in the browser, it fit the static-site setup with no backend
to add and no build step to grow.

## What's in scope (and what's not)?

In: the article body (`article.prose`) — text size (14–28px in 2px steps)
and typeface (Sans / Serif / Mono / OpenDyslexic).

Not in: the site chrome — navigation, header, and footer stay fixed; the
light/dark theme, which is the site's existing toggle and a separate
concern; and cross-device sync — the preference lives in the browser, not
an account, because the site has no backend to sync one through.

## How do we know it works?

The clearest proof is to use it. The demo below is a faithful, sandboxed
copy of the controls — change the size and typeface and the sample text
re-renders live:

{{ demo(name="mylearnbase/reader-controls", height=520, caption="The reader controls, sandboxed. Resize the body text and switch the typeface — including OpenDyslexic — and the article body responds.") }}

And the proof isn't confined to the sandbox: **this very page is a real
post**, so the floating "Aa" button at the bottom-left drives the same
change on the text you're reading right now. If OpenDyslexic renders when
you pick it, the on-demand font load worked; if your chosen size survives a
reload, persistence worked.

The handful of lines that make that happen:

[`static/css/custom.css:105`](https://github.com/RustWright/mylearnbase/blob/c0fe53b80c423a48b273eb0b95879000b0c8b568/static/css/custom.css#L105) at `c0fe53b`
> `  font-size: var(--reader-font-size, var(--font-size));`
>
> Text size is one CSS custom property on the reading surface. Every size button just sets this variable; the body reads it and falls back to the theme default when it's unset — so a no-prefs visitor is unchanged.

[`static/js/reader-controls.js:45`](https://github.com/RustWright/mylearnbase/blob/c0fe53b80c423a48b273eb0b95879000b0c8b568/static/js/reader-controls.js#L45) at `c0fe53b`
> `    else root.setAttribute("data-reader-font", key);`
>
> Typeface is selected by a data attribute on `<html>`, not a font map in JS. The font stacks live in CSS, so adding a face is a CSS-only change and the script stays tiny.

[`templates/_head_extend.html:24`](https://github.com/RustWright/mylearnbase/blob/c0fe53b80c423a48b273eb0b95879000b0c8b568/templates/_head_extend.html#L24) at `c0fe53b`
> `      if (s) el.style.setProperty("--reader-font-size", s + "px");`
>
> A saved size is applied here, in the `<head>`, before the page paints — which is what stops a far-sighted reader from seeing a flash of default text that then jumps.

[`templates/post.html:165`](https://github.com/RustWright/mylearnbase/blob/c0fe53b80c423a48b273eb0b95879000b0c8b568/templates/post.html#L165) at `c0fe53b`
> `<div id="reader-controls" hidden>`
>
> Progressive enhancement: the control ships [hidden] and reader-controls.js reveals it. A reader with JS disabled gets the unchanged default, never a dead button.
