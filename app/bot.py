import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from app.config import settings
from app.database import create_tables
from app.handlers import start, horoscope, chart, sign, panchang, ask, spiritual
from app.handlers import match, dosha, remedy, lucky
from app.handlers import career, marriage, wealth, dasha
from app.handlers import puja, mantra, gems

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await create_tables()
    logger.info("Database tables ready")

    storage = RedisStorage.from_url(settings.redis_url)
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=storage)

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
        BotCommand(command="gems",      description="💎 Gemstone recommendations"),
    ])

    logger.info("Starting bot @Nakshatra_Astrobot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
