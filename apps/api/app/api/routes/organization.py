from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models import AuditLog, OrganizationProfile, Role, Tenant, User
from app.schemas import (
    AccountDeleteIn,
    OrganizationProfileIn,
    OrganizationProfileOut,
    TenantUserCreateIn,
    TenantUserCreateOut,
    TenantUserOut,
    TenantUserUpdateIn,
)
from app.models import ContractOpportunity, Opportunity
from app.services.accounts import email_taken, generate_temp_password, user_seat_limit
from app.services.ingestion import store_contract_score, store_opportunity_score

router = APIRouter()


def _active_owner_count(db: Session, tenant_id: str, excluding: str | None = None) -> int:
    query = db.query(User).filter(User.tenant_id == tenant_id, User.role == Role.OWNER, User.is_active.is_(True))
    if excluding:
        query = query.filter(User.id != excluding)
    return query.count()


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
    db.flush()

    # The profile drives every fit score, so re-score the tenant's pipeline —
    # this also covers records created before the profile was first filled in.
    for opportunity in db.query(Opportunity).filter(Opportunity.tenant_id == user.tenant_id).all():
        store_opportunity_score(db, user.tenant_id, opportunity)
    for contract in db.query(ContractOpportunity).filter(ContractOpportunity.tenant_id == user.tenant_id).all():
        store_contract_score(db, user.tenant_id, contract)

    db.commit()
    db.refresh(profile)
    return profile


# ---------------- Team management ----------------


@router.get("/users", response_model=list[TenantUserOut])
def list_users(user: User = Depends(require_role(Role.OWNER, Role.ADMIN)), db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).filter(User.tenant_id == user.tenant_id).order_by(User.created_at.asc()).all()


@router.post("/users", response_model=TenantUserCreateOut)
def create_user(
    payload: TenantUserCreateIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> TenantUserCreateOut:
    try:
        role = Role(payload.role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    if email_taken(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    tenant = db.get(Tenant, user.tenant_id)
    seat_limit = user_seat_limit(tenant)
    if seat_limit is not None:
        active_users = db.query(User).filter(User.tenant_id == tenant.id, User.is_active.is_(True)).count()
        if active_users >= seat_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Your {tenant.plan} plan includes {seat_limit} user seat{'s' if seat_limit != 1 else ''}. Upgrade to add more.",
            )
    temp_password = generate_temp_password()
    new_user = User(
        tenant_id=user.tenant_id,
        email=payload.email.lower(),
        name=payload.name,
        password_hash=hash_password(temp_password),
        role=role,
    )
    db.add(new_user)
    db.add(AuditLog(tenant_id=user.tenant_id, actor_user_id=user.id, action="organization.user.created", target_type="User"))
    db.commit()
    db.refresh(new_user)
    return TenantUserCreateOut(user=TenantUserOut.model_validate(new_user), temporary_password=temp_password)


@router.patch("/users/{user_id}", response_model=TenantUserOut)
def update_user(
    user_id: str,
    payload: TenantUserUpdateIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> User:
    target = db.query(User).filter(User.id == user_id, User.tenant_id == user.tenant_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id and payload.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account here")

    demoting_or_deactivating_owner = target.role == Role.OWNER and (
        payload.is_active is False or (payload.role is not None and payload.role != Role.OWNER.value)
    )
    if demoting_or_deactivating_owner and _active_owner_count(db, user.tenant_id, excluding=target.id) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An organization must keep at least one active Owner")

    if payload.role is not None:
        try:
            target.role = Role(payload.role)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    if payload.is_active is not None:
        target.is_active = payload.is_active
    db.add(AuditLog(tenant_id=user.tenant_id, actor_user_id=user.id, action="organization.user.updated", target_type="User", target_id=target.id))
    db.commit()
    db.refresh(target)
    return target


# ---------------- Account lifecycle (self-service) ----------------


@router.post("/deactivate")
def deactivate_account(user: User = Depends(require_role(Role.OWNER)), db: Session = Depends(get_db)) -> dict[str, str]:
    """Deactivate the whole organization: logins are blocked, data is retained."""
    tenant = db.get(Tenant, user.tenant_id)
    tenant.is_active = False
    tenant.subscription_status = "deactivated"
    db.add(AuditLog(tenant_id=tenant.id, actor_user_id=user.id, action="tenant.deactivated.self", target_type="Tenant", target_id=tenant.id))
    db.commit()
    return {"status": "deactivated"}


@router.post("/delete")
def delete_account(
    payload: AccountDeleteIn,
    user: User = Depends(require_role(Role.OWNER)),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Permanently delete the organization and all of its data."""
    tenant = db.get(Tenant, user.tenant_id)
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant.id).first()
    accepted_names = {tenant.name.strip().lower()}
    if profile:
        accepted_names.add(profile.organization_name.strip().lower())
    if payload.confirm_organization_name.strip().lower() not in accepted_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type your organization name exactly to confirm deletion",
        )
    db.add(AuditLog(tenant_id=None, actor_user_id=None, action="tenant.deleted.self", target_type="Tenant", target_id=tenant.id, metadata_json={"name": tenant.name}))
    db.delete(tenant)  # FK ondelete=CASCADE removes all tenant-scoped data
    db.commit()
    return {"status": "deleted"}

