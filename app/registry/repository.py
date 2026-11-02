from __future__ import annotations

from typing import Dict, List, Optional

from app.models.agent import AgentRecord
from app.registry.agent_card import AgentCard


class AgentRepository:
    """Repository layer for agent registry entries.

    This initial version is in-memory for fast iteration. The same interface can later
    be backed by PostgreSQL or a proper database model.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, AgentCard] = {}

    def create(self, card: AgentCard) -> AgentCard:
        self._agents[card.id] = card
        return card

    def get(self, agent_id: str) -> Optional[AgentCard]:
        return self._agents.get(agent_id)

    def get_by_name(self, name: str) -> Optional[AgentCard]:
        for card in self._agents.values():
            if card.name == name:
                return card
        return None

    def list(self) -> List[AgentCard]:
        return list(self._agents.values())

    def list_public(self) -> List[AgentCard]:
        return [card for card in self._agents.values() if card.is_public]

    def search(self, query: str, limit: int = 10) -> List[AgentCard]:
        q = query.lower()
        matches = []
        for card in self._agents.values():
            haystack = " ".join(
                [
                    card.name,
                    card.purpose,
                    card.system_prompt,
                    " ".join(card.allowed_tools),
                    " ".join(card.metadata_tags.keys()),
                ]
            ).lower()
            if q in haystack:
                matches.append(card)
        return matches[:limit]

    def delete(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    def to_record(self, card: AgentCard) -> AgentRecord:
        return AgentRecord(
            id=card.id,
            name=card.name,
            purpose=card.purpose,
            owner_id=card.owner_id,
            model_preference=card.model_preference,
            system_prompt=card.system_prompt,
            allowed_tools=card.allowed_tools,
            trust_score=card.trust_score,
            is_public=card.is_public,
            metadata_tags=card.metadata_tags,
        )


__all__ = ["AgentRepository"]
