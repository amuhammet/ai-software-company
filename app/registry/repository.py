from __future__ import annotations

from typing import Dict, List, Optional

from app.registry.agent_card import AgentCard


class AgentRepository:
    """In-memory registry for development. Replace with SQLAlchemy later."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentCard] = {}

    def save(self, agent: AgentCard) -> AgentCard:
        self._agents[agent.id] = agent
        return agent

    def get(self, agent_id: str) -> Optional[AgentCard]:
        return self._agents.get(agent_id)

    def list(self) -> List[AgentCard]:
        return list(self._agents.values())

    def list_public(self) -> List[AgentCard]:
        return [agent for agent in self._agents.values() if agent.is_public]

    def delete(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)


__all__ = ["AgentRepository"]
