import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.mantra_service import mantra_sadhana, get_mantra_reading

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("mantra"))
async def cmd_mantra(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    await message.answer(t(lang, "mantra_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        md = mantra_sadhana(kundli)
        reading = await get_mantra_reading(
            name=u.name or "You",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            mantra_data=md,
            lang=lang,
        )
    except Exception:
        logger.exception("Mantra error for user %s", u.telegram_id)
        await message.answer(t(lang, "ai_error"))
        return

    dm = md["daily_mantra"]
    dsh = md["dasha_mantra"]
    tips = md["sadhana_tips_hi"] if lang == "hi" else md["sadhana_tips"]

    if lang == "en":
        dasha_section = ""
        if not md["same_lord"]:
            dasha_section = (
                f"\n🌟 *Dasha Mantra ({md['current_dasha']} period):*\n"
                f"`{dsh['mantra']}`\n"
                f"_{dsh['benefit']}_\n"
            )
        text = (
            f"🕉️ *Personal Mantra Sadhana — {u.name}*\n\n"
            f"⭐ *Nakshatra:* {md['nakshatra']} (Lord: {md['nakshatra_lord']})\n"
            f"📅 *Current Dasha:* {md['current_dasha']}\n\n"
            f"🔱 *Daily Mantra ({md['nakshatra_lord']} beeja):*\n"
            f"`{dm['mantra']}`\n"
            f"🙏 *Deity:* {dm['deity']}  |  ⏰ *Best time:* {dm['best_time']}\n"
            f"✨ *Benefit:* {dm['benefit']}\n"
            f"{dasha_section}\n"
            f"📿 *Sadhana Tips:*\n"
            + "\n".join(f"• {tip}" for tip in tips) +
            f"\n\n{reading}"
        )
    else:
        dasha_section = ""
        if not md["same_lord"]:
            dasha_section = (
                f"\n🌟 *दशा मंत्र ({md['current_dasha']} दशा):*\n"
                f"`{dsh['mantra']}`\n"
                f"_{dsh['benefit']}_\n"
            )
        text = (
            f"🕉️ *व्यक्तिगत मंत्र साधना — {u.name}*\n\n"
            f"⭐ *नक्षत्र:* {md['nakshatra']} (स्वामी: {md['nakshatra_lord']})\n"
            f"📅 *वर्तमान दशा:* {md['current_dasha']}\n\n"
            f"🔱 *दैनिक मंत्र ({md['nakshatra_lord']} बीज):*\n"
            f"`{dm['mantra']}`\n"
            f"🙏 *देवता:* {dm['deity']}  |  ⏰ *उचित समय:* {dm['best_time']}\n"
            f"✨ *लाभ:* {dm['benefit']}\n"
            f"{dasha_section}\n"
            f"📿 *साधना सुझाव:*\n"
            + "\n".join(f"• {tip}" for tip in tips) +
            f"\n\n{reading}"
        )

    await message.answer(text, parse_mode="Markdown")
