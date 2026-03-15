import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli, NAKSHATRAS

logger = logging.getLogger(__name__)
router = Router()

_LUCKY_DAYS = {
    "Sun": "Sunday", "Moon": "Monday", "Mars": "Tuesday",
    "Mercury": "Wednesday", "Jupiter": "Thursday",
    "Venus": "Friday", "Saturn": "Saturday",
    "Rahu": "Saturday", "Ketu": "Tuesday",
}
_LUCKY_DAYS_HI = {
    "Sun": "रविवार", "Moon": "सोमवार", "Mars": "मंगलवार",
    "Mercury": "बुधवार", "Jupiter": "गुरुवार",
    "Venus": "शुक्रवार", "Saturn": "शनिवार",
    "Rahu": "शनिवार", "Ketu": "मंगलवार",
}
_LUCKY_COLORS = {
    "Sun": "Orange/Gold", "Moon": "White/Silver", "Mars": "Red",
    "Mercury": "Green", "Jupiter": "Yellow", "Venus": "White/Pink",
    "Saturn": "Blue/Black", "Rahu": "Dark Blue", "Ketu": "Grey/Brown",
}
_LUCKY_GEMS = {
    "Sun": "Ruby", "Moon": "Pearl", "Mars": "Red Coral",
    "Mercury": "Emerald", "Jupiter": "Yellow Sapphire",
    "Venus": "Diamond/White Sapphire", "Saturn": "Blue Sapphire",
    "Rahu": "Hessonite (Gomed)", "Ketu": "Cat's Eye",
}

_VOWEL_LETTERS = {
    1: "A, I, Y", 2: "B, K, R", 3: "G, L, S", 4: "D, M, T",
    5: "E, H, N, X", 6: "U, V, W", 7: "O, Z", 8: "F, P",
    9: "C, G, J, Q",
}


def _life_path(dob: date) -> int:
    n = sum(int(c) for c in str(dob.year) + f"{dob.month:02d}" + f"{dob.day:02d}")
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


@router.message(Command("lucky"))
async def cmd_lucky(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        nak_lord = kundli["nakshatra_lord"]
        life_path = _life_path(u.birth_date)
        lucky_letters = _VOWEL_LETTERS.get(life_path, "A")
        lucky_day = (_LUCKY_DAYS_HI if lang == "hi" else _LUCKY_DAYS).get(nak_lord, "—")
        lucky_color = _LUCKY_COLORS.get(nak_lord, "—")
        lucky_gem = _LUCKY_GEMS.get(nak_lord, "—")
        lucky_number = life_path
        lucky_num_2 = (u.birth_date.day % 9) or 9
    except Exception:
        logger.exception("Lucky error for user %s", u.telegram_id)
        await message.answer(t(lang, "chart_error"))
        return

    if lang == "en":
        text = (
            f"🍀 *Lucky Profile — {u.name}*\n\n"
            f"🌟 *Nakshatra Lord:* {nak_lord}\n\n"
            f"🔢 *Life Path Number:* {lucky_number}\n"
            f"🔢 *Personal Number:* {lucky_num_2}\n"
            f"🔤 *Lucky Name Letters:* {lucky_letters}\n\n"
            f"📅 *Lucky Day:* {lucky_day}\n"
            f"🎨 *Lucky Color:* {lucky_color}\n"
            f"💎 *Lucky Gemstone:* {lucky_gem}\n\n"
            f"🌙 *Nakshatra:* {kundli['nakshatra']} (lord: {nak_lord})\n\n"
            f"_For baby/business names, start with letters: *{lucky_letters}*_\n"
            f"_Vehicle numbers with digit {lucky_number} are favorable._"
        )
    else:
        text = (
            f"🍀 *शुभ प्रोफ़ाइल — {u.name}*\n\n"
            f"🌟 *नक्षत्र स्वामी:* {nak_lord}\n\n"
            f"🔢 *जीवन पथ संख्या:* {lucky_number}\n"
            f"🔢 *व्यक्तिगत संख्या:* {lucky_num_2}\n"
            f"🔤 *शुभ नाम अक्षर:* {lucky_letters}\n\n"
            f"📅 *शुभ दिन:* {lucky_day}\n"
            f"🎨 *शुभ रंग:* {lucky_color}\n"
            f"💎 *शुभ रत्न:* {lucky_gem}\n\n"
            f"🌙 *नक्षत्र:* {kundli['nakshatra']} (स्वामी: {nak_lord})\n\n"
            f"_बच्चे/व्यवसाय के नाम *{lucky_letters}* अक्षरों से शुरू करें_\n"
            f"_{lucky_number} अंक वाले वाहन नंबर शुभ हैं।_"
        )

    await message.answer(text, parse_mode="Markdown")
