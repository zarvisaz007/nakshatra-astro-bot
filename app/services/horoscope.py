import logging
from datetime import date

from openai import AsyncOpenAI

from app.config import settings
from app.services import cache

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None

# Compact prompts — fold sign context into one message, no system prompt overhead
_HORO_PROMPT = {
    "en": (
        "Daily Vedic horoscope for {sign} ({rashi}), {date}. "
        "Moon in {moon_sign}, nakshatra {nakshatra}. "
        "~150 words. Include: energy, relationships, work, lucky number {lucky_num}, lucky color {lucky_color}. "
        "Warm, specific, actionable. No disclaimers."
    ),
    "hi": (
        "Write daily Vedic horoscope for {sign} ({rashi}) in Hindi, {date}. "
        "Moon in {moon_sign}, nakshatra {nakshatra}. "
        "~150 words. Include energy, relationships, work, lucky number {lucky_num}, lucky color {lucky_color}. "
        "Warm and specific."
    ),
}

_INTRO_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Write a warm 3-sentence personalized introduction for {name}. "
        "They have: Lagna {lagna}, Moon sign {rashi}, Nakshatra {nakshatra} (lord {nak_lord}), "
        "current Mahadasha {dasha}. Be specific and encouraging."
    ),
    "hi": (
        "You are a Vedic astrologer. Write a warm 3-sentence personalized introduction in Hindi for {name}. "
        "They have: Lagna {lagna}, Moon sign {rashi}, Nakshatra {nakshatra} (lord {nak_lord}), "
        "current Mahadasha {dasha}. Be specific and encouraging."
    ),
}

_ASK_PROMPT = {
    "en": (
        "You are a Vedic astrologer answering: \"{question}\"\n"
        "User profile: {name}, Lagna {lagna}, Rashi {rashi}, Nakshatra {nakshatra}, "
        "Mahadasha {dasha}. ~100 words. Specific, grounded in Vedic principles."
    ),
    "hi": (
        "You are a Vedic astrologer. Answer in Hindi: \"{question}\"\n"
        "User: {name}, Lagna {lagna}, Rashi {rashi}, Nakshatra {nakshatra}, "
        "Mahadasha {dasha}. ~100 words. Specific, Vedic principles."
    ),
}

_SPIRITUAL_PROMPT = {
    "en": (
        "Daily spiritual guidance for someone with Moon in {moon_sign}, nakshatra {nakshatra}, {date}. "
        "Include: planet influence today, mantra (with meaning), one spiritual practice. ~100 words."
    ),
    "hi": (
        "Daily spiritual guidance in Hindi for Moon in {moon_sign}, nakshatra {nakshatra}, {date}. "
        "Include planet influence, mantra with meaning, one spiritual practice. ~100 words."
    ),
}

# Lucky colors by day of week
_LUCKY_COLORS = ["White", "Pink", "Red", "Green", "Yellow", "Blue", "Purple"]
_LUCKY_COLORS_HI = ["सफ़ेद", "गुलाबी", "लाल", "हरा", "पीला", "नीला", "बैंगनी"]


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client


async def _call_ai(prompt: str) -> str:
    response = await _get_client().chat.completions.create(
        model=settings.openrouter_model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


async def get_reading(sign: str, rashi: str, moon_sign: str, nakshatra: str,
                      day: date, lang: str = "en") -> str:
    cache_key = f"{sign}:{lang}"
    cached = await cache.get_horoscope(cache_key, day)
    if cached:
        return cached

    lucky_num = (day.day + day.month) % 9 + 1
    lucky_color = (_LUCKY_COLORS_HI if lang == "hi" else _LUCKY_COLORS)[day.weekday()]

    prompt = _HORO_PROMPT.get(lang, _HORO_PROMPT["en"]).format(
        sign=sign, rashi=rashi, date=day.strftime("%B %d, %Y"),
        moon_sign=moon_sign, nakshatra=nakshatra,
        lucky_num=lucky_num, lucky_color=lucky_color,
    )

    logger.info("Generating horoscope: %s %s lang=%s", sign, day, lang)
    reading = await _call_ai(prompt)
    if reading:
        await cache.set_horoscope(cache_key, day, reading)
    return reading


async def get_intro(name: str, lagna: str, rashi: str, nakshatra: str,
                    nak_lord: str, dasha: str, lang: str = "en") -> str:
    prompt = _INTRO_PROMPT.get(lang, _INTRO_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        nakshatra=nakshatra, nak_lord=nak_lord, dasha=dasha,
    )
    return await _call_ai(prompt)


async def ask_ai(question: str, name: str, lagna: str, rashi: str,
                 nakshatra: str, dasha: str, lang: str = "en") -> str:
    prompt = _ASK_PROMPT.get(lang, _ASK_PROMPT["en"]).format(
        question=question, name=name, lagna=lagna,
        rashi=rashi, nakshatra=nakshatra, dasha=dasha,
    )
    return await _call_ai(prompt)


async def get_spiritual_guidance(moon_sign: str, nakshatra: str,
                                  day: date, lang: str = "en") -> str:
    cache_key = f"spiritual:{moon_sign}:{lang}"
    cached = await cache.get_horoscope(cache_key, day)
    if cached:
        return cached

    prompt = _SPIRITUAL_PROMPT.get(lang, _SPIRITUAL_PROMPT["en"]).format(
        moon_sign=moon_sign, nakshatra=nakshatra,
        date=day.strftime("%B %d, %Y"),
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, day, result)
    return result
