from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # App
    APP_NAME: str = "Fintech Platform"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Frontend
    FRONTEND_URLS: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()