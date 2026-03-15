import logging
from datetime import date, time

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from geopy.geocoders import Nominatim

from app.database import AsyncSessionFactory
from app.services import user as user_service

logger = logging.getLogger(__name__)
router = Router()

_geocoder = Nominatim(user_agent="astrology-bot")


class Onboarding(StatesGroup):
    birth_date = State()
    birth_time = State()
    birth_location = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)

    if u.is_onboarded:
        await message.answer(
            f"Welcome back! ✨\n\nYour profile is set — try /horoscope or /chart.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await message.answer(
        "Welcome to your personal astrology bot! 🌟\n\n"
        "To get started, I need your birth information.\n\n"
        "What's your birth date? (format: DD/MM/YYYY)\n"
        "Example: 15/03/1990"
    )
    await state.set_state(Onboarding.birth_date)


@router.message(Onboarding.birth_date)
async def onboarding_birth_date(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    try:
        birth_date = date(*reversed([int(p) for p in text.split("/")]))
    except (ValueError, TypeError):
        await message.answer("Couldn't parse that date. Please use DD/MM/YYYY — e.g. 15/03/1990")
        return

    await state.update_data(birth_date=birth_date.isoformat())

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Skip")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        f"Great! Born on {birth_date.strftime('%B %d, %Y')} ✓\n\n"
        "What time were you born? (format: HH:MM, 24h)\n"
        "Example: 14:30\n\n"
        "If you don't know, tap Skip — your rising sign won't be accurate.",
        reply_markup=kb,
    )
    await state.set_state(Onboarding.birth_time)


@router.message(Onboarding.birth_time)
async def onboarding_birth_time(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    birth_time = None

    if text.lower() != "skip":
        try:
            h, m = text.split(":")
            birth_time = time(int(h), int(m))
        except (ValueError, TypeError):
            await message.answer("Couldn't parse that. Use HH:MM (e.g. 14:30) or tap Skip.")
            return

    await state.update_data(birth_time=birth_time.isoformat() if birth_time else None)

    await message.answer(
        "Almost done! 🌍\n\nWhat city were you born in?\n"
        "Example: London, Paris, New York",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Onboarding.birth_location)


@router.message(Onboarding.birth_location)
async def onboarding_birth_location(message: Message, state: FSMContext) -> None:
    city = message.text.strip()

    location = await _geocoder.geocode(city, exactly_one=True)
    if location is None:
        await message.answer(f"Couldn't find '{city}'. Try a different spelling or nearby city.")
        return

    data = await state.get_data()
    birth_date = date.fromisoformat(data["birth_date"])
    birth_time_str = data.get("birth_time")
    birth_time = time.fromisoformat(birth_time_str) if birth_time_str else None

    async with AsyncSessionFactory() as session:
        await user_service.update_birth_data(
            session=session,
            telegram_id=message.from_user.id,
            birth_date=birth_date,
            birth_lat=location.latitude,
            birth_lon=location.longitude,
            city_name=location.address.split(",")[0],
            birth_time=birth_time,
        )

    await state.clear()
    await message.answer(
        f"All set! 🎉\n\n"
        f"📅 Born: {birth_date.strftime('%B %d, %Y')}"
        + (f" at {birth_time.strftime('%H:%M')}" if birth_time else "")
        + f"\n📍 {location.address.split(',')[0]}\n\n"
        "Try /horoscope for today's reading or /chart for your natal chart."
    )
