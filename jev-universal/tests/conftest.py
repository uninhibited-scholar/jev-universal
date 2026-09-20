"""Tests must never inherit real API credentials or deployment settings."""

import os

import pytest


@pytest.fixture(autouse=True)
def isolated_jev_environment(monkeypatch):
    for name in os.environ:
        if name.startswith("JEV_") or name in {"TYPESAFE_API_KEY", "TYPESAFE_API_KEY_FILE"}:
            monkeypatch.delenv(name, raising=False)
