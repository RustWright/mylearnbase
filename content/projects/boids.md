+++
title = "Boids flocking simulation"
description = "A flocking simulation built three ways, from a Python reference to a Rust core compiled to WebAssembly, used to study control-loop tuning and neighbour-search performance."
weight = 10

[extra]
# active | complete. Anything else fails the build (templates/project.html).
status = "complete"
period = "July – September 2026"
stack = ["Python", "NumPy", "Rust", "WebAssembly", "Dioxus"]
# The PUBLIC export. The working repository is private and must never be linked.
repo = "https://github.com/RustWright/boids-flocking-sim"
posts = [
  "posts/concepts/a-flock-is-a-control-loop.md",
  "posts/concepts/two-languages-two-bottlenecks.md",
]
+++

Three simple rules, applied to each boid on its own, are enough to make a whole flock move together. This project builds that simulation three times over, and each version asks a different question of the same system.

The first version is a scalar Python reference, where each boid is an object and each rule is plain vector math. The second rewrites it with NumPy and a spatial grid, so finding a boid's neighbours no longer scales with the square of the flock. The third ports the core to Rust and compiles it to WebAssembly, which is what runs in the demos on this page. A correctness check confirms that the grid finds exactly the same neighbours as a brute-force search.

Two write-ups came out of it. The first reads the three flocking rules as a bank of proportional controllers and looks at how the flock responds as each gain changes. The second pushes the flock to thousands of boids and follows where each language hits its bottleneck, and what actually fixes it.
