import os
import json
import redis
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class MemoryManager:
    def __init__(self):
        # 1. Episodic Memory: Redis for session state and fast retrieval
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )

        # 2. Semantic Memory: ChromaDB for long-term "lessons learned"
        self.chroma_client = chromadb.PersistentClient(
            path=os.getenv("CHROMA_DB_PATH", "./chroma_db")
        )
        # Using default embedding function (Sentence Transformers)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.lesson_store = self.chroma_client.get_or_create_collection(
            name="company_playbook",
            embedding_function=self.embedding_fn
        )

    # --- Episodic Memory (Redis) ---
    
    def save_session(self, session_id: str, state: Dict[str, Any]):
        """Saves the current graph state to Redis to allow session recovery."""
        self.redis_client.set(f"session:{session_id}", json.dumps(state))

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the last known state for a session."""
        data = self.redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else None

    def add_to_history(self, session_id: str, event: str):
        """Appends an event to a Redis list for fast chronological audit."""
        self.redis_client.lpush(f"history:{session_id}", event)

    # --- Semantic Memory (ChromaDB) ---

    def store_lesson(self, lesson: str, task_context: str, metadata: Dict[str, Any] = None):
        """
        Distills a failure or success into a long-term lesson.
        Called primarily by the PostMortem agent.
        """
        lesson_id = f"lesson_{self.redis_client.incr('lesson_counter')}"
        self.lesson_store.add(
            documents=[lesson],
            metadatas=[{"context": task_context, **(metadata or {})}],
            ids=[lesson_id]
        )

    def query_lessons(self, query: str, n_results: int = 3) -> List[str]:
        """
        Retrieves the most relevant historical lessons for a new task.
        Called primarily by the Researcher and Architect agents.
        """
        results = self.lesson_store.query(
            query_texts=[query],
            n_results=n_results
        )
        # Extract documents from the nested results list
        return results['documents'][0] if results['documents'] else []

if __name__ == "__main__":
    # Basic functional test
    mem = MemoryManager()

    # Test Redis
    test_state = {"task": "Build API", "status": "coding"}
    mem.save_session("user_123", test_state)
    print(f"Redis Session Load: {mem.load_session('user_123')}")

    # Test ChromaDB
    mem.store_lesson(
        lesson="Using requests inside the sandbox fails because network is disabled. Use mock libraries for testing.",
        task_context="Sandbox Testing"
    )
    
    query = "How do I handle network calls in the sandbox?"
    lessons = mem.query_lessons(query)
    print(f"Semantic Memory Result: {lessons}")
