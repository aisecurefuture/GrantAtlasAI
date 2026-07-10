"""Shared ingestion pipeline used by API routes and scheduled Celery tasks.

Each tenant's organization profile drives the search query (top focus areas),
so nightly runs keep every tenant's pipeline fresh without manual imports.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import (
    ContractAction,
    ContractOpportunity,
    ContractScore,
    Opportunity,
    OpportunityScore,
    OrganizationProfile,
    PastPerformanceProject,
    RecommendedAction,
    TeamingPartner,
    Tenant,
)
from app.services.contract_scoring import score_contract
from app.services.grants_gov import search_grants_gov
from app.services.sam_gov import search_sam_gov
from app.services.scoring import score_opportunity

logger = logging.getLogger(__name__)


def store_opportunity_score(db: Session, tenant_id: str, opportunity: Opportunity) -> OpportunityScore | None:
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant_id).first()
    if not profile:
        return None
    result = score_opportunity(
        profile={
            "mission": profile.mission,
            "focus_areas": profile.focus_areas,
            "programs": profile.programs,
            "target_populations": profile.target_populations,
            "past_performance": profile.past_performance,
        },
        opportunity={
            "title": opportunity.title,
            "description": opportunity.description,
            "categories": opportunity.categories,
            "keywords": opportunity.keywords,
            "eligibility": opportunity.eligibility,
            "close_date": opportunity.close_date,
            "award_ceiling": opportunity.award_ceiling,
            "cost_share_required": opportunity.cost_share_required,
            "required_partners": opportunity.required_partners,
        },
    )
    existing = db.query(OpportunityScore).filter(OpportunityScore.opportunity_id == opportunity.id).first()
    score = existing or OpportunityScore(tenant_id=tenant_id, opportunity_id=opportunity.id)
    for key, value in result.__dict__.items():
        if key == "recommended_action":
            setattr(score, key, RecommendedAction(value))
        else:
            setattr(score, key, value)
    db.add(score)
    return score


def store_contract_score(db: Session, tenant_id: str, contract: ContractOpportunity) -> ContractScore | None:
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant_id).first()
    if not profile:
        return None
    past_projects = db.query(PastPerformanceProject).filter(PastPerformanceProject.tenant_id == tenant_id).all()
    partners = db.query(TeamingPartner).filter(TeamingPartner.tenant_id == tenant_id).all()
    result = score_contract(
        profile={
            "mission": profile.mission,
            "focus_areas": profile.focus_areas,
            "past_performance": profile.past_performance,
        },
        contract={
            "title": contract.title,
            "opportunity_type": contract.opportunity_type,
            "set_aside": contract.set_aside,
            "naics_code": contract.naics_code,
            "classification_code": contract.classification_code,
            "response_deadline": contract.response_deadline,
        },
        past_performance=[
            {
                "naics_codes": project.naics_codes,
                "classification_codes": project.classification_codes,
                "summary": project.summary,
                "outcomes": project.outcomes,
            }
            for project in past_projects
        ],
        partners=[
            {
                "naics_codes": partner.naics_codes,
                "set_aside_statuses": partner.set_aside_statuses,
            }
            for partner in partners
        ],
    )
    existing = db.query(ContractScore).filter(ContractScore.contract_opportunity_id == contract.id).first()
    score = existing or ContractScore(tenant_id=tenant_id, contract_opportunity_id=contract.id)
    for key, value in result.__dict__.items():
        if key == "recommended_action":
            setattr(score, key, ContractAction(value))
        else:
            setattr(score, key, value)
    db.add(score)
    return score


def upsert_grants_gov_items(db: Session, tenant_id: str, items: list[dict[str, Any]]) -> int:
    imported = 0
    for item in items:
        existing = None
        if item.get("opportunity_number"):
            existing = (
                db.query(Opportunity)
                .filter(
                    Opportunity.tenant_id == tenant_id,
                    Opportunity.source == "Grants.gov",
                    Opportunity.opportunity_number == item["opportunity_number"],
                )
                .first()
            )
        opportunity = existing or Opportunity(tenant_id=tenant_id)
        for key, value in item.items():
            setattr(opportunity, key, value)
        db.add(opportunity)
        db.flush()
        store_opportunity_score(db, tenant_id, opportunity)
        imported += 1
    return imported


def upsert_sam_gov_items(db: Session, tenant_id: str, items: list[dict[str, Any]]) -> int:
    imported = 0
    for item in items:
        existing = None
        if item.get("notice_id"):
            existing = (
                db.query(ContractOpportunity)
                .filter(
                    ContractOpportunity.tenant_id == tenant_id,
                    ContractOpportunity.source == "SAM.gov",
                    ContractOpportunity.notice_id == item["notice_id"],
                )
                .first()
            )
        contract = existing or ContractOpportunity(tenant_id=tenant_id)
        for key, value in item.items():
            setattr(contract, key, value)
        db.add(contract)
        db.flush()
        store_contract_score(db, tenant_id, contract)
        imported += 1
    return imported


def _tenant_query_terms(profile: OrganizationProfile | None) -> str:
    if not profile or not profile.focus_areas:
        return ""
    # Grants.gov keyword search works best with a small number of terms.
    return " ".join(str(area) for area in profile.focus_areas[:3])


async def ingest_grants_gov_for_all_tenants() -> dict:
    results: dict[str, int] = {}
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant.id).first()
            query = _tenant_query_terms(profile)
            try:
                items = await search_grants_gov(query)
                results[tenant.slug] = upsert_grants_gov_items(db, tenant.id, items)
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("Grants.gov ingestion failed for tenant %s", tenant.slug)
                results[tenant.slug] = -1
    finally:
        db.close()
    return {"source": "Grants.gov", "results": results}


async def ingest_sam_gov_for_all_tenants() -> dict:
    if not settings.sam_gov_api_key:
        logger.info("Skipping SAM.gov ingestion: no API key configured")
        return {"source": "SAM.gov", "skipped": "no API key"}
    results: dict[str, int] = {}
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant.id).first()
            query = _tenant_query_terms(profile)
            try:
                items = await search_sam_gov(query=query)
                results[tenant.slug] = upsert_sam_gov_items(db, tenant.id, items)
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("SAM.gov ingestion failed for tenant %s", tenant.slug)
                results[tenant.slug] = -1
    finally:
        db.close()
    return {"source": "SAM.gov", "results": results}
