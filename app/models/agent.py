from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class AgentRecord(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    purpose = Column(String, nullable=False)
    owner_id = Column(String, nullable=False, index=True)
    model_preference = Column(String, default="gpt-4o-mini")
    system_prompt = Column(String, nullable=False)
    allowed_tools = Column(JSON, default=list)
    trust_score = Column(Float, default=100.0)
    is_public = Column(Boolean, default=False)
    metadata_tags = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional inference if the project later adds team ownership.
    # This keeps the shape future-friendly without requiring a strict relationship yet.
    __table_args__ = {"extend_existing": True}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "owner_id": self.owner_id,
            "model_preference": self.model_preference,
            "system_prompt": self.system_prompt,
            "allowed_tools": self.allowed_tools or [],
            "trust_score": self.trust_score,
            "is_public": self.is_public,
            "metadata_tags": self.metadata_tags or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


__all__ = ["AgentRecord"]
