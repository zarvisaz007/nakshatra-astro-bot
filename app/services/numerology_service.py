import logging
from datetime import date

from app.services import cache
from app.services.horoscope import _call_ai

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chaldean letter → value mapping
# ---------------------------------------------------------------------------
_CHALDEAN: dict[str, int] = {}
for _letter in "AIJQY":
    _CHALDEAN[_letter] = 1
for _letter in "BKR":
    _CHALDEAN[_letter] = 2
for _letter in "CGLS":
    _CHALDEAN[_letter] = 3
for _letter in "DMT":
    _CHALDEAN[_letter] = 4
for _letter in "EHNX":
    _CHALDEAN[_letter] = 5
for _letter in "UVW":
    _CHALDEAN[_letter] = 6
for _letter in "OZ":
    _CHALDEAN[_letter] = 7
for _letter in "FP":
    _CHALDEAN[_letter] = 8

_VOWELS = set("AEIOU")

# ---------------------------------------------------------------------------
# Vedic planet & meaning for each number
# ---------------------------------------------------------------------------
_PLANET: dict[int, str] = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu",
    5: "Mercury",
    6: "Venus",
    7: "Ketu",
    8: "Saturn",
    9: "Mars",
    11: "Master (Moon/Sun)",
    22: "Master (Uranus/Saturn)",
    33: "Master (Jupiter/Neptune)",
}

_MEANING_EN: dict[int, str] = {
    1: "Leadership, independence, pioneering spirit. Sun blesses you with authority and self-reliance.",
    2: "Sensitivity, intuition, cooperation. Moon gifts you with empathy and emotional depth.",
    3: "Creativity, communication, optimism. Jupiter expands your self-expression and joy.",
    4: "Hard work, stability, discipline. Rahu drives you toward material mastery through effort.",
    5: "Adaptability, travel, freedom. Mercury makes you versatile, curious, and quick-witted.",
    6: "Love, beauty, harmony. Venus blesses relationships, arts, and domestic happiness.",
    7: "Spirituality, mysticism, introspection. Ketu pulls you inward toward inner wisdom.",
    8: "Karma, discipline, wealth. Saturn tests you, then rewards with enduring success.",
    9: "Courage, humanitarianism, completion. Mars fuels your drive to serve and inspire.",
    11: "Spiritual messenger, illumination, higher intuition. A master number of divine inspiration.",
    22: "Master builder, visionary leadership, large-scale achievement. Rare and powerful.",
    33: "Master teacher, selfless service, compassion. The highest expression of nurturing.",
}

_MEANING_HI: dict[int, str] = {
    1: "नेतृत्व, स्वतंत्रता, अग्रणी भावना। सूर्य आपको अधिकार और आत्मनिर्भरता प्रदान करता है।",
    2: "संवेदनशीलता, अंतर्ज्ञान, सहयोग। चंद्रमा आपको गहरी भावनात्मक बुद्धि देता है।",
    3: "रचनात्मकता, संवाद, आशावाद। बृहस्पति आपकी अभिव्यक्ति और आनंद को विस्तार देता है।",
    4: "परिश्रम, स्थिरता, अनुशासन। राहु आपको भौतिक कुशलता की ओर प्रेरित करता है।",
    5: "अनुकूलनशीलता, यात्रा, स्वतंत्रता। बुध आपको बहुमुखी और जिज्ञासु बनाता है।",
    6: "प्रेम, सौंदर्य, सद्भाव। शुक्र रिश्तों और कलाओं में सुख प्रदान करता है।",
    7: "आध्यात्मिकता, रहस्यवाद, आत्म-चिंतन। केतु आपको आंतरिक ज्ञान की ओर ले जाता है।",
    8: "कर्म, अनुशासन, धन। शनि परीक्षा लेकर स्थायी सफलता प्रदान करता है।",
    9: "साहस, मानवता-प्रेम, परिपूर्णता। मंगल आपको सेवा और प्रेरणा का बल देता है।",
    11: "आध्यात्मिक संदेशवाहक, प्रकाश, उच्च अंतर्ज्ञान। दिव्य प्रेरणा का मास्टर नंबर।",
    22: "मास्टर निर्माता, दूरदर्शी नेतृत्व, बड़े पैमाने पर उपलब्धि। दुर्लभ और शक्तिशाली।",
    33: "मास्टर शिक्षक, निःस्वार्थ सेवा, करुणा। पोषण की सर्वोच्च अभिव्यक्ति।",
}

# ---------------------------------------------------------------------------
# Reduction helpers
# ---------------------------------------------------------------------------

def _reduce(n: int) -> int:
    """Reduce a number to single digit, preserving master numbers 11, 22, 33."""
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))


# ---------------------------------------------------------------------------
# Core numerology calculations
# ---------------------------------------------------------------------------

def calc_life_path(dob: date) -> int:
    """Sum all digits of the birth date, reduce to single digit or master number."""
    total = _digit_sum(dob.day) + _digit_sum(dob.month) + _digit_sum(dob.year)
    return _reduce(total)


def calc_name_number(name: str) -> int:
    """Chaldean destiny number — all letters in name."""
    total = sum(_CHALDEAN.get(c, 0) for c in name.upper() if c.isalpha())
    return _reduce(total)


def calc_soul_urge(name: str) -> int:
    """Chaldean soul urge — vowels only."""
    total = sum(_CHALDEAN.get(c, 0) for c in name.upper() if c in _VOWELS)
    return _reduce(total) if total else 0


