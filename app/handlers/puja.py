import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.puja_service import puja_recommendation, get_puja_reading

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("puja"))
async def cmd_puja(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "puja_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        puja = puja_recommendation(kundli)
        reading = await get_puja_reading(
            name=u.name or "You",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            puja=puja,
            lang=lang,
        )
    except Exception:
        logger.exception("Puja error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    p = puja["primary_puja"]
    specials = puja["special_pujas"]

    if lang == "en":
        special_lines = "\n".join(f"• *{s['name']}* ({s['day']}) — {s['benefit']}" for s in specials)
        text = (
            f"🕉️ *Puja Recommendations — {u.name}*\n\n"
            f"🙏 *Primary Puja:* {p['name']}\n"
            f"👁️ *Deity:* {p['deity']}\n"
            f"📅 *Best Day:* {p['day']}\n"
            f"🔱 *Mantra:* `{p['mantra']}`\n"
            f"✨ *Benefit:* {p['benefit']}\n\n"
            f"🌟 *Special Pujas:*\n{special_lines}\n\n"
            f"{reading}"
        )
    else:
        special_lines = "\n".join(f"• *{s['name']}* ({s['day']}) — {s['benefit']}" for s in specials)
        text = (
            f"🕉️ *पूजा अनुशंसा — {u.name}*\n\n"
            f"🙏 *प्रमुख पूजा:* {p['name']}\n"
            f"👁️ *देवता:* {p['deity']}\n"
            f"📅 *उचित दिन:* {p['day']}\n"
            f"🔱 *मंत्र:* `{p['mantra']}`\n"
            f"✨ *लाभ:* {p['benefit']}\n\n"
            f"🌟 *विशेष पूजाएं:*\n{special_lines}\n\n"
            f"{reading}"
        )

    await message.answer(text, parse_mode="Markdown")
