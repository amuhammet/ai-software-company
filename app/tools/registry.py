from __future__ import annotations

from typing import Any, Dict, List


class ToolRegistry:
    """Stores tools available to the platform."""

    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, tool: Any) -> Any:
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Any:
        return self._tools.get(name)

    def list(self) -> List[str]:
        return list(self._tools.keys())


__all__ = ["ToolRegistry"]
