from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.gateway.provider_adapter import LLMProviderAdapter


class LLMGatewayRouter:
    """Simple policy-based routing layer for tasks and providers."""

    PROVIDER_MAP = {
        "reasoning": ["openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet", "ollama/llama3"],
        "coding": ["openai/gpt-4o-mini", "ollama/codellama", "anthropic/claude-3-5-sonnet"],
        "qa": ["openai/gpt-4o-mini", "ollama/llama3"],
    }

    def __init__(self, provider_adapter: Optional[Any] = None) -> None:
        self.provider_adapter = provider_adapter or LLMProviderAdapter()

    def route_model(self, task_type: str, preferred_model: Optional[str] = None) -> str:
        if preferred_model:
            return preferred_model

        candidates = self.PROVIDER_MAP.get(task_type, [settings.default_model])
        if not candidates:
            return settings.default_model
        return candidates[0]

    def dispatch(
        self,
        task_type: str,
        messages: List[Dict[str, str]],
        preferred_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        model = self.route_model(task_type, preferred_model)
        return self.provider_adapter.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            fallbacks=[],
        )


__all__ = ["LLMGatewayRouter"]
