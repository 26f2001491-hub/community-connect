from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    DB_ECHO: bool = False
    TWILIO_ACCOUNT_SID: str = "AC65f7b5a75f90c85e7f9a16205c9b1a6d"
    TWILIO_AUTH_TOKEN: str = "1703973fe7d08e1db6bb74a3d4b89266"
    TWILIO_VERIFY_SID: str = "VA324ece2ab74b1a4ddfb02c3bee2f0d07"


settings = Settings()