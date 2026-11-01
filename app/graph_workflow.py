from typing import TypedDict, List, Annotated, Dict, Any
import operator
from langgraph.graph import StateGraph, END
from app.agents import LocalLLM, AGENT_ROLES
from app.sandbox import CodeSandbox
from app.release import ReleaseManager

# 1. Define the State
class AgentState(TypedDict):
    task: str
    research: str
    architecture: str
    code: str
    qa_feedback: str
    status: str # "planning", "coding", "reviewing", "finalizing"
    iterations: int
    history: Annotated[List[str], operator.add]

# Initialize tools
llm = LocalLLM()
sandbox = CodeSandbox()
release_mgr = ReleaseManager()

# --- Node Functions ---

def research_node(state: AgentState):
    prompt = f"Research the following task: {state['task']}"
    res = llm.chat(AGENT_ROLES["Researcher"], prompt)
    return {"research": res, "status": "planning", "history": ["Research completed"]}

def architect_node(state: AgentState):
    prompt = f"Based on this research: {state['research']}, design the architecture for: {state['task']}"
    arch = llm.chat(AGENT_ROLES["Architect"], prompt)
    return {"architecture": arch, "status": "planning", "history": ["Architecture designed"]}

def developer_node(state: AgentState):
    prompt = f"Build this: {state['architecture']}. Feedback from previous attempt: {state.get('qa_feedback', 'None')}"
    code = llm.chat(AGENT_ROLES["Developer"], prompt)
    return {"code": code, "status": "coding", "iterations": state['iterations'] + 1, "history": ["Code implemented"]}

def qa_node(state: AgentState):
    # Execute in Sandbox
    out, exit_code = sandbox.execute(state['code'])
    
    # LLM Analysis of Sandbox Output
    prompt = f"Code: {state['code']}\nSandbox Output: {out}\nExit Code: {exit_code}\nAnalyze if this meets the goal: {state['task']}"
    feedback = llm.chat(AGENT_ROLES["QA"], prompt)
    
    status = "reviewing"
    if "PASSED" in feedback.upper():
        status = "finalizing"
    
    return {"qa_feedback": feedback, "status": status, "history": ["QA Review completed"]}

def ceo_node(state: AgentState):
    prompt = f"Review the final results for: {state['task']}. Code: {state['code']}. QA: {state['qa_feedback']}"
    decision = llm.chat(AGENT_ROLES["CEO"], prompt)
    
    if "RELEASE" in decision.upper():
        # Trigger GitHub Release
        release_mgr.create_production_release(
            version=f"v0.1.{state['iterations']}", 
            description=f"AI Generated solution for {state['task']}"
        )
        return {"status": "completed", "history": ["CEO approved and released"]}
    
    return {"status": "planning", "history": ["CEO requested rework"]}

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("researcher", research_node)
workflow.add_node("architect", architect_node)
workflow.add_node("developer", developer_node)
workflow.add_node("qa", qa_node)
workflow.add_node("ceo", ceo_node)

# Define Edges
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "architect")
workflow.add_edge("architect", "developer")
workflow.add_edge("developer", "qa")

# Conditional Routing: QA -> Developer (Fix Loop) or QA -> CEO (Approval)
def route_after_qa(state: AgentState):
    if state["status"] == "finalizing":
        return "ceo"
    if state["iterations"] > 5: # Circuit breaker to prevent infinite loops
        return "ceo"
    return "developer"

workflow.add_conditional_edges("qa", route_after_qa)

# Conditional Routing: CEO -> END or CEO -> Researcher (Rework)
def route_after_ceo(state: AgentState):
    if state["status"] == "completed":
        return END
    return "researcher"

workflow.add_conditional_edges("ceo", route_after_ceo)

# Compile
app_graph = workflow.compile()
