import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.services import user as user_service
from app.services.astrology import get_natal_chart

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("chart"))
async def cmd_chart(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    if not u.is_onboarded:
        await message.answer("You haven't set up your profile yet. Run /start to get started!")
        return

    await message.answer("Calculating your natal chart... 🔭")

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
        await message.answer("Something went wrong calculating your chart. Try again in a moment.")
        return

    await message.answer(chart_text, parse_mode="Markdown")
