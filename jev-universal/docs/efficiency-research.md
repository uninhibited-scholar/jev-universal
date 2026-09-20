# Existing efficiency practices and this Skill's design

This document combines a design review with local pilot benchmark results. Community examples are useful for discovering operational tactics, but individual savings figures are not treated as independently verified results.

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

## Local pilot 005

We changed the compact Skill to explicitly avoid whole-repository inventories when the request already names a subsystem. On the seeded issuer-validation regression, the baseline ran first and the Skill second. Both fixes passed all 8 auth tests when run independently.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens | 137,500 | 72,675 | −47.1% |
| Output tokens | 2,429 | 1,616 | −33.5% |
| Input + output tokens | 139,929 | 74,291 | −46.9% |
| Tool calls | 9 | 6 | −33.3% |
| Wall time | 64.5 s | 44.3 s | −31.4% |
| Reported cost | $0.1428 | $0.1037 | −27.4% |
| Auth tests | 8/8 | 8/8 | tied |

The baseline first listed the repository, read three files, edited implementation and tests, then ran pytest twice. The Skill searched the named auth area, edited the fix, and ran the existing auth suite once; it recognized that an existing invalid-issuer case already tested the core invariant. This is the clearest evidence so far for avoiding redundant discovery and tests, though it is one task/run.

## Local pilot 006

We repeated the same issuer regression with the same compact Skill, but ran Skill first and baseline second. Both patches were independently verified; baseline had 9 auth tests and Skill had 8 because they added different regression coverage (a direct verifier test versus an HTTP-path assertion).

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens | 112,171 | 89,246 | −20.4% |
| Output tokens | 2,131 | 1,849 | −13.2% |
| Input + output tokens | 114,302 | 91,095 | −20.3% |
| Tool calls | 8 | 7 | −12.5% |
| Wall time | 50.5 s | 45.1 s | −10.5% |
| Reported cost | $0.1214 | $0.0991 | −18.4% |
| Auth tests | 9/9 | 8/8 | all passed |

This reversed-order repeat also favored the Skill, with smaller savings. It does not meet the 2x target.

## Local pilot 007

On a second task type, both agents updated `TYPESAFE_API_KEY_FILE` to accept `~/` without expanding `$VAR`, added regression tests, and documented the behavior. Skill ran first. An independent identical run of `tests/test_core.py` and `tests/test_cli.py` passed all 29 tests in both copies; this gave both arms the same correctness gate even though their in-agent test selections differed.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Total input tokens | 202,783 | 151,309 | −25.4% |
| Output tokens | 3,807 | 2,788 | −26.8% |
| Input + output tokens | 206,590 | 154,097 | −25.4% |
| Tool calls | 13 | 12 | −7.7% |
| Wall time | 78.8 s | 59.5 s | −24.5% |
| Reported cost | $0.2063 | $0.1347 | −34.7% |
| Acceptance tests | 29/29 | 29/29 | tied |

### Current checkpoint

Across pilots 005–007, pooled input-plus-output usage fell from 460,821 to 319,483 tokens (−30.7%, about 1.44x fewer), wall time fell about 23%, and reported cost fell about 28%. That checkpoint covered only two task types and was too small to establish reliability. Pilot 008 below is a forced-invocation applicability control, not an in-scope repository-scale task; pooling it with the earlier runs would obscure that distinction. Earlier pilots with the longer Skill showed mixed or adverse results. Keep the goal active and add further in-scope task types and repetitions before asserting stable savings. The 2x target remains unmet; 10x has no supporting evidence.


## Reproducibility checkpoint (2026-09-20)

We reran the same acceptance command outside the agent approval layer for both pilot 007 fixture copies: `uv run --no-editable pytest tests/test_cli.py tests/test_core.py -q`. Baseline and Skill each passed 29/29 tests. The original agent test commands had been blocked by approval, so this independent rerun closes that verification gap for pilot 007.

The pilot traces are stored as local JSONL under the ignored `.local/efficiency/` directory because they contain private prompts and local paths; only sanitized aggregate metrics are published here. To reproduce a privacy-preserving summary from local Claude Code traces, run `python3 jev-universal/scripts/summarize_agent_trace.py <baseline.jsonl> <skill.jsonl>` or add `--model <slug>` for Codex CLI JSONL traces. The JSON output follows argument order and contains token breakdowns, per-model cost when the trace reports it, tool-action counts, turns, elapsed time when available, and status; it never prints prompt contents or source paths. Codex CLI does not expose per-run USD cost or elapsed time in its events. If only a final result JSON was saved without message events, tool-call counts are `null` rather than being misreported as zero. At this checkpoint, the authenticated Claude Code CLI reported 98% utilization of its seven-day window and we paused. Pilot 008 was later run as a single bounded pair when the CLI continued to allow requests; its trace then reported 99% utilization. After recording that pair, we stopped further Claude runs. We then used the separate Codex CLI subscription for one cross-model control, which does not expose per-run USD cost. This is an account-capacity constraint, not a Skill evaluation result. The goal remains open.


## Local pilot 008: forced-invocation applicability control

