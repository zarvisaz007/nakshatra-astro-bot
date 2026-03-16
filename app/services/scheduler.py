import asyncio
import logging
from datetime import datetime, timezone, date

from aiogram import Bot
from sqlalchemy import select

from app.database import AsyncSessionFactory
from app.models.user import User
from app.services.astrology import get_nakshatra, NAKSHATRAS
from app.services.horoscope import get_reading, _call_ai
from app.services.cache import get_redis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Nakshatra brief meanings
# ---------------------------------------------------------------------------

NAK_MEANINGS = {
    "Ashwini": "New beginnings, healing, swift action",
    "Bharani": "Transformation, responsibility, karma",
    "Krittika": "Purification, courage, sharp focus",
    "Rohini": "Abundance, creativity, material growth",
    "Mrigashira": "Searching, curiosity, travel",
    "Ardra": "Storm before calm, research, deep change",
    "Punarvasu": "Renewal, optimism, returning home",
    "Pushya": "Nourishment, prosperity, spiritual growth",
    "Ashlesha": "Deep perception, kundalini, hidden forces",
    "Magha": "Ancestors, royalty, leadership",
    "Purva Phalguni": "Joy, creativity, romance",
    "Uttara Phalguni": "Service, contracts, long-term bonds",
    "Hasta": "Skill, craftsmanship, manifestation",
    "Chitra": "Beauty, art, brilliant mind",
    "Swati": "Independence, flexibility, trade",
    "Vishakha": "Goal-oriented, patience, purpose",
    "Anuradha": "Devotion, friendship, occult",
    "Jyeshtha": "Power, protection, courage",
    "Moola": "Root causes, liberation, extremes",
    "Purva Ashadha": "Invincibility, purification, victory",
    "Uttara Ashadha": "Final victory, universal principles",
    "Shravana": "Listening, learning, connection",
    "Dhanishtha": "Wealth, music, Mars energy",
    "Shatabhisha": "Healing, research, solitude",
    "Purva Bhadrapada": "Fire, passion, transformation",
    "Uttara Bhadrapada": "Depth, rain, Shiva energy",
    "Revati": "Completion, nourishment, safe journey",
}

# ---------------------------------------------------------------------------
# Festival list for 2026
# ---------------------------------------------------------------------------

FESTIVALS_2026 = [
    ("2026-01-14", "Makar Sankranti", "☀️ Sun enters Capricorn — harvest festival"),
    ("2026-01-26", "Republic Day", "🇮🇳 Republic Day blessings"),
    ("2026-02-17", "Maha Shivratri", "🔱 The great night of Lord Shiva"),
    ("2026-03-14", "Holi", "🌈 Festival of colors and spring"),
    ("2026-03-30", "Ram Navami", "🙏 Birthday of Lord Ram"),
    ("2026-04-14", "Baisakhi", "🌾 Harvest festival"),
    ("2026-08-15", "Independence Day", "🇮🇳 Independence Day blessings"),
    ("2026-08-26", "Janmashtami", "🦚 Birthday of Lord Krishna"),
    ("2026-09-14", "Ganesh Chaturthi", "🐘 Festival of Lord Ganesha"),
    ("2026-10-02", "Navratri begins", "🌺 Nine nights of the Divine Mother"),
    ("2026-10-11", "Dussehra", "🏹 Victory of good over evil"),
    ("2026-10-20", "Diwali", "🪔 Festival of lights"),
    ("2026-11-08", "Chhath Puja", "☀️ Sun worship festival"),
    # Ekadashi — roughly every 15 days, 11th lunar day
    ("2026-01-11", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-01-26", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-02-09", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-02-24", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-03-11", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-03-25", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-04-09", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
    ("2026-04-24", "Ekadashi", "🌙 Auspicious fasting day — Ekadashi"),
]


# ---------------------------------------------------------------------------
# DB helper
# ---------------------------------------------------------------------------

async def _get_notification_users() -> list:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).where(
                User.notifications_enabled == True,  # noqa: E712
                User.birth_lat.is_not(None),
            )
        )
        return result.scalars().all()


# ---------------------------------------------------------------------------
# Daily horoscope push — 01:30 UTC (7:00 AM IST)
# ---------------------------------------------------------------------------

async def _check_daily_horoscope(bot: Bot, now: datetime) -> None:
    if not (now.hour == 1 and now.minute < 30):
        return

    today = now.date()
    users = await _get_notification_users()
    if not users:
        return

    logger.info("Sending daily horoscope push to %d users", len(users))
    redis = get_redis()

    from app.services.astrology import get_kundli, get_sun_sign

    for user in users:
        user_id = user.telegram_id
        redis_key = f"sched:sent:daily_horo:{user_id}:{today.isoformat()}"
        already_sent = await redis.get(redis_key)
        if already_sent:
            continue

        try:
            kundli = get_kundli(
                user.birth_date,
                user.birth_lat,
                user.birth_lon,
                user.birth_time,
                user.timezone or "UTC",
            )
            sign = get_sun_sign(user.birth_date)
            rashi = kundli["rashi"]
            moon_sign = kundli["rashi"]
            nakshatra = kundli["nakshatra"]
            lang = user.language or "en"

            reading = await get_reading(sign, rashi, moon_sign, nakshatra, today, lang)
            if not reading:
                continue

            text = f"🌅 *Your Daily Horoscope — {today.strftime('%d %B %Y')}*\n\n{reading}"
            await bot.send_message(user_id, text, parse_mode="Markdown")

            # Mark as sent with TTL of 26 hours to prevent double-send
            await redis.setex(redis_key, 93600, "1")
        except Exception:
            logger.exception("Daily horoscope push failed for user %s", user_id)


