from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import Opportunity, OpportunityScore, OrganizationProfile, RecommendedAction, Role, User
from app.schemas import OpportunityDetailOut, OpportunityIn, OpportunityOut
from app.services.grants_gov import search_grants_gov
from app.services.scoring import score_opportunity

router = APIRouter()


def _score_and_store(db: Session, tenant_id: str, opportunity: Opportunity) -> OpportunityScore | None:
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


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(
    q: str | None = None,
    status: str | None = None,
    source: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[Opportunity]:
    query = db.query(Opportunity).filter(Opportunity.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Opportunity.title.ilike(like), Opportunity.description.ilike(like), Opportunity.agency.ilike(like)))
    if status:
        query = query.filter(Opportunity.status == status)
    if source:
        query = query.filter(Opportunity.source == source)
    return query.order_by(Opportunity.close_date.asc().nullslast(), Opportunity.created_at.desc()).limit(200).all()


@router.post("", response_model=OpportunityOut)
def create_opportunity(
    payload: OpportunityIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> Opportunity:
    opportunity = Opportunity(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(opportunity)
    db.flush()
    _score_and_store(db, user.tenant_id, opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.get("/{opportunity_id}", response_model=OpportunityDetailOut)
def get_opportunity(opportunity_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> OpportunityDetailOut:
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id, Opportunity.tenant_id == user.tenant_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    score = db.query(OpportunityScore).filter(OpportunityScore.opportunity_id == opportunity.id, OpportunityScore.tenant_id == user.tenant_id).first()
    return OpportunityDetailOut(opportunity=opportunity, score=score)


@router.post("/ingest/grants-gov", response_model=list[OpportunityOut])
async def ingest_grants_gov(
    query: str = Query(default=""),
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> list[Opportunity]:
    imported: list[Opportunity] = []
    for item in await search_grants_gov(query):
        existing = None
        if item.get("opportunity_number"):
            existing = (
                db.query(Opportunity)
                .filter(
                    Opportunity.tenant_id == user.tenant_id,
                    Opportunity.source == "Grants.gov",
                    Opportunity.opportunity_number == item["opportunity_number"],
                )
                .first()
            )
        opportunity = existing or Opportunity(tenant_id=user.tenant_id)
        for key, value in item.items():
            setattr(opportunity, key, value)
        db.add(opportunity)
        db.flush()
        _score_and_store(db, user.tenant_id, opportunity)
        imported.append(opportunity)
    db.commit()
    return imported

