# ADR 0001 — ACP v1 stdio connectivity

Status: proposed for review.

Discovery: enable a real coding agent without coupling the domain to a specific vendor. Choose ACP v1 newline-delimited JSON-RPC with one process and session per task. No new runtime dependencies. Prefer a protocol SDK once the wider session lifecycle is needed.

Delivery: initialize, negotiate version, create session, prompt, collect text updates, reject client tool methods and cancel permission requests. Bound runtime and output. Mock remains the default. Configuration is process-level, not user-controlled.

Security: ACP permission cancellation is not a sandbox. The child inherits OS permissions and environment; it may have its own tools. Enable only in an isolated disposable test environment without sensitive credentials or repositories. Real provider execution requires explicit opt-in. No MCP servers or client filesystem/terminal capabilities advertised. API is single-user and unauthenticated; do not expose beyond loopback.

Postmortem / validation: fake ACP process tests cover handshake, streaming, permission cancellation, timeout and opt-in. Real Devin authentication, compatibility, cancellation, streaming to UI, session persistence, process-tree containment, and usage limits remain to be verified. Protocol v2 is not supported.
