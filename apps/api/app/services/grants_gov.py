from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def normalize_grants_gov_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": item.get("title") or item.get("opportunityTitle") or "Untitled Grant",
        "agency": item.get("agencyName") or item.get("agency") or "",
        "source": "Grants.gov",
        "source_url": item.get("url") or item.get("link"),
        "opportunity_number": item.get("opportunityNumber") or item.get("oppNum"),
        "assistance_listing": item.get("cfdaList") or item.get("assistanceListings"),
        "posted_date": _parse_date(item.get("postedDate")),
        "close_date": _parse_date(item.get("closeDate")),
        "award_floor": item.get("awardFloor"),
        "award_ceiling": item.get("awardCeiling"),
        "expected_awards": item.get("expectedNumberOfAwards"),
        "eligibility": item.get("eligibility") or item.get("applicantEligibilityDesc") or "",
        "cost_share_required": bool(item.get("costSharingOrMatchingRequirement")),
        "required_partners": "",
        "description": item.get("description") or item.get("synopsis") or "",
        "categories": [item.get("fundingInstrumentType")] if item.get("fundingInstrumentType") else [],
        "keywords": [],
        "attachments": [],
        "contact_info": {"raw": item.get("contactInformation")} if item.get("contactInformation") else {},
    }


async def search_grants_gov(query: str = "", rows: int | None = None) -> list[dict[str, Any]]:
    rows = rows or settings.grants_gov_fetch_limit
    payload = {
        "keyword": query,
        "oppStatuses": "forecasted|posted",
        "rows": rows,
        "startRecordNum": 0,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(settings.grants_gov_search_url, json=payload)
        response.raise_for_status()
        data = response.json()
    items = data.get("oppHits") or data.get("data", {}).get("oppHits") or data.get("opportunities") or []
    return [normalize_grants_gov_item(item) for item in items]

