# GrantAtlas

GrantAtlas is a multi-tenant funding intelligence SaaS for nonprofits, universities, research organizations, and future government contractors.

This repository contains the MVP foundation:

- `apps/api`: FastAPI backend with tenant-aware auth, opportunities, scoring, proposals, content library, Stripe, Resend, and admin surfaces.
- `apps/web`: Next.js TypeScript frontend with a SaaS dashboard, opportunity detail views, proposal workspace, organization profile, library, and admin views.
- `infra`: Caddy reverse proxy config for Hetzner/Docker Compose deployment.
- `docs`: architecture, deployment, security, API, connector, billing, and roadmap notes.
- `scripts`: local seed and maintenance helpers.

## Quick Start

1. Copy `.env.example` to `.env` and fill in secrets.
2. Start services:

```bash
docker compose up --build
```

3. Run migrations and seed data:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

4. Open `http://localhost:3000`.

## Production

- Hetzner hardening with root SSH keys: [docs/hetzner-hardening-root-ssh.md](docs/hetzner-hardening-root-ssh.md)
- Production deployment: [docs/production-deployment.md](docs/production-deployment.md)
- General deployment notes: [docs/deployment.md](docs/deployment.md)

Default seeded account:

- Email: `owner@gratitech.org`
- Password: `ChangeMe123!`

Change the seeded password immediately outside local development.

## MVP Scope

The MVP implements a working end-to-end path:

- Tenant-aware email/password authentication
- Organization profile for Gratitech Research & Charitable Endeavor Corp.
- Manual opportunity entry
- Grants.gov ingestion adapter
- Transparent rule-based scoring
- Pipeline dashboard and opportunity detail API
- Proposal workspace and reusable content library
- Stripe Checkout and Customer Portal integration hooks
- Resend transactional email hooks
- Super-admin read views
- Docker Compose deployment for Hetzner

SAM.gov contracting, foundation connectors, AI drafting, SSO, and partner CRM workflows are designed in the roadmap but intentionally deferred.
The v2 contracting scaffold now includes SAM.gov import plumbing, contract scoring, capture plans, teaming partners, and past-performance records; advanced RFP parsing and CRM integrations remain on the roadmap.
