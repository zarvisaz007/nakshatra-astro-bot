import asyncio
import logging
from datetime import date, time

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from dateutil import parser as dateparser
from geopy.geocoders import Nominatim

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service

logger = logging.getLogger(__name__)
router = Router()

_geocoder = Nominatim(user_agent="nakshatra-astrology-bot")


class Onboarding(StatesGroup):
    birth_date = State()
    birth_time = State()
    birth_location = State()


def _lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        InlineKeyboardButton(text="🇮🇳 हिंदी", callback_data="lang:hi"),
    ]])


def _skip_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "skip"))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def _geocode(city: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _geocoder.geocode(city, exactly_one=True))


def _parse_date(text: str) -> date | None:
    try:
        return dateparser.parse(text, dayfirst=True, fuzzy=True).date()
    except Exception:
        return None


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        t("en", "choose_lang"),
        reply_markup=_lang_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def cb_language(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split(":")[1]
    await state.update_data(lang=lang)

    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, callback.from_user.id)
        u.language = lang
        await session.commit()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    if u.is_onboarded:
        await callback.message.answer(t(lang, "welcome_back"), reply_markup=ReplyKeyboardRemove())
        return

    await callback.message.answer(t(lang, "welcome_new"), reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await state.set_state(Onboarding.birth_date)


@router.message(Onboarding.birth_date)
async def onboarding_birth_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")

    birth_date = _parse_date(message.text.strip())
    if birth_date is None:
        await message.answer(t(lang, "bad_date"), parse_mode="Markdown")
        return

    await state.update_data(birth_date=birth_date.isoformat())
    await message.answer(
        t(lang, "got_date", date=birth_date.strftime("%B %d, %Y")),
        reply_markup=_skip_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(Onboarding.birth_time)


@router.message(Onboarding.birth_time)
async def onboarding_birth_time(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    text = message.text.strip()
    birth_time = None

    if text.lower() not in ("skip", t(lang, "skip").lower()):
        try:
            h, m = text.split(":")
            birth_time = time(int(h), int(m))
        except (ValueError, TypeError):
            await message.answer(t(lang, "bad_time"), parse_mode="Markdown")
            return

    await state.update_data(birth_time=birth_time.isoformat() if birth_time else None)
    key = "got_time" if birth_time else "skip_time"
    await message.answer(t(lang, key), reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await state.set_state(Onboarding.birth_location)


@router.message(Onboarding.birth_location)
async def onboarding_birth_location(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    city = message.text.strip()

    location = await _geocode(city)
    if location is None:
        await message.answer(t(lang, "bad_city", city=city), parse_mode="Markdown")
        return

    birth_date = date.fromisoformat(data["birth_date"])
    birth_time_str = data.get("birth_time")
    birth_time = time.fromisoformat(birth_time_str) if birth_time_str else None
    city_name = location.address.split(",")[0]

    async with AsyncSessionFactory() as session:
        await user_service.update_birth_data(
            session=session,
            telegram_id=message.from_user.id,
            birth_date=birth_date,
            birth_lat=location.latitude,
            birth_lon=location.longitude,
            city_name=city_name,
            birth_time=birth_time,
        )

    await state.clear()
    await message.answer(
        t(lang, "onboard_done",
          date=birth_date.strftime("%B %d, %Y"),
          time=f" at {birth_time.strftime('%H:%M')}" if birth_time else "",
          city=city_name),
        parse_mode="Markdown",
    )
