from datetime import date, time

from kerykeion import AstrologicalSubject

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_SYMBOLS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
    "Uranus": "⛢", "Neptune": "♆", "Pluto": "♇",
}


def get_sun_sign(birth_date: date) -> str:
    subject = AstrologicalSubject(
        name="user",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=12,
        minute=0,
        lat=0.0,
        lng=0.0,
        tz_str="UTC",
        online=False,
    )
    return subject.sun.sign


def get_natal_chart(
    birth_date: date,
    birth_lat: float,
    birth_lon: float,
    birth_time: time | None = None,
    city_name: str = "",
) -> str:
    hour = birth_time.hour if birth_time else 12
    minute = birth_time.minute if birth_time else 0
    time_note = "" if birth_time else " (approximate — no birth time given)"

    subject = AstrologicalSubject(
        name="user",
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=hour,
        minute=minute,
        lat=birth_lat,
        lng=birth_lon,
        tz_str="UTC",
        online=False,
    )

    planets = [
        ("Sun", subject.sun),
        ("Moon", subject.moon),
        ("Mercury", subject.mercury),
        ("Venus", subject.venus),
        ("Mars", subject.mars),
        ("Jupiter", subject.jupiter),
        ("Saturn", subject.saturn),
    ]

    lines = [
        f"*Your Natal Chart*{time_note}",
        f"Born: {birth_date.strftime('%B %d, %Y')}" + (f" {birth_time.strftime('%H:%M')}" if birth_time else ""),
        f"Location: {city_name or f'{birth_lat:.2f}, {birth_lon:.2f}'}",
        "",
        "*Planetary Positions*",
    ]

    for name, planet in planets:
        symbol = PLANET_SYMBOLS.get(name, "")
        sign_symbol = SIGN_SYMBOLS.get(planet.sign, "")
        lines.append(f"{symbol} {name}: {sign_symbol} {planet.sign} {planet.position:.1f}°")

    lines += [
        "",
        f"*Rising Sign:* {SIGN_SYMBOLS.get(subject.first_house.sign, '')} {subject.first_house.sign}"
        + ("" if birth_time else " *(accurate birth time needed)*"),
    ]

    return "\n".join(lines)
