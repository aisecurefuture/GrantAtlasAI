from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ScoreResult:
    total_score: float
    mission_fit: float
    eligibility_fit: float
    deadline_urgency: float
    funding_size: float
    proposal_complexity: float
    partnership_fit: float
    past_performance_fit: float
    strategic_value: float
    probability_of_success: float
    recommended_action: str
    reasons: list[str]


def _tokens(value: str | list[str] | None) -> set[str]:
    if value is None:
        return set()
    text = " ".join(value) if isinstance(value, list) else value
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {part for part in cleaned.split() if len(part) > 2}


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, round(value, 1)))


def score_opportunity(profile: dict, opportunity: dict, now: datetime | None = None) -> ScoreResult:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []

    profile_terms = (
        _tokens(profile.get("mission"))
        | _tokens(profile.get("focus_areas"))
        | _tokens(profile.get("programs"))
        | _tokens(profile.get("target_populations"))
        | _tokens(profile.get("past_performance"))
    )
    opportunity_terms = (
        _tokens(opportunity.get("title"))
        | _tokens(opportunity.get("description"))
        | _tokens(opportunity.get("categories"))
        | _tokens(opportunity.get("keywords"))
    )
    overlap = profile_terms & opportunity_terms
    mission_fit = _clamp(35 + min(len(overlap) * 8, 55))
    if overlap:
        reasons.append(f"Mission overlap found for: {', '.join(sorted(list(overlap))[:8])}.")
    else:
        reasons.append("Limited direct mission keyword overlap; review strategic fit manually.")

    eligibility_text = (opportunity.get("eligibility") or "").lower()
    nonprofit_terms = ["nonprofit", "501", "charitable", "education", "institution"]
    eligibility_hits = [term for term in nonprofit_terms if term in eligibility_text]
    eligibility_fit = _clamp(45 + len(eligibility_hits) * 13)
    if eligibility_hits:
        reasons.append("Eligibility language appears compatible with nonprofit or education applicants.")
    else:
        reasons.append("Eligibility is unclear or does not explicitly mention nonprofit-aligned applicants.")

    close_date = opportunity.get("close_date")
    deadline_urgency = 50.0
    if close_date:
        if close_date.tzinfo is None:
            close_date = close_date.replace(tzinfo=timezone.utc)
        days = (close_date - now).days
        if days < 0:
            deadline_urgency = 0
            reasons.append("Deadline has passed.")
        elif days <= 14:
            deadline_urgency = 95
            reasons.append("Deadline is within 14 days; treat as urgent.")
        elif days <= 45:
            deadline_urgency = 80
            reasons.append("Deadline is approaching within 45 days.")
        else:
            deadline_urgency = 60
            reasons.append("Deadline has enough runway for planning.")

    ceiling = opportunity.get("award_ceiling") or 0
    if ceiling >= 500_000:
        funding_size = 90
        reasons.append("Funding ceiling is large enough to justify a full proposal effort.")
    elif ceiling >= 100_000:
        funding_size = 75
    elif ceiling > 0:
        funding_size = 55
    else:
        funding_size = 50
        reasons.append("Award ceiling is missing; funding size score is neutral.")

    complexity_penalty = 0
    if opportunity.get("cost_share_required"):
        complexity_penalty += 20
        reasons.append("Cost share requirement increases proposal complexity.")
    if opportunity.get("required_partners"):
        complexity_penalty += 15
        reasons.append("Partner requirement should be validated before applying.")
    proposal_complexity = _clamp(85 - complexity_penalty)
    partnership_fit = 55 if opportunity.get("required_partners") else 85

    past_terms = _tokens(profile.get("past_performance"))
    past_performance_fit = _clamp(45 + min(len(past_terms & opportunity_terms) * 10, 45))
    strategic_value = _clamp((mission_fit * 0.7) + (funding_size * 0.3))
    probability_of_success = _clamp((eligibility_fit * 0.35) + (mission_fit * 0.3) + (past_performance_fit * 0.2) + (proposal_complexity * 0.15))

    total = _clamp(
        mission_fit * 0.22
        + eligibility_fit * 0.18
        + deadline_urgency * 0.08
        + funding_size * 0.12
        + proposal_complexity * 0.08
        + partnership_fit * 0.08
        + past_performance_fit * 0.1
        + strategic_value * 0.08
        + probability_of_success * 0.06
    )

    if total >= 78 and eligibility_fit >= 65:
        action = "Apply"
    elif opportunity.get("required_partners") or partnership_fit < 70:
        action = "Partner"
    elif total >= 55:
        action = "Monitor"
    else:
        action = "Skip"

    reasons.append(f"Recommended action: {action} based on a transparent rules score of {total}.")
    return ScoreResult(
        total_score=total,
        mission_fit=mission_fit,
        eligibility_fit=eligibility_fit,
        deadline_urgency=deadline_urgency,
        funding_size=funding_size,
        proposal_complexity=proposal_complexity,
        partnership_fit=partnership_fit,
        past_performance_fit=past_performance_fit,
        strategic_value=strategic_value,
        probability_of_success=probability_of_success,
        recommended_action=action,
        reasons=reasons,
    )

