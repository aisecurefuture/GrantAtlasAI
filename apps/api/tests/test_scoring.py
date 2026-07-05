from datetime import datetime, timedelta, timezone

from app.services.scoring import score_opportunity


def test_scoring_recommends_apply_for_strong_fit() -> None:
    profile = {
        "mission": "AI safety education and cybersecurity education for nonprofits",
        "focus_areas": ["AI literacy", "nonprofit cybersecurity"],
        "programs": ["teacher AI literacy"],
        "target_populations": ["teachers", "nonprofits"],
        "past_performance": "cybersecurity education and AI literacy workshops",
    }
    opportunity = {
        "title": "Nonprofit AI Literacy and Cybersecurity Education Grant",
        "description": "Funds nonprofit cybersecurity and AI safety education programs.",
        "categories": ["education"],
        "keywords": ["AI literacy", "cybersecurity"],
        "eligibility": "Nonprofit organizations and educational institutions may apply.",
        "close_date": datetime.now(timezone.utc) + timedelta(days=40),
        "award_ceiling": 500000,
        "cost_share_required": False,
        "required_partners": "",
    }
    result = score_opportunity(profile, opportunity)
    assert result.total_score >= 78
    assert result.recommended_action == "Apply"
    assert result.reasons


def test_scoring_flags_partner_requirement() -> None:
    result = score_opportunity(
        {"mission": "AI education", "focus_areas": ["AI"], "programs": [], "target_populations": [], "past_performance": ""},
        {
            "title": "Regional innovation partnership",
            "description": "Requires formal partnership network.",
            "categories": [],
            "keywords": [],
            "eligibility": "",
            "close_date": datetime.now(timezone.utc) + timedelta(days=60),
            "award_ceiling": 100000,
            "cost_share_required": False,
            "required_partners": "University partner required",
        },
    )
    assert result.recommended_action == "Partner"
    assert any("Partner requirement" in reason for reason in result.reasons)

