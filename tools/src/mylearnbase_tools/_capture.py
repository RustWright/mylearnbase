"""Capture-file manipulation primitives shared by logbook/cookbook/workflows.

Captures are markdown files structured with `## <header>` sections. These
helpers append text into a named section without disturbing surrounding
structure.
"""

from __future__ import annotations

from pathlib import Path


def append_to_section(file: Path, section_header: str, text: str) -> None:
    """Append `text` after the existing content of `## {section_header}`.

    Raises FileNotFoundError if `file` doesn't exist.
    Raises ValueError if the section header is not present.
    """
    if not file.exists():
        raise FileNotFoundError(f"capture file does not exist: {file}")

    content = file.read_text(encoding="utf-8")
    lines = content.splitlines()
    target = f"## {section_header}"

    section_start = None
    for i, line in enumerate(lines):
        if line.strip() == target:
            section_start = i
            break
    if section_start is None:
        raise ValueError(f"section not found in {file}: {target!r}")

    section_end = len(lines)
    for j in range(section_start + 1, len(lines)):
        if lines[j].startswith("## "):
            section_end = j
            break

    body_start = section_start + 1
    while body_start < section_end and not lines[body_start].strip():
        body_start += 1
    body_end = section_end
    while body_end > body_start and not lines[body_end - 1].strip():
        body_end -= 1

    has_existing = body_end > body_start
    insertion = ["", text] if has_existing else [text]

    new_lines = lines[:body_end] + insertion + [""] + lines[section_end:]
    file.write_text(
        "\n".join(new_lines) + ("\n" if content.endswith("\n") else ""),
        encoding="utf-8",
    )
