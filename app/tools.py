from __future__ import annotations

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


class MemoryStore:
    """Production-style memory layer with Redis/ChromaDB support and in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None, chroma_path: Optional[str] = None) -> None:
        self.redis_url = redis_url
        self.chroma_path = chroma_path
        self._memory: Dict[str, MemoryRecord] = {}
        self._redis_client = None
        self._chroma_client = None

        if redis_url and redis is not None:
            try:
                self._redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis_client.ping()
            except Exception:
                self._redis_client = None

        if chroma_path and chromadb is not None:
            try:
                self._chroma_client = chromadb.PersistentClient(path=chroma_path)
            except Exception:
                self._chroma_client = None

    def store(self, key: str, value: Dict[str, Any], tags: Optional[List[str]] = None) -> None:
        record = MemoryRecord(key=key, value=value, tags=tags or [])
        self._memory[key] = record
        if self._redis_client is not None:
            try:
                self._redis_client.hset(key, mapping={"value": str(value), "tags": ",".join(record.tags)})
            except Exception:
                pass

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._memory:
            return self._memory[key].value
        if self._redis_client is not None:
            try:
                value = self._redis_client.hgetall(key)
                if value:
                    return {"raw": value}
            except Exception:
                pass
        return None

    def by_tag(self, tag: str) -> List[Dict[str, Any]]:
        return [item.value for item in self._memory.values() if tag in item.tags]

    def snapshot(self) -> Dict[str, Any]:
        return {k: v.value for k, v in self._memory.items()}

    def add_semantic_fact(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self._chroma_client is not None:
            try:
                collection = self._chroma_client.get_or_create_collection(name="company_memory")
                collection.add(documents=[text], metadatas=[metadata or {}], ids=[text[:80]])
            except Exception:
                pass

    def search_semantic(self, query: str, limit: int = 3) -> List[str]:
        if self._chroma_client is not None:
            try:
                collection = self._chroma_client.get_or_create_collection(name="company_memory")
                results = collection.query(query_texts=[query], n_results=limit)
                return [item for item in results.get("documents", [[]])[0]]
            except Exception:
                pass
        return []


memory = MemoryStore(redis_url=None, chroma_path=None)

memory.store(
    "default_context",
    {
        "frameworks": ["LangGraph", "CrewAI", "Ollama", "Docker"],
        "notes": "Use structured validation, memory, and sandbox isolation before release.",
    },
    tags=["defaults", "company", "architecture"],
)

__all__ = ["MemoryStore", "memory"]
