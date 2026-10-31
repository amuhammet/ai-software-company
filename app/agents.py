from __future__ import annotations

from typing import Any, Dict

try:
    import ollama  # type: ignore
except Exception:  # pragma: no cover
    ollama = None


class LocalLLM:
    def __init__(self, model_name: str = "llama3") -> None:
        self.model_name = model_name

    def invoke(self, prompt: str) -> str:
        return f"[{self.model_name}] Generated response for: {prompt[:180]}"


class ModelRouter:
    """Routes different tasks to different model families."""

    def __init__(self) -> None:
        self.models: Dict[str, Any] = {
            "reasoning": self._build_model("llama3"),
            "coding": self._build_model("deepseek-coder"),
            "review": self._build_model("llama3"),
        }

    def _build_model(self, model_name: str) -> Any:
        if ollama is not None:
            try:
                return ollama.Client().generate(model=model_name, prompt="hello")
            except Exception:
                pass
        return LocalLLM(model_name=model_name)

    def get_model(self, node_name: str) -> Any:
        if node_name in {"developer", "coding"}:
            return self.models["coding"]
        if node_name in {"qa", "validator", "review"}:
            return self.models["review"]
        return self.models["reasoning"]


router = ModelRouter()

__all__ = ["ModelRouter", "router", "LocalLLM"]
