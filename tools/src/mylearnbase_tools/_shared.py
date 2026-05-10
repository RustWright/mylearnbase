"""Cross-form helpers shared by logbook/cookbook/workflows.

These exist as a separate module so per-form CLI modules don't drift in their
shared substrate (showboat invocation, repo discovery, zola check, image copy,
empty-section pruning). Per-form modules import what they need; nothing here
is form-specific.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run_showboat(args: list[str]) -> subprocess.CompletedProcess:
    """Invoke showboat. Raises RuntimeError if not on PATH."""
    try:
        return subprocess.run(["showboat", *args], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("showboat not found on PATH; install showboat before using this tool") from exc


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError("not in a git repository")
    return Path(out.stdout.strip())


def mylearnbase_root() -> Path:
    """Resolve the mylearnbase repo path. MYLEARNBASE_ROOT env wins; default fallback."""
    env = os.environ.get("MYLEARNBASE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    fallback = Path("~/productive_learning/projects/mylearnbase").expanduser().resolve()
    if fallback.is_dir():
        return fallback
    raise RuntimeError(
        "MYLEARNBASE_ROOT is unset and the default ~/productive_learning/projects/mylearnbase does not exist."
    )


def read_text_arg(text: str | None) -> str:
    """Return text arg if provided, else read from stdin."""
    if text is not None:
        return text
    if sys.stdin.isatty():
        print("no text provided; reading from stdin (Ctrl-D to end)...", file=sys.stderr)
    return sys.stdin.read().rstrip("\n")


_IMAGE_REF_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def copy_referenced_images(body: str, src_dir: Path, dest_dir: Path) -> list[str]:
    """Copy local image references from `src_dir` to `dest_dir`.

    Skips http(s) URLs and absolute paths. Returns the list of relative paths copied.
    """
    copied: list[str] = []
    for match in _IMAGE_REF_RE.finditer(body):
        ref = match.group(1).strip().split()[0]
        if ref.startswith(("http://", "https://", "/")):
            continue
        src = src_dir / ref
        if not src.is_file():
            continue
        dest = dest_dir / ref
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(ref)
    return copied


def strip_empty_sections(body: str) -> str:
    """Drop `## ` headers whose body is empty/whitespace."""
    parts = re.split(r"^(## .+)$", body, flags=re.MULTILINE)
    out: list[str] = []
    if parts and parts[0].strip():
        out.append(parts[0])
    for i in range(1, len(parts), 2):
        header = parts[i]
        section_body = parts[i + 1] if i + 1 < len(parts) else ""
        if section_body.strip():
            out.append(header)
            out.append(section_body)
    return "".join(out).strip() + "\n"


def zola_check(content_root: Path, skip_external_links: bool = True) -> tuple[int, str]:
    """Run `zola check` from a Zola site root. Returns (returncode, combined_output).

    External-link probing is the slow part; skipped by default.
    """
    cmd = ["zola", "check"]
    if skip_external_links:
        cmd.append("--skip-external-links")
    result = subprocess.run(
        cmd,
        cwd=content_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()
