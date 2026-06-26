+++
title = "Site search"
slug = "site-search"
date = 2026-06-25T12:00:00
draft = false

[taxonomies]
tags = ["search", "ux", "frontend"]
+++

## What does this feature do?

Readers can now search the whole site. The magnifier button in the header — or
the `/` key, or Cmd/Ctrl-K — opens a search overlay; typing a query returns
matching posts as you type, each grouped with a snippet of text around the match,
and clicking a result (or pressing Enter on it) jumps to that post. Escape, or a
click outside the panel, closes it. The search covers every post — the logbook,
workflows, and the archived back-catalogue — and matches on the *body* of each
post, not just its title.

## Why was it added now?

The site had crossed the point where finding a specific past post meant scanning
section listings by eye — there are two dozen posts now, across the logbook,
workflows, and the archive. Search was the founding item on the discoverability
backlog, on the principle that if I can reliably find my own writing again, a
visitor can too. It became buildable *now* for a concrete reason: the
[persistent header](@/posts/logbook/mylearnbase/site-header/index.md) had just
shipped, so there was finally somewhere to hang a search trigger.
The engine choice followed from the setup — a static site with no backend rules
out hosted search services, and of the tools that run entirely in the browser,
Pagefind is the one that is actively maintained and built for exactly this. It
indexes the *rendered HTML* after the site builds, so it sees the same pages a
reader does, including the aggregated per-project logbook sections that only
exist after the build runs.

## What's in scope (and what's not)?

In: full-text search across the body of every post — logbook, workflows, and the
archived back-catalogue — through an overlay that opens on click, `/`, or
Cmd/Ctrl-K, with the search UI itself loaded only on first use.

Not in: the site chrome. Navigation, header, footer, and the non-post section
pages are not indexed — search matches post *content*, not the furniture around
it. Also out, by the nature of the setup: any hosted or server-side search (the
site has no backend), Zola's own built-in search index (Pagefind replaces it),
and any record of what visitors search for (there is no analytics or backend to
collect it).

## How do we know it works?

The proof is to use it: press `/` — or Cmd/Ctrl-K, or the magnifier in the
header — right now, and search for a word you remember from a post. The matching
entries surface with snippets, and clicking one takes you there. It works in
light and dark, because the result UI inherits the site's own theme colors.

The pieces that make that happen:

[`templates/post.html:96`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/templates/post.html#L96) at `19c11d9`
> `      <article class="prose" data-pagefind-body>`
>
> Indexing is scoped by one attribute. data-pagefind-body tells Pagefind to index only the post body, which is why the header, nav, and footer text never turn up in results.

[`build.sh:30`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/build.sh#L30) at `19c11d9`
> `npx -y "pagefind@${PAGEFIND_VERSION}" --site public`
>
> The index is built after Zola renders the site — Pagefind reads the finished HTML in public/ and writes its index back into public/pagefind/. Indexing rendered output rather than source markdown is what lets it cover the aggregated `logbook/<project>/` pages, which only exist after the build.

[`static/js/search.js:32`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/static/js/search.js#L32) at `19c11d9`
> `      script.src = "/pagefind/pagefind-ui.js";`
>
> The Pagefind UI bundle is injected on the first open, not on page load. A reader who never searches downloads none of it — the search button is the only cost until it's actually used.

[`static/css/custom.css:429`](https://github.com/RustWright/mylearnbase/blob/19c11d9ec29d4e3584ea7017dbc9b5037eb3f0d6/static/css/custom.css#L429) at `19c11d9`
> `  --pagefind-ui-primary: var(--primary-color);`
>
> Pagefind exposes its UI through its own CSS variables; mapping them onto the site's theme variables makes results adopt the current light/dark palette for free, with no separate dark-mode stylesheet for search.

## What's worth remembering or doing next?

- Search depends on the Pagefind index being built. The repo's `build.sh` runs
  `zola build` and then `npx pagefind`; the Cloudflare build command was switched
  to call it. A plain `zola build` (or `zola serve`) skips indexing, and the
  overlay degrades to a "search is unavailable" message rather than breaking —
  worth remembering when previewing locally.
- The index is regenerated on every deploy, so there is no separate step to keep
  it fresh.
- *How site search actually works* — the spectrum from hosted engines to
  in-browser indexes to post-build HTML indexing — is a strong concepts-demo
  candidate. It came straight out of genuinely not knowing, up front, why "just
  turn on the built-in search" wasn't the trivial change it sounded like.
- Deferred: keyboard navigation through the result list, a visible result count,
  and title-weighting so a query that matches a post's title ranks above an
  incidental body mention. None are blocking; revisit if search gets real use.
