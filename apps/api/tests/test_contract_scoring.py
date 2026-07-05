from datetime import datetime, timedelta, timezone

from app.services.contract_scoring import score_contract


def test_contract_scoring_recommends_pursue_for_direct_naics_match() -> None:
    result = score_contract(
        profile={
            "mission": "AI literacy and cybersecurity education",
            "focus_areas": ["cybersecurity education", "workforce development"],
            "past_performance": "training and responsible AI adoption",
        },
        contract={
            "title": "Cybersecurity and AI literacy training",
            "opportunity_type": "Sources Sought",
            "set_aside": "",
            "naics_code": "611430",
            "classification_code": "U008",
            "response_deadline": datetime.now(timezone.utc) + timedelta(days=30),
        },
        past_performance=[
            {
                "naics_codes": ["611430"],
                "classification_codes": ["U008"],
                "summary": "Cybersecurity education and AI literacy training",
                "outcomes": ["trained educators"],
            }
        ],
        partners=[],
    )
    assert result.total_score >= 78
    assert result.recommended_action == "Pursue"
    assert any("NAICS 611430" in reason for reason in result.reasons)


def test_contract_scoring_recommends_team_for_partner_naics_match() -> None:
    result = score_contract(
        profile={"mission": "technology education", "focus_areas": [], "past_performance": ""},
        contract={
            "title": "IT training support",
            "opportunity_type": "Solicitation",
            "set_aside": "Small Business",
            "naics_code": "541519",
            "classification_code": "D399",
            "response_deadline": datetime.now(timezone.utc) + timedelta(days=25),
        },
        past_performance=[],
        partners=[{"naics_codes": ["541519"], "set_aside_statuses": ["Small Business"]}],
    )
    assert result.recommended_action == "Team"
    assert any("teaming" in reason.lower() for reason in result.reasons)
