#!/usr/bin/env python3
"""Capture gallery posters for the heavy demos.

A demo above the size threshold is never previewed live in the Playground — it
would cost a visitor ~600KB on scroll — so it shows a still with a play button
over it instead. This captures those stills.

WHICH DEMOS: this script does not decide. It reads the `heavy` flag that
build-demo-index.py derives from measured byte weight, so the rule lives in one
place and adding a demo never means making a per-demo judgment call. Add a demo,
run the build, run this: whatever came out heavy and lacks a current poster gets
captured.

STAYING IN SYNC: posters are content-addressed — the filename carries a hash of
the demo bundle that produced it (see poster_name() in build-demo-index.py). A
poster is therefore only ever found when it matches the bytes currently on disk.
Edit a demo and the expected filename stops existing, the gallery falls back to
the drawn card, and the build reports that a poster needs recapturing. A stale
screenshot cannot be displayed, which is why there is no "is it still accurate?"
check anywhere: the question cannot arise.

WHY LOCAL, like the résumé PDF: Cloudflare's build image is not guaranteed to
carry a browser, and these demos change a few times a year. Posters are
committed artifacts.

  Usage:
    python3 scripts/capture-demo-posters.py           # capture what is missing
    python3 scripts/capture-demo-posters.py --all     # recapture everything
    python3 scripts/capture-demo-posters.py --prune   # also delete orphans
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "static" / "demos" / "_shared" / "demos.json"
POSTERS = ROOT / "static" / "img" / "demos"
PORT = 1189

# Capture viewport. Wide enough that every demo renders its DESKTOP layout
# rather than the narrow fallback, matching what the live previews show.
VIEW_W, VIEW_H = 1200, 750

# Output width. The tile is ~350px at 3-up and ~540px in a single-demo row, so
# 900 covers both at 2x for retina without carrying a full-size screenshot.
OUT_W = 900
WEBP_QUALITY = 72

# Simulated milliseconds to run before the shot. Chrome's virtual time budget
# fast-forwards the page clock, so this is deterministic rather than a race
# against a real sleep — which matters because two of these demos are WASM apps
# that mount into an empty div and then need their simulation to settle.
VIRTUAL_TIME_MS = 4000

# Below this many distinct colours a capture is almost certainly a blank page:
# WASM that never mounted, or a demo that starts empty and needs an interaction.
# Shipping a blank poster is worse than shipping none, because the fallback card
# is fine and a blank tile just looks broken.
MIN_COLORS = 48


def find_chrome() -> str:
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(c):
            return c
    sys.exit("error: no Chrome/Chromium on PATH — needed to capture demo posters.")


def main() -> int:
    recapture_all = "--all" in sys.argv
    prune = "--prune" in sys.argv

    try:
        from PIL import Image
    except ImportError:
        sys.exit("error: Pillow is required (python3 -m pip install Pillow).")

    if not INDEX.exists():
        sys.exit(f"error: {INDEX.relative_to(ROOT)} missing — run build-demo-index.py first.")
    entries = json.loads(INDEX.read_text(encoding="utf-8"))["demos"]

    wanted = {e["name"]: e for e in entries if e["heavy"] and e["listed"]}
    todo = [e for e in wanted.values() if recapture_all or not e["poster"]]

    keep = {f"{e['name'].replace('/', '-')}.{e['hash']}.webp" for e in wanted.values()}
    if prune:
        for old in sorted(POSTERS.glob("*.webp")) if POSTERS.exists() else []:
            if old.name not in keep:
                old.unlink()
                print(f"  pruned stale poster {old.name}")

    if not todo:
        print(f"All {len(wanted)} heavy demos already have a current poster.")
        return 0

    chrome = find_chrome()
    if not shutil.which("zola"):
        sys.exit("error: zola not on PATH.")
    POSTERS.mkdir(parents=True, exist_ok=True)

    # --base-url is NOT optional. get_url() bakes zola.toml's base_url into every
    # asset href, so a default build would serve the local page while pulling its
    # CSS and JS from the DEPLOYED site — capturing production rather than what is
    # on disk, silently and convincingly.
    build_dir = Path(tempfile.mkdtemp())
    server = None
    try:
        print(f"Building against http://127.0.0.1:{PORT} …")
        subprocess.run(
            ["zola", "build", "--base-url", f"http://127.0.0.1:{PORT}",
             "--output-dir", str(build_dir), "--force"],
            check=True, stdout=subprocess.DEVNULL,
        )
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(PORT),
             "--directory", str(build_dir), "--bind", "127.0.0.1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=0.3)
                break
            except Exception:
                time.sleep(0.1)

        failures = []
        for e in todo:
            name, digest = e["name"], e["hash"]
            out = POSTERS / f"{name.replace('/', '-')}.{digest}.webp"
            # ?poster suppresses the standalone back-link bar, which would
            # otherwise be baked into the thumbnail (demo-chrome.js).
            url = f"http://127.0.0.1:{PORT}/demos/{name}/?poster=1"
            print(f"Capturing {name} …")

            with tempfile.TemporaryDirectory() as shot_dir:
                png = Path(shot_dir) / "shot.png"
                subprocess.run(
                    [chrome, "--headless=old", "--disable-gpu", "--no-sandbox",
                     "--hide-scrollbars",
                     f"--window-size={VIEW_W},{VIEW_H}",
                     f"--virtual-time-budget={VIRTUAL_TIME_MS}",
                     f"--screenshot={png}", url],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                if not png.exists() or png.stat().st_size == 0:
                    failures.append(f"{name}: chrome produced no image")
                    continue

                img = Image.open(png).convert("RGB")
                colors = img.getcolors(maxcolors=1 << 20)
                distinct = len(colors) if colors else 1 << 20
                if distinct < MIN_COLORS:
                    failures.append(
                        f"{name}: capture has {distinct} distinct colours — looks blank. "
                        f"Raise VIRTUAL_TIME_MS, or the demo may need an interaction first.")
                    continue

                img = img.resize((OUT_W, round(img.height * OUT_W / img.width)), Image.LANCZOS)
                img.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
                print(f"  wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB, "
                      f"{distinct} colours)")

        if failures:
            print("\nsome posters were not written:", file=sys.stderr)
            for f in failures:
                print(f"  {f}", file=sys.stderr)
            print("  Those tiles keep the drawn card, which is a working fallback.",
                  file=sys.stderr)
            return 1
    finally:
        if server:
            server.terminate()
        shutil.rmtree(build_dir, ignore_errors=True)

    print("\nRe-run build-demo-index.py (or build.sh) so demos.json picks the posters up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
