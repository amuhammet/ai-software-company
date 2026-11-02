from __future__ import annotations

from typing import Any, Dict, List


class LessonStore:
    """Stores global lessons learned across tasks and projects."""

    def __init__(self) -> None:
        self._lessons: List[Dict[str, Any]] = []

    def add_lesson(self, lesson: str, context: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        item = {
            "lesson": lesson,
            "context": context,
            "metadata": metadata or {},
        }
        self._lessons.append(item)
        return item

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        q = query.lower()
        matches = []
        for item in self._lessons:
            text = f"{item.get('lesson','')} {item.get('context','')}".lower()
            if q in text:
                matches.append(item)
        return matches[:limit]

    def list(self) -> List[Dict[str, Any]]:
        return list(self._lessons)


__all__ = ["LessonStore"]
