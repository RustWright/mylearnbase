+++
title = "Where the indices go in a Coriolis matrix"
description = "How three indices pick entries of the mass matrix to build the Coriolis matrix C. Watch each entry get built, predict the cells, then check the result live."
slug = "christoffel-symbols"
date = 2026-10-12
draft = false

[taxonomies]
tags = ["robotics", "dynamics"]

[extra]
math = true
+++

## Where the question started

I needed to derive the system dynamics for a 2-DOF exoskeleton leg in a project I was working on. Using the [Lagrangian](https://en.wikipedia.org/wiki/Lagrangian_mechanics) seemed like the best method, but I was a bit rusty and needed to refresh my understanding of how it worked. Figuring out the mass matrix and gravity vector was pretty straightforward, but I just couldn't wrap my head around how the indices worked when using Christoffel symbols to create the Coriolis matrix.

After several unsuccessful attempts to figure it out on my own, I had Claude build me a visual, interactive demo. That was what helped things click for me. That's what you see below. It helped me, so I hope it's useful for you, or for future me when I forget how this works again.

## The shape everything stacks into

Lagrange's method gives one equation of motion per coordinate. For a robot arm, a leg, or a cart with a pendulum on it, those equations always stack into the same matrix form:

$$
M(q)\,\ddot q + C(q,\dot q)\,\dot q + G(q) = \tau
$$

$M(q)$ is the **mass matrix**, read straight off the kinetic energy, $T = \tfrac12\dot q^{\mathsf T} M \dot q$. $G(q)$ is the **gravity vector**, one entry per equation, $G_k = \partial V/\partial q_k$, where $V$ is the potential energy. $C$ is the awkward one. It collects every term where two velocities multiply, $\dot q_i\dot q_j$. These are the centrifugal and Coriolis terms, which is why $C$ is called the Coriolis matrix. The standard way to build it is from **Christoffel symbols**, coefficients $c_{ijk}$ made out of partial derivatives of $M$ alone. This post calls the formula below "the recipe":

$$
c_{ijk} = \tfrac12\left(\frac{\partial M_{kj}}{\partial q_i} + \frac{\partial M_{ki}}{\partial q_j} - \frac{\partial M_{ij}}{\partial q_k}\right),
\qquad
C_{kj} = \sum_i c_{ijk}\,\dot q_i
$$

Three indices, three partial derivatives, and each index moves to a different slot in each term. Here $k$ is the equation, so it is the row of $C$; $i$ and $j$ name the two velocities being multiplied. Textbooks disagree on which slot means "the equation," so the first thing to check in any source is which index plays that role. These demos follow [*Robot Modeling and Control*](https://faculty.cc.gatech.edu/~seth/SHV/) by Spong, Hutchinson and Vidyasagar. The book calls the mass matrix $D(q)$, with entries $d_{kj}$, where this post writes $M(q)$.

The demos use two small systems whose answers are easy to check by hand: a puck sliding on a table in polar coordinates, and a cart on a track with a pendulum hanging from it. Both have two coordinates, so $M$ and $C$ are $2\times2$. Differentiating $M$ by each coordinate gives one $2\times2$ matrix per coordinate, $\partial M/\partial q_1$ and $\partial M/\partial q_2$, and stacked together they form a $2\times2\times2$ cube.

## Watch C get built

The demo below builds $C$ one entry at a time. Pick an entry of $C$, press **Step**, and follow each piece. The recipe picks out an entry of $M$, differentiates it, combines it with two others, multiplies by a velocity, and adds the result into its cell.

{{ demo(name="concepts/christoffel-symbols/build", height=1420, wide=true, caption="The recipe run one move at a time. Each entry of M flies to the workbench, is differentiated, combined and multiplied by a velocity, then lands in its cell of C. Open it standalone on a wide screen to see M, the workbench and C side by side.") }}

What to notice:

- The row and column of the entry fix $k$ and $j$. Only $i$ varies, which is why every entry is a sum of exactly two pieces in a two-coordinate system.
- For the puck, the $-mr\dot\varphi$ in $C_{12}$ is what produces the $-mr\dot\varphi^2$ centrifugal term in the first equation once $C$ multiplies $\dot q$.
- For the cart and pendulum, the second row of $C$ comes out zero even though nonzero entries of $M$ get picked and differentiated along the way. They cancel, which is why the pendulum's own equation has no velocity-times-velocity term.

## Which three cells?

Watching is one thing; picking the cells yourself is the test. This demo shows the recipe and the whole cube of partial derivatives, then asks you to click the three cells the recipe combines for a given coefficient, before it shows you the answer.

{{ demo(name="concepts/christoffel-symbols/predict", height=1170, wide=true, caption="Read a coefficient's indices off a term in the equations of motion, then click the three cells of the cube the recipe combines. Build a whole row of C, then find the cancellation in the cart and pendulum.") }}

What to notice:

- After the first attempt, the pattern opens. Terms 1 and 2 keep $k$ in the row of $M$, because together they are $\dot M\dot q$, which is equation $k$'s own row of $M$ changing as the system moves. Term 3 drops $k$ to the bottom, because it is $-\partial T/\partial q_k$, how the kinetic energy changes when you nudge coordinate $k$.
- $c_{ijk}$ and $c_{jik}$ multiply the same product, $\dot q_i\dot q_j = \dot q_j\dot q_i$. That pair is where the $2$ in the puck's $2mr\,\dot r\dot\varphi$ comes from.

## Trust it

A recipe with three moving indices is easy to get subtly wrong, so the last demo checks it two ways while you drag the system's state around.

{{ demo(name="concepts/christoffel-symbols/check", height=1090, caption="Drag the positions and velocities. Check 1 compares the recipe against a calculation with no indices; Check 2 confirms that M-dot minus 2C stays skew-symmetric.") }}

What to notice:

- **Check 1** computes $\dot M\dot q - \partial T/\partial q$ directly, by differentiating $M$ numerically, with no indices at all. It must equal $C\dot q$. This is the check that catches a slot mistake. Swapping two indices in the recipe makes it fail.
- **Check 2** tests something only the Christoffel choice of $C$ guarantees. Many matrices produce the same $C\dot q$, but this one also makes $\dot M - 2C$ skew-symmetric, and that property is what passivity-based robot controllers lean on. On its own it is a weaker test, because an index swap can leave it passing.
- Set both velocities to zero and both checks pass for *any* $C$, because every velocity product vanishes. The demo says so when you do it.

## What clicked

Two things made this stick for me. The first was understanding how the indices $i$, $j$, $k$, in the convention this post uses, map onto the $C$ matrix, with $k$ as the row and $j$ as the column. That way I always knew which cell I was trying to fill.

The second was the intermediate step of building the partial derivative matrix for each coordinate. It's a lot easier to find $\partial M_{12}/\partial q_1$, for example, when all the entries of $\partial M/\partial q_1$ are already sitting in front of you.

## Where this shows up

- Any serial robot arm or legged robot modelled with Lagrange's method has this $C$. With $n$ coordinates the cube is $n\times n\times n$, and the recipe does not change.
- The skew-symmetry of $\dot M - 2C$ is what passivity-based robust and adaptive robot controllers build on. [*Robot Modeling and Control*](https://faculty.cc.gatech.edu/~seth/SHV/) proves it in its dynamics chapter, notes that it holds only when $C$ is built with the Christoffel recipe, and uses it in its later control chapters.
