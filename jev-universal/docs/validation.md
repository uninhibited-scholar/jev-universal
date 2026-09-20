# Validation record — 2026-09-20

Preview v0.2.0. Evidence must distinguish transport, client tool calling, and
real model inference.

| Layer | Result | What was actually checked |
|---|---|---|
| Unit and protocol tests | 37 passed locally | Input/response validation; no credential leaks in errors; budgets; uncertainty retention; real stdio and HTTP handshake/tool calls |
| OAuth resource server | Passed locally | RSA signature, issuer, expiry, audience and scope checks; 401/403 behavior; valid-token initialization; protected resource metadata |
| Built wheel | Passed | Separate uv tool environment installed the built wheel and performed MCP discovery and a pinned-content roundtrip |
| Claude Code 2.1.266 | Passed | claude-sonnet-4-6 used ToolSearch, called Jev, and received the exact pinned sentinel |
| Kimi Code 2.0.2 | Passed | kimi-code/k3 called Jev and received the exact pinned sentinel |
| ZCode bundled CLI 0.16.5 / GLM-5.3 | Passed | Actual role=tool result preserved the pinned sentinel; native user MCP config was used |
| ChatGPT | Not account-tested | Local HTTP and OAuth tested; actual account connection needs a configured tunnel or HTTPS issuer/deployment |
| Real TypeSafe inference | Not run | No TypeSafe API key was configured during these tests |

[Sanitized client call evidence](evidence/client-smoke.json) includes actual tool
arguments and tool results, not assistant claims. Raw client transcripts are
excluded because they may contain unrelated local settings and private metadata.

Observed client pitfalls fixed or documented:

- Claude Code `--tools ''` removes tools, and listing only an MCP name can prevent
  deferred discovery. Keep ToolSearch available (normal/default tool set).
- Kimi skips untrusted project MCP config. Trust the test directory interactively.
- Kimi omitted an optional `pinned` argument in an early test. The field is now
  required, so omission fails validation instead of silently classifying content.

The tests make no paid Jev call. Their results do not establish Jev accuracy,
latency, reduction ratio or production suitability. Run `doctor --live` with your
own key, then use a labeled task corpus before automating consequential decisions.

ZCode bundled CLI required native user-scoped MCP configuration in this environment. Its advertised `--settings`/`--allowed-tools` options were rejected. The test used process-scoped model settings and restored the temporary MCP entry afterward. Desktop UI import follows the vendor-documented route and was not itself verified.
