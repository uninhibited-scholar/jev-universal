---
name: jev-dev-efficient
description: Use for unfamiliar coding, debugging, or feature work that crosses files or contracts. Skip localized changes with a known source and check. No TypeSafe account or API required.
---

# Jev-inspired efficient development

Use only when an unfamiliar bug or feature crosses files, components, or contracts. If the source and change are clear, do the task directly; this Skill can cost more than it saves.

1. **Set acceptance.** Identify the behavior and check. Resolve choices from evidence; ask only if an unresolved choice changes the implementation.
2. **Search once, narrowly.** Start from named files, symbols, or subsystem. No opening `pwd`, whole-repo file list, or README. Batch one bounded search and reads of matching code, tests, contracts, and only the affected doc sections. Expand only when evidence requires it; do not reread unchanged files.
3. **Patch additively.** Make the smallest coherent change. Preserve unrelated behavior, public fields, clients, settings, tests, and security assertions. For an additive feature, add a new test and doc bullet; do not rewrite or remove existing tests, client sections, examples, or safety notes. Only touch files needed for acceptance. Review one focused diff; unexplained deletions fail acceptance.
4. **Verify once.** Run each requested acceptance/test/lint gate once. Use the existing environment and at most one local fallback after a setup failure. Do not retry network installs, rerun passing checks, clean caches, or inspect unrelated repo state. Never claim an unrun check passed. Stop when acceptance holds and report briefly.

This adapts Jev's public idea of narrow judgments and explicit decision rules; the host model still does the work. It promises no fixed accuracy, speed, or token savings. Measure total input+output tokens, tool actions, elapsed time, and task success in matched runs.
