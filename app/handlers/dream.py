import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database import AsyncSessionFactory
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.dream_service import interpret_dream

logger = logging.getLogger(__name__)
router = Router()

# ── Inline UI strings ──────────────────────────────────────────────────────────

_PROMPT_MSG = {
    "en": (
        "🌙 Please describe your dream in detail. "
        "What did you see, feel, and experience?"
    ),
    "hi": (
        "🌙 कृपया अपना स्वप्न विस्तार से बताएं। "
        "आपने क्या देखा, महसूस किया और अनुभव किया?"
    ),
}

_NO_PROFILE = {
    "en": "⚠️ Please complete your profile first with /start.",
    "hi": "⚠️ कृपया पहले /start से अपना प्रोफ़ाइल पूरा करें।",
}

_TOO_SHORT = {
    "en": "🌙 Please describe your dream in more detail (at least 10 characters).",
    "hi": "🌙 कृपया अपना स्वप्न और विस्तार से बताएं (कम से कम 10 अक्षर)।",
}

_WAIT_MSG = {
    "en": "🔮 Reading the cosmic messages in your dream...",
    "hi": "🔮 आपके स्वप्न में ब्रह्मांडीय संदेश पढ़े जा रहे हैं...",
}

_ERROR_MSG = {
    "en": "❌ Something went wrong. Please try again later.",
    "hi": "❌ कुछ गड़बड़ हो गई। कृपया बाद में पुनः प्रयास करें।",
}

_RESULT_EN = (
    "🌙 *Dream Interpretation — {name}*\n\n"
    "*Your Dream:* _{dream_summary}_\n\n"
    "🔮 *Vedic Analysis:*\n"
    "{ai_reading}\n\n"
    "_Dreams are messages from the cosmos. Reflect on this wisdom._"
)

_RESULT_HI = (
    "🌙 *स्वप्न विश्लेषण — {name}*\n\n"
    "*आपका स्वप्न:* _{dream_summary}_\n\n"
    "🔮 *वैदिक विश्लेषण:*\n"
    "{ai_reading}\n\n"
    "_स्वप्न ब्रह्मांड के संदेश हैं। इस ज्ञान पर विचार करें।_"
)


# ── FSM States ─────────────────────────────────────────────────────────────────

class DreamState(StatesGroup):
    waiting_for_dream = State()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _summarise(text: str) -> str:
    """Return first 100 chars of dream text with ellipsis if truncated."""
    text = text.strip()
    if len(text) <= 100:
        return text
    return text[:100] + "..."


# ── Handlers ───────────────────────────────────────────────────────────────────

@router.message(Command("dream"))
async def cmd_dream(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(_NO_PROFILE[lang])
        return

    await message.answer(_PROMPT_MSG[lang], parse_mode="Markdown")
    await state.set_state(DreamState.waiting_for_dream)


@router.message(DreamState.waiting_for_dream)
async def process_dream(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"
    dream_text = (message.text or "").strip()

    # Reject empty or very short descriptions — ask again (keep state)
    if len(dream_text) < 10:
        await message.answer(_TOO_SHORT[lang], parse_mode="Markdown")
        return

    # Clear state before async work so a crash doesn't trap the user
    await state.clear()

    await message.answer(_WAIT_MSG[lang])

    try:
        kundli = get_kundli(
            u.birth_date,
            u.birth_lat,
            u.birth_lon,
            u.birth_time,
            u.timezone or "UTC",
        )

        ai_reading = await interpret_dream(
            dream=dream_text,
            name=u.name or "Friend",
            moon_sign=kundli["rashi"],
            nakshatra=kundli["nakshatra"],
            dasha=kundli["current_dasha"],
            lang=lang,
        )
    except Exception:
        logger.exception("Dream interpretation error for user %s", message.from_user.id)
        await message.answer(_ERROR_MSG[lang])
        return

    template = _RESULT_HI if lang == "hi" else _RESULT_EN
    reply = template.format(
        name=u.name or "Friend",
        dream_summary=_summarise(dream_text),
        ai_reading=ai_reading,
    )

    await message.answer(reply, parse_mode="Markdown")
