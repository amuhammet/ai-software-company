from __future__ import annotations

from typing import Any, Dict

from app.registry.agent_card import AgentCard


class AgentFactory:
    """Builds agent objects from registry card metadata."""

    def __init__(self) -> None:
        self._registry: Dict[str, AgentCard] = {}

    def register(self, agent: AgentCard) -> AgentCard:
        self._registry[agent.id] = agent
        return agent

    def create(self, agent_id: str) -> AgentCard:
        if agent_id not in self._registry:
            raise KeyError(f"Agent {agent_id} is not registered")
        return self._registry[agent_id]


__all__ = ["AgentFactory"]
