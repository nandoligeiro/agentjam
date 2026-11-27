# ADR 0005 — Declarative distributions

Status: proposed.

Discovery: allow downstream branding, default provider and local skills sources without modifying the upstream application.

Delivery: strict versioned YAML manifest, local file loading via AGENTJAM_DISTRIBUTION, shared API/worker configuration, safe public branding metadata endpoint, frontend branding. Relative skill paths resolve relative to the manifest; explicit environment variables override manifest defaults, including an empty skills path. Missing manifest variable selects the built-in Community edition. Unknown fields and unsupported versions fail startup.

Security: trusted operator-owned manifest only. It is configuration, not a security policy. It cannot grant ACP permissions or configure executable commands. The existing explicit ACP opt-ins remain mandatory. API exposes branding only, not local paths. Do not store secrets in manifest. Downstream files remain private.

Trade-offs: branding text/color only; no plugins, logo assets, feature flags, policy enforcement, packaged release or agent templates yet. Existing environment settings stay compatible. PyYAML added for safe loading. Frontend accent may need manual contrast review.

Validation: tests for default/override behavior, relative sources, invalid manifests and ACP opt-in. CI and browser smoke test required. See GitHub backlog issues 5–10.
