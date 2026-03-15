from datetime import date, time, datetime, timezone
from math import floor

from kerykeion import AstrologicalSubject

# kerykeion returns 3-letter abbreviations
_SHORT = {
    "Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Can": "Cancer",
    "Leo": "Leo",   "Vir": "Virgo",  "Lib": "Libra",  "Sco": "Scorpio",
    "Sag": "Sagittarius", "Cap": "Capricorn", "Aqu": "Aquarius", "Pis": "Pisces",
}

SIGN_NAMES = list(_SHORT.values())

SIGN_SYMBOLS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌",   "Virgo": "♍", "Libra": "♎",  "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

# Hindi rashi names
RASHI_HINDI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुम्भ", "Pisces": "मीन",
}

# 27 Nakshatras with their lords
NAKSHATRAS = [
    ("Ashwini", "Ketu", 0),       ("Bharani", "Venus", 13.333),
    ("Krittika", "Sun", 26.666),  ("Rohini", "Moon", 40.0),
    ("Mrigashira", "Mars", 53.333), ("Ardra", "Rahu", 66.666),
    ("Punarvasu", "Jupiter", 80.0), ("Pushya", "Saturn", 93.333),
    ("Ashlesha", "Mercury", 106.666), ("Magha", "Ketu", 120.0),
    ("Purva Phalguni", "Venus", 133.333), ("Uttara Phalguni", "Sun", 146.666),
    ("Hasta", "Moon", 160.0), ("Chitra", "Mars", 173.333),
    ("Swati", "Rahu", 186.666), ("Vishakha", "Jupiter", 200.0),
    ("Anuradha", "Saturn", 213.333), ("Jyeshtha", "Mercury", 226.666),
    ("Moola", "Ketu", 240.0), ("Purva Ashadha", "Venus", 253.333),
    ("Uttara Ashadha", "Sun", 266.666), ("Shravana", "Moon", 280.0),
    ("Dhanishtha", "Mars", 293.333), ("Shatabhisha", "Rahu", 306.666),
    ("Purva Bhadrapada", "Jupiter", 320.0), ("Uttara Bhadrapada", "Saturn", 333.333),
    ("Revati", "Mercury", 346.666),
]

# Vimshottari Dasha periods (years)
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Rahu Kaal by weekday (slot index out of 8 daytime slots)
_RAHU_KAAL_SLOT = {0: 7, 1: 1, 2: 6, 3: 4, 4: 5, 5: 3, 6: 2}  # Mon=0


def _full(sign: str) -> str:
    return _SHORT.get(sign, sign)


def _subject(birth_date: date, birth_time: time | None, lat: float, lon: float, tz_str: str = "UTC") -> AstrologicalSubject:
    return AstrologicalSubject(
        name="user",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=birth_time.hour if birth_time else 12,
        minute=birth_time.minute if birth_time else 0,
        lat=lat,
        lng=lon,
        tz_str=tz_str or "UTC",
        zodiac_type="Sidereal",
        sidereal_mode="LAHIRI",
        online=False,
    )


def get_nakshatra(moon_abs_pos: float) -> tuple[str, str, int]:
    """Returns (nakshatra_name, lord, pada)."""
    pos = moon_abs_pos % 360
    idx = int(pos / (360 / 27))
    idx = min(idx, 26)
    name, lord, _ = NAKSHATRAS[idx]
    pada = int((pos % (360 / 27)) / (360 / 108)) + 1
    return name, lord, pada


def get_kundli(
    birth_date: date,
    birth_lat: float,
    birth_lon: float,
    birth_time: time | None = None,
    tz_str: str = "UTC",
) -> dict:
    s = _subject(birth_date, birth_time, birth_lat, birth_lon, tz_str)

    moon_abs = s.moon.abs_pos
    nakshatra, nak_lord, pada = get_nakshatra(moon_abs)
    rashi = _full(s.moon.sign)
    lagna = _full(s.first_house.sign)

    planets = {
        "Sun":     (_full(s.sun.sign),     s.sun.position,     s.sun.retrograde),
        "Moon":    (_full(s.moon.sign),    s.moon.position,    s.moon.retrograde),
        "Mercury": (_full(s.mercury.sign), s.mercury.position, s.mercury.retrograde),
        "Venus":   (_full(s.venus.sign),   s.venus.position,   s.venus.retrograde),
        "Mars":    (_full(s.mars.sign),    s.mars.position,    s.mars.retrograde),
        "Jupiter": (_full(s.jupiter.sign), s.jupiter.position, s.jupiter.retrograde),
        "Saturn":  (_full(s.saturn.sign),  s.saturn.position,  s.saturn.retrograde),
        "Rahu":    (_full(s.true_node.sign), s.true_node.position, True),
    }

    houses = [
        _full(getattr(s, h).sign)
        for h in ["first_house","second_house","third_house","fourth_house",
                  "fifth_house","sixth_house","seventh_house","eighth_house",
                  "ninth_house","tenth_house","eleventh_house","twelfth_house"]
    ]

    # Vimshottari dasha from nakshatra lord
    dasha_elapsed_frac = (moon_abs % (360 / 27)) / (360 / 27)
    dasha_start_lord = nak_lord
    dasha_idx = DASHA_ORDER.index(dasha_start_lord)
    dasha_years_total = DASHA_YEARS[dasha_start_lord]
    dasha_elapsed_years = dasha_elapsed_frac * dasha_years_total

    birth_dt = datetime(birth_date.year, birth_date.month, birth_date.day)
    current_dasha, next_dasha, years_left = _get_current_dasha(birth_dt, dasha_idx, dasha_elapsed_years)

    return {
        "lagna": lagna,
        "rashi": rashi,
        "nakshatra": nakshatra,
        "nakshatra_pada": pada,
        "nakshatra_lord": nak_lord,
        "planets": planets,
        "houses": houses,
        "current_dasha": current_dasha,
        "next_dasha": next_dasha,
        "dasha_years_left": round(years_left, 1),
    }


