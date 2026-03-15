import logging
from datetime import date

from app.services.horoscope import _call_ai
from app.services import cache

logger = logging.getLogger(__name__)

_SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

_DASHA_PUJA = {
    "Sun":     {"name": "Surya Puja", "deity": "Lord Surya", "day": "Sunday", "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "benefit": "Health, authority, father's blessings"},
    "Moon":    {"name": "Shiva Abhishek", "deity": "Lord Shiva", "day": "Monday", "mantra": "ॐ नमः शिवाय", "benefit": "Peace, mother's blessings, emotional stability"},
    "Mars":    {"name": "Hanuman Puja", "deity": "Lord Hanuman", "day": "Tuesday", "mantra": "ॐ हं हनुमते नमः", "benefit": "Courage, protection, removal of Manglik effects"},
    "Mercury": {"name": "Vishnu Puja", "deity": "Lord Vishnu", "day": "Wednesday", "mantra": "ॐ नमो नारायणाय", "benefit": "Intelligence, business success, communication"},
    "Jupiter": {"name": "Brihaspati Puja", "deity": "Lord Vishnu/Brihaspati", "day": "Thursday", "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", "benefit": "Wisdom, children, financial growth"},
    "Venus":   {"name": "Lakshmi Puja", "deity": "Goddess Lakshmi", "day": "Friday", "mantra": "ॐ श्रीं ह्रीं श्रीं कमले कमलालये प्रसीद प्रसीद", "benefit": "Wealth, beauty, relationships, luxury"},
    "Saturn":  {"name": "Shani Puja", "deity": "Lord Shani", "day": "Saturday", "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", "benefit": "Removal of obstacles, karmic relief, discipline"},
    "Rahu":    {"name": "Durga Puja", "deity": "Goddess Durga", "day": "Saturday", "mantra": "ॐ दुं दुर्गायै नमः", "benefit": "Protection from evil, sudden gains, foreign connections"},
    "Ketu":    {"name": "Ganesha Puja", "deity": "Lord Ganesha", "day": "Tuesday/Wednesday", "mantra": "ॐ गं गणपतये नमः", "benefit": "Obstacle removal, spiritual growth, new beginnings"},
}

_NAVAGRAHA_PUJA = {
    "name": "Navagraha Puja", "deity": "Nine Planets", "day": "Sunday",
    "mantra": "ॐ नवग्रहाय नमः", "benefit": "Balances all planetary energies",
}
_MANGAL_PUJA = {
    "name": "Mangal Chandika Puja", "deity": "Goddess Chandika", "day": "Tuesday",
    "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः", "benefit": "Reduces Manglik dosha, harmonizes marriage",
}
_SHANI_SHANTI_PUJA = {
    "name": "Shani Shanti Puja", "deity": "Lord Shani", "day": "Saturday",
    "mantra": "ॐ शं शनैश्चराय नमः", "benefit": "Removes Saturn affliction, brings discipline and success",
}
_KAAL_SARP_PUJA = {
    "name": "Kaal Sarp Dosh Puja", "deity": "Lord Shiva/Nag Devta", "day": "Monday/Panchami",
    "mantra": "ॐ नमः शिवाय", "benefit": "Removes Kaal Sarp obstacles, opens blocked destiny",
}

_PUJA_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Puja recommendations for {name}. "
        "Lagna {lagna}, Moon sign {rashi}, current Mahadasha {dasha}. "
        "Primary deity: {deity}. "
        "~150 words. Explain WHY this puja is beneficial now, best timing (day/tithi), "
        "and what blessings to expect. Warm, devotional tone. Specific Vedic reasoning."
    ),
    "hi": (
        "आप एक वैदिक ज्योतिषी हैं। {name} के लिए पूजा अनुशंसा। "
        "लग्न {lagna}, राशि {rashi}, महादशा {dasha}। "
        "प्रमुख देवता: {deity}। "
        "~150 शब्द। पूजा का कारण, उचित समय, और आशीर्वाद बताएं। भक्तिपूर्ण भाव में।"
    ),
}


def puja_recommendation(kundli: dict) -> dict:
    planets = kundli["planets"]
    houses = kundli["houses"]
    current_dasha = kundli["current_dasha"]

    primary_puja = _DASHA_PUJA.get(current_dasha, _DASHA_PUJA["Jupiter"])
    special_pujas = [_NAVAGRAHA_PUJA]

    # Mars in 1,4,7,8,12 → Manglik
    mars_sign = planets["Mars"][0]
    mars_house = houses.index(mars_sign) + 1 if mars_sign in houses else 0
    if mars_house in (1, 4, 7, 8, 12):
        special_pujas.append(_MANGAL_PUJA)

    # Saturn in kendra → Shani Shanti
    saturn_sign = planets["Saturn"][0]
    saturn_house = houses.index(saturn_sign) + 1 if saturn_sign in houses else 0
    if saturn_house in (1, 4, 7, 10):
        special_pujas.append(_SHANI_SHANTI_PUJA)

    # Kaal Sarp: all planets between Rahu and Ketu (simplified)
    rahu_sign = planets["Rahu"][0]
    rahu_house = houses.index(rahu_sign) + 1 if rahu_sign in houses else 0
    planet_houses = [
        houses.index(planets[p][0]) + 1 if planets[p][0] in houses else 0
        for p in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    ]
    if rahu_house > 0 and all(h <= rahu_house or h == 0 for h in planet_houses):
        special_pujas.append(_KAAL_SARP_PUJA)

    return {
        "primary_puja": primary_puja,
        "special_pujas": special_pujas,
        "current_dasha": current_dasha,
        "lagna": kundli["lagna"],
    }


async def get_puja_reading(name: str, lagna: str, rashi: str,
                            puja: dict, lang: str = "en") -> str:
    cache_key = f"puja:{lagna}:{puja['current_dasha']}:{lang}"
    today = date.today()
    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached

    deity = puja["primary_puja"]["deity"]
    prompt = _PUJA_PROMPT.get(lang, _PUJA_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        dasha=puja["current_dasha"], deity=deity,
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, today, result)
    return result
