+++
title = "A Flock Is a Control Loop"
slug = "a-flock-is-a-control-loop"
date = 2026-08-03
draft = false

[taxonomies]
tags = ["control-systems", "simulation", "emergence"]

[extra]
math = true
+++

<a id="demo"></a>

{{ demo(name="concepts/a-flock-is-a-control-loop/flock", wide=true, height=820, caption="The finished flock, all three rules live.") }}

Watching emergent group behaviour after defining simple rules on the individual level brings a genuine smile to my face. After working on this project I've caught myself just staring at the boids as they move around the screen, because of how satisfying it looks.[^build]

Without understanding the control loop dynamics it feels like magic that defining rules for each boid creates group behaviour that is stable and organized.

We'll break down how to describe and analyse the group's emergent behaviour from the lens of a controls engineer. We'll also review how the behaviour can be tuned to create different system effects by adjusting the three rules affecting the emergent behaviour.

## The three rules, one at a time

- **Cohesion**: acts on a boid's velocity to pull it closer to the center of the group of boids closest to it.
- **Separation**: acts on a boid's velocity to force it away from its nearest neighbours and ensure boids never overlap in position.
- **Alignment**: acts on a boid's velocity to force a boid to point in the same direction as the group around it.

If any of the three rules is missing the emergent behaviour cannot be described as flocking

![Containment only: boids drift and bounce off the walls — no flocking forces yet.](/demos/concepts/a-flock-is-a-control-loop/boids_1_wall_only.gif)

1 - **Basic boid containment rules**: these rules keep the boids acting within the boundary of the simulation. The boids are set to start moving in different directions and are repulsed from any wall they get too close to.

![Cohesion on: nearby boids collapse together and swarm around a centre.](/demos/concepts/a-flock-is-a-control-loop/boids_2_cohesion.gif)

2 - **Adding cohesion**: when cohesion is turned on any boids close enough to each other collapse and swarm around a central point. They behave more like a group of mosquitos than a flock of birds since there is no defined shape.

![Cohesion + separation: the swarm spreads into evenly spaced groups.](/demos/concepts/a-flock-is-a-control-loop/boids_3_cohesion_separation.gif)

3 - **Adding cohesion and separation**: cohesion brings the boids together but separation ensures that they are spaced out far enough that the shape of a group can start to form once enough boids are close together. Although the boids are attracted to each other and move as a group, they do so in a chaotic looking manner.

![All three rules: the group aligns and moves as a single flock.](/demos/concepts/a-flock-is-a-control-loop/boids_4_full_flock.gif)

4 - **Adding all three rules to create the flock**: with cohesion holding groups of boids together, and separation keeping them spaced apart so they have a clear formation and structure, alignment is what makes a group of boids seem to behave like a single unit. Alignment makes each boid *align* its direction with that of the group, so the group of boids acts as a flock.

Only with all three turned on and properly balanced does the group of boids behave like a flock. Weaken or drop any one and it collapses into some other state, stable or not.

Now that we've discussed each of the rules and how they contribute to the emergent flock behaviour, let's see how to analyse each rule from a controls engineer's perspective.

## Each rule is a controller

I'll be using the *alignment rule* as an example since it's the switch that takes the boids from looking chaotic to looking like a single unit.

The alignment rule measures an error which is the difference in the *direction* between any specific boid and that of the group. If the boid is pointing perfectly in line with the average velocity of the group, there is no error to correct. Conversely, if the boid is pointing in the exact opposite direction of the group this is the maximum error scenario with the strongest corrective effect.

The error is then multiplied by an *alignment gain* which amplifies the effect it has on the velocity. The higher the gain, the more aggressively the boid tries to correct its velocity to get back in line with the rest of the group.

Viewing each rule as a proportional controller allows us to analyse the entire system as a control loop.

With cohesion the error is the distance between a boid and the centroid of its group. The correction to this error is amplified by the cohesion gain and is acting to bring the boid closer to the centroid.

With separation the error is the sum of the differences between a boid's distance to all its neighbours and the maximum possible distance it can be from a neighbour. The closer a boid is to its neighbours, the larger the proportional effect pushing it away as far as its neighbour sensing boundary. The rule creates this effect by applying a resultant vector sum of all the vectors pointing away from the neighbours with a separation gain applied to it. When the entire system is considered together there is a balance between the cohesion rule and separation rule that allows the boids to sit a stable distance away from one another in *formation*.

