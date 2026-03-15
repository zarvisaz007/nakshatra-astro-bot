from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    anthropic_api_key: str
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite+aiosqlite:///./astro.db"


settings = Settings()
