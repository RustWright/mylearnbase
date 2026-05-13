"""workflows: sync a source doc to a Zola workflows post.

The tool's job is one-way sync: read a markdown source doc (e.g.,
`PROJECT_PROCESS.md` from a project repo), render frontmatter, escape Zola
shortcodes, and write to `<mylearnbase>/content/posts/workflows/<slug>.md`.
On republish the existing `date` is preserved and `updated` is set to today;
the body is replaced; `taxonomies`/`extra` tables stay intact.

Categories 2 and 3 from the post plan (drafted directly under mylearnbase,
no parallel doc) don't need this tool — the user edits the Zola file
directly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import re
import sys
from pathlib import Path

from . import _frontmatter, _shared


_PRESERVED_KEYS = ("date", "draft", "taxonomies.tags", "extra.outdate_alert_days")


def _slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _extract_title(body: str) -> tuple[str, str]:
    """Return (title, body_with_title_line_removed). Title = first `# `-prefixed line."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            remaining = lines[:i] + lines[i + 1 :]
            while remaining and not remaining[0].strip():
                remaining.pop(0)
            return title, "\n".join(remaining)
    return "", body


def _escape_zola_shortcodes(text: str) -> str:
    """Escape `{{ ... }}` and `{% ... %}` for Zola's shortcode pre-pass.

    Zola interprets shortcodes inside fenced code blocks too, and `{% raw %}`
    does not bypass detection. Escape format per project memory:
        `{{ x }}` -> `{{/* x */}}`
        `{% x %}` -> `{%/* x */%}`

    Lookahead/lookbehind skip already-escaped pairs so re-runs are idempotent.
    """
    text = re.sub(r"\{\{(?!/\*)(.*?)(?<!\*/)\}\}", r"{{/*\1*/}}", text, flags=re.DOTALL)
    text = re.sub(r"\{%(?!/\*)(.*?)(?<!\*/)%\}", r"{%/*\1*/%}", text, flags=re.DOTALL)
    return text


def _build_fields(
    title: str,
    slug: str,
    today: str,
    is_republish: bool,
    draft_flag: bool,
    preserved: dict[str, object],
) -> dict[str, object]:
    if is_republish:
        fields: dict[str, object] = {
            "title": title,
            "slug": slug,
            "date": preserved.get("date", today),
            "updated": today,
            "draft": draft_flag if draft_flag else preserved.get("draft", False),
        }
        if "taxonomies.tags" in preserved:
            fields["taxonomies"] = {"tags": preserved["taxonomies.tags"]}
        if "extra.outdate_alert_days" in preserved:
            fields["extra"] = {"outdate_alert_days": preserved["extra.outdate_alert_days"]}
        return fields
    return {
        "title": title,
        "slug": slug,
        "date": today,
        "draft": draft_flag,
    }


def _render_post(fields: dict[str, object], body: str) -> str:
    """Render the full post text (frontmatter + body)."""
    return _frontmatter.render(fields) + "\n" + body.strip() + "\n"


