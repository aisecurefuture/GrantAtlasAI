from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import Opportunity, OpportunityScore, Role, User
from app.models import OrganizationProfile
from app.schemas import OpportunityDetailOut, OpportunityIn, OpportunityListItemOut, OpportunityOut, ScoreOut
from app.services.ai import ai_enabled, generate_fit_narrative
from app.services.grants_gov import search_grants_gov
from app.services.ingestion import store_opportunity_score, upsert_grants_gov_items

router = APIRouter()


@router.get("", response_model=list[OpportunityListItemOut])
def list_opportunities(
    q: str | None = None,
    status: str | None = None,
    source: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[OpportunityListItemOut]:
    query = db.query(Opportunity).filter(Opportunity.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Opportunity.title.ilike(like), Opportunity.description.ilike(like), Opportunity.agency.ilike(like)))
    if status:
        query = query.filter(Opportunity.status == status)
    if source:
        query = query.filter(Opportunity.source == source)
    opportunities = query.order_by(Opportunity.close_date.asc().nullslast(), Opportunity.created_at.desc()).limit(200).all()
    if not opportunities:
        return []
    score_rows = (
        db.query(OpportunityScore)
        .filter(
            OpportunityScore.tenant_id == user.tenant_id,
            OpportunityScore.opportunity_id.in_([opp.id for opp in opportunities]),
        )
        .all()
    )
    scores = {row.opportunity_id: row for row in score_rows}
    items: list[OpportunityListItemOut] = []
    for opp in opportunities:
        score = scores.get(opp.id)
        item = OpportunityListItemOut.model_validate(opp)
        if score:
            item.fit_score = score.total_score
            item.recommended_action = score.recommended_action.value
        items.append(item)
    return items


@router.post("", response_model=OpportunityOut)
def create_opportunity(
    payload: OpportunityIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> Opportunity:
    opportunity = Opportunity(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(opportunity)
    db.flush()
    store_opportunity_score(db, user.tenant_id, opportunity)
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


@router.post("/{opportunity_id}/ai-narrative", response_model=ScoreOut)
def generate_opportunity_narrative(
    opportunity_id: str,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> OpportunityScore:
    if not ai_enabled():
        raise HTTPException(status_code=503, detail="AI analysis is not configured on this environment")
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id, Opportunity.tenant_id == user.tenant_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    score = db.query(OpportunityScore).filter(OpportunityScore.opportunity_id == opportunity.id, OpportunityScore.tenant_id == user.tenant_id).first()
    if not score:
        raise HTTPException(status_code=400, detail="Score the opportunity first by saving an organization profile")
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    narrative = generate_fit_narrative(
        profile={
            "mission": profile.mission if profile else "",
            "focus_areas": profile.focus_areas if profile else [],
            "past_performance": profile.past_performance if profile else "",
        },
        subject={
            "title": opportunity.title,
            "agency": opportunity.agency,
            "description": opportunity.description[:2000],
            "eligibility": opportunity.eligibility[:1000],
            "award_ceiling": opportunity.award_ceiling,
            "close_date": opportunity.close_date,
        },
        score={
            "total_score": score.total_score,
            "recommended_action": score.recommended_action.value,
            "reasons": score.reasons,
        },
        kind="grant",
    )
    if not narrative:
        raise HTTPException(status_code=502, detail="AI analysis is temporarily unavailable")
    score.ai_narrative = narrative
    db.commit()
    db.refresh(score)
    return score


@router.post("/ingest/grants-gov", response_model=list[OpportunityOut])
async def ingest_grants_gov(
    query: str = Query(default=""),
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> list[Opportunity]:
    items = await search_grants_gov(query)
    upsert_grants_gov_items(db, user.tenant_id, items)
    db.commit()
    numbers = [item["opportunity_number"] for item in items if item.get("opportunity_number")]
    return (
        db.query(Opportunity)
        .filter(Opportunity.tenant_id == user.tenant_id, Opportunity.source == "Grants.gov", Opportunity.opportunity_number.in_(numbers))
        .all()
        if numbers
        else []
    )

