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

Use it selectively for unfamiliar failures spanning components, noisy command
output, or repeated diagnosis. Skip it for localized changes with known source
and acceptance checks. No tested version has shown reliable token savings. On
the repeated Zed feature task, two compact candidate versions used 39.0% and
43.8% more total tokens; one earlier cross-layer bug pair used 0.7% more. See
the [pilot and research notes](jev-universal/docs/efficiency-research.md) for
the full evidence and limits.

The target remains at least 2x fewer total tokens, with 10x as a stretch goal.
Neither has been demonstrated. The Skill is an experimental workflow prompt,
not a proven efficiency improvement; evaluation continues.

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
