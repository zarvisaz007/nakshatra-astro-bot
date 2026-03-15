import logging
from datetime import date

import anthropic

from app.config import settings
from app.services import cache

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None

SYSTEM_PROMPT = (
    "You are a thoughtful, modern astrologer. Write daily horoscope readings that are "
    "insightful, grounded, and practical — not generic. Each reading should feel personally "
    "relevant: touch on energy, relationships, work, and one actionable suggestion. "
    "Keep it 150-200 words. Warm, encouraging tone. No disclaimers."
)


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def get_reading(sign: str, day: date) -> str:
    cached = await cache.get_horoscope(sign, day)
    if cached:
        logger.debug("Cache hit for %s %s", sign, day)
        return cached

    logger.info("Generating reading for %s %s via Claude", sign, day)
    prompt = (
        f"Write today's horoscope for {sign.capitalize()}. "
        f"Date: {day.strftime('%B %d, %Y')}."
    )

    message = await _get_client().messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    reading = message.content[0].text.strip()
    await cache.set_horoscope(sign, day, reading)
    return reading
