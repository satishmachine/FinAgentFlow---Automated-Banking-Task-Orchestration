"""
Agent Registry — Central registry for dynamically discovering and
instantiating task agents based on task type.
"""

from typing import Dict, Optional, Type

from app.agents.base import TaskAgent
from app.core.exceptions import AgentNotFoundError
from app.core.logging import get_logger

logger = get_logger("AgentRegistry")


class AgentRegistry:
    """
    Maintains a mapping of task type → agent class.

    Agents register themselves, and the orchestrator uses the registry
    to find the right agent for each task.
    """

    _agents: Dict[str, Type[TaskAgent]] = {}

    @classmethod
    def register(cls, agent_class: Type[TaskAgent]) -> Type[TaskAgent]:
        """
        Register an agent class by its `agent_type`.

        Can be used as a decorator:
            @AgentRegistry.register
            class MyAgent(TaskAgent): ...
        """
        instance = agent_class()
        agent_type = instance.agent_type
        cls._agents[agent_type] = agent_class
        logger.info(f"Registered agent: {agent_type} → {agent_class.__name__}")
        return agent_class

    @classmethod
    def get(cls, task_type: str) -> TaskAgent:
        """
        Get an instance of the agent for the given task type.

        Args:
            task_type: The task type string (e.g., "reconciliation").

        Returns:
            An instantiated TaskAgent.

        Raises:
            AgentNotFoundError: If no agent is registered for the given type.
        """
        agent_class = cls._agents.get(task_type)
        if agent_class is None:
            available = list(cls._agents.keys())
            raise AgentNotFoundError(
                f"No agent registered for task type '{task_type}'. "
                f"Available types: {available}"
            )
        return agent_class()

    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """Return a dict of registered task_type → agent description."""
        result = {}
        for task_type, agent_class in cls._agents.items():
            instance = agent_class()
            result[task_type] = instance.description
        return result

    @classmethod
    def is_registered(cls, task_type: str) -> bool:
        """Check if an agent is registered for the given task type."""
        return task_type in cls._agents

    @classmethod
    def register_defaults(cls) -> None:
        """Register all built-in agents."""
        from app.agents.reconciliation import ReconcileAgent
        from app.agents.compliance import ComplianceAgent
        from app.agents.communication import CommunicationAgent

        for agent_cls in [ReconcileAgent, ComplianceAgent, CommunicationAgent]:
            if not cls.is_registered(agent_cls().agent_type):
                cls.register(agent_cls)
