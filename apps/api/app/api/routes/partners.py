from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import Role, TeamingPartner, User
from app.schemas import TeamingPartnerIn, TeamingPartnerOut

router = APIRouter()


@router.get("", response_model=list[TeamingPartnerOut])
def list_partners(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[TeamingPartner]:
    return db.query(TeamingPartner).filter(TeamingPartner.tenant_id == user.tenant_id).order_by(TeamingPartner.name.asc()).all()


@router.post("", response_model=TeamingPartnerOut)
def create_partner(
    payload: TeamingPartnerIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> TeamingPartner:
    partner = TeamingPartner(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner


@router.put("/{partner_id}", response_model=TeamingPartnerOut)
def update_partner(
    partner_id: str,
    payload: TeamingPartnerIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> TeamingPartner:
    partner = db.query(TeamingPartner).filter(TeamingPartner.id == partner_id, TeamingPartner.tenant_id == user.tenant_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Teaming partner not found")
    for key, value in payload.model_dump().items():
        setattr(partner, key, value)
    db.commit()
    db.refresh(partner)
    return partner

