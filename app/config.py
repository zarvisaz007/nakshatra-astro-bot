from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_model: str = "thudm/glm-4.5-air:free"
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite+aiosqlite:///./astro.db"


settings = Settings()
