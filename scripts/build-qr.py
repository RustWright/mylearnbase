#!/usr/bin/env python3
"""Render the site's QR code (static/img/site-qr.svg) from zola.toml's print_url.

One code serves every printed surface: the résumé's masthead and the business
card. It encodes print_url, the short name-based domain, NOT canonical_url. That
domain 301s to the site at Cloudflare, so where a printed code LEADS can change
later by editing one redirect rule, while what is printed never has to.

WHY UPPERCASE: QR alphanumeric mode packs 0-9, A-Z and $%*+-./: at 5.5 bits a
character; a single lowercase letter forces byte mode at 8. "https://efeerhie.com"
needs a version-2 grid (25x25) at error-correction M, "HTTPS://EFEERHIE.COM" fits
version 1 (21x21), so each module prints ~19% wider at the same size. Safe only
because scheme and host are case-insensitive (RFC 3986). A PATH is not, so the
script refuses a print_url that has one rather than silently breaking it.

VERIFIED, not trusted: the code is decoded back with OpenCV and compared to the
URL. Skipped with a warning when OpenCV is absent. Committed, like the résumé
PDF, because the URL changes about never and the deploy image need not carry a
QR library.

  Usage:  python3 scripts/build-qr.py        (needs the `qrcode` package)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import qrcode
import qrcode.image.svg

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "img" / "site-qr.svg"


def print_url() -> str:
    m = re.search(r'^print_url\s*=\s*"([^"]+)"', (ROOT / "zola.toml").read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit("error: could not find extra.print_url in zola.toml")
    url = m.group(1).rstrip("/")
    if re.sub(r"^https?://", "", url).count("/"):
        sys.exit(f"error: print_url {url!r} has a path. Paths are case-sensitive, so it cannot be uppercased.")
    return url


def build(data: str) -> qrcode.QRCode:
    # border=0: NO quiet zone in the file. Every placement must leave 4 modules of
    # blank space around the code itself, and on paper the margins already do;
    # a built-in border would spend ~28% of the printed width on white.
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0,
                       image_factory=qrcode.image.svg.SvgPathImage)
    qr.add_data(data)
    qr.make(fit=True)
    return qr


def verify(qr: qrcode.QRCode, expected: str) -> None:
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("warning: OpenCV not found, the QR code was NOT decode-verified.", file=sys.stderr)
        return
    # Rasterise the module matrix directly: white is 255, 10 px a module. Padded
    # with the 4-module quiet zone the file leaves to its placement.
    img = np.where(np.array(qr.get_matrix(), dtype=bool), 0, 255).astype(np.uint8)
    img = np.pad(img, 4, constant_values=255)
    img = np.kron(img, np.ones((10, 10), dtype=np.uint8))
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if decoded != expected:
        sys.exit(f"error: the QR code decodes to {decoded!r}, expected {expected!r}")
    print(f"Verified: decodes to {decoded}")


def main() -> None:
    url = print_url()
    data = url.upper()
    qr = build(data)
    verify(qr, data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    qr.make_image().save(str(OUT))
    print(f"Wrote {OUT.relative_to(ROOT)}: {url} as version {qr.version} ({qr.modules_count}x{qr.modules_count}), EC level M")


if __name__ == "__main__":
    main()
