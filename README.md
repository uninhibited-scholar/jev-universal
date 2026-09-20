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
and acceptance checks. Results remain exploratory: one forced-on local task used
40% more tokens, while a separate JWT diagnosis saved tokens but dropped an
existing returned claims field and failed an added compatibility check. Its revised
repeat preserved behavior but used 79% more tokens. See the [pilot and research
notes](jev-universal/docs/efficiency-research.md) for the full evidence and limits.

Three newer synthetic, cross-layer runs remain mixed: one pair saved 26.7% total
tokens, the next used 9.7% more, and a counterbalanced repeat saved 14.6%. The two
repeats of the same task pool to only 2.5% fewer tokens. All passed identical
locally runnable correctness gates, but this does not establish a stable saving
or approach the 2x target. The evaluation is ongoing.

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
