+++
title = "Two Languages, Two Bottlenecks"
slug = "two-languages-two-bottlenecks"
date = 2026-08-22
draft = false
aliases = ["/posts/logbook/two-languages-two-bottlenecks/"]

[taxonomies]
tags = ["performance", "algorithms", "rust", "simulation"]

[extra]
math = false
+++

In [a previous article](/posts/concepts/a-flock-is-a-control-loop/) I showed how a flock of boids can be tuned like a controller. By varying the weight on each proportional rule, you shape the group's behaviour the way you would tune a PID loop. That example used a small flock, where efficiency wasn't a concern because the loop stayed smooth at that scale.

In real production settings, small populations and simple loops are a luxury you don't get. This article pushes the simulation to a much larger flock and follows where the bottlenecks show up, how to spot each one, and what actually fixes it.

## The interpreter tax

All the initial work for this project is in Python, which is famously easy to read and write. But Python is interpreted, so any loop written purely in it is slower than the same loop in a compiled language like C, C++ or Rust.

That interpreter cost is the first bottleneck to overcome. The baseline for everything that follows is a plain Python loop over individual boid objects, written with pygame's C-accelerated Vector2 so even the starting point isn't as slow as pure Python would be. Even with that advantage, every iteration still pays the interpreter tax, the overhead of all the work Python does to compute the next step.

The common fix is to get out of the interpreter's way, handing the expensive work to a library written in a faster language. Here that library is NumPy, which moves the heavy parts of the loop out of Python and into compiled C. The payoff is immediate. On the same machine, the NumPy version runs the same math about 3× faster than the baseline. This is the first drop you can see in the chart, with the pure-Python loop highest and NumPy's all-pairs line about 3× below it.

![The benchmark so far, Python only. The pure-Python loop is highest, NumPy all-pairs about 3× below it, and the NumPy grid crossing all-pairs near N=500.](/demos/concepts/two-languages-two-bottlenecks/chart-python.svg)

## Why reach for a spatial grid

With the interpreter dealt with, the next obvious bottleneck is how computationally wasteful the baseline algorithm is. To apply the cohesion, separation and alignment rules, every boid has to answer "who is my neighbour?" And to answer it, the baseline checks and filters the entire population, no matter what, every, single, time.

When the population is small, like the N=100 flock from the tuning post, this barely matters. But as the flock grows into the thousands and tens of thousands, and the canvas grows with it, it becomes obviously wasteful to keep testing boids on opposite sides of the canvas as potential neighbours. In big-O terms every boid is compared against every other, so the baseline is O(n²), its cost growing quadratically with the population.

The accepted solution for this issue is breaking up the entire canvas into a spatial grid. Now, instead of scanning the whole population, each boid only searches the cells that could actually hold a neighbour, the cell it's in and the 8 around it, a 3×3 block shown in the figure below. So as N grows the cost rises only linearly, O(n), instead of quadratically, which means a much faster loop at large N.

![A canvas split into grid cells. One boid searches only its own cell and the 8 around it, a 3×3 block; boids outside the block are never checked.](/demos/concepts/two-languages-two-bottlenecks/grid-search.svg)

## When the faster algorithm loses

So far the story is simple. At large N the O(n) grid beats O(n²) all-pairs, all else held equal. But all else is rarely equal, and that's exactly what I ran into implementing the grid myself.

I did it by moving some of the work I'd handed to NumPy back up into the Python layer, simply because that was easier to write for the comparisons I wanted to make. But that muted the gains from running the loop in C, because it forced a constant hand-off back and forth between C and Python.

You can see it in the numbers. At small N, the "less efficient" O(n²) all-pairs version, which does more of its work in NumPy, actually beats the O(n) grid. On my machine the grid didn't pull ahead until the population passed ~500 boids, right where you can watch the two Python lines cross in the chart. After that the O(n) grid was the clear winner.

So how an algorithm is implemented, not just its big-O, decides its real-world speed, and what counts as a good implementation depends on the language.

## Across the border into Rust

The demo needs to run in a browser, and browsers can't natively interpret python, so I need the same logic expressed in something web-native such as javascript or WASM to let you test out and experience the different concepts discussed in this post.

I enjoy working in Rust, which compiles cleanly to a WASM binary, so that's what I reached for. The first thing you notice is that Rust, being a modern compiled language, is much faster even with the naive O(n²) all-pairs loop, beating the NumPy grid across every population size I tested. In the chart, the whole Rust band sits an order of magnitude or more below the Python lines. This is the same constants-versus-asymptotics story in reverse though. Rust's naive loop is still O(n²), so a large enough N would eventually let NumPy's O(n) grid win out, but Rust's constant factor is so small that the crossover sits somewhere past ~15,000 boids, beyond anything this demo runs.

