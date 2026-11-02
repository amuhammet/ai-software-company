import logging
from typing import Any, Dict

from app.gateway.client import GatewayClient

logger = logging.getLogger("AIPlatformAgents")
gateway_client = GatewayClient()


class BaseAgentNode:
    def __init__(self, name: str, role_prompt: str, model: str = "ollama/llama3"):
        self.name = name
        self.role_prompt = role_prompt
        self.model = model

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Executing task via Gateway (Model: {self.model})...")

        user_prompt = state.get("current_task", "Analyze the repository and provide recommendations.")

        messages = [
            {"role": "system", "content": self.role_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            result = gateway_client.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.2,
            )

            output_content = result.get("content", "")
            logger.info(f"[{self.name}] Completed successfully. Cost: ${result.get('cost_usd', 0.0):.4f}")

            state[f"{self.name.lower()}_output"] = output_content
            state["history"] = state.get("history", []) + [{self.name: output_content}]

        except Exception as exc:
            logger.error(f"[{self.name}] Execution failed: {str(exc)}")
            state["error"] = str(exc)

        return state


ArchitectAgent = BaseAgentNode(
    name="Architect",
    role_prompt="You are a Principal Software Architect. Design clean, scalable folder structures and workflows.",
    model="ollama/llama3",
)

DeveloperAgent = BaseAgentNode(
    name="Developer",
    role_prompt="You are a Senior Python Developer. Implement robust code based on architectural designs.",
    model="ollama/llama3",
)


__all__ = ["BaseAgentNode", "ArchitectAgent", "DeveloperAgent"]
