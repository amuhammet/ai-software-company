from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowApprovalGate:
    """Simple approval gate for destructive or sensitive actions."""

    def __init__(self) -> None:
        self._state: Dict[str, Dict[str, Any]] = {}

    def request_approval(self, run_id: str, action_description: str, required_role: str = "admin") -> str:
        self._state[run_id] = {
            "status": ApprovalStatus.PENDING.value,
            "description": action_description,
            "required_role": required_role,
        }
        return f"Workflow {run_id} paused. Human approval required for: {action_description}"

    def approve(self, run_id: str) -> ApprovalStatus:
        state = self._state.setdefault(run_id, {"status": ApprovalStatus.PENDING.value})
        state["status"] = ApprovalStatus.APPROVED.value
        return ApprovalStatus.APPROVED

    def reject(self, run_id: str) -> ApprovalStatus:
        state = self._state.setdefault(run_id, {"status": ApprovalStatus.PENDING.value})
        state["status"] = ApprovalStatus.REJECTED.value
        return ApprovalStatus.REJECTED

    def check_approval(self, run_id: str) -> ApprovalStatus:
        state = self._state.get(run_id)
        if not state:
            return ApprovalStatus.PENDING
        return ApprovalStatus(state["status"])

    def requires_human_approval(self, action_name: str) -> bool:
        destructive_actions = {
            "git_commit",
            "database_migration",
            "package_install",
            "cloud_deploy",
            "secret_write",
            "production_release",
        }
        return action_name.lower() in destructive_actions


__all__ = ["ApprovalStatus", "WorkflowApprovalGate"]
