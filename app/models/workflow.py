"""
Workflow data models.

A workflow is a collection of tasks with dependencies, orchestrated by
the WorkflowManager. These models track definition and runtime state.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.task import TaskDefinition, TaskResult


class WorkflowStatus(str, Enum):
    """Lifecycle status of a workflow."""
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowDefinition(BaseModel):
    """
    Defines a complete workflow composed of multiple tasks.

    Attributes:
        id: Unique workflow identifier.
        name: Human-readable workflow name.
        description: Optional description.
        tasks: List of tasks to execute.
        created_at: When the workflow was defined.
    """
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    description: Optional[str] = None
    tasks: List[TaskDefinition] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wf-001",
                "name": "Q1 Banking Review Workflow",
                "description": "End-to-end quarterly review: reconcile, check compliance, draft communications.",
                "tasks": [
                    {
                        "id": "task-001",
                        "type": "reconciliation",
                        "name": "Reconcile Transactions",
                        "parameters": {"period": "2026-Q1"},
                        "dependencies": [],
                    },
                    {
                        "id": "task-002",
                        "type": "compliance",
                        "name": "Compliance Summary",
                        "parameters": {},
                        "dependencies": ["task-001"],
                    },
                    {
                        "id": "task-003",
                        "type": "communication",
                        "name": "Draft Customer Notice",
                        "parameters": {"template": "quarterly_review"},
                        "dependencies": ["task-002"],
                    },
                ],
            }
        }


class WorkflowExecution(BaseModel):
    """
    Runtime state of a workflow execution.

    Attributes:
        workflow_id: References the WorkflowDefinition.
        execution_id: Unique run identifier.
        status: Current execution status.
        results: Task results keyed by task ID.
        started_at: When execution began.
        completed_at: When execution ended.
        duration_seconds: Total wall-clock time.
        error: Top-level error message if the workflow failed.
    """
    workflow_id: str
    execution_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    status: WorkflowStatus = WorkflowStatus.QUEUED
    results: Dict[str, TaskResult] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
