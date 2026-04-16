"""
User input data models.

Captures user-submitted workflow definitions from the UI or API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.task import TaskDefinition


class UserInput(BaseModel):
    """
    Captures a user-submitted workflow request.

    Attributes:
        user_id: Identifier for the user (optional for anonymous usage).
        workflow_name: Name for the new workflow.
        workflow_description: Optional description.
        tasks: List of task definitions submitted by the user.
        input_data: Additional user-provided input data (e.g., CSV paths).
    """
    user_id: Optional[str] = None
    workflow_name: str
    workflow_description: Optional[str] = None
    tasks: List[TaskDefinition]
    input_data: Dict[str, Any] = Field(default_factory=dict)
