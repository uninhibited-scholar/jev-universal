#!/usr/bin/env python3
"""Print privacy-preserving token and tool summaries from coding-agent traces."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        records = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Some CLIs mix human-readable diagnostics onto the JSONL stream.
                continue
    else:
        records = [json.loads(text)]
    return [record for record in records if isinstance(record, dict)]


def summarize(records: list[dict[str, Any]], model_override: str | None = None) -> dict[str, Any]:
    codex_turns = [
        record
        for record in records
        if record.get("type") == "turn.completed" and isinstance(record.get("usage"), dict)
    ]
    if codex_turns:
        usage_events = [record["usage"] for record in codex_turns]
        input_tokens = sum(int(usage.get("input_tokens", 0) or 0) for usage in usage_events)
        cached_input = sum(
            int(usage.get("cached_input_tokens", 0) or 0) for usage in usage_events
        )
        output_tokens = sum(int(usage.get("output_tokens", 0) or 0) for usage in usage_events)
        reasoning_tokens = sum(
            int(usage.get("reasoning_output_tokens", 0) or 0) for usage in usage_events
        )
        actions: Counter[str] = Counter(
            str((record.get("item") or {}).get("type", "unknown"))
            for record in records
            if record.get("type") == "item.started"
            and (record.get("item") or {}).get("type") != "agent_message"
        )
        return {
            "format": "codex-cli-jsonl",
            "model": model_override,
            "input_tokens": input_tokens,
            "cached_input_tokens_subset": cached_input,
            "output_tokens": output_tokens,
            "reasoning_output_tokens_subset": reasoning_tokens,
            "total_tokens": input_tokens + output_tokens,
            "tool_actions": dict(sorted(actions.items())),
            "tool_actions_total": sum(actions.values()),
            "num_turns": len(codex_turns),
            "duration_ms": None,
            "reported_cost_usd": None,
            "cost_note": "Codex CLI subscription usage does not expose per-run USD cost",
            "is_error": any(record.get("type") == "turn.failed" for record in records),
        }

    results = [
        record
        for record in records
        if record.get("type") == "result" or "modelUsage" in record
    ]
    if not results:
        raise ValueError("Trace has no result or modelUsage record")
    result = results[-1]
    model_usage = result.get("modelUsage")
    if not isinstance(model_usage, dict):
        raise ValueError("Final result has no modelUsage object")

    models: dict[str, dict[str, int | float]] = {}
    input_tokens = output_tokens = thinking_tokens = cost = 0
    for model, usage in model_usage.items():
        if not isinstance(usage, dict):
            continue
        uncached = int(usage.get("inputTokens", 0) or 0)
        cache_read = int(usage.get("cacheReadInputTokens", 0) or 0)
        cache_create = int(usage.get("cacheCreationInputTokens", 0) or 0)
        output = int(usage.get("outputTokens", 0) or 0)
        model_cost = float(usage.get("costUSD", 0) or 0)
        models[str(model)] = {
            "input_tokens": uncached + cache_read + cache_create,
            "uncached_input_tokens": uncached,
            "cache_read_input_tokens": cache_read,
            "cache_creation_input_tokens": cache_create,
            "output_tokens": output,
            "thinking_tokens": int(usage.get("thinkingTokens", 0) or 0),
            "reported_cost_usd": model_cost,
        }
        input_tokens += uncached + cache_read + cache_create
        output_tokens += output
        thinking_tokens += int(usage.get("thinkingTokens", 0) or 0)
        cost += model_cost

    has_message_events = any(record.get("type") in {"assistant", "user"} for record in records)
    tool_calls: Counter[str] = Counter()
    for record in records:
        message = record.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_calls[str(block.get("name", "unknown"))] += 1

    return {
        "format": "claude-code-json",
        "models": models,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thinking_tokens_subset_of_output": thinking_tokens,
        "total_tokens": input_tokens + output_tokens,
        "tool_calls": dict(sorted(tool_calls.items())) if has_message_events else None,
        "tool_calls_total": sum(tool_calls.values()) if has_message_events else None,
        "num_turns": result.get("num_turns"),
        "duration_ms": result.get("duration_ms"),
        "reported_cost_usd": result.get("total_cost_usd", cost),
        "is_error": result.get("is_error"),
        "subtype": result.get("subtype"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces", nargs="+", type=Path, help="Claude Code JSON or JSONL, or Codex CLI JSONL traces")
    parser.add_argument("--model", help="Model name for Codex CLI traces; not present in their JSONL")
    args = parser.parse_args()
    summaries = []
    try:
        for trace in args.traces:
            # Do not echo the source filename: local paths can contain private data.
            summaries.append(summarize(read_records(trace), args.model))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.exit(2, f"error: cannot summarize trace ({type(error).__name__})\n")
    print(json.dumps(summaries, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
