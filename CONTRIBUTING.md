# Contributing

From the repository root:

```sh
uv sync --project jev-universal --locked --no-editable
uv run --project jev-universal --no-editable ruff check --config jev-universal/pyproject.toml jev-universal/src jev-universal/tests
uv run --project jev-universal --no-editable ruff format --check --config jev-universal/pyproject.toml jev-universal/src jev-universal/tests
uv run --project jev-universal --no-editable python -m pytest jev-universal/tests -q
uv build --project jev-universal --out-dir dist
```

After source changes, use `uv sync --project jev-universal --no-editable
--reinstall-package jev-universal` to refresh the installed copy. Tests isolate
credentials and never make a paid Jev request. `doctor --live` is explicit and
makes one paid request. The manual live workflow needs a secret configured in
the protected `live-jev` GitHub environment; it never runs on pull requests.

Keep client compatibility claims tied to evidence. Add regressions for behavior,
not tests that merely mirror source. Do not commit env files, personal paths,
private chat logs or access tokens. Submit changes through pull requests.
