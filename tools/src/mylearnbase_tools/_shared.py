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
_BASH_IMAGE_BLOCK_RE = re.compile(
    r"```bash \{image\}\n(?P<path>[^\n]+)\n```\n?", re.MULTILINE
)


def copy_and_rewrite_referenced_images(
    body: str, src_dir: Path, dest_dir: Path
) -> tuple[str, list[str]]:
    """Process showboat-emitted and hand-written image refs for the colocated layout.

    Three passes:
      1. Strip ` ```bash {image}\\n<path>\\n``` ` blocks; record the absolute path.
         These are showboat's leading-code-fence-for-images, useless in the post.
      2. For each stripped block, find the next `![alt](<tracking-id>.png)` ref and
         rewrite it to `![alt](./<basename-of-recorded-path>)`, copying the source.
      3. For remaining hand-written `![alt](<rel>)` refs, resolve <rel> against
         src_dir, copy source to dest_dir/<basename>, and rewrite to `./<basename>`.

    Leaves http/https and absolute paths alone.

    Returns (rewritten_body, list_of_copied_basenames).
    """
    copied: list[str] = []

    # Pass 1 + 2: process bash {image} blocks and their paired refs.
    pending_sources: list[Path] = []

    def _strip_block(match: re.Match) -> str:
        pending_sources.append(Path(match.group("path").strip()))
        return ""

    body = _BASH_IMAGE_BLOCK_RE.sub(_strip_block, body)

    # Walk forward through image refs, consuming pending_sources in order.
    out_parts: list[str] = []
    last_end = 0
    pending_iter = iter(pending_sources)
    next_pending = next(pending_iter, None)

    for match in _IMAGE_REF_RE.finditer(body):
        ref = match.group(1).strip().split()[0]
        out_parts.append(body[last_end:match.start()])

        if ref.startswith(("http://", "https://", "/")):
            out_parts.append(match.group(0))
            last_end = match.end()
            continue

        if next_pending is not None and next_pending.is_file():
            basename = next_pending.name
            shutil.copy2(next_pending, dest_dir / basename)
            copied.append(basename)
            alt = match.group(0).split("](", 1)[0]
            out_parts.append(f"{alt}](./{basename})")
            last_end = match.end()
            next_pending = next(pending_iter, None)
            continue

        src = (src_dir / ref).resolve()
        if not src.is_file():
            out_parts.append(match.group(0))
            last_end = match.end()
            continue

        basename = src.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_dir / basename)
        copied.append(basename)
        alt = match.group(0).split("](", 1)[0]
        out_parts.append(f"{alt}](./{basename})")
        last_end = match.end()

    out_parts.append(body[last_end:])
    return "".join(out_parts), copied


def strip_empty_sections(body: str, required_headers: list[str] | None = None) -> str:
    """Drop `## ` headers whose body is empty/whitespace.

    If `required_headers` is provided, raise ValueError naming any required
    sections whose body is empty — caller is the form module that knows which
    section headers are required vs optional.
    """
    required = set(required_headers or [])
    parts = re.split(r"^(## .+)$", body, flags=re.MULTILINE)
    out: list[str] = []
    missing: list[str] = []
    if parts and parts[0].strip():
        out.append(parts[0])
    for i in range(1, len(parts), 2):
        header = parts[i]
        section_body = parts[i + 1] if i + 1 < len(parts) else ""
        if section_body.strip():
            out.append(header)
            out.append(section_body)
        else:
            header_text = header[3:].strip()
            if header_text in required:
                missing.append(header_text)
    if missing:
        raise ValueError(f"required section(s) empty: {', '.join(missing)}")
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
