"""cookbook: scaffold (init) and publish (draft -> Zola post) for cookbook entries."""

import argparse
import sys


def _handle_init(args: argparse.Namespace) -> int:
    print(f"[cookbook init stub] slug={args.slug} from_logbook={args.from_logbook}")
    print("Phase 6 will scaffold <project>/cookbook/_drafts/<slug>.md with the 6-section structure.")
    return 0


def _handle_publish(args: argparse.Namespace) -> int:
    print(f"[cookbook publish stub] slug={args.slug}")
    print("Phase 6 will move the draft into mylearnbase/content/posts/cookbook/<slug>.md.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cookbook",
        description="Capture and publish cookbook entries (reusable patterns and principles).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="{init,publish}")

    p_init = sub.add_parser("init", help="Scaffold a new cookbook draft with the 6-section structure.")
    p_init.add_argument("slug")
    p_init.add_argument("--from-logbook", help="Optional: pre-fill section 6 with a back-link to a logbook entry.")
    p_init.set_defaults(handler=_handle_init)

    p_pub = sub.add_parser("publish", help="Move a draft cookbook entry into mylearnbase/content/posts/cookbook/.")
    p_pub.add_argument("slug")
    p_pub.set_defaults(handler=_handle_publish)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
