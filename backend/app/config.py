from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Cursor API key (Cursor Dashboard → Integrations)
    cursor_api_key: str = Field(default="", validation_alias="CURSOR_COMPOSER_1_5_API_KEY")
    cursor_api_key_alt: str = Field(default="", validation_alias="CURSOR_API_KEY")
    # GitHub repo URL for Cloud Agents (must be accessible to your Cursor account)
    cursor_repo: str = Field(
        default="https://github.com/AdityaVRM/ProjectAria",
        validation_alias="CURSOR_REPO",
    )
    # Model for Cloud Agents (composer-1.5, claude-4.6-opus-high-thinking, gpt-5.3-codex-high, gpt-5.2-high)
    cursor_model: str = Field(default="composer-1.5", validation_alias="CURSOR_MODEL")
    environment: str = "development"
    memory_backend: str = "memory"
    database_url: str = "sqlite+aiosqlite:///./solos_memory.db"

    @model_validator(mode="after")
    def use_alt_cursor_key(self) -> "Settings":
        if not self.cursor_api_key and self.cursor_api_key_alt:
            object.__setattr__(self, "cursor_api_key", self.cursor_api_key_alt)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
