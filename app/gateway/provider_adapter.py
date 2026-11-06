from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    import litellm
except ImportError:  # pragma: no cover
    litellm = None


class LLMProviderAdapter:
    """Unified gateway wrapper for LLM providers."""

    def __init__(self) -> None:
        if litellm is not None:
            litellm.drop_params = True

    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        fallbacks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if litellm is not None:
            try:
                response = litellm.completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    fallbacks=fallbacks or [],
                )
                cost = litellm.completion_cost(completion_response=response)
                return {
                    "content": response.choices[0].message.content,
                    "model_used": response.model,
                    "cost_usd": cost,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                }
            except Exception:
                pass

        prompt_text = " ".join(message.get("content", "") for message in messages if message.get("content"))
        return {
            "content": (
                "LLM provider is not configured in this local environment. "
                "Set an API key or Ollama endpoint to enable model routing. "
                f"Request preview: {prompt_text[:200]}"
            ),
            "model_used": model,
            "cost_usd": 0.0,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }


__all__ = ["LLMProviderAdapter"]
