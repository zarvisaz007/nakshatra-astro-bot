import logging
from datetime import date

from app.services.horoscope import _call_ai
from app.services.cache import get_redis

logger = logging.getLogger(__name__)

# Dasha themes for milestone mapping
_DASHA_THEMES = {
    "Sun":     "authority, career, father, government, health",
    "Moon":    "emotions, mother, home, travel, public life",
    "Mars":    "energy, property, siblings, courage, ambition",
    "Mercury": "education, business, communication, skills",
    "Jupiter": "wisdom, children, wealth, spirituality, marriage",
    "Venus":   "relationships, luxury, art, beauty, marriage",
    "Saturn":  "karma, hard work, delays then rewards, discipline",
    "Rahu":    "ambition, foreign, sudden changes, innovation",
    "Ketu":    "spirituality, detachment, research, past karma",
}

_MARRIAGE_DASHAS = {"Venus", "Jupiter"}
_CAREER_DASHAS = {"Sun", "Saturn", "Mars", "Mercury"}
_WEALTH_DASHAS = {"Jupiter", "Venus", "Mercury"}
_SPIRITUAL_DASHAS = {"Ketu", "Jupiter", "Saturn"}

_MILESTONES_PROMPT = {
    "en": (
        "You are a Vedic astrologer. Life milestone prediction for {name}, age {age}.\n"
        "Lagna: {lagna}, Moon in {rashi}, Nakshatra: {nakshatra}.\n"
        "Dasha timeline: {timeline}\n"
        "Current dasha: {current_dasha} (running since approx age {dasha_start}).\n\n"
        "Predict:\n"
        "1. Key life phases (5-6 most important dasha periods and what they bring)\n"
        "2. Best age for: career peak, marriage, wealth, spiritual growth\n"
        "3. Current phase advice: what to focus on NOW\n"
        "4. Longevity & vitality indication (Vedic perspective, not medical)\n\n"
        "~250 words. Specific ages/periods. Warm, encouraging, Vedic grounded."
    ),
    "hi": (
        "आप वैदिक ज्योतिषी हैं। {name} की जीवन यात्रा का विश्लेषण, वर्तमान आयु {age} वर्ष।\n"
        "लग्न: {lagna}, राशि: {rashi}, नक्षत्र: {nakshatra}।\n"
        "दशा क्रम: {timeline}\n"
        "वर्तमान दशा: {current_dasha}।\n\n"
        "बताएं:\n"
        "1. जीवन के मुख्य चरण और उनका महत्व\n"
        "2. करियर शिखर, विवाह, धन और आध्यात्मिक उन्नति की उम्र\n"
        "3. अभी क्या करें — वर्तमान दशा का सर्वश्रेष्ठ उपयोग\n"
        "4. दीर्घायु संकेत (वैदिक दृष्टिकोण)\n\n"
        "~250 शब्द। विशिष्ट उम्र/काल बताएं।"
    ),
}


