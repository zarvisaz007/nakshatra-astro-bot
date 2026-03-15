import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.gems_service import gem_recommendation, get_gems_reading

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("gems"))
async def cmd_gems(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    wait_msg = await message.answer("💎 Calculating your gemstone chart...")

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        gems = gem_recommendation(kundli)
        ai_reading = await get_gems_reading(
            name=u.name,
            lagna=gems["lagna"],
            rashi=kundli.get("rashi", kundli.get("moon_sign", "")),
            gems=gems,
            lang=lang,
        )
    except Exception:
        logger.exception("Gems error for user %s", u.telegram_id)
        await wait_msg.delete()
        await message.answer(t(lang, "ai_error"))
        return

    primary = gems["primary_gem"]
    supporting = gems["supporting_gems"]
    avoid = gems["gems_to_avoid"]
    lagna_lord = primary.get("planet", "")
    nak_lord = gems["nakshatra_lord"]
    dasha = gems["current_dasha"]

    if supporting:
        supporting_lines = "\n".join(
            f"• {g['name']} ({g['planet']}) — {g['benefit']}" for g in supporting
        )
    else:
        supporting_lines = "• None" if lang == "en" else "• कोई नहीं"

    avoid_text = ", ".join(avoid) if avoid else ("None" if lang == "en" else "कोई नहीं")

    if lang == "en":
        text = (
            f"💎 *Gemstone Recommendations — {u.name}*\n\n"
            f"🌅 *Lagna:* {gems['lagna']} (Lord: {lagna_lord})\n"
            f"⭐ *Nakshatra Lord:* {nak_lord}\n"
            f"📅 *Current Dasha:* {dasha}\n\n"
            f"✨ *Primary Gem (Lagna):*\n"
            f"💍 *{primary['name']}*\n"
            f"🖐️ Wear on: {primary['finger']} | 🥇 Metal: {primary['metal']}\n"
            f"⚖️ Weight: {primary['weight']}\n"
            f"🌟 Benefit: {primary['benefit']}\n"
            f"⚠️ Caution: {primary['caution']}\n\n"
            f"🔮 *Supporting Gems:*\n"
            f"{supporting_lines}\n\n"
            f"🚫 *Gems to Avoid:*\n"
            f"{avoid_text}\n\n"
            f"{ai_reading}\n\n"
            f"_Always consult a qualified Vedic astrologer before wearing gemstones._"
        )
    else:
        text = (
            f"💎 *रत्न अनुशंसा — {u.name}*\n\n"
            f"🌅 *लग्न:* {gems['lagna']} (स्वामी: {lagna_lord})\n"
            f"⭐ *नक्षत्र स्वामी:* {nak_lord}\n"
            f"📅 *वर्तमान दशा:* {dasha}\n\n"
            f"✨ *प्रमुख रत्न (लग्न):*\n"
            f"💍 *{primary['name']}*\n"
            f"🖐️ धारण करें: {primary['finger']} | 🥇 धातु: {primary['metal']}\n"
            f"⚖️ वजन: {primary['weight']}\n"
            f"🌟 लाभ: {primary['benefit']}\n"
            f"⚠️ सावधानी: {primary['caution']}\n\n"
            f"🔮 *सहायक रत्न:*\n"
            f"{supporting_lines}\n\n"
            f"🚫 *परहेज करें:*\n"
            f"{avoid_text}\n\n"
            f"{ai_reading}\n\n"
            f"_रत्न धारण करने से पहले हमेशा किसी योग्य वैदिक ज्योतिषी से परामर्श लें।_"
        )

    await wait_msg.delete()
    await message.answer(text, parse_mode="Markdown")
