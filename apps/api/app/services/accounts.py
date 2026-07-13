"""Tenant and user provisioning shared by public registration and super-admin."""

import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import OrganizationProfile, Role, Tenant, User
from app.services.billing import AVAILABLE_PLANS, subscription_limit_for_plan

VALID_SIGNUP_PLANS = {plan["id"] for plan in AVAILABLE_PLANS} | {"Free Trial"}
TRIAL_DAYS = 14


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:100] or "org"


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    slug = base
    counter = 2
    while db.query(Tenant).filter(Tenant.slug == slug).first() is not None:
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def email_taken(db: Session, email: str) -> bool:
    # Login looks users up by email globally, so emails must be unique across tenants.
    return db.query(User).filter(User.email == email.lower()).first() is not None


def generate_temp_password() -> str:
    return secrets.token_urlsafe(12)


def create_tenant_with_owner(
    db: Session,
    *,
    organization_name: str,
    owner_name: str,
    owner_email: str,
    password: str,
    plan: str,
) -> tuple[Tenant, User]:
    """Create a tenant on a trial of the chosen plan, plus its Owner user and profile stub."""
    tenant = Tenant(
        name=organization_name,
        slug=unique_slug(db, organization_name),
        plan=plan,
        subscription_status="trialing",
        trial_end=datetime.now(timezone.utc) + timedelta(days=settings.stripe_trial_days or TRIAL_DAYS),
        usage_limits=subscription_limit_for_plan(plan),
    )
    db.add(tenant)
    db.flush()
    owner = User(
        tenant_id=tenant.id,
        email=owner_email.lower(),
        name=owner_name,
        password_hash=hash_password(password),
        role=Role.OWNER,
    )
    db.add(owner)
    db.add(OrganizationProfile(tenant_id=tenant.id, organization_name=organization_name))
    return tenant, owner


def user_seat_limit(tenant: Tenant) -> int | None:
    limits = tenant.usage_limits or subscription_limit_for_plan(tenant.plan)
    return limits.get("users")
