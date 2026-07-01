+++
title = "Measuring document similarity with TF-IDF"
slug = "tf-idf"
date = 2026-07-01
draft = false

[taxonomies]
tags = ["tf-idf", "search", "vectors", "algorithms"]
+++

## Where the question started

Every post on this site ends with a short list of **Related** links, and none of them are hand-picked. A script reads the words of every post and works out which ones are about the same kind of thing. That is the puzzle this post is about: how can comparing *words* tell you two posts share a *topic*, when two articles on the same subject might not use many of the same words at all?

The [earlier post on search indexing](@/posts/concepts/how-search-works.md) left a related thread hanging. It stopped at *finding* the documents that contain your search terms, and noted that ranking them, deciding which comes **first**, was a separate question. That ranking uses the same method as the Related links: **TF-IDF**, which is built from two numbers that are weak on their own and sharp together.

## Try it: what is a document about?

Start with a simpler question than similarity: if you had to summarise a document with a handful of its own words, which words would you pick? The demo below scores every word in twelve Wikipedia articles three ways. Flip between them and watch which words rise to the top of each card.

{{ demo(name="concepts/tf-idf/ablation", height=900, wide=true, caption="Twelve Wikipedia articles, four topics. Score each word by raw count (TF), by rarity across the collection (IDF), or by the two multiplied together (TF-IDF). Watch which words each method promotes.") }}

The lesson is in the failures of the first two:

- **Count alone (TF)** promotes `the`, `of`, `and`. Every document's summary looks identical, because the most frequent words are the most frequent words in *any* English text.
- **Rarity alone (IDF)** overcorrects. It loves words that appear in almost no other article, which surfaces one-off oddities that happen to be rare but say little about the whole document.
- **The two multiplied (TF-IDF)** keeps only words that are frequent *in this document* **and** rare *across the collection*. Now each card reads like a fingerprint of its topic: `python, indentation, statement`; `mars, martian, geological`. Frequency says "this matters here"; rarity says "and it's distinctive." Neither is enough by itself, which is the whole point.

## Try it: how alike are two documents?

Once every word has a TF-IDF weight, a document becomes a long list of numbers: one weight per word. That list is a **vector**. To compare two documents you line their vectors up, multiply the two weights on each word, and add up the results. That single number is the **cosine similarity**: 0 when they have nothing in common, 1 when they point in exactly the same direction.

{{ demo(name="concepts/tf-idf/vector-space", height=780, wide=true, caption="Pick any two of the twelve documents. The score is decomposed into one contribution per shared word, and the panel on the right ranks each document against all the others.") }}

A few things worth watching:

- The score is **built out of words you can see**. Each shared word contributes its two weights multiplied together, and those contributions sum exactly to the cosine. No single word carries it; the similarity is the accumulation of many small agreements.
- A word that **only one** document uses contributes nothing. It multiplies against a zero on the other side and drops out. `africa` and `mane` are core to the Lion article, but Tiger never uses them, so they add nothing to how alike the two are. Only *shared* vocabulary moves the needle.
- Now the surprising part, in the ranking panel: even the best score sits well below 1. Lion's nearest neighbour, Leopard, is only about 0.40. That is not a bug, and it is worth knowing why.

In a space with thousands of word-axes, almost any two documents point in nearly perpendicular directions, because no two real texts overlap on more than a small fraction of the vocabulary. High-dimensional vectors trend toward being mutually orthogonal; low similarity scores are the normal, expected state ([Ni et al., 2024](https://arxiv.org/abs/2401.00422)). So the absolute number is not the signal. The **ranking** is: Lion's own kind (Leopard, Tiger) sits clearly above everything else, even though 0.40 sounds unimpressive. When the site picks Related links, it never asks "is this above some bar"; it asks "which are the closest few," and closeness is always relative.

## Try it: bring your own text

Nothing above was special about Wikipedia. Any two chunks of text become vectors the same way, so the same cosine compares them. A search query, in fact, is just an extreme case of a document: one line long. Paste your own text into both boxes below, or click an example, and watch the score assemble itself.

{{ demo(name="concepts/tf-idf/your-text", height=560, wide=true, caption="Compare any two pieces of text. Blank to start; the example buttons load pairs that score very differently. Your text never leaves the browser.") }}

The three examples are chosen to land in three different places, and the third is the interesting one:

- Two descriptions of espresso score **clearly related**: they genuinely reuse the same words.
- Coffee versus photography scores **loosely related**, on the strength of `good`, `steady`, and `shot`. None of those are about either topic, and `shot` means two completely different things. The method sees only the string.
- Two sentences that plainly *mean* the same thing ("the film was a slog" / "what a tedious movie") score **zero**. They share no words at all, so TF-IDF sees nothing in common.

That last case is the ceiling of this whole approach. It can only ever compare the words that are literally present, and people rarely choose the same words for the same idea. In a classic study, two people picking a term for the same familiar concept agreed less than 20% of the time ([Furnas, Landauer, Gomez & Dumais, 1987](https://dl.acm.org/doi/10.1145/32206.32212)). Getting past that means representing *meaning* rather than *spelling*, which is what learned embeddings do, and what modern search systems increasingly blend with the lexical scoring shown here ([Gao, Dai & Callan, 2021](https://aclanthology.org/2021.naacl-main.241.pdf)).

## What clicked

Working on this post with Claude, two things clicked for me.

The first was realising that a search query is a document in its own right, one you can run through the very same algorithm. I had never thought of it that way, and building the demos is what surfaced it.

The second was how low the cosine similarity stays, even for texts that are clearly related. In my head I had pictured the vectors for similar texts lining up almost perfectly. What the demos show is that the number is only really meaningful in a relative sense: the useful question is whether one document is more related than another, not how aligned any two documents are on their own.



## Where this shows up

The Related links under this very post were chosen by exactly the machinery above: the same TF-IDF vectors, the same cosine, the same "closest few" ranking. The [build log for that feature](@/posts/logbook/mylearnbase/related-posts/index.md) has the plumbing; this is the *why* underneath it.

Two honest edges to it, both already visible in the demos:

- It works better here than it would in general. This is a single-author site, so the same person reuses the same vocabulary from post to post, and shared words really do track shared topics. Across many authors writing about the same things in different words, the vocabulary mismatch above would bite much harder. A meaning-based upgrade (static embeddings) is the planned next step if the word-overlap matches ever start reading weak as the writing here gets more varied.
- The same math answers the ranking question the [search post](@/posts/concepts/how-search-works.md) left open. Once search *finds* the documents containing your words, deciding which comes **first** is a cosine between your query and each document, with the rarer query words weighted more. Finding and ranking are the same trick, run at two different scales.
