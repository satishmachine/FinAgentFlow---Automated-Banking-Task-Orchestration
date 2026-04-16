"""
Agents package — Task agents for banking workflow execution.

Each agent encapsulates the logic for a specific banking task type.
All agents inherit from the abstract TaskAgent base class.
"""

from app.agents.base import TaskAgent
from app.agents.reconciliation import ReconcileAgent
from app.agents.compliance import ComplianceAgent
from app.agents.communication import CommunicationAgent
from app.agents.registry import AgentRegistry

__all__ = [
    "TaskAgent",
    "ReconcileAgent",
    "ComplianceAgent",
    "CommunicationAgent",
    "AgentRegistry",
]
