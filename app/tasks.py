from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TaskSpec:
    description: str
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


STATE_SEQUENCE = [
    "task_received",
    "research_done",
    "design_done",
    "implementation_done",
    "validation_done",
    "approved",
    "released",
    "postmortem_done",
]
