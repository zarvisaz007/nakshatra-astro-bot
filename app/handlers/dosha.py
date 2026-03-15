import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import detect_doshas

logger = logging.getLogger(__name__)
router = Router()

_DOSHA_EMOJI = {"present": "⚠️", "absent": "✅"}


@router.message(Command("dosha"))
async def cmd_dosha(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "generating"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        doshas = detect_doshas(kundli)
    except Exception:
        logger.exception("Dosha error for user %s", u.telegram_id)
        await message.answer(t(lang, "chart_error"))
        return

    header = f"🔯 *Dosha Analysis — {u.name}*\n\n" if lang == "en" else f"🔯 *दोष विश्लेषण — {u.name}*\n\n"
    lines = [header]

    dosha_labels = {
        "en": {"Manglik": "Manglik Dosha", "Kaal Sarp": "Kaal Sarp Dosha",
               "Shani": "Shani Dosha", "Pitru": "Pitru Dosha"},
        "hi": {"Manglik": "मांगलिक दोष", "Kaal Sarp": "काल सर्प दोष",
               "Shani": "शनि दोष", "Pitru": "पितृ दोष"},
    }

    for key, data in doshas.items():
        icon = "⚠️" if data["present"] else "✅"
        label = dosha_labels.get(lang, dosha_labels["en"]).get(key, key)
        lines.append(f"{icon} *{label}*")
        lines.append(f"_{data['description']}_")
        lines.append("")

    lines.append("_Use /remedy for personalized remedies._" if lang == "en"
                 else "_व्यक्तिगत उपाय के लिए /remedy उपयोग करें।_")

    await message.answer("\n".join(lines), parse_mode="Markdown")
