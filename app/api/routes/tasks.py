"""
Task-related API routes — query available agent types.
"""

from fastapi import APIRouter

from app.agents.registry import AgentRegistry

router = APIRouter()


@router.get("/tasks/agents")
async def list_available_agents():
    """List all registered task agent types and their descriptions."""
    AgentRegistry.register_defaults()
    return {
        "agents": AgentRegistry.list_agents(),
        "total": len(AgentRegistry.list_agents()),
    }
