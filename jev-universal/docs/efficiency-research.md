# Existing efficiency practices and this Skill's design

This document combines a design review with local pilot benchmark results. Community examples are useful for discovering operational tactics, but individual savings figures are not treated as independently verified results.

## Current evaluation checkpoint (2026-09-21)

The target is at least 2x fewer total input+output tokens on representative development work, with 10x as a stretch goal. The last evaluated revision (commit `48ad1e4`) saved 15.4% and 4.0% in an order-balanced all-pinned task pair and 26.3% in one key-file feature run, but the key-file order-reversed repeat P057 was invalidated by a dataless Python environment hanging during import. Its cross-task reliability and the 2x goal remain unproven. A stricter rule against rediscovering named files is now in the draft and still needs a matched evaluation. Earlier evidence remains mixed: RTK and Pluck pilots did not pass the efficacy gate, and several favorable pairs reversed with order or had quality failures. Do not pool across Skill revisions or treat one task pair as proof. USD cost was unavailable on subscription billing. See the detailed pilots below.

An instrumentation audit also found that pilots 019–021 had placed the candidate under plain `skills/`, not Codex's supported `.agents/skills/` discovery path; traces show manual/late reads in those runs. They are not valid estimates of an automatically invoked Skill and are excluded from the four-pair summary above. Pilot 018 also read the Skill only after repository exploration and is exploratory. Earlier pilots with no Skill-load evidence, late reads, or material behavior/test regressions remain useful for debugging the evaluation method, but not as efficacy evidence. The official [Codex Skills guide](https://developers.openai.com/zh-Hans/docs/build-skills) describes supported locations and progressive loading.

Pilot 026 is an invalid/incomplete pair. Its baseline runner ignored the intended root and ran `rg --files` over the package, then attempted `uv` dependency downloads that the environment blocked. Targeted CLI tests passed, but full test collection failed because the system `mcp` package is incompatible with the repository. No treatment run was made, so this pilot contributes no efficacy estimate. In pilots 027–028, the runner exposed the same preinstalled environment to both arms, and independent full-suite checks used it; treatment agents did not consistently select it. Token use did not improve. See below.

## Patterns worth keeping

