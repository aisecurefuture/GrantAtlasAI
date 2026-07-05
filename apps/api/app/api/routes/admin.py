from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models import AuditLog, Opportunity, Tenant, User

router = APIRouter()


@router.get("/tenants")
def list_tenants(_: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> list[dict]:
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    return [
        {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan,
            "subscription_status": tenant.subscription_status,
            "trial_end": tenant.trial_end,
        }
        for tenant in tenants
    ]


@router.get("/usage")
def usage(_: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> dict:
    return {
        "tenants": db.query(Tenant).count(),
        "users": db.query(User).count(),
        "opportunities": db.query(Opportunity).count(),
        "recent_audit_events": db.query(AuditLog).count(),
    }

