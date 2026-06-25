#!/usr/bin/env bash
# Production build for Cloudflare Pages.
#
# Cloudflare doesn't pre-install Zola and runs no post-build step, so this script
# owns the whole pipeline: fetch Zola if it isn't already on PATH, build the site,
# then index the rendered HTML in public/ with Pagefind (which writes public/pagefind/).
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

echo "Building site with ${ZOLA}…"
"$ZOLA" build

echo "Indexing with Pagefind v${PAGEFIND_VERSION}…"
npx -y "pagefind@${PAGEFIND_VERSION}" --site public

echo "Build + index complete → public/ (search index in public/pagefind/)."
