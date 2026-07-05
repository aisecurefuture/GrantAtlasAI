from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import settings


def _parse_sam_date(value: str | None) -> datetime | None:
    if not value or value == "null":
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(value[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def normalize_sam_opportunity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": item.get("title") or "Untitled Contract Opportunity",
        "source": "SAM.gov",
        "notice_id": item.get("noticeId"),
        "solicitation_number": item.get("solicitationNumber"),
        "department": item.get("department") or "",
        "subtier": item.get("subTier") or item.get("subtier") or "",
        "office": item.get("office") or "",
        "posted_date": _parse_sam_date(item.get("postedDate")),
        "response_deadline": _parse_sam_date(item.get("responseDeadLine") or item.get("responseDeadline")),
        "opportunity_type": item.get("type") or "",
        "set_aside": item.get("typeOfSetAsideDescription") or item.get("setAside"),
        "set_aside_code": item.get("typeOfSetAside") or item.get("setAsideCode"),
        "naics_code": item.get("naicsCode"),
        "classification_code": item.get("classificationCode"),
        "place_of_performance": item.get("placeOfPerformance") or {},
        "description_url": item.get("description"),
        "ui_link": item.get("uiLink"),
        "resource_links": item.get("resourceLinks") or [],
        "point_of_contact": item.get("pointOfContact") or [],
        "active": item.get("active", "Yes") == "Yes",
        "raw_payload": item,
    }


async def search_sam_gov(
    query: str = "",
    naics: str | None = None,
    classification_code: str | None = None,
    posted_from: datetime | None = None,
    posted_to: datetime | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not settings.sam_gov_api_key:
        raise RuntimeError("SAM_GOV_API_KEY is required for SAM.gov ingestion")
    posted_to = posted_to or datetime.now(timezone.utc)
    posted_from = posted_from or posted_to - timedelta(days=settings.sam_gov_default_posted_days)
    params: dict[str, Any] = {
        "api_key": settings.sam_gov_api_key,
        "postedFrom": posted_from.strftime("%m/%d/%Y"),
        "postedTo": posted_to.strftime("%m/%d/%Y"),
        "limit": limit or settings.sam_gov_fetch_limit,
        "offset": 0,
    }
    if query:
        params["title"] = query
    if naics:
        params["ncode"] = naics
    if classification_code:
        params["ccode"] = classification_code
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(settings.sam_gov_opportunities_url, params=params)
        response.raise_for_status()
        data = response.json()
    return [normalize_sam_opportunity(item) for item in data.get("opportunitiesData", [])]
