"""
Artifact API routes — retrieve and download workflow artifacts.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.storage.artifact_store import ArtifactStore

router = APIRouter()

_store = ArtifactStore()


@router.get("/artifacts/{workflow_id}")
async def list_artifacts(workflow_id: str, task_id: Optional[str] = None):
    """List all artifacts for a workflow, optionally filtered by task."""
    artifacts = _store.list_artifacts(workflow_id, task_id)
    return {"workflow_id": workflow_id, "artifacts": artifacts}


@router.get("/artifacts/{workflow_id}/{task_id}/{artifact_id}")
async def get_artifact(workflow_id: str, task_id: str, artifact_id: str):
    """Get a specific artifact's content."""
    try:
        artifact = _store.get_artifact(workflow_id, task_id, artifact_id)
        return {
            "artifact_id": artifact.artifact_id,
            "type": artifact.type.value,
            "name": artifact.name,
            "content": artifact.content,
            "metadata": artifact.metadata,
            "created_at": artifact.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/artifacts/{workflow_id}/{task_id}/{artifact_id}/download")
async def download_artifact(workflow_id: str, task_id: str, artifact_id: str):
    """Download an artifact file."""
    try:
        artifact = _store.get_artifact(workflow_id, task_id, artifact_id)
        if artifact.file_path:
            return FileResponse(
                artifact.file_path,
                filename=f"{artifact.name}.{artifact.type.value}",
            )
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
