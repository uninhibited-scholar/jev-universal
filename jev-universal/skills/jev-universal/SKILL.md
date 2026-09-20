---
name: jev-dev-efficient
description: For coding/debugging that must diagnose an unfamiliar failure across components or files, or repeated attempts/noisy output. Do not invoke for a localized change with known source and acceptance checks. No TypeSafe account/API required; Jev-inspired workflow, not the Jev model.
---

# Jev-inspired efficient development

Use when a reported failure must be traced across components, clients, or runtime configuration and its source file or root cause is not yet known, even if the affected subsystems are named. If the request already identifies the source and exact change/checks, inspect those directly; do not perform a repository inventory. For an obvious small change, follow the request directly; this instruction can cost more than it saves.

1. **Set the finish line.** Identify the requested change and acceptance check. Resolve from evidence any yes/no or choice that would change the implementation; ask only if necessary.
2. **Narrow the search.** If the request names a subsystem or error, start there; do not inventory the whole repository or read its README first. Search that subsystem's symbols and tests, then inspect matching code and direct callers. Expand only if targeted search fails or evidence points elsewhere. Reuse unchanged results. Cap noisy command output and inspect useful matches or failure tails.
3. **Choose and act.** Use the evidence to pick one next step. Every additional search must answer a specific unresolved question; do not re-scan to reconfirm findings already supported by code or tests. Make the smallest coherent patch using existing patterns. Preserve existing return fields and validation outside the requested fix; do not drop data or add indirection without evidence. Avoid unrelated refactors and parallel agents for dependent work.
4. **Verify and stop.** Run the smallest meaningful tests for the change; broaden only for shared interfaces or a new failure. Never skip required checks or hide failures to save tokens. Once acceptance is established, stop exploring and report the change, checks, and remaining issue briefly.

This borrows Jev's public pattern: narrow judgments, explicit decision rules, then act. The host model still performs the work. The Skill makes no accuracy, speed, or token-saving guarantee; demonstrate savings only with matched measurements of total tokens, tool calls, elapsed time, and task success.
