+++
title = "Building a Python Image Generation CLI with Google Imagen 4"
slug = "python-image-generation-cli-google-imagen"
date = 2026-02-18
draft = false

[taxonomies]
tags = ["python", "ai", "image-generation", "google-ai"]
# series = ["Series Name"]       # Uncomment if part of a series

# [extra]
# series_order = N               # Uncomment if part of a series
+++

## Reflections

A couple of things stand out from this project.

The first is the choice to use Python for scripting. I have been a bit stubborn about reaching for Rust for everything — [man with a hammer syndrome](https://en.wikipedia.org/wiki/Law_of_the_instrument), probably. I learned Rust, and I still feel that what the language is trying to achieve is genuinely cool. That said, rapidly prototyping an idea in Python is night and day different from doing the same thing in Rust.

The gap feels even wider when you add LLM-assisted development into the mix. There is far more Python in a model's training data than Rust, and the difference shows. The ease with which Claude was able to generate and troubleshoot these scripts was noticeably sharper than my experience working through Rust projects of comparable complexity.

Personally, I enjoy debugging. Not sure if that is a hot take, but I like working out where my mental model of a problem diverges from what I actually expressed in code — there is a dopamine hit when you find that gap and close it. So I am probably more willing than most to sit with a stubborn error for hours. For a business trying to minimize that time, though, the Python advantage is hard to ignore. That said, I still think Rust's safety guarantees — when the code is written well — provide enough value that it will remain my go-to for serious long-term projects.

Based on all that, my approach going forward will be: prototype fast in Python first, and if something proves out enough to justify the effort, translate it to Rust.

That said — I have glossed over why I built this in the first place. I was trying to edit a YouTube video for my mom. I am not a great video editor, but I have been using image generation to reduce how many images I need to pull from the internet (and deal with copyright, attribution, etc.) when making visuals. My previous workflow was clunky — a very disorganized Google Colab notebook — and I finally replaced it here after one of the APIs I relied on got discontinued.

If you want to see videos that may or may not contain images from this tool, check them out on YouTube at [Urhobo Made Easy](http://www.youtube.com/@EasyUrhobo). Otherwise, enjoy the tutorial.

---

## Tutorial: Building a Python Image Generation CLI with Google Imagen 4 and Speech Bubble Overlays

This tutorial walks through building a two-part Python toolchain using Claude Code as the primary development agent. The full source is on GitHub: [github.com/RustWright/img_gen](https://github.com/RustWright/img_gen).

1. `main.py` — a CLI for generating images via Google's Imagen 4 and Gemini APIs
2. `overlay.py` + `apply_bubbles.py` — a compositor that overlays speech bubbles with Unicode text onto generated images

The specific use case was producing visuals for a YouTube video about Urhobo (a Nigerian ethnic group) greetings, where each scene needed correct Urhobo text — including diacritics like `ọ`, `ẹ`, `ọ` — rendered as speech bubbles. Baking that text into the image generation prompt would have been unreliable; compositing it in afterward gave full typographic control.

### What You'll End Up With

- A `uv`-managed Python project with a two-backend image generation CLI (Imagen 4 and Gemini)
- Support for five model tiers, four aspect ratios, and batch generation
- A local Lanczos upscaler (free; no API call)
- A Pillow-based speech bubble compositor that correctly renders Unicode diacritics
- A batch script to apply per-scene bubbles to a set of images

### Assumptions

- **Operating system:** Linux (Ubuntu 22.04+) — this is what the tutorial was built and tested on
- **Python:** 3.12 (managed via `uv`)
- **API key:** Google AI Studio key (free tier available at [aistudio.google.com](https://aistudio.google.com/apikey))

**macOS users:** Everything works as-is. Install `uv` with the same `curl` command. The one difference is the DejaVu Sans font used by the speech bubble overlay — it may not be present by default. Install it with `brew install --cask font-dejavu` (requires Homebrew), or point `overlay.py` at any system font that supports your target characters.

**Windows users:** Install `uv` via PowerShell (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`) instead of the `curl` command. `pathlib.Path` handles path separators automatically so the scripts are otherwise compatible. For the DejaVu font, download it from [dejavu-fonts.github.io](https://dejavu-fonts.github.io) and install it, or update the font path in `overlay.py` to point to a local TTF file explicitly.

---

### Step 1: Pick an Image Generation API

Before writing any code, it is worth knowing which API to target. A survey of the options ranked by quality, cost, and ergonomics produces roughly this ordering:

| Rank | API | Cost/image | Notes |
|------|-----|-----------|-------|
| 1 | **Google Imagen 4** | $0.02–$0.06 | Best quality/cost ratio, simple SDK, fast |
| 2 | OpenAI GPT-Image-1 | ~$0.04–$0.19 | Highest raw quality, stricter content policy |
| 3 | FLUX 2 (fal.ai / self-host) | $0.02–$0.05 | Strong quality, self-hosting option |
| 4+ | Stability AI, Ideogram, etc. | Varies | Solid alternatives, more niche |

**Google Imagen 4 wins** for this project:

- Cleanest SDK (`google-genai`)
- Simple API key auth (no service account ceremony)
- Three model tiers covering draft-to-production quality
- The same key unlocks Gemini models, which can return interleaved text reasoning alongside images

One important auth decision up front: the `google-genai` SDK supports two auth paths — a simple **Gemini API key** (from AI Studio) and the more involved **Vertex AI** credentials. This project uses the API key path because it is frictionless. The tradeoff: the `allow_all` person generation policy and the `imagen-4.0-upscale-preview` API are Vertex AI-only. Everything else works fine on the API key path.

---

### Step 2: Project Setup with `uv`

`uv` is a modern Python package manager that handles virtual environments, dependency locking, and script running in one tool. Install it if you do not have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Initialize the project:

```bash
mkdir img_gen && cd img_gen
uv init --python 3.12
```

Add the three dependencies:

```bash
uv add google-genai Pillow python-dotenv
```

Create a `.env` file for your API key:

```bash
# .env
GEMINI_API_KEY=your_key_here
```

Get a key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — the free tier is sufficient for development.

Add a `.gitignore` so the key never ends up in version control:

```
.env
output/
__pycache__/
.python-version
```

---

### Step 3: The Image Generation CLI ([`main.py`](https://github.com/RustWright/img_gen/blob/master/main.py))

#### Model registry

The script defines two groups of models with their API identifiers and estimated per-image costs:

```python
IMAGEN_MODELS = {
    "imagen-fast":  ("imagen-4.0-fast-generate-001",  0.02),
    "imagen":       ("imagen-4.0-generate-001",        0.04),
    "imagen-ultra": ("imagen-4.0-ultra-generate-001",  0.06),
}

GEMINI_MODELS = {
    "gemini":     ("gemini-2.5-flash-image", 0.035),
    "gemini-pro": ("gemini-3-pro-image-preview", 0.07),
}

ALL_MODELS = {**IMAGEN_MODELS, **GEMINI_MODELS}
```

The API does not return billing metadata, so cost is calculated locally from these fixed rates.

#### Two different API backends

Imagen and Gemini use distinct SDK methods with different response shapes.

**Imagen — `generate_images()`:**

```python
def generate_imagen(client, prompt, model="imagen", count=1,
                    aspect_ratio="1:1", person_generation="allow_adult"):
    model_id, _ = IMAGEN_MODELS[model]
    response = client.models.generate_images(
        model=model_id,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=count,
            aspect_ratio=aspect_ratio,
            person_generation=person_generation,
        ),
    )
    images = []
    if response.generated_images:
        for gen_img in response.generated_images:
            images.append(gen_img.image._pil_image)
    return images
```

**Gotcha:** `generate_images()` returns `GeneratedImage` objects, not PIL Images. You must access the private `._pil_image` attribute to get a usable image object. This is not documented prominently.

**Gemini — `generate_content()`:**

```python
def generate_gemini(client, prompt, model="gemini", aspect_ratio="1:1"):
    model_id, _ = GEMINI_MODELS[model]
    response = client.models.generate_content(
        model=model_id,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )
    images = []
    text_parts = []
    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_parts.append(part.text)
            elif part.inline_data is not None:
                img = Image.open(BytesIO(part.inline_data.data))
                images.append(img)
    text = "\n".join(text_parts) if text_parts else None
    return images, text
```

The Gemini path can return interleaved text reasoning alongside the image — useful for understanding how the model interpreted a complex prompt. The image data comes back as raw bytes in `part.inline_data.data`; wrapping in `BytesIO` and passing to `Image.open()` converts it to a PIL Image.

#### Saving images

Images are saved to an `output/` directory with timestamped, prompt-derived filenames:

```python
def save_images(images, prompt):
    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt[:40]).strip()
    slug = slug.replace(" ", "_")
    saved = []
    for i, img in enumerate(images):
        suffix = f"_{i+1}" if len(images) > 1 else ""
        filename = OUTPUT_DIR / f"{ts}_{slug}{suffix}.png"
        img.save(filename)
        saved.append(filename)
        print(f"  [{i+1}] {filename} ({img.width}x{img.height})")
    return saved
```

#### Local upscaling

The actual Google upscaling API (`imagen-4.0-upscale-preview`) requires Vertex AI credentials. For API key users, a free local alternative using Pillow's Lanczos resampler is provided instead:

```python
def upscale_local(input_path, scale):
    img = Image.open(input_path)
    new_size = (img.width * scale, img.height * scale)
    upscaled = img.resize(new_size, Image.LANCZOS)
    out_path = input_path.parent / f"{input_path.stem}_upscaled_{scale}x.png"
    upscaled.save(out_path)
    return out_path
```

This is not AI upscaling, but Lanczos is a quality resampling algorithm that works well for clean photorealistic outputs. Supported scales: 2x, 3x, 4x.

#### Argparse with an implicit default subcommand

The CLI has two subcommands — `generate` (default) and `upscale` — but should feel natural to invoke without typing `generate` explicitly:

```bash
uv run main.py "a cat astronaut floating in space"       # should just work
uv run main.py -n 4 "neon jellyfish"                    # no subcommand, has flags
uv run main.py upscale output/image.png --scale 2       # explicit subcommand
```

**Gotcha:** You cannot detect a missing subcommand by checking `args.command is None` after `parse_args()`. If the user runs `main.py -n 2 "prompt"`, argparse sees `-n 2` as flags and `"prompt"` as a positional — but with no subcommand defined, it may error or mis-parse.

**Solution:** Inspect `sys.argv[1:]` directly before parsing, and prepend `"generate"` if the first argument is not a known subcommand or `--help`:

```python
subcommands = {"generate", "gen", "upscale"}
argv = sys.argv[1:]
if argv and argv[0] not in subcommands and argv[0] not in ("-h", "--help"):
    argv = ["generate"] + argv
args = parser.parse_args(argv)
```

This approach is robust because it handles both `"prompt"` as the first argument and flag-first invocations like `-n 4 "prompt"`.

#### Putting it all together — usage examples

```bash
# Default model (imagen, ~$0.04)
uv run main.py "a cat astronaut floating in space"

# Fast draft — 4 images, 16:9
uv run main.py -m imagen-fast -n 4 -a 16:9 "neon jellyfish underwater"

# Gemini — returns text reasoning alongside image
uv run main.py -m gemini "watercolor mountain village at dawn"

# Upscale a favourite result
uv run main.py upscale output/20260218_cat_astronaut.png --scale 2
```

Cost is printed after every run:

```
Generated 2 image(s):
  [1] output/20260218_210001_neon_jellyfish_1.png (1024x1024)
  [2] output/20260218_210001_neon_jellyfish_2.png (1024x1024)

  Cost: 2 image(s) x $0.020 = $0.040
```

---

### Step 4: The Speech Bubble Compositor ([`overlay.py`](https://github.com/RustWright/img_gen/blob/master/overlay.py))

#### Why composite instead of prompting for text?

When the use case involves non-Latin text with special diacritics — like Urhobo's `ọ`, `ẹ`, `Vrẹndo`, `migwọ` — asking the image generation model to render that text in the scene is unreliable. AI image models struggle with precise Unicode diacritics and tend to hallucinate or drop them.

The cleaner approach: generate scenes without any text, then composite speech bubbles using a real font renderer. This keeps the two concerns cleanly separated and gives complete typographic control.

#### Font selection

The script uses DejaVu Sans Bold, which ships with most Linux systems and correctly renders Urhobo diacritics out of the box:

```python
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
```

To verify font coverage on your system, you can use `fc-list` to find candidate fonts and then test diacritic rendering with Pillow:

```bash
fc-list | grep -i "dejavu"
```

In Python, a quick check:

```python
from PIL import ImageFont, ImageDraw, Image

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
img = Image.new("RGB", (400, 100), "white")
draw = ImageDraw.Draw(img)
draw.text((10, 10), "migwọ — Vrẹndo", font=font, fill="black")
img.save("test_diacritics.png")
```

If the saved image shows the characters correctly, the font is suitable.

#### Dynamic font sizing

Bubbles should fill as much width as possible without overflowing their allocated half of the image. The `fit_font_size` function steps down from a maximum size until the text fits within `max_width`:

```python
def fit_font_size(text, max_width, max_size=42, min_size=22):
    for size in range(max_size, min_size - 1, -2):
        font = get_font(size)
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        if text_w + BUBBLE_PADDING * 2 <= max_width:
            return font
    return get_font(min_size)
```

#### Drawing a bubble

Each bubble is a rounded rectangle with a small triangular tail pointing downward toward the speaker's position. The drawing is done on a transparent RGBA overlay that is alpha-composited onto the base image:

```python
def draw_bubble(draw, text, font, center_x, bottom_y, tail_side="left",
                img_width=1024, img_height=1024):
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    bw = text_w + BUBBLE_PADDING * 2
    bh = text_h + BUBBLE_PADDING * 2

    bx0 = center_x - bw // 2
    by0 = bottom_y - bh - TAIL_SIZE
    bx1 = bx0 + bw
    by1 = by0 + bh

    # Clamp to image bounds
    if bx0 < MARGIN:
        shift = MARGIN - bx0; bx0 += shift; bx1 += shift
    if bx1 > img_width - MARGIN:
        shift = bx1 - (img_width - MARGIN); bx0 -= shift; bx1 -= shift
    if by0 < MARGIN:
        shift = MARGIN - by0; by0 += shift; by1 += shift

    draw.rounded_rectangle((bx0, by0, bx1, by1), radius=18,
                            fill=(255, 255, 255, 230),
                            outline=(60, 60, 60, 255), width=2)

    tail_x = max(bx0 + 20, min(center_x, bx1 - 20))
    draw.polygon([(tail_x - 8, by1), (tail_x + 8, by1), (tail_x, by1 + TAIL_SIZE)],
                 fill=(255, 255, 255, 230), outline=(60, 60, 60, 255), width=1)
    draw.line([(tail_x - 7, by1), (tail_x + 7, by1)],
              fill=(255, 255, 255, 230), width=3)

    draw.text((bx0 + BUBBLE_PADDING, by0 + BUBBLE_PADDING - bbox[1]),
              text, fill=(30, 30, 30, 255), font=font)
```

The `draw.line` after the polygon tail is a cleanup step: it paints over the outline segment where the tail joins the bubble body, preventing a visible double-line artifact.

The alpha-composite step at the end merges the bubble overlay onto the base image cleanly:

```python
result = Image.alpha_composite(img, overlay).convert("RGB")
result.save(output_path)
```

#### Positioning bubbles

The `overlay_bubbles` function accepts optional `pos_left` and `pos_right` arguments as `(x_fraction, y_fraction)` tuples, where `(0, 0)` is top-left and `(1, 1)` is bottom-right. The tail of each bubble points to this position. When positions are omitted, sensible defaults place bubbles at the lower-left and lower-right quarters of the image.

```bash
# Single bubble
uv run overlay.py input.png output.png --left "migwọ"

# Two bubbles
uv run overlay.py input.png output.png --left "migwọ" --right "Vrẹndo"
```

---

### Step 5: The Batch Script ([`apply_bubbles.py`](https://github.com/RustWright/img_gen/blob/master/apply_bubbles.py))

With 16 greeting scenes to process, a batch script is more practical than running `overlay.py` sixteen times manually. Scene definitions live in a separate `scenes.toml` file rather than being baked into the script — this keeps the code stable while the data (image filenames, bubble text, positions) stays easy to edit without touching Python.

#### The scene file (`scenes.toml`)

Each `[[scenes]]` block defines one image. Omit any optional field to skip that bubble:

```toml
[[scenes]]
# Single bubble — greeting only
input = "20260218_migwo_morning.png"
output = "01_migwo_morning.png"
left = "migwọ"
pos_left = [0.30, 0.25]

[[scenes]]
# Two bubbles — greeting and response
input = "20260218_migwo_vrendo.png"
output = "05_migwo_vrendo.png"
left = "migwọ"
right = "Vrẹndo"
pos_left = [0.28, 0.25]
pos_right = [0.85, 0.20]
```

`scenes.toml` is gitignored since it references locally generated image filenames. A [`scenes.example.toml`](https://github.com/RustWright/img_gen/blob/master/scenes.example.toml) is committed to the repo as a template with full field documentation.

#### The script

`apply_bubbles.py` reads the TOML file using Python's stdlib `tomllib` (available from 3.11+), then runs each scene through `overlay_bubbles`:

```python
import sys
import tomllib
from pathlib import Path
from overlay import overlay_bubbles

OUTPUT_DIR = Path("output")
FINAL_DIR = Path("output/final")

def load_scenes(path):
    with open(path, "rb") as f:
        return tomllib.load(f).get("scenes", [])

def main():
    scenes_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("scenes.toml")
    scenes = load_scenes(scenes_file)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    for scene in scenes:
        input_path = OUTPUT_DIR / scene["input"]
        output_path = FINAL_DIR / scene["output"]
        if not input_path.exists():
            print(f"  SKIP (not found): {scene['input']}")
            continue
        pos_left = tuple(scene["pos_left"]) if "pos_left" in scene else None
        pos_right = tuple(scene["pos_right"]) if "pos_right" in scene else None
        overlay_bubbles(input_path, output_path,
                        left_text=scene.get("left"), right_text=scene.get("right"),
                        pos_left=pos_left, pos_right=pos_right)
        print(f"  OK: {scene['output']}")
        ok += 1

    print(f"\nDone! {ok}/{len(scenes)} images processed, saved to {FINAL_DIR}/")
```

Positions were tuned per image by examining each generated scene and estimating where each speaker appears in the frame. The fractional coordinate system — rather than raw pixels — makes them resolution-independent.

Run it:

```bash
uv run apply_bubbles.py              # uses scenes.toml
uv run apply_bubbles.py custom.toml  # uses a different file
```

Output lands in `output/final/` as numbered PNG files, ready for import into a video editor.

---

### Full Project Structure

Full source: [github.com/RustWright/img_gen](https://github.com/RustWright/img_gen)

```
img_gen/
├── .env                    # GEMINI_API_KEY (not committed)
├── .gitignore
├── pyproject.toml          # uv project config
├── uv.lock
├── main.py                 # Image generation CLI
├── overlay.py              # Speech bubble compositor
├── apply_bubbles.py        # Batch scene processor
├── scenes.example.toml     # Scene config template (committed)
├── scenes.toml             # Your actual scene data (gitignored)
└── output/
    ├── *.png               # Raw generated images
    └── final/
        └── *.png           # Final composited images
```

---

### Key Gotchas Summary

**`generate_images()` returns its own type, not PIL.**
Access `gen_img.image._pil_image` to get a usable PIL Image. The public API surface does not expose this directly — you have to reach into the internal attribute.

**`generate_content()` gives you raw bytes.**
For the Gemini image path, `part.inline_data.data` is bytes. Wrap in `BytesIO` before passing to `Image.open()`.

**`allow_all` person generation is Vertex AI only.**
On the Gemini API key path, `allow_adult` is the highest setting available. If you need unrestricted person generation, you need Vertex AI credentials.

**The Google upscale API is also Vertex AI only.**
`imagen-4.0-upscale-preview` does not work with an API key. The local Lanczos fallback covers most use cases without an API call.

**Do not bake Unicode diacritics into image prompts.**
Urhobo text like `migwọ` or `Vrẹndo` will not render reliably from an image generation prompt. Generate clean scenes, then overlay text as a post-processing step using a proper font renderer.

**Argparse subcommand detection requires `sys.argv` inspection.**
You cannot reliably detect "no subcommand given" by checking `args.command` after parsing, because flags like `-n 2` may confuse the parser when no positional subcommand is present. Inspect `sys.argv[1:]` before calling `parse_args()` and prepend `"generate"` if needed.

---

### Version Reference

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Runtime |
| uv | 0.5+ | Package management |
| google-genai | latest | Gemini/Imagen API client |
| Pillow | latest | Image I/O and compositing |
| python-dotenv | latest | `.env` loading |
| DejaVu Sans Bold | system | Unicode-capable font for overlays |
