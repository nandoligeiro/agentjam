# ADR 0004 — Explicit skills and agent memory

Status: proposed.

Discovery: make reusable operator-selected knowledge available to both synchronous and background tasks without coupling core to any skills repository.

Delivery: filesystem skills adapter, per-agent skill selection, SQLite memory with explicit CRUD, shared contextual provider decorator, and Context UI. Reads SKILL.md as UTF-8 text, not executable code; no scripts/resources automatically run. Up to eight skills, ten most recent notes included per execution, 48,000-character serialized context budget; fail closed if selected skills disappear or budget exceeded. Up to 100 stored notes per agent.

Trade-offs: no semantic retrieval, automatic learning, session continuation, version pinning or reference-file resolution yet. Skills source order and paths determine IDs; keep source ordering consistent between API and worker. Read-only adapter does not enforce OS isolation, and symlink checks are not a security boundary against concurrent hostile filesystem changes. Trust configured roots only. Context may be sent to provider and reflected in stored results. Deleting a note does not delete previous task results, backups or provider records. Memory isolation is logical, not authentication. Never put secrets in skills or memory. No corporate-specific names or data upstream.

Validation: integration tests cover isolation, manual and worker context, missing skills and symlink rejection. CI and browser smoke test required.
