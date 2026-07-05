from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import AuditLog, OrganizationProfile, Role, User
from app.schemas import OrganizationProfileIn, OrganizationProfileOut

router = APIRouter()


@router.get("/profile", response_model=OrganizationProfileOut)
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)) -> OrganizationProfile:
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Organization profile not found")
    return profile


@router.put("/profile", response_model=OrganizationProfileOut)
def update_profile(
    payload: OrganizationProfileIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> OrganizationProfile:
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    if not profile:
        profile = OrganizationProfile(tenant_id=user.tenant_id, **payload.model_dump())
        db.add(profile)
    else:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
    db.add(AuditLog(tenant_id=user.tenant_id, actor_user_id=user.id, action="organization.profile.updated", target_type="OrganizationProfile", target_id=profile.id))
    db.commit()
    db.refresh(profile)
    return profile

