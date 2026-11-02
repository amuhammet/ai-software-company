import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1_auth import router as auth_router
from app.api.v1_chat import router as chat_router
from app.api.v2_agents import router as agents_router
from app.api.v2_tools import router as tools_router
from app.api.v3_memory import router as memory_router

load_dotenv()

app = FastAPI(title="AI Software Company Platform", version="0.1.0")

# API routes for Sprint 1
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(agents_router)
app.include_router(tools_router)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "ai-software-company-platform"}


# Preserve the original local demo functionality behind an opt-in environment flag.
if os.getenv("RUN_DEMO", "0") == "1":
    from app.graph_workflow import app_graph

    class AISoftwareCompany:
        def __init__(self):
            self.workflow = app_graph

        def run_project(self, task_goal: str):
            state = {
                "task": task_goal,
                "research": "",
                "architecture": "",
                "code": "",
                "qa_feedback": "",
                "status": "planning",
                "iterations": 0,
                "history": [f"Project started: {task_goal}"],
            }
            return list(self.workflow.stream(state))

    def _demo_main() -> None:
        company = AISoftwareCompany()
        company.run_project(
            "Create a Python script that validates passwords with 12+ characters, one digit, and one special character."
        )

    _demo_main()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
