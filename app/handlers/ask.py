import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services import horoscope as horo_service
from app.services.astrology import get_kundli

logger = logging.getLogger(__name__)
router = Router()


class AskState(StatesGroup):
    waiting_question = State()


@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    if u.questions_remaining == 0:
        await message.answer(t(lang, "ask_limit"), parse_mode="Markdown")
        return

    await message.answer(
        t(lang, "ask_prompt", remaining=u.questions_remaining),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    await state.set_state(AskState.waiting_question)


@router.message(AskState.waiting_question)
async def handle_question(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    lang = u.language or "en"

    if u.questions_remaining == 0:
        await state.clear()
        await message.answer(t(lang, "ask_limit"), parse_mode="Markdown")
        return

    await message.answer(t(lang, "ask_wait"))

    try:
        kundli = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        answer = await horo_service.ask_ai(
            question=message.text.strip(),
            name=u.name or "User",
            lagna=kundli["lagna"],
            rashi=kundli["rashi"],
            nakshatra=kundli["nakshatra"],
            dasha=kundli["current_dasha"],
            lang=lang,
        )
    except Exception:
        logger.exception("Ask AI error for user %s", u.telegram_id)
        await state.clear()
        await message.answer(t(lang, "ai_error"))
        return

    # Deduct question
    async with AsyncSessionFactory() as session:
        u = await user_service.increment_questions(session, u.telegram_id)

    remaining = u.questions_remaining
    footer = f"\n\n_({remaining} free questions remaining)_" if lang == "en" else f"\n\n_({remaining} मुफ़्त प्रश्न शेष)_"

    await state.clear()
    await message.answer("🔮 " + answer + (footer if remaining >= 0 else ""), parse_mode="Markdown")
