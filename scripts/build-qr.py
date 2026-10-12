#!/usr/bin/env python3
"""Render the printed QR codes (static/img/*-qr.svg) from zola.toml's print_url.

Every code encodes print_url, the short name-based domain, NOT canonical_url.
That domain 301s to the site at Cloudflare, path and query kept, so where a
printed code LEADS can change later by editing one redirect rule, while what is
printed never has to. Each surface gets the destination its reader needs:

  site-qr.svg    print_url              résumé masthead: the reader already holds
                                        the résumé, so send them to the projects
  resume-qr.svg  print_url + /resume/   business card: the reader holds a name and
                                        an email, so send them to the résumé

WHY UPPERCASE (bare domain only): QR alphanumeric mode packs 0-9, A-Z and
$%*+-./: at 5.5 bits a character; a single lowercase letter forces byte mode at
8. "https://efeerhie.com" needs a version-2 grid (25x25) at error-correction M,
"HTTPS://EFEERHIE.COM" fits version 1 (21x21), so each module prints ~19% wider
at the same size. Safe because scheme and host are case-insensitive (RFC 3986).
A PATH is not, so a code with a path stays lowercase and takes the bigger grid.

VERIFIED, not trusted: each code is decoded back with OpenCV and compared to its
URL. Skipped with a warning when OpenCV is absent. Committed, like the résumé
PDF, because the URLs change about never and the deploy image need not carry a
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
OUT_DIR = ROOT / "static" / "img"

# (file, path appended to print_url). An empty path is the bare domain.
CODES = [
    ("site-qr.svg", ""),
    ("resume-qr.svg", "/resume/"),
]


def print_url() -> str:
    m = re.search(r'^print_url\s*=\s*"([^"]+)"', (ROOT / "zola.toml").read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit("error: could not find extra.print_url in zola.toml")
    url = m.group(1).rstrip("/")
    if re.sub(r"^https?://", "", url).count("/"):
        sys.exit(f"error: print_url {url!r} must be a bare domain; per-code paths live in CODES.")
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
    base = print_url()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, path in CODES:
        data = base.upper() if not path else base + path
        qr = build(data)
        verify(qr, data)
        out = OUT_DIR / name
        qr.make_image().save(str(out))
        print(f"Wrote {out.relative_to(ROOT)}: {data} as version {qr.version} ({qr.modules_count}x{qr.modules_count}), EC level M")


if __name__ == "__main__":
    main()
