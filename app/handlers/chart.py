import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_natal_chart

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("chart"))
async def cmd_chart(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "generating"))

    try:
        chart_text = get_natal_chart(
            birth_date=u.birth_date,
            birth_lat=u.birth_lat,
            birth_lon=u.birth_lon,
            birth_time=u.birth_time,
            city_name=u.city_name or "",
        )
    except Exception:
        logger.exception("Failed to calculate chart for user %s", u.telegram_id)
        await message.answer(t(lang, "chart_error"))
        return

    await message.answer(chart_text, parse_mode="Markdown")
