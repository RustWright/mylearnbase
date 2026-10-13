+++
title = "Choosing what a Snake bot sees"
description = "A hand-written Snake bot decides every move from five numbers. Watch the three cells it inspects, read its state vector as it plays, then take the controls yourself."
slug = "choosing-what-a-snake-bot-sees"
date = 2026-10-13
draft = false

[taxonomies]
tags = ["simulation", "algorithms", "state-representation", "feature-engineering"]
+++

<a id="demo"></a>

{{ demo(name="concepts/choosing-what-a-snake-bot-sees/snake", wide=true, height=1160, playground=true, caption="Watch the rule bot play, with the three cells it inspects drawn on the board and its five-number state vector live underneath. The second tab hands you the arrow keys.") }}


## The curiosity moment

This post came about because I'm going through a self-created curriculum to learn all the skills needed for autonomous robotics. I'm still early on the journey and I wanted to learn how Q-learning worked before moving on to the more complex concepts, and designing a bot to play the classic Snake game seemed like a good starting point. Before any of that learning could happen though, there was an earlier problem to solve, and this post is about that one rather than about Q-learning itself.

Before building the bot, I first had to decide what aspects of the game state it would be allowed to see. Too few features and the bot cannot tell two genuinely different situations apart. That is called perceptual aliasing, and no amount of training fixes it, because the information was never in the key to begin with. Too many and situations that are effectively identical get filed separately, so the same lesson has to be learned again for each one.

The demo above visualizes the choice I settled on. Everything the bot sees is relative to its own head rather than to the board, so it is told that food is ahead and to the left, never that food is at column 14, row 3.

## What the five numbers are

Every move the bot makes comes out of five values, and nothing else reaches the
decision. Two of them place the food relative to the direction the snake is
currently pointed. One says whether it is ahead, level, or behind. The other
says whether it sits to the left, dead in line, or to the right. The remaining
three ask whether the cell to the left, straight ahead, and to the right would
kill it.

That is the whole interface between the game and the thing playing it. The
snake's length, the shape of its body beyond one cell, and how much open space
sits behind a wall of itself are all absent. Turn on "Show what the bot sees"
and the three inspected cells are drawn directly on the board, so what the bot
is blind to is visible as everything that stays unmarked.

The counter reading "states seen" is the other half of the picture. Five
features in this encoding combine into exactly 64 distinct situations, and a
single game walks through a surprisingly small fraction of them.
