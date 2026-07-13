from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import Opportunity, ProposalWorkspace, Role, User
from app.schemas import ProposalWorkspaceIn, ProposalWorkspaceOut, ProposalWorkspaceUpdateIn

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

