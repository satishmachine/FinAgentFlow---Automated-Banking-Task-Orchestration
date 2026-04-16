"""
WorkflowManager — Central orchestrator for workflow lifecycle.

Manages the full lifecycle of a workflow: creation, validation,
execution via LangGraph, result aggregation, and artifact storage.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.agents.registry import AgentRegistry
from app.core.exceptions import WorkflowError, WorkflowNotFoundError
from app.core.logging import get_logger, get_audit_logger
from app.models.task import TaskDefinition, TaskResult, TaskStatus
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
)
from app.orchestration.dependency_resolver import resolve_dependencies
from app.orchestration.graph_builder import build_workflow_graph, WorkflowState

logger = get_logger("WorkflowManager")


class WorkflowManager:
    """
    Central brain of FinAgentFlow — manages workflow lifecycle.

    Responsibilities:
        - Parse and validate workflow definitions
        - Build LangGraph execution graphs
        - Execute workflows and aggregate results
        - Track workflow state and produce audit logs
    """

    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}

        # Register default agents
        AgentRegistry.register_defaults()

    def create_workflow(
        self,
        name: str,
        tasks: List[TaskDefinition],
        description: Optional[str] = None,
    ) -> WorkflowDefinition:
        """
        Create and register a new workflow.

        Args:
            name: Workflow name.
            tasks: List of task definitions.
            description: Optional description.

        Returns:
            The created WorkflowDefinition.
        """
        workflow = WorkflowDefinition(
            name=name,
            description=description,
            tasks=tasks,
        )

        # Validate dependencies
        resolve_dependencies(tasks)

        self._workflows[workflow.id] = workflow
        logger.info(f"Created workflow '{name}' (id={workflow.id}) with {len(tasks)} tasks")
        return workflow

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Retrieve a workflow by ID."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            raise WorkflowNotFoundError(f"Workflow '{workflow_id}' not found.")
        return wf

    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all registered workflows."""
        return list(self._workflows.values())

    async def run_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow using the LangGraph engine.

        Args:
            workflow_id: ID of the workflow to execute.
            input_data: Input data to pass to tasks.

        Returns:
            A WorkflowExecution with results from all tasks.
        """
        workflow = self.get_workflow(workflow_id)
        execution = WorkflowExecution(workflow_id=workflow_id)
        execution.started_at = datetime.now()
        execution.status = WorkflowStatus.RUNNING

        audit = get_audit_logger(execution.execution_id)
        audit.info(f"Starting workflow: {workflow.name} (id={workflow.id})")

        self._executions[execution.execution_id] = execution

        try:
            # Build and run the LangGraph
            compiled_graph = build_workflow_graph(workflow.tasks)

            initial_state: WorkflowState = {
                "input_data": input_data or {},
                "results": {},
                "logs": [],
                "current_task": "",
                "status": "running",
            }

            audit.info(f"Executing {len(workflow.tasks)} tasks")
            final_state = await compiled_graph.ainvoke(initial_state)

            # Map results back to TaskResult objects
            for task in workflow.tasks:
                output = final_state["results"].get(task.id, {})
                execution.results[task.id] = TaskResult(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    output_data=output,
                )

            execution.status = WorkflowStatus.COMPLETED
            audit.info("Workflow completed successfully")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            audit.error(f"Workflow failed: {e}")
            logger.error(f"Workflow execution failed: {e}")

        finally:
            execution.completed_at = datetime.now()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()

        return execution

    def get_execution(self, execution_id: str) -> WorkflowExecution:
        """Retrieve an execution by ID."""
        ex = self._executions.get(execution_id)
        if ex is None:
            raise WorkflowNotFoundError(f"Execution '{execution_id}' not found.")
        return ex

    def list_executions(
        self, workflow_id: Optional[str] = None
    ) -> List[WorkflowExecution]:
        """List all executions, optionally filtered by workflow."""
        execs = list(self._executions.values())
        if workflow_id:
            execs = [e for e in execs if e.workflow_id == workflow_id]
        return execs