def calc_day_number(dob: date) -> int:
    return _reduce(dob.day)


def calc_personal_year(dob: date, year: int) -> int:
    total = _digit_sum(dob.day) + _digit_sum(dob.month) + _digit_sum(year)
    return _reduce(total)


def get_numerology_profile(name: str, dob: date, current_year: int) -> dict:
    life_path = calc_life_path(dob)
    destiny = calc_name_number(name)
    soul_urge = calc_soul_urge(name)
    day_num = calc_day_number(dob)
    year_num = calc_personal_year(dob, current_year)

    return {
        "life_path": life_path,
        "destiny": destiny,
        "soul_urge": soul_urge,
        "day_num": day_num,
        "year_num": year_num,
        "planet": _PLANET.get(life_path, ""),
    }


# ---------------------------------------------------------------------------
# AI reading
# ---------------------------------------------------------------------------

_NUMEROLOGY_PROMPT = {
    "en": (
        "Vedic numerology reading for {name}. "
        "Life Path {life_path} ({planet}), Destiny {destiny}, Soul Urge {soul_urge}. "
        "Born {dob}. ~150 words. "
        "Cover: life purpose, personality traits, karmic lessons, lucky periods. "
        "Vedic planetary perspective. Warm, specific, no disclaimers."
    ),
    "hi": (
        "Vedic numerology reading for {name}. "
        "Life Path {life_path} ({planet}), Destiny {destiny}, Soul Urge {soul_urge}. "
        "Born {dob}. ~150 words. "
        "Cover: life purpose, personality traits, karmic lessons, lucky periods. "
        "Vedic planetary perspective. Warm, specific, no disclaimers. "
        "Write the entire response in Hindi."
    ),
}


async def get_numerology_reading(
    name: str,
    dob: date,
    profile: dict,
    lang: str = "en",
) -> str:
    today = date.today()
    cache_key = f"numerology:{name.lower()}:{dob.isoformat()}:{lang}"

    cached = await cache.get_horoscope(cache_key, today)
    if cached:
        return cached

    prompt = _NUMEROLOGY_PROMPT.get(lang, _NUMEROLOGY_PROMPT["en"]).format(
        name=name,
        life_path=profile["life_path"],
        planet=profile["planet"],
        destiny=profile["destiny"],
        soul_urge=profile["soul_urge"],
        dob=dob.strftime("%B %d, %Y"),
    )

    logger.info("Generating numerology reading for %s lang=%s", name, lang)
    reading = await _call_ai(prompt)
    if reading:
        await cache.set_horoscope(cache_key, today, reading)
    return reading


def format_reading_en(name: str, dob: date, profile: dict, ai_reading: str) -> str:
    lp = profile["life_path"]
    dest = profile["destiny"]
    soul = profile["soul_urge"]
    day_n = profile["day_num"]
    yr_n = profile["year_num"]
    planet = profile["planet"]

    lp_meaning = _MEANING_EN.get(lp, "")
    dest_meaning = _MEANING_EN.get(dest, "")
    soul_meaning = _MEANING_EN.get(soul, "")

    return (
        f"🔢 *Numerology Reading — {name}*\n\n"
        f"📅 *Date of Birth:* {dob.strftime('%d %B %Y')}\n"
        f"✍️ *Name:* {name}\n\n"
        f"🌟 *Life Path Number: {lp}* ({planet})\n"
        f"{lp_meaning}\n\n"
        f"🎯 *Destiny Number: {dest}*\n"
        f"{dest_meaning}\n\n"
        f"💫 *Soul Urge Number: {soul}*\n"
        f"{soul_meaning}\n\n"
        f"📅 *Day Number: {day_n}*\n"
        f"🗓️ *Personal Year: {yr_n}*\n\n"
        f"---\n"
        f"{ai_reading}\n\n"
        f"_Numerology reveals your soul's blueprint._"
    )


def format_reading_hi(name: str, dob: date, profile: dict, ai_reading: str) -> str:
    lp = profile["life_path"]
    dest = profile["destiny"]
    soul = profile["soul_urge"]
    day_n = profile["day_num"]
    yr_n = profile["year_num"]
    planet = profile["planet"]

    lp_meaning = _MEANING_HI.get(lp, "")
    dest_meaning = _MEANING_HI.get(dest, "")
    soul_meaning = _MEANING_HI.get(soul, "")

    return (
        f"🔢 *अंकज्योतिष पठन — {name}*\n\n"
        f"📅 *जन्म तिथि:* {dob.strftime('%d %B %Y')}\n"
        f"✍️ *नाम:* {name}\n\n"
        f"🌟 *जीवन पथ अंक: {lp}* ({planet})\n"
        f"{lp_meaning}\n\n"
        f"🎯 *भाग्य अंक: {dest}*\n"
        f"{dest_meaning}\n\n"
        f"💫 *आत्मा की इच्छा अंक: {soul}*\n"
        f"{soul_meaning}\n\n"
        f"📅 *दिन अंक: {day_n}*\n"
        f"🗓️ *व्यक्तिगत वर्ष: {yr_n}*\n\n"
        f"---\n"
        f"{ai_reading}\n\n"
        f"_अंकज्योतिष आपकी आत्मा का नक्शा प्रकट करता है।_"
    )
