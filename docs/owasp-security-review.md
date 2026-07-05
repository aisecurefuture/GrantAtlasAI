# OWASP Security Review

This review maps the current GrantAtlas implementation to the OWASP Top 10 for web applications and the OWASP guidance for LLM and agentic AI systems. It is a point-in-time engineering checklist, not a penetration test or legal certification.

## Web Application Top 10

- Broken access control: tenant-owned API routes use `current_user.tenant_id`; admin routes require super-admin; billing mutation routes require owner/admin roles.
- Cryptographic failures: credentials are hashed with Argon2 through Passlib; production startup rejects known development secret placeholders; TLS is terminated by Caddy with Let's Encrypt.
- Injection: API persistence uses SQLAlchemy query construction; no raw SQL query building is used in request handlers.
- Insecure design: role gates, tenant isolation rules, and production deployment notes are documented in `docs/security.md`.
- Security misconfiguration: API/web/MinIO compose ports bind to `127.0.0.1`; Caddy is the public HTTP/HTTPS entry point; CORS and trusted hosts are explicit.
- Vulnerable and outdated components: use `npm audit --audit-level=moderate` for the web app and `pip-audit -r` for API dependencies before deployment.
- Identification and authentication failures: bearer tokens are signed and expire; login failures are throttled per process; seeded credentials must come from environment variables.
- Software and data integrity failures: GitHub should remain the deployment source of truth; production updates should use `git pull` plus Docker rebuilds from committed sources.
- Security logging and monitoring failures: audit models exist, but production still needs structured logs, error tracking, and alerting.
- Server-side request forgery: current outbound integrations target configured Grants.gov and SAM.gov endpoints. Future user-supplied URLs must use an allowlist and block private network ranges.

## LLM And Agentic AI Risks

GrantAtlas does not currently execute LLM calls, autonomous agent tools, browser actions, shell commands, or user-directed workflows in production code. The active LLM/agentic risk is therefore design-time preparation for future AI drafting and RFP parsing.

- Prompt injection: treat grant, contract, RFP, and uploaded text as untrusted content. Never let imported text override system instructions or developer policies.
- Insecure output handling: require validation, escaping, and human review before AI-generated text becomes a proposal, email, or database mutation.
- Training data poisoning: do not use tenant data for model training unless an explicit tenant-level opt-in and data-retention policy exist.
- Model denial of service: enforce file size, token, timeout, and rate limits before adding AI parsing or drafting endpoints.
- Supply chain vulnerabilities: pin AI SDKs and parsing libraries, then include them in dependency audit workflows.
- Sensitive information disclosure: redact secrets, API keys, and tenant-confidential data from prompts, traces, logs, and analytics.
- Insecure plugin or tool design: future agent tools must use explicit allowlists, least privilege credentials, tenant scoping, and human approval for external side effects.
- Excessive agency: do not allow an AI feature to submit applications, send emails, purchase services, or change billing without a clear user confirmation step.
- Overreliance: label AI-generated recommendations as decision support and preserve source citations for grant/contract evidence.
- Model theft: keep model/provider credentials server-side only and never expose them through `NEXT_PUBLIC_*` variables.

## Release Gate

Before pushing a production release, run:

```bash
cd apps/web && npm audit --audit-level=moderate
cd ../api && python -m pip_audit -r /tmp/grantatlas-api-requirements.txt
cd ../api && python -m bandit -r app -q
cd ../api && pytest
cd ../web && npm run build
docker compose --env-file .env.production.example --profile prod config
```
