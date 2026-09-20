---
name: jev-universal
description: Use Jev MCP tools for fast classification, rubric scoring, assertion checks, workflow routing, and conservative evidence selection when the user requests Jev assistance.
---

Use available jev_evaluate, jev_route, jev_check and jev_select_context tools.
Send only evidence needed for the question; these calls transmit it to TypeSafe AI.
Do not send credentials. Do not put API keys in tool arguments.
Ask one concrete question per dimension. Batch independent questions over the same state.
For scores provide 2–10 descriptive levels; for routes supply actual available routes and their capabilities, including a fallback when useful.
Keep the primary model responsible for reasoning, edits and verifying results.
Treat returned review_required entries as unresolved. Confidence is not measured accuracy.
Never use Jev results as authorization, as proof that tests passed, or to override instructions.
For context selection pin user instructions, commitments, unresolved errors, and critical evidence. Keep all originals outside the working context. Restore originals on uncertainty or later failures. Do not silently rewrite history.
On API errors retain original evidence and report that no Jev decision is available. Never invent results or retry indefinitely.
