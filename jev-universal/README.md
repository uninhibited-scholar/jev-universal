# Jev Universal — package setup

Cross-client Jev tools over MCP. [Repository overview](../README.md) · [中文](docs/README.zh-CN.md)

## Reproducible development-skill comparisons

`scripts/run_skill_pair.py` runs one exact prompt against two frozen Git workspaces
with a pinned Codex model and caller-selected order. Both workspaces must have the
same `HEAD`, be separate real Git worktree roots, and have no changes beyond the
arm-specific Skill file; install that Skill before the run (the baseline may omit
it). Set `--skill-path` if the Skill is outside the
workspace root, and pass the expected per-arm Skill hashes to make exposure
verifiable. Run once as `baseline-first` and once as
`candidate-first` for an order-balanced pair. The runner writes raw local traces,
stderr, and a JSON summary with prompt/Skill hashes, token counts, cached input,
tool actions, elapsed time, and exit status. It does not judge patch quality: check
the same tests and behavior in both arms separately. Raw traces may contain private
prompt or repository data; review before sharing.

Example:

```sh
python scripts/run_skill_pair.py \
  --baseline /path/to/baseline-worktree \
  --candidate /path/to/candidate-worktree \
  --prompt /path/to/task.txt \
  --commit <shared-git-commit> --model gpt-5.5 \
  --skill-path .agents/skills/jev-dev-efficient/SKILL.md \
  --baseline-skill-sha256 <baseline-hash> \
  --candidate-skill-sha256 <candidate-hash> \
  --order baseline-first --out /path/to/results-a
```

The agent can modify its workspace. For the reverse-order run, recreate clean
worktrees at the same commit and reinstall the same Skill files, then use
`--order candidate-first` and a new empty output directory. Rotate which task gets
each order across a multi-task study.
Use the reported `total_tokens`, not cache-adjusted estimates, and report the
cached-input subset separately. Token savings alone do not establish equal quality.

## Install

From this package directory (the inner `jev-universal` directory):

```sh
uv sync --locked --no-dev --no-editable
uv run --no-editable jev-universal probe
```

Alternatively install a wheel from a GitHub release with `uv tool install
/path/to/jev_universal-0.2.0-py3-none-any.whl`. The executable is `jev-universal`.
The committed JSON configs use `uvx` with a pinned GitHub tag so they contain no
machine-specific paths. Git and internet access are required for the first run.

## Credentials

Create a private env file outside the checkout containing:

```dotenv
TYPESAFE_API_KEY=your-own-key
JEV_MODEL=jev-latest
```

Protect it with filesystem permissions (for example `chmod 600` on macOS/Linux).
Pass it explicitly: `jev-universal --env-file /absolute/path/private.env doctor`.
No automatic `.env` discovery occurs. Environment variables take precedence, and
values are not interpolated. Alternatively configure `TYPESAFE_API_KEY_FILE` to
read a secret file containing only the key, such as a mounted Docker secret.

`doctor` verifies configuration without sending a request. `doctor --live` makes
one paid mixed-primitives request. Get a key from [TypeSafe](https://console.typesafe.ai).
Never paste the key into your assistant's conversation or commit it.

## Local clients

```sh
uv run --no-editable jev-universal --env-file /absolute/path/private.env config --client claude
```

Supported formats: `claude`, `kimi`, `zcode` (generic JSON for import),
`zcode-native` (`mcp.servers`), `codex` (TOML), `zed` (`context_servers`).
The command prints configuration; it never changes your client settings. Merge
only the generated `jev-universal` entry into your existing settings object, then
start a new session. Do not replace unrelated servers, profiles, or editor
settings. It quotes paths correctly, including Windows and paths containing
spaces.

- Claude Code: project `.mcp.json`. Approve the project MCP server in the client.
  Claude Desktop uses its own MCP settings file; use the same generated JSON.
- Kimi Code: `.kimi-code/mcp.json` or `~/.kimi-code/mcp.json`. A project server is
  skipped until the folder is trusted; launch `kimi` interactively once and trust
  your checkout. Leave model selection (including K3) in your existing settings.
- ZCode: import JSON in Settings → MCP Servers → Full configuration. Native
  `.zcode` entries override `.agents/mcp.json` within the same scope. The native
  user location is `~/.zcode/cli/config.json`, while workspace config is
  `.zcode/config.json`. Choose GLM-5.3 in ZCode itself.
- Codex: merge the generated TOML into the relevant MCP settings, or use the
  included `.codex-plugin/plugin.json` via a local plugin marketplace.
- Zed: open Settings → AI → MCP Servers or run `zed: open settings file`. Merge
  the generated `context_servers.jev-universal` object into the existing
  `context_servers` object in `settings.json`. Keep any existing
  `context_servers` entries; do not replace the full settings file.

If `uvx` is not on a GUI app's PATH, use generated config: it points directly at
an existing installed Python. Re-run config generation if the installation moves.
Keep secrets in the private env file or `TYPESAFE_API_KEY_FILE`; the generated
client config should contain only the env-file path, not the API key value.

## ChatGPT / HTTP

```sh
uv run --no-editable jev-universal --env-file /absolute/path/private.env --transport streamable-http
```

Default: `http://127.0.0.1:8765/mcp`. ChatGPT cannot directly reach a server on your
laptop; connect a Secure MCP Tunnel or deploy with OAuth. See [hosting](docs/hosting.md).

## API behavior

- Four tools: `jev_evaluate`, `jev_route`, `jev_check`, `jev_select_context`.
- Text instructions only (a deliberate subset of TypeSafe's structured format).
- Choice: 2–255 described options; Score: 2–10 ordered described levels; Noul:
  a probability-like 0–1 truth judgment. Choice and Score expose confidence.
- `review_required` lists low-certainty answers. For Noul the local policy uses
  `max(p, 1-p)`, not a vendor confidence or measured accuracy.
- Maximum 64 questions, 200 KB upstream request, 1 MB upstream response, 30-second
  HTTP operation timeout. No automatic retries, including rate-limit responses.
- Inputs and questions are sent to TypeSafe. No automatic repository or transcript
  collection, no persistent cache, no model orchestration, no history rewrites.
- Malformed/error responses produce tool errors without forwarding the upstream
  error body. Original evidence must be retained by the caller.

Context tool example:

```json
{
  "goal": "Fix the parser regression",
  "chunks": [
    {"id":"requirements","text":"Preserve the public API","pinned":true},
    {"id":"old-log","text":"Old successful build output","pinned":false}
  ],
  "threshold": 0.85
}
```

All-pinned requests make no TypeSafe call. With any unpinned chunk, the supplied
state is sent for relevance evaluation, including pinned context. Pinning prevents
omission, not transmission.
