import logging
from datetime import date

from app.services.horoscope import _call_ai
from app.services import cache

logger = logging.getLogger(__name__)

_FIRE_SIGNS = {"Aries", "Leo", "Sagittarius"}
_EARTH_SIGNS = {"Taurus", "Virgo", "Capricorn"}
_AIR_SIGNS = {"Gemini", "Libra", "Aquarius"}
_WATER_SIGNS = {"Cancer", "Scorpio", "Pisces"}

_PLANET_MANTRA = {
    "Sun":     {"mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "deity": "Lord Surya",    "count": 108, "best_time": "Sunrise (5–7 AM)",    "benefit": "Health, vitality, authority, father's blessings"},
    "Moon":    {"mantra": "ॐ श्रां श्रीं श्रौं सः चंद्रमसे नमः", "deity": "Lord Chandra",  "count": 108, "best_time": "Monday evening",        "benefit": "Emotional peace, mother's blessings, intuition"},
    "Mars":    {"mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः",   "deity": "Lord Mangal",   "count": 108, "best_time": "Tuesday dawn",           "benefit": "Courage, energy, property, protection"},
    "Mercury": {"mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः",   "deity": "Lord Budha",    "count": 108, "best_time": "Wednesday morning",      "benefit": "Intelligence, business, communication, education"},
    "Jupiter": {"mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः",   "deity": "Lord Brihaspati","count": 108, "best_time": "Thursday morning",       "benefit": "Wisdom, children, wealth, spiritual growth"},
    "Venus":   {"mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", "deity": "Goddess Shukra", "count": 108, "best_time": "Friday evening",         "benefit": "Love, beauty, luxury, artistic talents"},
    "Saturn":  {"mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः","deity": "Lord Shani",     "count": 108, "best_time": "Saturday dawn",          "benefit": "Discipline, karmic relief, longevity, service"},
    "Rahu":    {"mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः",   "deity": "Rahu",           "count": 108, "best_time": "Saturday night",         "benefit": "Ambition, foreign gains, illusion removal"},
    "Ketu":    {"mantra": "ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः","deity": "Ketu",          "count": 108, "best_time": "Tuesday night",          "benefit": "Spiritual liberation, past karma resolution, moksha"},
}

_SADHANA_TIPS = {
    "fire":  ["Practice at sunrise facing East", "Use Rudraksha mala", "Offer water to the sun after practice"],
    "earth": ["Practice at dusk facing North", "Use Sphatik (crystal) mala", "Light a ghee lamp during practice"],
    "air":   ["Practice at dawn facing East", "Use Tulsi mala", "Sit near a window with fresh air"],
    "water": ["Practice at night facing West", "Use Pearl or white mala", "Place a glass of water nearby, offer it to a plant after"],
}
_SADHANA_TIPS_HI = {
    "fire":  ["सूर्योदय पर पूर्व दिशा की ओर मुख करके अभ्यास करें", "रुद्राक्ष माला उपयोग करें", "अभ्यास के बाद सूर्य को जल चढ़ाएं"],
    "earth": ["संध्या को उत्तर दिशा में अभ्यास करें", "स्फटिक माला उपयोग करें", "अभ्यास के दौरान घी का दीपक जलाएं"],
    "air":   ["भोर में पूर्व दिशा में अभ्यास करें", "तुलसी माला उपयोग करें", "खिड़की के पास ताज़ी हवा में बैठें"],
    "water": ["रात को पश्चिम दिशा में अभ्यास करें", "मोती या सफ़ेद माला उपयोग करें", "पास में जल रखें, अभ्यास के बाद पौधे को दें"],
}

_MANTRA_PROMPT = {
    "en": (
        "You are a Vedic astrologer and mantra teacher. Personalized mantra sadhana for {name}. "
        "Lagna {lagna}, Moon sign {rashi}, Nakshatra {nakshatra} (lord {nak_lord}), Mahadasha {dasha}. "
        "Daily mantra: {mantra}. "
        "~150 words. Explain the spiritual significance of this mantra for their chart, best practice time, "
        "how to sit, how to use mala beads, and what transformation to expect. Warm, devotional, practical."
    ),
    "hi": (
        "आप एक वैदिक ज्योतिषी और मंत्र गुरु हैं। {name} के लिए व्यक्तिगत मंत्र साधना। "
        "लग्न {lagna}, राशि {rashi}, नक्षत्र {nakshatra} (स्वामी {nak_lord}), महादशा {dasha}। "
        "दैनिक मंत्र: {mantra}। "
        "~150 शब्द। मंत्र का महत्व, अभ्यास समय, आसन, माला का उपयोग और परिवर्तन बताएं।"
    ),
}


def _lagna_element(lagna: str) -> str:
    if lagna in _FIRE_SIGNS:
        return "fire"
    if lagna in _EARTH_SIGNS:
        return "earth"
    if lagna in _AIR_SIGNS:
        return "air"
    return "water"


def mantra_sadhana(kundli: dict) -> dict:
    nak_lord = kundli["nakshatra_lord"]
    dasha_lord = kundli["current_dasha"]
    lagna = kundli["lagna"]

    daily_mantra = _PLANET_MANTRA.get(nak_lord, _PLANET_MANTRA["Jupiter"])
    dasha_mantra = _PLANET_MANTRA.get(dasha_lord, _PLANET_MANTRA["Jupiter"])

    element = _lagna_element(lagna)

    return {
        "daily_mantra": daily_mantra,
        "dasha_mantra": dasha_mantra,
        "same_lord": nak_lord == dasha_lord,
        "nakshatra_lord": nak_lord,
        "current_dasha": dasha_lord,
        "nakshatra": kundli["nakshatra"],
        "sadhana_tips": _SADHANA_TIPS[element],
        "sadhana_tips_hi": _SADHANA_TIPS_HI[element],
        "lagna": lagna,
    }


async def get_mantra_reading(name: str, lagna: str, rashi: str,
                              mantra_data: dict, lang: str = "en") -> str:
    cache_key = f"mantra:{rashi}:{mantra_data['nakshatra_lord']}:{lang}"
    today = date.today()
    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached

    prompt = _MANTRA_PROMPT.get(lang, _MANTRA_PROMPT["en"]).format(
        name=name, lagna=lagna, rashi=rashi,
        nakshatra=mantra_data["nakshatra"],
        nak_lord=mantra_data["nakshatra_lord"],
        dasha=mantra_data["current_dasha"],
        mantra=mantra_data["daily_mantra"]["mantra"],
    )
    result = await _call_ai(prompt)
    if result:
        await cache.set_horoscope(cache_key, today, result)
    return result
