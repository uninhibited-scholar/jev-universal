---
name: jev-dev-efficient
description: Use for unfamiliar coding, debugging, or feature work that crosses files or contracts. Skip localized changes with a known source and check. No TypeSafe account or API required.
---

# Jev-inspired efficient development

Use only when an unfamiliar bug or feature crosses files, components, or contracts. If the source and change are clear, do the task directly; this Skill can cost more than it saves.

1. **Set acceptance.** Identify the behavior and check. Resolve choices from evidence; ask only if an unresolved choice changes the implementation.
2. **Build a task-indexed working set.** Start with the named symptom/symbol, its implementation, focused tests, and direct callers/dependencies needed for acceptance. If locations are unknown, run one bounded `rg -n` search over likely source/test directories; never begin with a full-repository listing or broad recursive search. Read contracts/docs only when the change touches their behavior or public interface. Keep uninspected regions available and expand only for a named gap; reuse returned context and reread only after relevant files change.
3. **Patch additively.** Make the smallest coherent change. Preserve unrelated behavior, public fields, clients, settings, tests, and security assertions. Keep every existing test case and its assertions; add a separate test or parameter case without removing/renaming prior cases or weakening shared assertions. Preserve client sections, examples, and safety notes. Only touch files needed for acceptance. Review one focused diff; unexplained deletions fail acceptance.
4. **Verify once.** Run each requested acceptance/test/lint gate once, using the repository's documented or already-present environment. If setup fails, inspect that failure and make at most one local fallback; do not probe multiple interpreters, retry network installs, rerun passing checks, clean caches, or inspect unrelated repo state. Never claim an unrun check passed. Stop when acceptance holds and report briefly.

This adapts Jev's public idea of narrow judgments and explicit decision rules; the host model still does the work. It promises no fixed accuracy, speed, or token savings. Measure total input+output tokens, tool actions, elapsed time, and task success in matched runs.
