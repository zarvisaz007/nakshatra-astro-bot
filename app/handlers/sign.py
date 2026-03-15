from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import SIGN_NAMES, SIGN_SYMBOLS

router = Router()

SIGN_INFO = {
    "Aries":       "Bold, driven, independent. Natural leader. Fire sign. Mar 21 – Apr 19.",
    "Taurus":      "Grounded, patient, sensual. Values stability & beauty. Earth sign. Apr 20 – May 20.",
    "Gemini":      "Curious, witty, adaptable. Master communicator. Air sign. May 21 – Jun 20.",
    "Cancer":      "Intuitive, nurturing, protective. Driven by emotion. Water sign. Jun 21 – Jul 22.",
    "Leo":         "Magnetic, generous, expressive. Born to shine. Fire sign. Jul 23 – Aug 22.",
    "Virgo":       "Analytical, precise, devoted. Finds meaning in service. Earth sign. Aug 23 – Sep 22.",
    "Libra":       "Charming, fair, aesthetic. Seeks harmony in all things. Air sign. Sep 23 – Oct 22.",
    "Scorpio":     "Intense, perceptive, transformative. Sees beneath surfaces. Water sign. Oct 23 – Nov 21.",
    "Sagittarius": "Free-spirited, philosophical, optimistic. Chases horizons. Fire sign. Nov 22 – Dec 21.",
    "Capricorn":   "Ambitious, disciplined, patient. Built for the long game. Earth sign. Dec 22 – Jan 19.",
    "Aquarius":    "Visionary, unconventional, humanitarian. Thinks in futures. Air sign. Jan 20 – Feb 18.",
    "Pisces":      "Empathic, imaginative, spiritual. Lives between worlds. Water sign. Feb 19 – Mar 20.",
}

_ALIASES: dict[str, str] = {s[:3].lower(): s for s in SIGN_NAMES} | {s.lower(): s for s in SIGN_NAMES}


async def _get_lang(telegram_id: int) -> str:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, telegram_id)
    return u.language or "en"


@router.message(Command("sign"))
async def cmd_sign(message: Message) -> None:
    lang = await _get_lang(message.from_user.id)
    parts = message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        signs_list = "  ".join(f"{SIGN_SYMBOLS[s]} {s}" for s in SIGN_NAMES)
        await message.answer(t(lang, "sign_usage", list=signs_list), parse_mode="Markdown")
        return

    query = parts[1].strip().lower()
    sign = _ALIASES.get(query)

    if not sign:
        await message.answer(t(lang, "sign_unknown", sign=parts[1]), parse_mode="Markdown")
        return

    await message.answer(
        f"{SIGN_SYMBOLS[sign]} *{sign}*\n\n{SIGN_INFO[sign]}",
        parse_mode="Markdown",
    )
