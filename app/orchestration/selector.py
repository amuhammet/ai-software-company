from __future__ import annotations

from typing import Optional

from app.registry.agent_card import AgentCard


class AgentSelector:
    """Dynamically selects the best agent from the registry based on capability and trust."""

    def __init__(self, agent_repository):
        self.repo = agent_repository

    def select_agent(self, required_capability: str, min_trust_score: float = 80.0) -> Optional[AgentCard]:
        public_agents = self.repo.list_public()

        qualified_agents = [
            agent
            for agent in public_agents
            if agent.trust_score >= min_trust_score
            and (
                required_capability.lower() in agent.purpose.lower()
                or required_capability in agent.metadata_tags.get("capabilities", [])
            )
        ]

        if not qualified_agents:
            return None

        qualified_agents.sort(key=lambda x: x.trust_score, reverse=True)
        return qualified_agents[0]


__all__ = ["AgentSelector"]
