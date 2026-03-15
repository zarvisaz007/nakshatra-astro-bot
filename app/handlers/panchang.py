import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_panchang

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("panchang"))
async def cmd_panchang(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    # Use user location if available, else default (Delhi)
    lat = u.birth_lat if u.birth_lat else 28.6
    lon = u.birth_lon if u.birth_lon else 77.2
    tz_str = u.timezone or "Asia/Kolkata"

    try:
        p = get_panchang(lat, lon, tz_str)
    except Exception:
        logger.exception("Panchang error")
        await message.answer(t(lang, "chart_error"))
        return

    today = datetime.now(timezone.utc).date()
    header = t(lang, "panchang_header", date=today.strftime("%d %B %Y"))
    body = t(lang, "panchang_body",
             tithi=p["tithi"], nakshatra=p["nakshatra"], lord=p["nakshatra_lord"],
             sun_sign=p["sun_sign"], moon_sign=p["moon_sign"],
             rahu_kaal=p["rahu_kaal"], abhijit=p["abhijit_muhurat"])

    await message.answer(header + body, parse_mode="Markdown")
