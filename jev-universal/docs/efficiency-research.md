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

Positive Claude pilots 005–007 remain a small, two-task-type sample at −30.7% pooled tokens. Forced Claude pilot 008 increased tokens by 40.4%. Codex pilot 009 did not provide an observable Skill-load event and increased measured tokens by 48.8%, so it cannot be attributed to the Skill body. The candidate applicability gate was exercised in an in-scope task in pilots 010–011, but only pilot 010 shows Skill-body evidence and the results do not repeat. The 2x goal remains unmet; follow-ups need repeated observed invocations across task types, counterbalanced order, monotonic runtime, and a pricing basis.


## Local pilot 010: cross-layer dotenv diagnosis (baseline first)

We seeded the same regression into identical package copies: dotenv interpolation was enabled by default, so `${HOME}` inside a valid API key could be expanded before validation. The task reported a symptom across generated Claude/Kimi client configuration, private dotenv loading, and key validation; it required preserving exported-environment precedence, keeping secrets out of config/output, adding coverage, and making no live API request. This matches the Skill's intended cross-component diagnosis trigger. Both runs used Codex CLI 0.143.0 with `gpt-5.5`, the same tool policy and sandbox, and the same task. The Skill fixture exposed the current Skill through `.agents/skills`; baseline had none. Baseline ran first. A monotonic wrapper captured elapsed runtime; Codex does not expose per-run dollar cost on the subscription plan.

Both patches restored non-interpolating dotenv loading; the resulting `cli.py` files were identical. Both full suites passed 39/39. The Skill treatment trace includes the Skill name and body heading, which is evidence that it was read in this run (the CLI has no structured skill-load event).

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 451,559 | 366,027 | −18.9% |
| Cached input (subset of input) | 412,416 | 330,368 | −19.9% |
| Output tokens | 5,611 | 4,507 | −19.7% |
| Input + output tokens | 457,170 | 370,534 | −18.9% |
| Tool actions (shell + file changes) | 33 | 25 | −24.2% |
| Model turns | 1 | 1 | tied |
| Wall time | 137.477 s | 117.770 s | −14.3% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Full test suite | 39/39 | 39/39 | tied |

This is a positive, in-scope single pair, but it is about 1.23x fewer tokens, far short of the 2x target.

## Local pilot 011: counterbalanced repeat

We repeated the same seeded task and runtime setup using fresh fixture copies, this time running Skill first. The Skill treatment trace did not contain the Skill name/body heading, so body invocation is not evidenced for this arm. Its patch introduced a helper around `dotenv_values(interpolate=False)` while baseline changed the existing `load_dotenv` option; both satisfy the behavior, but the treatment did more work. The first agent-selected suite sizes differed (39 versus 40); we copied the broader regression test file into the treatment fixture and then ran the same full suite in both: 40/40 passed.

| Measure | Baseline | Skill available | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 308,358 | 539,155 | +74.9% |
| Cached input (subset of input) | 273,920 | 496,768 | +81.4% |
| Output tokens | 4,559 | 5,785 | +26.9% |
| Input + output tokens | 312,917 | 544,940 | +74.2% |
| Tool actions (shell + file changes) | 29 | 34 | +17.2% |
| Model turns | 1 | 1 | tied |
| Wall time | 115.656 s | 152.378 s | +31.8% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical full test suite | 40/40 | 40/40 | tied |

This is a counterbalanced repeat but not a second confirmed Skill-body invocation. Across the two baseline runs, usage was 770,087 tokens and 253.133 s; across Skill-available runs it was 915,474 tokens and 270.148 s. That combined +18.9% token use and +6.7% runtime must not be presented as a skill-effect estimate because pilot 011 has no evidenced body load. It does show that Skill selection is inconsistent and that outcomes on a repeated task vary substantially.

## Current checkpoint after pilot 011

The first confirmed in-scope Codex treatment (pilot 010) saved 18.9% tokens, 24.2% tool actions, and 14.3% time while matching all tests. This is below the target and has only one confirmed invocation. The counterbalanced pilot 011 was not a confirmed Skill invocation and was worse than baseline. The applicability description was revised to name unfamiliar cross-component failure diagnosis as a trigger while continuing to exclude localized changes with a known source and acceptance checks. That routing change remains unvalidated. Keep the goal active and repeat on multiple task types with observed Skill invocation, identical acceptance gates, counterbalanced order, token telemetry, monotonic elapsed timing, and a recorded pricing basis where available.


## Local pilot 012: revised trigger, Skill-first repeat

