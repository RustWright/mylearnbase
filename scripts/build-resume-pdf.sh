#!/usr/bin/env bash
# Render /resume/ to the downloadable PDF.
#
# The HTML page is the source of truth; this script is how the PDF stays equal to
# it. Run it whenever content/resume/_index.md changes — build.sh warns when the
# two have drifted (it compares the markdown's hash against .source-hash below).
#
# WHY THIS RUNS LOCALLY AND COMMITS ITS OUTPUT, when related.json is computed in
# CI: Cloudflare Pages build images are not guaranteed to carry a browser, and
# losing a deploy over a missing Chrome is a bad trade for a document that changes
# a few times a year. related.json changes on every post; this does not.
#
#   Usage:  bash scripts/build-resume-pdf.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

SRC="content/resume/_index.md"
OUT_DIR="static/resume"
OUT="$OUT_DIR/efe-oghene-erhie-resume.pdf"
HASH_FILE="$OUT_DIR/.source-hash"
PORT="${RESUME_PDF_PORT:-1187}"

CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
done
if [ -z "$CHROME" ]; then
  echo "error: no Chrome/Chromium on PATH — needed to print the résumé to PDF." >&2
  echo "       install one, or generate the PDF on a machine that has it." >&2
  exit 1
fi

if ! command -v zola >/dev/null 2>&1; then
  echo "error: zola not on PATH." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# Print from a real HTTP server rather than a file:// path. The page pulls CSS and
# fonts through absolute site-root URLs (/css/custom.css), which file:// resolves
# against the filesystem root and silently fails to load — producing an unstyled
# PDF that still looks like a successful run.
# --base-url is NOT optional. get_url() bakes zola.toml's base_url into every
# asset href, so a default build serves the local page while pulling its CSS from
# https://mylearnbase.com — the PDF then reflects whatever is DEPLOYED rather than
# what is on disk, and a stylesheet that has not shipped yet simply 404s. That
# failure is invisible: the page still looks styled, because production CSS
# loaded fine. Build into a scratch directory so the committed public/ is not
# left holding localhost URLs.
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "Building site against http://127.0.0.1:$PORT …"
zola build --base-url "http://127.0.0.1:$PORT" --output-dir "$BUILD_DIR" --force >/dev/null

echo "Serving the local build on :$PORT…"
python3 -m http.server "$PORT" --directory "$BUILD_DIR" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$BUILD_DIR"' EXIT

# Wait for readiness instead of sleeping a guessed interval.
for _ in $(seq 1 50); do
  if curl -fsS "http://127.0.0.1:$PORT/resume/" >/dev/null 2>&1; then break; fi
  sleep 0.1
done

echo "Printing /resume/ with $CHROME…"
# --headless=old is REQUIRED, and it is not interchangeable with plain --headless.
# Chrome's new headless renders --print-to-pdf against SCREEN media, so the
# @media print block in static/css/custom.css is ignored entirely and the PDF
# comes out carrying the site nav, the theme toggle and a "Download PDF" button
# inside the download. Verified on Chrome 151 by printing with a red background
# forced under @media print: the PDF stayed white.
#
# Old headless is deprecated and will eventually be removed. That is why the
# verification below exists rather than a comment hoping someone notices.
#
# --no-pdf-header-footer drops Chrome's own page URL/date furniture.
"$CHROME" \
  --headless=old \
  --disable-gpu \
  --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf="$OUT" \
  "http://127.0.0.1:$PORT/resume/?print" >/dev/null 2>&1

if [ ! -s "$OUT" ]; then
  echo "error: no PDF produced at $OUT" >&2
  exit 1
fi

# Verify the print stylesheet actually took, instead of trusting the exit code.
# The whole failure mode here is silent: a PDF that renders fine, opens fine, and
# has a navigation bar across the top of someone's résumé. Assert on content.
if command -v pdftotext >/dev/null 2>&1; then
  TXT="$(pdftotext "$OUT" - 2>/dev/null || true)"
  LEAKED=""
  for marker in "Download PDF" "My Learn Base"; do
    case "$TXT" in *"$marker"*) LEAKED="$LEAKED  - $marker"$'\n' ;; esac
  done
  if [ -n "$LEAKED" ]; then
    echo "error: the print stylesheet did not apply — screen-only chrome leaked into the PDF:" >&2
    printf '%s' "$LEAKED" >&2
    echo "       Chrome's NEW headless prints against screen media. If --headless=old has" >&2
    echo "       been removed from this Chrome, switch this script to a CDP-driven printer" >&2
    echo "       (Playwright's page.pdf() emulates print media correctly)." >&2
    rm -f "$OUT"
    exit 1
  fi
  echo "Verified: no screen-only chrome in the PDF text."
else
  echo "warning: pdftotext not found — could not verify the print stylesheet applied." >&2
fi

# The --base-url override above is necessary, and it is also a leak waiting to
# happen: anything that renders base_url prints this script's localhost address.
# The first structured résumé did exactly that — "127.0.0.1:1187" as the site
# address, and six clickable links in the PDF pointing at localhost. BOTH places
# need checking, because each is invisible to the other method: link targets
# live in uncompressed /URI annotations that pdftotext never shows, while the
# printed text sits in compressed content streams that a raw byte search cannot
# read. Verified: a raw grep of that PDF found the five link targets and missed
# the printed "127.0.0.1:1187" entirely.
LOCALHOST_RE="127\.0\.0\.1|localhost"
if { pdftotext "$OUT" - 2>/dev/null; cat "$OUT"; } | LC_ALL=C grep -a -q -E "$LOCALHOST_RE"; then
  echo "error: the PDF names a localhost address — base_url leaked into the printed page:" >&2
  { pdftotext "$OUT" - 2>/dev/null; cat "$OUT"; } \
    | LC_ALL=C grep -a -o -E "/URI \([^)]*($LOCALHOST_RE)[^)]*\)|[^ ]*($LOCALHOST_RE)[^ ]*" \
    | sort -u | head -8 | sed 's/^/  - /' >&2
  echo "       Anything that names the real site must read config.extra.canonical_url," >&2
  echo "       which this script does not override. See templates/resume.html." >&2
  rm -f "$OUT"
  exit 1
fi
echo "Verified: no localhost address in the PDF text or its links."

# Record what the PDF was built FROM, so build.sh can tell when the page has moved
# on without it. Hashing the source (not the PDF) is the point: the PDF's bytes
# change on every run from timestamps, so it cannot be its own witness.
shasum -a 256 "$SRC" | awk '{print $1}' > "$HASH_FILE"

echo "Wrote $OUT ($(wc -c < "$OUT") bytes)"
echo "Recorded source hash → $HASH_FILE"
echo
echo "Both files are committed artifacts. Run 'zola build' again so the PDF is"
echo "copied into public/, then commit static/resume/."
