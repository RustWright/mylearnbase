+++
title = "How indexing can make search faster"
slug = "how-search-works"
date = 2026-06-27

[taxonomies]
tags = ["search", "data-structures", "indexing", "algorithms"]
+++

## Where the question started

The question started with needing to add search to mylearnbase. I use Zola as my static site generator, so I figured turning on search would be a trivial switch to flip, since Zola has built-in search functionality. But Claude suggested the Pagefind JS library instead. Pagefind's main draw is its chunked indexes, which cut down how much data has to be sent over at any one time, plus an easier UI to wire up and the appeal of letting a maintained library handle the indexing for me.

The options came in a few flavors: in-browser JS indexes like Lunr and Fuse, hosted search services like Algolia and Meilisearch, and Pagefind. Trying to understand the trade-offs between them pulled me into digging deeper into how search actually works than I'd expected when I first thought to add the feature.

Since I hadn't written a concepts post yet, this felt like a natural first one. The core optimization behind modern search is that an index speeds things up when you expect to query a data source many times, and I wanted to turn that into something you can build an intuition for by playing with it.

That's enough setup. Try the demo below and poke around to get a feel for indexes: when and why they earn their place.

## Try it: scan vs. index

The demo below races two ways of answering the same question (*find every line
that mentions a word*) against the real text of *The Adventures of Sherlock
Holmes*, one sentence per "document." Walk the four missions: first on a handful
of lines, then on all 5,463 of them. The last mission asks the question that
actually matters: whether building the index was worth it at all.

{{ demo(name="concepts/how-search-works", height=760, wide=true, caption="Race two ways to search the same book: scan every line, or look the word up in a prebuilt index. Four missions, ending on whether the index earns its keep. Works best on a wider screen.") }}

Two things worth watching. First, how the scan's comparison count climbs with the
size of the book while the index's stays stuck at **one**. Second, in the last
mission, the exact point where the index's up-front build cost finally pays for
itself.

## Where this shows up

The move underneath all of this is *pre-arrange your data around the question
you'll ask, so the question becomes cheap,* and it isn't really about search. It's
a database index, a hash map, a cache, a memoized function: pay an up-front cost
once so every later lookup is nearly free, worth it only when you'll ask often
enough to amortize the build. Once you've felt it here, it's hard to stop seeing
it.

A couple of threads from here:

- The search box on this very site is the same idea in production. See the
  [build log for adding it](@/posts/logbook/mylearnbase/site-search/index.md).
- This demo stops at *finding* the matches. Which of them comes **first** is a
  separate step, covered in the [post on measuring document similarity with
  TF-IDF](@/posts/concepts/tf-idf.md).
