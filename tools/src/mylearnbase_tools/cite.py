"""cite: capture file:line + line content + HEAD SHA + GitHub permalink.

Form-agnostic. Discovers project context from cwd + `git remote get-url origin`,
so it runs from any project repo, not just mylearnbase.
"""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cite",
        description="Capture a code citation (file:line + commit-SHA permalink) into a capture file.",
    )
    parser.add_argument("capture_file", help="Path to the capture file to append to.")
    parser.add_argument("ref", help="Code reference in the form <path>:<line> (e.g. src/foo.rs:42).")
    parser.add_argument("--note", help="Optional inline commentary to attach to the citation.", default=None)
    args = parser.parse_args(argv)

    print(f"[cite stub] capture_file={args.capture_file} ref={args.ref} note={args.note}")
    print("Phase 4 will implement the actual capture logic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
