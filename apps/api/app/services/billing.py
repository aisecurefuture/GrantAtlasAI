from app.core.config import settings


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

