#!/usr/bin/env bash
# Production build for Cloudflare Pages.
#
# Cloudflare doesn't pre-install Zola and runs no post-build step, so this script
# owns the whole pipeline: fetch Zola if it isn't already on PATH, compute the
# related-posts index (scripts/compute-related.py → related.json, read by
# templates/post.html via load_data), build the site, then index the rendered HTML
# in public/ with Pagefind (which writes public/pagefind/). related.json, like the
# Pagefind index, is a regenerated build artifact (gitignored) — never committed.
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

echo "Computing related posts (TF-IDF → related.json)…"
python3 scripts/compute-related.py

echo "Building site with ${ZOLA}…"
"$ZOLA" build

echo "Indexing with Pagefind v${PAGEFIND_VERSION}…"
npx -y "pagefind@${PAGEFIND_VERSION}" --site public

echo "Build + index complete → public/ (search index in public/pagefind/)."
