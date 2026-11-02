from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.registry.agent_card import AgentCard
from app.registry.repository import AgentRepository


class DynamicAgentRouter:
    """Selects the best agent for a task based on metadata and capability matching."""

    def __init__(self, repository: Optional[AgentRepository] = None):
        self.repository = repository or AgentRepository()

    def score_agent(self, agent: AgentCard, task_description: str, required_tools: Optional[List[str]] = None) -> float:
        text = task_description.lower()
        score = 0.0

        if "architect" in agent.name.lower() or "architect" in text:
            score += 3
        if "developer" in agent.name.lower() or "code" in text or "implement" in text:
            score += 3
        if "qa" in agent.name.lower() or "test" in text or "review" in text:
            score += 3
        if "research" in agent.name.lower() or "research" in text:
            score += 2

        for tag_key, tag_value in agent.metadata_tags.items():
            tag_text = f"{tag_key} {tag_value}".lower()
            if tag_text and tag_text in text:
                score += 2

        if required_tools:
            overlap = len(set(required_tools).intersection(set(agent.allowed_tools)))
            score += overlap * 2

        score += float(agent.trust_score) / 100.0
        return score

    def select(
        self,
        task_description: str,
        required_tools: Optional[List[str]] = None,
        public_only: bool = False,
    ) -> Optional[AgentCard]:
        candidates = self.repository.list_public() if public_only else self.repository.list()
        if not candidates:
            return None

        ranked = sorted(
            candidates,
            key=lambda agent: self.score_agent(agent, task_description, required_tools),
            reverse=True,
        )
        return ranked[0]


__all__ = ["DynamicAgentRouter"]
