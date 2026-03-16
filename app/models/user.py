from datetime import date, datetime, time

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(5), server_default="en")
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)  # male/female/other
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    free_questions_used: Mapped[int] = mapped_column(Integer, server_default="0")
    subscription_tier: Mapped[str] = mapped_column(String(20), server_default="free")  # free/basic/premium/elite
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    FREE_QUESTION_LIMIT = 3

    @property
    def is_onboarded(self) -> bool:
        return self.birth_date is not None and self.birth_lat is not None

    @property
    def questions_remaining(self) -> int:
        if self.subscription_tier != "free":
            return 999
        return max(0, self.FREE_QUESTION_LIMIT - (self.free_questions_used or 0))
