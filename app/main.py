from __future__ import annotations

from typing import Any, Dict, List, TypedDict

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover
    END = "END"

    class StateGraph:  # type: ignore
        def __init__(self, state_type: Any) -> None:
            self.state_type = state_type
            self.nodes: Dict[str, Any] = {}
            self.conditional_edges: List[tuple[str, Any, Dict[str, str]]] = []
            self.entry = None

        def add_node(self, name: str, func: Any) -> "StateGraph":
            self.nodes[name] = func
            return self

        def set_entry_point(self, name: str) -> "StateGraph":
            self.entry = name
            return self

        def add_edge(self, source: str, target: str) -> "StateGraph":
            return self

        def add_conditional_edges(self, source: str, fn: Any, mapping: Dict[str, str]) -> "StateGraph":
            self.conditional_edges.append((source, fn, mapping))
            return self

        def compile(self) -> "StateGraph":
            return self

        def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
            current = self.entry
            while current is not None and current != END:
                state = self.nodes[current](state)
                if current == "qa":
                    decision = self.conditional_edges[0][1](state)
                    current = self.conditional_edges[0][2].get(decision, END)
                    continue
                if "next_step" in state:
                    current = state["next_step"]
                    if current == "end":
                        break
                else:
                    break
            return state

from app.agents import (
    ArchitectAgent,
    CEOAgent,
    DeveloperAgent,
    PostMortemAgent,
    QAAgent,
    ResearcherAgent,
    SelfUpdaterAgent,
)
from app.memory import memory
from app.model_router import ModelRouter


class SoftwareState(TypedDict):
    task: str
    research_data: str
    blueprint: str
    code_versions: List[str]
    errors: List[str]
    lessons: str
    status: str
    iterations: int
    next_step: str


class WorkflowGraph:
    def __init__(self) -> None:
        self.ceo = CEOAgent()
        self.researcher = ResearcherAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()
        self.qa = QAAgent()
        self.postmortem = PostMortemAgent()
        self.self_updater = SelfUpdaterAgent()
        self.router = ModelRouter()
        self.memory = memory
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph = StateGraph(SoftwareState)

        def ceo_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.ceo.run(state)
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "researcher")
            return state

        def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.researcher.run(state)
            state["research_data"] = result.result.get("research_data", "")
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "architect")
            return state

        def architect_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.architect.run(state)
            state["blueprint"] = result.result.get("blueprint", "")
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "developer")
            return state

        def developer_node(state: Dict[str, Any]) -> Dict[str, Any]:
            state["lessons"] = self.memory.retrieve_lessons(state["task"], n_results=3)
            result = self.developer.run(state)
            state["code_versions"] = result.result.get("code_versions", [])
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "qa")
            return state

        def qa_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.qa.run(state)
            state["errors"] = [item for item in result.result.get("qa_reports", []) if "FAIL" in item.upper() or "ERROR" in item.upper()]
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "ceo")
            return state

        def postmortem_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.postmortem.run(state)
            if "lesson" in result.result:
                self.memory.save_lesson("project_default", str(result.result["lesson"]))
            state["status"] = result.state
            state["lessons"] = str(result.result.get("rules", []))
            state["next_step"] = result.result.get("next_step", "self_updater")
            return state

        def self_updater_node(state: Dict[str, Any]) -> Dict[str, Any]:
            result = self.self_updater.run(state)
            state["status"] = result.state
            state["next_step"] = result.result.get("next_step", "end")
            return state

        graph.add_node("ceo", ceo_node)
        graph.add_node("researcher", researcher_node)
        graph.add_node("architect", architect_node)
        graph.add_node("developer", developer_node)
        graph.add_node("qa", qa_node)
        graph.add_node("postmortem", postmortem_node)
        graph.add_node("self_updater", self_updater_node)

        graph.set_entry_point("ceo")
        graph.add_edge("ceo", "researcher")
        graph.add_edge("researcher", "architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "qa")

        def route_after_qa(state: Dict[str, Any]) -> str:
            if state.get("errors"):
                return "developer"
            return "postmortem"

        graph.add_conditional_edges(
            "qa",
            route_after_qa,
            {"developer": "developer", "postmortem": "postmortem"},
        )
        graph.add_edge("postmortem", "self_updater")
        graph.add_edge("self_updater", END)

        return graph.compile()

    def run(self, task_description: str) -> Dict[str, Any]:
        init_state: Dict[str, Any] = {
            "task": task_description,
            "research_data": "",
            "blueprint": "",
            "code_versions": [],
            "errors": [],
            "lessons": "",
            "status": "task_received",
            "iterations": 0,
            "next_step": "ceo",
        }
        result = self.graph.invoke(init_state)
        return {
            "task": result.get("task", task_description),
            "status": result.get("status", "completed"),
            "research_data": result.get("research_data", ""),
            "blueprint": result.get("blueprint", ""),
            "code_versions": result.get("code_versions", []),
            "errors": result.get("errors", []),
            "lessons": result.get("lessons", ""),
            "next_step": result.get("next_step", END),
        }


workflow_graph = WorkflowGraph()

__all__ = ["WorkflowGraph", "workflow_graph", "SoftwareState"]
