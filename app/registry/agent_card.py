from pydantic import BaseModel, Field
from typing import Any, Dict, List


class AgentCard(BaseModel):
    id: str = Field(..., description="Unique id for the agent")
    name: str = Field(..., description="Display name for the agent")
    purpose: str = Field(..., description="Short summary of what this agent does")
    owner_id: str = Field(..., description="User or team that owns the agent")
    model_preference: str = Field(default="gpt-4o-mini", description="Preferred model")
    system_prompt: str = Field(..., description="Persona and instructions")
    allowed_tools: List[str] = Field(default_factory=list)
    trust_score: float = Field(default=100.0)
    is_public: bool = Field(default=False)
    metadata_tags: Dict[str, Any] = Field(default_factory=dict)


__all__ = ["AgentCard"]
