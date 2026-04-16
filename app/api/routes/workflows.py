"""
Workflow API routes — CRUD and execution endpoints for workflows.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.task import TaskDefinition, TaskType
from app.models.workflow import WorkflowStatus
from app.orchestration.workflow_manager import WorkflowManager

router = APIRouter()

# Shared workflow manager instance
_manager = WorkflowManager()


# ── Request / Response Schemas ────────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    """Request body for creating a new workflow."""
    name: str
    description: Optional[str] = None
    tasks: List[TaskDefinition]


class RunWorkflowRequest(BaseModel):
    """Request body for executing a workflow."""
    input_data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    """Response body for workflow endpoints."""
    id: str
    name: str
    description: Optional[str]
    task_count: int
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

@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(req: CreateWorkflowRequest):
    """Create a new workflow definition."""
    try:
        wf = _manager.create_workflow(
            name=req.name,
            tasks=req.tasks,
            description=req.description,
        )
        return WorkflowResponse(
            id=wf.id,
            name=wf.name,
            description=wf.description,
            task_count=len(wf.tasks),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows():
    """List all registered workflows."""
    return [
        WorkflowResponse(
            id=wf.id,
            name=wf.name,
            description=wf.description,
            task_count=len(wf.tasks),
        )
        for wf in _manager.list_workflows()
    ]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
    try:
        wf = _manager.get_workflow(workflow_id)
        return WorkflowResponse(
            id=wf.id,
            name=wf.name,
            description=wf.description,
            task_count=len(wf.tasks),
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


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


@router.get("/workflows/{workflow_id}/executions", response_model=List[ExecutionResponse])
async def list_executions(workflow_id: str):
    """List all executions for a workflow."""
    return [
        ExecutionResponse(
            execution_id=ex.execution_id,
            workflow_id=ex.workflow_id,
            status=ex.status.value,
            results={
                tid: result.output_data
                for tid, result in ex.results.items()
            },
            duration_seconds=ex.duration_seconds,
            error=ex.error,
        )
        for ex in _manager.list_executions(workflow_id)
    ]
