# Jev Universal — package setup

Cross-client Jev tools over MCP. [Repository overview](../README.md) · [中文](docs/README.zh-CN.md)

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
`zcode-native` (`mcp.servers`), `codex` (TOML). The command prints configuration;
it never changes your client settings. Merge the entry, then start a new session.
It quotes paths correctly, including Windows and paths containing spaces.

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

If `uvx` is not on a GUI app's PATH, use generated config: it points directly at
an existing installed Python. Re-run config generation if the installation moves.

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
