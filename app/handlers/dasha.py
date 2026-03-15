import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import get_dasha_timeline

logger = logging.getLogger(__name__)
router = Router()

_DASHA_KEYWORDS = {
    "Sun":     "authority, health, government",
    "Moon":    "emotions, home, mother, public",
    "Mars":    "energy, ambition, property, siblings",
    "Mercury": "communication, business, education",
    "Jupiter": "wisdom, expansion, children, wealth",
    "Venus":   "love, luxury, arts, relationships",
    "Saturn":  "discipline, delays, service, karma",
    "Rahu":    "ambition, foreign, illusion, sudden changes",
    "Ketu":    "spirituality, moksha, past karma, detachment",
}
_DASHA_KEYWORDS_HI = {
    "Sun":     "अधिकार, स्वास्थ्य, सरकार",
    "Moon":    "भावना, घर, माता, जनता",
    "Mars":    "ऊर्जा, महत्वाकांक्षा, संपत्ति",
    "Mercury": "संचार, व्यापार, शिक्षा",
    "Jupiter": "ज्ञान, विस्तार, संतान, धन",
    "Venus":   "प्रेम, विलासिता, कला, रिश्ते",
    "Saturn":  "अनुशासन, विलंब, सेवा, कर्म",
    "Rahu":    "महत्वाकांक्षा, विदेश, भ्रम, अचानक बदलाव",
    "Ketu":    "आध्यात्म, मोक्ष, पिछला कर्म, वैराग्य",
}


@router.message(Command("dasha"))
async def cmd_dasha(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        timeline = get_dasha_timeline(kundli)
    except Exception:
        logger.exception("Dasha error for user %s", u.telegram_id)
        await message.answer(t(lang, "chart_error"))
        return

    keywords = _DASHA_KEYWORDS_HI if lang == "hi" else _DASHA_KEYWORDS

    if lang == "en":
        lines = [f"🌀 *Vimshottari Dasha — {u.name}*\n"]
        for d in timeline:
            marker = "▶️ " if d["is_current"] else "   "
            kw = keywords.get(d["planet"], "")
            lines.append(
                f"{marker}*{d['planet']}* ({d['years']} yrs)\n"
                f"    {d['start'].strftime('%b %Y')} → {d['end'].strftime('%b %Y')}\n"
                f"    _{kw}_\n"
            )
        lines.append("_Vimshottari system: 120-year cycle of 9 planetary periods._")
    else:
        lines = [f"🌀 *विंशोत्तरी दशा — {u.name}*\n"]
        for d in timeline:
            marker = "▶️ " if d["is_current"] else "   "
            kw = keywords.get(d["planet"], "")
            lines.append(
                f"{marker}*{d['planet']}* ({d['years']} वर्ष)\n"
                f"    {d['start'].strftime('%b %Y')} → {d['end'].strftime('%b %Y')}\n"
                f"    _{kw}_\n"
            )
        lines.append("_विंशोत्तरी पद्धति: 120 वर्षीय 9 ग्रह दशाओं का चक्र।_")

    await message.answer("\n".join(lines), parse_mode="Markdown")
