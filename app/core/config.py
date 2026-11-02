import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppSettings:
    app_name: str = "ai-software-company"
    environment: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("APP_SECRET_KEY", "dev-secret-key-change-me")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    default_model: str = os.getenv("DEFAULT_MODEL", "ollama/llama3")
    budget_default_usd: float = float(os.getenv("DEFAULT_ORG_BUDGET_USD", "100.0"))
    allowed_providers: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.allowed_providers is None:
            self.allowed_providers = [
                provider.strip()
                for provider in os.getenv("ALLOWED_PROVIDERS", "ollama,openai,anthropic,gemini,azure").split(",")
                if provider.strip()
            ]


settings = AppSettings()


__all__ = ["settings", "AppSettings"]
