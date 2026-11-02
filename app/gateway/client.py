import os
from typing import Any, Dict, List, Optional

import requests


class GatewayClient:
    """
    Internal client wrapper for agents to communicate with the LLM Gateway,
    ensuring budget tracking, model routing, and failover are handled centrally.
    """

    def __init__(self, gateway_url: Optional[str] = None, default_tenant: str = "org_default"):
        self.gateway_url = gateway_url or os.getenv("GATEWAY_URL", "http://localhost:8000")
        self.default_tenant = default_tenant

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "ollama/llama3",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.gateway_url}/api/v1/llm/chat"
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id or self.default_tenant,
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Agent Gateway Client Error: {str(exc)}") from exc


__all__ = ["GatewayClient"]
