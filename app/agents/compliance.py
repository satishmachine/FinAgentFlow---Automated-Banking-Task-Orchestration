"""
ComplianceAgent — Generates compliance summaries and checks.

Analyzes financial data against configurable compliance rules and produces
structured reports with an AI-generated narrative summary.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.agents.base import TaskAgent
from app.models.task import TaskDefinition, TaskResult, TaskStatus


# Default compliance rules
DEFAULT_RULES = [
    {
        "id": "rule-001",
        "name": "Transaction Limit",
        "description": "Single transactions must not exceed $50,000 without approval.",
        "threshold": 50_000,
        "field": "amount",
        "check": "max_value",
    },
    {
        "id": "rule-002",
        "name": "Daily Volume Cap",
        "description": "Daily transaction volume must not exceed 500 transactions.",
        "threshold": 500,
        "field": "count",
        "check": "max_count",
    },
    {
        "id": "rule-003",
        "name": "Suspicious Activity",
        "description": "Flag transactions with amounts just below reporting thresholds.",
        "threshold": 10_000,
        "field": "amount",
        "check": "structuring_detection",
    },
]


class ComplianceAgent(TaskAgent):
    """Agent for running compliance checks and generating compliance summaries."""

    @property
    def agent_type(self) -> str:
        return "compliance"

    @property
    def description(self) -> str:
        return "Runs compliance checks against configurable rules and generates compliance reports."

    async def execute(
        self,
        task: TaskDefinition,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Execute compliance checks.

        Expected parameters:
            - rules: Optional list of rule overrides (uses defaults if not provided)

        Expected input_data:
            - transactions: List of transaction dicts to check
        """
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.started_at = datetime.now()
        result.logs.append(self.log_step("Starting compliance check"))

        # Load rules
        rules = task.parameters.get("rules", DEFAULT_RULES)
        transactions: List[Dict] = input_data.get("transactions", [])

        # Also accept upstream reconciliation data
        if not transactions and context:
            for task_result in context.values():
                if isinstance(task_result, dict) and "matched_transactions" in task_result:
                    transactions = task_result.get("matched_transactions", [])
                    break

        result.logs.append(
            self.log_step(f"Checking {len(transactions)} transactions against {len(rules)} rules")
        )

        # ── Run Checks ────────────────────────────────────────────────────
        violations = []
        warnings = []
        passed_rules = []

        for rule in rules:
            rule_id = rule.get("id", "unknown")
            check_type = rule.get("check", "")
            threshold = rule.get("threshold", 0)

            if check_type == "max_value":
                flagged = [
                    txn for txn in transactions
                    if (txn.get("amount", 0) or 0) > threshold
                ]
                if flagged:
                    violations.append({
                        "rule_id": rule_id,
                        "rule_name": rule.get("name"),
                        "description": rule.get("description"),
                        "flagged_count": len(flagged),
                        "flagged_transactions": [
                            {"id": t.get("id"), "amount": t.get("amount")} for t in flagged[:10]
                        ],
                    })
                else:
                    passed_rules.append(rule_id)

            elif check_type == "max_count":
                if len(transactions) > threshold:
                    violations.append({
                        "rule_id": rule_id,
                        "rule_name": rule.get("name"),
                        "description": rule.get("description"),
                        "actual_count": len(transactions),
                        "threshold": threshold,
                    })
                else:
                    passed_rules.append(rule_id)

            elif check_type == "structuring_detection":
                suspicious = [
                    txn for txn in transactions
                    if 0.8 * threshold <= (txn.get("amount", 0) or 0) < threshold
                ]
                if suspicious:
                    warnings.append({
                        "rule_id": rule_id,
                        "rule_name": rule.get("name"),
                        "description": rule.get("description"),
                        "suspicious_count": len(suspicious),
                        "suspicious_transactions": [
                            {"id": t.get("id"), "amount": t.get("amount")} for t in suspicious[:10]
                        ],
                    })
                else:
                    passed_rules.append(rule_id)

        # ── Build output ──────────────────────────────────────────────────
        compliance_status = "compliant" if not violations else "non_compliant"

        result.output_data = {
            "compliance_status": compliance_status,
            "total_transactions_checked": len(transactions),
            "rules_checked": len(rules),
            "summary": {
                "violations": len(violations),
                "warnings": len(warnings),
                "passed": len(passed_rules),
            },
            "violations": violations,
            "warnings": warnings,
            "passed_rules": passed_rules,
        }

        result.logs.append(
            self.log_step(
                f"Compliance check complete: status={compliance_status}, "
                f"{len(violations)} violations, {len(warnings)} warnings"
            )
        )

        result.status = TaskStatus.COMPLETED
        return result
