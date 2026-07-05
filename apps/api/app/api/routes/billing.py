from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Tenant, User
from app.services.billing import price_id_for_plan

router = APIRouter()


@router.post("/checkout")
def create_checkout_session(plan: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    import stripe

    stripe.api_key = settings.stripe_secret_key
    tenant = db.get(Tenant, user.tenant_id)
    price_id = price_id_for_plan(plan)
    if not tenant or not price_id:
        raise HTTPException(status_code=400, detail="Invalid tenant or plan")
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=tenant.stripe_customer_id or None,
        customer_email=None if tenant.stripe_customer_id else user.email,
        line_items=[{"price": price_id, "quantity": 1}],
        subscription_data={"trial_period_days": settings.stripe_trial_days, "metadata": {"tenant_id": tenant.id}},
        success_url=f"{settings.web_base_url}/dashboard?billing=success",
        cancel_url=f"{settings.web_base_url}/dashboard?billing=cancelled",
        metadata={"tenant_id": tenant.id, "plan": plan},
    )
    return {"url": session.url}


@router.post("/portal")
def create_portal_session(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    import stripe

    stripe.api_key = settings.stripe_secret_key
    tenant = db.get(Tenant, user.tenant_id)
    if not tenant or not tenant.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Stripe customer is not connected")
    session = stripe.billing_portal.Session.create(customer=tenant.stripe_customer_id, return_url=f"{settings.web_base_url}/dashboard")
    return {"url": session.url}

