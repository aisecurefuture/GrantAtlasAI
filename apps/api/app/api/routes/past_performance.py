from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import PastPerformanceProject, Role, User
from app.schemas import PastPerformanceProjectIn, PastPerformanceProjectOut

router = APIRouter()


@router.get("", response_model=list[PastPerformanceProjectOut])
def list_projects(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[PastPerformanceProject]:
    return db.query(PastPerformanceProject).filter(PastPerformanceProject.tenant_id == user.tenant_id).order_by(PastPerformanceProject.created_at.desc()).all()


@router.post("", response_model=PastPerformanceProjectOut)
def create_project(
    payload: PastPerformanceProjectIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> PastPerformanceProject:
    project = PastPerformanceProject(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=PastPerformanceProjectOut)
def update_project(
    project_id: str,
    payload: PastPerformanceProjectIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> PastPerformanceProject:
    project = db.query(PastPerformanceProject).filter(PastPerformanceProject.id == project_id, PastPerformanceProject.tenant_id == user.tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Past performance project not found")
    for key, value in payload.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

