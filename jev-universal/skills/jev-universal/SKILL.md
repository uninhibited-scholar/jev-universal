---
name: jev-dev-efficient
description: For repository-scale coding/debugging only when relevant files are unclear, tool output is noisy, or diagnosis has repeated. Reduce wasted exploration and retries while preserving correctness. Skip obvious localized edits. No TypeSafe account/API required; Jev-inspired workflow, not the Jev model.
---

# Jev-inspired efficient development

Use only when repository exploration or repeated diagnosis is substantial. For an obvious small change, follow the request directly; this instruction can cost more than it saves.

1. **Set the finish line.** Identify the requested change and acceptance check. Resolve from evidence any yes/no or choice that would change the implementation; ask only if necessary.
2. **Narrow the search.** Search symbols and error text first. Read matching code, direct callers, and relevant tests; expand only when evidence points elsewhere. Reuse unchanged results. Cap noisy command output and inspect only useful matches or failure tails.
3. **Choose and act.** Use the evidence to pick one next step. Make the smallest coherent patch using existing patterns. Avoid redundant searches, unrelated refactors, and parallel agents for dependent work.
4. **Verify and stop.** Run the smallest meaningful tests for the change; broaden only for shared interfaces or a new failure. Never skip required checks or hide failures to save tokens. Once acceptance is established, stop exploring and report the change, checks, and remaining issue briefly.

This borrows Jev's public pattern: narrow judgments, explicit decision rules, then act. The host model still performs the work. The Skill makes no accuracy, speed, or token-saving guarantee; demonstrate savings only with matched measurements of total tokens, tool calls, elapsed time, and task success.