We repeated pilot 010's exact seeded dotenv regression on fresh copies after revising the description to explicitly cover unfamiliar cross-component failures. Skill ran first. The Skill/body heading was present in its trace; baseline had no Skill fixture. Both resulting `cli.py` implementations restored the existing `load_dotenv(..., interpolate=False)` option and were identical. The same regression test file was copied into both fixtures after the runs to equalize acceptance coverage; both full suites passed 40/40.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 468,285 | 377,121 | −19.5% |
| Cached input (subset of input) | 421,632 | 339,200 | −19.5% |
| Output tokens | 5,773 | 4,545 | −21.3% |
| Input + output tokens | 474,058 | 381,666 | −19.5% |
| Tool actions (shell + file changes) | 33 | 21 | −36.4% |
| Model turns | 1 | 1 | tied |
| Wall time | 142.032 s | 121.929 s | −14.2% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical full test suite | 40/40 | 40/40 | tied |

Across the two confirmed Skill-body runs (pilot 010 baseline-first and pilot 012 Skill-first), input-plus-output usage fell from 931,228 to 752,200 tokens (−19.2%), elapsed time fell from 279.509 to 239.699 seconds (−14.2%), and tool actions fell from 66 to 46 (−30.3%). This is a repeatable direction on one seeded task type, not evidence across representative task types or of a multi-fold saving. Pilot 011 remains evidence that Skill discovery did not happen consistently before the description change.

## Current checkpoint after pilot 012

The revised description now has two observed Skill-body invocations on the same cross-layer dotenv task, with counterbalanced order and similar token savings (−18.9% and −19.5%). This is materially stronger than the earlier one-shot results but still only one task type, one model, and about 1.24x fewer tokens. Pilot 011's non-invocation and adverse available-Skill result remains a routing failure signal; pilot 009 showed the localized skip case is noisy. No per-run USD cost is available for Codex subscription runs. Next, test a different cross-file failure class with the current Skill while preserving identical security regression gates, then repeat before broad claims. The target of 2x remains unmet.


## Local pilot 013: JWT audience isolation and compatibility audit

We seeded removal of JWT audience validation in fresh package copies. The task asked for end-to-end public OAuth/MCP diagnosis, strict audience isolation, preservation of issuer/expiry/scope checks, local-only test keys, and a full suite. Codex CLI `gpt-5.5` ran baseline first; the updated Skill was available in the treatment, and its name/body heading appeared in the trace. No external issuer or TypeSafe API was contacted.

Both agents restored audience validation and kept the same issuer/expiry/scope checks. The treatment also removed `claims=claims` from the returned `AccessToken`; that unrequested change was not covered by the agent-selected tests. We then applied the same broader 40-test auth suite to both copies, adding a compatibility assertion that a valid `AccessToken` continues exposing its validated `claims` field. Baseline passed 40/40. Treatment passed 39 and failed that assertion (`claims` was `None`). This is a real behavior regression, so the large token/time reduction below does **not** count as a successful Skill result.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 753,076 | 410,900 | −45.4% |
| Cached input (subset of input) | 705,408 | 378,880 | −46.3% |
| Output tokens | 7,423 | 4,066 | −45.2% |
| Input + output tokens | 760,499 | 414,966 | −45.4% |
| Tool actions (shell + file changes) | 43 | 28 | −34.9% |
| Model turns | 1 | 1 | tied |
| Wall time | 193.623 s | 121.771 s | −37.1% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Common 40-test gate | 40/40 | 39/40 | treatment failed compatibility check |

The token and speed reductions are not quality-adjusted gains. This run exposed that the Skill's “smallest patch” instruction needs an explicit preservation rule for existing return contracts and validated data. The Skill was updated accordingly; the fix remains to be tested on a fresh task.

## Current checkpoint after pilot 013

Two confirmed Skill-body runs on the dotenv task saved about 19% tokens with equal tests, in counterbalanced order. A different JWT task showed a much larger apparent reduction but regressed an existing `AccessToken.claims` behavior and failed the common gate. Thus the Skill has not yet demonstrated reliable savings across task types without regressions. Its applicability and preservation instructions have now been revised from observed misses, but those revisions are unvalidated. Continue with fresh tasks and repeats; the 2x goal remains unmet.


## Local pilot 014: preservation rule, counterbalanced JWT repeat

We repeated pilot 013 with the revised Skill and Skill-first order. The updated Skill body was present in the treatment trace. Baseline followed. Both agents restored the configured audience check and retained the existing `AccessToken.claims` field. The implementation files were behaviorally identical apart from the ordering of `issuer` and `audience` keyword arguments. The same treatment-auth regression suite, including a valid multi-audience token and claims preservation assertion, was applied to both copies after the runs; both full suites passed 38/38.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 347,013 | 622,044 | +79.3% |
| Cached input (subset of input) | 314,880 | 577,664 | +83.5% |
| Output tokens | 4,231 | 4,871 | +15.1% |
| Input + output tokens | 351,244 | 626,915 | +78.5% |
| Tool actions (shell + file changes) | 22 | 34 | +54.5% |
| Model turns | 1 | 1 | tied |
| Wall time | 104.746 s | 127.490 s | +21.7% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical full test suite | 38/38 | 38/38 | tied |

