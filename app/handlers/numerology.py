import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.services import user as user_service
from app.services.numerology_service import (
    get_numerology_profile,
    get_numerology_reading,
    format_reading_en,
    format_reading_hi,
)

logger = logging.getLogger(__name__)
router = Router()

_STRINGS = {
    "en": {
        "no_profile": "Please complete your profile first. Use /start to set up.",
        "wait": "🔢 Calculating your numerology reading... please wait.",
        "error": "Sorry, could not generate your numerology reading. Please try again later.",
    },
    "hi": {
        "no_profile": "कृपया पहले अपना प्रोफ़ाइल पूरा करें। /start का उपयोग करें।",
        "wait": "🔢 आपका अंकज्योतिष पठन तैयार हो रहा है... कृपया प्रतीक्षा करें।",
        "error": "क्षमा करें, अंकज्योतिष पठन उत्पन्न नहीं हो सका। कृपया बाद में पुनः प्रयास करें।",
    },
}


@router.message(Command("numerology"))
async def cmd_numerology(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"
    strings = _STRINGS.get(lang, _STRINGS["en"])

    if not u.is_onboarded:
        await message.answer(strings["no_profile"])
        return

    await message.answer(strings["wait"])

    try:
        dob: date = u.birth_date
        name: str = u.name or "You"
        today = date.today()

        profile = get_numerology_profile(name, dob, today.year)
        ai_reading = await get_numerology_reading(name, dob, profile, lang)
    except Exception:
        logger.exception("Numerology error for user %s", u.telegram_id)
        await message.answer(strings["error"])
        return

    if not ai_reading:
        await message.answer(strings["error"])
        return

    if lang == "hi":
        text = format_reading_hi(name, dob, profile, ai_reading)
    else:
        text = format_reading_en(name, dob, profile, ai_reading)

    await message.answer(text, parse_mode="Markdown")
