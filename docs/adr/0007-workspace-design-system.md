# ADR 0007 — Graphite workspace design system

Status: proposed.

Discovery: replace visually dense MVP styling with a restrained engineering workspace. Design direction is a hypothesis, not evidence of increased engagement.

Delivery: graphite surfaces, semantic status colors, distribution-aware accent tokens, locally available font stack (Inter if installed, otherwise system), SVG icons, searchable agent navigation, hierarchical header, optional agent inspector, responsive layout, accessible names and focus states. Keep feature modules and existing API contracts. No new UI dependencies, network fonts, telemetry or corporate branding.

Trade-offs: dark theme only; light theme, localization, keyboard shortcuts, full WCAG audit, user research and browser screenshot/E2E tests remain future work. Distribution accents with inadequate contrast use a readable teal for text while retaining the configured brand swatch. No new backend capability or security guarantee.

Validation: unit tests check contrast token behavior; existing CI checks TypeScript and backend. Browser visual verification and usability feedback are required before claiming accessibility compliance or engagement gains.