def get_milestones_data(birth_date: date, nakshatra: str, kundli: dict) -> dict:
    """Calculate dasha timeline as age ranges + milestone predictions."""
    from app.services.astrology import DASHA_ORDER, DASHA_YEARS, NAKSHATRAS

    today = date.today()
    current_age = (today - birth_date).days // 365

    current_dasha = kundli["current_dasha"]
    years_left = kundli["dasha_years_left"]

    # Approximate current dasha start age
    current_dasha_total_years = DASHA_YEARS[current_dasha]
    dasha_elapsed = current_dasha_total_years - years_left
    dasha_start_age = current_age - dasha_elapsed
    dasha_end_age = dasha_start_age + current_dasha_total_years

    # Build full timeline: go back from current dasha to reconstruct all 9 dashas
    # We know: current dasha started at dasha_start_age
    # Walk backwards through DASHA_ORDER to fill in prior dashas
    # Then walk forwards for future dashas
    # All 9 dashas make the full 120-year cycle; we show all of them anchored to birth

    cur_idx = DASHA_ORDER.index(current_dasha)

    # Build a list of (planet, start_age, end_age) for all dashas in the 120-year cycle
    # We anchor by working backward from current dasha start
    dasha_timeline = []

    # Walk backwards: fill prior dashas from birth
    age_cursor = dasha_start_age
    backwards = []
    idx = cur_idx
    while age_cursor > 0:
        idx = (idx - 1) % 9
        planet = DASHA_ORDER[idx]
        years = DASHA_YEARS[planet]
        end_age = age_cursor
        start_age = end_age - years
        backwards.append((planet, max(0, round(start_age, 1)), round(end_age, 1)))
        age_cursor = start_age

    backwards.reverse()
    for planet, start_a, end_a in backwards:
        dasha_timeline.append({
            "planet": planet,
            "start_age": start_a,
            "end_age": end_a,
            "years": DASHA_YEARS[planet],
            "theme": _DASHA_THEMES.get(planet, ""),
        })

    # Add current dasha
    dasha_timeline.append({
        "planet": current_dasha,
        "start_age": round(dasha_start_age, 1),
        "end_age": round(dasha_end_age, 1),
        "years": current_dasha_total_years,
        "theme": _DASHA_THEMES.get(current_dasha, ""),
    })

    # Walk forwards: fill future dashas until age 120
    idx = cur_idx
    age_cursor = dasha_end_age
    while age_cursor < 120:
        idx = (idx + 1) % 9
        planet = DASHA_ORDER[idx]
        years = DASHA_YEARS[planet]
        start_a = age_cursor
        end_a = age_cursor + years
        dasha_timeline.append({
            "planet": planet,
            "start_age": round(start_a, 1),
            "end_age": round(min(end_a, 120), 1),
            "years": years,
            "theme": _DASHA_THEMES.get(planet, ""),
        })
        age_cursor = end_a

    # Identify key milestone windows from the timeline
    marriage_window = "N/A"
    career_peak = "N/A"
    wealth_period = "N/A"
    spiritual_phase = "N/A"

    for d in dasha_timeline:
        p = d["planet"]
        s = int(d["start_age"])
        e = int(d["end_age"])
        age_range = f"{s}–{e}"

        if p in _MARRIAGE_DASHAS and marriage_window == "N/A":
            marriage_window = age_range
        if p in _CAREER_DASHAS and career_peak == "N/A":
            career_peak = age_range
        if p in _WEALTH_DASHAS and wealth_period == "N/A":
            wealth_period = age_range
        if p in _SPIRITUAL_DASHAS and spiritual_phase == "N/A":
            spiritual_phase = age_range

    return {
        "dasha_timeline": dasha_timeline,
        "current_dasha": current_dasha,
        "current_age": current_age,
        "dasha_start_age": round(dasha_start_age, 1),
        "marriage_window": marriage_window,
        "career_peak": career_peak,
        "wealth_period": wealth_period,
        "spiritual_phase": spiritual_phase,
    }


def _format_timeline_for_prompt(dasha_timeline: list[dict], current_dasha: str) -> str:
    """Format as: Ketu(0-7) → Venus(7-27) → ▶Sun(27-33) → ..."""
    parts = []
    for d in dasha_timeline:
        s = int(d["start_age"])
        e = int(d["end_age"])
        marker = "▶" if d["planet"] == current_dasha else ""
        parts.append(f"{marker}{d['planet']}({s}-{e})")
    return " → ".join(parts)


def _format_timeline_display(dasha_timeline: list[dict], current_dasha: str, lang: str) -> str:
    """Format for message display: Ketu: 0–7 | ▶ Sun: 27–33 | ..."""
    parts = []
    for d in dasha_timeline:
        s = int(d["start_age"])
        e = int(d["end_age"])
        if d["planet"] == current_dasha:
            parts.append(f"▶ *{d['planet']}*: {s}–{e}")
        else:
            parts.append(f"{d['planet']}: {s}–{e}")
    return " | ".join(parts)


async def get_milestones_reading(
    u,
    kundli: dict,
    lang: str = "en",
) -> str:
    """Generate AI milestones reading with Redis caching."""
    cache_key = f"milestones:{u.telegram_id}:{lang}"
    r = get_redis()

    cached = await r.get(cache_key)
    if cached:
        return cached

    birth_date = u.birth_date
    name = u.name or "You"
    nakshatra = kundli.get("nakshatra", "")
    lagna = kundli.get("lagna", "")
    rashi = kundli.get("rashi", "")

    milestones = get_milestones_data(birth_date, nakshatra, kundli)

    timeline_str = _format_timeline_for_prompt(
        milestones["dasha_timeline"], milestones["current_dasha"]
    )

    prompt = _MILESTONES_PROMPT.get(lang, _MILESTONES_PROMPT["en"]).format(
        name=name,
        age=milestones["current_age"],
        lagna=lagna,
        rashi=rashi,
        nakshatra=nakshatra,
        timeline=timeline_str,
        current_dasha=milestones["current_dasha"],
        dasha_start=int(milestones["dasha_start_age"]),
    )

    logger.info(
        "Generating milestones reading: telegram_id=%s lang=%s",
        u.telegram_id, lang,
    )
    reading = await _call_ai(prompt)

    if reading:
        await r.setex(cache_key, 604800, reading)

    return reading
