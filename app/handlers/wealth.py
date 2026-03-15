import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import wealth_analysis
from app.services import horoscope as horoscope_service

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("wealth"))
async def cmd_wealth(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "wealth_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        wealth = wealth_analysis(kundli)
        reading = await horoscope_service.get_wealth_reading(
            name=u.name or "You",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            wealth=wealth,
            lang=lang,
        )
    except Exception:
        logger.exception("Wealth error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    p2_en = ", ".join(wealth["planets_in_2nd"]) or "None"
    p11_en = ", ".join(wealth["planets_in_11th"]) or "None"
    p2_hi = ", ".join(wealth["planets_in_2nd"]) or "कोई नहीं"
    p11_hi = ", ".join(wealth["planets_in_11th"]) or "कोई नहीं"

    if lang == "en":
        text = (
            f"💰 *Wealth Analysis — {u.name}*\n\n"
            f"🏦 *2nd House (Savings):* {wealth['second_sign']} (Lord: {wealth['second_lord']})\n"
            f"📈 *11th House (Gains):* {wealth['eleventh_sign']} (Lord: {wealth['eleventh_lord']})\n"
            f"🪐 *Jupiter in house:* {wealth['jupiter_house']}\n"
            f"💎 *Planets in 2nd:* {p2_en}\n"
            f"📊 *Planets in 11th:* {p11_en}\n"
            f"🌿 *Wealth Nature:* {wealth['wealth_nature']}\n"
            f"📅 *Current Dasha:* {wealth['current_dasha']} ({wealth['dasha_years_left']} yrs left)\n\n"
            f"{reading}"
        )
    else:
        text = (
            f"💰 *धन विश्लेषण — {u.name}*\n\n"
            f"🏦 *द्वितीय भाव (बचत):* {wealth['second_sign']} (स्वामी: {wealth['second_lord']})\n"
            f"📈 *एकादश भाव (लाभ):* {wealth['eleventh_sign']} (स्वामी: {wealth['eleventh_lord']})\n"
            f"🪐 *बृहस्पति भाव:* {wealth['jupiter_house']}\n"
            f"💎 *द्वितीय भाव में ग्रह:* {p2_hi}\n"
            f"📊 *एकादश भाव में ग्रह:* {p11_hi}\n"
            f"🌿 *धन स्वभाव:* {wealth['wealth_nature']}\n"
            f"📅 *वर्तमान दशा:* {wealth['current_dasha']} ({wealth['dasha_years_left']} वर्ष शेष)\n\n"
            f"{reading}"
        )

    await message.answer(text, parse_mode="Markdown")
