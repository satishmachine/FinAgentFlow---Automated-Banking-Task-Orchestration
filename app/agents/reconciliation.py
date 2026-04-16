"""
ReconcileAgent — Handles transaction reconciliation tasks.

Compares transactions between two sources (e.g., internal ledger vs. bank
statement), identifies discrepancies, and produces a reconciliation report
with an AI-generated summary.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.agents.base import TaskAgent
from app.models.task import TaskDefinition, TaskResult, TaskStatus


class ReconcileAgent(TaskAgent):
    """Agent for transaction reconciliation between two data sources."""

    @property
    def agent_type(self) -> str:
        return "reconciliation"

    @property
    def description(self) -> str:
        return "Reconciles transactions between two data sources and identifies discrepancies."

    async def execute(
        self,
        task: TaskDefinition,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Execute a transaction reconciliation.

        Expected parameters:
            - period: Time period to reconcile (e.g., "2026-Q1")
            - source: Name of the source dataset
            - target: Name of the target dataset

        Expected input_data:
            - source_transactions: List of transaction dicts from source
            - target_transactions: List of transaction dicts from target
        """
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.started_at = datetime.now()
        result.logs.append(self.log_step("Starting transaction reconciliation"))

        # Extract parameters
        period = task.parameters.get("period", "unknown")
        source_name = task.parameters.get("source", "source")
        target_name = task.parameters.get("target", "target")

        # Get transaction data
        source_txns: List[Dict] = input_data.get("source_transactions", [])
        target_txns: List[Dict] = input_data.get("target_transactions", [])

        result.logs.append(
            self.log_step(
                f"Reconciling {len(source_txns)} {source_name} txns "
                f"vs {len(target_txns)} {target_name} txns for period: {period}"
            )
        )

        # ── Reconciliation Logic ──────────────────────────────────────────
        source_index = {txn.get("id", idx): txn for idx, txn in enumerate(source_txns)}
        target_index = {txn.get("id", idx): txn for idx, txn in enumerate(target_txns)}

        matched = []
        discrepancies = []
        missing_in_target = []
        missing_in_source = []

        for txn_id, txn in source_index.items():
            if txn_id in target_index:
                target_txn = target_index[txn_id]
                if txn.get("amount") == target_txn.get("amount"):
                    matched.append({"id": txn_id, "amount": txn.get("amount")})
                else:
                    discrepancies.append({
                        "id": txn_id,
                        "source_amount": txn.get("amount"),
                        "target_amount": target_txn.get("amount"),
                        "difference": round(
                            (txn.get("amount", 0) or 0) - (target_txn.get("amount", 0) or 0), 2
                        ),
                    })
            else:
                missing_in_target.append({"id": txn_id, **txn})

        for txn_id, txn in target_index.items():
            if txn_id not in source_index:
                missing_in_source.append({"id": txn_id, **txn})

        # ── Build output ──────────────────────────────────────────────────
        result.output_data = {
            "period": period,
            "source": source_name,
            "target": target_name,
            "summary": {
                "total_source": len(source_txns),
                "total_target": len(target_txns),
                "matched": len(matched),
                "discrepancies": len(discrepancies),
                "missing_in_target": len(missing_in_target),
                "missing_in_source": len(missing_in_source),
            },
            "matched_transactions": matched,
            "discrepancies": discrepancies,
            "missing_in_target": missing_in_target,
            "missing_in_source": missing_in_source,
        }

        result.logs.append(
            self.log_step(
                f"Reconciliation complete: {len(matched)} matched, "
                f"{len(discrepancies)} discrepancies, "
                f"{len(missing_in_target)} missing in target, "
                f"{len(missing_in_source)} missing in source"
            )
        )

        result.status = TaskStatus.COMPLETED
        return result
