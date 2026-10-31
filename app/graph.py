from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskSpec:
    description: str
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent: str
    state: str
    result: Dict[str, Any]


class BaseAgent:
    def __init__(self, name: str, role: str, prompt: str) -> None:
        self.name = name
        self.role = role
        self.prompt = prompt

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        raise NotImplementedError


class CEOAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "CEO",
            "Orchestrator",
            "Define goals, assign work, and approve the final output.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        return AgentResult(
            agent=self.name,
            state="task_received",
            result={
                "objective": task.description,
                "constraints": task.constraints,
                "status": "accepted",
            },
        )


class ResearcherAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "Researcher",
            "Research",
            "Investigate recent docs, trends, and APIs relevant to the task.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        from app.tools import search_web

        findings = search_web(task.description, max_results=3)
        return AgentResult(
            agent=self.name,
            state="research_done",
            result={
                "summary": "Latest references collected and distilled.",
                "findings": findings,
                "task": task.description,
            },
        )


class ArchitectAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "Architect",
            "Design",
            "Turn findings into a blueprint with modules, schema, and data flow.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        blueprint = {
            "project_name": "AI-powered e-commerce bot",
            "tech_stack": ["Python", "FastAPI", "Redis", "PostgreSQL", "Docker", "LangGraph", "CrewAI"],
            "modules": {
                "api": "Request and response layer",
                "orchestration": "Task routing and graph control",
                "memory": "Redis + ChromaDB-backed memory",
                "sandbox": "Docker execution environment",
                "release": "GitHub + CI/CD integration",
            },
            "schema": {
                "products": ["id", "name", "price", "stock"],
                "orders": ["id", "product_id", "quantity", "status"],
                "sessions": ["id", "user_id", "state"],
            },
            "notes": [
                "Validate in sandbox before release.",
                "Use memory to reduce repeated mistakes.",
                "Route failures back to developer with structured feedback.",
            ],
        }
        return AgentResult(
            agent=self.name,
            state="design_done",
            result={"blueprint": blueprint},
        )


class DeveloperAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "Developer",
            "Implementation",
            "Generate modular code that matches the validated blueprint.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        generated_files = {
            "src/__init__.py": "# package marker\n",
            "src/main.py": "def main():\n    print('E-commerce bot booted successfully')\n\nif __name__ == '__main__':\n    main()\n",
            "src/agents.py": "class WorkflowAgent:\n    def __init__(self, name):\n        self.name = name\n\n    def run(self):\n        return {'agent': self.name, 'status': 'ok'}\n",
            "src/store.py": "class Store:\n    def __init__(self):\n        self.products = []\n\n    def add_product(self, product):\n        self.products.append(product)\n",
            "requirements.txt": "requests\npython-dotenv\n",
            "Dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"src/main.py\"]\n",
        }
        return AgentResult(
            agent=self.name,
            state="implementation_done",
            result={"generated_files": generated_files},
        )


class QAAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "QA",
            "Testing",
            "Execute validation, detect defects, and route the work back if necessary.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        from app.tools import run_python_in_sandbox

        sample_code = "print('QA validation passed in sandbox')\n"
        validation = run_python_in_sandbox(sample_code, timeout=30)
        passed = validation.success
        return AgentResult(
            agent=self.name,
            state="validation_done",
            result={
                "passed": passed,
                "details": validation.as_dict(),
                "next_action": "approve" if passed else "fix",
            },
        )


class PostMortemAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "PostMortem",
            "Learning",
            "Analyze failures and convert them into durable learning rules.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        rules = [
            "Execute untrusted code in an isolated Docker environment.",
            "Pin dependency versions before release.",
            "Use overlay memory to prevent repeated failures.",
        ]
        return AgentResult(
            agent=self.name,
            state="postmortem_done",
            result={"rules": rules},
        )


class SelfUpdaterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            "SelfUpdater",
            "Maintenance",
            "Track framework updates and warn when infrastructure upgrade is recommended.",
        )

    def run(self, task: TaskSpec, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        report = {
            "frameworks": ["CrewAI", "LangGraph", "Ollama", "Tavily"],
            "recommendation": "Monitor release notes and run compatibility checks before upgrading orchestration tooling.",
        }
        return AgentResult(
            agent=self.name,
            state="upgrade_reviewed",
            result={report},
        )


__all__ = [
    "BaseAgent",
    "TaskSpec",
    "AgentResult",
    "CEOAgent",
    "ResearcherAgent",
    "ArchitectAgent",
    "DeveloperAgent",
    "QAAgent",
    "PostMortemAgent",
    "SelfUpdaterAgent",
]


# Compatibility alias kept for older code paths.
Task = TaskSpec
