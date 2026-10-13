+++
title = "The checkpoint lottery"
description = "A Q-learning agent's score swung between 7 and 48 across one training run. Drag a slider to stop training at any point and watch the table you would have shipped actually play."
slug = "the-checkpoint-lottery"
date = 2026-10-13
draft = true

[taxonomies]
# `reinforcement-learning` is new to the vocabulary and genuinely fits here, where
# the earlier Snake post deliberately avoided it (nothing in that one learned).
tags = ["simulation", "algorithms", "reinforcement-learning"]
+++

<a id="demo"></a>

{{ demo(name="concepts/the-checkpoint-lottery/checkpoints", wide=true, height=910, caption="One training run, measured every 500 episodes. Drag the slider to stop training at that point, and the snake plays with the table you would have saved. The live average builds up over repeated games, because a single game proves nothing either way.") }}

<!-- DRAFT. The demo above is finished; the prose is not written.

     Per editorial/concepts.md the voice-bearing sections are the author's to
     draft first, so they are left as marked gaps rather than filled with a
     plausible-sounding version. What is drafted below is descriptive framing.

     Facts available, all measured and reproducible:
       - swing across 39 checkpoints: 7.44 to 47.71 (greedy, 300 games each)
       - best checkpoint is episode 12,000; the final episode scores far lower
       - alpha = 0.09 constant, gamma = 0.992, epsilon decayed over 5,000 episodes
       - the shipped table measures 49.85 (bench seed 0) / 48.85 +/- 0.39 (held out)
       - the CP-2 rule bot it has to beat: 30.68 +/- 0.06
-->

## The curiosity moment

<!-- GAP: author's own words. Where the question actually came from. -->

## What a constant learning rate does

The update that trains this agent nudges one number toward a new estimate:

```
Q[state][action]  +=  alpha * (target - Q[state][action])
```

That is not a step toward an answer so much as a running average. With `alpha`
held constant at 0.09, each new sample always carries the same weight, so the
estimate keeps a memory of roughly its last eleven visits and no more. It never
stops moving, because the newest reading always gets its full share of the vote
no matter how much evidence came before it.

The consequence is the curve above. It is not a climb with noise on it. It is an
orbit, and where it happens to be when training stops is what gets saved.

## What clicked

<!-- GAP: author's own words, or cut this section entirely.
     concepts.md: "A forced reflection reads flat; an absent one reads fine." -->
