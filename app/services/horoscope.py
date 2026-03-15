import logging
from datetime import date

from openai import AsyncOpenAI

from app.config import settings
from app.services import cache

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None

_PROMPT = {
    "en": (
        "Daily horoscope for {sign}, {date}. "
        "~150 words. Cover: energy, relationships, work, one action tip. "
        "Warm, specific, no disclaimers."
    ),
    "hi": (
        "Write a daily horoscope for {sign} ({date}) in Hindi language. "
        "About 150 words. Cover energy, relationships, work, one practical tip. "
        "Warm, specific, no disclaimers."
    ),
}


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client


async def get_reading(sign: str, day: date, lang: str = "en") -> str:
    cache_key = f"{sign}:{lang}"
    cached = await cache.get_horoscope(cache_key, day)
    if cached:
        logger.debug("Cache hit for %s %s [%s]", sign, day, lang)
        return cached

    logger.info("Generating horoscope: %s %s lang=%s", sign, day, lang)
    prompt = _PROMPT.get(lang, _PROMPT["en"]).format(
        sign=sign, date=day.strftime("%B %d, %Y")
    )

    response = await _get_client().chat.completions.create(
        model=settings.openrouter_model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    reading = (response.choices[0].message.content or "").strip()
    if reading:
        await cache.set_horoscope(cache_key, day, reading)
    return reading
