from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentResult:
    agent: str
    state: str
    result: Dict[str, Any] = field(default_factory=dict)


class LocalLLM:
    """Small lightweight fallback used when Ollama/LLM clients are unavailable."""

    def __init__(self, model_name: str = "llama3") -> None:
        self.model_name = model_name

    def invoke(self, prompt: str) -> str:
        return f"[{self.model_name}] Generated response for: {prompt[:180]}"


class BaseAgent:
    def __init__(self, name: str, role: str, prompt: str) -> None:
        self.name = name
        self.role = role
        self.prompt = prompt
        self.llm = LocalLLM(model_name="llama3")

    def run(self, state: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError


class CEOAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="CEO",
            role="Orchestrator",
            prompt="Define objective, assign work, and approve final output.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            state="task_received",
            result={
                "objective": state["task"],
                "status": "accepted",
                "next_step": "researcher",
            },
        )


class ResearcherAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Researcher",
            role="Research",
            prompt="Investigate latest docs, APIs, and trends for the target task.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        summary = (
            f"Research summary for '{state['task']}': "
            "latest ecosystem guidance suggests modular architecture, secure sandbox execution, "
            "and version pinning before release."
        )
        return AgentResult(
            agent=self.name,
            state="research_done",
            result={
                "research_data": summary,
                "next_step": "architect",
            },
        )


class ArchitectAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Architect",
            role="Design",
            prompt="Convert research findings into a blueprint with modules and schema.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        blueprint = (
            f"Blueprint for '{state['task']}': use Python + FastAPI + Redis + Docker; "
            "define product/order/session modules and validate in sandbox before release."
        )
        return AgentResult(
            agent=self.name,
            state="design_done",
            result={
                "blueprint": blueprint,
                "next_step": "developer",
            },
        )


class DeveloperAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Developer",
            role="Implementation",
            prompt="Write modular code according to the blueprint and quality requirements.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        code = self.llm.invoke(
            f"Task: {state['task']}\nBlueprint: {state.get('blueprint', 'N/A')}\nGenerate modular Python code."
        )
        return AgentResult(
            agent=self.name,
            state="implementation_done",
            result={
                "code_versions": [code],
                "next_step": "qa",
            },
        )


class QAAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="QA",
            role="Testing",
            prompt="Run validation in sandbox, report defects, and decide whether to route back for fix.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        code = state.get("code_versions", [""])[-1]
        passed = "ERROR" not in code.upper() and "FAIL" not in code.upper()
        next_step = "ceo" if passed else "developer"
        return AgentResult(
            agent=self.name,
            state="validation_done",
            result={
                "qa_reports": ["PASS" if passed else "FAIL: validation error discovered"],
                "passed": passed,
                "next_step": next_step,
            },
        )


class PostMortemAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="PostMortem",
            role="Learning",
            prompt="Analyze the failure and convert it into durable prevention rules.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        rules = [
            "Run untrusted code in isolated Docker containers.",
            "Pin third-party dependency versions.",
            "Store recurring failure patterns in memory for reuse.",
        ]
        return AgentResult(
            agent=self.name,
            state="postmortem_done",
            result={"rules": rules, "next_step": "self_updater"},
        )


class SelfUpdaterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="SelfUpdater",
            role="Maintenance",
            prompt="Monitor framework updates and propose infrastructure upgrades.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        report = {
            "frameworks": ["LangGraph", "CrewAI", "Ollama", "Tavily"],
            "recommendation": "Check release notes and validate compatibility before upgrading orchestration dependencies.",
            "next_step": "end",
        }
        return AgentResult(
            agent=self.name,
            state="upgrade_reviewed",
            result=report,
        )


__all__ = [
    "BaseAgent",
    "CEOAgent",
    "ResearcherAgent",
    "ArchitectAgent",
    "DeveloperAgent",
    "QAAgent",
    "PostMortemAgent",
    "SelfUpdaterAgent",
    "AgentResult",
]
