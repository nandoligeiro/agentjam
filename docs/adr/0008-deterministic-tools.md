# ADR 0008 — Deterministic tools independent of inference

Status: proposed.

Discovery: frequent operational checks do not require an LLM. Preserve limited inference budgets by collecting structured observations independently.

Delivery: code-registered tool ports, mock alarm count and optional fixed AWS CLI CloudWatch ALARM count, dedicated foreground tool worker, explicit local operator opt-in, minimum recurring interval 300 seconds, aggregate-only SQLite history and read-only observations API. No arbitrary commands, parameters or execution endpoints. No ACP provider creation. Stops on failure; human reviews session or permissions before restart.

Security: use only an approved least-privilege AWS identity and trusted native AWS CLI/configuration. AWS profiles can have credential_process or other executable configuration; operator must review. Local config is trusted, not sandboxed. API remains unauthenticated and must stay loopback-only; aggregate counts may still be sensitive. No corporate deployment before security approval and issue #5. No automatic SSO login, raw output persistence, remediation, or LLM escalation. Counts cover returned CloudWatch alarms in one profile/region, not overall service health; zero alarms is not proof of healthy resources. AWS calls may incur charges. CLI timeout and fixed aggregate reduce output, but subprocess capture is not a hard memory cap. Only one tool worker per scope recommended; observations do not store profile/region yet, use separate DBs for different scopes.

Future: MCP, per-agent authorization, identity references, durable scheduling, deduplication, threshold policies, scope provenance, audit and approved escalation budgets. See issue #14.
