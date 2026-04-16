"""
TaskAgent — Abstract base class for all banking task agents.

Every agent must implement the `execute()` method, which receives input data,
performs the task, and returns a TaskResult. Agents may optionally invoke the
AI generation layer for human-readable summaries.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.logging import get_logger
from app.models.task import TaskDefinition, TaskResult, TaskStatus


class TaskAgent(ABC):
    """
    Abstract base class for banking task agents.

    Subclasses must implement `execute()` with the actual task logic.
    The base class provides logging, timing, and error handling.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return the task type this agent handles (e.g., 'reconciliation')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of this agent."""
        ...

    @abstractmethod
    async def execute(
        self,
        task: TaskDefinition,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Execute the task and return a result.

        Args:
            task: The task definition with parameters.
            input_data: Input data for the task (from user or upstream tasks).
            context: Optional context from the workflow (e.g., prior task results).

        Returns:
            A TaskResult with status, output data, and optional AI summary.
        """
        ...

    async def run(
        self,
        task: TaskDefinition,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Wrapper around execute() that adds timing, logging, and error handling.

        This is the public-facing entry point called by the orchestrator.
        """
        self.logger.info(f"Starting task: {task.name} (id={task.id})")
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.started_at = datetime.now()

        try:
            result = await self.execute(task, input_data, context)
            result.status = TaskStatus.COMPLETED
            self.logger.info(f"Task completed: {task.name}")
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            self.logger.error(f"Task failed: {task.name} — {e}")
        finally:
            result.completed_at = datetime.now()
            if result.started_at:
                result.duration_seconds = (
                    result.completed_at - result.started_at
                ).total_seconds()
            result.logs.append(
                f"[{result.completed_at}] Task '{task.name}' finished with status: {result.status.value}"
            )

        return result

    def log_step(self, message: str) -> str:
        """Log a step within the agent's execution and return the log entry."""
        entry = f"[{datetime.now().isoformat()}] {message}"
        self.logger.info(message)
        return entry
