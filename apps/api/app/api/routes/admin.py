from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import HTTPException, status
from sqlalchemy import func

from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models import AuditLog, ContractOpportunity, Opportunity, ProposalWorkspace, Tenant, User
from app.schemas import AdminTenantCreateIn, AdminTenantCreateOut, TenantUserOut
from app.services.accounts import VALID_SIGNUP_PLANS, create_tenant_with_owner, email_taken, generate_temp_password

router = APIRouter()


def _get_tenant(db: Session, tenant_id: str) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/tenants")
def list_tenants(_: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> list[dict]:
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    user_counts = dict(db.query(User.tenant_id, func.count(User.id)).group_by(User.tenant_id).all())
    opp_counts = dict(db.query(Opportunity.tenant_id, func.count(Opportunity.id)).group_by(Opportunity.tenant_id).all())
    return [
        {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan,
            "subscription_status": tenant.subscription_status,
            "trial_end": tenant.trial_end,
            "is_active": tenant.is_active,
            "user_count": user_counts.get(tenant.id, 0),
            "opportunity_count": opp_counts.get(tenant.id, 0),
        }
        for tenant in tenants
    ]


@router.post("/tenants", response_model=AdminTenantCreateOut)
def create_tenant(
    payload: AdminTenantCreateIn,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminTenantCreateOut:
    if payload.plan not in VALID_SIGNUP_PLANS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")
    if email_taken(db, payload.owner_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    temp_password = generate_temp_password()
    tenant, owner = create_tenant_with_owner(
        db,
        organization_name=payload.organization_name,
        owner_name=payload.owner_name,
        owner_email=payload.owner_email,
        password=temp_password,
        plan=payload.plan,
    )
    db.add(AuditLog(tenant_id=tenant.id, actor_user_id=admin.id, action="tenant.created.admin", target_type="Tenant", target_id=tenant.id))
    db.commit()
    db.refresh(owner)
    return AdminTenantCreateOut(tenant_id=tenant.id, owner=TenantUserOut.model_validate(owner), temporary_password=temp_password)


@router.post("/tenants/{tenant_id}/deactivate")
def deactivate_tenant(tenant_id: str, admin: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> dict:
    tenant = _get_tenant(db, tenant_id)
    if tenant_id == admin.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate the platform tenant")
    tenant.is_active = False
    tenant.subscription_status = "deactivated"
    db.add(AuditLog(tenant_id=tenant.id, actor_user_id=admin.id, action="tenant.deactivated.admin", target_type="Tenant", target_id=tenant.id))
    db.commit()
    return {"status": "deactivated", "tenant_id": tenant.id}


@router.post("/tenants/{tenant_id}/activate")
def activate_tenant(tenant_id: str, admin: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> dict:
    tenant = _get_tenant(db, tenant_id)
    tenant.is_active = True
    if tenant.subscription_status == "deactivated":
        tenant.subscription_status = "trialing" if tenant.stripe_subscription_id is None else "active"
    db.add(AuditLog(tenant_id=tenant.id, actor_user_id=admin.id, action="tenant.activated.admin", target_type="Tenant", target_id=tenant.id))
    db.commit()
    return {"status": "active", "tenant_id": tenant.id}


@router.delete("/tenants/{tenant_id}")
def delete_tenant(tenant_id: str, admin: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> dict:
    tenant = _get_tenant(db, tenant_id)
    if tenant_id == admin.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete the platform tenant")
    db.add(AuditLog(tenant_id=None, actor_user_id=admin.id, action="tenant.deleted.admin", target_type="Tenant", target_id=tenant.id, metadata_json={"name": tenant.name}))
    db.delete(tenant)
    db.commit()
    return {"status": "deleted", "tenant_id": tenant_id}


@router.get("/usage")
def usage(_: User = Depends(require_super_admin), db: Session = Depends(get_db)) -> dict:
    return {
        "tenants": db.query(Tenant).count(),
        "users": db.query(User).count(),
        "opportunities": db.query(Opportunity).count(),
        "contract_opportunities": db.query(ContractOpportunity).count(),
        "proposals": db.query(ProposalWorkspace).count(),
        "recent_audit_events": db.query(AuditLog).count(),
    }

