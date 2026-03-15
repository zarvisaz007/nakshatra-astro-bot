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
    birth_date: date,
    birth_lat: float,
    birth_lon: float,
    city_name: str,
    birth_time: time | None = None,
) -> User:
    user = await get_or_create(session, telegram_id)
    user.birth_date = birth_date
    user.birth_lat = birth_lat
    user.birth_lon = birth_lon
    user.city_name = city_name
    user.birth_time = birth_time
    await session.commit()
    await session.refresh(user)
    return user
