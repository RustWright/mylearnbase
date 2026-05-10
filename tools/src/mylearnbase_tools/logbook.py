"""logbook: capture (init/what/why/scope/note) and publish (capture -> Zola post)."""

import argparse
import sys


def _add_init(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="Template a fresh capture file with the 7-section structure.")
    p.add_argument("project")
    p.add_argument("feature_name")
    p.set_defaults(handler=_handle_init)


def _add_section_writer(sub: argparse._SubParsersAction, name: str, section_label: str) -> None:
    p = sub.add_parser(name, help=f"Fill the '{section_label}' section of an existing capture.")
    p.add_argument("capture_file")
    p.add_argument("text", nargs="?", help="Text to write (reads from stdin if omitted).")
    p.set_defaults(handler=lambda args: _handle_section_writer(name, args))


def _add_publish(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("publish", help="Convert a capture file to a Zola post under content/posts/logbook/<project>/.")
    p.add_argument("capture_file")
    p.add_argument("--slug", help="Override the inferred slug.")
    p.set_defaults(handler=_handle_publish)


def _handle_init(args: argparse.Namespace) -> int:
    print(f"[logbook init stub] project={args.project} feature={args.feature_name}")
    print("Phase 4 will template a fresh capture file with the 7-section structure.")
    return 0


def _handle_section_writer(section: str, args: argparse.Namespace) -> int:
    print(f"[logbook {section} stub] capture_file={args.capture_file} text={args.text!r}")
    print(f"Phase 4 will fill the '{section}' section of the capture file.")
    return 0


def _handle_publish(args: argparse.Namespace) -> int:
    print(f"[logbook publish stub] capture_file={args.capture_file} slug={args.slug}")
    print("Phase 4 will convert the capture into a Zola post under content/posts/logbook/<project>/.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="logbook",
        description="Capture and publish logbook entries (per-feature implementation logs).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{init,what,why,scope,note,publish}")

    _add_init(sub)
    _add_section_writer(sub, "what", "What does this feature do?")
    _add_section_writer(sub, "why", "Why was it added now?")
    _add_section_writer(sub, "scope", "What's in scope (and what's not)?")
    _add_section_writer(sub, "note", "What's worth remembering or doing next?")
    _add_publish(sub)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
