import logging
from datetime import date

from app.services.horoscope import _call_ai
from app.services import cache

logger = logging.getLogger(__name__)

_GEMS = {
    "Sun":     {"name": "Ruby (Manik)", "planet": "Sun", "finger": "Ring finger", "metal": "Gold", "weight": "3-5 carats", "benefit": "Authority, health, father, government favor", "caution": "Avoid if Saturn is your lagna lord"},
    "Moon":    {"name": "Pearl (Moti)", "planet": "Moon", "finger": "Little finger", "metal": "Silver", "weight": "5-7 carats", "benefit": "Peace, mother, emotions, intuition", "caution": "Natural pearl only, not cultured"},
    "Mars":    {"name": "Red Coral (Moonga)", "planet": "Mars", "finger": "Ring finger", "metal": "Gold/Copper", "weight": "6-9 carats", "benefit": "Courage, property, siblings, Manglik remedy", "caution": "Not for Gemini/Virgo lagna"},
    "Mercury": {"name": "Emerald (Panna)", "planet": "Mercury", "finger": "Little finger", "metal": "Gold", "weight": "3-5 carats", "benefit": "Intelligence, business, communication, education", "caution": "Avoid with Pearl"},
    "Jupiter": {"name": "Yellow Sapphire (Pukhraj)", "planet": "Jupiter", "finger": "Index finger", "metal": "Gold", "weight": "3-5 carats", "benefit": "Wisdom, wealth, children, spiritual growth", "caution": "Most auspicious gem, generally safe"},
    "Venus":   {"name": "Diamond (Heera) / White Sapphire", "planet": "Venus", "finger": "Middle finger", "metal": "Silver/White Gold", "weight": "0.5-1 carat (diamond)", "benefit": "Love, luxury, arts, beauty, relationships", "caution": "Avoid with Ruby and Red Coral"},
    "Saturn":  {"name": "Blue Sapphire (Neelam)", "planet": "Saturn", "finger": "Middle finger", "metal": "Silver/Panchdhatu", "weight": "3-5 carats", "benefit": "Discipline, career, longevity, removes obstacles", "caution": "Most powerful — test for 3 days before wearing"},
    "Rahu":    {"name": "Hessonite (Gomed)", "planet": "Rahu", "finger": "Middle finger", "metal": "Silver/Panchdhatu", "weight": "6-10 carats", "benefit": "Ambition, foreign gains, protection from evil", "caution": "Consult astrologer; can amplify both good and bad"},
    "Ketu":    {"name": "Cat's Eye (Lahsuniya)", "planet": "Ketu", "finger": "Middle finger", "metal": "Silver/Panchdhatu", "weight": "3-6 carats", "benefit": "Spiritual growth, intuition, past karma resolution", "caution": "Very powerful — must consult astrologer first"},
}

_LAGNA_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

_ENEMIES = {
    "Sun":     ["Saturn", "Venus"],
    "Moon":    ["Rahu", "Ketu"],
    "Mars":    ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus":   ["Sun", "Moon"],
    "Saturn":  ["Sun", "Moon", "Mars"],
    "Rahu":    ["Sun", "Moon", "Mars"],
    "Ketu":    ["Sun", "Moon", "Mars"],
}


def gem_recommendation(kundli: dict) -> dict:
    lagna = kundli.get("lagna", "")
    nakshatra_lord = kundli.get("nakshatra_lord", "")
    current_dasha = kundli.get("current_dasha", "")

    lagna_lord = _LAGNA_LORD.get(lagna, "Jupiter")

    # Primary gem — lagna lord's gemstone
    primary_gem = _GEMS.get(lagna_lord, _GEMS["Jupiter"]).copy()

    # Supporting gems — nakshatra lord + dasha lord, if different from lagna lord
    seen = {lagna_lord}
    supporting_gems = []
    for planet in [nakshatra_lord, current_dasha]:
        if planet and planet not in seen and planet in _GEMS:
            supporting_gems.append(_GEMS[planet].copy())
            seen.add(planet)
        if len(supporting_gems) >= 2:
            break

    # Gems to avoid — enemy planets of the lagna lord
    enemy_planets = _ENEMIES.get(lagna_lord, [])
    gems_to_avoid = []
    for ep in enemy_planets:
        gem = _GEMS.get(ep)
        if gem:
            gems_to_avoid.append(gem["name"])

    return {
        "primary_gem": primary_gem,
        "supporting_gems": supporting_gems,
        "gems_to_avoid": gems_to_avoid,
        "current_dasha": current_dasha,
        "nakshatra_lord": nakshatra_lord,
        "lagna": lagna,
    }


_GEMS_PROMPT = {
    "en": (
        "You are a Vedic gemologist and astrologer. Gemstone recommendations for {name}. "
        "Lagna {lagna} (lord: {lagna_lord}), Moon sign {rashi}, Nakshatra lord {nak_lord}, Mahadasha {dasha}. "
        "Primary gem: {gem}. "
        "~150 words. Explain the astrological reason for this gem, how to wear it (day, finger, metal, weight), "
        "purification ritual before wearing, and what changes to expect. Warm, specific, Vedic."
    ),
    "hi": (
        "आप एक वैदिक रत्नशास्त्री और ज्योतिषी हैं। {name} के लिए रत्न अनुशंसा। "
        "लग्न {lagna} (स्वामी: {lagna_lord}), राशि {rashi}, नक्षत्र स्वामी {nak_lord}, महादशा {dasha}। "
        "प्रमुख रत्न: {gem}। "
        "~150 शब्द। रत्न का ज्योतिषीय कारण, धारण विधि, शुद्धिकरण और अपेक्षित परिवर्तन बताएं।"
    ),
}


async def get_gems_reading(name: str, lagna: str, rashi: str, gems: dict, lang: str = "en") -> str:
    nak_lord = gems.get("nakshatra_lord", "")
    key = f"gems:{lagna}:{nak_lord}:{lang}"

    cached = await cache.get_horoscope(key, date.today())
    if cached:
        return cached

    lagna_lord = _LAGNA_LORD.get(lagna, "Jupiter")
    primary_gem = gems.get("primary_gem", {})
    dasha = gems.get("current_dasha", "")

    prompt = _GEMS_PROMPT.get(lang, _GEMS_PROMPT["en"]).format(
        name=name,
        lagna=lagna,
        lagna_lord=lagna_lord,
        rashi=rashi,
        nak_lord=nak_lord,
        dasha=dasha,
        gem=primary_gem.get("name", ""),
    )

    logger.info("Generating gems reading: lagna=%s nak_lord=%s lang=%s", lagna, nak_lord, lang)
    reading = await _call_ai(prompt)
    if reading:
        await cache.set_horoscope(key, date.today(), reading)
    return reading
