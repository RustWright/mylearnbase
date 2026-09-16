#!/usr/bin/env python3
"""Render the link-preview card (static/img/og-default.png) from the site itself.

The card shows the logo, the site title, the homepage tagline and the site's
host. It used to be a one-off PNG with no source, so when the tagline changed the
card kept the old one on every shared link and nothing noticed. Now the text is
read from where the site keeps it:

  title    zola.toml            title
  host     zola.toml            [extra] canonical_url
  tagline  content/_index.md    [extra] bio
  logo     static/img/logo.svg

STAYING IN SYNC: the filled-in HTML is hashed into static/img/.og-card-hash.
That document is exactly what gets rendered, so the hash changes whenever the
template, the tagline, the title, the host or the logo does. build.sh runs this
script with --check and warns when the committed card is stale.

WHY LOCAL, like the résumé PDF: Cloudflare's build image is not guaranteed to
carry a browser, and the card changes a few times a year. The PNG is committed.

  Usage:  python3 scripts/build-og-card.py           # render the card
          python3 scripts/build-og-card.py --check   # warn if it is stale
"""
from __future__ import annotations

import hashlib
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "scripts" / "og-card.html"
OUT = ROOT / "static" / "img" / "og-default.png"
HASH_FILE = ROOT / "static" / "img" / ".og-card-hash"
FONT = "DejaVu Sans"


def _read(pattern: str, path: Path, what: str) -> str:
    m = re.search(pattern, path.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"error: could not find {what} in {path.relative_to(ROOT)}")
    return m.group(1)


def filled_card() -> str:
    title = _read(r'^title\s*=\s*"([^"]+)"', ROOT / "zola.toml", "title")
    canonical = _read(r'^canonical_url\s*=\s*"([^"]+)"', ROOT / "zola.toml", "extra.canonical_url")
    tagline = _read(r'^bio\s*=\s*"([^"]+)"', ROOT / "content" / "_index.md", "extra.bio (the tagline)")
    logo = (ROOT / "static" / "img" / "logo.svg").read_text(encoding="utf-8").strip()
    host = re.sub(r"^https?://", "", canonical).rstrip("/")

    doc = TEMPLATE.read_text(encoding="utf-8")
    slots = {"{{LOGO}}": logo, "{{TITLE}}": html.escape(title), "{{TAGLINE}}": html.escape(tagline), "{{HOST}}": html.escape(host)}
    for slot, value in slots.items():
        if doc.count(slot) != 1:
            sys.exit(f"error: {TEMPLATE.relative_to(ROOT)} must contain {slot} exactly once")
        doc = doc.replace(slot, value)
    return doc


def digest(doc: str) -> str:
    return hashlib.sha256(doc.encode("utf-8")).hexdigest()


def check() -> int:
    current = digest(filled_card())
    if not HASH_FILE.exists():
        print(f"WARNING: no {HASH_FILE.relative_to(ROOT)}; the link-preview card has never been rendered from source.")
    elif HASH_FILE.read_text().strip() != current:
        print("WARNING: the link-preview card is stale. Its title, tagline, host, logo or template changed.")
        print("         Fix with: python3 scripts/build-og-card.py && git add static/img/")
    return 0  # warn, never fail: a stale preview image is not worth a blocked deploy


def render() -> int:
    chrome = next((c for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if shutil.which(c)), None)
    if not chrome:
        sys.exit("error: no Chrome/Chromium on PATH; it is needed to render the card.")
    matched = subprocess.run(["fc-match", "-f", "%{family}", FONT], capture_output=True, text=True).stdout
    if FONT not in matched:
        sys.exit(f"error: font {FONT!r} is not installed (fc-match gave {matched!r}); the card would render in a fallback typeface.")

    doc = filled_card()
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        shot = Path(tmp) / "card.png"
        page.write_text(doc, encoding="utf-8")
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
             "--window-size=1200,630", f"--screenshot={shot}", page.as_uri()],
            capture_output=True, check=True,
        )
        if not shot.exists():
            sys.exit("error: Chrome exited without writing a screenshot.")
        shutil.copyfile(shot, OUT)
    HASH_FILE.write_text(digest(doc) + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)} and {HASH_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv[1:] else render())
