from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_or_create(session: AsyncSession, telegram_id: int) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def update_birth_data(
    session: AsyncSession,
    telegram_id: int,
    name: str,
    birth_date: date,
    birth_lat: float,
    birth_lon: float,
    city_name: str,
    timezone: str,
    birth_time: time | None = None,
    gender: str | None = None,
) -> User:
    user = await get_or_create(session, telegram_id)
    user.name = name
    user.birth_date = birth_date
    user.birth_lat = birth_lat
    user.birth_lon = birth_lon
    user.city_name = city_name
    user.timezone = timezone
    user.birth_time = birth_time
    user.gender = gender
    await session.commit()
    await session.refresh(user)
    return user


async def increment_questions(session: AsyncSession, telegram_id: int) -> User:
    user = await get_or_create(session, telegram_id)
    user.free_questions_used = (user.free_questions_used or 0) + 1
    await session.commit()
    await session.refresh(user)
    return user
