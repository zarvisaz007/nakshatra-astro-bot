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

_CAREER_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Career analysis for {name}. "
        "Lagna {lagna}, Moon sign {rashi}, 10th house {tenth_sign} (lord: {tenth_lord} in {tenth_lord_sign}), "
        "current Mahadasha {dasha} ({years_left} years left). "
        "Career domains suited: {domains}. "
        "~150 words. Cover: career strengths, best fields, current dasha influence, growth period. "
        "Vedic, specific, practical. No generic advice."
    ),
    "hi": (
        "आप एक वैदिक ज्योतिषी हैं। {name} का करियर विश्लेषण करें। "
        "लग्न {lagna}, राशि {rashi}, दसवां भाव {tenth_sign} (स्वामी: {tenth_lord} {tenth_lord_sign} में), "
        "महादशा {dasha} ({years_left} वर्ष शेष)। "
        "~150 शब्द। करियर शक्तियां, उचित क्षेत्र, दशा प्रभाव और उन्नति काल बताएं।"
    ),
}

_MARRIAGE_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Marriage analysis for {name}. "
        "Lagna {lagna}, Moon sign {rashi}, 7th house {seventh_sign} (lord: {seventh_lord} in house {seventh_lord_house}), "
        "Venus in house {venus_house}, Jupiter in house {jupiter_house}. "
        "Manglik: {manglik}. Current Mahadasha: {dasha} ({years_left} yrs left). "
        "~150 words. Cover: partner qualities, timing for marriage, relationship strengths/challenges. "
        "Vedic, warm, specific."
    ),
    "hi": (
        "आप एक वैदिक ज्योतिषी हैं। {name} का विवाह विश्लेषण करें। "
        "लग्न {lagna}, राशि {rashi}, सप्तम भाव {seventh_sign} (स्वामी: {seventh_lord} भाव {seventh_lord_house} में), "
        "शुक्र भाव {venus_house}, बृहस्पति भाव {jupiter_house}। "
        "मांगलिक: {manglik}। महादशा: {dasha} ({years_left} वर्ष शेष)। "
        "~150 शब्द। जीवनसाथी के गुण, विवाह समय, रिश्ते की शक्तियां/चुनौतियां बताएं।"
    ),
}

_WEALTH_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Wealth analysis for {name}. "
        "Lagna {lagna}, Moon sign {rashi}, 2nd house {second_sign} (lord: {second_lord}), "
        "11th house {eleventh_sign} (lord: {eleventh_lord}), "
        "Jupiter in house {jupiter_house}. Current Mahadasha: {dasha} ({years_left} yrs left). "
        "~150 words. Cover: wealth potential, income sources, financial challenges, best prosperity period. "
        "Vedic, specific, actionable."
    ),
    "hi": (
        "आप एक वैदिक ज्योतिषी हैं। {name} का धन विश्लेषण करें। "
        "लग्न {lagna}, राशि {rashi}, द्वितीय भाव {second_sign} (स्वामी: {second_lord}), "
        "एकादश भाव {eleventh_sign} (स्वामी: {eleventh_lord}), "
        "बृहस्पति भाव {jupiter_house} में। महादशा: {dasha} ({years_left} वर्ष शेष)। "
        "~150 शब्द। धन क्षमता, आय स्रोत, वित्तीय चुनौतियां और समृद्धि काल बताएं।"
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


async def get_career_reading(name: str, lagna: str, rashi: str,
                             career: dict, lang: str = "en") -> str:
    cache_key = f"career:{lagna}:{career['current_dasha']}:{lang}"
    today = date.today()
    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached
    prompt = _CAREER_PROMPT.get(lang, _CAREER_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        tenth_sign=career["tenth_sign"], tenth_lord=career["tenth_lord"],
        tenth_lord_sign=career["tenth_lord_sign"],
        dasha=career["current_dasha"], years_left=round(career["dasha_years_left"], 1),
        domains=career["career_domains"],
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, today, result)
    return result


async def get_marriage_reading(name: str, lagna: str, rashi: str,
                                marriage: dict, lang: str = "en") -> str:
    cache_key = f"marriage:{lagna}:{marriage['current_dasha']}:{lang}"
    today = date.today()
    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached
    manglik_str = ("Yes" if marriage["is_manglik"] else "No") if lang == "en" else ("हां" if marriage["is_manglik"] else "नहीं")
    prompt = _MARRIAGE_PROMPT.get(lang, _MARRIAGE_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        seventh_sign=marriage["seventh_sign"], seventh_lord=marriage["seventh_lord"],
        seventh_lord_house=marriage["seventh_lord_house"],
        venus_house=marriage["venus_house"], jupiter_house=marriage["jupiter_house"],
        manglik=manglik_str,
        dasha=marriage["current_dasha"], years_left=round(marriage["dasha_years_left"], 1),
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, today, result)
    return result


async def get_wealth_reading(name: str, lagna: str, rashi: str,
                              wealth: dict, lang: str = "en") -> str:
    cache_key = f"wealth:{lagna}:{wealth['current_dasha']}:{lang}"
    today = date.today()
    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached
    prompt = _WEALTH_PROMPT.get(lang, _WEALTH_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        second_sign=wealth["second_sign"], second_lord=wealth["second_lord"],
        eleventh_sign=wealth["eleventh_sign"], eleventh_lord=wealth["eleventh_lord"],
        jupiter_house=wealth["jupiter_house"],
        dasha=wealth["current_dasha"], years_left=round(wealth["dasha_years_left"], 1),
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, today, result)
    return result


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
