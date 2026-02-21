from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Gemini API key (https://aistudio.google.com/apikey)
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    # Gemini model name
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")
    environment: str = "development"
    memory_backend: str = "memory"
    database_url: str = "sqlite+aiosqlite:///./solos_memory.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
