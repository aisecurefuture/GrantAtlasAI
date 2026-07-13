from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import LibraryItem, Opportunity, OpportunityScore, OrganizationProfile, ProposalWorkspace, Role, User
from app.schemas import ProposalSectionDraftIn, ProposalWorkspaceIn, ProposalWorkspaceOut, ProposalWorkspaceUpdateIn
from app.services.ai import ai_enabled, generate_proposal_section

router = APIRouter()


@router.get("", response_model=list[ProposalWorkspaceOut])
def list_workspaces(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ProposalWorkspace]:
    return db.query(ProposalWorkspace).filter(ProposalWorkspace.tenant_id == user.tenant_id).order_by(ProposalWorkspace.updated_at.desc()).all()


@router.post("", response_model=ProposalWorkspaceOut)
def create_workspace(
    payload: ProposalWorkspaceIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ProposalWorkspace:
    opportunity = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id, Opportunity.tenant_id == user.tenant_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    workspace = ProposalWorkspace(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=ProposalWorkspaceOut)
def get_workspace(workspace_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ProposalWorkspace:
    workspace = db.query(ProposalWorkspace).filter(ProposalWorkspace.id == workspace_id, ProposalWorkspace.tenant_id == user.tenant_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Proposal workspace not found")
    return workspace


@router.put("/{workspace_id}", response_model=ProposalWorkspaceOut)
def update_workspace(
    workspace_id: str,
    payload: ProposalWorkspaceUpdateIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ProposalWorkspace:
    workspace = db.query(ProposalWorkspace).filter(ProposalWorkspace.id == workspace_id, ProposalWorkspace.tenant_id == user.tenant_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Proposal workspace not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(workspace, key, value)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.post("/{workspace_id}/draft-section", response_model=ProposalWorkspaceOut)
def draft_section(
    workspace_id: str,
    payload: ProposalSectionDraftIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> ProposalWorkspace:
    if not ai_enabled():
        raise HTTPException(status_code=503, detail="AI drafting is not configured on this environment")
    workspace = db.query(ProposalWorkspace).filter(ProposalWorkspace.id == workspace_id, ProposalWorkspace.tenant_id == user.tenant_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Proposal workspace not found")
    opportunity = db.query(Opportunity).filter(Opportunity.id == workspace.opportunity_id, Opportunity.tenant_id == user.tenant_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Linked opportunity not found")

    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    library = db.query(LibraryItem).filter(LibraryItem.tenant_id == user.tenant_id).order_by(LibraryItem.updated_at.desc()).limit(12).all()
    score = db.query(OpportunityScore).filter(OpportunityScore.opportunity_id == opportunity.id, OpportunityScore.tenant_id == user.tenant_id).first()

    draft = generate_proposal_section(
        profile={
            "organization_name": profile.organization_name if profile else "",
            "mission": profile.mission if profile else "",
            "vision": profile.vision if profile else "",
            "programs": profile.programs if profile else [],
            "focus_areas": profile.focus_areas if profile else [],
            "target_populations": profile.target_populations if profile else [],
            "geographic_service_area": profile.geographic_service_area if profile else "",
            "past_performance": profile.past_performance if profile else "",
        },
        opportunity={
            "title": opportunity.title,
            "agency": opportunity.agency,
            "description": (opportunity.description or "")[:2500],
            "eligibility": (opportunity.eligibility or "")[:1200],
            "award_ceiling": opportunity.award_ceiling,
            "categories": opportunity.categories,
        },
        section_heading=payload.heading,
        section_guidance=payload.guidance,
        library=[{"title": item.title, "category": item.category, "body": item.body} for item in library],
        fit_reasons=list(score.reasons) if score and score.reasons else [],
    )
    if not draft:
        raise HTTPException(status_code=502, detail="AI drafting is temporarily unavailable")

    # Upsert the drafted content into narrative_sections keyed by heading.
    sections = [dict(s) for s in (workspace.narrative_sections or [])]
    for section in sections:
        if section.get("heading") == payload.heading:
            section["content"] = draft
            break
    else:
        sections.append({"heading": payload.heading, "content": draft})
    workspace.narrative_sections = sections
    db.commit()
    db.refresh(workspace)
    return workspace

