import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import marriage_analysis
from app.services import horoscope as horoscope_service

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("marriage"))
async def cmd_marriage(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "marriage_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        marriage = marriage_analysis(kundli)
        reading = await horoscope_service.get_marriage_reading(
            name=u.name or "You",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            marriage=marriage,
            lang=lang,
        )
    except Exception:
        logger.exception("Marriage error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    manglik_en = "Yes ⚠️" if marriage["is_manglik"] else "No ✅"
    manglik_hi = "हां ⚠️" if marriage["is_manglik"] else "नहीं ✅"
    planets_str_en = ", ".join(marriage["planets_in_7th"]) or "None"
    planets_str_hi = ", ".join(marriage["planets_in_7th"]) or "कोई नहीं"

    if lang == "en":
        text = (
            f"💑 *Marriage Analysis — {u.name}*\n\n"
            f"🏠 *7th House:* {marriage['seventh_sign']} (Lord: {marriage['seventh_lord']} in house {marriage['seventh_lord_house']})\n"
            f"💫 *Venus in house:* {marriage['venus_house']}\n"
            f"🪐 *Jupiter in house:* {marriage['jupiter_house']}\n"
            f"🔴 *Planets in 7th:* {planets_str_en}\n"
            f"⚠️ *Manglik:* {manglik_en}\n"
            f"📅 *Current Dasha:* {marriage['current_dasha']} ({marriage['dasha_years_left']} yrs left)\n\n"
            f"{reading}"
        )
    else:
        text = (
            f"💑 *विवाह विश्लेषण — {u.name}*\n\n"
            f"🏠 *सप्तम भाव:* {marriage['seventh_sign']} (स्वामी: {marriage['seventh_lord']} भाव {marriage['seventh_lord_house']} में)\n"
            f"💫 *शुक्र भाव:* {marriage['venus_house']}\n"
            f"🪐 *बृहस्पति भाव:* {marriage['jupiter_house']}\n"
            f"🔴 *सप्तम भाव में ग्रह:* {planets_str_hi}\n"
            f"⚠️ *मांगलिक:* {manglik_hi}\n"
            f"📅 *वर्तमान दशा:* {marriage['current_dasha']} ({marriage['dasha_years_left']} वर्ष शेष)\n\n"
            f"{reading}"
        )

    await message.answer(text, parse_mode="Markdown")
