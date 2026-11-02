from fastapi import APIRouter

from app.memory.base import SessionMemory, TaskMemory
from app.memory.lesson_store import LessonStore
from app.memory.project_memory import ProjectMemory

router = APIRouter(prefix="/api/v3/memory", tags=["Memory"])

session_memory = SessionMemory()
task_memory = TaskMemory()
project_memory = ProjectMemory()
lesson_store = LessonStore()


@router.get("/sessions/{session_id}")
def get_session_memory(session_id: str):
    return {"session_id": session_id, "records": [record.__dict__ for record in session_memory.get(session_id)]}


@router.post("/sessions/{session_id}")
def add_session_memory(session_id: str, key: str, value: str):
    record = session_memory.add(session_id, key, {"value": value}, tags=["session"])
    return {"status": "ok", "record": record.__dict__}


@router.get("/tasks/{task_id}")
def get_task_memory(task_id: str):
    return {"task_id": task_id, "records": [record.__dict__ for record in task_memory.get(task_id)]}


@router.post("/tasks/{task_id}")
def add_task_memory(task_id: str, key: str, value: str):
    record = task_memory.add(task_id, key, {"value": value}, tags=["task"])
    return {"status": "ok", "record": record.__dict__}


@router.post("/projects/{project_id}/facts")
def add_project_fact(project_id: str, key: str, value: str):
    item = project_memory.add(project_id, key, value, tags=["project"])
    return {"status": "ok", "item": item}


@router.get("/projects/{project_id}/facts")
def get_project_facts(project_id: str):
    return {"project_id": project_id, "facts": project_memory.list(project_id)}


@router.post("/lessons")
def add_lesson(lesson: str, context: str):
    item = lesson_store.add_lesson(lesson, context)
    return {"status": "ok", "item": item}


@router.get("/lessons")
def get_lessons(query: str | None = None):
    if query:
        return {"results": lesson_store.search(query)}
    return {"results": lesson_store.list()}


__all__ = ["router"]
