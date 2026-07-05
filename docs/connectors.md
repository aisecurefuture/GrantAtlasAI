# Connector Notes

## Grants.gov MVP Connector

GrantAtlas starts with Grants.gov because it is directly aligned with the nonprofit and research grant discovery MVP.

The adapter lives at `apps/api/app/services/grants_gov.py`.

Current behavior:

- Sends a keyword search request to `GRANTS_GOV_SEARCH_URL`.
- Defaults to `https://api.grants.gov/v1/api/search2`.
- Normalizes opportunity fields into the internal schema.
- Imports records into the requesting tenant only.
- Runs transparent rules scoring after import.

Operational notes:

- Keep `GRANTS_GOV_FETCH_LIMIT` conservative at first.
- Store raw payload snapshots in a future ingestion table before broad production use.
- Track ingestion job status, error logs, and external API response metadata.
- Backfill attachments and package details in a later iteration.

## SAM.gov V2 Connector

The v2 scaffold includes a SAM.gov Contract Opportunities connector at `apps/api/app/services/sam_gov.py`.

Current behavior:

- Uses `SAM_GOV_API_KEY`; no API key is committed.
- Calls `SAM_GOV_OPPORTUNITIES_URL`, defaulting to `https://api.sam.gov/opportunities/v2/search`.
- Sends required posted date range parameters.
- Supports keyword title search, NAICS (`ncode`), and classification/PSC (`ccode`) filters.
- Normalizes SAM.gov opportunity payloads into `contract_opportunities`.
- Runs v2 contract scoring after import.

Implemented v2 capture primitives:

- NAICS and PSC matching
- Past-performance library
- Teaming partner database
- Set-aside-aware recommendations
- Capture plan, compliance matrix, color team reviews, and tasks

Still future:

- Attachment/package retrieval
- RFP parsing
- CRM integrations
- Automated partner recommendations
- Full color-team workflow permissions

## Future Foundation and Corporate Connectors

Private foundation and corporate philanthropy sources often have varied terms of service and inconsistent structured APIs. Treat these as connector-specific integrations with review of licensing, scraping permissions, and attribution requirements before implementation.
