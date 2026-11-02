from typing import List, Optional

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str = Field(..., description="Role of message: system, user, assistant")
    content: str = Field(..., description="Text content for the message")


class LLMRequestDTO(BaseModel):
    model: str = Field(..., description="Model name, e.g. gpt-4o-mini, claude-3-5-sonnet, ollama/llama3")
    messages: List[LLMMessage] = Field(..., description="Conversation messages")
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    fallbacks: List[str] = Field(default_factory=list)


class LLMResponseDTO(BaseModel):
    status: str
    data: str
    model_used: str
    cost_usd: float | None = None
    remaining_budget: float | None = None


__all__ = ["LLMMessage", "LLMRequestDTO", "LLMResponseDTO"]
