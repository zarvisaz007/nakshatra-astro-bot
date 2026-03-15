from datetime import date, datetime, timezone

import redis.asyncio as aioredis

from app.config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _seconds_until_midnight_utc() -> int:
    now = datetime.now(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # advance to next midnight
    from datetime import timedelta
    midnight += timedelta(days=1)
    return int((midnight - now).total_seconds())


async def get_horoscope(sign: str, day: date) -> str | None:
    key = f"horoscope:{sign.lower()}:{day.isoformat()}"
    return await get_redis().get(key)


async def set_horoscope(sign: str, day: date, reading: str) -> None:
    key = f"horoscope:{sign.lower()}:{day.isoformat()}"
    ttl = _seconds_until_midnight_utc()
    await get_redis().setex(key, ttl, reading)
