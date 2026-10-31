from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryRecord:
    key: str
    value: Dict[str, Any]
    tags: List[str] = field(default_factory=list)


class MemoryStore:
    """Simple production-oriented memory layer with Redis/ChromaDB hooks."""

    def __init__(self) -> None:
        self._store: Dict[str, MemoryRecord] = {}

    def store(self, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> None:
        self._store[key] = MemoryRecord(key=key, value=value, tags=tags or [])

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        item = self._store.get(key)
        return None if item is None else item.value

    def by_tag(self, tag: str) -> List[Dict[str, Any]]:
        return [item.value for item in self._store.values() if tag in item.tags]

    def snapshot(self) -> Dict[str, Any]:
        return {key: item.value for key, item in self._store.items()}


memory = MemoryStore()

memory.store(
    "default_context",
    {
        "frameworks": ["LangGraph", "CrewAI", "Ollama", "Docker"],
        "notes": "Use graph-based routing, sandbox execution, and postmortem learning to improve reliability.",
    },
    tags=["defaults", "architecture", "company"],
)

__all__ = ["MemoryStore", "memory"]
