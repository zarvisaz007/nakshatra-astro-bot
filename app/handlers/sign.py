from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.astrology import SIGN_NAMES, SIGN_SYMBOLS

router = Router()

SIGN_INFO: dict[str, str] = {
    "Aries": "Bold, driven, and fiercely independent. A natural leader with unstoppable energy. Rules: action, new beginnings. Element: Fire. Dates: Mar 21 – Apr 19.",
    "Taurus": "Grounded, patient, and deeply sensual. Values stability, beauty, and the finer things. Element: Earth. Dates: Apr 20 – May 20.",
    "Gemini": "Curious, witty, and endlessly adaptable. Masters of communication and quick thinking. Element: Air. Dates: May 21 – Jun 20.",
    "Cancer": "Deeply intuitive and nurturing. Protective of loved ones, driven by emotion and memory. Element: Water. Dates: Jun 21 – Jul 22.",
    "Leo": "Magnetic, generous, and born to shine. Leads with heart and craves authentic self-expression. Element: Fire. Dates: Jul 23 – Aug 22.",
    "Virgo": "Analytical, precise, and quietly devoted. Finds meaning in service and mastery of craft. Element: Earth. Dates: Aug 23 – Sep 22.",
    "Libra": "Charming, fair-minded, and aesthetically gifted. Seeks harmony and balance in all things. Element: Air. Dates: Sep 23 – Oct 22.",
    "Scorpio": "Intense, perceptive, and transformative. Digs beneath surfaces and never takes things at face value. Element: Water. Dates: Oct 23 – Nov 21.",
    "Sagittarius": "Freedom-loving, philosophical, and wildly optimistic. Always chasing the next horizon. Element: Fire. Dates: Nov 22 – Dec 21.",
    "Capricorn": "Ambitious, disciplined, and built for the long game. Turns dreams into structures that last. Element: Earth. Dates: Dec 22 – Jan 19.",
    "Aquarius": "Visionary, unconventional, and deeply humanitarian. Thinks in systems and futures. Element: Air. Dates: Jan 20 – Feb 18.",
    "Pisces": "Empathic, imaginative, and spiritually attuned. Lives between worlds — logic and dream. Element: Water. Dates: Feb 19 – Mar 20.",
}

_ALIASES: dict[str, str] = {
    s[:3].lower(): s for s in SIGN_NAMES
} | {s.lower(): s for s in SIGN_NAMES}


@router.message(Command("sign"))
async def cmd_sign(message: Message) -> None:
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        signs_list = "  ".join(f"{SIGN_SYMBOLS[s]} {s}" for s in SIGN_NAMES)
        await message.answer(
            "Usage: /sign <zodiac>\nExample: /sign Aries\n\n" + signs_list
        )
        return

    query = parts[1].strip().lower()
    sign = _ALIASES.get(query)

    if not sign:
        await message.answer(f"Unknown sign '{parts[1]}'. Try /sign for the full list.")
        return

    symbol = SIGN_SYMBOLS.get(sign, "")
    await message.answer(f"{symbol} *{sign}*\n\n{SIGN_INFO[sign]}", parse_mode="Markdown")
