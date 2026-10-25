+++
title = "Playground"
description = "A few interactive toys that need no reading: herd a flock of boids, try to outscore a Snake-playing neural network, and build an SVG by hand."
template = "playground.html"

[extra]
title = "Playground"
subtitle = "Things to play with, no reading required. Each one has a write-up if you get curious."
+++
{{ toy(name="snake/versus", post="posts/concepts/what-the-snake-bot-was-missing.md", caption="Play a board of Snake with the arrow keys or a swipe, then watch a neural network play the same board. Can you outscore it?") }}
{{ toy(name="boids/herd", post="posts/concepts/a-flock-is-a-control-loop.md", caption="You are the predator. Chase a flock of boids apart into two groups, then three, up to six, against the clock.") }}
