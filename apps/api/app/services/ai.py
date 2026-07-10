"""Claude-powered narrative analysis for scored opportunities.

Env-gated: when ANTHROPIC_API_KEY is unset these functions return None and the
product falls back to the transparent rules-based reasons alone.
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are GrantAtlas, a funding-strategy analyst for nonprofits and small businesses. "
    "You are given an organization profile, a funding opportunity, and a transparent rules-based "
    "fit score with its component reasons. Write a crisp go/no-go analysis for a busy executive "
    "director: 2-4 sentences on why this opportunity does or does not fit, the single biggest risk "
    "or gap to address before applying, and one concrete next step. Plain prose, no headings, no "
    "bullet points, no restating raw numbers."
)


def ai_enabled() -> bool:
    return bool(settings.anthropic_api_key)


def generate_fit_narrative(profile: dict, subject: dict, score: dict, kind: str = "grant") -> str | None:
    """Return a short narrative fit analysis, or None when AI is not configured or fails."""
    if not ai_enabled():
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Opportunity type: {kind}\n\n"
                        f"Organization profile:\n{_format(profile)}\n\n"
                        f"Opportunity:\n{_format(subject)}\n\n"
                        f"Rules-based score:\n{_format(score)}"
                    ),
                }
            ],
        )
        if response.stop_reason == "refusal":
            return None
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        return text or None
    except Exception:
        logger.exception("AI narrative generation failed")
        return None


def _format(data: dict) -> str:
    lines = []
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) or "- (no data)"
