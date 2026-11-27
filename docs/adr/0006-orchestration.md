# ADR 0006 — Explicit multi-agent delegation

Status: proposed.

Discovery: coordinate independent agents while preserving lineage and bounded execution. Avoid interpreting untrusted model text as commands.

Delivery: operator chooses an existing successful background job and target agent, supplies an explicit prompt, and queues a child job transactionally with lineage. Max depth 3, 5 children per parent, 20 descendants per root. No repeated agent within an ancestor path. Existing worker executes child jobs; target context is independently loaded. Parent result is not automatically forwarded. API and Team UI expose incoming/outgoing delegations.

Trade-offs: no autonomous agent-to-agent calls, shared memory, workflow join, result synthesis, org chart editing, parallel worker pool, shared spend budget or automatic approval. Limits are per tree, not global spending limits. This is a single-user prototype; source ownership check is logical, not authentication. Operator submission is not a durable approval system. Only successful background jobs are eligible; synchronous tasks are not parents. Keep mock default. Production requires security hardening.

Validation: tests for lineage, cycle prevention, depth, atomic fanout and API ownership. CI and browser smoke test required. Future work remains tracked in issue #10.
