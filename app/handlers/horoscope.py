import logging
from datetime import date, timezone, datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.services import user as user_service
from app.services import horoscope as horoscope_service
from app.services.astrology import get_sun_sign, SIGN_SYMBOLS

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("horoscope"))
async def cmd_horoscope(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    if not u.is_onboarded:
        await message.answer("You haven't set up your profile yet. Run /start to get started!")
        return

    sign = get_sun_sign(u.birth_date)
    today = datetime.now(timezone.utc).date()

    await message.answer("Consulting the stars... ✨")

    try:
        reading = await horoscope_service.get_reading(sign, today)
    except Exception:
        logger.exception("Failed to generate horoscope for %s", sign)
        await message.answer("Something went wrong generating your horoscope. Try again in a moment.")
        return

    symbol = SIGN_SYMBOLS.get(sign, "")
    header = f"{symbol} *{sign} — {today.strftime('%B %d, %Y')}*\n\n"
    await message.answer(header + reading, parse_mode="Markdown")
