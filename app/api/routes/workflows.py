"""
Workflow API routes — CRUD and execution endpoints for workflows.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.task import TaskDefinition, TaskType
from app.models.user import UserInput
from app.models.workflow import WorkflowStatus
from app.orchestration.workflow_manager import WorkflowManager

router = APIRouter()

# Shared workflow manager instance
_manager = WorkflowManager()


def get_manager() -> WorkflowManager:
    """Return the shared WorkflowManager (used by other route modules)."""
    return _manager


# ── Request / Response Schemas ────────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    """Request body for creating a new workflow."""
    name: str
    description: Optional[str] = None
    tasks: List[TaskDefinition]
    continue_on_failure: bool = False


class RunWorkflowRequest(BaseModel):
    """Request body for executing a workflow."""
    input_data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    """Response body for workflow endpoints."""
    id: str
    name: str
    description: Optional[str]
    task_count: int
    continue_on_failure: bool = False
    status: str = "draft"


class ExecutionResponse(BaseModel):
    """Response body for workflow execution results."""
    execution_id: str
    workflow_id: str
    status: str
    results: Dict[str, Any]
    duration_seconds: Optional[float]
    error: Optional[str]


# ── Endpoints ─────────────────────────────────────────────────────────────

def _workflow_response(wf) -> WorkflowResponse:
    return WorkflowResponse(
        id=wf.id,
        name=wf.name,
        description=wf.description,
        task_count=len(wf.tasks),
        continue_on_failure=wf.continue_on_failure,
    )


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(req: CreateWorkflowRequest):
    """Create a new workflow definition."""
    try:
        wf = _manager.create_workflow(
            name=req.name,
            tasks=req.tasks,
            description=req.description,
            continue_on_failure=req.continue_on_failure,
        )
        return _workflow_response(wf)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/from-user-input", response_model=WorkflowResponse)
async def create_workflow_from_user_input(user_input: UserInput):
    """
    Create a new workflow from a UserInput payload (LLD model).

    Accepts the user-facing UserInput schema (user_id, workflow_name,
    workflow_description, tasks, input_data) and persists it as a workflow.
    The input_data is not stored with the definition; pass it at execute time.
    """
    try:
        wf = _manager.create_workflow(
            name=user_input.workflow_name,
            tasks=user_input.tasks,
            description=user_input.workflow_description,
        )
        return _workflow_response(wf)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows():
    """List all registered workflows."""
    return [_workflow_response(wf) for wf in _manager.list_workflows()]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
    try:
        return _workflow_response(_manager.get_workflow(workflow_id))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workflows/{workflow_id}/tasks", response_model=WorkflowResponse)
async def add_task_to_workflow(workflow_id: str, task: TaskDefinition):
    """Append a task to an existing workflow (LLD WorkflowManager.add_task)."""
    try:
        wf = _manager.add_task(workflow_id, task)
        return _workflow_response(wf)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/{workflow_id}/run", response_model=ExecutionResponse)
async def run_workflow(workflow_id: str, req: RunWorkflowRequest):
    """Execute a workflow and return results."""
    try:
        execution = await _manager.run_workflow(workflow_id, req.input_data)
        return ExecutionResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status.value,
            results={
                tid: result.output_data
                for tid, result in execution.results.items()
            },
            duration_seconds=execution.duration_seconds,
            error=execution.error,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _execution_response(ex) -> ExecutionResponse:
    return ExecutionResponse(
        execution_id=ex.execution_id,
        workflow_id=ex.workflow_id,
        status=ex.status.value,
        results={tid: result.output_data for tid, result in ex.results.items()},
        duration_seconds=ex.duration_seconds,
        error=ex.error,
    )


@router.get("/workflows/{workflow_id}/executions", response_model=List[ExecutionResponse])
async def list_executions(workflow_id: str):
    """List all executions for a workflow."""
    return [_execution_response(ex) for ex in _manager.list_executions(workflow_id)]


@router.get("/executions", response_model=List[ExecutionResponse])
async def list_all_executions():
    """List all executions across every workflow (UI dashboard)."""
    return [_execution_response(ex) for ex in _manager.list_executions()]


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str):
    """Fetch a specific execution by id."""
    try:
        return _execution_response(_manager.get_execution(execution_id))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/executions/{execution_id}/audit-log")
async def get_audit_log(execution_id: str):
    """Return the raw audit log text for a given execution."""
    from pathlib import Path
    from app.core.config import settings

    audit_path = Path(settings.log_dir) / "audit" / f"workflow_{execution_id}.log"
    if not audit_path.exists():
        raise HTTPException(status_code=404, detail="Audit log not found")
    return {
        "execution_id": execution_id,
        "path": str(audit_path),
        "content": audit_path.read_text(encoding="utf-8"),
    }
