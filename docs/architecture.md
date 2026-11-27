# Architecture and discovery
Goal: an extensible local-first workspace for persistent agents, with replaceable providers and separately versioned distributions.

Current modules: agents (identity), tasks (manual execution). Adapters: SQLite and mock. Composition root: main.py. No external model calls.

Future boundaries: conversations, workspaces, sessions, automations, memory, skills, governance and observability. Add only when a use case exists. Frontend will be feature modular React/TypeScript. Distribution manifest is illustrative and not loaded yet.

Security: loopback binding is not authentication. Current demo is single-user only, not production-ready. Before real providers: verify ACP support, enforce process isolation, workspace allowlists, approval handling, data retention and audit. Keep employer-specific extensions private and obtain authorization before deployment.
