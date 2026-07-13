"""AI-powered analysis and drafting for GrantAtlas.

Two providers, selected by AI_PROVIDER:
  - "anthropic" (default): Claude via the Anthropic API. Enabled when
    ANTHROPIC_API_KEY is set.
  - "ollama": a local model (e.g. Gemma) served by Ollama — no usage costs.

When the selected provider isn't available these functions return None and the
product falls back to the transparent rules-based reasons alone.
"""

import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

NARRATIVE_SYSTEM_PROMPT = (
    "You are GrantAtlas, a funding-strategy analyst for nonprofits and small businesses. "
    "You are given an organization profile, a funding opportunity, and a transparent rules-based "
    "fit score with its component reasons. Write a crisp go/no-go analysis for a busy executive "
    "director: 2-4 sentences on why this opportunity does or does not fit, the single biggest risk "
    "or gap to address before applying, and one concrete next step. Plain prose, no headings, no "
    "bullet points, no restating raw numbers."
)

DRAFTING_SYSTEM_PROMPT = (
    "You are GrantAtlas, an expert grant and federal-proposal writer. You draft ONE section of a "
    "funding proposal at a time, in a confident, concrete, funder-ready voice that mirrors the "
    "funder's own priorities and language.\n\n"
    "STRICT GROUNDING RULES — these are non-negotiable:\n"
    "1. Use ONLY facts present in the ORGANIZATION PROFILE and REUSABLE CONTENT provided. Do not "
    "invent statistics, dollar amounts, dates, staff names, partner names, or past awards.\n"
    "2. Where a specific fact would strengthen the section but is NOT provided, insert a visible "
    "bracketed placeholder the writer must fill in, e.g. [INSERT: number of participants served in 2025] "
    "or [INSERT: name of evaluation partner]. Never fabricate a value to fill a placeholder.\n"
    "3. Tie the organization's real mission, programs, and past performance to the funder's stated "
    "goals and eligibility. Be specific, not generic.\n"
    "4. Return ONLY the section prose. No heading, no preamble, no meta-commentary, no markdown "
    "headers. 2-5 tight paragraphs."
)


def ai_enabled() -> bool:
    if settings.ai_provider == "ollama":
        return True
    return bool(settings.anthropic_api_key)


# ---------------- Public entry points ----------------


def generate_fit_narrative(profile: dict, subject: dict, score: dict, kind: str = "grant") -> str | None:
    if not ai_enabled():
        return None
    prompt = (
        f"Opportunity type: {kind}\n\n"
        f"Organization profile:\n{_format(profile)}\n\n"
        f"Opportunity:\n{_format(subject)}\n\n"
        f"Rules-based score:\n{_format(score)}"
    )
    return _complete(NARRATIVE_SYSTEM_PROMPT, prompt, max_tokens=1024, num_predict=250)


def generate_proposal_section(
    *,
    profile: dict,
    opportunity: dict,
    section_heading: str,
    section_guidance: str = "",
    library: list[dict],
    fit_reasons: list[str],
) -> str | None:
    """Draft a single proposal-section narrative, grounded in the org's own material."""
    if not ai_enabled():
        return None
    library_block = "\n\n".join(
        f"[{item.get('category', 'Content')}] {item.get('title', '')}\n{(item.get('body') or '')[:1500]}"
        for item in library
    ) or "(no reusable content provided — rely on the organization profile and use placeholders for specifics)"

    prompt = (
        f"SECTION TO DRAFT: {section_heading}\n"
        + (f"SECTION GUIDANCE: {section_guidance}\n" if section_guidance else "")
        + "\nOPPORTUNITY (the funder and what they want):\n"
        + _format(opportunity)
        + (f"\nWHY THIS IS A FIT (from scoring):\n- " + "\n- ".join(fit_reasons) if fit_reasons else "")
        + "\n\nORGANIZATION PROFILE (the applicant — ground all claims here):\n"
        + _format(profile)
        + "\n\nREUSABLE CONTENT (the applicant's own approved language — draw from this):\n"
        + library_block
    )
    return _complete(DRAFTING_SYSTEM_PROMPT, prompt, max_tokens=1600, num_predict=900)


# ---------------- Provider plumbing ----------------


def _complete(system_prompt: str, user_prompt: str, *, max_tokens: int, num_predict: int) -> str | None:
    try:
        if settings.ai_provider == "ollama":
            return _generate_ollama(system_prompt, user_prompt, num_predict)
        return _generate_anthropic(system_prompt, user_prompt, max_tokens)
    except Exception:
        logger.exception("AI generation failed (provider=%s)", settings.ai_provider)
        return None


def _generate_anthropic(system_prompt: str, user_prompt: str, max_tokens: int) -> str | None:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    if response.stop_reason == "refusal":
        return None
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or None


def _generate_ollama(system_prompt: str, user_prompt: str, num_predict: int) -> str | None:
    # Stream the response: local generation can take minutes (model load + slow
    # tokens under memory pressure), and Docker's host-gateway proxy drops
    # connections that sit idle — streaming keeps bytes flowing. `think: False`
    # stops reasoning models (Gemma 4) from spending the whole budget thinking.
    parts: list[str] = []
    with httpx.Client(timeout=httpx.Timeout(300, read=180)) as client:
        with client.stream(
            "POST",
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            json={
                "model": settings.ollama_model,
                "stream": True,
                "think": False,
                "options": {"num_predict": num_predict},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
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