This control used the same copied package, task text, Claude Code 2.1.266, `claude-sonnet-4-6`, permissions, tool allowlist, and $0.50 per-run budget cap. Baseline ran first; the Skill treatment received the then-current Skill as an appended instruction. The task named the subsystem, exact privacy behavior, and acceptance checks. Under the Skill's stated applicability rule it should have skipped the workflow, but this experiment forcibly supplied it to measure the cost of over-invocation. Treat the result as a stress/control case, not an estimate for correctly triggered use.

Both agents removed pinned chunk text from the state sent to the evaluator and avoided calling the evaluator when all chunks were pinned. The final code changes were equivalent. The same full test suite was run independently in both copies: 39/39 passed in each, including the regression checks.

| Measure | Baseline | Forced Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cache read/create) | 371,723 | 524,116 | +41.0% |
| Output tokens | 5,417 | 5,459 | +0.8% |
| Input + output tokens | 377,140 | 529,575 | +40.4% |
| Tool calls | 14 | 21 | +50.0% |
| Model turns | 15 | 22 | +46.7% |
| Wall time | 102.4 s | 93.9 s | −8.3% |
| Reported cost | $0.4176 | $0.4643 | +11.2% |
| Full test suite | 39/39 | 39/39 | tied |

The run used only `claude-sonnet-4-6`; its reported input comprised 13 uncached, 332,264 cache-read, and 39,446 cache-create tokens in baseline, versus 15 uncached, 496,702 cache-read, and 27,399 cache-create tokens with the Skill. Outputs were 5,417 and 5,459. The Skill treatment made seven more tool calls, including three extra globs and two extra reads. It was somewhat faster, but token use and cost increased. This reinforces the need for strict applicability gating: force-invoking the Skill on a localized, fully specified task can erase prior savings.

A separate CLI calibration used a $0.05 maximum-budget flag, but the smallest request was reported at $0.0678 after 11,282 cache-creation tokens and ended as budget-exhausted. The flag did not act as a hard billing ceiling; that calibration is excluded from task-pair metrics. Subsequent Claude trace rate-limit events showed 99% seven-day utilization, so no more paid model runs were started in this checkpoint.

## Current checkpoint after pilot 008

The positive pilots 005–007 remain exploratory and their pooled −30.7% token result is not stable evidence. Pilot 008 is deliberately excluded from the triggered-use estimate because the correct behavior under the Skill's own trigger is to skip it; as a forced-on control it worsened total tokens by 40.4% while both arms passed the same full suite. The candidate Skill was tightened to make the applicability gate explicit and to require each additional search to answer a specific unresolved question. This is a hypothesis for the next paired run, not a validated improvement. The goal remains active.


## Local pilot 009: Codex automatic-discovery control

We repeated pilot 008's same localized privacy task with Codex CLI 0.143.0 and `gpt-5.5`, but changed the treatment to place the candidate under project-level `.agents/skills/jev-dev-efficient/SKILL.md` and let Codex discover it normally. The baseline had no project Skill. Skill ran first, then baseline. This task explicitly names the subsystem, behavior, and acceptance checks, so the candidate description says it should not activate. The JSONL contains no explicit skill-load event or skill name; therefore this is a trigger/discovery control, not proof that the Skill body was used.

The two agents made the same one-line implementation change to keep pinned chunks out of the evaluator state. Their initial agent-selected test files differed by one test. We copied the broader regression test file into both isolated fixtures and ran the exact same full test suite after both agent runs; each passed 39/39.

| Measure | Baseline | Skill available | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 251,598 | 375,581 | +49.3% |
| Cached input (subset of input) | 221,696 | 341,376 | +54.0% |
| Output tokens | 3,474 | 3,912 | +12.6% |
| Input + output tokens | 255,072 | 379,493 | +48.8% |
| Tool actions (shell + file changes) | 23 | 24 | +4.3% |
| Model turns | 1 | 1 | tied |
| Wall time | not emitted/captured | not emitted/captured | unavailable |
| Per-run USD cost | not exposed (subscription) | not exposed (subscription) | unavailable |
| Full test suite | 39/39 | 39/39 | tied |

The native Codex event reports `input_tokens` as the total input count and `cached_input_tokens` as a subset, so the cached figure is not added again. We did not capture a monotonic timer in this run. A separate run showed Codex CLI usage reporting was available, but this pair is too noisy and lacks invocation, elapsed-time, and dollar-cost telemetry to estimate Skill effectiveness. It is retained as a cross-model control only.

## Checkpoint after Codex control

Positive Claude pilots 005–007 remain a small, two-task-type sample at −30.7% pooled tokens. Forced Claude pilot 008 increased tokens by 40.4%. Codex pilot 009 did not provide an observable Skill-load event and increased measured tokens by 48.8%, so it cannot be attributed to the Skill body. The candidate applicability gate is still unvalidated in an in-scope, repeated Codex task. The 2x goal remains unmet; a proper follow-up must use a repository-scale diagnosis that matches the trigger, counterbalance order, and capture monotonic runtime as well as model usage.
