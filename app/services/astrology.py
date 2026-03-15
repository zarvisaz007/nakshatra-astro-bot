from datetime import date, time

from kerykeion import AstrologicalSubject

# kerykeion returns 3-letter abbreviations — map to full names
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

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}


def _full(sign: str) -> str:
    return _SHORT.get(sign, sign)


def _subject(birth_date: date, birth_time: time | None, lat: float, lon: float) -> AstrologicalSubject:
    return AstrologicalSubject(
        name="user",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=birth_time.hour if birth_time else 12,
        minute=birth_time.minute if birth_time else 0,
        lat=lat,
        lng=lon,
        tz_str="UTC",
        online=False,
    )


def get_sun_sign(birth_date: date) -> str:
    s = _subject(birth_date, None, 0.0, 0.0)
    return _full(s.sun.sign)


def get_natal_chart(
    birth_date: date,
    birth_lat: float,
    birth_lon: float,
    birth_time: time | None = None,
    city_name: str = "",
) -> str:
    s = _subject(birth_date, birth_time, birth_lat, birth_lon)
    time_note = "" if birth_time else " _(approximate — no birth time)_"

    planets = [
        ("Sun", s.sun), ("Moon", s.moon), ("Mercury", s.mercury),
        ("Venus", s.venus), ("Mars", s.mars), ("Jupiter", s.jupiter), ("Saturn", s.saturn),
    ]

    lines = [
        f"*Your Natal Chart*{time_note}",
        f"📅 {birth_date.strftime('%B %d, %Y')}" + (f" {birth_time.strftime('%H:%M')}" if birth_time else ""),
        f"📍 {city_name or f'{birth_lat:.2f}, {birth_lon:.2f}'}",
        "",
        "*Planets*",
    ]
    for name, planet in planets:
        sym = PLANET_SYMBOLS.get(name, "")
        sign = _full(planet.sign)
        lines.append(f"{sym} {name}: {SIGN_SYMBOLS.get(sign,'')} {sign} {planet.position:.1f}°")

    rising = _full(s.first_house.sign)
    lines += [
        "",
        f"*Rising:* {SIGN_SYMBOLS.get(rising,'')} {rising}"
        + ("" if birth_time else " _(need birth time)_"),
    ]
    return "\n".join(lines)
