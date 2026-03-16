import base64
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.palm_service import get_palm_reading

logger = logging.getLogger(__name__)
router = Router()


class PalmState(StatesGroup):
    waiting_for_photo = State()


@router.message(Command("palmreading"))
async def cmd_palmreading(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    if lang == "hi":
        prompt_text = (
            "🖐️ अपने प्रमुख हाथ की एक स्पष्ट फोटो भेजें (हथेली ऊपर की ओर)। "
            "सुनिश्चित करें कि रेखाएं स्पष्ट दिखें।"
        )
    else:
        prompt_text = (
            "🖐️ Send a clear photo of your dominant hand (palm facing up). "
            "Make sure the lines are visible."
        )

    await message.answer(prompt_text)
    await state.set_state(PalmState.waiting_for_photo)


@router.message(PalmState.waiting_for_photo, F.photo)
async def process_palm_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()

    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    wait_text = "🖐️ Reading your palm..." if lang == "en" else "🖐️ आपकी हथेली पढ़ी जा रही है..."
    await message.answer(wait_text)

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)
        photo_b64 = base64.b64encode(file_bytes.read()).decode()
    except Exception:
        logger.exception("Palm photo download error for user %s", message.from_user.id)
        error_text = (
            "❌ Could not download your photo. Please try again."
            if lang == "en"
            else "❌ फोटो डाउनलोड नहीं हो सकी। कृपया पुनः प्रयास करें।"
        )
        await message.answer(error_text)
        return

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        reading = await get_palm_reading(
            photo_base64=photo_b64,
            name=u.name or "User",
            lagna=kundli["lagna"],
            nakshatra=kundli["nakshatra"],
            dasha=kundli["current_dasha"],
            lang=lang,
        )
    except Exception:
        logger.exception("Palm reading AI error for user %s", message.from_user.id)
        await message.answer(t(lang, "ai_error"))
        return

    if not reading:
        await message.answer(t(lang, "ai_error"))
        return

    name = u.name or "User"

    if lang == "hi":
        text = (
            f"🖐️ *हस्त रेखा विश्लेषण — {name}*\n\n"
            f"🔮 *वैदिक हस्त रेखा पाठ:*\n\n"
            f"{reading}\n\n"
            f"_आपकी हथेली आपके कर्म का नक्शा है।_"
        )
    else:
        text = (
            f"🖐️ *Palm Reading — {name}*\n\n"
            f"🔮 *Vedic Hast Rekha Analysis:*\n\n"
            f"{reading}\n\n"
            f"_Your palm is a map of your karma. Consult a qualified palmist for detailed guidance._"
        )

    await message.answer(text, parse_mode="Markdown")


@router.message(PalmState.waiting_for_photo)
async def process_palm_not_photo(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if lang == "hi":
        remind_text = (
            "📸 कृपया अपनी हथेली की एक फोटो भेजें। "
            "टेक्स्ट नहीं, फोटो चाहिए।"
        )
    else:
        remind_text = (
            "📸 Please send a photo of your palm. "
            "I need an image, not text."
        )

    await message.answer(remind_text)
