"""cookbook: scaffold (init) and publish (draft -> Zola post) for cookbook entries.

Captures live at `<repo-root>/cookbook/_drafts/<slug>.md` and are showboat
documents structured into 6 sections (cookbook owns the section discipline).
Publish converts a capture to a Zola post under
`<mylearnbase>/content/posts/cookbook/<slug>.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

from . import _frontmatter, _shared


SECTION_SITUATION = "The situation"
SECTION_PATTERN = "The pattern"
SECTION_WHY_IT_WORKS = "Why it works"
SECTION_BREAKS_DOWN = "When this breaks down"
SECTION_SHOWS_UP = "Where it shows up"

_OPTIONAL_SECTIONS = (SECTION_BREAKS_DOWN, SECTION_SHOWS_UP)


def _slugify(title: str) -> str:
    """Best-effort slug from a title. Lowercase, non-alnum → '-', collapse, strip."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _capture_path(repo_root: Path, slug: str) -> Path:
    return repo_root / "cookbook" / "_drafts" / f"{slug}.md"


def _resolve_capture_arg(arg: str) -> Path:
    p = Path(arg)
    if p.suffix == ".md" or "/" in arg:
        return p.resolve()
    return _capture_path(_shared.repo_root(), arg)


def _from_logbook_line(value: str) -> str:
    """Render the backlink placeholder for `--from-logbook`. Real link if PROJECT/SLUG, else TODO."""
    if "/" in value:
        label = value.split("/", 1)[1]
        return f"- Originating logbook: [`{label}`](@/posts/logbook/{value}.md)"
    return f"- Originating logbook: TODO link (slug: `{value}`)"


def _post_init_additions(slug: str, summary_placeholder: str, from_logbook: str | None) -> str:
    """Metadata blockquote + summary blockquote + 5 empty section headers."""
    meta = [
        f"> Slug: {slug}",
        f"> Tags: TBD",
    ]
    if from_logbook:
        meta.append(f"> From-logbook: {from_logbook}")
    section_6_body = "\n" + _from_logbook_line(from_logbook) + "\n" if from_logbook else ""
    return (
        "\n"
        + "\n".join(meta) + "\n\n"
        + f"> {summary_placeholder}\n\n"
        + f"## {SECTION_SITUATION}\n\n"
        + f"## {SECTION_PATTERN}\n\n"
        + f"## {SECTION_WHY_IT_WORKS}\n\n"
        + f"## {SECTION_BREAKS_DOWN}\n\n"
        + f"## {SECTION_SHOWS_UP}\n"
        + section_6_body
        + "\n"
    )


def _split_metadata_and_body(capture: Path) -> tuple[dict[str, str], str, str]:
    """Return (metadata_dict, title_block, body_after_metadata).

    Metadata blockquote = the first contiguous `> ` block. Anything after the
    blockquote (including a follow-on summary blockquote) is body.
    """
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


