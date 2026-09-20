#!/usr/bin/env python3
"""Search or retrieve a large shell result parked by the Jev Codex hook."""

from __future__ import annotations

import argparse
import re

from jev_output_store import read_output

MAX_RETURN_CHARS = 16_000


def select_lines(text: str, line_range: str | None, pattern: str | None) -> str:
    lines = text.splitlines()
    if line_range:
        match = re.fullmatch(r"(\d+)-(\d+)", line_range)
        if not match:
            raise ValueError("line range must use START-END")
        start, end = map(int, match.groups())
        if start < 1 or end < start:
            raise ValueError("line range must be positive and ordered")
        selected = [(index, line) for index, line in enumerate(lines, 1) if start <= index <= end]
    elif pattern:
        regex = re.compile(pattern, re.IGNORECASE)
        selected = [(index, line) for index, line in enumerate(lines, 1) if regex.search(line)]
    else:
        selected = list(enumerate(lines, 1))
    rendered = "\n".join(f"{index}: {line}" for index, line in selected)
    if len(rendered) > MAX_RETURN_CHARS:
        rendered = rendered[:MAX_RETURN_CHARS] + "\n[recall output capped; request a narrower range/pattern]"
    return f"matched {len(selected)} of {len(lines)} lines\n{rendered}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="output id shown in the Jev compact-output receipt")
    parser.add_argument("--lines", help="retrieve a one-based inclusive range, e.g. 30-55")
    parser.add_argument("--grep", dest="pattern", help="regex-search the parked output")
    args = parser.parse_args()
    try:
        if not args.id:
            parser.error("--id is required")
        if args.lines and args.pattern:
            parser.error("choose either --lines or --grep")
        print(select_lines(read_output(args.id), args.lines, args.pattern))
    except (OSError, UnicodeError, ValueError, re.error) as error:
        parser.exit(2, f"Jev recall: {type(error).__name__}: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
