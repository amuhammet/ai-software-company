from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTool(ABC):
    """Standardized tool contract for safe, policy-aware tool invocation."""

    name: str = "base_tool"
    description: str = "Base tool contract"
    required_permissions: List[str] = []
    allowed_scopes: List[str] = ["tenant"]

    @abstractmethod
    def run(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError


__all__ = ["BaseTool"]
