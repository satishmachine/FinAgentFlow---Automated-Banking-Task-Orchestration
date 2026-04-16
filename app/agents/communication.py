"""
CommunicationAgent — Drafts customer communications.

Uses AI content generation to produce customer-facing communications
such as notices, reports, and summaries based on workflow context.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from app.agents.base import TaskAgent
from app.models.task import TaskDefinition, TaskResult, TaskStatus


# Communication templates
TEMPLATES = {
    "quarterly_review": {
        "subject": "Quarterly Account Review Summary",
        "sections": ["greeting", "account_summary", "key_findings", "action_items", "closing"],
    },
    "compliance_notice": {
        "subject": "Compliance Review Notification",
        "sections": ["greeting", "compliance_status", "details", "next_steps", "closing"],
    },
    "reconciliation_report": {
        "subject": "Transaction Reconciliation Report",
        "sections": ["greeting", "reconciliation_summary", "discrepancies", "resolution", "closing"],
    },
    "general": {
        "subject": "Important Account Notification",
        "sections": ["greeting", "body", "closing"],
    },
}


class CommunicationAgent(TaskAgent):
    """Agent for drafting customer communications based on workflow context."""

    @property
    def agent_type(self) -> str:
        return "communication"

    @property
    def description(self) -> str:
        return "Drafts customer-facing communications and reports using AI content generation."

    async def execute(
        self,
        task: TaskDefinition,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Draft a customer communication.

        Expected parameters:
            - template: Template name (e.g., "quarterly_review", "compliance_notice")
            - customer_name: Optional customer name for personalization
            - tone: Optional tone (e.g., "formal", "friendly"). Defaults to "professional"

        Expected input_data / context:
            - Data from upstream tasks to incorporate into the communication
        """
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.started_at = datetime.now()
        result.logs.append(self.log_step("Starting communication drafting"))

        # Extract parameters
        template_name = task.parameters.get("template", "general")
        customer_name = task.parameters.get("customer_name", "Valued Customer")
        tone = task.parameters.get("tone", "professional")

        template = TEMPLATES.get(template_name, TEMPLATES["general"])

        result.logs.append(
            self.log_step(f"Using template: {template_name}, tone: {tone}")
        )

        # ── Build Communication Draft ─────────────────────────────────────
        # Gather context from upstream tasks
        context_summary = self._summarize_context(context or {})

        draft_sections = {}
        for section in template["sections"]:
            draft_sections[section] = self._generate_section(
                section, customer_name, context_summary, tone
            )

        full_draft = "\n\n".join(draft_sections.values())

        # ── Build output ──────────────────────────────────────────────────
        result.output_data = {
            "template": template_name,
            "subject": template["subject"],
            "customer_name": customer_name,
            "tone": tone,
            "sections": draft_sections,
            "full_draft": full_draft,
            "context_used": list((context or {}).keys()),
            "requires_ai_enhancement": True,  # Flag for AI generation layer
        }

        result.logs.append(
            self.log_step(
                f"Communication draft generated: {len(full_draft)} chars, "
                f"{len(draft_sections)} sections"
            )
        )

        result.status = TaskStatus.COMPLETED
        return result

    @staticmethod
    def _summarize_context(context: Dict[str, Any]) -> str:
        """Extract key points from upstream task results for the communication."""
        points = []
        for task_id, data in context.items():
            if isinstance(data, dict):
                if "summary" in data:
                    points.append(f"- {task_id}: {data['summary']}")
                elif "compliance_status" in data:
                    points.append(f"- Compliance status: {data['compliance_status']}")
        return "\n".join(points) if points else "No upstream context available."

    @staticmethod
    def _generate_section(
        section: str, customer_name: str, context: str, tone: str
    ) -> str:
        """
        Generate a placeholder section.

        In production, this would call the AI generation layer.
        Currently returns structured placeholders that the ContentGenerator
        will enhance with GPT-4.
        """
        section_templates = {
            "greeting": f"Dear {customer_name},",
            "account_summary": (
                f"[AI-GENERATED SECTION: Account Summary]\n"
                f"Context:\n{context}\n"
                f"Tone: {tone}"
            ),
            "key_findings": (
                f"[AI-GENERATED SECTION: Key Findings]\n"
                f"Context:\n{context}\n"
                f"Tone: {tone}"
            ),
            "compliance_status": (
                f"[AI-GENERATED SECTION: Compliance Status]\n"
                f"Context:\n{context}\n"
                f"Tone: {tone}"
            ),
            "reconciliation_summary": (
                f"[AI-GENERATED SECTION: Reconciliation Summary]\n"
                f"Context:\n{context}\n"
                f"Tone: {tone}"
            ),
            "discrepancies": (
                f"[AI-GENERATED SECTION: Discrepancies]\n"
                f"Context:\n{context}"
            ),
            "details": (
                f"[AI-GENERATED SECTION: Details]\n"
                f"Context:\n{context}"
            ),
            "action_items": "[AI-GENERATED SECTION: Action Items]",
            "next_steps": "[AI-GENERATED SECTION: Next Steps]",
            "resolution": "[AI-GENERATED SECTION: Resolution Steps]",
            "body": (
                f"[AI-GENERATED SECTION: Body]\n"
                f"Context:\n{context}\n"
                f"Tone: {tone}"
            ),
            "closing": (
                "Thank you for your continued trust.\n\n"
                "Sincerely,\n"
                "FinAgentFlow Banking Operations"
            ),
        }
        return section_templates.get(section, f"[Section: {section}]")
