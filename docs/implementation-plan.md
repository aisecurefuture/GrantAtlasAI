# Implementation Plan

## Phase 1: Foundation

- Create monorepo structure.
- Add FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, MinIO, Caddy, and Next.js.
- Implement tenant, user, profile, opportunity, score, proposal, library, audit, and billing tables.
- Seed Gratitech starter tenant and proposal content.

## Phase 2: MVP Workflow

- Add login and tenant-aware route guards.
- Add organization profile editing.
- Add manual opportunity CRUD.
- Add Grants.gov ingestion job tracking.
- Run scoring on create/import/update.
- Build dashboard filters and opportunity detail views.
- Create proposal workspace from opportunity.
- Add library insertion into narrative sections.

## Phase 3: Monetization and Notifications

- Configure Stripe Checkout and Customer Portal.
- Add webhook verification and subscription reconciliation.
- Enforce usage limits by plan.
- Add Resend transactional email templates.
- Schedule deadline, high-fit, trial-ending, payment-failed, and task notifications.

## Phase 4: Production Hardening

- Add row-level security.
- Add rate limiting.
- Add structured logs and error tracking.
- Add backups and restore automation.
- Add CI checks for tests, linting, migrations, and frontend build.
- Add super-admin impersonation with audit controls.

## Phase 5: V2 Contracting

- Add contract opportunity, contract score, capture plan, past performance, and teaming partner tables.
- Add SAM.gov Contract Opportunities ingestion using API key, posted date range, title, NAICS, and PSC/classification filters.
- Add transparent contract scoring across NAICS, PSC, past performance, set-aside, deadline, competition, and strategic value.
- Add contract dashboard, contract detail, capture matrix, color team review, partner, and past-performance screens.
- Keep contract workflows separate from grant workflows until shared search/reporting is needed.
