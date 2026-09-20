# Jev-inspired Efficient Development Skill

**A portable coding workflow for reducing wasted exploration and retries. No TypeSafe account, API key, server, or plugin service required.**

[中文说明](jev-universal/docs/README.zh-CN.md) · [Skill](jev-universal/skills/jev-universal/SKILL.md) · [Research notes](jev-universal/docs/research.md) · [Optional TypeSafe MCP adapter](jev-universal/README.md)

Jev is TypeSafe AI's decision model. This repository's default offering is a
prompt-level development Skill that combines common context-efficiency practices
with Jev's public idea of breaking work into narrow judgments and explicit
decision rules. It runs with the assistant you already use, including Claude,
ChatGPT, Kimi Code, and ZCode. It is **not Jev**, does not reproduce its trained
model, and does not guarantee Jev's performance or any fixed token savings.

## Use the Skill

Install or copy the folder `jev-universal/skills/jev-universal/` into the skills
directory supported by your AI client, then start a new conversation. Or copy
the `SKILL.md` instructions into the assistant's project/user instructions.
No API key or login is needed.

Use it selectively for unfamiliar multi-file features, bugs, or debugging
tasks, especially when the relevant implementation is not yet clear. Skip it
for localized changes with known source and acceptance checks. In the clean
no-Skill comparison on a cross-file Zed config task, one order used 4.2% fewer
tokens with the Skill and the reversed order used 5.6% more; pooled, the Skill
used 0.3% more. This does not show reliable token savings. Results from other
task types also vary. No stable multi-fold savings are established; the 2x
target remains unmet. See the [pilot and research notes](jev-universal/docs/efficiency-research.md)
for the full evidence and limits.

The target remains at least 2x fewer total tokens, with 10x as a stretch goal.
Neither target has been demonstrated. The Skill is an experimental workflow
prompt, not a proven general efficiency improvement; evaluation continues.

## Optional: Codex large-output hook

The plugin also contains an experimental Codex-only hook that replaces large
Bash results with a short preview and a local recall command. In four
order-balanced pairs (eight runs) on two test-heavy coding tasks, it reduced
combined total tokens by 9.5%;
the larger task varied from 6.3% to 20.6% savings when run order reversed. This
is not a multi-fold result and does not apply to Claude, Kimi, or ZCode. The
hook needs no API key or network service. Captured output is recallable for one
hour; expired files are pruned opportunistically. It skips recognized test
failures and likely secret patterns.
Install the GitHub marketplace entry with Codex CLI:

```sh
codex plugin marketplace add uninhibited-scholar/jev-universal --ref main --sparse .agents/plugins --sparse jev-universal
codex plugin add jev-universal@jev-universal
```

Then review and trust the bundled hook with `/hooks`. See the [hook notes and
measurements](jev-universal/docs/efficiency-research.md). The Skill can be used
in other clients, but this automatic output hook currently runs only in Codex.

## Optional: TypeSafe API adapter

The repository also retains an MCP adapter for people who already have TypeSafe
API access. TypeSafe currently gates access to Jev behind its waitlist, so this
adapter is optional and is not needed to use the Skill. See the [adapter setup](jev-universal/README.md)
and [client validation record](jev-universal/docs/validation.md). No shared API
key or hosted access is provided.

The workflow is inspired by TypeSafe's [public description of Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
and its [structured workflow evaluations](https://evals.typesafe.ai/). The
workflow's utility still needs independent measurement in the intended use
cases; TypeSafe's reported benchmarks describe its own model and evaluations.

MIT licensed. This project's license does not grant access to TypeSafe's model
or services.