And with alignment as described already, the error is the difference in the direction of travel of the boid and that of the group, amplified by the alignment gain and acting to bring the boid in line with the group.

## Break it

There are two failure modes I want to highlight using this demo. Each failure mode will demonstrate one possible way control systems can fail.

Before reading the explanations below, I recommend you try two different experiments yourself with the demo at the start of this post ([jump back to it](#demo)). The explanations below would make a lot more sense once you've gotten a chance to see the effects yourself.

Experiments:

1. Starting with the provided pre-set stable flocking state, try to make the flock *more aligned* by increasing the alignment gain. What do you observe when the gain is increased too far?
2. Starting with the stable state, play around with the ratio between the cohesion gain and the separation gain. Does the system remain stable? Without setting **Separation to 0**, can you get all the boids in a flock to perfectly overlap with each other so it looks like a single boid?

### Over-aligned

Ok, I'm assuming you've tried the first experiment and noticed a unique property of the system that might seem counterintuitive if you don't understand the underlying mechanisms.

Increasing the alignment gain doesn't always make the system *more aligned*. Past a point, it makes the system less stable.

Consider the equation:

$$\text{new error} = \text{old error} - (W \times \text{old error}) = \text{old error} \times (1 - W)$$

That equation comes from the fact that for alignment, the old error encodes how far off we are from an error of 0, the equilibrium point. With an old error we multiply it by the gain to determine what correction needs to be substracted to bring the error to 0 as quickly as possible.

Imagine two scenarios:

1. With a gain of 1.5, starting from an error of 8:

<div>
$$
\begin{aligned}
\text{new error} &= 8 \times (1 - 1.5) = 8 \times -0.5 = -4 \\
\text{new error} &= -4 \times (1 - 1.5) = -4 \times -0.5 = 2 \\
\text{new error} &= 2 \times (1 - 1.5) = 2 \times -0.5 = -1
\end{aligned}
$$
</div>

Each step overshoots zero, but by less each time which means the error decays toward equilibrium.

2. With a gain of 15:

<div>
$$
\begin{aligned}
\text{new error} &= 8 \times (1 - 15) = 8 \times -14 = -112 \\
\text{new error} &= -112 \times (1 - 15) = -112 \times -14 = 1568 \\
\text{new error} &= 1568 \times (1 - 15) = 1568 \times -14 = -21,952
\end{aligned}
$$
</div>

Each overshoot is bigger than the last which means the error runs away.

This process continues with the error that the proportional system is trying to correct for continuously growing because of an overly aggressive alignment gain.

The demo used in this post has a limit applied to the maximum speed allowed for any boid. So, while the control logic suggests that increasing the gain will lead the error and by extension the velocity to spiral out of control, the speed limiter stops that from happening. 

All you'll see are more chaotic boids.

### Too Much Cohesion
Now for the second failure mode where you tried to make the entire flock collapse to form a single boid without setting Separation to 0. 

I'm pretty confident you weren't successful. Let me explain why.

Whereas increasing the alignment gain led to an unstable system, allowing the effect of the cohesion rule to overwhelm that of the separation rule can lead to a different kind of failure even if the system remains stable.

If the gain of the cohesion rule is increased in relation to the separation gain, with alignment held constant, visually the flock loses its evenly spaced and organized shape and collapses into a tighter structure.

The separation rules are written to guarantee two boids never perfectly overlap. This means the entire flock won't collapse to a single point, but the desired shape of the system is lost when one gain is allowed to grow and overshadow another.

This holds only while separation is actually switched on since it's the relative strength of the two rules that's in play. Drop the separation gain all the way to zero and nothing resists cohesion, so the flock really does collapse to a single overlapping point.

The system might still be able to find a stable equilibrium state with the cohesion gain much larger than the separation gain, but the visual effect of flocking would be lost in the process.

## What's the Point of All of this?

Understanding how to analyse and tune the boid simulation as a control system is useful because the same systems thinking approach and tools can be applied to a physical controller or to an ML algorithm. Each application is just a different approach to minimizing system error to reach a desired state/equilibrium.

[^build]: I wanted the demo to be something you could actually tune, which means running the simulation live in the page as WebAssembly. I'd built and tuned the logic in Python, but Python isn't suited to compiling to WASM, so I rewrote it in Rust to get the embeddable version. A write-up on that port is coming.
