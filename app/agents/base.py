"""
TaskAgent — Abstract base class for all banking task agents.

Every agent must implement the `execute()` method, which receives input data,
performs the task, and returns a TaskResult. After execution, the base class
automatically invokes the AI generation layer for human-readable summaries.
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
    The base class provides logging, timing, error handling, and
    automatic AI summary generation after each task.
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
        Wrapper around execute() that adds timing, logging, error handling,
        and automatic AI summary generation.

        This is the public-facing entry point called by the orchestrator.
        """
        self.logger.info(f"Starting task: {task.name} (id={task.id})")
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.started_at = datetime.now()

        try:
            result = await self.execute(task, input_data, context)
            result.status = TaskStatus.COMPLETED
            self.logger.info(f"Task completed: {task.name}")

            # ── Auto-generate AI summary (Gap 1 fix) ─────────────────
            result.ai_summary = await self._generate_ai_summary(task, result)

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

    async def _generate_ai_summary(
        self, task: TaskDefinition, result: TaskResult
    ) -> Optional[str]:
        """
        Generate an AI-powered summary for a completed task using EuriAI.

        Falls back gracefully if the API key is not set or generation fails.
        """
        try:
            from app.generation.content_generator import ContentGenerator
            from app.generation.prompts import PromptTemplates

            generator = ContentGenerator()

            # Select the right prompt based on task type
            if task.type.value == "reconciliation":
                prompt = PromptTemplates.reconciliation_summary(result.output_data)
            elif task.type.value == "compliance":
                prompt = PromptTemplates.compliance_report(result.output_data)
            elif task.type.value == "communication":
                prompt = PromptTemplates.communication_draft(result.output_data)
            else:
                prompt = PromptTemplates.task_summary(
                    task.name, task.type.value, result.output_data
                )

            summary = await generator.generate_text(prompt)
            self.logger.info(f"AI summary generated for task: {task.name}")
            result.logs.append(
                f"[{datetime.now().isoformat()}] AI summary generated ({len(summary)} chars)"
            )
            return summary

        except Exception as e:
            self.logger.warning(
                f"AI summary skipped for task '{task.name}': {e}"
            )
            result.logs.append(
                f"[{datetime.now().isoformat()}] AI summary skipped: {e}"
            )
            return None

    def log_step(self, message: str) -> str:
        """Log a step within the agent's execution and return the log entry."""
        entry = f"[{datetime.now().isoformat()}] {message}"
        self.logger.info(message)
        return entry

