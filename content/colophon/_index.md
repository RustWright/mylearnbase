+++
title = "Colophon"
description = "How mylearnbase is built, and what it stores about you (almost nothing)."
template = "prose.html"

[extra]
title = "Colophon"
subtitle = "How the site is built, and what it stores about you. (Short version of the second part: almost nothing.)"
+++

## How it's built

mylearnbase is a static site. Every page is plain HTML, generated ahead of time.
There is no application server and no database, and nothing runs per visitor.

- **[Zola](https://www.getzola.org)** turns Markdown into the site; **Tera** is
  its templating layer.
- The design began with the **[Serene](https://github.com/isunjn/serene)** theme,
  since heavily customized.
- **[Pagefind](https://pagefind.app)** powers search. Its index is built once at
  deploy time and queried entirely in your browser.
- **[Cloudflare Pages](https://pages.cloudflare.com)** builds and hosts the site.
- Interactive demos are self-contained pages embedded in an `<iframe>`. The
  "Related" links under each article are computed at build time by a small
  TF-IDF script over the post text.
- The project's own documentation is a separate
  **[mdBook](https://rust-lang.github.io/mdBook/)** site.

A fuller, annotated list of the tools and references behind the site lives in
[a dedicated resources post](@/posts/resources/building-mylearnbase.md).

## Privacy

I'll keep this short, because there genuinely isn't much:

- **No analytics, no tracking, no advertising, no third-party cookies.** Nothing
  here tries to identify you or follow you between visits.
- The only data stored on your device is **your own preferences**: your theme
  choice (kept for the session) and your reader settings, the text size and
  typeface. These live in your browser's `localStorage` and `sessionStorage`,
  are read only by this site, and are never sent anywhere. Clearing your browser
  storage resets them.
- **Search runs in your browser.** Your queries go to a search index loaded into
  the page, not to a server.
- A few pages that render math or diagrams fetch a library from a public CDN
  (jsDelivr) when you open them; as with any web request, that CDN can see its
  file was requested. Most pages load nothing from third parties.
- The host, Cloudflare, may keep ordinary server access logs, as nearly every
  web host does. That is infrastructure, not something this site collects or uses.

Because the site stores only strictly-necessary functional preferences and sets
no tracking cookies, there is no consent banner: there is nothing to consent to.

If that ever changes, for example if I add privacy-respecting, cookieless
analytics, I'll note it here first.
