import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services import horoscope as horoscope_service
from app.services.astrology import get_sun_sign, SIGN_SYMBOLS

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("horoscope"))
async def cmd_horoscope(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    sign = get_sun_sign(u.birth_date)
    today = datetime.now(timezone.utc).date()

    await message.answer(t(lang, "generating"))

    try:
        reading = await horoscope_service.get_reading(sign, today, lang)
    except Exception:
        logger.exception("Failed to generate horoscope for %s", sign)
        await message.answer(t(lang, "horo_error"))
        return

    if not reading:
        await message.answer(t(lang, "horo_error"))
        return

    symbol = SIGN_SYMBOLS.get(sign, "")
    await message.answer(
        f"{symbol} *{sign} — {today.strftime('%B %d, %Y')}*\n\n{reading}",
        parse_mode="Markdown",
    )
