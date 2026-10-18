+++
title = "What the Snake bot was missing"
description = "Watch three Snake bots die, scrub back to the move that really lost each game, and see what the next bot needed to be told."
slug = "what-the-snake-bot-was-missing"
date = 2026-10-18
draft = false

[taxonomies]
tags = ["algorithms", "simulation", "state-representation", "feature-engineering", "reinforcement-learning"]
+++

## The curiosity moment

I started working on this Snake project knowing nothing about [reinforcement learning](https://en.wikipedia.org/wiki/Reinforcement_learning), but wanting to learn how it works by implementing it. In a [previous post](@/posts/concepts/choosing-what-a-snake-bot-sees.md) I discussed how I built a hand-written rule bot to play the game, and how my choice of features decided what it could tell apart.

Feature choice mattered twice as much once I moved from the rule bot to a learner built on a [Q-table](https://en.wikipedia.org/wiki/Q-learning). The table has a limit. The more features I added, the larger it became and the harder it was to train.

So I reimplemented Q-learning with a [neural network](https://en.wikipedia.org/wiki/Neural_network_(machine_learning)), making it a [DQN](https://en.wikipedia.org/wiki/Q-learning#Deep_Q-learning). That let me push past the wall the Q-table had hit, and this post came about as a result of that. The demo below walks through what I saw and tried while building a better Snake bot.

## The demo

In each of the first three missions, one bot plays the same board, and each bot is
told one thing more than the bot before it. The second and third bots
were each designed by watching the previous one die and asking what it would have
needed to know at the move where the game was really lost.

<a id="demo"></a>

{{ demo(name="concepts/what-the-snake-bot-was-missing/snake", wide=true, height=1150, caption="Four missions. In each of the first three a bot plays one board to its death; drag the timeline back to find the move that really lost the game, then reveal it. The last mission averages each bot over 2,000 boards.") }}

Notice that in each replay, the move that lost the game looks safe from the
head. The danger is always somewhere the bot was not told about yet.

## What clicked

My main takeaway is the investigative process it takes to guide a model trained with reinforcement learning. Without touching any other training parameter, I found the gaps in the feature set just by investigating why the model fails, which here means why the snake dies. Visualising the deaths themselves helps a lot too.

Building these visualisations even gave me the next idea, which is to give the Snake bot features that tell it where the escape hatch (the cell of the snake's own body, in the wall enclosing it, that moves away soonest) is located. In many of the games I watched, the escape bot died because it moved towards the escape hatch too early, which left it no room to circle back once the hatch opened. I'm leaving that as an open curiosity for now, one that may bring me back to this project.

There was a side benefit, too. Because I always make myself write these algorithms twice, once in Python with [PyTorch](https://pytorch.org/) and again in Rust with only the standard library, I got to implement [backpropagation](https://en.wikipedia.org/wiki/Backpropagation) and the [Adam optimizer](https://en.wikipedia.org/wiki/Stochastic_gradient_descent#Adam) by hand. That gave me a much deeper understanding than memorising an API would have.

## Where this shows up

- [Choosing what a Snake bot sees](@/posts/concepts/choosing-what-a-snake-bot-sees.md),
  the five-number bot this one starts from.

All of the code behind this post, the Python and Rust versions of every bot and the
experiments that did not make it in, is on [GitHub](https://github.com/RustWright/snake-dqn).
