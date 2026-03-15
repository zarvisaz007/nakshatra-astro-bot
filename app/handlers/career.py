import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import career_analysis
from app.services import horoscope as horoscope_service

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("career"))
async def cmd_career(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "career_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        career = career_analysis(kundli)
        reading = await horoscope_service.get_career_reading(
            name=u.name or "You",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            career=career,
            lang=lang,
        )
    except Exception:
        logger.exception("Career error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    if lang == "en":
        planets_str = ", ".join(career["planets_in_10th"]) or "None"
        text = (
            f"💼 *Career Analysis — {u.name}*\n\n"
            f"🏠 *10th House:* {career['tenth_sign']} (Lord: {career['tenth_lord']})\n"
            f"🌟 *Suited Careers:* {career['career_domains']}\n"
            f"🪐 *Planets in 10th:* {planets_str}\n"
            f"📅 *Current Dasha:* {career['current_dasha']} ({career['dasha_years_left']} yrs left)\n\n"
            f"{reading}"
        )
    else:
        planets_str = ", ".join(career["planets_in_10th"]) or "कोई नहीं"
        text = (
            f"💼 *करियर विश्लेषण — {u.name}*\n\n"
            f"🏠 *दसवां भाव:* {career['tenth_sign']} (स्वामी: {career['tenth_lord']})\n"
            f"🌟 *उचित करियर:* {career['career_domains']}\n"
            f"🪐 *दसवें भाव में ग्रह:* {planets_str}\n"
            f"📅 *वर्तमान दशा:* {career['current_dasha']} ({career['dasha_years_left']} वर्ष शेष)\n\n"
            f"{reading}"
        )

    await message.answer(text, parse_mode="Markdown")
