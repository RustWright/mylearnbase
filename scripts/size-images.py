#!/usr/bin/env python3
"""Give every local <img> in the built site its intrinsic width and height.

Zola renders a Markdown image, ![alt](src), as a bare <img> with no dimensions,
and has no setting to add them (its only Markdown image option is
lazy_async_image). Without them the browser cannot reserve the image's box
before it loads, so on a slow connection the text below jumps down when it
arrives: layout shift. The attributes fix that because the theme pairs them
with `.prose img { max-width: 100%; height: auto }`, which scales the box
proportionally; images outside .prose are already sized by their own CSS, so
for them the attributes are inert.

Done HERE, on the built HTML, rather than per post (a figure() shortcode),
because `logbook publish` regenerates Markdown image references and would undo
a per-post fix on every republish. This way plain Markdown stays the authoring
format and every future post is covered for free.

Dimensions come from the file headers (PNG, GIF, WebP, JPEG, SVG), no image
library, so it runs on the deploy image. An <img> that already has BOTH
attributes is left alone; one with only a width (the demo-gallery posters)
gets the height that keeps the file's aspect ratio.

FAILS THE BUILD if any local image cannot be sized afterwards: a missing file
is a broken image, and an unreadable format means this script needs teaching.

  Usage:  python3 scripts/size-images.py public [BASE_URL]
          BASE_URL defaults to zola.toml's; pass it when the site was built with
          `zola build --base-url …`, or absolute image URLs on that host read as
          another site's and are skipped.
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
# Minified output may drop attribute quotes, so accept quoted and bare values.
ATTR_RE = lambda name: re.compile(r"\s" + name + r"""\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.I)
SRC_RE, W_RE, H_RE = ATTR_RE("src"), ATTR_RE("width"), ATTR_RE("height")


def base_url() -> str:
    m = re.search(r'^base_url\s*=\s*"([^"]+)"', (ROOT / "zola.toml").read_text(encoding="utf-8"), re.M)
    return m.group(1).rstrip("/") if m else ""


def _svg_len(v: str | None) -> float | None:
    if not v:
        return None
    m = re.fullmatch(r"\s*([\d.]+)\s*(px)?\s*", v)   # a % or em size is not intrinsic
    return float(m.group(1)) if m else None


def dimensions(p: Path) -> tuple[int, int] | None:
    b = p.read_bytes()[:65536]
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", b[6:10])
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            n = int.from_bytes(b[21:25], "little")
            return (n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1
        if kind == b"VP8X":
            return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
        return None
    if b[:2] == b"\xff\xd8":                                     # JPEG: walk to a SOF marker
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1; continue
            marker, size = b[i + 1], struct.unpack(">H", b[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + size
        return None
    text = b.decode("utf-8", "ignore")
    root = re.search(r"<svg\b[^>]*>", text, re.I)
    if root:
        tag = root.group(0)
        get = lambda a: (re.search(r"\s" + a + r'\s*=\s*["\']([^"\']*)["\']', tag) or [None, None])[1]
        w, h = _svg_len(get("width")), _svg_len(get("height"))
        if w and h:
            return round(w), round(h)
        vb = get("viewBox")
        if vb:
            parts = [float(x) for x in re.split(r"[\s,]+", vb.strip())]
            if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
                return round(parts[2]), round(parts[3])
    return None


def resolve(src: str, page: Path, public: Path, base: str) -> Path | None:
    """The file an <img src> points at inside public/, or None if it is external."""
    if src.startswith("data:"):
        return None
    if base and src.startswith(base + "/"):
        return public / unquote(urlsplit(src[len(base):]).path).lstrip("/")
    parts = urlsplit(src)
    if parts.scheme or parts.netloc:
        return None                                              # another host: not ours to size
    path = unquote(parts.path)
    return public / path.lstrip("/") if path.startswith("/") else page.parent / path


def main() -> int:
    public = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
    base = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else base_url()
    added = complete = 0
    problems: list[str] = []
    for page in sorted(public.rglob("*.html")):
        if "pagefind" in page.relative_to(public).parts:
            continue
        html = page.read_text(encoding="utf-8")
        rel = page.relative_to(public)

        def fix(m: re.Match) -> str:
            nonlocal added, complete
            tag = m.group(0)
            has_w, has_h = W_RE.search(tag), H_RE.search(tag)
            if has_w and has_h:
                complete += 1
                return tag
            src_m = SRC_RE.search(tag)
            src = src_m.group(1).strip("\"'") if src_m else ""
            f = resolve(src, page, public, base) if src else None
            if f is None:
                return tag                                       # external or data: URI
            if not f.is_file():
                problems.append(f"{rel}: image not found: {src}")
                return tag
            d = dimensions(f)
            if not d or not all(d):
                problems.append(f"{rel}: could not read dimensions of {src}")
                return tag
            w, h = d
            if has_w:                                            # keep the given width, match its height
                given = int(re.sub(r"\D", "", has_w.group(1)) or 0)
                attrs = f" height={round(given * h / w)}" if given else f" height={h}"
            else:
                attrs = f" width={w} height={h}"
            added += 1
            end = "/>" if tag.endswith("/>") else ">"
            return tag[: -len(end)].rstrip() + attrs + end

        new = IMG_RE.sub(fix, html)
        if new != html:
            page.write_text(new, encoding="utf-8")

    print(f"Image sizing: {added} tag(s) given dimensions, {complete} already complete.")
    if problems:
        print("error: some local images could not be sized:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
