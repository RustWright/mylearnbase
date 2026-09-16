#!/usr/bin/env bash
# Production build for Cloudflare Pages.
#
# Cloudflare doesn't pre-install Zola and runs no post-build step, so this script
# owns the whole pipeline: fetch Zola if it isn't already on PATH, compute the
# related-posts index (scripts/compute-related.py → related.json, read by
# templates/post.html via load_data), derive the demo index
# (scripts/build-demo-index.py → static/demos/_shared/demos.json), build the site,
# then index the rendered HTML in public/ with Pagefind (which writes
# public/pagefind/). Both indexes, like the Pagefind index, are regenerated build
# artifacts (gitignored) — never committed.
#
# Cloudflare Pages → Settings → Builds & deployments → Build command:  bash build.sh
#
# Runs locally too: if Zola is already installed it's reused (no re-download), so
# `bash build.sh` reproduces the production output, including the search index that
# a plain `zola serve` can't generate.
set -euo pipefail

ZOLA_VERSION="0.22.1"
PAGEFIND_VERSION="1.5.2"

if command -v zola >/dev/null 2>&1; then
  ZOLA="zola"
else
  echo "Zola not found — downloading v${ZOLA_VERSION}…"
  curl -sL "https://github.com/getzola/zola/releases/download/v${ZOLA_VERSION}/zola-v${ZOLA_VERSION}-x86_64-unknown-linux-gnu.tar.gz" | tar xz
  ZOLA="./zola"
fi

# Résumé drift check. The HTML page is the source of truth and the PDF is
# generated from it (scripts/build-resume-pdf.sh), but that generation happens
# LOCALLY — Cloudflare's build image is not guaranteed to carry a browser. So the
# one thing CI can do is notice when the two have parted company.
#
# Warn, never fail: a stale download is worth shipping; a blocked deploy over a
# résumé bullet is not. The point is that the drift is LOUD rather than silent.
RESUME_SRC="content/resume/_index.md"
RESUME_HASH="static/resume/.source-hash"
if [ -f "$RESUME_SRC" ]; then
  if [ -f "$RESUME_HASH" ]; then
    if [ "$(shasum -a 256 "$RESUME_SRC" | awk '{print $1}')" != "$(cat "$RESUME_HASH")" ]; then
      echo "WARNING: $RESUME_SRC changed since the PDF was generated."
      echo "         The page and its download now disagree."
      echo "         Fix with: bash scripts/build-resume-pdf.sh && git add static/resume/"
    fi
  else
    echo "WARNING: no $RESUME_HASH — the résumé PDF has never been generated."
  fi
fi

# Link-preview card drift check. Same shape as the résumé check: the PNG is
# rendered locally from the site's own title, tagline, host and logo, and CI can
# only notice when it no longer matches them. The script owns the hash, so the
# rule for what counts as a change lives in one place. It warns and never fails.
python3 scripts/build-og-card.py --check

# Homepage "Now" line freshness. It states what is happening at present, and a
# static page keeps stating it long after it stops being true. Warn, never
# fail, for the same reason as above; the homepage prints the date regardless.
python3 - <<'PY'
import datetime, re
from pathlib import Path

m = re.search(r'^now_updated\s*=\s*"(\d{4}-\d{2}-\d{2})"', Path("content/_index.md").read_text(), re.M)
if m:
    age = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
    if age > 90:
        print(f"WARNING: the homepage Now line is {age} days old (now_updated = {m.group(1)}).")
        print("         Rewrite the body of content/_index.md and bump now_updated.")
PY

# Download sizes. A download link states its file size, the way a page link does
# not: someone saving a file thinks about what they are getting, and Zola has no
# template function that can read a file's size (its file helpers are get_hash,
# get_image_metadata and load_data). So measure here, into download-sizes.json.
#
# Measured at build time from the file actually being deployed, rather than
# recorded when build-resume-pdf.sh generates the PDF: a size written at
# generation goes stale if the file ever arrives another way, while one measured
# here cannot disagree with what ships. Keyed by site URL, so a template looks it
# up with the same path its front matter already carries (extra.pdf).
echo "Measuring downloads (static/**/*.pdf → download-sizes.json)…"
python3 - <<'PY'
import json
from pathlib import Path

sizes = {}
for pdf in sorted(Path("static").rglob("*.pdf")):
    n = pdf.stat().st_size
    label = f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{round(n / 1024)} KB"
    sizes["/" + pdf.relative_to("static").as_posix()] = {"bytes": n, "label": label}
Path("download-sizes.json").write_text(json.dumps(sizes, indent=2) + "\n", encoding="utf-8")
print(f"  {len(sizes)} download(s) measured")
PY

echo "Computing related posts (TF-IDF → related.json)…"
python3 scripts/compute-related.py

echo "Deriving the demo index (demo() calls → static/demos/_shared/demos.json)…"
python3 scripts/build-demo-index.py

echo "Building site with ${ZOLA}…"
"$ZOLA" build

# Assert the derived back-links actually resolve in what was just built.
#
# This is the one link class Zola cannot check: the demo bar is injected by
# JavaScript at runtime, so a wrong URL is invisible to `zola check` and to the
# build, and surfaces only as a reader hitting a 404 from inside a demo.
# build-demo-index.py reconstructs Zola's routing in Python to produce those
# URLs, and this is what keeps that reconstruction honest.
echo "Verifying demo back-links resolve…"
python3 scripts/build-demo-index.py --verify public

echo "Indexing with Pagefind v${PAGEFIND_VERSION}…"
npx -y "pagefind@${PAGEFIND_VERSION}" --site public

echo "Build + index complete → public/ (search index in public/pagefind/)."
