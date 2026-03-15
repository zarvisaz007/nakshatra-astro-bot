"""
Vedic astrology calculations: Guna Milan, Dosha detection, remedies.
"""
from datetime import date, time

from app.services.astrology import get_kundli, NAKSHATRAS

# ── Guna Milan ────────────────────────────────────────────────────────────────

# Nakshatra index (0–26)
def _nak_index(nakshatra: str) -> int:
    for i, (name, _, _) in enumerate(NAKSHATRAS):
        if name.lower() == nakshatra.lower():
            return i
    return 0

# Varna (1 point)
_VARNA = {
    "Ashwini":1,"Bharani":0,"Krittika":3,"Rohini":3,"Mrigashira":2,"Ardra":0,
    "Punarvasu":2,"Pushya":3,"Ashlesha":0,"Magha":1,"Purva Phalguni":1,
    "Uttara Phalguni":3,"Hasta":2,"Chitra":1,"Swati":2,"Vishakha":1,
    "Anuradha":2,"Jyeshtha":0,"Moola":1,"Purva Ashadha":1,"Uttara Ashadha":3,
    "Shravana":3,"Dhanishtha":1,"Shatabhisha":2,"Purva Bhadrapada":1,
    "Uttara Bhadrapada":3,"Revati":2,
}  # 0=Shudra 1=Vaishya 2=Kshatriya 3=Brahmin

# Yoni (4 points) — animal pairs
_YONI = {
    "Ashwini":"horse","Bharani":"elephant","Krittika":"goat","Rohini":"serpent",
    "Mrigashira":"dog","Ardra":"dog","Punarvasu":"cat","Pushya":"goat",
    "Ashlesha":"cat","Magha":"rat","Purva Phalguni":"rat","Uttara Phalguni":"cow",
    "Hasta":"buffalo","Chitra":"tiger","Swati":"buffalo","Vishakha":"tiger",
    "Anuradha":"rabbit","Jyeshtha":"rabbit","Moola":"dog","Purva Ashadha":"monkey",
    "Uttara Ashadha":"mongoose","Shravana":"monkey","Dhanishtha":"lion",
    "Shatabhisha":"horse","Purva Bhadrapada":"lion","Uttara Bhadrapada":"cow","Revati":"elephant",
}
_YONI_FRIENDLY = {
    ("horse","horse"):4,("elephant","elephant"):4,("dog","dog"):4,("cat","cat"):4,
    ("rat","rat"):4,("cow","cow"):4,("buffalo","buffalo"):4,("tiger","tiger"):4,
    ("rabbit","rabbit"):4,("monkey","monkey"):4,("lion","lion"):4,("goat","goat"):4,
    ("serpent","serpent"):4,("mongoose","mongoose"):4,
    ("horse","elephant"):2,("elephant","horse"):2,
    ("dog","rabbit"):2,("rabbit","dog"):2,
    ("cat","rat"):0,("rat","cat"):0,
    ("mongoose","serpent"):0,("serpent","mongoose"):0,
}

# Rashi Guna (7 points max via Graha Maitri)
_SIGN_LORD = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter",
}
_PLANET_FRIENDS = {
    "Sun":    {"Moon","Mars","Jupiter"},
    "Moon":   {"Sun","Mercury"},
    "Mars":   {"Sun","Moon","Jupiter"},
    "Mercury":{"Sun","Venus"},
    "Jupiter":{"Sun","Moon","Mars"},
    "Venus":  {"Mercury","Saturn"},
    "Saturn": {"Mercury","Venus"},
}


def _graha_maitri(r1: str, r2: str) -> int:
    l1 = _SIGN_LORD.get(r1, "")
    l2 = _SIGN_LORD.get(r2, "")
    f1 = l2 in _PLANET_FRIENDS.get(l1, set())
    f2 = l1 in _PLANET_FRIENDS.get(l2, set())
    if f1 and f2: return 5
    if f1 or f2: return 4
    if l1 == l2: return 5
    return 1


