"""AI-powered narrative analysis for scored opportunities.

Two providers, selected by AI_PROVIDER:
  - "anthropic" (default): Claude via the Anthropic API. Enabled when
    ANTHROPIC_API_KEY is set.
  - "ollama": a local model (e.g. Gemma) served by Ollama — no usage costs.
    Enabled when the Ollama server is reachable.

When the selected provider isn't available these functions return None and the
product falls back to the transparent rules-based reasons alone.
"""

import logging

import httpx

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
    if settings.ai_provider == "ollama":
        return True
    return bool(settings.anthropic_api_key)


def generate_fit_narrative(profile: dict, subject: dict, score: dict, kind: str = "grant") -> str | None:
    """Return a short narrative fit analysis, or None when AI is not configured or fails."""
    if not ai_enabled():
        return None
    prompt = (
        f"Opportunity type: {kind}\n\n"
        f"Organization profile:\n{_format(profile)}\n\n"
        f"Opportunity:\n{_format(subject)}\n\n"
        f"Rules-based score:\n{_format(score)}"
    )
    try:
        if settings.ai_provider == "ollama":
            return _generate_ollama(prompt)
        return _generate_anthropic(prompt)
    except Exception:
        logger.exception("AI narrative generation failed (provider=%s)", settings.ai_provider)
        return None


def _generate_anthropic(prompt: str) -> str | None:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        return None
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or None


def _generate_ollama(prompt: str) -> str | None:
    # Stream the response: local generation can take minutes (model load +
    # slow tokens under memory pressure), and Docker's host-gateway proxy
    # drops connections that sit idle — streaming keeps bytes flowing.
    import json

    parts: list[str] = []
    with httpx.Client(timeout=httpx.Timeout(300, read=120)) as client:
        with client.stream(
            "POST",
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            json={
                "model": settings.ollama_model,
                "stream": True,
                # Reasoning models (e.g. Gemma 4) otherwise spend the whole
                # token budget thinking and return empty content.
                "think": False,
                "options": {"num_predict": 250},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                parts.append((chunk.get("message") or {}).get("content", ""))
                if chunk.get("done"):
                    break
    text = "".join(parts).strip()
    return text or None


def _format(data: dict) -> str:
    lines = []
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) or "- (no data)"
