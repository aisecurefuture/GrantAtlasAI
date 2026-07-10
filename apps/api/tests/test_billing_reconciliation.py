"""Stripe webhook reconciliation logic (no Stripe network calls)."""

from app.services.billing import apply_subscription_state, plan_for_price_id, subscription_limit_for_plan
from tests.conftest import make_tenant


def _event(event_type: str, obj: dict) -> dict:
    return {"id": "evt_test", "type": event_type, "data": {"object": obj}}


def test_checkout_completed_connects_customer_and_activates(db_session):
    tenant = make_tenant(db_session, "billing-a")
    event = _event(
        "checkout.session.completed",
        {
            "customer": "cus_123",
            "subscription": "sub_456",
            "metadata": {"tenant_id": tenant.id, "plan": "Professional"},
        },
    )
    result = apply_subscription_state(db_session, event)
    assert result is not None and result.id == tenant.id
    assert tenant.stripe_customer_id == "cus_123"
    assert tenant.stripe_subscription_id == "sub_456"
    assert tenant.plan == "Professional"
    assert tenant.subscription_status == "active"
    assert tenant.usage_limits == subscription_limit_for_plan("Professional")


def test_subscription_deleted_downgrades_to_free_trial(db_session):
    tenant = make_tenant(db_session, "billing-b")
    tenant.stripe_customer_id = "cus_789"
    tenant.plan = "Growth"
    db_session.commit()

    event = _event("customer.subscription.deleted", {"customer": "cus_789", "status": "canceled", "items": {"data": []}})
    result = apply_subscription_state(db_session, event)
    assert result is not None
    assert tenant.subscription_status == "canceled"
    assert tenant.plan == "Free Trial"


def test_payment_failed_marks_past_due(db_session):
    tenant = make_tenant(db_session, "billing-c")
    tenant.stripe_customer_id = "cus_pd"
    db_session.commit()

    result = apply_subscription_state(db_session, _event("invoice.payment_failed", {"customer": "cus_pd"}))
    assert result is not None
    assert tenant.subscription_status == "past_due"


def test_unknown_events_and_tenants_are_ignored(db_session):
    assert apply_subscription_state(db_session, _event("customer.created", {"customer": "cus_none"})) is None
    assert apply_subscription_state(db_session, _event("customer.subscription.updated", {"customer": "cus_missing"})) is None


def test_plan_for_price_id_returns_none_when_unconfigured():
    assert plan_for_price_id(None) is None
    assert plan_for_price_id("price_unknown") is None
