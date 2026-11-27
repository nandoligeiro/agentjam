# ADR 0003 — Durable local runtime

Status: proposed.

Discovery: execute queued and periodic tasks independently of the browser. Preserve existing synchronous API and task history.

Delivery: separate foreground worker, SQLite queue and interval schedules. Atomic claim and completion, one active background job per database, fixed interval in UTC epoch seconds, coalesced missed occurrences, disable future scheduling. Queued work survives restart; expired running jobs become interrupted, not retried. Successful jobs enter existing task history atomically. Run API and worker with the same database and provider configuration.

Trade-offs: interval scheduling only; no cron/calendar timezone, event triggers, job cancellation, distributed leases, service installation or health heartbeat. Single worker deployment required; lease expiry is not process fencing. Synchronous API bypasses queue concurrency. Never infer that an interrupted provider did not perform external side effects. Do not automatically retry. Disabling a schedule does not cancel existing jobs. No guaranteed execution while workstation sleeps/offline. Worker runs until stopped; approved OS supervisor needed for startup/restart. Mock default; real ACP needs separate opt-in and remains unsandboxed. No production use.

Validation: tests cover persistence, concurrent claim, expiry, late completion, schedule coalescing, and API. CI and real environment smoke test required.
