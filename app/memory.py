from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover
    END = "__END__"

    class StateGraph:  # type: ignore[override]
        def __init__(self, state_type: Any):
            self.state_type = state_type
            self.nodes: Dict[str, Any] = {}
            self.edges: List[tuple[str, str]] = []

        def add_node(self, name: str, func: Any) -> "StateGraph":
            self.nodes[name] = func
            return self

        def add_edge(self, source: str, target: str) -> "StateGraph":
            self.edges.append((source, target))
            return self

        def add_conditional_edges(self, source: str, condition: Any, mapping: Dict[str, str]) -> "StateGraph":
            self.edges.append((source, source))
            self._condition = condition
            self._mapping = mapping
            return self

        def compile(self) -> Any:
            return self

        def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
            current = state.get("state", "task_received")
            for node_name, func in self.nodes.items():
                if current == node_name:
                    return func(state)
            # fallback sequential execution
            for name in list(self.nodes.keys()):
                if name == "__start__":
                    continue
                state = self.nodes[name](state)
            return state


from app.agents import (
    ArchitectAgent,
    CEOAgent,
    DeveloperAgent,
    PostMortemAgent,
    QAAgent,
    ResearcherAgent,
    SelfUpdaterAgent,
    TaskSpec,
)


class AgentState(TypedDict):
    task: str
    state: str
    objective: str
    summary: Dict[str, Any]
    research: Dict[str, Any]
    blueprint: Dict[str, Any]
    generated_files: List[str]
    validation: Dict[str, Any]
    rules: List[str]
    approved: bool
    release_note: str


class WorkflowGraph:
    def __init__(self) -> None:
        self.ceo = CEOAgent()
        self.researcher = ResearcherAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()
        self.qa = QAAgent()
        self.postmortem = PostMortemAgent()
        self.self_updater = SelfUpdaterAgent()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph = StateGraph(AgentState)

        def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"])
            result = self.ceo.run(task)
            state["objective"] = result.result["objective"]
            state["summary"] = {"status": result.result["status"]}
            state["state"] = result.state
            return state

        def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["research only", "keep objective aligned"])
            result = self.researcher.run(task)
            state["research"] = result.result
            state["state"] = result.state
            return state

        def architect_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["use modular architecture", "validate before release"])
            result = self.architect.run(task)
            state["blueprint"] = result.result["blueprint"]
            state["state"] = result.state
            return state

        def developer_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["generate code", "modular structure"])
            result = self.developer.run(task)
            state["generated_files"] = result.result["generated_files"]
            state["state"] = result.state
            return state

        def qa_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["run validation", "report failures clearly"])
            result = self.qa.run(task)
            state["validation"] = result.result
            state["state"] = result.state
            return state

        def fix_node(state: Dict[str, Any]) -> Dict[str, Any]:
            state["state"] = "fixing"
            state["summary"] = {"status": "revision requested", "reason": "QA validation failed"}
            return state

        def approve_node(state: Dict[str, Any]) -> Dict[str, Any]:
            state["approved"] = True
            state["release_note"] = "Approved by QA and CEO workflow gate."
            state["state"] = "approved"
            return state

        def postmortem_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["capture lessons", "update rules"])
            result = self.postmortem.run(task)
            state["rules"] = result.result["rules"]
            state["state"] = result.state
            return state

        def updater_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task = TaskSpec(description=state["task"], constraints=["check for updates", "report maintenance plan"])
            result = self.self_updater.run(task)
            state["summary"] = {**state.get("summary", {}), "upgrade": result.result}
            state["state"] = result.state
            return state

        graph.add_node("__start__", start_node)
        graph.add_node("ceo", start_node)
        graph.add_node("researcher", research_node)
        graph.add_node("architect", architect_node)
        graph.add_node("developer", developer_node)
        graph.add_node("qa", qa_node)
        graph.add_node("fix", fix_node)
        graph.add_node("approve", approve_node)
        graph.add_node("postmortem", postmortem_node)
        graph.add_node("self_updater", updater_node)

        graph.add_edge("__start__", "ceo")
        graph.add_edge("ceo", "researcher")
        graph.add_edge("researcher", "architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "qa")
        graph.add_conditional_edges(
            "qa",
            lambda state: "fix" if not state.get("validation", {}).get("passed", True) else "approve",
            {"fix": "fix", "approve": "approve"},
        )
        graph.add_edge("fix", "developer")
        graph.add_edge("approve", "postmortem")
        graph.add_edge("postmortem", "self_updater")
        graph.add_edge("self_updater", END)

        return graph.compile()

    def run(self, description: str) -> Dict[str, Any]:
        initial_state: Dict[str, Any] = {
            "task": description,
            "state": "task_received",
            "objective": "",
            "summary": {},
            "research": {},
            "blueprint": {},
            "generated_files": [],
            "validation": {},
            "rules": [],
            "approved": False,
            "release_note": "",
        }
        result = self.graph.invoke(initial_state)
        return {
            "task": description,
            "state": result.get("state", "released"),
            "objective": result.get("objective"),
            "summary": result.get("summary"),
            "research": result.get("research"),
            "blueprint": result.get("blueprint"),
            "generated_files": result.get("generated_files"),
            "validation": result.get("validation"),
            "rules": result.get("rules"),
            "approved": result.get("approved", False),
            "release_note": result.get("release_note"),
        }


workflow_graph = WorkflowGraph()

__all__ = ["WorkflowGraph", "workflow_graph", "AgentState"]
