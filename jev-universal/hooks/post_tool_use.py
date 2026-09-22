#!/usr/bin/env python3
"""Replace oversized, non-sensitive Bash output with a recallable preview."""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from jev_output_store import cleanup_stale, store_output

MIN_BYTES = 4_000
MIN_LINES = 36
PREVIEW_HEAD = 4
PREVIEW_TAIL = 8
MAX_PREVIEW_LINE_CHARS = 320
_FAILURE = re.compile(
    r"(?im)^\s*(?:FAILED|ERROR|FATAL|Traceback|AssertionError|Exception|npm ERR!)\b|"
    r"^.*\b\d+\s+(?:failed|errors?)\b.*$|"
    r"^.*\b(?:failed|errors?)\s*[:=]\s*[1-9]\d*\b.*$"
)
_SECRET = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"\b(?:ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16})\b|"
    r"(?:authorization\s*:\s*bearer|(?:api[_-]?key|access[_-]?token|"
    r"client[_-]?secret|password)\s*[:=])\s*['\"]?[A-Za-z0-9_./+=:-]{16,}"
    , re.IGNORECASE
)
_TEST_COMMAND = re.compile(
    r"(?i)(?:pytest|unittest|cargo\s+test|npm\s+test|pnpm\s+test|yarn\s+test|"
    r"go\s+test|ruff|mypy|eslint|tsc|\bbuild\b|\bcheck\b)"
)
_GO_TEST_FAILURE = re.compile(
    r"(?m)^\s*FAIL(?:\s+\S+)?(?:\s+(?:\d+(?:\.\d+)?s|\[build failed\]))?\s*$"
)


def is_sensitive(text: str) -> bool:
    return bool(_SECRET.search(text))


def should_compact(command: str, text: str) -> bool:
    if len(text.encode("utf-8")) < MIN_BYTES and len(text.splitlines()) < MIN_LINES:
        return False
    if is_sensitive(text):
        return False
    if _TEST_COMMAND.search(command) and (_FAILURE.search(text) or _GO_TEST_FAILURE.search(text)):
        return False
    return True


def _short_line(line: str) -> str:
    if len(line) <= MAX_PREVIEW_LINE_CHARS:
        return line
    half = MAX_PREVIEW_LINE_CHARS // 2
    return f"{line[:half]} … [{len(line)} chars] … {line[-half:]}"


def preview(text: str) -> str:
    lines = text.splitlines()
    if len(lines) <= PREVIEW_HEAD + PREVIEW_TAIL:
        indices = list(range(len(lines)))
    else:
        indices = list(range(PREVIEW_HEAD)) + list(range(len(lines) - PREVIEW_TAIL, len(lines)))
    selected = set(indices)
    rendered = [f"{index + 1}: {_short_line(lines[index])}" for index in indices]
    signals = [
        (index, line)
        for index, line in enumerate(lines)
        if index not in selected and re.search(r"(?i)\b(?:warning|deprecated|skipped)\b", line)
    ][:12]
    if signals:
        rendered.append("Relevant warning/skip lines:")
        rendered.extend(f"{index + 1}: {_short_line(line)}" for index, line in signals)
    omitted = len(lines) - len(indices) - len(signals)
    if omitted > 0:
        rendered.insert(PREVIEW_HEAD, f"… {omitted} lines omitted from preview …")
    return "\n".join(rendered)


def process_event(request: dict, root: Path | None = None) -> dict | None:
    if request.get("tool_name") != "Bash":
        return None
    tool_input = request.get("tool_input")
    response = request.get("tool_response")
    if not isinstance(tool_input, dict) or not isinstance(response, str):
        return None
    command = tool_input.get("command")
    session_id = request.get("session_id")
    if not isinstance(command, str) or not isinstance(session_id, str) or not session_id:
        return None
    try:
        cleanup_stale(root)
    except OSError:
        pass
    if not should_compact(command, response):
        return None
    try:
        output_id, _ = store_output(session_id, response, root)
    except OSError:
        return None
    recall = Path(__file__).resolve().parents[1] / "scripts" / "jev_output_recall.py"
    recall_command = shlex.quote(str(recall))
    reason = (
        "Jev compacted this Bash result; the command has already run.\n"
        f"Original output: {len(response.splitlines())} lines, {len(response)} characters; "
        f"temporary recall id `{output_id}`.\n"
        f"Preview:\n{preview(response)}\n"
        f"Recover exact lines: `python3 {recall_command} --id {output_id} --lines START-END`\n"
        f"Search parked text: `python3 {recall_command} --id {output_id} --grep 'pattern'`. "
        "The output is stored locally for at most one hour, then removed automatically."
    )
    return {"continue": False, "stopReason": reason}


def main() -> int:
    try:
        request = json.load(sys.stdin)
        result = process_event(request)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0
    if result is not None:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
