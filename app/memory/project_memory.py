from __future__ import annotations

from typing import Any, Dict, List


class ProjectMemory:
    """Team/project context and reusable architectural memory."""

    def __init__(self) -> None:
        self._memory: Dict[str, List[Dict[str, Any]]] = {}

    def add(self, project_id: str, key: str, value: Any, tags: List[str] | None = None) -> Dict[str, Any]:
        bucket = self._memory.setdefault(project_id, [])
        item = {"key": key, "value": value, "tags": tags or []}
        bucket.append(item)
        return item

    def get(self, project_id: str, key: str | None = None) -> List[Dict[str, Any]]:
        items = self._memory.get(project_id, [])
        if key is None:
            return list(items)
        return [item for item in items if item.get("key") == key]

    def list(self, project_id: str) -> List[Dict[str, Any]]:
        return list(self._memory.get(project_id, []))


__all__ = ["ProjectMemory"]
