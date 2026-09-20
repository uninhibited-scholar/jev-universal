---
name: jev-dev-efficient
description: For repository-scale coding/debugging only when relevant files or causal paths are unclear, tool output is noisy, or diagnosis has repeated. Do not invoke for a localized request that already states the subsystem, behavior, and acceptance checks. No TypeSafe account/API required; Jev-inspired workflow, not the Jev model.
---

# Jev-inspired efficient development

Use only when repository exploration or repeated diagnosis is substantial. If the request names the affected subsystem, expected behavior, and acceptance checks, inspect that implementation and those tests directly; do not perform a repository inventory. For an obvious small change, follow the request directly; this instruction can cost more than it saves.

1. **Set the finish line.** Identify the requested change and acceptance check. Resolve from evidence any yes/no or choice that would change the implementation; ask only if necessary.
2. **Narrow the search.** If the request names a subsystem or error, start there; do not inventory the whole repository or read its README first. Search that subsystem's symbols and tests, then inspect matching code and direct callers. Expand only if targeted search fails or evidence points elsewhere. Reuse unchanged results. Cap noisy command output and inspect useful matches or failure tails.
3. **Choose and act.** Use the evidence to pick one next step. Every additional search must answer a specific unresolved question; do not re-scan to reconfirm findings already supported by code or tests. Make the smallest coherent patch using existing patterns. Avoid unrelated refactors and parallel agents for dependent work.
4. **Verify and stop.** Run the smallest meaningful tests for the change; broaden only for shared interfaces or a new failure. Never skip required checks or hide failures to save tokens. Once acceptance is established, stop exploring and report the change, checks, and remaining issue briefly.

This borrows Jev's public pattern: narrow judgments, explicit decision rules, then act. The host model still performs the work. The Skill makes no accuracy, speed, or token-saving guarantee; demonstrate savings only with matched measurements of total tokens, tool calls, elapsed time, and task success.
