import json
import os
import subprocess
import sys
import tomllib

import pytest
from jev_universal.cli import client_config
from jev_universal.core import api_key


@pytest.mark.parametrize("client", ["claude", "kimi", "zcode", "zcode-native", "codex"])
def test_client_config_is_portable(client, tmp_path):
    config = client_config(client, tmp_path / "secret file.env")
    if client == "codex":
        entry = tomllib.loads(config)["mcp_servers"]["jev-universal"]
    elif client == "zcode-native":
        entry = config["mcp"]["servers"]["jev-universal"]
    else:
        entry = config["mcpServers"]["jev-universal"]
    assert entry["command"] == sys.executable
    assert entry["args"][-1] == str(tmp_path / "secret file.env")


def test_key_file(monkeypatch, tmp_path):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    secret = tmp_path / "secret"
    secret.write_text("test-file-key\n")
    monkeypatch.setenv("TYPESAFE_API_KEY_FILE", str(secret))
    assert api_key() == "test-file-key"
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-env-key")
    assert api_key() == "test-env-key"


def test_doctor_without_key():
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"TYPESAFE_API_KEY", "TYPESAFE_API_KEY_FILE"}
    }
    result = subprocess.run(
        [sys.executable, "-m", "jev_universal.cli", "doctor"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["api_key_configured"] is False


def test_missing_env_file(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jev_universal.cli",
            "--env-file",
            str(tmp_path / "missing"),
            "doctor",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "does not exist" in result.stderr


def test_env_file_secret_not_in_config(tmp_path):
    secret = tmp_path / "private.env"
    secret.write_text("TYPESAFE_API_KEY=never-echo-this\n")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jev_universal.cli",
            "--env-file",
            str(secret),
            "config",
            "--client",
            "kimi",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "never-echo-this" not in result.stdout + result.stderr
    assert str(secret) in result.stdout
