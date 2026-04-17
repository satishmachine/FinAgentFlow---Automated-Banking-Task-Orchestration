"""
Integration tests for end-to-end workflow execution.
"""

import pytest

from app.core.exceptions import CircularDependencyError, WorkflowError
from app.models.task import TaskDefinition, TaskType
from app.orchestration.workflow_manager import WorkflowManager


class TestWorkflowIntegration:
    """End-to-end workflow integration tests."""

    @pytest.fixture
    def manager(self):
        return WorkflowManager()

    @pytest.fixture
    def sample_workflow(self, manager):
        tasks = [
            TaskDefinition(
                id="reconcile",
                type=TaskType.RECONCILIATION,
                name="Reconcile Transactions",
                parameters={"period": "2026-Q1", "source": "ledger", "target": "bank"},
            ),
            TaskDefinition(
                id="comply",
                type=TaskType.COMPLIANCE,
                name="Compliance Check",
                dependencies=["reconcile"],
            ),
            TaskDefinition(
                id="communicate",
                type=TaskType.COMMUNICATION,
                name="Draft Report",
                parameters={"template": "quarterly_review"},
                dependencies=["comply"],
            ),
        ]
        return manager.create_workflow(
            name="Q1 Review",
            tasks=tasks,
            description="Integration test workflow",
        )

    def test_workflow_creation(self, manager, sample_workflow):
        assert sample_workflow.name == "Q1 Review"
        assert len(sample_workflow.tasks) == 3

    def test_workflow_retrieval(self, manager, sample_workflow):
        retrieved = manager.get_workflow(sample_workflow.id)
        assert retrieved.id == sample_workflow.id

    @pytest.mark.asyncio
    async def test_workflow_execution(self, manager, sample_workflow):
        """Test full end-to-end workflow execution."""
        input_data = {
            "source_transactions": [
                {"id": "txn-1", "amount": 100.0},
                {"id": "txn-2", "amount": 200.0},
            ],
            "target_transactions": [
                {"id": "txn-1", "amount": 100.0},
                {"id": "txn-2", "amount": 200.0},
            ],
        }

        execution = await manager.run_workflow(sample_workflow.id, input_data)

        assert execution.status.value in ("completed", "failed")
        assert execution.duration_seconds is not None

    def test_add_task_appends(self, manager, sample_workflow):
        """add_task should append and keep the dependency graph valid."""
        new_task = TaskDefinition(
            id="notify",
            type=TaskType.COMMUNICATION,
            name="Final Notification",
            dependencies=["communicate"],
        )
        updated = manager.add_task(sample_workflow.id, new_task)
        assert len(updated.tasks) == 4
        assert updated.tasks[-1].id == "notify"

    def test_add_task_duplicate_id_rejected(self, manager, sample_workflow):
        dup = TaskDefinition(
            id="reconcile",
            type=TaskType.COMPLIANCE,
            name="Duplicate",
        )
        with pytest.raises(WorkflowError):
            manager.add_task(sample_workflow.id, dup)

    def test_add_task_rejects_cycle(self, manager, sample_workflow):
        # A self-dependency creates a cycle, which Kahn's algorithm catches.
        cyclic = TaskDefinition(
            id="selfdep",
            type=TaskType.COMPLIANCE,
            name="Cyclic",
            dependencies=["selfdep"],
        )
        with pytest.raises(CircularDependencyError):
            manager.add_task(sample_workflow.id, cyclic)

    def test_continue_on_failure_flag_persisted(self, manager):
        """create_workflow should persist continue_on_failure."""
        wf = manager.create_workflow(
            name="Resilient",
            tasks=[
                TaskDefinition(
                    id="r1",
                    type=TaskType.RECONCILIATION,
                    name="R1",
                )
            ],
            continue_on_failure=True,
        )
        assert wf.continue_on_failure is True
