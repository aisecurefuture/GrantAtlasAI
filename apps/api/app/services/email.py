import httpx

from app.core.config import settings


async def send_email(to: str, subject: str, html: str) -> bool:
    if not settings.resend_api_key:
        return False
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={"from": settings.email_from, "to": [to], "subject": subject, "html": html},
        )
        response.raise_for_status()
    return True

