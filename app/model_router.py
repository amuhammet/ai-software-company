from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover
    chromadb = None


@dataclass
class MemoryRecord:
    key: str
    value: Dict[str, Any]
    tags: List[str] = field(default_factory=list)


class CompanyMemory:
    """Hybrid memory: local in-memory fallback + optional Redis/ChromaDB hooks."""

    def __init__(self, redis_url: Optional[str] = None, chroma_path: Optional[str] = None) -> None:
        self._store: Dict[str, MemoryRecord] = {}
        self._local_lessons: List[str] = []
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.chroma_path = chroma_path or os.getenv("CHROMA_PATH", "./.chroma")
        self._redis_client = None
        self._chroma_client = None

        if self.redis_url and redis is not None:
            try:
                self._redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                self._redis_client.ping()
            except Exception:
                self._redis_client = None

        if self.chroma_path and chromadb is not None:
            try:
                self._chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            except Exception:
                self._chroma_client = None

    def store(self, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> None:
        record = MemoryRecord(key=key, value=value, tags=tags or [])
        self._store[key] = record
        if self._redis_client is not None:
            try:
                self._redis_client.hset(key, mapping={"value": str(value), "tags": ",".join(record.tags)})
            except Exception:
                pass

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        record = self._store.get(key)
        if record is not None:
            return record.value
        if self._redis_client is not None:
            try:
                raw = self._redis_client.hgetall(key)
                if raw:
                    return {"raw": raw}
            except Exception:
                pass
        return None

    def by_tag(self, tag: str) -> List[Dict[str, Any]]:
        return [item.value for item in self._store.values() if tag in item.tags]

    def snapshot(self) -> Dict[str, Any]:
        return {key: item.value for key, item in self._store.items()}

    def save_lesson(self, project_id: str, lesson: str) -> None:
        self._local_lessons.append(lesson)
        if self._chroma_client is not None:
            try:
                collection = self._chroma_client.get_or_create_collection(name="company_lessons")
                collection.add(
                    documents=[lesson],
                    metadatas=[{"project_id": project_id}],
                    ids=[f"lesson_{project_id}_{len(self._local_lessons)}"],
                )
            except Exception:
                pass

    def retrieve_lessons(self, query: str, n_results: int = 3) -> str:
        if self._chroma_client is not None:
            try:
                collection = self._chroma_client.get_or_create_collection(name="company_lessons")
                results = collection.query(query_texts=[query], n_results=n_results)
                documents = results.get("documents", [[]])[0]
                if documents:
                    return "\n".join(documents)
            except Exception:
                pass
        if self._local_lessons:
            return "\n".join(self._local_lessons[-n_results:])
        return "Önceki ders bulunamadı."


memory = CompanyMemory()

memory.store(
    "default_context",
    {
        "frameworks": ["LangGraph", "CrewAI", "Ollama", "Docker"],
        "notes": "Use structured validation, hybrid memory, and sandbox isolation before release.",
    },
    tags=["defaults", "architecture", "company"],
)

__all__ = ["CompanyMemory", "memory"]
