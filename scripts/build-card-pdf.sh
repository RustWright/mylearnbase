#!/usr/bin/env bash
# Render print/business-card/card.html to a print-ready PDF for W Print.
#
# Same printer as build-resume-pdf.sh (headless Chrome, --headless=old; see the
# reasoning there), but from file:// with no server: the card's asset paths are
# all relative, so nothing resolves against the filesystem root. The card is
# not part of the site and is never deployed.
#
# Then VERIFY, because every failure here is silent and costs a print run:
#   - two pages (front, back), each 3.75 x 2.25in = trimmed 3.5 x 2 plus bleed
#   - the fonts actually embedded (a fallback face would still "work")
#   - the back's QR code decodes, from the rendered page, to the résumé URL
#   - no protected title: "Engineer" as a word, never as part of "Engineering"
#   - every email address is the @efeerhie.com alias
#
#   Usage:  bash scripts/build-card-pdf.sh      (run build-qr.py first if the URL changed)
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

SRC="print/business-card/card.html"
OUT="print/business-card/efe-oghene-erhie-card.pdf"
EXPECT_QR="https://efeerhie.com/resume/"

CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
done
[ -n "$CHROME" ] || { echo "error: no Chrome/Chromium on PATH." >&2; exit 1; }

echo "Printing $SRC with $CHROME…"
"$CHROME" --headless=old --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf="$OUT" "file://$PWD/$SRC" >/dev/null 2>&1
[ -s "$OUT" ] || { echo "error: no PDF produced at $OUT" >&2; exit 1; }

fail() { echo "error: $*" >&2; rm -f "$OUT"; exit 1; }

PAGES="$(pdfinfo "$OUT" | awk '/^Pages:/{print $2}')"
[ "$PAGES" = "2" ] || fail "expected 2 pages (front, back), got $PAGES. Something overflowed a page."
SIZE="$(pdfinfo "$OUT" | awk -F': *' '/^Page size:/{print $2}')"
case "$SIZE" in 270*x*162*) ;; *) fail "page size is '$SIZE', expected 270 x 162 pts (3.75 x 2.25in with bleed)." ;; esac
echo "Verified: 2 pages at 3.75 x 2.25in (3.5 x 2in card + 0.125in bleed)."

pdffonts "$OUT" | grep -q "SourceSans3" || fail "Source Sans 3 is not embedded; the card printed in a fallback face."
echo "Verified: Source Sans 3 embedded."

TXT="$(pdftotext "$OUT" -)"
if printf '%s' "$TXT" | grep -q -w -i "engineer"; then
  fail "the card uses 'Engineer' as a title. Unlicensed in Ontario: degree wording only."
fi
STRAY="$(printf '%s' "$TXT" | grep -o -E "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" | grep -v -i "@efeerhie.com\$" || true)"
[ -z "$STRAY" ] || fail "an email outside @efeerhie.com is on the card: $STRAY"
echo "Verified: no protected title; email is the alias."

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pdftoppm -r 300 -f 2 -l 2 -png "$OUT" "$TMP/back"
GOT="$(python3 -c "import cv2,glob; print(cv2.QRCodeDetector().detectAndDecode(cv2.imread(glob.glob('$TMP/back*.png')[0]))[0])" 2>/dev/null || true)"
[ "$GOT" = "$EXPECT_QR" ] || fail "the printed QR decodes to '$GOT', expected '$EXPECT_QR'."
echo "Verified: the printed back's QR decodes to $GOT"

echo "Wrote $OUT ($(wc -c < "$OUT") bytes). Upload it to W Print as a double-sided 3.5 x 2in card."
