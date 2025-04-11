from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"

    # Настройки API
    API_PREFIX: str = "/api/v1"
    APP_TITLE: str = "Feast API - Бронирование столиков"
    APP_DESCRIPTION: str = (
        "API для управления столиками и их бронированием в ресторане."
    )
    APP_VERSION: str = "1.0.0"

    # Настройки Uvicorn (можно переопределить через .env или переменные окружения)
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
