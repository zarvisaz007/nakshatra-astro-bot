import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import get_remedies

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("remedy"))
async def cmd_remedy(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "generating"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        remedies = get_remedies(kundli)
    except Exception:
        logger.exception("Remedy error for user %s", u.telegram_id)
        await message.answer(t(lang, "chart_error"))
        return

    lines = [
        f"🕉️ *Personal Remedies — {u.name}*\n" if lang == "en" else f"🕉️ *व्यक्तिगत उपाय — {u.name}*\n"
    ]

    # Dasha remedy
    dr = remedies["dasha_remedy"]
    lines += [
        f"*Current Mahadasha: {dr['planet']}*" if lang == "en" else f"*वर्तमान महादशा: {dr['planet']}*",
        f"_{dr['remedy']}_",
        "",
    ]

    # Planet remedies
    if remedies["planet_remedies"]:
        lines.append("*Planetary Remedies:*" if lang == "en" else "*ग्रह उपाय:*")
        for planet, data in remedies["planet_remedies"].items():
            lines += [
                f"\n🪐 *{planet}*",
                f"📿 {data['mantra']}",
                f"🤲 {data['donation']}",
                f"💎 {data['gemstone']}",
            ]

    lines += [
        "",
        "_Consult a qualified astrologer before wearing gemstones._" if lang == "en"
        else "_रत्न पहनने से पहले किसी योग्य ज्योतिषी से परामर्श लें।_",
    ]

    await message.answer("\n".join(lines), parse_mode="Markdown")
