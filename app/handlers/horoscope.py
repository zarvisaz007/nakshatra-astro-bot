import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services import horoscope as horo_service
from app.services.astrology import get_kundli, get_sun_sign, SIGN_SYMBOLS, RASHI_HINDI

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

    today = datetime.now(timezone.utc).date()
    await message.answer(t(lang, "generating"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        sign = get_sun_sign(u.birth_date)
        rashi = kundli["rashi"]
        moon_sign = kundli["rashi"]
        nakshatra = kundli["nakshatra"]

        lucky_num = (today.day + today.month) % 9 + 1
        from app.services.horoscope import _LUCKY_COLORS, _LUCKY_COLORS_HI
        lucky_color = (_LUCKY_COLORS_HI if lang == "hi" else _LUCKY_COLORS)[today.weekday()]

        reading = await horo_service.get_reading(sign, rashi, moon_sign, nakshatra, today, lang)
    except Exception:
        logger.exception("Horoscope error for user %s", u.telegram_id)
        await message.answer(t(lang, "horo_error"))
        return

    if not reading:
        await message.answer(t(lang, "horo_error"))
        return

    symbol = SIGN_SYMBOLS.get(sign, "")
    rashi_display = f"{rashi} / {RASHI_HINDI.get(rashi, '')}" if lang == "hi" else rashi
    header = t(lang, "horo_header", symbol=symbol, sign=sign, rashi=rashi_display,
               date=today.strftime("%d %B %Y"))
    footer = t(lang, "horo_footer", num=lucky_num, color=lucky_color)

    await message.answer(header + reading + footer, parse_mode="Markdown")
