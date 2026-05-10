"""cite: capture file:line + line content + HEAD SHA + GitHub permalink.

Form-agnostic. Discovers project context from the working directory + the
project's git remote, so it runs from any project repo.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from . import _capture


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    """Run `git <args>` and return stripped stdout. Raises on nonzero exit."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def _parse_ref(ref: str) -> tuple[str, int]:
    """Split `<path>:<line>` into (path, line). Raises ValueError on bad input."""
    if ":" not in ref:
        raise ValueError(f"ref must be of the form <path>:<line>, got {ref!r}")
    path, _, line_str = ref.rpartition(":")
    if not path:
        raise ValueError(f"ref missing a path: {ref!r}")
    try:
        line = int(line_str)
    except ValueError as exc:
        raise ValueError(f"ref line must be an integer, got {line_str!r}") from exc
    if line < 1:
        raise ValueError(f"ref line must be >= 1, got {line}")
    return path, line


def _repo_root() -> Path:
    """Return the absolute path of the current git repo root."""
    return Path(_run_git(["rev-parse", "--show-toplevel"]))


def _parse_remote_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub remote URL. Returns None if not GitHub."""
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[: -len(".git")]
    m = re.match(r"^git@github\.com:([^/]+)/(.+)$", url)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^https://github\.com/([^/]+)/(.+)$", url)
    if m:
        return m.group(1), m.group(2)
    return None


def _file_is_dirty(repo_root: Path, rel_path: str) -> bool:
    """True if `rel_path` has uncommitted changes (staged or unstaged)."""
    out = _run_git(["status", "--porcelain", "--", rel_path], cwd=repo_root)
    return bool(out.strip())


def _read_line(file: Path, line: int) -> str:
    """Return the 1-indexed line content of `file`, sans trailing newline."""
    with file.open(encoding="utf-8") as f:
        for i, content in enumerate(f, start=1):
            if i == line:
                return content.rstrip("\n")
    raise ValueError(f"{file} has fewer than {line} lines")


def _format_cite_block(
    rel_path: str,
    line: int,
    sha: str,
    line_content: str,
    permalink: str | None,
    note: str | None,
) -> str:
    """Render a markdown citation block."""
    short_sha = sha[:7]
    if permalink:
        header = f"[`{rel_path}:{line}`]({permalink}) at `{short_sha}`"
    else:
        header = f"`{rel_path}:{line}` at `{short_sha}`"
    block = f"{header}\n> `{line_content}`"
    if note:
        block += f"\n>\n> {note}"
    return block


def _resolve_path(arg_path: str, repo_root: Path) -> tuple[Path, str]:
    """Resolve `arg_path` (cwd-relative or absolute) to (absolute, repo-relative)."""
    abs_path = Path(arg_path).resolve()
    try:
        rel = abs_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"{abs_path} is not inside the git repo at {repo_root}") from exc
    return abs_path, str(rel)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cite",
        description="Capture a code citation (file:line + commit-SHA permalink) into a capture file.",
    )
    parser.add_argument("capture_file", help="Path to the capture file to append to.")
    parser.add_argument("ref", help="Code reference in the form <path>:<line> (e.g. src/foo.rs:42).")
    parser.add_argument("--note", help="Optional inline commentary to attach to the citation.", default=None)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Skip the per-file dirty check. Permalink stability is the caller's responsibility.",
    )
    parser.add_argument(
        "--section",
        help="Append into a specific `## <header>` section of the capture file (form-agnostic). "
        "If omitted, appends to end of file.",
        default=None,
    )
    args = parser.parse_args(argv)

    try:
        path_arg, line = _parse_ref(args.ref)
    except ValueError as exc:
        print(f"cite: {exc}", file=sys.stderr)
        return 2

    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"cite: not in a git repo ({exc})", file=sys.stderr)
        return 2

    try:
        abs_path, rel_path = _resolve_path(path_arg, root)
    except ValueError as exc:
        print(f"cite: {exc}", file=sys.stderr)
        return 2

    if not abs_path.is_file():
        print(f"cite: {abs_path} is not a file", file=sys.stderr)
        return 2

    if not args.allow_dirty and _file_is_dirty(root, rel_path):
        print(
            f"cite: {rel_path} has uncommitted changes — permalink would be unstable. "
            "Commit/stash, or pass --allow-dirty.",
            file=sys.stderr,
        )
        return 1

    try:
        sha = _run_git(["rev-parse", "HEAD"], cwd=root)
    except RuntimeError as exc:
        print(f"cite: cannot resolve HEAD ({exc})", file=sys.stderr)
        return 2

    permalink: str | None = None
    try:
        remote_url = _run_git(["remote", "get-url", "origin"], cwd=root)
        owner_repo = _parse_remote_url(remote_url)
        if owner_repo:
            owner, repo = owner_repo
            permalink = f"https://github.com/{owner}/{repo}/blob/{sha}/{rel_path}#L{line}"
    except RuntimeError:
        pass

    try:
        line_content = _read_line(abs_path, line)
    except ValueError as exc:
        print(f"cite: {exc}", file=sys.stderr)
        return 2

    block = _format_cite_block(rel_path, line, sha, line_content, permalink, args.note)

    capture = Path(args.capture_file)
    capture.parent.mkdir(parents=True, exist_ok=True)

    if args.section:
        if not capture.exists():
            print(f"cite: capture file does not exist: {capture}", file=sys.stderr)
            return 1
        try:
            _capture.append_to_section(capture, args.section, block)
        except ValueError as exc:
            print(f"cite: {exc}", file=sys.stderr)
            return 1
    else:
        existing = capture.read_text(encoding="utf-8") if capture.exists() else ""
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        capture.write_text(existing + separator + block + "\n", encoding="utf-8")

    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
