# Jev Universal

**Give your AI assistant fast, structured Jev decisions through one MCP server.**

[中文说明](jev-universal/docs/README.zh-CN.md) · [Setup](jev-universal/README.md) · [ChatGPT & hosting](jev-universal/docs/hosting.md) · [Research](jev-universal/docs/research.md) · [Security](SECURITY.md)

An independent integration for **Claude / Claude Code, ChatGPT, Kimi Code (K3),
ZCode (GLM-5.3), and Codex**. Your existing model stays in charge; Jev supplies
classification, rubric scores, assertion checks and conservative context selection.

> **v0.2.0 preview:** local MCP, authentication and packaging tests pass. Real
> TypeSafe inference requires your own API key. See the [validation record](jev-universal/docs/validation.md)
> for the exact client tests and remaining limits. This project does not provide a
> shared hosted service or free TypeSafe credits, and is not an official vendor plugin.

## Install from GitHub

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.

```sh
git clone https://github.com/uninhibited-scholar/jev-universal.git
cd jev-universal
uv sync --project jev-universal --locked --no-dev --no-editable
uv run --project jev-universal --no-editable jev-universal probe
```

The probe lists four tools and checks an exact pinned-content roundtrip **without
calling the paid TypeSafe API**. Set `TYPESAFE_API_KEY` in the server environment,
or use `--env-file` with a private file outside this repository:

```sh
uv run --project jev-universal --no-editable jev-universal --env-file /absolute/path/to/private.env doctor --live
uv run --project jev-universal --no-editable jev-universal --env-file /absolute/path/to/private.env config --client claude
```

`doctor --live` sends **one paid request** testing all three Jev primitives. `config`
prints JSON using your installed Python's path; merge it into your client's settings.
Use `--client kimi`, `zcode`, `zcode-native` or `codex` for the other formats. Never
redirect over an existing configuration file: preserve other servers.

| Client | Connection |
|---|---|
| Claude Code | Merge generated JSON into project `.mcp.json`; approve the project server |
| Claude Desktop | Merge generated JSON into the desktop MCP configuration |
| Kimi Code / K3 | Merge into `.kimi-code/mcp.json`; trust that project on first interactive launch |
| ZCode / GLM-5.3 | Settings → MCP Servers → Full configuration; import generated JSON |
| Codex | Merge generated TOML from `--client codex` into MCP settings |
| ChatGPT | Run HTTP behind a Secure MCP Tunnel or an OAuth-protected HTTPS endpoint; [instructions](jev-universal/docs/hosting.md) |

**Claude Code plugin install** (requires `uvx` on PATH and the API key in its environment):

```sh
claude plugin marketplace add uninhibited-scholar/jev-universal
claude plugin install jev-universal@jev-universal
```

The bundled MCP config fetches the pinned `v0.2.0` Git tag. No PyPI publication is
assumed. For a checkout or a private env file, use the generated config instead.

## Tools

| Tool | What it does |
|---|---|
| `jev_evaluate` | Batch independent Choice, Score and Noul questions |
| `jev_route` | Recommend one of your named workflow/model routes; never invokes it |
| `jev_check` | Check assertions against supplied evidence; uncertainty goes to review |
| `jev_select_context` | Keep exact original chunks; omit only confidently irrelevant ones |

Example request to your assistant:

> Use Jev to check whether this implementation has evidence for each acceptance
> criterion. Return uncertain checks for my review. Do not claim that tests passed
> unless we actually ran them.

Context chunks require an explicit `pinned` boolean. Pin instructions, commitments,
critical evidence and unresolved errors. Keep originals so later steps can recover
omitted material. Jev judgments do not grant permissions or establish correctness.

## Development

See [CONTRIBUTING](CONTRIBUTING.md). CI tests Linux, macOS and Windows on Python
3.11 and 3.13. The optional live workflow runs only when manually dispatched with
a configured protected environment secret.

MIT licensed. The license covers this integration; TypeSafe API usage is subject
to TypeSafe's own terms and billing.
