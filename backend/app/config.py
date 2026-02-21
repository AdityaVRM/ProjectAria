from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cursor_composer_api_key: str = Field(default="", validation_alias="CURSOR_COMPOSER_1_5_API_KEY")
    environment: str = "development"
    memory_backend: str = "memory"
    database_url: str = "sqlite+aiosqlite:///./solos_memory.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
