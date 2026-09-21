from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_skill_pair


def make_git_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    (path / "tracked.txt").write_text("frozen\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "tracked.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "fixture"], check=True, capture_output=True
    )


def test_git_checks_require_repo_root_and_allow_only_arm_skill(tmp_path):
    workspace = tmp_path / "workspace"
    make_git_repo(workspace)
    skill = workspace / ".agents/skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("arm-specific\n", encoding="utf-8")

    assert run_skill_pair.git_head(workspace)
    assert run_skill_pair.git_status_outside_skill(workspace, skill) == ""
    (workspace / "nested").mkdir()
    with pytest.raises(ValueError, match="Git worktree root"):
        run_skill_pair.git_head(workspace / "nested")

    (workspace / "tracked.txt").write_text("unrelated change\n", encoding="utf-8")
    assert run_skill_pair.git_status_outside_skill(workspace, skill).strip()


def test_run_arm_records_usage_hashes_and_elapsed_time(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skill = workspace / ".agents/skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Use focused evidence.\n", encoding="utf-8")
    trace = {
        "type": "turn.completed",
        "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 3},
    }
    read_event = {
        "type": "item.completed",
        "item": {
            "type": "command_execution",
            "command": "sed -n '1,20p' .agents/skills/example/SKILL.md",
            "exit_code": 0,
            "aggregated_output": "Use focused evidence.\n",
        },
    }

    def fake_run(command, **kwargs):
        if command[:3] == ["git", "-C", str(workspace)]:
            if "--show-toplevel" in command:
                return subprocess.CompletedProcess(
                    command, 0, stdout=str(workspace) + "\n", stderr=""
                )
            if "--porcelain" in command:
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        assert 'model_reasoning_effort="low"' in command
        assert 'model_verbosity="low"' in command
        kwargs["stdout"].write(json.dumps(trace) + "\n")
        kwargs["stdout"].write(json.dumps(read_event) + "\n")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_skill_pair.subprocess, "run", fake_run)
    result = run_skill_pair.run_arm(
        arm="candidate",
        workspace=workspace,
        prompt="Fix the regression.",
        model="test-model",
        output_dir=tmp_path,
        position=1,
        expected_commit="abc123",
        skill_relative_path=Path(".agents/skills/example/SKILL.md"),
        expected_skill_sha256=run_skill_pair.sha256(skill),
        reasoning_effort="low",
        verbosity="low",
    )

    assert result["skill_present"] is True
    assert result["skill_read_observed_in_trace"] is True
    assert result["workspace_commit"] == "abc123"
    assert result["usage"]["total_tokens"] == 15
    assert result["elapsed_seconds"] >= 0


def test_run_arm_rejects_wrong_skill_hash(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skill = workspace / "SKILL.md"
    skill.write_text("actual skill", encoding="utf-8")

    def fake_git(command, **kwargs):
        if "--show-toplevel" in command:
            return subprocess.CompletedProcess(command, 0, stdout=str(workspace) + "\n")
        if "--porcelain" in command:
            return subprocess.CompletedProcess(command, 0, stdout="")
        return subprocess.CompletedProcess(command, 0, stdout="abc123\n")

    monkeypatch.setattr(run_skill_pair.subprocess, "run", fake_git)

    with pytest.raises(ValueError, match="Skill hash"):
        run_skill_pair.run_arm(
            arm="candidate",
            workspace=workspace,
            prompt="task",
            model="test-model",
            output_dir=tmp_path,
            position=1,
            expected_commit="abc123",
            skill_relative_path=Path("SKILL.md"),
            expected_skill_sha256="wrong",
            reasoning_effort="low",
            verbosity="low",
        )


def test_skill_reference_with_failed_read_is_not_counted_as_loaded():
    records = [
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "sed -n '1,20p' .agents/skills/example/SKILL.md",
                "exit_code": 2,
            },
        }
    ]
    assert (
        run_skill_pair.skill_read_observed(
            records, Path(".agents/skills/example/SKILL.md"), "Use focused evidence.\n"
        )
        is False
    )


def test_file_check_without_skill_contents_is_not_counted_as_read():
    records = [
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "test -f .agents/skills/example/SKILL.md && sed -n '1,20p' .agents/skills/example/SKILL.md || true",
                "exit_code": 0,
                "aggregated_output": "",
            },
        }
    ]
    assert (
        run_skill_pair.skill_read_observed(
            records, Path(".agents/skills/example/SKILL.md"), "Use focused evidence.\n"
        )
        is False
    )
