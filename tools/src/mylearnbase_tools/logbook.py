"""logbook: capture (init/what/why/scope/note) and publish (capture -> Zola post).

Captures live in the *project* repo at `<repo-root>/logbook/_drafts/<slug>.md`
(mirrors cookbook's draft layout). Section writers append to a named section.
Publish converts a capture to a Zola post under
`<mylearnbase>/content/posts/logbook/<project>/<slug>.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import _capture, _frontmatter

SECTION_WHAT = "What does this feature do?"
SECTION_WHY = "Why was it added now?"
SECTION_SCOPE = "What's in scope (and what's not)?"
SECTION_EVIDENCE = "How do we know it works?"
SECTION_NEXT = "What's worth remembering or doing next?"


def _repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError("not in a git repository")
    return Path(out.stdout.strip())


def _capture_path(repo_root: Path, slug: str) -> Path:
    return repo_root / "logbook" / "_drafts" / f"{slug}.md"


def _utc_iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").capitalize()


def _capture_template(project: str, slug: str, title: str, timestamp: str) -> str:
    return (
        f"# {title}\n"
        f"*{timestamp}*\n\n"
        f"> Project: {project}\n"
        f"> Slug: {slug}\n"
        f"> Tags: TBD\n\n"
        f"## {SECTION_WHAT}\n\n"
        f"## {SECTION_WHY}\n\n"
        f"## {SECTION_SCOPE}\n\n"
        f"## {SECTION_EVIDENCE}\n\n"
        f"## {SECTION_NEXT}\n\n"
    )


def _read_text_arg(text: str | None) -> str:
    """Return text arg if provided, else read from stdin."""
    if text is not None:
        return text
    if sys.stdin.isatty():
        print("logbook: no text provided; reading from stdin (Ctrl-D to end)...", file=sys.stderr)
    return sys.stdin.read().rstrip("\n")




def _resolve_capture_arg(arg: str) -> Path:
    """Accept either a path (foo.md) or a slug (resolves to logbook/_drafts/<slug>.md)."""
    p = Path(arg)
    if p.suffix == ".md" or "/" in arg:
        return p.resolve()
    return _capture_path(_repo_root(), arg)


def _read_metadata_block(capture: Path) -> dict[str, str]:
    """Extract Project/Slug/Tags from the metadata blockquote at the top."""
    meta: dict[str, str] = {}
    for line in capture.read_text(encoding="utf-8").splitlines():
        if not line.startswith("> "):
            if meta:
                break
            continue
        kv = line[2:]
        if ":" in kv:
            k, _, v = kv.partition(":")
            meta[k.strip().lower()] = v.strip()
    return meta


def _split_metadata_and_body(capture: Path) -> tuple[dict[str, str], str, str]:
    """Return (metadata, title_block, body_after_metadata)."""
    text = capture.read_text(encoding="utf-8")
    lines = text.splitlines()

    meta_start = None
    meta_end = None
    for i, line in enumerate(lines):
        if line.startswith("> ") and meta_start is None:
            meta_start = i
        elif meta_start is not None and not line.startswith("> "):
            meta_end = i
            break
    if meta_start is None:
        raise ValueError(f"no metadata blockquote found in {capture}")
    if meta_end is None:
        meta_end = len(lines)

    meta: dict[str, str] = {}
    for line in lines[meta_start:meta_end]:
        kv = line[2:]
        if ":" in kv:
            k, _, v = kv.partition(":")
            meta[k.strip().lower()] = v.strip()

    title_block = "\n".join(lines[:meta_start]).rstrip()
    body = "\n".join(lines[meta_end:]).strip()
    return meta, title_block, body


def _strip_empty_sections(body: str) -> str:
    """Remove section headers whose body is empty (mainly the optional scope section)."""
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


def _mylearnbase_root() -> Path:
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


def _project_section_template(project: str) -> str:
    """Render an `_index.md` for a per-project logbook sub-section.

    Mirrors the existing `posts/logbook/omni-me/_index.md` shape so the new
    section behaves identically to hand-scaffolded ones.
    """
    title = f"{project} Logbook"
    desc = f"Implementation logs for {project}"
    return (
        "+++\n"
        f'title = "{title}"\n'
        f'description = "{desc}"\n'
        'sort_by = "date"\n'
        'template = "blog.html"\n'
        'page_template = "post.html"\n'
        'insert_anchor_links = "right"\n\n'
        "[extra]\n"
        'lang = "en"\n'
        f'title = "{title}"\n'
        f'subtitle = "{desc}"\n'
        'date_format = "%b %-d, %Y"\n'
        "categorized = false\n"
        "back_to_top = true\n"
        "toc = true\n"
        "comment = false\n"
        "copy = true\n"
        "outdate_alert = true\n"
        "outdate_alert_days = 120\n"
        'outdate_alert_text_before = "This article was last updated "\n'
        'outdate_alert_text_after = " days ago and may be out of date."\n'
        "+++\n"
    )


def _zola_check(content_root: Path) -> tuple[int, str]:
    """Run `zola check` from a Zola site root. Returns (returncode, combined_output)."""
    result = subprocess.run(
        ["zola", "check"],
        cwd=content_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def cmd_init(args: argparse.Namespace) -> int:
    try:
        root = _repo_root()
    except RuntimeError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 2

    slug = args.feature_name
    capture = _capture_path(root, slug)
    if capture.exists() and not args.force:
        print(f"logbook: capture already exists at {capture} (use --force to overwrite)", file=sys.stderr)
        return 1

    capture.parent.mkdir(parents=True, exist_ok=True)
    title = args.title or _title_from_slug(slug)
    capture.write_text(
        _capture_template(args.project, slug, title, _utc_iso_now()),
        encoding="utf-8",
    )
    print(str(capture))
    return 0


def _section_cmd(section_header: str) -> callable:
    def handler(args: argparse.Namespace) -> int:
        capture = _resolve_capture_arg(args.capture_file)
        text = _read_text_arg(args.text)
        if not text.strip():
            print("logbook: refusing to write empty text", file=sys.stderr)
            return 1
        try:
            _capture.append_to_section(capture, section_header, text)
        except (FileNotFoundError, ValueError) as exc:
            print(f"logbook: {exc}", file=sys.stderr)
            return 1
        return 0

    return handler


def cmd_publish(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    try:
        meta, title_block, body = _split_metadata_and_body(capture)
    except ValueError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 1

    project = meta.get("project")
    slug = args.slug or meta.get("slug")
    tags_raw = meta.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip() and t.strip() != "TBD"]

    if not project or not slug:
        print(f"logbook: capture missing Project/Slug metadata: {meta!r}", file=sys.stderr)
        return 1

    title = ""
    for line in title_block.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = _title_from_slug(slug)

    body_clean = _strip_empty_sections(body)

    try:
        mb_root = _mylearnbase_root()
    except RuntimeError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 2

    project_dir = mb_root / "content" / "posts" / "logbook" / project
    dest = project_dir / f"{slug}.md"
    if dest.exists() and not args.force:
        print(f"logbook: destination already exists at {dest} (use --force to overwrite)", file=sys.stderr)
        return 1

    project_index = project_dir / "_index.md"
    project_index_created = False
    if not project_index.exists():
        project_dir.mkdir(parents=True, exist_ok=True)
        project_index.write_text(_project_section_template(project), encoding="utf-8")
        project_index_created = True

    fields: dict[str, object] = {
        "title": title,
        "slug": slug,
        "date": dt.date.today().isoformat(),
        "draft": True,
    }
    if tags:
        fields["taxonomies"] = {"tags": tags}

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("", encoding="utf-8")
    _frontmatter.write(dest, fields)

    with dest.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write(body_clean)
        if not body_clean.endswith("\n"):
            f.write("\n")

    rc, output = _zola_check(mb_root)
    if rc != 0:
        print(f"logbook: zola check failed (rc={rc}):\n{output}", file=sys.stderr)
        return 1

    print(str(dest))
    print(f"  draft = true (review, then flip to false in frontmatter)")
    print(f"  tags = {tags or '(none — fill in frontmatter)'}")
    print(f"  zola check: clean")
    if project_index_created:
        print(f"  created {project_index} (review title/description if desired)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="logbook",
        description="Capture and publish logbook entries (per-feature implementation logs).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{init,what,why,scope,note,publish}")

    p_init = sub.add_parser("init", help="Template a fresh capture file with the 7-section structure.")
    p_init.add_argument("project")
    p_init.add_argument("feature_name", help="Slug for the capture (used as filename and metadata).")
    p_init.add_argument("--title", help="Override the auto-derived title.", default=None)
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing capture.")
    p_init.set_defaults(handler=cmd_init)

    for verb, header in [
        ("what", SECTION_WHAT),
        ("why", SECTION_WHY),
        ("scope", SECTION_SCOPE),
        ("note", SECTION_NEXT),
    ]:
        p = sub.add_parser(verb, help=f"Append text to the '{header}' section.")
        p.add_argument("capture_file", help="Capture path or bare slug (resolves under logbook/_drafts/).")
        p.add_argument("text", nargs="?", help="Text to write (reads from stdin if omitted).")
        p.set_defaults(handler=_section_cmd(header))

    p_pub = sub.add_parser("publish", help="Convert a capture to a Zola post under content/posts/logbook/<project>/.")
    p_pub.add_argument("capture_file", help="Capture path or bare slug.")
    p_pub.add_argument("--slug", help="Override the slug from metadata.", default=None)
    p_pub.add_argument("--force", action="store_true", help="Overwrite the destination if it exists.")
    p_pub.set_defaults(handler=cmd_publish)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