# ---------------------------------------------------------------------------
# Transit alert — Moon nakshatra change
# ---------------------------------------------------------------------------

async def _check_transit_alert(bot: Bot, now: datetime) -> None:
    from kerykeion import AstrologicalSubject

    try:
        s = AstrologicalSubject(
            name="transit",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=12,
            minute=0,
            lat=0.0,
            lng=0.0,
            tz_str="UTC",
            zodiac_type="Sidereal",
            sidereal_mode="LAHIRI",
            online=False,
        )
        moon_pos = s.moon.abs_pos
    except Exception:
        logger.exception("Transit: failed to get moon position")
        return

    current_nak, current_lord, _ = get_nakshatra(moon_pos)

    redis = get_redis()
    last_nak = await redis.get("sched:transit:moon_nak")

    if last_nak == current_nak:
        return

    # Nakshatra has changed — update Redis and alert users
    await redis.set("sched:transit:moon_nak", current_nak)

    if last_nak is None:
        # First run — just record, don't alert
        logger.info("Transit: initialized moon nakshatra to %s", current_nak)
        return

    logger.info("Transit: Moon moved from %s to %s", last_nak, current_nak)

    meaning = NAK_MEANINGS.get(current_nak, "")
    text = (
        f"🌙 Moon has entered *{current_nak}* nakshatra (Lord: {current_lord})\n\n"
        f"{meaning}"
    )

    users = await _get_notification_users()
    for user in users:
        try:
            await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
        except Exception:
            logger.exception("Transit alert failed for user %s", user.telegram_id)


# ---------------------------------------------------------------------------
# Festival reminders — 1 day before, at 06:00 UTC
# ---------------------------------------------------------------------------

async def _check_festivals(bot: Bot, now: datetime) -> None:
    if now.hour != 6:
        return

    tomorrow = (now.date().replace(day=now.day) if False else None)
    from datetime import timedelta
    tomorrow = now.date() + timedelta(days=1)

    redis = get_redis()

    upcoming = [
        (festival_date, name, desc)
        for festival_date, name, desc in FESTIVALS_2026
        if festival_date == tomorrow.isoformat()
    ]

    if not upcoming:
        return

    users = await _get_notification_users()

    for festival_date, name, desc in upcoming:
        year = tomorrow.year
        redis_key = f"sched:sent:festival:{name.replace(' ', '_')}:{year}"
        already_sent = await redis.get(redis_key)
        if already_sent:
            continue

        text = (
            f"🌺 *{name} Tomorrow!*\n\n"
            f"{desc}\n\n"
            f"May this auspicious time bring you peace, prosperity, and divine blessings. 🙏\n\n"
            f"_Nakshatra Astro_"
        )

        logger.info("Sending festival reminder: %s to %d users", name, len(users))
        for user in users:
            try:
                await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
            except Exception:
                logger.exception("Festival reminder failed for user %s", user.telegram_id)

        # Mark sent — TTL 30 days
        await redis.setex(redis_key, 2592000, "1")


# ---------------------------------------------------------------------------
# Weekly digest — every Monday at 05:00 UTC
# ---------------------------------------------------------------------------

async def _check_weekly_digest(bot: Bot, now: datetime) -> None:
    # Monday = weekday 0, at 05:00 UTC
    if now.weekday() != 0 or now.hour != 5:
        return

    today = now.date()
    week_num = today.isocalendar()[1]
    year = today.year
    redis_key = f"sched:sent:weekly:{year}:week{week_num}"

    redis = get_redis()
    already_sent = await redis.get(redis_key)
    if already_sent:
        return

    users = await _get_notification_users()
    if not users:
        return

    logger.info("Generating weekly digest for week %d/%d", week_num, year)

    prompt = (
        f"Weekly Vedic astrology digest for week of {today.strftime('%B %d, %Y')}. "
        "Key planetary transits, auspicious days, days to avoid, spiritual focus for the week. "
        "~150 words. Practical and uplifting."
    )

    try:
        ai_weekly = await _call_ai(prompt)
    except Exception:
        logger.exception("Weekly digest AI call failed")
        return

    if not ai_weekly:
        return

    text = (
        f"🗓️ *Weekly Cosmic Digest — Week of {today.strftime('%B %d, %Y')}*\n\n"
        f"{ai_weekly}\n\n"
        f"_Your weekly guide from Nakshatra Astro_ 🌟"
    )

    for user in users:
        try:
            await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
        except Exception:
            logger.exception("Weekly digest failed for user %s", user.telegram_id)

    # Mark sent — TTL 8 days
    await redis.setex(redis_key, 691200, "1")


# ---------------------------------------------------------------------------
# Main scheduler loop
# ---------------------------------------------------------------------------

async def run_scheduler(bot: Bot) -> None:
    """Main scheduler loop. Run as background asyncio task."""
    logger.info("Scheduler started")
    while True:
        try:
            now = datetime.now(timezone.utc)
            await _check_daily_horoscope(bot, now)
            await _check_transit_alert(bot, now)
            await _check_festivals(bot, now)
            await _check_weekly_digest(bot, now)
        except Exception:
            logger.exception("Scheduler error")
        # Check every 30 minutes
        await asyncio.sleep(1800)
