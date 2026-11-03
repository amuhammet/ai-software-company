from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.agent import AgentRecord
from app.registry.agent_card import AgentCard


class AgentRepository:
    """SQL-backed repository for persistent agent registry entries.

    If a SQLAlchemy session is passed, the caller owns its lifecycle. Otherwise,
    each operation creates and closes its own session, which is convenient for
    simple API handlers and bootstrap code.
    """

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    def _to_card(self, record: AgentRecord) -> AgentCard:
        return AgentCard(
            id=record.id,
            name=record.name,
            purpose=record.purpose,
            owner_id=record.owner_id,
            model_preference=record.model_preference or "gpt-4o-mini",
            system_prompt=record.system_prompt,
            allowed_tools=record.allowed_tools or [],
            trust_score=record.trust_score if record.trust_score is not None else 100.0,
            is_public=bool(record.is_public),
            metadata_tags=record.metadata_tags or {},
        )

    def _using_session(self, operation):
        if self.db is not None:
            return operation(self.db)
        db = SessionLocal()
        try:
            return operation(db)
        finally:
            db.close()

    def create(self, card: AgentCard) -> AgentCard:
        def operation(db: Session) -> AgentCard:
            record = db.get(AgentRecord, card.id)
            if record is None:
                record = AgentRecord(id=card.id)
                db.add(record)
            record.name = card.name
            record.purpose = card.purpose
            record.owner_id = card.owner_id
            record.model_preference = card.model_preference
            record.system_prompt = card.system_prompt
            record.allowed_tools = card.allowed_tools
            record.trust_score = card.trust_score
            record.is_public = card.is_public
            record.metadata_tags = card.metadata_tags
            db.commit()
            db.refresh(record)
            return self._to_card(record)

        return self._using_session(operation)

    def save(self, card: AgentCard) -> AgentCard:
        """Compatibility alias for callers using the more generic save() name."""
        return self.create(card)

    def get(self, agent_id: str) -> Optional[AgentCard]:
        def operation(db: Session) -> Optional[AgentCard]:
            record = db.get(AgentRecord, agent_id)
            return self._to_card(record) if record is not None else None

        return self._using_session(operation)

    def get_by_name(self, name: str) -> Optional[AgentCard]:
        def operation(db: Session) -> Optional[AgentCard]:
            record = db.query(AgentRecord).filter(AgentRecord.name == name).first()
            return self._to_card(record) if record is not None else None

        return self._using_session(operation)

    def list(self) -> List[AgentCard]:
        def operation(db: Session) -> List[AgentCard]:
            records = db.query(AgentRecord).order_by(AgentRecord.name).all()
            return [self._to_card(record) for record in records]

        return self._using_session(operation)

    def list_public(self) -> List[AgentCard]:
        def operation(db: Session) -> List[AgentCard]:
            records = (
                db.query(AgentRecord)
                .filter(AgentRecord.is_public.is_(True))
                .order_by(AgentRecord.name)
                .all()
            )
            return [self._to_card(record) for record in records]

        return self._using_session(operation)

    def list_public_agents(self) -> List[AgentCard]:
        """Compatibility alias for callers using the earlier method name."""
        return self.list_public()

    def search(self, query: str, limit: int = 10) -> List[AgentCard]:
        if limit <= 0:
            return []

        def operation(db: Session) -> List[AgentCard]:
            pattern = f"%{query}%"
            records = (
                db.query(AgentRecord)
                .filter(
                    AgentRecord.name.ilike(pattern)
                    | AgentRecord.purpose.ilike(pattern)
                    | AgentRecord.system_prompt.ilike(pattern)
                )
                .order_by(AgentRecord.trust_score.desc())
                .limit(limit)
                .all()
            )
            return [self._to_card(record) for record in records]

        return self._using_session(operation)

    def delete(self, agent_id: str) -> None:
        def operation(db: Session) -> None:
            record = db.get(AgentRecord, agent_id)
            if record is not None:
                db.delete(record)
                db.commit()

        self._using_session(operation)


__all__ = ["AgentRepository"]
