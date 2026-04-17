"""
ArtifactStore — Persists structured data artifacts and reports.

Supports saving/loading artifacts as JSON and CSV files.
Each artifact is stored in a directory structure organized by
workflow ID and task ID.
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings, ARTIFACTS_DIR
from app.core.exceptions import ArtifactNotFoundError, StorageError
from app.core.logging import get_logger
from app.models.artifact import Artifact, ArtifactType

logger = get_logger("ArtifactStore")


class ArtifactStore:
    """
    File-system based artifact storage.

    Directory structure:
        artifacts/
        └── {workflow_id}/
            └── {task_id}/
                ├── {artifact_id}.json
                ├── {artifact_id}.csv
                └── manifest.json
    """

    def __init__(
        self,
        base_dir: Optional[str] = None,
        fallback_dir: Optional[str] = None,
    ):
        self.base_dir = Path(base_dir or settings.artifacts_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.fallback_dir = Path(fallback_dir or settings.storage_fallback_dir)
        logger.info(f"ArtifactStore initialized at: {self.base_dir}")

    def _artifact_dir(self, workflow_id: str, task_id: str, root: Optional[Path] = None) -> Path:
        """Get the directory for a specific task's artifacts."""
        base = root or self.base_dir
        d = base / workflow_id / task_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_artifact(self, artifact: Artifact) -> str:
        """
        Save an artifact to disk with retry and a fallback directory.

        Implements the LLD error-handling scenario: on transient write
        failure, retry with exponential backoff; if the primary location
        remains unavailable, fall back to the configured fallback directory.

        Args:
            artifact: The Artifact to save.

        Returns:
            The file path where the artifact was saved.

        Raises:
            StorageError: If saving fails on both primary and fallback.
        """
        last_error: Optional[Exception] = None
        attempts = max(1, settings.storage_retry_attempts)

        for attempt in range(attempts):
            try:
                return self._write_to(self.base_dir, artifact)
            except Exception as e:  # pragma: no cover - exact path is env-dependent
                last_error = e
                delay = settings.storage_retry_delay * (2 ** attempt)
                logger.warning(
                    f"Artifact save attempt {attempt + 1}/{attempts} failed: {e} "
                    f"— retrying in {delay:.2f}s"
                )
                time.sleep(delay)

        # Primary failed — try fallback directory once
        try:
            self.fallback_dir.mkdir(parents=True, exist_ok=True)
            logger.error(
                f"Primary storage failed after {attempts} attempts; writing to fallback: "
                f"{self.fallback_dir}"
            )
            return self._write_to(self.fallback_dir, artifact)
        except Exception as e:
            raise StorageError(
                f"Failed to save artifact to primary ({last_error}) and fallback ({e})"
            )

    def _write_to(self, root: Path, artifact: Artifact) -> str:
        """Perform the actual artifact write under the given root directory."""
        directory = self._artifact_dir(artifact.workflow_id, artifact.task_id, root=root)

        if artifact.type in (ArtifactType.JSON_DATA, ArtifactType.REPORT, ArtifactType.SUMMARY):
            file_path = directory / f"{artifact.artifact_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "artifact_id": artifact.artifact_id,
                        "workflow_id": artifact.workflow_id,
                        "task_id": artifact.task_id,
                        "type": artifact.type.value,
                        "name": artifact.name,
                        "content": artifact.content,
                        "metadata": artifact.metadata,
                        "created_at": artifact.created_at.isoformat(),
                    },
                    f,
                    indent=2,
                    default=str,
                )

        elif artifact.type == ArtifactType.CSV_DATA:
            file_path = directory / f"{artifact.artifact_id}.csv"
            content = artifact.content
            if isinstance(content, list) and content:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=content[0].keys())
                    writer.writeheader()
                    writer.writerows(content)
            else:
                file_path = directory / f"{artifact.artifact_id}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2, default=str)

        elif artifact.type == ArtifactType.AUDIT_LOG:
            file_path = directory / f"{artifact.artifact_id}_audit.log"
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(artifact.content, list):
                    f.write("\n".join(str(line) for line in artifact.content))
                else:
                    f.write(str(artifact.content))

        else:
            file_path = directory / f"{artifact.artifact_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(artifact.content, f, indent=2, default=str)

        artifact.file_path = str(file_path)
        self._update_manifest(directory, artifact)
        logger.info(f"Artifact saved: {file_path}")
        return str(file_path)

    def get_artifact(self, workflow_id: str, task_id: str, artifact_id: str) -> Artifact:
        """
        Load an artifact from disk.

        Args:
            workflow_id: Workflow identifier.
            task_id: Task identifier.
            artifact_id: Artifact identifier.

        Returns:
            The loaded Artifact.

        Raises:
            ArtifactNotFoundError: If the artifact doesn't exist.
        """
        directory = self._artifact_dir(workflow_id, task_id)

        # Try JSON first, then CSV, then log
        for ext in [".json", ".csv", "_audit.log"]:
            file_path = directory / f"{artifact_id}{ext}"
            if file_path.exists():
                try:
                    if ext == ".json":
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        return Artifact(
                            artifact_id=data.get("artifact_id", artifact_id),
                            workflow_id=data.get("workflow_id", workflow_id),
                            task_id=data.get("task_id", task_id),
                            type=ArtifactType(data.get("type", "json")),
                            name=data.get("name", ""),
                            content=data.get("content"),
                            file_path=str(file_path),
                            metadata=data.get("metadata", {}),
                        )
                    elif ext == ".csv":
                        with open(file_path, "r", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                        return Artifact(
                            artifact_id=artifact_id,
                            workflow_id=workflow_id,
                            task_id=task_id,
                            type=ArtifactType.CSV_DATA,
                            name=artifact_id,
                            content=rows,
                            file_path=str(file_path),
                        )
                    else:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        return Artifact(
                            artifact_id=artifact_id,
                            workflow_id=workflow_id,
                            task_id=task_id,
                            type=ArtifactType.AUDIT_LOG,
                            name=artifact_id,
                            content=content,
                            file_path=str(file_path),
                        )
                except Exception as e:
                    raise StorageError(f"Failed to load artifact: {e}")

        raise ArtifactNotFoundError(
            f"Artifact '{artifact_id}' not found for workflow '{workflow_id}', task '{task_id}'"
        )

    def list_artifacts(self, workflow_id: str, task_id: Optional[str] = None) -> List[Dict]:
        """
        List all artifacts for a workflow, optionally filtered by task.

        Returns:
            List of artifact metadata dicts.
        """
        results = []
        workflow_dir = self.base_dir / workflow_id

        if not workflow_dir.exists():
            return results

        task_dirs = [workflow_dir / task_id] if task_id else workflow_dir.iterdir()

        for td in task_dirs:
            manifest_path = td / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                results.extend(manifest.get("artifacts", []))

        return results

    @staticmethod
    def _update_manifest(directory: Path, artifact: Artifact) -> None:
        """Update the manifest file with a new artifact entry."""
        manifest_path = directory / "manifest.json"
        manifest = {"artifacts": []}

        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

        manifest["artifacts"].append({
            "artifact_id": artifact.artifact_id,
            "type": artifact.type.value,
            "name": artifact.name,
            "file_path": artifact.file_path,
            "created_at": artifact.created_at.isoformat(),
        })

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
