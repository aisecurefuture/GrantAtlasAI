from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Tenant


# Published pricing from the GrantAtlas pitch deck (annual prices are the -20% figures).
AVAILABLE_PLANS = [
    {"id": "Starter", "name": "Starter", "price_monthly": 149, "price_annual": 119, "seats": "2 users", "blurb": "Discovery, fit scoring, and pipeline."},
    {"id": "Professional", "name": "Professional", "price_monthly": 349, "price_annual": 279, "seats": "5 users", "blurb": "Proposal workspaces, content library, capture plans."},
    {"id": "Growth", "name": "Growth", "price_monthly": 749, "price_annual": 599, "seats": "15 users", "blurb": "Partner CRM, past performance, advanced reporting."},
    {"id": "Enterprise", "name": "Enterprise", "price_monthly": 1500, "price_annual": 1500, "seats": "Custom", "blurb": "Universities, municipalities, multi-team funding ops."},
]


PLAN_PRICE_IDS = {
    "Starter": "stripe_starter_price_id",
    "Professional": "stripe_professional_price_id",
    "Growth": "stripe_growth_price_id",
    "Enterprise": "stripe_enterprise_price_id",
}


def price_id_for_plan(plan: str) -> str | None:
    attr = PLAN_PRICE_IDS.get(plan)
    return getattr(settings, attr) if attr else None


def subscription_limit_for_plan(plan: str) -> dict:
    limits = {
        "Free Trial": {"saved_opportunities": 25, "users": 3, "proposal_workspaces": 5},
        "Starter": {"saved_opportunities": 50, "users": 1, "proposal_workspaces": 5},
        "Professional": {"saved_opportunities": 250, "users": 10, "proposal_workspaces": 50},
        "Growth": {"saved_opportunities": 1000, "users": 25, "proposal_workspaces": 250},
        "Enterprise": {"saved_opportunities": None, "users": None, "proposal_workspaces": None},
    }
    return limits.get(plan, limits["Free Trial"])


def plan_for_price_id(price_id: str | None) -> str | None:
    if not price_id:
        return None
    for plan, attr in PLAN_PRICE_IDS.items():
        if getattr(settings, attr) == price_id:
            return plan
    return None


def _tenant_for_event(db: Session, data: dict[str, Any]) -> Tenant | None:
    metadata = data.get("metadata") or {}
    tenant_id = metadata.get("tenant_id")
    if tenant_id:
        tenant = db.get(Tenant, tenant_id)
        if tenant:
            return tenant
    customer_id = data.get("customer")
    if customer_id:
        return db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
    return None


def apply_subscription_state(db: Session, event: dict[str, Any]) -> Tenant | None:
    """Reconcile tenant plan/subscription state from a verified Stripe webhook event.

    Handles checkout completion, subscription lifecycle updates, and payment failure.
    Returns the affected tenant, or None when the event doesn't map to one.
    """
    event_type = event.get("type", "")
    data = (event.get("data") or {}).get("object") or {}

    if event_type == "checkout.session.completed":
        tenant = _tenant_for_event(db, data)
        if not tenant:
            return None
        if data.get("customer"):
            tenant.stripe_customer_id = data["customer"]
        if data.get("subscription"):
            tenant.stripe_subscription_id = data["subscription"]
        plan = (data.get("metadata") or {}).get("plan")
        if plan in PLAN_PRICE_IDS:
            tenant.plan = plan
            tenant.usage_limits = subscription_limit_for_plan(plan)
        tenant.subscription_status = "active"
        return tenant

    if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
        tenant = _tenant_for_event(db, data)
        if not tenant:
            return None
        status = data.get("status") or ("canceled" if event_type.endswith("deleted") else tenant.subscription_status)
        tenant.subscription_status = status
        tenant.stripe_subscription_id = data.get("id") or tenant.stripe_subscription_id
        items = ((data.get("items") or {}).get("data")) or []
        price_id = (items[0].get("price") or {}).get("id") if items else None
        plan = plan_for_price_id(price_id)
        if plan:
            tenant.plan = plan
            tenant.usage_limits = subscription_limit_for_plan(plan)
        trial_end = data.get("trial_end")
        if trial_end:
            tenant.trial_end = datetime.fromtimestamp(trial_end, tz=timezone.utc)
        if event_type.endswith("deleted"):
            tenant.plan = "Free Trial"
            tenant.usage_limits = subscription_limit_for_plan("Free Trial")
        return tenant

    if event_type == "invoice.payment_failed":
        tenant = _tenant_for_event(db, data)
        if not tenant:
            return None
        tenant.subscription_status = "past_due"
        return tenant

    return None

