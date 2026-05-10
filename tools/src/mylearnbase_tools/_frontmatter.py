"""Hand-rolled TOML frontmatter helpers.

Python 3.10 has no `tomllib`, and the project deliberately avoids external
deps (see POST_SYSTEM_PLAN). The cross-form frontmatter schema is flat and
known, so a line-based reader/writer covers what the tools need.

Frontmatter blocks are TOML, delimited by `+++` lines (Zola convention).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Sequence

DELIMITER = "+++"


def _extract_block(text: str) -> list[str]:
    """Return the lines of the frontmatter block (between the first two `+++`).

    Raises ValueError if the file does not begin with a frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != DELIMITER:
        raise ValueError("file does not begin with a `+++` frontmatter delimiter")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == DELIMITER:
            end = i
            break
    if end is None:
        raise ValueError("frontmatter block is not closed (missing trailing `+++`)")
    return lines[1:end]


def _parse_value(raw: str) -> Any:
    """Best-effort scalar parse of a TOML right-hand-side.

    Supports: quoted strings, bools, integers, bare dates (YYYY-MM-DD),
    and inline string arrays. Anything else falls through as the raw string.
    """
    s = raw.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    if s.lstrip("-").isdigit():
        return int(s)
    if len(s) == 10 and s[4] == "-" and s[7] == "-" and s.replace("-", "").isdigit():
        return s
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        items: list[Any] = []
        for item in _split_array(inner):
            items.append(_parse_value(item))
        return items
    return s


def _split_array(inner: str) -> list[str]:
    """Split a comma-separated TOML-array body, respecting quoted strings."""
    items: list[str] = []
    buf: list[str] = []
    in_quote: str | None = None
    for ch in inner:
        if in_quote:
            buf.append(ch)
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        items.append("".join(buf))
    return [i.strip() for i in items if i.strip()]


def read_keys(path: Path | str, keys: Sequence[str]) -> dict[str, Any]:
    """Extract specific keys from a frontmatter block.

    Keys may be top-level (`"title"`) or dotted to address a table
    (`"extra.outdate_alert_days"`, `"taxonomies.tags"`).

    Missing keys are simply absent from the result; the caller checks with
    `key in result` rather than relying on a sentinel.
    """
    text = Path(path).read_text(encoding="utf-8")
    lines = _extract_block(text)

    current_table = ""
    parsed: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current_table = stripped[1:-1].strip()
            continue
        if "=" not in stripped:
            continue
        key, _, raw_val = stripped.partition("=")
        key = key.strip()
        full_key = f"{current_table}.{key}" if current_table else key
        parsed[full_key] = _parse_value(raw_val)

    requested: dict[str, Any] = {}
    for k in keys:
        if k in parsed:
            requested[k] = parsed[k]
    return requested


def _format_value(value: Any) -> str:
    """Render a Python value as TOML right-hand-side text."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        if len(value) == 10 and value[4] == "-" and value[7] == "-" and value.replace("-", "").isdigit():
            return value
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        return "[" + ", ".join(_format_value(v) for v in value) + "]"
    raise TypeError(f"unsupported frontmatter value type: {type(value).__name__}")


_TOP_LEVEL_ORDER = ("title", "slug", "date", "updated", "draft")


def render(fields: dict[str, Any]) -> str:
    """Render `fields` as a `+++`-delimited TOML frontmatter block (no body).

    Top-level keys render in `_TOP_LEVEL_ORDER`; convention-tables
    (`taxonomies`, `extra`) follow in that order; other dict-valued keys
    after those. The returned string ends with a trailing newline.
    """
    out: list[str] = [DELIMITER]

    for k in _TOP_LEVEL_ORDER:
        if k in fields and not isinstance(fields[k], dict):
            out.append(f"{k} = {_format_value(fields[k])}")
    for k, v in fields.items():
        if k in _TOP_LEVEL_ORDER or isinstance(v, dict):
            continue
        out.append(f"{k} = {_format_value(v)}")

    for table_name in ("taxonomies", "extra"):
        if table_name in fields and isinstance(fields[table_name], dict):
            out.append("")
            out.append(f"[{table_name}]")
            for k, v in fields[table_name].items():
                out.append(f"{k} = {_format_value(v)}")

    for k, v in fields.items():
        if k in ("taxonomies", "extra") or not isinstance(v, dict):
            continue
        out.append("")
        out.append(f"[{k}]")
        for sub_k, sub_v in v.items():
            out.append(f"{sub_k} = {_format_value(sub_v)}")

    out.append(DELIMITER)
    return "\n".join(out) + "\n"


def write(path: Path | str, fields: dict[str, Any]) -> None:
    """Render fresh frontmatter and write it (plus any existing body) to `path`.

    `fields` is a nested dict:
        {
            "title": "...", "slug": "...", "date": "2026-05-09",
            "draft": False,
            "taxonomies": {"tags": [...], "series": [...]},
            "extra": {"series_order": 1, "outdate_alert_days": 120},
        }
    """
    p = Path(path)
    body = ""
    if p.exists():
        try:
            existing_text = p.read_text(encoding="utf-8")
            existing_lines = _extract_block(existing_text)
            after = existing_text.splitlines()[len(existing_lines) + 2:]
            body = "\n".join(after)
            if existing_text.endswith("\n") and not body.endswith("\n"):
                body += "\n"
        except ValueError:
            body = ""

    rendered = render(fields)
    if body:
        rendered += body
    p.write_text(rendered, encoding="utf-8")
