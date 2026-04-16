"""
Task data models.

Defines the structure of individual tasks within a workflow, including
their type, parameters, dependencies, status, and execution results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Supported banking task types."""
    RECONCILIATION = "reconciliation"
    COMPLIANCE = "compliance"
    COMMUNICATION = "communication"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Lifecycle status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskDefinition(BaseModel):
    """
    Defines a single task within a workflow.

    Attributes:
        id: Unique task identifier.
        type: The banking task type (reconciliation, compliance, etc.).
        name: Human-readable task name.
        description: Optional description of what the task does.
        parameters: Task-specific configuration parameters.
        dependencies: List of task IDs this task depends on.
    """
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    type: TaskType
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task-001",
                "type": "reconciliation",
                "name": "Monthly Transaction Reconciliation",
                "description": "Reconcile Q1 2026 transactions between ledger and bank statement.",
                "parameters": {
                    "period": "2026-Q1",
                    "source": "ledger",
                    "target": "bank_statement",
                },
                "dependencies": [],
            }
        }


class TaskResult(BaseModel):
    """
    Captures the output of an executed task.

    Attributes:
        task_id: References the TaskDefinition.id.
        status: Final execution status.
        output_data: Structured output produced by the task.
        ai_summary: Human-readable AI-generated summary of the result.
        logs: Step-by-step execution logs.
        error: Error message if the task failed.
        started_at: Timestamp when execution began.
        completed_at: Timestamp when execution ended.
        duration_seconds: Wall-clock execution time.
    """
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    output_data: Dict[str, Any] = Field(default_factory=dict)
    ai_summary: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
