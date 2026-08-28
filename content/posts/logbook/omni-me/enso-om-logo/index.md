+++
title = "An enso for the app icon, generated rather than drawn"
slug = "enso-om-logo"
date = 2026-08-28
updated = 2026-08-28
draft = true

[taxonomies]
tags = ["branding", "design", "svg", "tauri"]
+++

## What does this feature do?

The app has a mark. It is an *enso* — the open, single-stroke circle of Zen brushwork — in
the interface's own accent blue on its own charcoal, with a small off-white dot at the
centre. The ring does not close, and that is the load-bearing half of the idea rather than
a stylistic tic: the gap is an admission that no application encompasses a whole life, and
the dot at the centre is the person the application is about.

It is a system rather than a picture. The ring alone is the app icon. The ring plus a
clean two-arch "m" is the compact wordmark — `om`, both the first two letters of the name
and a gateway. Both are drawn by the same function from shared parameters, so the
wordmark's ring is the icon's ring at fourteen twenty-sevenths scale rather than a second
drawing that happens to resemble the first.

There is no illustration file anywhere in this. The taper that makes the stroke look
brushed is faked with geometry — an outer circle and a slightly offset inner circle,
subtracted, with the opening cut at a chosen angle and a round cap dropped onto each of
the two brush terminals. All of it comes out of a fifty-five-line Python script. From there
the entire platform icon set is generated from a small manifest by the Tauri CLI:
thirty-three rasters plus a Mac icon bundle and a Windows `.ico`, spanning desktop,
Windows tiles, iOS and Android — including the two-layer adaptive icon Android insists on.

## Why was it added now?

An app you visit has a URL. An app you install has an icon, and for most of the day that
icon *is* the interface — it is what gets found in a grid of thirty other icons, at
forty-eight pixels, by someone not reading the labels. Until this, that slot held the
framework's default. A default icon is not neutral: it reads as unfinished, and it makes
the app genuinely harder to find, because it looks like every other thing on the device
nobody has got to yet.

The timing came from delivery rather than from taste. The app had just gained a wireless
update pipeline — signed builds arriving on the phone by themselves instead of being
rebuilt and side-loaded over a cable. That is the point at which an installed application
stops being a thing you are working on and becomes a thing that lives on a device between
sessions, and the placeholder stops being a placeholder somebody will get to.

## What's in scope (and what's not)?

In scope: the mark and its compact wordmark; the generator that draws both from shared
parameters; the manifest naming which SVG plays which role on which platform; the
regenerated cross-platform icon set, including Android's two-layer adaptive icon; and the
archived exploration — twenty-five candidates across three families, then a
weight-refinement round — kept in the repository rather than thrown away.

Not in scope:

- **This is a mark, not a brand system.** No type family, no palette beyond the two colours
  the interface already uses, no usage rules. The colours are the app's existing accent and
  background precisely so that the icon and the interface read as the same object.
- **The mark does not appear inside the app.** It is the platform icon and nothing else;
  the app's own header is still set type. Nothing in the interface renders the ring.
- **The generated set covers platforms the app does not ship on.** iOS app icons and
  Windows tile assets come out because the generator emits the whole set; only Linux
  desktop and Android are actually built. They are kept rather than pruned, since pruning
  would have to be redone on every regeneration.
- **The final choice was made by eye.** Three weights were rendered at the sizes that had
  failed, and one was picked by looking at them. There is no legibility metric behind it
  and none was sought.

## How do we know it works?

```bash
tmp=$(mktemp -d) && cp tauri-app/branding/generate-logo.py "$tmp/" && python3 "$tmp/generate-logo.py" \
  && diff "$tmp/icon-enso-a-light.svg" tauri-app/branding/omni-me-icon.svg && echo "icon: identical to the committed art" \
  && diff "$tmp/om-enso-a-light.svg"   tauri-app/branding/omni-me-om.svg   && echo "wordmark: identical to the committed art"
rm -rf "$tmp"
```

```output
wrote a-light
wrote b-medium
wrote c-bold
icon: identical to the committed art
wordmark: identical to the committed art
```

The committed artwork is byte-identical to what the script produces from scratch. That is
the property worth checking, because it is the one that decays silently: the moment
somebody nudges a path by hand in an editor, the SVG and the script stop agreeing, and the
generator quietly becomes a historical curiosity that nobody dares re-run. Here the script
is run into a throwaway directory so it cannot touch the repository, and both of its
outputs are diffed against the files actually shipped. `diff` printing nothing is the
result; the two `echo`s only run because it did.

Note also what the script emits in passing — three weights, not one. The committed mark is
the light variant, and its two siblings are regenerated every time, which is what makes
the choice revisitable rather than archaeological.

```bash
git ls-files tauri-app/src-tauri/icons | grep '\.png$' | xargs file -b \
  | sed -E 's/PNG image data, ([0-9]+) x ([0-9]+).*/\1x\2/' | sort -t x -k1 -n | uniq -c
```

```output
      1 20x20
      1 29x29
      1 30x30
      1 32x32
      3 40x40
      1 44x44
      1 50x50
      2 58x58
      1 60x60
      1 64x64
      1 71x71
      1 76x76
      2 80x80
      1 87x87
      1 89x89
      1 107x107
      2 120x120
      1 128x128
      1 142x142
      1 150x150
      1 152x152
      1 167x167
      1 180x180
      1 256x256
      1 284x284
      1 310x310
      1 512x512
      1 1024x1024
```

