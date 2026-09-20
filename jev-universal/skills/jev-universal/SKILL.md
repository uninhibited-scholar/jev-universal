---
name: jev-dev-efficient
description: Use for unfamiliar coding, debugging, or feature work that crosses files or contracts. Skip localized changes with a known source and check. No TypeSafe account or API required.
---

# Jev-inspired efficient development

Use only when an unfamiliar bug or feature crosses files, components, or contracts. If the source and change are clear, do the task directly; this Skill can cost more than it saves.

1. **Set acceptance.** Identify the behavior and check. Resolve choices from evidence; ask only if an unresolved choice changes the implementation.
2. **Build a task-indexed working set.** Start with the named symptom/symbol, its implementation, focused tests, and direct callers/dependencies needed for acceptance. For a known symbol or exact error text, run one `rg -n -C 3` search in likely source/test paths. Once it returns a match, do not repeat it with synonyms, product names, or broad categories; expand only for a specific acceptance item not yet located. For unknown locations, use one bounded search over likely paths. For named documentation deliverables, inspect only those target documents; don't scan sibling docs or `docs/*.md`. Never start with `rg` over `.` or full-file reads. Read a whole file only if it is short (about 80 lines) or acceptance requires its overall structure. Batch independent first-pass reads into one shell call. Read contracts/docs only when the change touches them. Keep uninspected regions available and reread only after relevant files change.
3. **Patch additively.** Make the smallest coherent change. Preserve unrelated behavior, public fields, clients, settings, tests, and security assertions. Keep every existing test's inputs, setup, parameter cases, and assertions unchanged. Never repurpose an old test for new behavior; add a distinct test or parameter case while retaining all old cases. Preserve client sections, examples, and safety notes. Only touch files needed for acceptance. Group related cross-file edits into one patch operation where practical instead of patching each file separately. Review one focused diff and compare the before/after test matrix; unexplained deletions fail acceptance.
4. **Verify once.** Run each requested acceptance/test/lint gate once, batching independent checks into one shell call and using the repository's documented or already-present environment. If setup fails, inspect that failure and make at most one local fallback; do not probe multiple interpreters, retry network installs, rerun passing checks, clean caches, or inspect unrelated repo state. Never claim an unrun check passed. Stop when acceptance holds and report briefly.

This adapts Jev's public idea of narrow judgments and explicit decision rules; the host model still does the work. It promises no fixed accuracy, speed, or token savings. Measure total input+output tokens, tool actions, elapsed time, and task success in matched runs.