def cmd_publish(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        print(f"workflows: source doc not found: {source}", file=sys.stderr)
        return 1

    raw = source.read_text(encoding="utf-8")
    title_from_doc, body_without_title = _extract_title(raw)
    title = args.title or title_from_doc
    if not title:
        print(
            f"workflows: could not find a `# Heading` in {source}; pass --title explicitly",
            file=sys.stderr,
        )
        return 1

    auto_slug = _slugify(title)
    final_slug = args.slug or auto_slug
    if not final_slug:
        print(f"workflows: could not derive a slug from {title!r}; pass --slug explicitly", file=sys.stderr)
        return 1

    try:
        mb_root = _shared.mylearnbase_root()
    except RuntimeError as exc:
        print(f"workflows: {exc}", file=sys.stderr)
        return 2

    workflows_dir = mb_root / "content" / "posts" / "workflows"
    dest = workflows_dir / f"{final_slug}.md"

    old_dest: Path | None = None
    if args.supersede_from:
        old_dest = workflows_dir / f"{args.supersede_from}.md"
        if not old_dest.is_file():
            print(f"workflows: no post found to supersede at {old_dest}", file=sys.stderr)
            return 1
        if args.supersede_from == final_slug:
            print(
                "workflows: superseding in place is incoherent; pass a different --slug or "
                "change the source doc's H1 so the auto-slug differs from --supersede-from.",
                file=sys.stderr,
            )
            return 1
        if dest.exists():
            print(
                f"workflows: destination post {dest} already exists; cannot supersede into "
                "an existing post. Delete it first or pick a different --slug.",
                file=sys.stderr,
            )
            return 1
    elif args.slug and args.slug != auto_slug:
        auto_dest = workflows_dir / f"{auto_slug}.md"
        if auto_dest.is_file():
            print(
                f"workflows: an existing post at {auto_dest} would be orphaned by --slug={final_slug!r}. "
                f"Pass --supersede-from {auto_slug} to supersede it, or remove --slug to keep the existing post's slug.",
                file=sys.stderr,
            )
            return 1

    body_escaped = _escape_zola_shortcodes(body_without_title)

    today = dt.date.today().isoformat()
    is_republish = dest.exists() and not args.supersede_from

    preserved: dict[str, object] = {}
    if is_republish:
        preserved = _frontmatter.read_keys(dest, _PRESERVED_KEYS)

    fields = _build_fields(title, final_slug, today, is_republish, args.draft, preserved)
    new_text = _render_post(fields, body_escaped)

    if args.dry_run:
        existing = dest.read_text(encoding="utf-8") if dest.exists() else ""
        diff = "".join(
            difflib.unified_diff(
                existing.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{dest} (current)",
                tofile=f"{dest} (after publish)",
            )
        )
        print(diff or f"(no changes for {dest})")
        if args.supersede_from and old_dest is not None:
            print(f"\n(supersession would also add `extra.superseded_by = \"posts/workflows/{final_slug}.md\"` to {old_dest})")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(new_text, encoding="utf-8")

    images_copied = _shared.copy_referenced_images(body_escaped, source.parent, dest.parent)

    if args.supersede_from and old_dest is not None:
        old_fields = _frontmatter.read_all(old_dest)
        old_fields.setdefault("extra", {})["superseded_by"] = f"posts/workflows/{final_slug}.md"
        _frontmatter.write(old_dest, old_fields)

    rc, output = _shared.zola_check(mb_root, skip_external_links=not args.full_check)
    if rc != 0:
        print(f"workflows: zola check failed (rc={rc}):\n{output}", file=sys.stderr)
        return 1

    check_label = "clean (full)" if args.full_check else "clean (internal links only)"
    if args.supersede_from:
        mode = "published (superseding)"
    elif is_republish:
        mode = "republished"
    else:
        mode = "published"
    print(str(dest))
    print(f"  {mode}: title = {title!r}, slug = {final_slug!r}")
    updated_line = f"  updated = {fields['updated']}" if "updated" in fields else ""
    print(f"  date = {fields['date']}{updated_line}")
    print(f"  draft = {'true' if fields['draft'] else 'false'}")
    if images_copied:
        print(f"  copied images: {', '.join(images_copied)}")
    if args.supersede_from and old_dest is not None:
        print(f"  superseded: {old_dest} now banners → {final_slug}")
    print(f"  zola check: {check_label}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workflows",
        description="Publish or republish workflow posts (sync project-repo docs to mylearnbase).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{publish}")

    p_pub = sub.add_parser("publish", help="Sync a source doc to a Zola workflows post.")
    p_pub.add_argument("source", help="Path to the source markdown doc (e.g., PROJECT_PROCESS.md).")
    p_pub.add_argument("--slug", help="Override the auto-slugified slug.", default=None)
    p_pub.add_argument("--title", help="Override the title from the source doc's H1.", default=None)
    p_pub.add_argument("--draft", action="store_true", help="Publish/republish as draft=true.")
    p_pub.add_argument("--dry-run", action="store_true", help="Print the diff without writing.")
    p_pub.add_argument(
        "--supersede-from",
        dest="supersede_from",
        metavar="OLD_SLUG",
        default=None,
        help="Treat this publish as superseding the post at OLD_SLUG. Writes the new post + adds an `extra.superseded_by` banner to the old post.",
    )
    p_pub.add_argument(
        "--full-check",
        action="store_true",
        help="Run a full `zola check` including external links (slow). Default skips external links.",
    )
    p_pub.set_defaults(handler=cmd_publish)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