So the first bottleneck, the interpreter, simply doesn't exist in Rust, which means the first thing worth optimizing is the algorithm itself. I've already covered why the O(n) grid beats O(n²) all-pairs at scale, so I won't repeat it.

I will point out, though, that just like in Python, how the algorithm is implemented introduces constant factors that cap its speed. My first attempt allocated a fresh data structure of neighbours for each non-empty cell, then combined all those little structures into one big list of neighbours for the boid. Each allocation is costly, and they add up. With that implementation the naive all-pairs (O(n²)) stayed faster until the population passed ~900 boids, and only after that did the grid's O(n) win out.

After some refactoring, the grid allocated a single structure once at the start of the loop and filled it as it went, adding neighbours while it searched the relevant non-empty cells. That version pulled ahead almost immediately, outperforming all-pairs below 100 boids, and in the chart it runs below the naive line from the very first point.

{{ demo(name="concepts/two-languages-two-bottlenecks/naive-vs-grid", wide=true, height=760, caption="Naive O(n²) against the spatial grid, live in Rust and WebAssembly. Toggle the mode and drag N upward.") }}

## Memory layout, the last lever

Rust is a compiled language, so it's already fast, check, and we've implemented an algorithm that performs better at larger population sizes by avoiding wasteful searches, check. The next natural question is if there is anything else we can do to improve performance in Rust beyond this.

And the answer is yes. Yes there is. There's one feature of NumPy I haven't highlighted yet, and it is the memory layout of the data. That layout, on top of the loop being written in C, is a second reason NumPy runs even faster. Here the layout means this. Instead of keeping all of one boid's data together in a single structure, a class in Python or a struct in Rust, you keep the same field for every boid together in one array, with a parallel array per field, and operate on whole arrays at a time.

This layout is faster because of how modern CPUs and compiled languages actually move and process data. I won't go too deep into the weeds, but the layout unlocks two things a compiler can exploit, cache locality and SIMD (Single Instruction Multiple Data).

Cache locality helps because the CPU pulls data from memory in chunks and keeps those chunks in a fast cache. When every boid's x is stored together in one array, each fetched chunk is far more likely to already hold the value the processor needs next, so it spends less time sitting idle waiting on memory.

SIMD helps for a related reason. A single CPU instruction can run the same operation on a whole batch of values at once, so work that would take N steps one value at a time finishes in a fraction of that, depending on how many values fit in a batch. The figure below shows why the layout matters. One memory load grabs a single boid's four fields when a boid's data is stored together, but four boids' worth of one field when it's stored field-by-field, so one instruction can update four boids at once.

![AoS versus SoA memory layout. The same 4-wide load reads one boid's four fields in AoS, but four boids' worth of a single field in SoA.](/demos/concepts/two-languages-two-bottlenecks/aos-soa.svg)

In Python you never had a choice about this layout, it comes baked into NumPy, and its speedup is folded inseparably into that same 3× from earlier. However, Rust is already compiled, so the layout becomes a deliberate choice, and something you can measure on its own by holding the algorithm fixed and changing nothing else. I adopted it anyway, without any ergonomics crates, just for the learning experience.

For me it was a lot more intuitive to think through the boid algorithms when treating each boid as a separate independent structure within an array, so an Array of Structures (AoS). The Structure of Arrays (SoA) version took some getting used to, since you reason about whole operations across all the boids at once and track each one by its index instead. You pay that intuition price to get the performance, but once the SoA way of thinking clicks, the payoff is clear. In the chart the two lowest lines are both this same Rust grid, and the only thing separating them is AoS versus SoA. There's a reason a lot of python libraries like Numpy, Pytorch and Tensorflow are built on this kind of array-based computation.

![The full benchmark matrix, all six implementations on one log-log chart. The four Rust lines sit an order of magnitude or more below the two Python lines.](/demos/concepts/two-languages-two-bottlenecks/chart-full.svg)

So what's the point of the whole exercise? Taken together, the chart tells the whole story in one view. At N=1000 the fastest implementation runs nearly 500× faster than where we started. On any real project at scale, you have to understand the actual bottlenecks before you can pick the lever that buys the biggest improvement. And just as importantly, as every example here has shown, how you implement that lever decides how much it actually buys you. A wasteful implementation adds constant factors that quietly cap your performance ceiling.

All of the code behind this post, the Python reference and the Rust port with both memory layouts, is on [GitHub](https://github.com/RustWright/boids-flocking-sim).