def guna_milan(
    nak1: str, rashi1: str,
    nak2: str, rashi2: str,
) -> dict:
    score = 0
    details = {}

    # 1. Varna (1)
    v = 1 if _VARNA.get(nak2, 0) >= _VARNA.get(nak1, 0) else 0
    score += v; details["Varna"] = (v, 1)

    # 2. Vashya (2) — simplified
    vashya = 2 if rashi1 == rashi2 else 1
    score += vashya; details["Vashya"] = (vashya, 2)

    # 3. Tara (3)
    diff = ((_nak_index(nak2) - _nak_index(nak1)) % 27) % 9
    tara = 3 if diff in (1,3,5,7) else 0
    score += tara; details["Tara"] = (tara, 3)

    # 4. Yoni (4)
    y1 = _YONI.get(nak1, ""); y2 = _YONI.get(nak2, "")
    yoni = _YONI_FRIENDLY.get((y1, y2), 2)
    score += yoni; details["Yoni"] = (yoni, 4)

    # 5. Graha Maitri (5)
    gm = _graha_maitri(rashi1, rashi2)
    score += gm; details["Graha Maitri"] = (gm, 5)

    # 6. Gana (6)
    gana_score = 6 if nak1 == nak2 else 3
    score += gana_score; details["Gana"] = (gana_score, 6)

    # 7. Bhakoot (7) — rashi distance
    bk = 7 if rashi1 == rashi2 else 4
    score += bk; details["Bhakoot"] = (bk, 7)

    # 8. Nadi (8)
    nadi = 8 if _nak_index(nak1) % 3 != _nak_index(nak2) % 3 else 0
    score += nadi; details["Nadi"] = (nadi, 8)

    total = 36
    compatibility = "Excellent" if score >= 28 else "Good" if score >= 21 else "Average" if score >= 18 else "Poor"
    return {"score": score, "total": total, "compatibility": compatibility, "details": details}


# ── Dosha Detection ───────────────────────────────────────────────────────────

def detect_doshas(kundli: dict) -> dict:
    planets = kundli["planets"]
    houses = kundli["houses"]  # list of 12 sign names

    def planet_house(planet: str) -> int:
        sign = planets[planet][0]
        try: return houses.index(sign) + 1
        except ValueError: return 0

    doshas = {}

    # Manglik Dosha — Mars in 1,4,7,8,12
    mars_h = planet_house("Mars")
    doshas["Manglik"] = {
        "present": mars_h in (1, 4, 7, 8, 12),
        "house": mars_h,
        "description": f"Mars in house {mars_h}. " + (
            "Manglik Dosha present. May cause friction in marriage. Remedy: Kumbh Vivah." if mars_h in (1,4,7,8,12)
            else "No Manglik Dosha."
        ),
    }

    # Kaal Sarp Dosha — all planets between Rahu and Ketu
    rahu_sign = planets["Rahu"][0]
    rahu_h = houses.index(rahu_sign) + 1 if rahu_sign in houses else 0
    # Simplified: if Rahu in houses 1-6 and most planets in those houses
    planet_houses = [planet_house(p) for p in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]]
    kaal_sarp = rahu_h > 0 and all(h <= rahu_h or h == 0 for h in planet_houses)
    doshas["Kaal Sarp"] = {
        "present": kaal_sarp,
        "description": "Kaal Sarp Dosha present. Life may have obstacles and delays. Remedy: Nag Panchami puja." if kaal_sarp
        else "No Kaal Sarp Dosha.",
    }

    # Shani Dosha — Saturn in 1,4,7,10 (Kendras)
    saturn_h = planet_house("Saturn")
    shani = saturn_h in (1, 4, 7, 10)
    doshas["Shani"] = {
        "present": shani,
        "house": saturn_h,
        "description": f"Saturn in house {saturn_h}. " + (
            "Shani Dosha present. May bring delays and hardships. Remedy: Shani Shanti puja, donate black sesame on Saturdays." if shani
            else "Saturn is well-placed."
        ),
    }

    # Pitru Dosha — Sun afflicted (with Rahu/Saturn)
    sun_h = planet_house("Sun")
    rahu_near_sun = abs(planet_house("Rahu") - sun_h) <= 1
    pitru = rahu_near_sun or planets["Sun"][2]  # retrograde Sun is also indicator
    doshas["Pitru"] = {
        "present": pitru,
        "description": "Pitru Dosha indicated. Ancestors may need prayers. Remedy: Perform Pind Daan, Shraddha puja." if pitru
        else "No significant Pitru Dosha.",
    }

    return doshas


