"""logbook: capture (init/title/tags/exec/screenshot) and publish.

Captures are showboat documents structured into 7 sections (logbook owns the
section discipline; showboat handles title block, exec/image blocks, and
verify). Prose sections are filled by direct-editing the capture file.
Captures live at `<repo-root>/logbook/_drafts/<slug>.md`. Publish converts
a capture to a Zola post under
`<mylearnbase>/content/posts/logbook/<project>/<slug>/index.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

from . import _capture, _frontmatter, _shared

SECTION_WHAT = "What does this feature do?"
SECTION_WHY = "Why was it added now?"
SECTION_SCOPE = "What's in scope (and what's not)?"
SECTION_EVIDENCE = "How do we know it works?"
SECTION_NEXT = "What's worth remembering or doing next?"

REQUIRED_SECTIONS = [SECTION_WHAT, SECTION_WHY, SECTION_EVIDENCE]


def _capture_path(repo_root: Path, slug: str) -> Path:
    return repo_root / "logbook" / "_drafts" / f"{slug}.md"


def _title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").capitalize()


def _post_init_additions(project: str, slug: str) -> str:
    """Metadata blockquote + 7 empty section headers, appended after `showboat init`."""
    return (
        "\n"
        f"> Project: {project}\n"
        f"> Slug: {slug}\n"
        f"> Tags: TBD\n\n"
        f"## {SECTION_WHAT}\n\n"
        f"## {SECTION_WHY}\n\n"
        f"## {SECTION_SCOPE}\n\n"
        f"## {SECTION_EVIDENCE}\n\n"
        f"## {SECTION_NEXT}\n\n"
    )


def _resolve_capture_arg(arg: str) -> Path:
    """Accept either a path (foo.md) or a slug (resolves to logbook/_drafts/<slug>.md)."""
    p = Path(arg)
    if p.suffix == ".md" or "/" in arg:
        return p.resolve()
    return _capture_path(_shared.repo_root(), arg)


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
        'insert_anchor_links = "right"\n'
        'transparent = true\n\n'
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


def cmd_init(args: argparse.Namespace) -> int:
    try:
        root = _shared.repo_root()
    except RuntimeError as err:
        print(f"logbook: {err}", file=sys.stderr)
        return 2

    slug = args.feature_name
    capture = _capture_path(root, slug)
    if capture.exists() and not args.force:
        print(f"logbook: capture already exists at {capture} (use --force to overwrite)", file=sys.stderr)
        return 1

    capture.parent.mkdir(parents=True, exist_ok=True)
    if capture.exists():
        capture.unlink()
    title = args.title

    try:
        result = _shared.run_showboat(["init", str(capture), title])
    except RuntimeError as err:
        print(f"logbook: {err}", file=sys.stderr)
        return 2
    if result.returncode != 0:
        print(f"logbook: showboat init failed: {result.stderr.strip()}", file=sys.stderr)
        return 1

    with capture.open("a", encoding="utf-8") as f:
        f.write(_post_init_additions(args.project, slug))

    print(str(capture))
    print(f"  title: {title}")
    return 0


def _relocate_appended_to_section(capture: Path, pre_line_count: int, target_section: str) -> int:
    """Move newly-appended lines (everything after `pre_line_count`) into `target_section`.

    Used after invoking a showboat command that appends to end-of-file. Returns
    0 on success, nonzero on failure.
    """
    text = capture.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) <= pre_line_count:
        print("logbook: showboat command produced no new content", file=sys.stderr)
        return 1

    appended = lines[pre_line_count:]
    while appended and not appended[0].strip():
        appended.pop(0)
    while appended and not appended[-1].strip():
        appended.pop()

    if not appended:
        print("logbook: showboat command appended only blank lines", file=sys.stderr)
        return 1

    pre_lines = lines[:pre_line_count]
    while pre_lines and not pre_lines[-1].strip():
        pre_lines.pop()
    capture.write_text("\n".join(pre_lines) + "\n", encoding="utf-8")

    section_block = "\n".join(appended)
    try:
        _capture.append_to_section(capture, target_section, section_block)
    except (FileNotFoundError, ValueError) as err:
        print(f"logbook: {err}", file=sys.stderr)
        return 1
    return 0


_CARGO_NOISE_RE = re.compile(r"^\s*(Compiling|Finished|Running unittests|warning:|\s+--> )")


def _strip_cargo_noise_from_appended(capture: Path, pre_line_count: int) -> None:
    """Drop cargo's compile/finished noise from the just-appended output fence.

    Targets the lines between ``` ```output ``` and its closing ``` ``` ``` that
    were just written by `showboat exec`. Compile-time and warning lines vary
    between runs and break `showboat verify`'s exact-match diffing; the test
    results themselves are deterministic and worth keeping.
    """
    lines = capture.read_text(encoding="utf-8").splitlines()
    appended = lines[pre_line_count:]
    in_output = False
    cleaned: list[str] = []
    for line in appended:
        if line.startswith("```output"):
            in_output = True
            cleaned.append(line)
            continue
        if in_output and line.startswith("```"):
            in_output = False
            cleaned.append(line)
            continue
        if in_output and _CARGO_NOISE_RE.match(line):
            continue
        cleaned.append(line)
    new_lines = lines[:pre_line_count] + cleaned
    text = "\n".join(new_lines)
    original = capture.read_text(encoding="utf-8")
    capture.write_text(text + ("\n" if original.endswith("\n") else ""), encoding="utf-8")


def cmd_run(args: argparse.Namespace) -> int:
    """Run a code block via showboat and embed it into the target section."""
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    pre_line_count = len(capture.read_text(encoding="utf-8").splitlines())
    code = args.code if args.code is not None else _shared.read_text_arg(None)
    if not code.strip():
        print("logbook: refusing to run empty code", file=sys.stderr)
        return 1

    try:
        result = _shared.run_showboat(["exec", str(capture), args.lang, code])
    except RuntimeError as err:
        print(f"logbook: {err}", file=sys.stderr)
        return 2

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if args.strip_cargo_noise:
        _strip_cargo_noise_from_appended(capture, pre_line_count)

    target = args.section or SECTION_EVIDENCE
    relocate_rc = _relocate_appended_to_section(capture, pre_line_count, target)
    if relocate_rc != 0:
        return relocate_rc
    return result.returncode


def cmd_screenshot(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    image_path = Path(args.path).expanduser()
    if not image_path.is_file():
        print(f"logbook: image not found: {image_path}", file=sys.stderr)
        return 1

    pre_line_count = len(capture.read_text(encoding="utf-8").splitlines())

    try:
        result = _shared.run_showboat(["image", str(capture), str(image_path)])
    except RuntimeError as err:
        print(f"logbook: {err}", file=sys.stderr)
        return 2
    if result.returncode != 0:
        print(f"logbook: showboat image failed: {result.stderr.strip()}", file=sys.stderr)
        return 1

    target = args.section or SECTION_EVIDENCE
    return _relocate_appended_to_section(capture, pre_line_count, target)


def cmd_title(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    text = capture.read_text(encoding="utf-8")
    new_h1 = f"# {args.title}"
    new_lines: list[str] = []
    replaced = False
    for line in text.splitlines():
        if not replaced and line.startswith("# "):
            new_lines.append(new_h1)
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        print("logbook: capture has no `# ` title line", file=sys.stderr)
        return 1

    capture.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    print(new_h1)
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
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
        print(f"logbook: capture has no `> Tags:` line in metadata blockquote", file=sys.stderr)
        return 1

    capture.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    print(new_line)
    return 0


_CROSSPOST_LINK_RE = re.compile(r"@/(posts/[^)\s\"#]+)")


def _normalize_crosspost_links(body: str, mb_root: Path) -> tuple[str, list[str], list[str]]:
    """Normalize `@/posts/...` refs to whichever shape the destination actually uses.

    Zola is strict: a `<slug>.md` ref doesn't match a `<slug>/index.md` target
    or vice-versa. Authors shouldn't have to track which prior posts have been
    bundle-restructured. This walks every `@/posts/...` ref and rewrites it to
    whichever of the two shapes resolves on disk.

    Returns (rewritten_body, rewrites, unresolved):
      - rewrites: list of "old → new" strings for stdout
      - unresolved: list of refs that didn't match either shape (for stderr warnings)
    """
    content_root = mb_root / "content"
    rewrites: list[str] = []
    unresolved: list[str] = []
    seen_unresolved: set[str] = set()

    def _replace(match: re.Match) -> str:
        ref = match.group(1)
        target = content_root / ref
        if target.is_file():
            return match.group(0)
        if ref.endswith(".md"):
            bundle_ref = f"{ref[:-3]}/index.md"
            if (content_root / bundle_ref).is_file():
                rewrites.append(f"@/{ref} → @/{bundle_ref}")
                return f"@/{bundle_ref}"
        elif ref.endswith("/index.md"):
            flat_ref = f"{ref[:-len('/index.md')]}.md"
            if (content_root / flat_ref).is_file():
                rewrites.append(f"@/{ref} → @/{flat_ref}")
                return f"@/{flat_ref}"
        if ref not in seen_unresolved:
            seen_unresolved.add(ref)
            unresolved.append(f"@/{ref}")
        return match.group(0)

    return _CROSSPOST_LINK_RE.sub(_replace, body), rewrites, unresolved


def cmd_publish(args: argparse.Namespace) -> int:
    capture = _resolve_capture_arg(args.capture_file)
    if not capture.exists():
        print(f"logbook: capture does not exist: {capture}", file=sys.stderr)
        return 1

    if not args.skip_verify:
        try:
            verify_result = _shared.run_showboat(["verify", str(capture)])
        except RuntimeError as err:
            print(f"logbook: {err}", file=sys.stderr)
            return 2
        if verify_result.returncode != 0:
            output = (verify_result.stdout + verify_result.stderr).strip()
            print(f"logbook: showboat verify failed (rc={verify_result.returncode}):\n{output}", file=sys.stderr)
            return 1

    try:
        meta, title_block, body = _split_metadata_and_body(capture)
    except ValueError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 1

    project = meta.get("project")
    slug = args.slug or meta.get("slug")
    if args.tags is not None:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    else:
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

    try:
        body_clean = _shared.strip_empty_sections(body, required_headers=REQUIRED_SECTIONS)
    except ValueError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 1

    try:
        mb_root = _shared.mylearnbase_root()
    except RuntimeError as exc:
        print(f"logbook: {exc}", file=sys.stderr)
        return 2

    project_dir = mb_root / "content" / "posts" / "logbook" / project
    slug_dir = project_dir / slug
    dest = slug_dir / "index.md"
    if dest.exists() and not args.force:
        print(f"logbook: destination already exists at {dest} (use --force to overwrite)", file=sys.stderr)
        return 1

    is_republish = dest.exists()
    preserved: dict[str, object] = {}
    if is_republish:
        preserved = _frontmatter.read_keys(dest, ("date", "draft"))

    project_index = project_dir / "_index.md"
    project_index_created = False
    if not project_index.exists():
        project_dir.mkdir(parents=True, exist_ok=True)
        project_index.write_text(_project_section_template(project), encoding="utf-8")
        project_index_created = True

    today = dt.date.today().isoformat()
    fields: dict[str, object] = {
        "title": title,
        "slug": slug,
        "date": preserved.get("date", today),
        "draft": preserved.get("draft", True),
    }
    if is_republish:
        fields["updated"] = today
    if tags:
        fields["taxonomies"] = {"tags": tags}

    slug_dir.mkdir(parents=True, exist_ok=True)
    body_with_images, images_copied = _shared.copy_and_rewrite_referenced_images(
        body_clean, capture.parent, slug_dir
    )
    body_rewritten, link_rewrites, unresolved_links = _normalize_crosspost_links(
        body_with_images, mb_root
    )

    dest.write_text("", encoding="utf-8")
    _frontmatter.write(dest, fields)

    with dest.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write(body_rewritten)
        if not body_rewritten.endswith("\n"):
            f.write("\n")

    rc, output = _shared.zola_check(mb_root, skip_external_links=not args.full_check)
    if rc != 0:
        print(f"logbook: zola check failed (rc={rc}):\n{output}", file=sys.stderr)
        return 1

    check_label = "clean (full)" if args.full_check else "clean (internal links only)"
    verify_label = "skipped" if args.skip_verify else "clean"
    print(str(dest))
    if is_republish:
        print(f"  republished: date = {fields['date']}, updated = {today}, draft = {fields['draft']}")
    else:
        print(f"  draft = true (review, then flip to false in frontmatter)")
    print(f"  tags = {tags or '(none — pass --tags or edit frontmatter)'}")
    print(f"  showboat verify: {verify_label}")
    print(f"  zola check: {check_label}")
    if images_copied:
        print(f"  copied {len(images_copied)} image(s): {', '.join(images_copied)}")
    if project_index_created:
        print(f"  created {project_index} (review title/description if desired)")
    for rewrite in link_rewrites:
        print(f"  normalized cross-post link: {rewrite}")
    for link in unresolved_links:
        print(f"  warning: unresolved cross-post link {link!r} (no matching .md or /index.md under content/)", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="logbook",
        description="Capture and publish logbook entries (per-feature implementation logs).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{init,title,tags,exec,screenshot,publish}")

    p_init = sub.add_parser("init", help="Template a fresh capture file with the 7-section structure.")
    p_init.add_argument("project")
    p_init.add_argument("feature_name", help="Slug for the capture (used as filename and metadata).")
    p_init.add_argument("--title", required=True, help="Post title; must read as a real phrase, not a slug fragment.")
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing capture.")
    p_init.set_defaults(handler=cmd_init)

    p_run = sub.add_parser("exec", help="Run code via showboat and embed it as runnable evidence in the target section (default: section 6).")
    p_run.add_argument("capture_file", help="Capture path or bare slug.")
    p_run.add_argument("lang", help="Language identifier (bash, python, etc.) — passed through to showboat.")
    p_run.add_argument("code", nargs="?", help="Code to run (reads from stdin if omitted).")
    p_run.add_argument("--section", help="Target section header text (default: 'How do we know it works?').", default=None)
    p_run.add_argument(
        "--strip-cargo-noise",
        action="store_true",
        help="Drop Compiling/Finished/Running-unittests/warning lines from the captured output. Use with `cargo test` execs so `showboat verify` stops failing on cache-state noise.",
    )
    p_run.set_defaults(handler=cmd_run)

    p_shot = sub.add_parser("screenshot", help="Embed an existing image file via showboat into the target section (default: section 6).")
    p_shot.add_argument("capture_file", help="Capture path or bare slug.")
    p_shot.add_argument("path", help="Path to an existing image file.")
    p_shot.add_argument("--section", help="Target section header text (default: 'How do we know it works?').", default=None)
    p_shot.set_defaults(handler=cmd_screenshot)

    p_pub = sub.add_parser("publish", help="Convert a capture to a Zola post under content/posts/logbook/<project>/.")
    p_pub.add_argument("capture_file", help="Capture path or bare slug.")
    p_pub.add_argument("--slug", help="Override the slug from metadata.", default=None)
    p_pub.add_argument("--tags", help="Comma-separated tags; overrides the capture's metadata blockquote.", default=None)
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
    p_tags.add_argument("tags", help='Comma-separated tags (e.g., "rust, dioxus, ui").')
    p_tags.set_defaults(handler=cmd_tags)

    p_title = sub.add_parser("title", help="Rewrite the title (`# ` line) in a capture.")
    p_title.add_argument("capture_file", help="Capture path or bare slug.")
    p_title.add_argument("title", help="New title text (no leading `# `).")
    p_title.set_defaults(handler=cmd_title)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
