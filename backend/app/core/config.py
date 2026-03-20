from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    frontend_urls: str

    class Config:
        env_file = ".env"


settings = Settings()