from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolExecutionContext:
    tenant_id: str
    user_id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolPermissionMiddleware:
    """Central policy gate for tool access by agent and tenant."""

    def __init__(self) -> None:
        self._allow_map: Dict[str, List[str]] = {}

    def allow(self, agent_id: str, tool_name: str) -> None:
        self._allow_map.setdefault(agent_id, [])
        if tool_name not in self._allow_map[agent_id]:
            self._allow_map[agent_id].append(tool_name)

    def authorize(self, agent_id: str, tool_name: str, context: Optional[ToolExecutionContext] = None) -> bool:
        allowed = self._allow_map.get(agent_id, [])
        if tool_name not in allowed:
            return False
        if context is None:
            return True
        return bool(context.tenant_id)

    def execute_allowed_tool(
        self,
        agent_id: str,
        tool_name: str,
        tool: Any,
        arguments: Dict[str, Any],
        context: Optional[ToolExecutionContext] = None,
    ) -> str:
        if not self.authorize(agent_id, tool_name, context):
            raise PermissionError(f"Agent '{agent_id}' is not allowed to use tool '{tool_name}'.")
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        return tool.run(arguments=arguments, context=context.metadata if context else None)


__all__ = ["ToolExecutionContext", "ToolPermissionMiddleware"]
