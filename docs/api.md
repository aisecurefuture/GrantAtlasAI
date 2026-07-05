# API Notes

The API is served by FastAPI. OpenAPI docs are available at `/docs` in non-restricted environments.

## Authentication

`POST /auth/login`

```json
{
  "email": "owner@gratitech.org",
  "password": "<BOOTSTRAP_ADMIN_PASSWORD>"
}
```

Returns a bearer token. Send it as:

```http
Authorization: Bearer <token>
```

## Opportunity Creation

`POST /opportunities`

```json
{
  "title": "Community Technology Education Capacity Grant",
  "agency": "Example Funder",
  "source": "Manual",
  "close_date": "2026-09-01T00:00:00Z",
  "award_ceiling": 250000,
  "eligibility": "Nonprofit organizations may apply.",
  "description": "Funds AI literacy and cybersecurity education."
}
```

The API scores the opportunity after creation when an organization profile exists.

## Grants.gov Ingestion

`POST /opportunities/ingest/grants-gov?query=cybersecurity`

Imports matching posted or forecasted opportunities into the current tenant and runs scoring.

## SAM.gov Contract Ingestion

`POST /contracts/ingest/sam-gov?query=cybersecurity&naics=541519`

Requires:

```env
SAM_GOV_API_KEY=<your key>
```

The connector calls the SAM.gov Contract Opportunities v2 search endpoint, stores normalized contract records in the current tenant, and runs v2 capture scoring.

## Contract Capture

`POST /contracts`

Creates a manual contract opportunity.

`GET /contracts/{id}`

Returns the contract, contract fit score, and capture plan.

`POST /contracts/{id}/capture-plan`

Creates or updates bid decision, win themes, customer pain points, partner strategy, compliance matrix, color team reviews, and capture tasks.

## Partner and Past Performance Assets

- `GET /partners`
- `POST /partners`
- `PUT /partners/{id}`
- `GET /past-performance`
- `POST /past-performance`
- `PUT /past-performance/{id}`

## Billing

`POST /billing/checkout?plan=Professional`

Creates a Stripe Checkout subscription session with `trial_period_days` set from `STRIPE_TRIAL_DAYS`.

`POST /billing/portal`

Creates a Stripe Customer Portal session for tenants with a Stripe customer ID.
