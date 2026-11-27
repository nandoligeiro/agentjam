# ADR 0002 — Modular web workspace

Status: proposed.

Discovery: replace Swagger for common agent and task operations.

Delivery: React + TypeScript + Vite, modules for agents and tasks, shared HTTP boundary and app composition. A local development/preview proxy forwards /api to the existing loopback API; no backend CORS expansion. React escapes task results as plain text. No raw HTML or tool invocation in browser.

Trade-offs: independent task history is presented as a timeline, not persistent conversational context. No streaming, authentication, production hosting, concurrent execution controls at backend, or scheduler. UI disables duplicate submissions during a request; reload may lose pending UI state. Provider selection is process-level. Keep mock default. No corporate branding or information in upstream.

Validation: API boundary unit tests and TypeScript production build configured in CI. Manual browser smoke test and real ACP integration remain required. Dependency versions are explicit but a lockfile must be generated and committed before reproducible builds are claimed.
