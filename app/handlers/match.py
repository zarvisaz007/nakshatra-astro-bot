import asyncio
import logging
from datetime import date, time

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from dateutil import parser as dateparser
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from app.database import AsyncSessionFactory
from app.i18n import t
from app.services import user as user_service
from app.services.astrology import get_kundli
from app.services.vedic import guna_milan
from app.services import horoscope as horo_service

logger = logging.getLogger(__name__)
router = Router()

_geocoder = Nominatim(user_agent="nakshatra-astro-bot-match")
_tzfinder = TimezoneFinder()


class MatchState(StatesGroup):
    partner_name = State()
    partner_dob = State()
    partner_city = State()


async def _geocode(city: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _geocoder.geocode(city, exactly_one=True))


@router.message(Command("match"))
async def cmd_match(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    if not u.is_onboarded:
        await message.answer(t(lang, "no_profile"))
        return

    msg = "💑 *Kundli Matching*\n\nEnter your partner's name:" if lang == "en" else "💑 *कुंडली मिलान*\n\nसाथी का नाम बताएं:"
    await message.answer(msg, parse_mode="Markdown")
    await state.set_state(MatchState.partner_name)


@router.message(MatchState.partner_name)
async def match_partner_name(message: Message, state: FSMContext) -> None:
    await state.update_data(partner_name=message.text.strip())
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"
    msg = "Partner's date of birth? (e.g. 15 Mar 1992)" if lang == "en" else "साथी की जन्म तिथि? (जैसे 15 Mar 1992)"
    await message.answer(msg)
    await state.set_state(MatchState.partner_dob)


@router.message(MatchState.partner_dob)
async def match_partner_dob(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"
    try:
        dob = dateparser.parse(message.text.strip(), dayfirst=True, fuzzy=True).date()
    except Exception:
        await message.answer(t(lang, "bad_date"), parse_mode="Markdown")
        return
    await state.update_data(partner_dob=dob.isoformat())
    msg = "Partner's birth city?" if lang == "en" else "साथी का जन्म शहर?"
    await message.answer(msg)
    await state.set_state(MatchState.partner_city)


@router.message(MatchState.partner_city)
async def match_partner_city(message: Message, state: FSMContext) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
    lang = u.language or "en"

    location = await _geocode(message.text.strip())
    if not location:
        await message.answer(t(lang, "bad_city", city=message.text.strip()), parse_mode="Markdown")
        return

    data = await state.get_data()
    await state.clear()

    lat, lon = location.latitude, location.longitude
    tz_str = _tzfinder.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    partner_dob = date.fromisoformat(data["partner_dob"])
    partner_name = data["partner_name"]

    await message.answer(t(lang, "generating"), reply_markup=ReplyKeyboardRemove())

    try:
        k1 = get_kundli(u.birth_date, u.birth_lat, u.birth_lon, u.birth_time, u.timezone or "UTC")
        k2 = get_kundli(partner_dob, lat, lon, None, tz_str)
        result = guna_milan(k1["nakshatra"], k1["rashi"], k2["nakshatra"], k2["rashi"])

        # Score bar
        pct = result["score"] / 36
        filled = int(pct * 10)
        bar = "█" * filled + "░" * (10 - filled)

        lines = [
            f"💑 *Kundli Match: {u.name} × {partner_name}*" if lang == "en"
            else f"💑 *कुंडली मिलान: {u.name} × {partner_name}*",
            "",
            f"*Score: {result['score']}/36* [{bar}]",
            f"*{result['compatibility']}*",
            "",
            "*Guna Details:*" if lang == "en" else "*गुण विवरण:*",
        ]
        for guna, (got, max_) in result["details"].items():
            lines.append(f"  {guna}: {got}/{max_}")

        lines += [
            "",
            f"Your Nakshatra: *{k1['nakshatra']}* | Rashi: *{k1['rashi']}*",
            f"Partner Nakshatra: *{k2['nakshatra']}* | Rashi: *{k2['rashi']}*",
        ]

        # Manglik check
        from app.services.vedic import detect_doshas
        d1 = detect_doshas(k1)
        d2 = detect_doshas(k2)
        m1 = d1["Manglik"]["present"]
        m2 = d2["Manglik"]["present"]
        if m1 or m2:
            lines.append("")
            if m1 and m2:
                lines.append("⚖️ Both Manglik — doshas cancel out. ✓")
            elif m1:
                lines.append(f"⚠️ {u.name} is Manglik. Partner should also be Manglik or seek remedy.")
            else:
                lines.append(f"⚠️ {partner_name} is Manglik. {u.name} should also be Manglik or seek remedy.")

        await message.answer("\n".join(lines), parse_mode="Markdown")

    except Exception:
        logger.exception("Match error")
        await message.answer(t(lang, "ai_error"))