def _get_current_dasha(birth_dt: datetime, start_idx: int, elapsed_years: float):
    now = datetime.now()
    total_years = (now - birth_dt).days / 365.25
    remaining_first = DASHA_YEARS[DASHA_ORDER[start_idx]] - elapsed_years
    age = remaining_first if remaining_first > 0 else 0

    idx = start_idx
    years_accum = remaining_first

    while years_accum < total_years:
        idx = (idx + 1) % 9
        years_accum += DASHA_YEARS[DASHA_ORDER[idx]]

    current = DASHA_ORDER[idx]
    nxt = DASHA_ORDER[(idx + 1) % 9]
    years_left = years_accum - total_years
    return current, nxt, years_left


def get_sun_sign(birth_date: date) -> str:
    s = _subject(birth_date, None, 0.0, 0.0)
    return _full(s.sun.sign)


def get_panchang(lat: float, lon: float, tz_str: str = "UTC") -> dict:
    """Calculate today's panchang."""
    now_utc = datetime.now(timezone.utc)
    s = AstrologicalSubject(
        name="panchang",
        year=now_utc.year, month=now_utc.month, day=now_utc.day,
        hour=now_utc.hour, minute=now_utc.minute,
        lat=lat, lng=lon, tz_str=tz_str or "UTC",
        zodiac_type="Sidereal", sidereal_mode="LAHIRI",
        online=False,
    )

    # Tithi = lunar day (Moon - Sun longitude / 12)
    moon_sun_diff = (s.moon.abs_pos - s.sun.abs_pos) % 360
    tithi_num = int(moon_sun_diff / 12) + 1
    tithi_name = _tithi_name(tithi_num)

    # Nakshatra of Moon today
    nak, lord, pada = get_nakshatra(s.moon.abs_pos)

    # Rahu Kaal (approximate, based on weekday)
    weekday = now_utc.weekday()
    slot = _RAHU_KAAL_SLOT.get(weekday, 1)
    rahu_start_h = 6 + (slot - 1) * 1.5
    rahu_end_h = rahu_start_h + 1.5
    rahu_kaal = f"{_fmt_time(rahu_start_h)} – {_fmt_time(rahu_end_h)}"

    # Abhijit Muhurat (~11:45 AM – 12:45 PM local)
    abhijit = "11:45 – 12:45"

    return {
        "tithi": tithi_name,
        "tithi_num": tithi_num,
        "nakshatra": nak,
        "nakshatra_lord": lord,
        "rahu_kaal": rahu_kaal,
        "abhijit_muhurat": abhijit,
        "moon_sign": _full(s.moon.sign),
        "sun_sign": _full(s.sun.sign),
    }


def _tithi_name(n: int) -> str:
    names = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
    ]
    return names[min(n - 1, 14)]


def _fmt_time(h: float) -> str:
    hh = int(h)
    mm = int((h - hh) * 60)
    return f"{hh:02d}:{mm:02d}"


def format_kundli_text(kundli: dict, name: str, lang: str = "en") -> str:
    p = kundli["planets"]
    sym = SIGN_SYMBOLS

    def planet_line(planet_name: str) -> str:
        sign, deg, retro = p[planet_name]
        r = " ℞" if retro else ""
        return f"{planet_name}: {sym.get(sign,'')} {sign} {deg:.1f}°{r}"

    if lang == "hi":
        rashi_display = f"{kundli['rashi']} ({RASHI_HINDI.get(kundli['rashi'], '')})"
        lagna_display = f"{kundli['lagna']} ({RASHI_HINDI.get(kundli['lagna'], '')})"
    else:
        rashi_display = kundli["rashi"]
        lagna_display = kundli["lagna"]

    lines = [
        f"🔯 *{name} की कुंडली*" if lang == "hi" else f"🔯 *Kundli — {name}*",
        "",
        f"🌅 लग्न (Lagna): {sym.get(kundli['lagna'],'')} {lagna_display}" if lang == "hi"
            else f"🌅 Lagna (Ascendant): {sym.get(kundli['lagna'],'')} {lagna_display}",
        f"🌙 राशि (Rashi): {sym.get(kundli['rashi'],'')} {rashi_display}" if lang == "hi"
            else f"🌙 Rashi (Moon Sign): {sym.get(kundli['rashi'],'')} {rashi_display}",
        f"⭐ नक्षत्र: {kundli['nakshatra']} पाद {kundli['nakshatra_pada']} (स्वामी: {kundli['nakshatra_lord']})" if lang == "hi"
            else f"⭐ Nakshatra: {kundli['nakshatra']}, Pada {kundli['nakshatra_pada']} (Lord: {kundli['nakshatra_lord']})",
        "",
        "*ग्रह स्थिति*" if lang == "hi" else "*Planet Positions*",
    ]

    for name_p in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu"]:
        lines.append(planet_line(name_p))

    lines += [
        "",
        f"📅 महादशा: *{kundli['current_dasha']}* ({kundli['dasha_years_left']} yrs left)" if lang == "en"
            else f"📅 महादशा: *{kundli['current_dasha']}* ({kundli['dasha_years_left']} वर्ष शेष)",
        f"⏭ अगली दशा: {kundli['next_dasha']}" if lang == "hi" else f"⏭ Next Dasha: {kundli['next_dasha']}",
    ]
    return "\n".join(lines)
