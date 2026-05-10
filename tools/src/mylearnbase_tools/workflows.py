"""workflows: publish (and republish) workflow posts (prescriptive processes)."""

import argparse
import sys


def _handle_publish(args: argparse.Namespace) -> int:
    print(f"[workflows publish stub] name={args.name} source={args.source}")
    print("Phase 6 will write/replace mylearnbase/content/posts/workflows/<slug>.md, "
          "preserving date on republish and setting `updated = today`.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workflows",
        description="Publish or republish workflow posts (LLM-referenced or post-only).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{publish}")

    p_pub = sub.add_parser("publish", help="Publish or republish a workflow post.")
    p_pub.add_argument("name", help="Workflow slug (used as filename and post identifier).")
    p_pub.add_argument("--source", help="Source markdown file to import.", default=None)
    p_pub.set_defaults(handler=_handle_publish)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
