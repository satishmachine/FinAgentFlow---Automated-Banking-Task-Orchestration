"""
Artifact data models.

Artifacts are the structured data outputs (JSON/CSV) and AI-generated
reports produced by each workflow step.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Types of artifacts produced by the system."""
    JSON_DATA = "json"
    CSV_DATA = "csv"
    REPORT = "report"
    SUMMARY = "summary"
    AUDIT_LOG = "audit_log"


class Artifact(BaseModel):
    """
    Represents a stored data artifact or report.

    Attributes:
        artifact_id: Unique artifact identifier.
        workflow_id: The workflow that produced this artifact.
        task_id: The specific task that produced this artifact.
        type: Format/type of the artifact.
        name: Human-readable name.
        content: The actual artifact content (text, JSON, etc.).
        file_path: Path to the stored file on disk.
        metadata: Additional metadata about the artifact.
        created_at: When the artifact was created.
    """
    artifact_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    workflow_id: str
    task_id: str
    type: ArtifactType
    name: str
    content: Optional[Any] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
