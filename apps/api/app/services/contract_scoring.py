from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ContractScoreResult:
    total_score: float
    naics_fit: float
    psc_fit: float
    past_performance_fit: float
    set_aside_fit: float
    deadline_fit: float
    competition_fit: float
    strategic_value: float
    recommended_action: str
    reasons: list[str]


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, round(value, 1)))


def _tokens(values: list[str] | str | None) -> set[str]:
    if not values:
        return set()
    text = " ".join(values) if isinstance(values, list) else values
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {part for part in cleaned.split() if len(part) > 2}


def score_contract(profile: dict, contract: dict, past_performance: list[dict], partners: list[dict], now: datetime | None = None) -> ContractScoreResult:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []

    target_naics = contract.get("naics_code")
    target_psc = contract.get("classification_code")
    past_naics = {code for project in past_performance for code in project.get("naics_codes", [])}
    past_psc = {code for project in past_performance for code in project.get("classification_codes", [])}
    partner_naics = {code for partner in partners for code in partner.get("naics_codes", [])}

    naics_fit = 90 if target_naics and target_naics in past_naics else 70 if target_naics and target_naics in partner_naics else 45
    if target_naics and target_naics in past_naics:
        reasons.append(f"Direct past performance match on NAICS {target_naics}.")
    elif target_naics and target_naics in partner_naics:
        reasons.append(f"Partner network has NAICS {target_naics}; teaming may improve fit.")
    elif target_naics:
        reasons.append(f"No direct NAICS {target_naics} match found in past performance or partners.")
    else:
        reasons.append("NAICS code is missing; NAICS fit is neutral-low.")

    psc_fit = 88 if target_psc and target_psc in past_psc else 55 if target_psc else 50
    if target_psc and target_psc in past_psc:
        reasons.append(f"Past performance includes PSC/classification {target_psc}.")

    contract_terms = _tokens([contract.get("title") or "", contract.get("opportunity_type") or "", contract.get("set_aside") or ""])
    profile_terms = _tokens(profile.get("focus_areas")) | _tokens(profile.get("mission")) | _tokens(profile.get("past_performance"))
    past_terms = set()
    for project in past_performance:
        past_terms |= _tokens(project.get("summary"))
        past_terms |= _tokens(project.get("outcomes"))
    overlap = contract_terms & (profile_terms | past_terms)
    past_performance_fit = _clamp(45 + min(len(overlap) * 8, 40) + (15 if target_naics and target_naics in past_naics else 0))
    if overlap:
        reasons.append(f"Capability language overlaps on: {', '.join(sorted(list(overlap))[:6])}.")

    set_aside = (contract.get("set_aside") or "").lower()
    partner_set_asides = {status.lower() for partner in partners for status in partner.get("set_aside_statuses", [])}
    if not set_aside:
        set_aside_fit = 70
    elif any(status in set_aside for status in partner_set_asides):
        set_aside_fit = 85
        reasons.append("A known teaming partner may satisfy the set-aside posture.")
    elif "small business" in set_aside or "8(a)" in set_aside or "veteran" in set_aside:
        set_aside_fit = 45
        reasons.append("Set-aside may require prime eligibility or a qualified partner.")
    else:
        set_aside_fit = 60

    deadline = contract.get("response_deadline")
    deadline_fit = 55
    if deadline:
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        days = (deadline - now).days
        if days < 0:
            deadline_fit = 0
            reasons.append("Response deadline has passed.")
        elif days <= 10:
            deadline_fit = 45
            reasons.append("Response deadline is very close; only pursue with existing materials.")
        elif days <= 45:
            deadline_fit = 82
            reasons.append("Response deadline has workable capture/proposal runway.")
        else:
            deadline_fit = 75

    competition_fit = 80 if contract.get("opportunity_type") in {"Sources Sought", "Special Notice"} else 65
    strategic_value = _clamp((naics_fit * 0.35) + (past_performance_fit * 0.35) + (set_aside_fit * 0.15) + (competition_fit * 0.15))
    total = _clamp(
        naics_fit * 0.22
        + psc_fit * 0.12
        + past_performance_fit * 0.22
        + set_aside_fit * 0.14
        + deadline_fit * 0.12
        + competition_fit * 0.08
        + strategic_value * 0.1
    )

    if total >= 78:
        action = "Pursue"
    elif target_naics and target_naics in partner_naics:
        action = "Team"
    elif total >= 55:
        action = "Watch"
    else:
        action = "No Bid"

    reasons.append(f"Recommended action: {action} based on v2 contract scoring score of {total}.")
    return ContractScoreResult(
        total_score=total,
        naics_fit=naics_fit,
        psc_fit=psc_fit,
        past_performance_fit=past_performance_fit,
        set_aside_fit=set_aside_fit,
        deadline_fit=deadline_fit,
        competition_fit=competition_fit,
        strategic_value=strategic_value,
        recommended_action=action,
        reasons=reasons,
    )

