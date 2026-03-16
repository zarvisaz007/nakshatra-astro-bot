import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.milestones_service import (
    get_milestones_data,
    get_milestones_reading,
    _format_timeline_display,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("milestones"))
async def cmd_milestones(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "generating"))

    try:
        kundli = get_kundli(
            u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC"
        )
        milestones = get_milestones_data(u.birth_date, kundli.get("nakshatra", ""), kundli)
        ai_reading = await get_milestones_reading(u, kundli, lang)
    except Exception:
        logger.exception("Milestones error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    name = u.name or "You"
    age = milestones["current_age"]
    current_dasha = milestones["current_dasha"]
    timeline_display = _format_timeline_display(
        milestones["dasha_timeline"], current_dasha, lang
    )

    if lang == "hi":
        text = (
            f"🌟 *जीवन के मुख्य पड़ाव — {name}* (आयु {age})\n\n"
            f"🌀 *आपकी दशा यात्रा:*\n"
            f"{timeline_display}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{ai_reading}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📌 *मुख्य काल:*\n"
            f"💼 करियर शिखर: {milestones['career_peak']}\n"
            f"💑 विवाह काल: {milestones['marriage_window']}\n"
            f"💰 धन काल: {milestones['wealth_period']}\n"
            f"🕉️ आध्यात्मिक शिखर: {milestones['spiritual_phase']}\n\n"
            "_दशा आपका ब्रह्मांडीय कैलेंडर है। इसका सदुपयोग करें। 🙏_"
        )
    else:
        text = (
            f"🌟 *Life Milestones — {name}* (Age {age})\n\n"
            f"🌀 *Your Dasha Journey:*\n"
            f"{timeline_display}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{ai_reading}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Key Windows:*\n"
            f"💼 Career Peak: {milestones['career_peak']}\n"
            f"💑 Marriage Window: {milestones['marriage_window']}\n"
            f"💰 Wealth Phase: {milestones['wealth_period']}\n"
            f"🕉️ Spiritual Peak: {milestones['spiritual_phase']}\n\n"
            "_Your dasha is your cosmic calendar. Use it wisely. 🙏_"
        )

    await message.answer(text, parse_mode="Markdown")
