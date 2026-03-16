"""
reportcard.py — /reportcard handler.

Generates and sends a Destiny Report Card image for the user.

NOTE: Register this router in app/bot.py:
    from app.handlers import reportcard
    dp.include_router(reportcard.router)
And add to set_my_commands:
    BotCommand(command="reportcard", description="🔯 Your Destiny Report Card"),
"""

import logging
from datetime import date, datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from app.database import AsyncSessionFactory
from app.services import user as user_service
from app.services.astrology import SIGN_SYMBOLS, get_kundli
from app.services.card_service import generate_report_card
from app.services.numerology_service import get_numerology_profile

logger = logging.getLogger(__name__)
router = Router()

# Weekday-indexed lucky colors (Mon=0 … Sun=6)
_LUCKY_COLORS = ["White", "Pink", "Red", "Green", "Yellow", "Blue", "Purple"]


@router.message(Command("reportcard"))
async def cmd_reportcard(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    if not u.is_onboarded:
        await message.answer(
            "Please complete your profile first with /start before generating your report card."
        )
        return

    wait_msg = await message.answer("\u2728 Generating your cosmic blueprint...")

    try:
        today = datetime.now(timezone.utc).date()

        # --- Kundli ---
        kundli = get_kundli(
            u.birth_date,
            u.birth_lat,
            u.birth_lon,
            u.birth_time,
            u.timezone or "UTC",
        )
        lagna      = kundli["lagna"]
        rashi      = kundli["rashi"]
        nakshatra  = kundli["nakshatra"]
        pada       = kundli["nakshatra_pada"]
        dasha      = kundli["current_dasha"]
        sign_symbol = SIGN_SYMBOLS.get(rashi, "\U0001f52f")

        # --- Numerology ---
        profile        = get_numerology_profile(u.name or "", u.birth_date, today.year)
        life_path       = profile["life_path"]
        life_path_planet = profile["planet"]
        destiny_num     = profile["destiny"]

        # --- Lucky ---
        lucky_num   = (today.day + today.month) % 9 + 1
        lucky_color = _LUCKY_COLORS[today.weekday()]

        # --- Formatted DOB ---
        dob_str = u.birth_date.strftime("%d %b %Y")
        city    = u.city_name or "Unknown"

        # --- Generate image ---
        img_bytes = await generate_report_card(
            name=u.name or "Unknown",
            dob=dob_str,
            city=city,
            lagna=lagna,
            rashi=rashi,
            nakshatra=nakshatra,
            pada=pada,
            dasha=dasha,
            life_path=life_path,
            life_path_planet=life_path_planet,
            destiny_num=destiny_num,
            lucky_num=lucky_num,
            lucky_color=lucky_color,
            sign_symbol=sign_symbol,
        )

        await wait_msg.delete()
        await message.answer_photo(
            BufferedInputFile(img_bytes, filename="destiny_card.png"),
            caption=(
                "\U0001f52f *Your Cosmic Blueprint*\n\n"
                "_Share this with friends!_ \u2728"
            ),
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("Report card error for user %s", message.from_user.id)
        await wait_msg.delete()
        await message.answer("Couldn't generate your card. Try again shortly.")
