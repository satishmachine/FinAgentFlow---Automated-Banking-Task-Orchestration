"""
Unit tests for the data models.
"""

import pytest
from app.models.task import TaskDefinition, TaskResult, TaskStatus, TaskType
from app.models.workflow import WorkflowDefinition, WorkflowExecution, WorkflowStatus
from app.models.artifact import Artifact, ArtifactType
from app.models.user import UserInput


class TestTaskModels:
    """Tests for task data models."""

    def test_task_definition_creation(self):
        task = TaskDefinition(
            type=TaskType.RECONCILIATION,
            name="Test Reconciliation",
            parameters={"period": "2026-Q1"},
        )
        assert task.name == "Test Reconciliation"
        assert task.type == TaskType.RECONCILIATION
        assert task.parameters["period"] == "2026-Q1"
        assert task.dependencies == []
        assert task.id is not None

    def test_task_definition_with_dependencies(self):
        task = TaskDefinition(
            id="task-002",
            type=TaskType.COMPLIANCE,
            name="Compliance Check",
            dependencies=["task-001"],
        )
        assert task.id == "task-002"
        assert task.dependencies == ["task-001"]

    def test_task_result_default_status(self):
        result = TaskResult(task_id="task-001")
        assert result.status == TaskStatus.PENDING
        assert result.output_data == {}
        assert result.logs == []
        assert result.error is None

    def test_task_type_enum(self):
        assert TaskType.RECONCILIATION.value == "reconciliation"
        assert TaskType.COMPLIANCE.value == "compliance"
        assert TaskType.COMMUNICATION.value == "communication"
        assert TaskType.CUSTOM.value == "custom"


class TestWorkflowModels:
    """Tests for workflow data models."""

    def test_workflow_definition_creation(self):
        wf = WorkflowDefinition(
            name="Test Workflow",
            description="A test workflow",
            tasks=[
                TaskDefinition(type=TaskType.RECONCILIATION, name="Reconcile"),
            ],
        )
        assert wf.name == "Test Workflow"
        assert len(wf.tasks) == 1
        assert wf.id is not None

    def test_workflow_execution_default(self):
        ex = WorkflowExecution(workflow_id="wf-001")
        assert ex.status == WorkflowStatus.QUEUED
        assert ex.results == {}
        assert ex.error is None


class TestArtifactModels:
    """Tests for artifact data models."""

    def test_artifact_creation(self):
        artifact = Artifact(
            workflow_id="wf-001",
            task_id="task-001",
            type=ArtifactType.JSON_DATA,
            name="reconciliation_output",
            content={"matched": 95, "discrepancies": 3},
        )
        assert artifact.type == ArtifactType.JSON_DATA
        assert artifact.content["matched"] == 95


class TestUserInput:
    """Tests for user input models."""

    def test_user_input_creation(self):
        ui = UserInput(
            workflow_name="My Workflow",
            tasks=[
                TaskDefinition(type=TaskType.RECONCILIATION, name="Reconcile"),
            ],
        )
        assert ui.workflow_name == "My Workflow"
        assert len(ui.tasks) == 1
        assert ui.user_id is None
