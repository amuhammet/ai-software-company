from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowApprovalGate:
    """Simple in-memory approval gate placeholder for workflow pause/resume actions."""

    def __init__(self, redis_client=None) -> None:
        self.redis = redis_client
        self._state = {}

    def request_approval(self, run_id: str, action_description: str) -> str:
        self._state[run_id] = {
            "status": ApprovalStatus.PENDING.value,
            "description": action_description,
        }
        return f"Workflow {run_id} is paused. Awaiting approval for: {action_description}"

    def check_approval(self, run_id: str) -> ApprovalStatus:
        state = self._state.get(run_id)
        if not state:
            return ApprovalStatus.PENDING
        return ApprovalStatus(state["status"])


__all__ = ["ApprovalStatus", "WorkflowApprovalGate"]