def cmd_init(args: argparse.Namespace) -> int:
    try:
        root = _shared.repo_root()
    except RuntimeError as err:
        print(f"cookbook: {err}", file=sys.stderr)
        return 2

    title = args.title.strip()
    if not title:
        print("cookbook: title cannot be empty", file=sys.stderr)
        return 1

    slug = args.slug or _slugify(title)
    if not slug:
        print(f"cookbook: could not derive a slug from {title!r}; pass --slug explicitly", file=sys.stderr)
        return 1

    capture = _capture_path(root, slug)
    if capture.exists() and not args.force:
        print(f"cookbook: capture already exists at {capture} (use --force to overwrite)", file=sys.stderr)
        return 1

    capture.parent.mkdir(parents=True, exist_ok=True)
    if capture.exists():
        capture.unlink()

    try:
        result = _shared.run_showboat(["init", str(capture), title])
    except RuntimeError as err:
        print(f"cookbook: {err}", file=sys.stderr)
        return 2
    if result.returncode != 0:
        print(f"cookbook: showboat init failed: {result.stderr.strip()}", file=sys.stderr)
        return 1

    summary_placeholder = "One-line summary of the pattern goes here (replace this blockquote)."
    with capture.open("a", encoding="utf-8") as f:
        f.write(_post_init_additions(slug, summary_placeholder, args.from_logbook))

    print(str(capture))
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"cookbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    if not args.skip_verify:
        try:
            verify_result = _shared.run_showboat(["verify", str(capture)])
        except RuntimeError as err:
            print(f"cookbook: {err}", file=sys.stderr)
            return 2
        if verify_result.returncode != 0:
            output = (verify_result.stdout + verify_result.stderr).strip()
            print(f"cookbook: showboat verify failed (rc={verify_result.returncode}):\n{output}", file=sys.stderr)
            return 1

    try:
        meta, title_block, body = _split_metadata_and_body(capture)
    except ValueError as exc:
        print(f"cookbook: {exc}", file=sys.stderr)
        return 1

    slug = args.slug or meta.get("slug")
    if not slug:
        print(f"cookbook: capture missing Slug metadata: {meta!r}", file=sys.stderr)
        return 1

    if args.tags is not None:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    else:
        tags_raw = meta.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip() and t.strip() != "TBD"]

    title = ""
    for line in title_block.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        print(f"cookbook: capture missing title line in {capture}", file=sys.stderr)
        return 1

    body_clean = _shared.strip_empty_sections(body)

    try:
        mb_root = _shared.mylearnbase_root()
    except RuntimeError as exc:
        print(f"cookbook: {exc}", file=sys.stderr)
        return 2

    dest = mb_root / "content" / "posts" / "cookbook" / f"{slug}.md"
    if dest.exists() and not args.force:
        print(f"cookbook: destination already exists at {dest} (use --force to overwrite)", file=sys.stderr)
        return 1

    fields: dict[str, object] = {
        "title": title,
        "slug": slug,
        "date": dt.date.today().isoformat(),
        "draft": args.draft,
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

    images_copied = _shared.copy_referenced_images(body_clean, capture.parent, dest.parent)

    rc, output = _shared.zola_check(mb_root, skip_external_links=not args.full_check)
    if rc != 0:
        print(f"cookbook: zola check failed (rc={rc}):\n{output}", file=sys.stderr)
        return 1

    check_label = "clean (full)" if args.full_check else "clean (internal links only)"
    verify_label = "skipped" if args.skip_verify else "clean"
    draft_label = "true (review, then flip to false in frontmatter)" if args.draft else "false (live on next deploy)"
    print(str(dest))
    print(f"  draft = {draft_label}")
    print(f"  tags = {tags or '(none — pass --tags or edit frontmatter)'}")
    print(f"  showboat verify: {verify_label}")
    print(f"  zola check: {check_label}")
    if images_copied:
        print(f"  copied {len(images_copied)} image(s): {', '.join(images_copied)}")
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"cookbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    text = capture.read_text(encoding="utf-8")
    new_line = f"> Tags: {args.tags}"
    new_lines: list[str] = []
    replaced = False
    for line in text.splitlines():
        if not replaced and line.startswith("> Tags:"):
            new_lines.append(new_line)
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        print("cookbook: capture has no `> Tags:` line in metadata blockquote", file=sys.stderr)
        return 1

    capture.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    print(new_line)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cookbook",
        description="Capture and publish cookbook entries (reusable patterns and principles).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{init,publish,tags}")

    p_init = sub.add_parser("init", help="Scaffold a new cookbook draft with the 6-section structure.")
    p_init.add_argument("title", help='Human-readable title (e.g., "Wrap existing tools").')
    p_init.add_argument("--slug", help="Override the auto-slugified slug.", default=None)
    p_init.add_argument(
        "--from-logbook",
        help="Pre-fill section 6 with a back-link. Accepts PROJECT/SLUG (real link) or just SLUG (TODO placeholder).",
        default=None,
    )
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing capture.")
    p_init.set_defaults(handler=cmd_init)

    p_pub = sub.add_parser("publish", help="Convert a capture to a Zola post under content/posts/cookbook/.")
    p_pub.add_argument("capture_file", help="Capture path or bare slug (resolves under cookbook/_drafts/).")
    p_pub.add_argument("--slug", help="Override the slug from metadata.", default=None)
    p_pub.add_argument("--tags", help="Comma-separated tags; overrides the capture's metadata blockquote.", default=None)
    p_pub.add_argument("--draft", action="store_true", help="Publish as draft=true (opt-in review). Default: draft=false (live).")
    p_pub.add_argument("--force", action="store_true", help="Overwrite the destination if it exists.")
    p_pub.add_argument(
        "--full-check",
        action="store_true",
        help="Run a full `zola check` including external links (slow). Default skips external links.",
    )
    p_pub.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip the `showboat verify` pre-check that re-runs embedded exec blocks.",
    )
    p_pub.set_defaults(handler=cmd_publish)

    p_tags = sub.add_parser("tags", help="Update the Tags line in a capture's metadata blockquote.")
    p_tags.add_argument("capture_file", help="Capture path or bare slug.")
    p_tags.add_argument("tags", help='Comma-separated tags (e.g., "pattern, llm, prose").')
    p_tags.set_defaults(handler=cmd_tags)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
