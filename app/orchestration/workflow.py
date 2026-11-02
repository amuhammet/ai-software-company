from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.gateway.client import GatewayClient
from app.orchestration.selector import AgentSelector

logger = logging.getLogger("DynamicOrchestrator")


class DynamicOrchestrationEngine:
    def __init__(self, selector: AgentSelector):
        self.selector = selector
        self.gateway = GatewayClient()

    def execute_task(self, task_description: str, required_capability: str) -> Dict[str, Any]:
        logger.info(f"Orchestrator looking for agent with capability: '{required_capability}'...")

        agent = self.selector.select_agent(required_capability=required_capability)
        if not agent:
            raise RuntimeError(f"No trusted agent found for capability: {required_capability}")

        logger.info(
            f"Selected Agent: {agent.name} (Model: {agent.model_preference}, Trust: {agent.trust_score})"
        )

        messages = [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": task_description},
        ]

        result = self.gateway.chat_completion(
            messages=messages,
            model=agent.model_preference,
        )

        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "output": result.get("content"),
            "cost_usd": result.get("cost_usd", 0.0),
        }


__all__ = ["DynamicOrchestrationEngine"]