The revised preservation instruction prevented the pilot 013 claims regression, but this repeat used substantially more tokens, actions, and time than baseline. It is a correctness success and an efficiency failure. It also shows the positive token result in pilot 013 was confounded by a behavior regression and cannot be used as evidence of savings.

## Current checkpoint after pilot 014

On the dotenv task, two confirmed Skill-body runs saved about 19% tokens with equal tests, in counterbalanced order. On the JWT task, the initial Skill run saved tokens but removed `AccessToken.claims` and failed an added compatibility check; after the preservation rule was added, the next Skill run preserved behavior and passed the common tests but used 78.5% more tokens. Thus correctness improved, but token efficiency is not stable across task types. The 2x target remains unmet. Continue with representative tasks and repeats, retain shared compatibility gates, instrument elapsed time and report the unavailable per-run cost honestly.

## Local pilot 015: MCP public-Origin configuration

This synthetic regression changed the public OAuth resource's allowed Origin from its configured HTTPS scheme to HTTP. It was chosen as a distinct transport-security boundary task; it is not a confirmed production incident. Codex CLI `gpt-5.5` ran baseline first and Skill second. The Skill body was visible in the treatment trace. Both changes derived the trusted public Origin from the configured URL and retained rejection of an untrusted origin. We normalized the auth test file after both runs and ran the exact same non-socket suite in each fixture: 36/36 passed. The full suite's local socket test could not bind `127.0.0.1` in this environment.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 493,152 | 361,490 | −26.7% |
| Cached input (subset of input) | 458,496 | 318,080 | −30.7% |
| Output tokens | 5,980 | 4,249 | −29.0% |
| Input + output tokens | 499,132 | 365,739 | −26.7% |
| Tool actions (commands + file changes) | 37 | 26 | −29.7% |
| Model turns | 1 | 1 | tied |
| Wall time | 158.989 s | 113.650 s | −28.5% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical non-socket suite | 36/36 | 36/36 | tied |

This is a positive one-pair result at about 1.36x fewer tokens. It is synthetic and single-run; it does not establish a general effect.

## Local pilot 016: response-validation to context-selection contract

This synthetic regression weakened the TypeSafe probability-mass check so a distribution totaling 0.90 passed validation and could be consumed by `jev_select_context` to omit unpinned context. It was introduced identically in fresh fixtures and used only local `httpx.MockTransport` responses. The Skill ran first, then baseline, reversing pilot 015's order. The treatment trace includes the Skill body. Both arms restored strict enough distribution validation and passed the same 37-test non-socket gate, including an end-to-end assertion that malformed upstream mass cannot yield a context-omission result. Both changed-file Ruff checks passed. Full-suite collection reached the existing socket-binding test, which the environment denied; a full-repository Ruff run also reported existing import-order findings outside the changed files.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 412,077 | 453,636 | +10.1% |
| Cached input (subset of input) | 377,856 | 419,584 | +11.0% |
| Output tokens | 6,191 | 5,279 | −14.7% |
| Input + output tokens | 418,268 | 458,915 | +9.7% |
| Tool actions (commands + file changes) | 30 | 31 | +3.3% |
| Model turns | 1 | 1 | tied |
| Wall time | 143.803 s | 133.121 s | −7.4% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical non-socket suite | 37/37 | 37/37 | tied |

The Skill made the smaller source change: it tightened the producer's probability-mass tolerance. Baseline also added a defensive consumer check that keeps malformed or contradictory answers. Both satisfy the shared end-to-end safety gate, but their implementations are not identical. The Skill was 7.4% faster while using 9.7% more total tokens and one more tool action, so this is a correctness success and token-efficiency failure.

## Current checkpoint after pilot 016

Two recent confirmed Skill invocations on different synthetic task types produce mixed token results: pilot 015 saved 26.7%, while pilot 016 used 9.7% more than baseline. Both passed their identical, locally runnable correctness gates and both used a different arm order. Runtime favored Skill in both pairs, but two single-run pairs do not demonstrate stable gains; neither approaches 2x. These results reinforce that the Skill's useful differentiator is narrow, evidence-led action with explicit contract preservation, not a reliable token multiplier yet. Continue paired repeats across representative task types, preserve exact usage/action/time telemetry, and do not claim a general saving until the evidence supports it. Codex subscription runs do not expose per-run USD cost.
