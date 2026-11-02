from __future__ import annotations

from fastapi import HTTPException, status

from app.registry.agent_card import AgentCard


def enforce_tool_permissions(agent: AgentCard, tool_name: str) -> bool:
    """Validates whether an agent is authorized to execute a specific tool."""
    if tool_name not in agent.allowed_tools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Violation: Agent '{agent.name}' (ID: {agent.id}) is not authorized to invoke tool '{tool_name}'.",
        )
    return True


__all__ = ["enforce_tool_permissions"]