# ── Remedies ─────────────────────────────────────────────────────────────────

_WEAK_PLANET_REMEDIES = {
    "Sun":     ("Surya Namaskar daily at sunrise. Chant: ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः (108x Sunday morning)", "Donate wheat/jaggery on Sundays", "Ruby gemstone"),
    "Moon":    ("Chant: ॐ श्रां श्रीं श्रौं सः चंद्रमसे नमः (108x Monday evening)", "Donate rice/milk on Mondays", "Pearl gemstone"),
    "Mars":    ("Chant: ॐ क्रां क्रीं क्रौं सः भौमाय नमः (108x Tuesday)", "Donate red lentils on Tuesdays", "Red Coral gemstone"),
    "Mercury": ("Chant: ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (108x Wednesday)", "Donate green gram on Wednesdays", "Emerald gemstone"),
    "Jupiter": ("Chant: ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (108x Thursday)", "Donate yellow dal on Thursdays", "Yellow Sapphire gemstone"),
    "Venus":   ("Chant: ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (108x Friday)", "Donate sugar/rice on Fridays", "Diamond/White Sapphire"),
    "Saturn":  ("Chant: ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (108x Saturday)", "Donate black sesame/oil on Saturdays", "Blue Sapphire (only after proper consultation)"),
    "Rahu":    ("Chant: ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (108x)", "Donate blue cloth on Saturdays", "Hessonite Garnet (Gomed)"),
    "Ketu":    ("Chant: ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः (108x)", "Donate blanket on Tuesdays", "Cat's Eye gemstone"),
}

_DASHA_REMEDIES = {
    "Sun":     "Surya worship. Visit Sun temples. Offer water to the sun.",
    "Moon":    "Worship Shiva. Offer milk on Shivling. Keep silver with you.",
    "Mars":    "Hanuman worship. Recite Hanuman Chalisa on Tuesdays.",
    "Mercury": "Worship Lord Vishnu. Read Vishnu Sahasranama on Wednesdays.",
    "Jupiter": "Worship Guru/Brihaspati. Visit Vishnu temple on Thursdays.",
    "Venus":   "Worship Goddess Lakshmi. Offer white flowers on Fridays.",
    "Saturn":  "Visit Shani temple on Saturdays. Serve the poor. Sesame oil donation.",
    "Rahu":    "Worship Durga/Kali. Chant Durga Saptashati. Keep camphor at home.",
    "Ketu":    "Worship Lord Ganesha. Chant Ganesha Atharvashirsha.",
}


def get_remedies(kundli: dict) -> dict:
    dasha = kundli["current_dasha"]
    # Find retrograde planets as "weak"
    weak = [p for p, (sign, deg, retro) in kundli["planets"].items() if retro]

    remedies = {
        "dasha_remedy": {
            "planet": dasha,
            "remedy": _DASHA_REMEDIES.get(dasha, "Worship your Ishta Devata daily."),
        },
        "planet_remedies": {},
    }
    for planet in (weak or ["Saturn"]):  # default Saturn if nothing retrograde
        if planet in _WEAK_PLANET_REMEDIES:
            mantra, donation, gem = _WEAK_PLANET_REMEDIES[planet]
            remedies["planet_remedies"][planet] = {
                "mantra": mantra, "donation": donation, "gemstone": gem,
            }
    return remedies