- **Targeted retrieval:** search for symbols and inspect matching regions instead of reading whole files. Cap output from unknown logs and commands. This is recommended in community coding-agent guidance such as [Austin Serb's AGENTS.md patterns](https://github.com/Austin1serb/agents-md), which reports a personal ~50% average reduction from a byte-capped output rule; that number is author-reported, not a general result.
- **Optimize the whole session:** avoid redundant reads, tool calls, and user round-trips; don't cut needed context if doing so risks a failed attempt. A [community token-efficiency skill](https://github.com/denfry/claude-skills/blob/main/skills/token-efficiency/SKILL.md) explicitly uses this total-cost framing and keeps detailed guidance/reference material separate from its tiny always-on contract.
- **Progressive disclosure:** keep the trigger and core rules short; load examples or specialized procedures only when relevant. GitHub's [Copilot skills guidance](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) similarly recommends repository instructions for simple always-relevant rules and Skills for detailed task-specific instructions. The 2026 [SkillReducer preprint](https://arxiv.org/abs/2603.29919) reports that compressing skill descriptions and deferring non-core material reduced its sampled skill bodies while retaining or improving evaluated function; this is evidence about skills in that benchmark, not a result for this Skill.
- **Small, purposeful validation:** verify changed behavior and acceptance criteria, but do not rerun unrelated checks without a reason. Keep successful output summarized and preserve actionable failure details.

## Additional GitHub research: mechanisms with direct token pathways

- **RTK (Rust Token Killer):** its documented hook rewrites supported shell commands and filters returned Bash output before it enters model context. Its “up to 90%” figure refers to shell-output bytes, not total session tokens or cost; the estimate uses bytes/4. Important version distinction: the stable v0.48.0 binary tested locally does **not** include the documented Codex hook; `rtk init --codex` only added `AGENTS.md`/`RTK.md` prompting command prefixes. Codex hook support is in the project's newer development line, so claims about it must name the version/channel. RTK is an optional local tool, not portable Skill behavior. See [RTK README](https://github.com/rtk-ai/rtk/blob/develop/README.md), [Codex hook contract](https://github.com/rtk-ai/rtk/blob/develop/hooks/codex/README.md), and [savings boundaries](https://github.com/rtk-ai/rtk/blob/develop/docs/guide/resources/savings-explained.md).
- **Vix virtual filesystem:** the project reports 20–50% fewer code-reading tokens by presenting Tree-sitter-minified source that removes whitespace while preserving syntax. This targets code payload, where a prompt cannot control all overhead; the claim is project-reported and its benchmark says it is observational, so it needs independent validation before adoption. See [Vix's VFS description](https://github.com/get-vix/vix#virtual-file-system).
- **Forge:** its public small benchmark reports 7.5% lower weighted token units overall, but +2.9% on small tasks and +16.3% on medium tasks, with savings only on its large fixture (−23.7%). The practical signal is that workflow overhead is paid up front and pays off only when it avoids enough exploration; do not add phase ceremonies to short tasks. These are project-authored results, not an independent replication. See [Forge's benchmark](https://github.com/daanavcoding/forge#original-benchmark-briefly).
- **Token-efficiency Skills:** examples such as [denfry/claude-skills](https://github.com/denfry/claude-skills/tree/main/skills/token-efficiency) consolidate reusable habits: answer-first prose, batch independent tool calls, targeted reads, no redundant rereads, and preserve correctness. Its deterministic reminder depends on Claude Code hooks; a model-invoked portable Skill can be ignored, as our own traces also demonstrate. These patterns are reasonable hypotheses, not measured savings by themselves.
- **Symbol-aware retrieval (Pluck):** Pluck's authors report 84–88% fewer tokens for eligible code reads, 23% fewer in a five-query session-dedup bench, and 25% fewer tokens in one selected code-fix task. These are project-authored measurements, not independent replication; broad LLM-in-the-loop results are still described as future work. The v0.6.0 macOS ARM64 CLI was independently installed in the ignored harness without account/API credentials (asset SHA-256 `458c1af13e11f73763d0a5caca34c923b10f8d7ce595dbc3c99a951afafd970a`). That release describes its search as BM25; newer semantic-search claims on the repository's main branch are not part of the tested binary. On our Zed-task snapshot, `pluck search "client_config zed context_servers" -k 2` returned the complete target function in 750 bytes versus 5,318 bytes for a whole-file read (−85.9% for that retrieval); `pluck read` returned only a 172-byte outline (−96.8%, but not the function body). It did not shrink `tests/test_cli.py` (2,611 bytes stayed unchanged), and useful Chinese-guide retrieval still required exact grep. Thus the portable lesson is symbol/line-scoped retrieval and avoiding duplicate chunks, with raw tests and docs when their full content matters—not accepting a headline percentage or requiring Pluck. The full Skill candidate in pilot 034 never invoked the installed CLI, so it does not validate this method end to end. See [Pluck's measured scenarios](https://github.com/hunhee98/pluck#performance--token-savings) and [retrieval design](https://github.com/hunhee98/pluck#why-pluck).
- **Task-induced context projection (context-kernel):** this project proposes starting with task symptoms/symbols, then including relevant dependency closure, callers, and tests; omitted regions remain discoverable as recoverable “page faults” instead of being treated as irrelevant forever. Its README reports −79% tokens in one live Claude Code session and 100% sufficiency on two 60-case fault benchmarks. These are project-authored results and its automatic hooks target Claude Code; the method, not the integration, is the portable hypothesis. It suggests a more precise version of targeted retrieval: build a task-indexed working set, expand only when acceptance evidence exposes a gap, and keep exclusions recoverable. We should independently test this on multiple development tasks. See [context-kernel's method and benchmarks](https://github.com/Pinperepette/context-kernel).

These results show deterministic filtering can reduce command-output size, but more work must target repeated input context and redundant agent turns to reduce full-session usage. Keep test output unfiltered when warnings matter. Evaluate byte reduction and complete session token usage separately; never infer total-session savings from filtered-output percentages.

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

## Local pilot 017: counterbalanced repeat of pilot 016

We repeated the same seeded probability-mass/context-selection task on fresh copies, this time running baseline first and Skill second. This reverses pilot 016's order. The Skill body was present in the treatment trace. Both implementations rejected a malformed 0.90 probability total, and both passed the exact same 37-test non-socket suite and changed-file Ruff checks. The full suite again hit the environment's denied loopback socket test. The baseline run needed a syntax correction after its first source edit and spent more time on repeated verification; this is included in the measured process duration, so the runtime comparison is especially noisy.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 414,658 | 354,136 | −14.6% |
| Cached input (subset of input) | 385,024 | 322,432 | −16.3% |
| Output tokens | 4,849 | 3,961 | −18.3% |
| Input + output tokens | 419,507 | 358,097 | −14.6% |
| Tool actions (commands + file changes) | 26 | 24 | −7.7% |
| Model turns | 1 | 1 | tied |
| Wall time | 274.368 s | 104.703 s | −61.8% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical non-socket suite | 37/37 | 37/37 | tied |

The repeat favors the Skill on tokens, but pilot 016 on the same task type went the other direction (+9.7% tokens for Skill). Pooling only this counterbalanced task-type repeat gives baseline 837,775 versus Skill 817,012 total tokens, a 2.5% reduction. Tool actions are nearly tied (56 versus 55). The pooled runtime difference is −43.1%, but pilot 017 includes a baseline syntax repair and extra verification, so it is not reliable evidence of a general speed effect. Two repetitions do not demonstrate stable efficiency.

## Current checkpoint after pilot 017

Across three recent Skill invocations on two synthetic task types, results remain mixed: pilot 015 saved 26.7%, pilot 016 used 9.7% more tokens, and the counterbalanced pilot 017 repeat saved 14.6%. The two repeats of the response-validation task pool to only 2.5% fewer tokens, with nearly tied tool actions. All paired gates passed, but these small local trials do not establish a stable gain, and no result approaches the 2x target. Keep the Skill goal active and continue repeated pairs across representative development tasks. Codex subscription runs do not expose per-run USD cost.

## Local pilot 018: Zed client-config feature

This is the first feature-development pair after expanding the Skill trigger to include multi-file work with unfamiliar interface contracts. The task added a Zed-native `context_servers` output to the CLI, tests, and English/Chinese setup guides, using Zed's [official MCP configuration shape](https://zed.dev/docs/ai/mcp). The Skill ran first; its body was visible in the trace. The two implementations passed the same 39-test non-socket suite after normalizing the CLI test file, and the changed-file Ruff checks passed. The full test suite in the restricted agent environment was blocked by loopback socket permissions; the final integrated checkout subsequently passed all 40 tests outside that restriction.

The Skill implementation preserved existing Chinese setup instructions for Claude, Kimi, ZCode, and Codex while adding Zed. Baseline replaced that multi-client section with Zed-only instructions, dropping existing guidance, though it also added a static `configs/zed.json` example. Both generated configurations used an empty `env` object and passed only the private env-file path in arguments; no API key or live service was used. The final public implementation uses the Skill group's preservation-friendly documentation and also includes the static Zed example as a separately reviewed addition.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 618,806 | 635,761 | +2.7% |
| Cached input (subset of input) | 569,088 | 582,016 | +2.3% |
| Output tokens | 7,240 | 5,893 | −18.6% |
| Input + output tokens | 626,046 | 641,654 | +2.5% |
| Tool actions (commands + file changes + web searches) | 36 | 29 | −19.4% |
| Model turns | 1 | 1 | tied |
| Wall time | 170.496 s | 148.031 s | −13.2% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical non-socket suite | 39/39 | 39/39 | tied |

This feature pair improved elapsed time and tool actions but used 2.5% more total tokens. The Skill's documentation-preservation behavior avoided a baseline regression, but the paired result still does not demonstrate a token saving.

## Local pilot 019: counterbalanced repeat of Zed client-config feature

We repeated pilot 018 from the same source commit and with the same prompt, this time running baseline first and Skill second. The Skill body was present in the treatment trace. Both variants produced the requested Zed `context_servers` schema; independent common verification passed the identical full 40-test suite in both copies. The two changed-file Ruff checks reported the same existing unsorted-import finding in `tests/test_cli.py`, so neither arm receives a lint pass. No service or API key was used. Per-run USD cost was unavailable.

The Skill edit regressed adjacent English setup documentation: it removed the general instruction to merge only the new entry and keep existing servers/settings. The baseline retained that guidance. This is a no-regression failure even though both implementations passed tests. The Skill also used more tokens and the action count tied.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 453,828 | 489,162 | +7.8% |
| Cached input (subset of input) | 402,048 | 435,200 | +8.2% |
| Output tokens | 5,052 | 5,220 | +3.3% |
| Input + output tokens | 458,880 | 494,382 | +7.7% |
| Tool actions (commands + file changes) | 28 | 28 | tied |
| Model turns | 1 | 1 | tied |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical full test suite | 40/40 | 40/40 | tied |

Across the two order-reversed repetitions of this feature task, baseline used 1,084,926 total tokens and Skill used 1,136,036, or 4.7% more for Skill. Pilot 018 had fewer Skill tool actions and elapsed time, but this repeat ties actions; elapsed time was not retained for pilot 019. The paired evidence is mixed on process signals and negative on pooled tokens. We added a specific adjacent-documentation preservation check to the Skill; that revision requires a fresh evaluation before drawing conclusions.

## Local pilot 020: retest after adding documentation-preservation rule

We repeated the same Zed feature task from the same source commit with the revised Skill, running Skill first and baseline second. This reverses pilot 019's order. The new rule was visible in the Skill trace. Both outputs retained the existing Claude, Kimi, ZCode, and Codex setup guidance while adding Zed instructions; neither deleted the general merge-only/preserve-other-settings guidance. Both passed the same independently run full 40-test suite. The changed-file Ruff check reported the same existing import-order finding in each arm. Per-run USD cost is unavailable under subscription billing.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (including cached) | 507,182 | 526,338 | +3.8% |
| Cached input (subset of input) | 461,824 | 477,824 | +3.5% |
| Output tokens | 4,861 | 5,418 | +11.5% |
| Input + output tokens | 512,043 | 531,756 | +3.8% |
| Tool actions (commands + file changes) | 26 | 27 | +3.8% |
| Model turns | 1 | 1 | tied |
| Wall time | 127.079 s | 136.022 s | +7.0% |
| Per-run USD cost | unavailable (subscription) | unavailable (subscription) | — |
| Identical full test suite | 40/40 | 40/40 | tied |

The revised rule prevented the documentation regression seen in pilot 019, but this is one corrected-quality repetition, not proof of a general quality improvement. It cost 3.8% more total tokens and 7.0% more time on this task. Across pilots 018–020, baseline totals 1,596,969 tokens and the respective Skill versions total 1,667,792 (+4.4%); because the Skill changed after pilot 019, this pooled figure is descriptive only, not an estimate for one fixed treatment.

## Historical checkpoint after pilot 020 (superseded)

The Skill still has no demonstrated stable token savings. Recent development-task pairs show +2.5%, +7.7%, then +3.8% token use for Skill; the revised documentation guard recovered the adjacent-doc quality regression but adds overhead and has only one post-change trial. Other tasks remain mixed, including two counterbalanced response-validation runs that pool to 2.5% fewer tokens. The minimum 2x target and 10x stretch target remain unmet by a wide margin. Continue with representative task pairs and counterbalanced order, but avoid adding broad workflow rules without evidence that their quality benefit justifies their measured overhead. Track usage, actions, elapsed time, and available cost; keep shared acceptance gates.

## Local pilot 022: Zed documentation/config task (baseline first)

This was a corrected-location, explicit-from-start Skill run on the same Zed task and source snapshot as pilot 018. Both used Codex CLI with `gpt-5.5`; baseline ran first. Both implementations passed an independently normalized 40/40 common suite. The Skill passed Ruff on its changed tests; the baseline hit the existing I001 import-order finding. The Skill also removed a Zed-specific no-secret-echo assertion from its task-created test, a security-test preservation failure. USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 867,372 (808,576) | 922,779 (863,488) | — |
| Output tokens | 6,296 | 5,961 | — |
| Input + output tokens | 873,668 | 928,740 | +6.3% |
| Tool actions | 37 | 36 | −2.7% |
| Wall time | 165.415 s | 161.400 s | −2.4% |
| Full common suite | 40/40 | 40/40 | tied |

The process signals improved slightly while total token use increased; removal of the security assertion is a no-regression failure.

## Local pilot 023: counterbalanced repeat of the Zed task

Same source and prompt, Skill first, baseline second, same model and explicit Skill location/loading. After copying the treatment CLI test into the baseline copy, both passed the same 40/40 suite. Changed-file Ruff reported the same existing import-order issue in both. The Skill added an unrequested static `configs/zed.json`; no important behavior regression was found. USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 540,381 (474,112) | 581,504 (535,296) | — |
| Output tokens | 4,850 | 5,031 | — |
| Input + output tokens | 545,231 | 586,535 | +7.6% |
| Tool actions | 25 | 26 | +4.0% |
| Wall time | 125.332 s | 131.393 s | +4.8% |
| Full common suite | 40/40 | 40/40 | tied |

## Local pilot 024: documentation/test preservation retest

Same Zed task, baseline first, with the then-current preservation Skill. Both normalized full suites passed 41/41; both changed-file Ruff checks had the same existing I001 failure. The treatment kept the no-secret-echo test, but rewrote the Chinese Zed guidance and deleted `test_zed_config_preserves_paths_with_spaces`, an explicit requirement. This is a no-regression failure. USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 525,212 (487,168) | 625,979 (571,776) | — |
| Output tokens | 5,530 | 6,618 | — |
| Input + output tokens | 530,742 | 632,597 | +19.2% |
| Tool actions | 27 | 37 | +37.0% |
| Wall time | 140.488 s | 163.812 s | +16.6% |
| Full common suite | 41/41 | 41/41 | tied |

This task's repeated pairs are consistently token-negative for the Skill, and pilot 024 also lost an acceptance test and neighboring guidance.

## Local pilot 025: cross-layer invalid probability-mass bug

This different task seeded invalid upstream probability mass that could cause a context selector to drop a pinned critical chunk. Both fixtures were identical, Skill ran first, and the Skill was explicitly loaded as the first repository operation. After normalizing the suite, both full common suites passed 39/39. The Skill replaced two direct unit regressions with one end-to-end `MockTransport` validation through the real selector; the shared suite passed, and the end-to-end test covered producer and consumer behavior. Both changed-file Ruff checks showed the same existing I001 failure. No live API was contacted; USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 447,555 (413,696) | 451,781 (417,792) | — |
| Output tokens | 5,019 | 3,867 | — |
| Input + output tokens | 452,574 | 455,648 | +0.7% |
| Tool actions | 28 | 25 | −10.7% |
| Wall time | 127.188 s | 118.913 s | −6.5% |
| Full common suite | 39/39 | 39/39 | tied |

This is encouraging on actions and time, nearly tied on tokens, and far from a multi-fold token reduction.

## Checkpoint after pilots 022–026 (superseded by 027–028)

Valid explicit-load treatment pairs so far comprise three Zed feature trials and one cross-layer bug trial. They do not establish token savings, much less the 2x threshold. The Zed trials consistently used more tokens; the one different bug task nearly tied on tokens while using fewer actions and less time. Pilot 026 failed its runner/setup and has no treatment arm, so it is excluded. The next useful step is to repair the runner and dependency environment, then counterbalance multiple task types with the exact current Skill and no acceptance/test deletions. Do not pool across Skill revisions as if they were one treatment.

## Local pilot 027: compact Skill candidate, Zed feature (baseline first)

We shortened repeated workflow instructions and emphasized bounded retrieval, compact output, minimal additive edits, and stopping after one verification pass. Same Zed feature prompt and source snapshot; baseline ran first, then Skill. Both arms had a symlink to the same existing project venv, although the agents did not use it consistently during their own checks. Independent common verification later passed the same full 40/40 suite in both arms. The Skill rewrote the Chinese guide section and removed a Zed-specific assertion that the generated config never echoes a secret. This is a safety-test preservation failure. USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 498,700 (437,632) | 695,770 (643,968) | — |
| Output tokens | 5,909 | 5,769 | — |
| Input + output tokens | 504,609 | 701,539 | +39.0% |
| Tool actions | 38 | 40 | +5.3% |
| Wall time | 163.790 s | 156.802 s | −4.3% |
| Same baseline test suite against both implementations | 40/40 | 40/40 | tied |

## Local pilot 028: environment and test-preservation rules, counterbalanced

We strengthened the candidate with explicit instructions to retain existing tests and avoid implicit dependency installers; Skill ran first, baseline second. It still tried `uv` and multiple Python/test commands instead of using the shared venv. Both independently passed the same full 40/40 suite; changed-file Ruff checks reported the same pre-existing I001 import-order issue in each. The Skill retained the task's CLI and schema assertions, while its Chinese guide narrowed/reworked the local-client section. USD cost was unavailable.

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 410,023 (371,712) | 591,558 (541,440) | — |
| Output tokens | 5,095 | 5,550 | — |
| Input + output tokens | 415,118 | 597,108 | +43.8% |
| Tool actions | 27 | 37 | +37.0% |
| Wall time | 145.003 s | 137.432 s | −5.2% |
| Same baseline test suite against both implementations | 40/40 | 40/40 | tied |

These are different Skill revisions, so don't pool them as one treatment. Both versions were faster in this particular task but materially more expensive in total tokens; 027 also failed safety-test preservation. The Skill instructions were visible in the treatment traces, but the tool trajectory did not reliably follow them. Further text-only instruction edits have diminishing credibility. Next experiments should isolate concrete mechanisms such as bounded shell output or a simpler deterministic runner, with the same commands/environment made explicit in both task arms. A tool-action reduction alone is not a token-saving result.

## Local pilot 030: RTK v0.48.0 instructions (invalid for filter efficacy)

We reran the same Zed task from identical Git snapshots with Codex `gpt-5.5`, baseline first. The treatment added RTK's generated `AGENTS.md` and `RTK.md` guidance, without changing the Jev Skill or task prompt. Both implementations passed the exact same full test suite: 40/40. Their application changes were materially equivalent. However, the treatment trace contains zero `rtk` invocations: the agent ran ordinary `uv run pytest` commands. Thus these numbers measure run variance plus an unheeded instruction, not RTK's output filter; they are excluded from efficacy estimates. A first baseline attempt used a read-only sandbox and is also excluded.

| Measure | Baseline | RTK instructions | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 561,209 (512,640) | 530,188 (478,464) | — |
| Output tokens | 4,155 | 4,566 | — |
| Input + output tokens | 565,364 | 534,754 | −5.4% (not attributable) |
| Tool actions / shell commands | 21 / 16 | 21 / 16 | tied |
| Wall time | 111.629 s | 120.829 s | +8.2% |
| Same baseline test suite | 40/40 | 40/40 | tied |

In a separate local command-output check using RTK v0.48.0, output bytes changed as follows: `pytest -q tests`, 908→18 (−98.0%); `ruff check src tests`, 1,518→372 (−75.5%); `git log -20`, 824→824; `rg --files`, 252→252; targeted `rg` search, 798→798. Across these selected commands: 4,300→2,264 bytes (−47.3%). These are command-output bytes, not full agent-session token counts, and the sample is small and deliberately includes both filtered and unchanged commands. A synthetic passing-test fixture also showed a caveat: RTK hid a warning while tests passed (496→17 bytes); on a failing fixture it retained the assertion marker, file, and nonzero exit status (723→265 bytes). Treat filtered success output as lossy and inspect raw output when warnings are relevant. Reproduce these observations with the ignored local harness before generalizing.

Hook feasibility check: the official macOS ARM64 asset for RTK tag `dev-0.50.0-rc.444` had SHA-256 `57e799a7b74a81bbee13ce14e3292acba52bd36f56b0a29c1efe41c50fc09033`. Despite the prerelease tag, the binary reports `rtk 0.48.0`. Pilot 031 below verifies end-to-end execution in Codex. The project's hook documentation notes project hooks require trust; it also warns that Codex classifies the rewritten `rtk ...` command, which can affect approval prompts and mutation detection. These measurements still do not establish general total-session token savings.

## Local pilot 031: Codex RTK hook on a warning-bearing test run

This isolated microtask paired the exact same two-test Git fixture, `gpt-5.5`, prompt, command, workspace-write sandbox, and environment, with baseline first. The treatment added RTK `dev-0.50.0-rc.444` as a project `PreToolUse` hook. We bypassed hook trust only for this disposable fixture after inspecting the hook and verifying the official release asset checksum; no global Codex settings were changed. The JSONL proves the hook rewrote the requested `pytest -q tests` command to `rtk pytest -q tests`.

| Measure | Baseline | RTK hook | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 29,531 (23,296) | 29,538 (23,296) | +0.02% |
| Output tokens | 144 | 111 | −22.9% |
| Input + output tokens | 29,675 | 29,649 | −0.09% |
| Tool actions | 1 | 1 | tied |
| Wall time | 10.888 s | 11.462 s | +5.3% |
| Test outcome | 2 passed, 1 warning | 2 passed, warning hidden | regression |
| Command output bytes | 517 | 17 | −96.7% |
| USD cost | unavailable (subscription) | unavailable (subscription) | — |

RTK compressed the command output substantially, but this task saved only 26 total session tokens and took longer. More seriously, it removed the warning text and the agent reported “Warnings: none reported.” This is a concrete correctness regression, so the hook is not safe as a blanket test-output filter. The result is one deliberately tiny task pair, not a general efficacy estimate; repeat on representative development work only with warning preservation included as an acceptance criterion.

Mitigation check: adding `[hooks]\nexclude_commands = ["pytest"]` to the isolated RTK config caused the Codex hook to leave `pytest -q tests` unchanged; the same test run then preserved the warning and the agent reported it correctly. In a direct hook protocol check, `git status --short` was still rewritten to `rtk git status --short`, while `uv run pytest -q tests` was excluded. Against the baseline row above, this safe-config run used 29,636 input (27,392 cached) plus 148 output tokens (29,784 total, +0.37%), took 11.257 s (+3.4%), and emitted the same 517 output bytes. This restores test-output fidelity but gives no saving on tests; any benefit from other filtered commands remains to be measured in a representative coding task. RTK documents `exclude_commands` in its [configuration guide](https://github.com/rtk-ai/rtk/blob/develop/docs/guide/getting-started/configuration.md).

## Local pilot 032: Jev Skill plus RTK hook on Zed feature work

This is a representative cross-file coding task: add Zed MCP config support, tests, and English/Chinese setup guidance. Both arms used Codex `gpt-5.5`, the same prompt, the Jev Skill from identical source commit `e371db4`, the same preinstalled Python environment, and `workspace-write`. To counterbalance the earlier baseline-first trials, RTK ran first and baseline second. The treatment installed only the project hook (no RTK awareness instructions) and used an isolated RTK config with `exclude_commands = ["pytest"]`; tests therefore ran raw and kept warnings. The trace shows six actual rewrites covering `rg` and Git status/diff commands. `sed` and Python/test commands were not rewritten.

| Measure | RTK hook | Baseline | Change with RTK |
|---|---:|---:|---:|
| Input tokens (cached subset) | 697,057 (648,064) | 623,856 (555,776) | +11.7% |
| Output tokens | 5,153 | 4,958 | +3.9% |
| Input + output tokens | 702,210 | 628,814 | +11.7% |
| Shell commands / file-change actions | 20 / 5 | 19 / 5 | +4.2% combined actions |
| Aggregate shell output bytes | 47,752 | 70,118 | −31.9% |
| Wall time | 147.794 s | 199.265 s | −25.8% |
| Same common non-socket suite | 39/39 | 39/39 | tied |
| USD cost | unavailable (subscription) | unavailable (subscription) | — |

Both implementations passed the same 39-test common suite and the changed-file Ruff check. Each agent also reported 39 passed and one loopback-socket test failure in the full suite under this sandbox; that environmental failure was excluded from the common non-socket suite. The treatment's code and user-visible behavior were materially equivalent, with no test/security assertion loss found in the focused diff. The hook reduced aggregate command-output bytes by 31.9% and finished faster, but used 11.7% more total session tokens despite making only one additional shell call. This single pair does not establish that the hook caused the token increase, but it does show that large reductions in command-output bytes did not translate to lower total session tokens in this run. RTK alone is therefore not an effective Jev Skill substitute or evidence for the 2x target; further runs must repeat on this task type and test a context-reducing method that also limits redundant searches.

## Local pilot 034: optional Pluck retrieval wording (invalid for retrieval efficacy)

This pair reused the exact Zed feature task and initial application snapshot `185ec711`, Codex `gpt-5.5`, prompt, workspace-write sandbox, and preinstalled Python environment. Baseline ran first; the candidate ran second. The candidate Skill said to use Pluck if the local CLI was available, otherwise fall back to bounded `rg`. The Pluck v0.6.0 binary was on `PATH` and its local index was prebuilt in an ignored directory. However, the candidate trace contains zero Pluck commands: it used `sed`, `rg`, and built-in reads. Therefore this is not an evaluation of Pluck's code-aware retrieval.

| Measure | Baseline Skill | Pluck-wording candidate | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 523,103 (476,160) | 443,072 (397,952) | −15.3% |
| Output tokens | 5,219 | 4,530 | −13.2% |
| Input + output tokens | 528,322 | 447,602 | −15.3% |
| Shell commands / file changes | 18 / 4 | 17 / 4 | −4.5% combined |
| Aggregate shell output bytes | 57,992 | 55,752 | −3.9% |
| Wall time | 134.675 s | 119.983 s | −10.9% |
| Same baseline non-socket suite | 40/40 | 40/40 | tied |
| Changed-file Ruff | I001 | I001 | tied |
| USD cost | unavailable (subscription) | unavailable (subscription) | — |

The token decrease cannot be accepted as a success: the candidate deleted `test_zed_config_preserves_executable_and_argument_paths_with_spaces`, replacing it with env-file path coverage that does not exercise a custom executable path. Both passed the common 40-test suite because it used the baseline test files against each implementation; the candidate's own focused diff reveals the missing acceptance coverage. This is a correctness/coverage regression. It also shows the Skill's existing additive-preservation rule did not prevent a deletion. Do not use this pair as Pluck evidence or as a valid no-regression efficacy result; the numeric decrease is exploratory only. A future candidate needs a clearer local-tool invocation rule and a hard acceptance-test preservation gate, then an order-reversed repeat.

## Local pilot 035: explicit Pluck invocation wording (invalid; candidate ran first)

This pair reused the same Zed feature prompt, model, source snapshot, and local Python environment as pilot 034, with candidate first and baseline second. The candidate's Skill explicitly said to check for Pluck, build its local index, then use symbol search; `pluck grep` should use named paths, not `--repo`. Trace review shows the agent checked the binary but did not index or search. It issued one malformed `pluck grep ... --repo .` (exit 2), then fell back to `rg`/file reads. Thus Pluck did not contribute retrieval savings.

| Measure | Baseline Skill (second) | Candidate (first) | Change |
|---|---:|---:|---:|
| Input tokens (cached subset) | 404,408 (357,248) | 600,669 (543,744) | +48.5% |
| Output tokens | 4,006 | 5,241 | +30.8% |
| Input + output tokens | 408,414 | 605,910 | +48.4% |
| Shell commands / file changes | 18 / 4 | 19 / 5 | +9.1% combined |
| Aggregate shell output bytes | 60,838 | 80,418 | +32.2% |
| Wall time | 119.449 s | 136.078 s | +13.9% |

Both agents report 12 focused CLI tests and the same 39-pass/one socket-bind environment failure in the full suite. But the candidate's changed test file omitted the pre-existing executable-and-arguments-with-spaces acceptance case; it added env-file path coverage instead. The baseline's own test retains the omitted case, so running only the baseline common suite against both would again mask this regression. Pilot 035 therefore fails both the retrieval-invocation and test-preservation gates. Its larger token count is not evidence that Pluck increases cost; this is a failed Skill candidate. Next evaluation should prefer a simpler, enforceable retrieval tactic (bounded symbol search and no duplicate reads) and compare the exact acceptance-test set before interpreting scores.

## Local pilots 038–039: targeted retrieval and bounded validation

These used the same Zed config task, `gpt-5.5`, prompt, clean Git starting point, and local test environment. Pilot 038 ran baseline then candidate; pilot 039 ran candidate first. Both loaded the Skill at their first operation, and both retained original client test cases while adding Zed coverage. The test-preservation wording changed between candidate revisions, so 039 is not a strict order-reversed repeat of 038. Independent full-suite runs passed both arms in both pairs (40/40 each). No API keys or services were used.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 038 | baseline → candidate | 860,304 | 573,972 | −33.3% | 30 → 25 (−16.7%) | 149.046 → 153.716 s (+3.1%) |
| 039 | candidate → baseline | 669,920 | 713,285 | +6.5% | 30 → 22 (−26.7%) | 132.904 → 144.189 s (+8.5%) |

Cached input was 799,744/855,154 baseline/candidate in 038 and 658,944/708,082 in 039; output tokens were 5,150/5,216 in 038 and 4,880/5,203 in 039. Aggregate shell output fell 19.5% in 038 and 1.7% in 039. USD cost was unavailable. Both pairs are exploratory, not proof; setup retries persisted despite the Skill's prose-only limit.

## Local pilots 040–043: key-file path task

The task was to support `~/...` in `TYPESAFE_API_KEY_FILE`, retain precedence and generic errors, add tests, and document the syntax. All clean pairs used `gpt-5.5`, the same prompt/source snapshot, and candidate Skill revision C (task-indexed working set plus explicit test preservation). Candidate was second in 040 and first in 043. Both preserved all tests from the starting commit and both arms passed the full locally available suite. Pair 041 is excluded: its setup accidentally carried forward task-generated tests. Pair 042 is excluded from efficacy because the candidate rewrote an existing absolute-path test to cover only `~/`, losing prior path coverage.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 040 | baseline → candidate | 684,300 | 490,714 | −28.3% | 31 → 23 (−25.8%) | 162.397 → 123.827 s (−23.7%) |
| 043 | candidate → baseline | 536,410 | 600,877 | +12.0% | 26 → 29 (+11.5%) | 113.863 → 127.726 s (+12.2%) |

Cached input was 640,640/452,736 baseline/candidate in 040 and 496,384/557,568 in 043; output tokens were 5,710/4,893 and 4,399/4,568, respectively. Aggregate shell output fell 26.0% in 040 and 2.4% in 043. P040's full suite passed 40/40 baseline and 41/41 candidate; P043 passed 40/40 baseline and 39/39 candidate. The differing counts reflect agents adding different numbers of new tests; the candidates did not remove starting-commit tests. Ruff reported the same existing I001 import-order issue in both arms of each pair. USD cost was unavailable. This opposite result under order reversal does not meet the repeatability gate.

## Local pilots 044–045: batched reads and checks

These used the same key-file task, source snapshot, `gpt-5.5`, and Skill revision D, which added explicit batching of independent initial reads and verification. P044 ran candidate first; P045 baseline first. Both had clean starting trees and the same environment. Neither is valid efficacy evidence: P044's candidate passed 41 tests but its independent Ruff check found a new I001 import-order failure that the baseline arm fixed. P045's candidate passed 38 tests versus 40 for baseline because it repurposed the existing absolute-path test to cover `~/`, losing the old path case; the Skill now explicitly forbids repurposing old tests.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 044 | candidate → baseline | 819,573 | 497,628 | −39.3% | 34 → 29 (−14.7%) | 165.422 → 142.089 s (−14.1%) |
| 045 | baseline → candidate | 536,391 | 611,120 | +13.9% | 26 → 24 (−7.7%) | 109.509 → 131.497 s (+20.1%) |

Cached input was 770,816/457,472 baseline/candidate in 044 and 498,816/566,400 in 045; output tokens were 5,909/5,744 and 4,148/4,828. Aggregate shell output fell 16.8% in 044 and rose 31.5% in 045. P044 full tests passed 40/40 baseline and 41/41 candidate; P045 passed 40/40 baseline and 38/38 candidate. Ruff passed baseline and failed candidate in 044; it failed baseline and passed candidate in 045, but the latter candidate still regressed test coverage. The savings changed sign with order and neither pair clears the quality gate. USD cost was unavailable.

## Local pilots 046–047: calibrated key-file task

These used the same key-file change task, `gpt-5.5`, clean Git snapshot, and Skill revision E. The task prompt supplied both arms the exact already-installed pytest and Ruff commands, avoiding interpreter/network discovery as a source of setup variance. P046 ran baseline then candidate; P047 reversed the order. Both candidates preserved existing test inputs and assertions, added new cases, and passed an independent common-environment full suite (39/39) and Ruff. No TypeSafe calls or real credentials were used.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 046 | baseline → candidate | 286,520 | 234,013 | −18.3% | 15 → 15 (0%) | 86.919 → 83.419 s (−4.0%) |
| 047 | candidate → baseline | 436,783 | 522,575 | +19.6% | 20 → 27 (+35.0%) | 118.356 → 133.064 s (+12.4%) |

Cached input was 260,608/205,568 baseline/candidate in 046 and 404,224/483,456 in 047; output tokens were 3,036/3,421 and 4,327/5,079. Aggregate shell output fell 1.6% in 046 and rose 30.7% in 047. USD cost was unavailable. Even with setup paths fixed in the shared prompt and no test/lint regression, total-token results reversed under order balance. Revision E has not demonstrated stable savings.

## Local pilots 048–049: targeted lookup rules

P048–049 continued the calibrated key-file task while tightening known-symbol search behavior. The candidate saved 18.3% in P046 but used 19.6% more in P047; new instructions did not make this pair stable. In P048, candidate used 7.0% more tokens despite fewer actions, and broader command output grew 32.3%. In P049, candidate used 110.6% more tokens and took 70.3% longer, with both arms still passing 39 tests and Ruff. Traces showed that an exact symbol lookup was followed by broad searches and extra documentation work. These valid-quality pairs do not establish savings.

| Pair | Candidate order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 048 | second | 356,699 | 381,812 | +7.0% | 20 → 16 | 87.124 → 100.600 s (+15.5%) |
| 049 | first | 255,182 | 537,368 | +110.6% | 14 → 29 | 81.486 → 138.751 s (+70.3%) |

## Local pilots 050–051: batched cross-file edits

These used the same key-file task, clean source snapshot, model, prompt, and Skill revision H; the order was reversed in P051. Both candidate arms preserved original test cases, added coverage, passed the independently checked 39-test suite and Ruff. Candidate grouped related edits into two file-change events versus six for baseline. The repeated savings and runtime reductions are encouraging for this task, but aggregate shell output was higher in P050, the task was only one narrow configuration/documentation change, and no independent task type has confirmed the effect. Keep the goal open.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 050 | baseline → candidate | 441,541 | 344,980 | −21.8% | 23 → 18 | 116.451 → 104.072 s (−10.7%) |
| 051 | candidate → baseline | 442,593 | 238,612 | −46.1% | 17 → 14 | 102.107 → 90.372 s (−11.5%) |

Cached input/output were 410,368/3,960 baseline and 311,168/4,270 candidate in P050; 407,936/3,587 baseline and 209,664/3,542 candidate in P051. Shell output bytes changed +48.4% in P050 and −18.0% in P051. Subscription billing did not provide per-run USD cost. P050 and P051 are not evidence for a 2x result or for other development task classes.

## Local pilots 052–053: all-pinned response consistency

This second task type fixed a real output-shape mismatch: the all-pinned `jev_select_context` fast path made no upstream request but omitted evaluation metadata returned by the normal path. The shared prompt, model (`gpt-5.5`), clean source commit (`448937d`), environment and test commands were held constant; P052 ran candidate first and P053 reversed the order. Both arms added a new focused test, left existing tests unchanged, passed all 41 tests and passed targeted Ruff. Independent full-suite runs were used because Codex's nested sandbox could not bind a loopback socket.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 052 | candidate → baseline | 236,241 | 304,307 | +28.8% | 17 → 19 | 85.463 → 92.660 s (+8.4%) |
| 053 | baseline → candidate | 196,779 | 216,593 | +10.1% | 18 → 17 | 78.363 → 75.712 s (−3.4%) |

Cached input was 212,096/274,304 baseline/candidate in P052 and 173,440/194,304 in P053; output tokens were 3,520/3,787 and 2,997/2,957. USD cost was unavailable. Traces show the Skill candidate still inventoried/scanned tests and repeated broad searches after targeted paths were known; the new working-set rule narrows those behaviors. That revision is not yet measured. P052–053 are quality-valid but are counterevidence to general token savings, not successful efficacy results.


## Local pilots 054–055: narrowed working-set rule

P054–055 repeated the identical P052–053 all-pinned metadata task from clean commit `48ad1e4`, with the same model (`gpt-5.5`), task prompt, environment and gates. The Skill candidate first in P054 and second in P055. Both candidates and baselines added focused tests without editing existing tests; all four full suites passed 41 tests and targeted Ruff passed. Codex traces show candidates did fewer repository commands after the rule discouraged test-tree inventories when target paths were known.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 054 | candidate → baseline | 245,654 | 207,718 | −15.4% | 17 → 12 (−29.4%) | 74.997 → 71.082 s (−5.2%) |
| 055 | baseline → candidate | 309,886 | 297,340 | −4.0% | 21 → 15 (−28.6%) | 85.037 → 78.029 s (−8.2%) |

Cached input was 222,720/175,872 baseline/candidate in P054 and 266,496/266,112 in P055; output tokens were 2,817/2,729 and 3,198/2,784. Subscription billing exposes no per-run USD cost. The positive direction survived order reversal, but savings were modest and are demonstrated only on this task.

## Local pilots 056–057: key-file behavior

P056–057 reused the same key-file expansion task and exact prompt as P050–051, on clean commit `48ad1e4` and the newer Skill revision. The requested behavior includes preserving environment-key precedence, absolute paths, literal `$VARS`, generic errors, additive tests and English/Chinese documentation. P056 ran candidate first; the P057 baseline ran first, but its candidate arm could not complete verification and is excluded.

| Pair | Order | Baseline total tokens | Candidate total tokens | Change | Actions (baseline → candidate) | Time (baseline → candidate) |
|---|---|---:|---:|---:|---:|---:|
| 056 | candidate → baseline | 343,450 | 253,098 | −26.3% | 20 → 13 (−35.0%) | 91.239 → 84.059 s (−7.9%) |

Cached input was 313,600/225,024 baseline/candidate; output tokens were 3,554/3,482. Both P056 arms passed all 42 tests and targeted Ruff. P057 candidate implemented the requested code and added tests, but its runner hung reading Python package files that macOS File Provider marked `dataless`; it never produced a usable test result or completed trace. Its partial data is not efficacy evidence. No per-run USD cost was available. Repeat the key-file task under a hydrated common environment before drawing a conclusion about the newer Skill across task types.


### P057 environment incident

The P057 candidate made the requested key-file code/test/documentation changes, but verification stalled while Python tried to read `pytest/__init__.py`, which File Provider reported as `isDownloaded=0` and marked `dataless`. Direct reads of the repository's `.git/config` also stalled after it became dataless. We stopped the run; no candidate completion, test result, candidate usage total or runtime was produced. Exclude P057 from efficacy calculations. This is a hydration failure in the local workspace environment, not a product test failure. Future runs must first verify that the shared virtualenv and Git metadata are hydrated, or use a pre-existing fully local environment without changing dependency versions.
