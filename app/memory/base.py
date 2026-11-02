from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryRecord:
    key: str
    value: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SessionMemory:
    """Short-lived memory for a task or session."""

    def __init__(self) -> None:
        self._store: Dict[str, List[MemoryRecord]] = {}

    def add(self, session_id: str, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> MemoryRecord:
        record = MemoryRecord(key=key, value=value, tags=tags or [], created_at=datetime.utcnow())
        self._store.setdefault(session_id, []).append(record)
        return record

    def get(self, session_id: str) -> List[MemoryRecord]:
        return self._store.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


class TaskMemory:
    """Project-level task memory abstraction."""

    def __init__(self) -> None:
        self._task_store: Dict[str, List[MemoryRecord]] = {}

    def add(self, task_id: str, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> MemoryRecord:
        record = MemoryRecord(key=key, value=value, tags=tags or [], created_at=datetime.utcnow())
        self._task_store.setdefault(task_id, []).append(record)
        return record

    def get(self, task_id: str) -> List[MemoryRecord]:
        return self._task_store.get(task_id, [])


__all__ = ["MemoryRecord", "SessionMemory", "TaskMemory"]
