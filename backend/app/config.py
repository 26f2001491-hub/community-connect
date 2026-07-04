# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str      # postgresql+asyncpg://user:pass@host:5432/dbname
    DB_ECHO: bool = False


settings = Settings()