Thirty-three rasters at twenty-eight distinct sizes, from 20 pixels square up to 1024 —
every one of them rendered from the same SVG by the Tauri CLI reading a five-key manifest.
(Android's are generated separately, into the Android project's resource directories,
which is why they are not in this list.) Nothing here was resized by hand, and that is
what makes the small end trustworthy: a 20-pixel icon downsampled from a 1024-pixel PNG
would be mush, while one rasterised from vector source directly at 20 pixels is as sharp
as 20 pixels allows.

The distribution is also a fair argument for having worried about the small end in the
first place. Eight of the thirty-three are 44 pixels or under — the sizes that end up in a
task switcher, a title bar, a notification. The 1024 is a store listing nobody will ever
look at closely.

[`tauri-app/branding/generate-logo.py:22`](https://github.com/RustWright/omni-me/blob/76b61f26128359452c1005ce1c7707cf284b47a8/tauri-app/branding/generate-logo.py#L22) at `76b61f2`
> `def enso(cx, cy, R, ri, off, gapc, gaph):`
>
> The whole mark, as a function. Seven numbers in — the centre, the outer radius, the inner radius, how far the inner circle is nudged toward the opening, and where that opening sits and how wide it is — one crescent path out, plus a circle at each brush terminal to round the ends. The taper is not drawn; it is what falls out when a circle is subtracted by another circle sitting slightly off-centre.

[`tauri-app/branding/logo-manifest.json:5`](https://github.com/RustWright/omni-me/blob/76b61f26128359452c1005ce1c7707cf284b47a8/tauri-app/branding/logo-manifest.json#L5) at `76b61f2`
> `  "android_fg": "omni-me-fg.svg",`
>
> The line that keeps the halo off Android. An adaptive icon is two layers, and the platform's default background is white — supply only a mark and a dark logo arrives inside a bright ring. Naming a transparent-mark SVG here, alongside the solid-charcoal one on the line above, is the whole fix; the two files exist for no other purpose.

Reproducibility and coverage are checkable in a terminal. Whether the thing is any good is
not, so the rest of this is the mark itself.

Both halves of the identity, at a size where the brushwork is visible:


![Two charcoal rounded tiles side by side. On the left, the app icon: a blue enso — an open ring, thick at the bottom and tapering as it sweeps up to an opening at the top right, both ends rounded — around a small off-white dot at its centre. On the right, the om wordmark: the same ring rendered small as a letter o, its dot intact, followed by a two-arch lowercase m drawn in the same blue with rounded stroke ends.](./enso-system.png)

That is the mark at a size nobody sees it at. The size that decides whether it works is
somewhere between sixteen and forty-eight pixels, through a mask the launcher picks, and
the only honest way to show that is to let you shrink it yourself.

The ladder below renders the real geometry — the same path data as the files in the
repository — at seven sizes at once. **Round 2** is the concept as it was chosen;
**round 3** is the same idea after the taper was given a floor and the brush terminals were
capped. Switch between them and watch the small end of the ladder, then try the circular
mask, which is what an Android launcher will do to it whether or not the mark was designed
for it.

{{ demo(name="omni-me/enso-mark", height=510, wide=true, caption="The enso at 16 to 160 pixels. Round 2 versus round 3, three weights, and the three masks a launcher might apply.") }}

The failure is specific and it is visible at 32 pixels: round 2's stroke thins to nothing
where the ring opens, so the ring stops being a ring and becomes an arc with a dot beside
it. Round 3 holds its shape all the way down to 16, where it is no longer a brushstroke but
is still unmistakably the same object. Bold holds hardest and reads least like calligraphy,
which is the trade the three weights exist to make explicit.

Finally, the artefact that actually ships — the 128-pixel PNG the desktop bundle points at,
embedded here as the file itself rather than as a re-render:


![The shipped 128-pixel application icon: the blue enso and its off-white centre dot on a charcoal square, reproduced here at its native size.](./shipped-128.png)

## What's worth remembering or doing next?

- **A logo that is a function of numbers is a logo you can change your mind about.** The
  mark is fully determined by an outer radius, an inner radius, an offset and a gap
  half-angle. That turned "which weight?" from an argument into three files rendered side
  by side. The general form: when a design decision has a small parameter space,
  generating the whole space is cheaper than defending one point inside it.
- **The thing that nearly killed the design was a taper, and it had been named in
  advance.** The selection notes for this candidate listed its weakness as the brush
  character being lost entirely at thirty-two pixels — and it was, worse than the note
  predicted, because the stroke narrowed to nothing exactly where the ring opens, so at
  small sizes the ring broke into an arc. Two changes fixed it: put a floor under the thin
  end, and cap both brush terminals with a circle so the ends carry mass. Small-size
  legibility is mostly a minimum-stroke-width problem, and artwork reviewed only at full
  size will never surface it.
- **Android's adaptive icon has a default that quietly ruins a dark mark.** It composites a
  foreground layer over a background layer, and with no background supplied it fills white
  — so a charcoal-and-blue mark arrives ringed in a white halo. The fix is to supply both
  layers explicitly, which is the entire reason the branding directory holds a
  transparent-mark SVG and a solid-charcoal SVG whose only job is to be those two layers.
- **The rejected candidates were worth keeping.** Twenty-five explorations sit in the
  repository, each with a written note saying what it was reaching for and where it was
  likely to fail. That archive is what makes "why an enso" a comparison rather than an
  assertion — and in this case it also held the warning that became the next round's
  brief.
- **Deferred: the horizontal lockup.** The square mark and the compact two-letter wordmark
  exist; a full `omni·me` lockup for wide contexts does not. The trigger is the first place
  that needs a header instead of a square.
