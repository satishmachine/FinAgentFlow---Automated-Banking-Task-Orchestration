"""
Prompt templates for AI content generation.

Each template is a structured prompt that the ContentGenerator sends to
GPT-4 or Google Generative AI to produce human-readable banking content.
"""

from typing import Any, Dict


class PromptTemplates:
    """Collection of prompt templates for various banking task outputs."""

    @staticmethod
    def reconciliation_summary(data: Dict[str, Any]) -> str:
        """Prompt for generating a reconciliation summary report."""
        summary = data.get("summary", {})
        return f"""You are a banking operations analyst. Generate a clear, professional 
reconciliation report summary based on the following data:

Period: {data.get('period', 'N/A')}
Source: {data.get('source', 'N/A')}
Target: {data.get('target', 'N/A')}

Results:
- Total source transactions: {summary.get('total_source', 0)}
- Total target transactions: {summary.get('total_target', 0)}
- Matched: {summary.get('matched', 0)}
- Discrepancies found: {summary.get('discrepancies', 0)}
- Missing in target: {summary.get('missing_in_target', 0)}
- Missing in source: {summary.get('missing_in_source', 0)}

Discrepancy details: {data.get('discrepancies', [])}

Generate a professional summary covering:
1. Overview of the reconciliation process
2. Key findings and match rate
3. Discrepancy analysis
4. Recommended actions

Use a formal banking tone. Be specific with numbers."""

    @staticmethod
    def compliance_report(data: Dict[str, Any]) -> str:
        """Prompt for generating a compliance check report."""
        summary = data.get("summary", {})
        return f"""You are a banking compliance officer. Generate a formal compliance 
report based on the following check results:

Compliance Status: {data.get('compliance_status', 'N/A')}
Transactions Checked: {data.get('total_transactions_checked', 0)}
Rules Applied: {data.get('rules_checked', 0)}

Results Summary:
- Violations: {summary.get('violations', 0)}
- Warnings: {summary.get('warnings', 0)}
- Rules Passed: {summary.get('passed', 0)}

Violations: {data.get('violations', [])}
Warnings: {data.get('warnings', [])}

Generate a formal compliance report covering:
1. Executive Summary
2. Compliance status determination
3. Violation details and severity
4. Warning flags for review
5. Remediation recommendations

Use formal regulatory language. Be precise with rule citations."""

    @staticmethod
    def communication_draft(data: Dict[str, Any]) -> str:
        """Prompt for enhancing a customer communication draft."""
        return f"""You are a professional banking communications specialist. 
Enhance the following customer communication draft:

Template: {data.get('template', 'general')}
Subject: {data.get('subject', 'Important Notice')}
Customer: {data.get('customer_name', 'Valued Customer')}
Tone: {data.get('tone', 'professional')}

Draft sections to enhance:
{data.get('full_draft', '')}

Requirements:
1. Replace all [AI-GENERATED SECTION] placeholders with professional content
2. Maintain the specified tone throughout
3. Incorporate any data context into the narrative
4. Keep the communication concise and actionable
5. Follow banking industry communication standards

Return the complete, polished communication ready to send."""

    @staticmethod
    def task_summary(task_name: str, task_type: str, output_data: Dict[str, Any]) -> str:
        """Generic prompt for summarizing any task result."""
        return f"""You are a banking operations assistant. Generate a brief, clear summary 
of the following completed task:

Task Name: {task_name}
Task Type: {task_type}
Output Data: {output_data}

Provide a 2-3 paragraph summary covering:
1. What was done
2. Key findings or results
3. Any notable items requiring attention

Use professional banking language."""
