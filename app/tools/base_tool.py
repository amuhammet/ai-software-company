from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool contract"

    @abstractmethod
    def run(self, arguments: Dict[str, Any]) -> str:
        """Return a serialized result or plain text output."""
        raise NotImplementedError


__all__ = ["BaseTool"]
