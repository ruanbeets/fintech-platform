from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    frontend_urls: str = "http://localhost:5173,http://127.0.0.1:5173"
    local_demo: bool = False
    demo_mode: bool = False
    cors_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    session_hours: int = 24

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
