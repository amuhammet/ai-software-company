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
        if litellm is None:
            raise RuntimeError(
                "litellm is not installed. Add it to requirements.txt to enable provider routing."
            )

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
