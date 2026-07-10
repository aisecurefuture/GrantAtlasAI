from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.core.config import settings
from app.db.session import get_db
from app.models import AuditLog, Opportunity, ProposalWorkspace, Role, Tenant, User
from app.schemas import BillingSummaryOut
from app.services.billing import (
    AVAILABLE_PLANS,
    apply_subscription_state,
    plan_for_price_id,
    price_id_for_plan,
    subscription_limit_for_plan,
)

router = APIRouter()


@router.get("/summary", response_model=BillingSummaryOut)
def billing_summary(user: User = Depends(current_user), db: Session = Depends(get_db)) -> BillingSummaryOut:
    tenant = db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    usage = {
        "users": db.query(User).filter(User.tenant_id == tenant.id).count(),
        "saved_opportunities": db.query(Opportunity).filter(Opportunity.tenant_id == tenant.id).count(),
        "proposal_workspaces": db.query(ProposalWorkspace).filter(ProposalWorkspace.tenant_id == tenant.id).count(),
    }
    return BillingSummaryOut(
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        trial_end=tenant.trial_end,
        stripe_configured=bool(settings.stripe_secret_key),
        stripe_customer_connected=bool(tenant.stripe_customer_id),
        limits=subscription_limit_for_plan(tenant.plan),
        usage=usage,
        available_plans=AVAILABLE_PLANS,
    )


@router.post("/checkout")
def create_checkout_session(plan: str, user: User = Depends(require_role(Role.OWNER, Role.ADMIN)), db: Session = Depends(get_db)) -> dict[str, str]:
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
def create_portal_session(user: User = Depends(require_role(Role.OWNER, Role.ADMIN)), db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    import stripe

    stripe.api_key = settings.stripe_secret_key
    tenant = db.get(Tenant, user.tenant_id)
    if not tenant or not tenant.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Stripe customer is not connected")
    session = stripe.billing_portal.Session.create(customer=tenant.stripe_customer_id, return_url=f"{settings.web_base_url}/billing")
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhooks are not configured")
    import stripe

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook signature") from exc

    handled = apply_subscription_state(db, event)
    if handled:
        db.add(
            AuditLog(
                tenant_id=handled.id,
                action=f"billing.webhook.{event['type']}",
                target_type="Tenant",
                target_id=handled.id,
                metadata_json={"event_id": event.get("id")},
            )
        )
        db.commit()
    return {"status": "ok"}
