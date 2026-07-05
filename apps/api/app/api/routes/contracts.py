from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import (
    CapturePlan,
    CaptureStatus,
    ContractAction,
    ContractOpportunity,
    ContractScore,
    OrganizationProfile,
    PastPerformanceProject,
    Role,
    TeamingPartner,
    User,
)
from app.schemas import CapturePlanIn, CapturePlanOut, ContractDetailOut, ContractOpportunityIn, ContractOpportunityOut
from app.services.contract_scoring import score_contract
from app.services.sam_gov import search_sam_gov

router = APIRouter()


def _score_and_store_contract(db: Session, tenant_id: str, contract: ContractOpportunity) -> ContractScore | None:
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


@router.get("", response_model=list[ContractOpportunityOut])
def list_contracts(
    q: str | None = None,
    status: str | None = None,
    naics: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[ContractOpportunity]:
    query = db.query(ContractOpportunity).filter(ContractOpportunity.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(ContractOpportunity.title.ilike(like), ContractOpportunity.department.ilike(like), ContractOpportunity.subtier.ilike(like)))
    if status:
        query = query.filter(ContractOpportunity.status == CaptureStatus(status))
    if naics:
        query = query.filter(ContractOpportunity.naics_code == naics)
    return query.order_by(ContractOpportunity.response_deadline.asc().nullslast(), ContractOpportunity.created_at.desc()).limit(200).all()


@router.post("", response_model=ContractOpportunityOut)
def create_contract(
    payload: ContractOpportunityIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ContractOpportunity:
    contract = ContractOpportunity(tenant_id=user.tenant_id, raw_payload={}, **payload.model_dump())
    db.add(contract)
    db.flush()
    _score_and_store_contract(db, user.tenant_id, contract)
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
    imported: list[ContractOpportunity] = []
    try:
        items = await search_sam_gov(query=query, naics=naics, classification_code=classification_code, posted_from=posted_from, posted_to=posted_to)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    for item in items:
        existing = None
        if item.get("notice_id"):
            existing = (
                db.query(ContractOpportunity)
                .filter(
                    ContractOpportunity.tenant_id == user.tenant_id,
                    ContractOpportunity.source == "SAM.gov",
                    ContractOpportunity.notice_id == item["notice_id"],
                )
                .first()
            )
        contract = existing or ContractOpportunity(tenant_id=user.tenant_id)
        for key, value in item.items():
            setattr(contract, key, value)
        db.add(contract)
        db.flush()
        _score_and_store_contract(db, user.tenant_id, contract)
        imported.append(contract)
    db.commit()
    return imported


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

