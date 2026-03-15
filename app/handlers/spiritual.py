import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services import horoscope as horo_service
from app.services.astrology import get_kundli

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("spiritual"))
async def cmd_spiritual(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    today = datetime.now(timezone.utc).date()
    await message.answer(t(lang, "generating"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        guidance = await horo_service.get_spiritual_guidance(
            moon_sign=kundli["rashi"],
            nakshatra=kundli["nakshatra"],
            day=today, lang=lang,
        )
    except Exception:
        logger.exception("Spiritual guidance error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    header = t(lang, "spiritual_header", date=today.strftime("%d %B %Y"))
    await message.answer(header + guidance, parse_mode="Markdown")
