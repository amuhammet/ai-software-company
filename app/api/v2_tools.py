from fastapi import APIRouter

from app.tools.registry import ToolRegistry

router = APIRouter(prefix="/api/v2/tools", tags=["Tools"])
tool_registry = ToolRegistry()


@router.get("/")
def list_tools():
    return {"tools": tool_registry.list()}


@router.post("/register")
def register_tool(name: str):
    tool_registry.register(type("ToolStub", (), {"name": name, "description": f"Registered tool: {name}"})())
    return {"status": "ok", "tool": name}


__all__ = ["router"]
