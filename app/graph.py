from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.model_router import ModelRouter


@dataclass
class AgentResult:
    agent: str
    state: str
    result: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    def __init__(self, name: str, role: str, prompt: str) -> None:
        self.name = name
        self.role = role
        self.prompt = prompt
        self.router = ModelRouter()

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
            prompt="Investigate latest docs, APIs, and trends for the task.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        model = self.router.get_model("reasoning")
        summary = model.invoke(f"Research latest guidance for: {state['task']}")
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
        model = self.router.get_model("reasoning")
        blueprint = model.invoke(
            f"Task: {state['task']}\nResearch: {state.get('research_data', 'N/A')}\nCreate a blueprint with modules, schema, and deployment notes."
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
        model = self.router.get_model("developer")
        prompt = (
            f"Task: {state['task']}\n"
            f"Lessons: {state.get('lessons', 'No prior lessons.')}\n"
            f"Blueprint: {state.get('blueprint', 'N/A')}\n"
            "Write production-quality Python code."
        )
        code = model.invoke(prompt)
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
        model = self.router.get_model("review")
        code = state.get("code_versions", [""])[-1]
        feedback = model.invoke(f"Review this code for bugs and correctness:\n{code}")
        passed = "ERROR" not in feedback.upper() and "FAIL" not in feedback.upper()
        return AgentResult(
            agent=self.name,
            state="validation_done",
            result={
                "qa_reports": [feedback],
                "passed": passed,
                "next_step": "ceo" if passed else "developer",
            },
        )


class PostMortemAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="PostMortem",
            role="Learning",
            prompt="Analyze the error and convert it into durable prevention rules.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        model = self.router.get_model("reasoning")
        errors = state.get("errors", ["No errors recorded."])
        lesson = model.invoke(f"Based on these errors: {errors}, what prevention rule should we add?")
        return AgentResult(
            agent=self.name,
            state="postmortem_done",
            result={
                "lesson": lesson,
                "rules": [lesson],
                "next_step": "self_updater",
            },
        )


class SelfUpdaterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="SelfUpdater",
            role="Maintenance",
            prompt="Check framework updates and propose infrastructure upgrades.",
        )

    def run(self, state: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            state="upgrade_reviewed",
            result={
                "frameworks": ["LangGraph", "CrewAI", "Ollama", "Tavily"],
                "recommendation": "Check release notes and validate compatibility before upgrading orchestration pathways.",
                "next_step": "end",
            },
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
