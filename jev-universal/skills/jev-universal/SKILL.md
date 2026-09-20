---
name: jev-dev-efficient
description: For unfamiliar multi-file coding tasks; read this Skill by itself before repository exploration, and skip when source and check are already clear.
---

# Efficient development

1. Define the requested behavior and acceptance check.
2. If the request names a command, flag, symbol, error, or path, search that exact term once in likely source and test paths; inspect the implementation and nearest test directly. If the location is unknown, use one bounded search in source/tests. Avoid repository-wide file listings and broad searches across docs, generated files, or caches. Read only documentation requested or needed for a specific acceptance gap. Read focused regions; expand one dependency hop only to close a gap. Reuse unchanged evidence.
3. Make the smallest additive patch. Preserve existing tests and unrelated behavior; add separate regression cases.
4. Run each requested check once. Stop when acceptance passes; report any check that could not run.

This adapts Jev's evidence-led decisions; the host model still performs the work. No fixed token savings are promised.
