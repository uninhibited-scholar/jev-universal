---
name: jev-dev-efficient
description: For coding/debugging or feature work that crosses components or files where the relevant contracts or root cause are unfamiliar, or repeated attempts/noisy output. Skip localized known-source changes. No TypeSafe account/API required; Jev-inspired workflow, not the Jev model.
---

# Jev-inspired efficient development

Use when requested behavior or a failure must be traced across components, clients, or runtime configuration and the relevant call path, interface contract, or root cause is not yet clear. This includes multi-file feature work with unfamiliar existing contracts, not only debugging. If the request identifies the source and exact change/checks, inspect those directly; do not perform a repository inventory. For an obvious small change, follow the request directly; this instruction can cost more than it saves.

1. **Set the finish line.** Identify the requested change and acceptance check. Resolve from evidence any yes/no or choice that would change the implementation; ask only if necessary.
2. **Narrow the search.** If the request names a subsystem or error, start there; do not inventory the whole repository or read its README first. Search the relevant symbols, tests, schemas, and direct callers, then inspect matching code. For a feature, trace the existing path and neighboring client/API contracts before extending them. Expand only if targeted search fails or evidence points elsewhere. Reuse unchanged results. Cap noisy command output and inspect useful matches or failure tails.
3. **Choose and act.** Use the evidence to pick one next step. Every additional search must answer a specific unresolved question; do not re-scan to reconfirm findings already supported by code or tests. Make the smallest coherent patch using existing patterns. Preserve existing return fields and validation outside the requested fix; do not drop data or add indirection without evidence. Avoid unrelated refactors and parallel agents for dependent work.
4. **Preserve adjacent guidance.** When editing a setup guide or shared configuration page, keep all existing clients, settings, and safety instructions that remain relevant. Re-read the edited section and confirm the new instructions did not replace or weaken neighboring guidance.
5. **Verify and stop.** Run the smallest meaningful tests for the change; broaden only for shared interfaces or a new failure. Never skip required checks or hide failures to save tokens. Once acceptance is established, stop exploring and report the change, checks, and remaining issue briefly.

This borrows Jev's public pattern: narrow judgments, explicit decision rules, then act. The host model still performs the work. The Skill makes no accuracy, speed, or token-saving guarantee; demonstrate savings only with matched measurements of total tokens, tool calls, elapsed time, and task success.
