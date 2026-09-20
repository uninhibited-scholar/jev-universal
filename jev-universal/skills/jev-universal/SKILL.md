---
name: jev-dev-efficient
description: For unfamiliar coding tasks spanning files or contracts; skip when the source and check are already clear.
---

# Efficient development

1. Define the behavior and acceptance check from the request.
2. Start from named symbols/files. Inspect the implementation and nearest relevant test. Search once in likely paths only when a location is unknown. Read focused regions; expand one dependency hop only to resolve an acceptance gap. Reuse unchanged file and command evidence; if more is needed, retrieve only the relevant lines or diff.
3. Make the smallest additive patch. Preserve existing tests and unrelated behavior; add a separate regression case.
4. Run each requested check once. Stop when acceptance passes; report any check that could not run.

This adapts Jev's narrow evidence-led decisions; the host model still performs the work. No fixed token savings are promised.
