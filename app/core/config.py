from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load environment variables; switch `LLM_BASE_URL` between Ollama and cloud."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_base_url: str = Field(
        default="http://127.0.0.1:11434/v1",
        validation_alias="LLM_BASE_URL",
        description="OpenAI-compatible API base URL (include /v1)",
    )
    openai_api_key: str = Field(
        default="",
        validation_alias="OPENAI_API_KEY",
        description="Required for cloud; optional for local Ollama",
    )
    llm_model: str = Field(
        default="llama3.2:1b",
        validation_alias="LLM_MODEL",
        description="Model name (Ollama tag or cloud model id)",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
