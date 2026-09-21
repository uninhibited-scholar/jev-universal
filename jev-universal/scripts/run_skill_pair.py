#!/usr/bin/env python3
"""Run a reproducible, order-balanced Codex CLI comparison for two frozen workspaces.

The runner records local raw traces; share only its redacted summary unless you have
reviewed traces for secrets. Each workspace must be a frozen copy of the same source
tree with its arm-specific Skill installed (or deliberately absent for baseline).
Skill text is explicitly injected into candidate input so exposure is auditable;
the baseline receives a neutral section and the exact same task text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from summarize_agent_trace import read_records, summarize  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_command_environment(path: Path | None) -> tuple[dict[str, str], str]:
    if path is None:
        overrides: dict[str, str] = {}
    else:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or any(
            not isinstance(key, str)
            or not key
            or "=" in key
            or "\0" in key
            or not isinstance(item, str)
            or "\0" in item
            for key, item in value.items()
        ):
            raise ValueError("command environment JSON must map valid variable names to strings")
        folded = [key.casefold() for key in value]
        if len(folded) != len(set(folded)):
            raise ValueError("command environment JSON has duplicate variable names")
        overrides = value
    canonical = json.dumps(overrides, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return overrides, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def git_head(workspace: Path) -> str:
    root = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if Path(root).resolve() != workspace.resolve():
        raise ValueError(f"{workspace} is not a Git worktree root")
    result = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_status_outside_skill(workspace: Path, skill_path: Path) -> str:
    command = ["git", "-C", str(workspace), "status", "--porcelain", "--untracked-files=all"]
    try:
        skill_relative = skill_path.resolve().relative_to(workspace.resolve())
    except ValueError:
        pass
    else:
        command.extend(["--", ".", f":(exclude,top){skill_relative.as_posix()}"])
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout


def prompt_for_arm(task_prompt: str, arm: str, skill_content: str | None) -> str:
    """Expose Skill text explicitly in treatment and use a neutral baseline section."""
    if arm == "candidate":
        if not skill_content:
            raise ValueError("candidate workspace must contain the Skill file")
        treatment = skill_content
    else:
        # Equalize the prompt envelope without giving baseline extra guidance.
        treatment = "[No development instructions are supplied in this section.]"
    return (
        "<development_instructions>\n"
        f"{treatment.rstrip()}\n"
        "</development_instructions>\n\n"
        "<task>\n"
        f"{task_prompt.rstrip()}\n"
        "</task>\n"
    )


def run_arm(
    *,
    arm: str,
    workspace: Path,
    prompt: str,
    model: str,
    output_dir: Path,
    position: int,
    expected_commit: str,
    skill_relative_path: Path,
    expected_skill_sha256: str | None,
    reasoning_effort: str,
    verbosity: str,
    command_environment: dict[str, str] | None = None,
    codex_executable: str = "codex",
) -> dict[str, Any]:
    head = git_head(workspace)
    if head != expected_commit:
        raise ValueError(f"{arm} workspace HEAD does not match --commit")
    skill_path = workspace / skill_relative_path
    status = git_status_outside_skill(workspace, skill_path)
    if status.strip():
        raise ValueError(f"{arm} workspace must be clean outside its Skill file before the run")
    skill_hash = sha256(skill_path) if skill_path.is_file() else None
    if arm == "candidate" and skill_hash is None:
        raise ValueError("candidate workspace must contain the Skill file")
    if arm == "baseline" and skill_hash is not None:
        raise ValueError("baseline workspace must not contain the Skill file")
    if expected_skill_sha256 is not None and skill_hash != expected_skill_sha256:
        raise ValueError(f"{arm} Skill hash does not match its expected hash")

    skill_content = skill_path.read_text(encoding="utf-8") if skill_hash is not None else None
    arm_prompt = prompt_for_arm(prompt, arm, skill_content)
    trace_path = output_dir / f"{arm}.jsonl"
    stderr_path = output_dir / f"{arm}.stderr"
    started = time.monotonic()
    with (
        trace_path.open("w", encoding="utf-8") as stdout,
        stderr_path.open("w", encoding="utf-8") as stderr,
    ):
        result = subprocess.run(
            [
                codex_executable,
                "exec",
                "--json",
                "--ephemeral",
                "--sandbox",
                "workspace-write",
                "--model",
                model,
                "--config",
                f'model_reasoning_effort="{reasoning_effort}"',
                "--config",
                f'model_verbosity="{verbosity}"',
                "--cd",
                str(workspace),
                "-",
            ],
            input=arm_prompt,
            env={**os.environ, **(command_environment or {})},
            text=True,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    elapsed = time.monotonic() - started
    records = read_records(trace_path)
    usage = summarize(records, model_override=model)
    return {
        "arm": arm,
        "position": position,
        "model": model,
        "workspace_commit": head,
        "skill_sha256": skill_hash,
        "skill_present": skill_path.is_file(),
        "skill_injected_into_prompt": arm == "candidate",
        "skill_injected_sha256": (
            hashlib.sha256(skill_content.encode("utf-8")).hexdigest()
            if arm == "candidate" and skill_content is not None
            else None
        ),
        "prompt_sha256": hashlib.sha256(arm_prompt.encode("utf-8")).hexdigest(),
        "task_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_bytes": len(arm_prompt.encode("utf-8")),
        "reasoning_effort": reasoning_effort,
        "verbosity": verbosity,
        "elapsed_seconds": round(elapsed, 3),
        "exit_code": result.returncode,
        "usage": usage,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline", required=True, type=Path, help="Frozen baseline git workspace"
    )
    parser.add_argument(
        "--candidate", required=True, type=Path, help="Frozen candidate git workspace"
    )
    parser.add_argument("--prompt", required=True, type=Path, help="Exact shared task prompt")
    parser.add_argument("--commit", required=True, help="Expected shared workspace HEAD")
    parser.add_argument("--model", required=True, help="Pinned Codex model identifier")
    parser.add_argument(
        "--reasoning-effort",
        required=True,
        choices=("minimal", "low", "medium", "high", "xhigh"),
        help="Pinned Codex reasoning effort",
    )
    parser.add_argument(
        "--verbosity",
        required=True,
        choices=("low", "medium", "high"),
        help="Pinned Codex response verbosity",
    )
    parser.add_argument(
        "--skill-path",
        type=Path,
        default=Path(".agents/skills/jev-dev-efficient/SKILL.md"),
        help="Skill path relative to each workspace root (default: %(default)s)",
    )
    parser.add_argument("--baseline-skill-sha256", help="Expected baseline Skill SHA-256")
    parser.add_argument("--candidate-skill-sha256", help="Expected candidate Skill SHA-256")
    parser.add_argument(
        "--command-env-json",
        type=Path,
        help="Optional shared JSON object of environment overrides for agent shell commands",
    )
    parser.add_argument("--out", required=True, type=Path, help="New or empty results directory")
    parser.add_argument("--order", choices=("baseline-first", "candidate-first"), required=True)
    args = parser.parse_args()

    baseline = args.baseline.resolve()
    candidate = args.candidate.resolve()
    prompt_path = args.prompt.resolve()
    out = args.out.resolve()
    if baseline == candidate:
        parser.error("baseline and candidate must be distinct workspaces")
    if not prompt_path.is_file():
        parser.error("prompt file does not exist")
    command_env_path = args.command_env_json.resolve() if args.command_env_json else None
    if command_env_path is not None and not command_env_path.is_file():
        parser.error("command environment JSON file does not exist")
    try:
        command_environment, command_environment_sha256 = read_command_environment(command_env_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(f"invalid command environment JSON: {error}")
    codex_executable = shutil.which("codex")
    if codex_executable is None:
        parser.error("Codex CLI executable not found on PATH")
    if out.exists() and any(out.iterdir()):
        parser.error("output directory must be empty")
    out.mkdir(parents=True, exist_ok=True)
    prompt = prompt_path.read_text(encoding="utf-8")
    order = (
        ["baseline", "candidate"] if args.order == "baseline-first" else ["candidate", "baseline"]
    )
    workspaces = {"baseline": baseline, "candidate": candidate}
    runs = []
    for position, arm in enumerate(order, start=1):
        runs.append(
            run_arm(
                arm=arm,
                workspace=workspaces[arm],
                prompt=prompt,
                model=args.model,
                output_dir=out,
                position=position,
                expected_commit=args.commit,
                skill_relative_path=args.skill_path,
                expected_skill_sha256=(
                    args.baseline_skill_sha256 if arm == "baseline" else args.candidate_skill_sha256
                ),
                reasoning_effort=args.reasoning_effort,
                verbosity=args.verbosity,
                command_environment=command_environment,
                codex_executable=codex_executable,
            )
        )
    report = {
        "schema_version": 4,
        "model": args.model,
        "codex_cli_version": subprocess.run(
            [codex_executable, "--version"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "reasoning_effort": args.reasoning_effort,
        "verbosity": args.verbosity,
        "python_version": platform.python_version(),
        "command_environment_override_keys": sorted(command_environment),
        "command_environment_overrides_sha256": command_environment_sha256,
        "order": order,
        "source_commit": args.commit,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_bytes": len(prompt.encode("utf-8")),
        "cost_note": "Codex CLI subscription runs do not expose per-run USD cost",
        "runs": runs,
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if any(run["exit_code"] for run in runs):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
