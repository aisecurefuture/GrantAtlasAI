from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import (
    CapturePlan,
    CaptureStatus,
    ContractOpportunity,
    ContractScore,
    Role,
    User,
)
from app.models import OrganizationProfile
from app.schemas import (
    CapturePlanIn,
    CapturePlanOut,
    ContractDetailOut,
    ContractListItemOut,
    ContractOpportunityIn,
    ContractOpportunityOut,
    ContractScoreOut,
)
from app.services.ai import ai_enabled, generate_fit_narrative
from app.services.ingestion import store_contract_score, upsert_sam_gov_items
from app.services.sam_gov import search_sam_gov

router = APIRouter()


@router.get("", response_model=list[ContractListItemOut])
def list_contracts(
    q: str | None = None,
    status: str | None = None,
    naics: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[ContractListItemOut]:
    query = db.query(ContractOpportunity).filter(ContractOpportunity.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(ContractOpportunity.title.ilike(like), ContractOpportunity.department.ilike(like), ContractOpportunity.subtier.ilike(like)))
    if status:
        query = query.filter(ContractOpportunity.status == CaptureStatus(status))
    if naics:
        query = query.filter(ContractOpportunity.naics_code == naics)
    contracts = query.order_by(ContractOpportunity.response_deadline.asc().nullslast(), ContractOpportunity.created_at.desc()).limit(200).all()
    if not contracts:
        return []
    score_rows = (
        db.query(ContractScore)
        .filter(
            ContractScore.tenant_id == user.tenant_id,
            ContractScore.contract_opportunity_id.in_([c.id for c in contracts]),
        )
        .all()
    )
    scores = {row.contract_opportunity_id: row for row in score_rows}
    items: list[ContractListItemOut] = []
    for contract in contracts:
        score = scores.get(contract.id)
        item = ContractListItemOut.model_validate(contract)
        if score:
            item.fit_score = score.total_score
            item.recommended_action = score.recommended_action.value
        items.append(item)
    return items


@router.post("", response_model=ContractOpportunityOut)
def create_contract(
    payload: ContractOpportunityIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ContractOpportunity:
    contract = ContractOpportunity(tenant_id=user.tenant_id, raw_payload={}, **payload.model_dump())
    db.add(contract)
    db.flush()
    store_contract_score(db, user.tenant_id, contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/{contract_id}", response_model=ContractDetailOut)
def get_contract(contract_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ContractDetailOut:
    contract = db.query(ContractOpportunity).filter(ContractOpportunity.id == contract_id, ContractOpportunity.tenant_id == user.tenant_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract opportunity not found")
    score = db.query(ContractScore).filter(ContractScore.contract_opportunity_id == contract.id, ContractScore.tenant_id == user.tenant_id).first()
    capture_plan = db.query(CapturePlan).filter(CapturePlan.contract_opportunity_id == contract.id, CapturePlan.tenant_id == user.tenant_id).first()
    return ContractDetailOut(contract=contract, score=score, capture_plan=capture_plan)


@router.post("/ingest/sam-gov", response_model=list[ContractOpportunityOut])
async def ingest_sam_gov(
    query: str = Query(default=""),
    naics: str | None = None,
    classification_code: str | None = None,
    posted_from: datetime | None = None,
    posted_to: datetime | None = None,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> list[ContractOpportunity]:
    try:
        items = await search_sam_gov(query=query, naics=naics, classification_code=classification_code, posted_from=posted_from, posted_to=posted_to)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    upsert_sam_gov_items(db, user.tenant_id, items)
    db.commit()
    notice_ids = [item["notice_id"] for item in items if item.get("notice_id")]
    return (
        db.query(ContractOpportunity)
        .filter(ContractOpportunity.tenant_id == user.tenant_id, ContractOpportunity.source == "SAM.gov", ContractOpportunity.notice_id.in_(notice_ids))
        .all()
        if notice_ids
        else []
    )


@router.post("/{contract_id}/ai-narrative", response_model=ContractScoreOut)
def generate_contract_narrative(
    contract_id: str,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ContractScore:
    if not ai_enabled():
        raise HTTPException(status_code=503, detail="AI analysis is not configured on this environment")
    contract = db.query(ContractOpportunity).filter(ContractOpportunity.id == contract_id, ContractOpportunity.tenant_id == user.tenant_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract opportunity not found")
    score = db.query(ContractScore).filter(ContractScore.contract_opportunity_id == contract.id, ContractScore.tenant_id == user.tenant_id).first()
    if not score:
        raise HTTPException(status_code=400, detail="Score the contract first by saving an organization profile")
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    narrative = generate_fit_narrative(
        profile={
            "mission": profile.mission if profile else "",
            "focus_areas": profile.focus_areas if profile else [],
            "past_performance": profile.past_performance if profile else "",
        },
        subject={
            "title": contract.title,
            "department": contract.department,
            "opportunity_type": contract.opportunity_type,
            "naics_code": contract.naics_code,
            "classification_code": contract.classification_code,
            "set_aside": contract.set_aside,
            "response_deadline": contract.response_deadline,
        },
        score={
            "total_score": score.total_score,
            "recommended_action": score.recommended_action.value,
            "reasons": score.reasons,
        },
        kind="federal contract",
    )
    if not narrative:
        raise HTTPException(status_code=502, detail="AI analysis is temporarily unavailable")
    score.ai_narrative = narrative
    db.commit()
    db.refresh(score)
    return score


@router.post("/{contract_id}/capture-plan", response_model=CapturePlanOut)
def upsert_capture_plan(
    contract_id: str,
    payload: CapturePlanIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> CapturePlan:
    contract = db.query(ContractOpportunity).filter(ContractOpportunity.id == contract_id, ContractOpportunity.tenant_id == user.tenant_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract opportunity not found")
    if payload.contract_opportunity_id != contract_id:
        raise HTTPException(status_code=400, detail="Capture plan contract ID does not match path")
    capture_plan = db.query(CapturePlan).filter(CapturePlan.contract_opportunity_id == contract_id, CapturePlan.tenant_id == user.tenant_id).first()
    if not capture_plan:
        capture_plan = CapturePlan(tenant_id=user.tenant_id)
    data = payload.model_dump()
    data["status"] = CaptureStatus(data["status"])
    for key, value in data.items():
        setattr(capture_plan, key, value)
    db.add(capture_plan)
    contract.status = capture_plan.status
    db.commit()
    db.refresh(capture_plan)
    return capture_plan

