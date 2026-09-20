# Existing efficiency practices and this Skill's design

This is a design review, not a benchmark of this repository's Skill. Community examples are useful for discovering operational tactics, but individual savings figures are not treated as independently verified results.

## Patterns worth keeping

- **Targeted retrieval:** search for symbols and inspect matching regions instead of reading whole files. Cap output from unknown logs and commands. This is recommended in community coding-agent guidance such as [Austin Serb's AGENTS.md patterns](https://github.com/Austin1serb/agents-md), which reports a personal ~50% average reduction from a byte-capped output rule; that number is author-reported, not a general result.
- **Optimize the whole session:** avoid redundant reads, tool calls, and user round-trips; don't cut needed context if doing so risks a failed attempt. A [community token-efficiency skill](https://github.com/denfry/claude-skills/blob/main/skills/token-efficiency/SKILL.md) explicitly uses this total-cost framing and keeps detailed guidance/reference material separate from its tiny always-on contract.
- **Progressive disclosure:** keep the trigger and core rules short; load examples or specialized procedures only when relevant. GitHub's [Copilot skills guidance](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) similarly recommends repository instructions for simple always-relevant rules and Skills for detailed task-specific instructions. The 2026 [SkillReducer preprint](https://arxiv.org/abs/2603.29919) reports that compressing skill descriptions and deferring non-core material reduced its sampled skill bodies while retaining or improving evaluated function; this is evidence about skills in that benchmark, not a result for this Skill.
- **Small, purposeful validation:** verify changed behavior and acceptance criteria, but do not rerun unrelated checks without a reason. Keep successful output summarized and preserve actionable failure details.

## Jev-inspired decision structure

Use narrow judgments internally to reduce the search space: which subsystem is implicated, which evidence would change the diagnosis, and what smallest action resolves the issue? Choose the next step from the evidence, then stop exploring once acceptance and relevant checks are satisfied. This borrows Jev's public workflow idea; the host model still performs all judgments and implementation.

## Why no blanket token-savings claim

Evidence on persistent agent instructions is mixed. A 2026 paired study of 124 pull requests across 10 repositories reports a 28.64% lower median runtime and 16.58% lower output-token consumption with `AGENTS.md`, while median input tokens were slightly higher and task-completion behavior was comparable ([paper](https://arxiv.org/abs/2601.20404)). In contrast, another 2026 study across SWE-bench and repository tasks reports that context files could increase inference cost by over 20% and reduce task success, concluding that unnecessary instructions make work harder ([paper](https://arxiv.org/abs/2602.11988)). These studies vary in setup and do not show that an arbitrary Skill saves tokens.

The Skill therefore stays short, avoids mandatory ceremonies, and treats saved work as a hypothesis. A valid local evaluation should pair the same tasks and model/settings, repeat runs where feasible, and report at least total input/output tokens, tool calls, wall-clock time, and task success/rework. Output brevity alone is not enough: skipped discovery or validation counts as a failure, not a saving.

## Local pilot 001

One paired run used Claude Code 2.1.266 with `claude-sonnet-4-6` on identical copies of a small Python repo. The task was a localized `Path.expanduser()` bugfix with explicit behavior and tests. The baseline got the task prompt only; the treatment got the same prompt plus this Skill's full text. Both ran in the same restricted environment with the same $0.40 run cap.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens across reported models, including cache read/create | 95,226 | 112,598 | +18.2% |
| Output tokens across reported models | 1,893 | 1,930 | +2.0% |
| Model turns | 9 | 11 | +22.2% |
| Wall time | 28.8 s | 37.7 s | +31.0% |
| Reported cost | $0.1994 | $0.2129 | +6.7% |
| Acceptance tests | 5/5 | 5/5 | tied |

The agent could not launch pytest because the restricted CLI session denied its shell command; the identical test suite was run outside the agent in both fixture copies and passed in each. Usage totals include 952 input and 16 output tokens from a Haiku helper in both conditions. Tool-call counts were not captured in this run. The fixture, JSON usage reports, and patches are kept locally under the ignored `.local/efficiency/pilot-001/` directory and are not committed.

This single easy task is not evidence about repository-scale debugging. It does show the full Skill should not be forced onto small obvious edits. The trigger is now scoped to substantial exploration, noisy output, or repeated diagnosis. Next, test that intended workload with several paired tasks and repeat runs; the exact numbers above are a pilot result, not a general effect estimate.

## Local pilot 002

A second paired run used the same Claude Code/model setup on identical copies of this Python MCP package. We seeded an issuer-validation regression in both copies and asked the agent to trace the authentication path, restore the issuer check without weakening other checks, add end-to-end regression coverage, and run auth tests. Both patches restored the configured issuer comparison and passed all 9 auth tests.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens across reported models, including cache read/create | 115,716 | 99,461 | −14.0% |
| Output tokens across reported models | 2,637 | 1,797 | −31.9% |
| Tool calls | 7 | 7 | tied |
| Model turns | 8 | 8 | tied |
| Wall time | 53.8 s | 35.2 s | −34.5% |
| Reported cost | $0.1286 | $0.1304 | +1.4% |
| Auth tests | 9/9 | 9/9 | tied |

This is one run per condition. The Skill used one fewer file read but one extra glob, so the call count did not change. Lower token and time usage did not lower reported cost in this run; prompt cache creation and stochastic execution can affect cost. The result is promising for this specific repository-diagnosis task, not yet a stable estimate. Repeat with multiple task types and swapped run order before making a general claim.

## Local pilot 003

The third paired run used identical copies of the full package and asked for `TYPESAFE_API_KEY_FILE` to accept `~/`, retain literal `$VAR` behavior, add tests, and document the setting. Both implementations were correct; an independent run of `tests/test_core.py` and `tests/test_cli.py` passed all 29 tests in each copy.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens across reported models, including cache read/create | 144,457 | 203,914 | +41.2% |
| Output tokens across reported models | 3,080 | 3,033 | −1.5% |
| Tool calls | 12 | 13 | +8.3% |
| Model turns | 13 | 14 | +7.7% |
| Wall time | 60.5 s | 45.8 s | −24.3% |
| Reported cost | $0.1490 | $0.1927 | +29.3% |
| Acceptance tests | 29/29 | 29/29 | tied |

The Skill run finished sooner but spent more tokens and reported higher cost. It read more files and ran a broader test selection; this may have improved diligence, but did not meet the token-saving objective. Across these three one-shot pairs, the Skill helped one security-diagnosis case and hurt two simpler changes. The evidence does not support a general saving claim, much less a multi-fold or 10x claim. Run-order effects and task variance remain uncontrolled; the next step is repeated, counterbalanced pairs or a much narrower Skill that does less work per invocation.

## Local pilot 004

To check order sensitivity, we repeated the seeded issuer-regression task with the compact 263-word Skill, running Skill first and baseline second. Both patches were correct. The baseline agent ran its test command; the Skill agent's test command was denied by the CLI permission layer, so both copies were independently checked afterward and passed all 8 auth tests.

| Measure | Baseline | Compact Skill | Change |
|---|---:|---:|---:|
| Total input tokens across reported models, including cache read/create | 93,865 | 95,734 | +2.0% |
| Output tokens across reported models | 2,183 | 1,863 | −14.7% |
| Tool calls | 6 | 7 | +16.7% |
| Model turns | 7 | 8 | +14.3% |
| Wall time | 36.3 s | 31.4 s | −13.5% |
| Reported cost | $0.1148 | $0.1210 | +5.4% |
| Auth tests | 8/8 | 8/8 | tied |

The compact Skill reduced output and time in this repeat, but not input tokens, total tool calls, or reported cost. Compared with pilot 002 on the same task, the one-run input result changed from −14.0% with the longer Skill to +2.0% with the compact Skill. Baseline input itself varied from 93,865 to 115,716. This confirms that one run is noisy and that we cannot infer a stable total-token saving from the current evidence. The compact version costs less prompt overhead and remains the candidate for further counterbalanced trials.
