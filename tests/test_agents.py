"""
Unit tests for task agents.
"""

import pytest
from app.agents.reconciliation import ReconcileAgent
from app.agents.compliance import ComplianceAgent
from app.agents.communication import CommunicationAgent
from app.agents.registry import AgentRegistry
from app.models.task import TaskDefinition, TaskType, TaskStatus


@pytest.fixture
def sample_reconciliation_task():
    return TaskDefinition(
        id="task-001",
        type=TaskType.RECONCILIATION,
        name="Test Reconciliation",
        parameters={"period": "2026-Q1", "source": "ledger", "target": "bank"},
    )


@pytest.fixture
def sample_transactions():
    return {
        "source_transactions": [
            {"id": "txn-1", "amount": 100.00, "date": "2026-01-15"},
            {"id": "txn-2", "amount": 250.50, "date": "2026-02-10"},
            {"id": "txn-3", "amount": 500.00, "date": "2026-03-01"},
        ],
        "target_transactions": [
            {"id": "txn-1", "amount": 100.00, "date": "2026-01-15"},
            {"id": "txn-2", "amount": 245.50, "date": "2026-02-10"},  # Discrepancy
            {"id": "txn-4", "amount": 300.00, "date": "2026-03-15"},  # Missing in source
        ],
    }


class TestReconcileAgent:
    @pytest.mark.asyncio
    async def test_reconciliation(self, sample_reconciliation_task, sample_transactions):
        agent = ReconcileAgent()
        result = await agent.run(sample_reconciliation_task, sample_transactions)

        assert result.status == TaskStatus.COMPLETED
        assert result.output_data["summary"]["matched"] == 1
        assert result.output_data["summary"]["discrepancies"] == 1
        assert result.output_data["summary"]["missing_in_target"] == 1
        assert result.output_data["summary"]["missing_in_source"] == 1

    @pytest.mark.asyncio
    async def test_empty_reconciliation(self, sample_reconciliation_task):
        agent = ReconcileAgent()
        result = await agent.run(sample_reconciliation_task, {})
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data["summary"]["matched"] == 0


class TestComplianceAgent:
    @pytest.mark.asyncio
    async def test_compliance_pass(self):
        task = TaskDefinition(
            id="task-002", type=TaskType.COMPLIANCE, name="Compliance Check"
        )
        agent = ComplianceAgent()
        result = await agent.run(task, {
            "transactions": [
                {"id": "t1", "amount": 100},
                {"id": "t2", "amount": 200},
            ]
        })
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data["compliance_status"] == "compliant"


class TestCommunicationAgent:
    @pytest.mark.asyncio
    async def test_communication_draft(self):
        task = TaskDefinition(
            id="task-003",
            type=TaskType.COMMUNICATION,
            name="Draft Notice",
            parameters={"template": "quarterly_review", "customer_name": "John Doe"},
        )
        agent = CommunicationAgent()
        result = await agent.run(task, {})
        assert result.status == TaskStatus.COMPLETED
        assert "full_draft" in result.output_data
        assert "John Doe" in result.output_data["full_draft"]


class TestAgentRegistry:
    def test_register_defaults(self):
        AgentRegistry.register_defaults()
        assert AgentRegistry.is_registered("reconciliation")
        assert AgentRegistry.is_registered("compliance")
        assert AgentRegistry.is_registered("communication")

    def test_get_agent(self):
        AgentRegistry.register_defaults()
        agent = AgentRegistry.get("reconciliation")
        assert isinstance(agent, ReconcileAgent)

    def test_list_agents(self):
        AgentRegistry.register_defaults()
        agents = AgentRegistry.list_agents()
        assert len(agents) >= 3
