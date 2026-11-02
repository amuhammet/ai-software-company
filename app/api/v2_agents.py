from fastapi import APIRouter

from app.registry.agent_card import AgentCard
from app.registry.repository import AgentRepository

router = APIRouter(prefix="/api/v2/agents", tags=["Agents"])
agent_repo = AgentRepository()


@router.get("/")
def list_agents():
    return [agent.model_dump() for agent in agent_repo.list()]


@router.post("/")
def create_agent(agent: AgentCard):
    saved = agent_repo.save(agent)
    return saved.model_dump()


@router.get("/public")
def list_public_agents():
    return [agent.model_dump() for agent in agent_repo.list_public()]


__all__ = ["router"]
