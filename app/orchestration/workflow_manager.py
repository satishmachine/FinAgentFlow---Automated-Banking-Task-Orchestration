"""
WorkflowManager — Central orchestrator for workflow lifecycle.

Manages the full lifecycle of a workflow: creation, validation,
execution via LangGraph, result aggregation, artifact storage,
and consolidated final report generation.
"""

import asyncio
import json
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
from app.models.artifact import Artifact, ArtifactType
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
        - Generate consolidated final reports
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
        continue_on_failure: bool = False,
    ) -> WorkflowDefinition:
        """
        Create and register a new workflow.

        Args:
            name: Workflow name.
            tasks: List of task definitions.
            description: Optional description.
            continue_on_failure: If True, a failing task does not abort the
                workflow; remaining tasks still run and the execution ends
                with status FAILED. If False (default), the workflow aborts
                on the first failure.

        Returns:
            The created WorkflowDefinition.
        """
        workflow = WorkflowDefinition(
            name=name,
            description=description,
            tasks=tasks,
            continue_on_failure=continue_on_failure,
        )

        # Validate dependencies
        resolve_dependencies(tasks)

        self._workflows[workflow.id] = workflow
        logger.info(f"Created workflow '{name}' (id={workflow.id}) with {len(tasks)} tasks")
        return workflow

    def add_task(
        self, workflow_id: str, task: TaskDefinition
    ) -> WorkflowDefinition:
        """
        Add a task to an existing workflow definition.

        Re-validates the dependency graph after insertion and rejects the
        change if it would introduce a cycle or a dangling dependency.

        Args:
            workflow_id: ID of the workflow to extend.
            task: Task to append.

        Returns:
            The updated WorkflowDefinition.

        Raises:
            WorkflowNotFoundError: Workflow does not exist.
            WorkflowError: Task ID already exists in the workflow.
            CircularDependencyError: Insertion would create a cycle.
        """
        workflow = self.get_workflow(workflow_id)

        existing_ids = {t.id for t in workflow.tasks}
        if task.id in existing_ids:
            raise WorkflowError(
                f"Task id '{task.id}' already exists in workflow '{workflow_id}'."
            )

        updated_tasks = workflow.tasks + [task]
        # Will raise CircularDependencyError on invalid graph
        resolve_dependencies(updated_tasks)

        workflow.tasks = updated_tasks
        logger.info(
            f"Added task '{task.id}' to workflow '{workflow_id}' "
            f"(now {len(workflow.tasks)} tasks)"
        )
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
            compiled_graph = build_workflow_graph(
                workflow.tasks,
                continue_on_failure=workflow.continue_on_failure,
            )

            initial_state: WorkflowState = {
                "input_data": input_data or {},
                "results": {},
                "logs": [],
                "current_task": "",
                "status": "running",
                "failed_tasks": [],
            }

            audit.info(
                f"Executing {len(workflow.tasks)} tasks "
                f"(continue_on_failure={workflow.continue_on_failure})"
            )
            final_state = await compiled_graph.ainvoke(initial_state)

            failed_ids = set(final_state.get("failed_tasks") or [])

            # Map results back to TaskResult objects
            for task in workflow.tasks:
                output = final_state["results"].get(task.id, {})
                status = TaskStatus.FAILED if task.id in failed_ids else TaskStatus.COMPLETED
                execution.results[task.id] = TaskResult(
                    task_id=task.id,
                    status=status,
                    output_data=output,
                    error=output.get("error") if isinstance(output, dict) and status == TaskStatus.FAILED else None,
                )

            if failed_ids:
                execution.status = WorkflowStatus.FAILED
                execution.error = (
                    f"{len(failed_ids)} task(s) failed: {', '.join(sorted(failed_ids))}"
                )
                audit.warning(execution.error)
            else:
                execution.status = WorkflowStatus.COMPLETED
                audit.info("Workflow completed successfully")

            # Calculate duration before generating final report
            execution.completed_at = datetime.now()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()

            # ── Generate consolidated final report ────────────────────
            final_report = await self.generate_final_report(workflow, execution)
            if final_report:
                audit.info("Final report generated successfully")

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

    async def generate_final_report(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
    ) -> Optional[str]:
        """
        Generate a consolidated final report for the entire workflow.

        Aggregates all task results and produces a comprehensive
        human-readable report using the AI generation layer (EuriAI).

        Args:
            workflow: The workflow definition.
            execution: The completed execution with all task results.

        Returns:
            The generated report text, or None if generation fails.
        """
        try:
            from app.generation.content_generator import ContentGenerator
            from app.storage.artifact_store import ArtifactStore

            generator = ContentGenerator()
            store = ArtifactStore()

            # Build summary of all task results
            results_summary = {}
            for task_id, result in execution.results.items():
                results_summary[task_id] = {
                    "status": result.status.value,
                    "output_summary": _truncate_dict(result.output_data, max_depth=2),
                }

            prompt = f"""You are a senior banking operations manager. Generate a comprehensive 
final report for the following completed workflow:

Workflow: {workflow.name}
Description: {workflow.description or 'N/A'}
Tasks Executed: {len(workflow.tasks)}
Duration: {execution.duration_seconds:.2f}s
Overall Status: {execution.status.value}

Task Results:
{json.dumps(results_summary, indent=2, default=str)}

Generate a professional executive summary report covering:
1. Executive Summary — high-level overview of what was accomplished
2. Task-by-Task Results — key findings from each task
3. Issues & Warnings — any items requiring attention
4. Recommendations — suggested next steps

Use formal banking language. Be specific with numbers and findings."""

            report_text = await generator.generate_text(prompt)
            logger.info(
                f"Final report generated for workflow '{workflow.name}' "
                f"({len(report_text)} chars)"
            )

            # Save the report as an artifact
            report_artifact = Artifact(
                workflow_id=workflow.id,
                task_id="__final_report__",
                type=ArtifactType.REPORT,
                name=f"{workflow.name} — Final Report",
                content={"report_text": report_text, "results_summary": results_summary},
                metadata={
                    "execution_id": execution.execution_id,
                    "generated_at": datetime.now().isoformat(),
                },
            )
            store.save_artifact(report_artifact)

            return report_text

        except Exception as e:
            logger.warning(f"Final report generation skipped: {e}")
            return None

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


def _truncate_dict(d: Dict, max_depth: int = 2, current_depth: int = 0) -> Any:
    """Truncate a nested dict for prompt inclusion (avoid token overflow)."""
    if current_depth >= max_depth:
        if isinstance(d, dict):
            return {k: "..." for k in list(d.keys())[:5]}
        elif isinstance(d, list):
            return f"[{len(d)} items]"
        return d
    if isinstance(d, dict):
        return {
            k: _truncate_dict(v, max_depth, current_depth + 1)
            for k, v in list(d.items())[:10]
        }
    if isinstance(d, list):
        return [_truncate_dict(v, max_depth, current_depth + 1) for v in d[:5]]
    return d
