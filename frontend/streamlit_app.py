"""
FinAgentFlow — Streamlit Frontend

A web-based UI for defining, executing, and monitoring banking workflows.
Provides task definition forms, workflow execution dashboards, result viewers,
and audit log browsing.
"""

import json
import requests
import streamlit as st

# ── Page Configuration ────────────────────────────────────────────────────

st.set_page_config(
    page_title="FinAgentFlow",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000/api/v1"

TASK_TYPES = ["reconciliation", "compliance", "communication"]


# ── Sidebar ───────────────────────────────────────────────────────────────

def render_sidebar():
    """Render the navigation sidebar."""
    st.sidebar.title("🏦 FinAgentFlow")
    st.sidebar.markdown("*Automated Banking Task Orchestration*")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Dashboard", "➕ Create Workflow", "▶️ Execute Workflow", "📊 Results", "📋 Audit Logs"],
        index=0,
    )
    st.sidebar.divider()
    st.sidebar.markdown("---")
    st.sidebar.caption("FinAgentFlow v0.1.0 | MIT License")
    return page


# ── Dashboard Page ────────────────────────────────────────────────────────

def page_dashboard():
    """Main dashboard showing overview and system status."""
    st.title("🏠 Dashboard")
    st.markdown("Welcome to **FinAgentFlow** — your AI-powered banking task orchestration platform.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Workflows", "—", help="Total registered workflows")
    with col2:
        st.metric("Executions", "—", help="Total workflow executions")
    with col3:
        st.metric("System Status", "🟢 Online")

    st.divider()
    st.subheader("Quick Start")
    st.markdown("""
    1. **Create a Workflow** — Define your banking tasks and their dependencies.
    2. **Execute** — Run the workflow with your input data.
    3. **Review Results** — View structured data artifacts and AI-generated reports.
    4. **Audit** — Browse step-by-step execution logs.
    """)


# ── Create Workflow Page ──────────────────────────────────────────────────

def page_create_workflow():
    """Workflow creation form."""
    st.title("➕ Create Workflow")

    with st.form("create_workflow_form"):
        name = st.text_input("Workflow Name", placeholder="e.g., Q1 Banking Review")
        description = st.text_area("Description (optional)", placeholder="Describe the workflow purpose...")

        st.subheader("Tasks")
        num_tasks = st.number_input("Number of tasks", min_value=1, max_value=10, value=1)

        tasks = []
        for i in range(int(num_tasks)):
            st.markdown(f"**Task {i + 1}**")
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input(f"Task name", key=f"task_name_{i}")
                task_type = st.selectbox(f"Task type", TASK_TYPES, key=f"task_type_{i}")
            with col2:
                task_desc = st.text_input(f"Description", key=f"task_desc_{i}")
                task_deps = st.text_input(f"Dependencies (comma-separated IDs)", key=f"task_deps_{i}")

            tasks.append({
                "name": task_name,
                "type": task_type,
                "description": task_desc,
                "dependencies": [d.strip() for d in task_deps.split(",") if d.strip()],
            })

        submitted = st.form_submit_button("Create Workflow", type="primary")

        if submitted and name:
            st.success(f"Workflow '{name}' created with {len(tasks)} tasks!")
            st.json({"name": name, "description": description, "tasks": tasks})


# ── Execute Workflow Page ─────────────────────────────────────────────────

def page_execute_workflow():
    """Workflow execution interface."""
    st.title("▶️ Execute Workflow")

    workflow_id = st.text_input("Workflow ID", placeholder="Enter workflow ID")

    with st.form("execute_form"):
        input_json = st.text_area(
            "Input Data (JSON)",
            value='{\n  "source_transactions": [],\n  "target_transactions": []\n}',
            height=200,
        )
        submitted = st.form_submit_button("Execute Workflow", type="primary")

        if submitted and workflow_id:
            with st.spinner("Executing workflow..."):
                st.info(f"Executing workflow: {workflow_id}")
                try:
                    data = json.loads(input_json)
                    st.json(data)
                except json.JSONDecodeError:
                    st.error("Invalid JSON input")


# ── Results Page ──────────────────────────────────────────────────────────

def page_results():
    """Workflow results viewer."""
    st.title("📊 Results")
    st.info("Execute a workflow to see results here.")

    st.subheader("Sample Result Structure")
    st.json({
        "execution_id": "exec-001",
        "status": "completed",
        "results": {
            "task-001": {"matched": 95, "discrepancies": 3},
            "task-002": {"compliance_status": "compliant", "violations": 0},
            "task-003": {"draft_generated": True, "sections": 5},
        },
    })


# ── Audit Logs Page ──────────────────────────────────────────────────────

def page_audit_logs():
    """Audit log viewer."""
    st.title("📋 Audit Logs")
    st.info("Workflow execution audit trails will appear here.")

    st.subheader("Sample Audit Trail")
    st.code("""
2026-04-15 10:00:00 | INFO     | Starting workflow: Q1 Banking Review
2026-04-15 10:00:01 | INFO     | Task 'Reconcile Transactions' started
2026-04-15 10:00:03 | INFO     | Task 'Reconcile Transactions' completed (2.1s)
2026-04-15 10:00:03 | INFO     | Task 'Compliance Summary' started
2026-04-15 10:00:05 | INFO     | Task 'Compliance Summary' completed (1.8s)
2026-04-15 10:00:05 | INFO     | Task 'Draft Customer Notice' started
2026-04-15 10:00:08 | INFO     | Task 'Draft Customer Notice' completed (3.2s)
2026-04-15 10:00:08 | INFO     | Workflow completed successfully (8.1s)
    """, language="text")


# ── Main App ──────────────────────────────────────────────────────────────

def main():
    """Main Streamlit application entry point."""
    page = render_sidebar()

    if "Dashboard" in page:
        page_dashboard()
    elif "Create" in page:
        page_create_workflow()
    elif "Execute" in page:
        page_execute_workflow()
    elif "Results" in page:
        page_results()
    elif "Audit" in page:
        page_audit_logs()


if __name__ == "__main__":
    main()
