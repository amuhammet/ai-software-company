from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "ai-software-company")
    model_provider: str = os.getenv("MODEL_PROVIDER", "ollama")
    model_name: str = os.getenv("MODEL_NAME", "llama3:70b")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    chroma_path: str = os.getenv("CHROMA_PATH", "./.chroma")
    sandbox_mode: str = os.getenv("SANDBOX_MODE", "docker")


settings = Settings()
