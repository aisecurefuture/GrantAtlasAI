# Security Notes

## Implemented Baseline

- Password hashing uses Passlib with Argon2 preferred and bcrypt fallback.
- Access tokens include user, tenant, role, and super-admin status.
- Tenant-owned routes filter by `current_user.tenant_id`.
- Role checks gate profile mutation, opportunity creation, ingestion, library writes, and proposals.
- Super-admin routes require `is_super_admin`.
- Subscription checkout and customer portal routes require owner/admin roles.
- Login attempts are throttled after repeated failures.
- Secrets are environment variables only, and production startup rejects known development placeholders.
- CORS allows explicit configured origins, methods, and request headers only.
- Trusted host validation rejects unexpected `Host` headers.
- Docker Compose binds API, web, and MinIO console ports to `127.0.0.1`; Caddy is the public entry point.
- Caddy adds security headers in production.
- The API adds defensive response headers for direct access.
- Audit log model is present for sensitive actions.

## Required Before Production Launch

- Add Stripe webhook signature verification route and subscription state reconciliation.
- Add invitation flow with expiring signed tokens.
- Add distributed rate limiting at Caddy or Redis before horizontal scaling. The current API login throttle is per process.
- Move browser auth to secure HTTP-only cookies if session UX requires cookie auth.
- Add CSRF protection for cookie-authenticated writes.
- Add file upload validation, malware scanning hooks, and object storage policies.
- Add row-level security policies in PostgreSQL as a second tenant-isolation layer.
- Add structured JSON logging and error tracking.
- Add database backup encryption and restore drills.
- Add support impersonation workflow with explicit audit events and time limits.

## Tenant Isolation Rule

No query against tenant-owned tables should omit a tenant predicate unless the route is explicitly super-admin only. This should be enforced with tests as the API grows.
