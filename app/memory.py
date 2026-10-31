from __future__ import annotations

from app.memory import memory


def get_memory_snapshot() -> dict:
    return memory.snapshot()
