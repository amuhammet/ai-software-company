from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Display name of the agent")
    purpose: str = Field(..., description="What the agent is optimized to do")
    owner_id: str = Field(..., description="User or team that owns this agent")
    model_preference: str = Field(default="gpt-4o-mini", description="Preferred provider/model route")
    system_prompt: str = Field(..., description="Core instructions or persona for the agent")
    allowed_tools: List[str] = Field(default_factory=list, description="Tool names this agent is allowed to use")
    trust_score: float = Field(default=100.0, description="Reliability/trust score")
    is_public: bool = Field(default=False, description="Whether the agent is visible in the marketplace")
    metadata_tags: Dict[str, Any] = Field(default_factory=dict, description="Custom tags and routing metadata")

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "AgentCard":
        return cls(
            id=record.get("id"),
            name=record.get("name"),
            purpose=record.get("purpose"),
            owner_id=record.get("owner_id"),
            model_preference=record.get("model_preference", "gpt-4o-mini"),
            system_prompt=record.get("system_prompt"),
            allowed_tools=record.get("allowed_tools", []),
            trust_score=float(record.get("trust_score", 100.0)),
            is_public=bool(record.get("is_public", False)),
            metadata_tags=record.get("metadata_tags", {}),
        )


__all__ = ["AgentCard"]
