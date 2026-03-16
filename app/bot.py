import asyncio
import logging
from datetime import date
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, Message

from app.config import settings
from app.database import create_tables
from app.handlers import start, horoscope, chart, sign, panchang, ask, spiritual
from app.handlers import match, dosha, remedy, lucky
from app.handlers import career, marriage, wealth, dasha
from app.handlers import puja, mantra, gems
from app.handlers import numerology, dream, palm, notifications
from app.handlers import reportcard, sharecard, milestones
from app.services.scheduler import run_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class StatsMiddleware(BaseMiddleware):
    """Track command usage + active users in Redis for admin dashboard."""
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message, data: Dict[str, Any]) -> Any:
        if event.text and event.text.startswith("/"):
            try:
                from app.services.cache import get_redis
                cmd = event.text.split()[0].lstrip("/").split("@")[0].lower()
                r = get_redis()
                today = date.today().isoformat()
                await r.incr(f"stats:cmd:{cmd}:{today}")
                await r.expire(f"stats:cmd:{cmd}:{today}", 86400 * 30)
                await r.incr(f"stats:cmd:{cmd}:total")
                await r.sadd(f"stats:users:active:{today}", event.from_user.id)
                await r.expire(f"stats:users:active:{today}", 86400 * 2)
            except Exception:
                pass
        return await handler(event, data)


async def main() -> None:
    await create_tables()
    logger.info("Database tables ready")

    storage = RedisStorage.from_url(settings.redis_url)
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=storage)
    dp.message.middleware(StatsMiddleware())

    dp.include_router(start.router)
    dp.include_router(horoscope.router)
    dp.include_router(chart.router)
    dp.include_router(sign.router)
    dp.include_router(panchang.router)
    dp.include_router(ask.router)
    dp.include_router(spiritual.router)
    dp.include_router(match.router)
    dp.include_router(dosha.router)
    dp.include_router(remedy.router)
    dp.include_router(lucky.router)
    dp.include_router(career.router)
    dp.include_router(marriage.router)
    dp.include_router(wealth.router)
    dp.include_router(dasha.router)
    dp.include_router(puja.router)
    dp.include_router(mantra.router)
    dp.include_router(gems.router)
    dp.include_router(numerology.router)
    dp.include_router(dream.router)
    dp.include_router(palm.router)
    dp.include_router(notifications.router)
    dp.include_router(reportcard.router)
    dp.include_router(sharecard.router)
    dp.include_router(milestones.router)

    await bot.set_my_commands([
        BotCommand(command="start",     description="🔄 Setup / Change language"),
        BotCommand(command="horoscope", description="🔮 Today's Vedic horoscope"),
        BotCommand(command="kundli",    description="🔯 Your birth chart"),
        BotCommand(command="panchang",  description="📅 Today's Panchang"),
        BotCommand(command="ask",       description="🙏 Ask astrology AI (3 free)"),
        BotCommand(command="match",     description="💑 Kundli matching"),
        BotCommand(command="dosha",     description="⚠️ Dosha analysis"),
        BotCommand(command="remedy",    description="🕉️ Personal remedies"),
        BotCommand(command="lucky",     description="🍀 Lucky numbers, colors, gems"),
        BotCommand(command="spiritual", description="🌸 Daily spiritual guidance"),
        BotCommand(command="sign",      description="♈ Zodiac sign info"),
        BotCommand(command="career",    description="💼 Career astrology"),
        BotCommand(command="marriage",  description="💑 Marriage prediction"),
        BotCommand(command="wealth",    description="💰 Wealth & finance astrology"),
        BotCommand(command="dasha",     description="🌀 Vimshottari Dasha timeline"),
        BotCommand(command="puja",      description="🕉️ Puja recommendations"),
        BotCommand(command="mantra",    description="🔱 Personal mantra sadhana"),
        BotCommand(command="gems",          description="💎 Gemstone recommendations"),
        BotCommand(command="numerology",    description="🔢 Vedic numerology reading"),
        BotCommand(command="dream",         description="🌙 Dream interpretation"),
        BotCommand(command="palmreading",   description="🖐️ Palm reading (send photo)"),
        BotCommand(command="notifications", description="🔔 Toggle daily notifications"),
        BotCommand(command="reportcard",    description="🔯 Your Destiny Report Card (shareable)"),
        BotCommand(command="sharecard",     description="💑 Compatibility card (shareable)"),
        BotCommand(command="milestones",    description="🌟 Life milestones & dasha forecast"),
    ])

    asyncio.create_task(run_scheduler(bot))
    logger.info("Scheduler started")

    logger.info("Starting bot @Nakshatra_Astrobot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
