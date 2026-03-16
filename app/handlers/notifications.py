import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.database import AsyncSessionFactory
from app.services import user as user_service

logger = logging.getLogger(__name__)
router = Router()


def _notif_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    if enabled:
        label = "🔔 Turn OFF Notifications"
    else:
        label = "🔕 Turn ON Notifications"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data="notif_toggle")]]
    )


def _status_text(enabled: bool) -> str:
    if enabled:
        return (
            "🔔 *Notifications are ON*\n\n"
            "You'll receive:\n"
            "• Daily horoscope at 7:00 AM IST\n"
            "• Moon transit alerts\n"
            "• Festival & Ekadashi reminders\n"
            "• Weekly cosmic digest every Monday\n\n"
            "Tap below to turn them off."
        )
    return (
        "🔕 *Notifications are OFF*\n\n"
        "You are not receiving any scheduled updates.\n\n"
        "Tap below to turn them on and get daily horoscopes, "
        "transit alerts, festival reminders, and weekly digests."
    )


@router.message(Command("notifications"))
async def cmd_notifications(message: Message) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, message.from_user.id)
        enabled = u.notifications_enabled

    await message.answer(
        _status_text(enabled),
        reply_markup=_notif_keyboard(enabled),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "notif_toggle")
async def toggle_notifications(callback: CallbackQuery) -> None:
    async with AsyncSessionFactory() as session:
        u = await user_service.get_or_create(session, callback.from_user.id)
        u.notifications_enabled = not u.notifications_enabled
        new_state = u.notifications_enabled
        await session.commit()

    logger.info(
        "User %s toggled notifications to %s",
        callback.from_user.id,
        "ON" if new_state else "OFF",
    )

    await callback.message.edit_text(
        _status_text(new_state),
        reply_markup=_notif_keyboard(new_state),
        parse_mode="Markdown",
    )
    await callback.answer(
        "Notifications turned ON ✅" if new_state else "Notifications turned OFF 🔕"
    )
