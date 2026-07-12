+++
title = "How SVGs actually work"
slug = "how-svgs-work"
date = 2026-07-11
draft = false

[taxonomies]
tags = ["svg", "graphics", "vectors"]
+++

## Where the question started

A lot of my recent projects need visual elements designed: logos, icons, that
sort of thing, and most of them end up as SVGs. Since I lean heavily on Claude
Code, the usual loop is that I describe what I want, Claude makes the changes and
defines the images, and I come back with feedback and approval. That works fine.
But it left me only vaguely aware of what an SVG actually is. I knew they were
scalable and that they "defined a path," with no real idea how that high-level
description turned into something concrete.

I'm not looking to design SVGs by hand. That's not how I want to spend my time,
and Claude can handle the big changes. I just want to be familiar enough that a
small tweak doesn't intimidate me, so I can edit a file directly instead of
spinning up a whole Claude Code session for something tiny.

I really enjoyed making and playing with this one. Hope you do too.

## Try it: pixels versus instructions

Start with the promise hiding in the name. The **S** is for *scalable*. Below is
this site's logo twice, at the same size: on the left stored as **SVG**, on the
right stored the way a photo, PNG, or JPEG is, as a fixed grid of coloured
**pixels**. They start out identical. Drag the zoom.

{{ demo(name="concepts/how-svgs-work/scale", height=620, wide=true, caption="The same logo stored two ways, at the same size. Drag the zoom: the pixel copy breaks into blocks, while the SVG, redrawn from its instructions, stays sharp. Works best on a wider screen.") }}

The pixel copy was saved once, at a fixed resolution; enlarging it just makes its
pixels bigger, so you hit the blocks. The SVG stores **no pixels at all**, only
instructions, which the browser re-runs from scratch at whatever size it's shown.
That is the whole trick behind "scalable": there is nothing to stretch.

So what *are* those instructions? Unlike a PNG, an SVG is just **text**, a few
lines you can open in any editor and read. Here is the whole logo:

```svg
<svg viewBox="0 0 100 100" fill="currentColor">
  <path d="M50 6 C53 32 62 43 80 46 C62 49 53 60 50 70 C47 60 38 49 20 46 C38 43 47 32 50 6 Z"/>
  <rect x="28" y="81" width="44" height="8" rx="4"/>
</svg>
```

Two shapes. The `<rect>` is the flat bar under the mark, and it reads plainly
enough. It's a box that starts at (28, 81), runs 44 wide and 8 tall, with corners
rounded by 4.
The `<path>` is the four-pointed spark, and its whole shape is crammed into that
`d` string, the part that looks like line noise. Let's take it apart.

## Try it: read the path

The demo below is that exact `d`, unpacked. **Step through it** one command at a
time; the matching piece of the string lights up as you go. On the curve
commands, **drag the hollow control points** and watch the shape (and the
numbers) change.

{{ demo(name="concepts/how-svgs-work/path", height=620, wide=true, caption="The logo's own path, taken apart. Step through the commands; on the curves, drag the control points and watch the d string rewrite itself. Works best on a wider screen.") }}

Every command is a pen instruction on a 100×100 grid: `M` lifts the pen and
**m**oves it somewhere without drawing, `C` draws a **c**ubic curve that bends
toward two control points it never actually touches, and `Z` closes the loop back
to the start. That's it. The control points are the one genuinely clever idea.
They're magnets that shape a curve from a distance. Dragging them is the fastest way I
know to feel what they do. Nothing in that string is magic; it's a pen being told
where to go.

## Try it: build your own

Reading a path is one thing; writing one is where it clicks. The editor below
renders SVG live as you type. Three challenges climb from easy to hard (a
smiley, a boat, a heart), and the last one needs the very curves you just pulled
apart. There's a quick reference if the vocabulary slips, and an example solution
for each when you're done (or stuck; there's never just one right answer).

{{ demo(name="concepts/how-svgs-work/build", height=820, wide=true, caption="A live SVG editor. Pick a challenge, type shapes, watch them render. Reveal an example when you're done or stuck. Nothing leaves your browser. Works best on a wider screen.") }}

By the time you're drawing the heart, you're writing `C` commands by hand,
placing control points on purpose, which is exactly what you were dragging around
two demos ago.

## What clicked

Once you understand the syntax, any shape you could draw by hand on a Cartesian
plane, simple or moderately complex, can also be built as an SVG. Whether you
want to just comes down to time and patience.

Knowing how SVGs are put together also gives me a feel for their limits, so I can
better judge what's reasonable to ask Claude for when I'm working on graphics,
and what's outlandish.

## Where this shows up

Once you can read one SVG, you start seeing them everywhere on this very site.
The logo in the header, the icon in your browser tab, the little glyphs on the
theme toggle and the footer links. All of them are SVG, a few lines of the same
markup you were just editing. It's why they stay crisp on any screen and why the
logo quietly recolours itself in dark mode: that `fill="currentColor"` in the
snippet above means *"paint me whatever the surrounding text colour is,"* so when
the page turns dark, so does the mark. None of that is a special export setting.
It's just text, and now it's text you can read.
