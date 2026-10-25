+++
title = "Getting back up to speed for control theory"
description = "The playlists and courses I used to rebuild the linear algebra, calculus and control theory a grad course in adaptive control assumed I still had."
slug = "control-theory-refresher"
date = 2026-10-16
updated = 2026-10-25
draft = false

[taxonomies]
tags = ["control-systems", "adaptive-control", "linear-algebra", "differential-equations", "matlab"]
+++

> The playlists and courses I used to rebuild the math, control theory and MATLAB
> a grad course in adaptive control assumed I still had. ✓ worked through;
> ? saved, not yet watched.

I went back to grad school after more than four years out of school, and one of
the courses I took in my first term at Waterloo was ME 641 (sometimes listed as
ME 780 Topic 10) on adaptive control.

The first couple of weeks were a rude awakening. I had forgotten a lot of the
basics I needed to understand modern control theory, so this post lists the
resources I used to get back up to speed, and the ones I'd likely turn to again
if I needed to relearn these concepts.

You'll notice most of the resources below are YouTube playlists. That's my
preferred medium when I need to learn something quickly, since I tend to process
a concept faster than when I'm reading a textbook.

The resources are listed in an order you can follow, though when I actually used
them I tended to interleave them. I'm still early in my degree as of writing this,
so I expect to keep adding to this list as I discover and use more.

I'm now putting this to work on a [reaction-wheel pendulum](@/posts/logbook/reaction-wheel/pendulum-model/index.md).

## Math

- ✓ **[Essence of linear algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab)**
  by 3Blue1Brown. Starting off with the basics. 3Blue1Brown has a way of building
  physical intuition, so I used three of his playlists to refresh my math
  foundation.
- ✓ **[Essence of calculus](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr)**
  by 3Blue1Brown. Same idea as Essence of linear algebra, rebuilding the
  foundation and intuition for material I had already learned in undergrad.
- ✓ **[Differential equations](https://www.youtube.com/playlist?list=PLZHQObOWTQDNPOjrT6KVlfJuKtYTftqH6)**
  by 3Blue1Brown. To finish things off, since most dynamical systems in controls
  can be expressed as differential equations.
- ? **[Engineering Math: Vector Calculus and Partial Differential Equations](https://www.youtube.com/playlist?list=PLMrJAkhIeNNQromC4WswpU1krLOq5Ro6S)**
  by Steve Brunton. I haven't watched this one yet. I use his Control Bootcamp
  below, so at some point I'll likely check out his engineering math course to
  supplement my 3Blue1Brown adventure.

## Control theory

- ✓ **[Control Bootcamp](https://www.youtube.com/playlist?list=PLMrJAkhIeNNR20Mz-VpzgfQs5zrYi085m)**
  by Steve Brunton. I found this series when I was struggling to get a physical
  intuition to balance out all the control-law proofs in my course, and Steve has
  a way of explaining things that made them click a lot quicker.
- ✓ **[Classical Control Theory](https://www.youtube.com/playlist?list=PLUMWjy5jgHK1NC52DXXrriwihVrYZKqjk)**
  by Brian Douglas. I actually watched these before Steve's videos, so if you
  struggle to follow his, try these first. They follow the more typical format I
  expected from my undergrad control courses, and Brian is really good at drawing
  cartoons, so they may be a better starting point if you're really, really
  rusty. He also has a lot of MATLAB Tech Talk videos that are more recent than
  this playlist, but I haven't found a playlist that organizes them as nicely
  yet, which is why they aren't here.

## Simulation and analysis

- ✓ **[MATLAB Onramp](https://matlabacademy.mathworks.com/en/details/matlab-onramp/gettingstarted)**
  by MathWorks. I needed to get familiar with MATLAB quickly for my course, so it
  made the most sense to learn from the company that makes the software. My
  student account gave me free access, so cost wasn't a concern.
- ✓ **[Simulink Onramp](https://matlabacademy.mathworks.com/details/simulink-onramp/simulink)**
  by MathWorks. Like MATLAB Onramp, I worked through this in less than a day to
  refamiliarise myself with the Simulink interface and how to build models and
  run simulations.
