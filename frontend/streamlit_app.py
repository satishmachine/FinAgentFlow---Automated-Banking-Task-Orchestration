"""
FinAgentFlow — Streamlit Frontend

A web-based UI for defining, executing, and monitoring banking workflows.
Provides task definition forms, workflow execution dashboards, result viewers,
and audit log browsing.
"""

import json
import os
from typing import Any, Dict, List, Optional

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

API_BASE = os.getenv("FINAGENT_API_BASE", "http://localhost:8000/api/v1")
DEFAULT_TIMEOUT = 120

TASK_TYPES = ["reconciliation", "compliance", "communication"]


# ── API Helpers ───────────────────────────────────────────────────────────

def _api_get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{API_BASE}{path}", timeout=DEFAULT_TIMEOUT, **kwargs)


def _api_post(path: str, **kwargs) -> requests.Response:
    return requests.post(f"{API_BASE}{path}", timeout=DEFAULT_TIMEOUT, **kwargs)


def api_health() -> bool:
    try:
        r = _api_get("/health")
        return r.status_code == 200
    except Exception:
        return False


def api_list_workflows() -> List[Dict[str, Any]]:
    r = _api_get("/workflows")
    r.raise_for_status()
    return r.json()


def api_list_executions(workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
    path = f"/workflows/{workflow_id}/executions" if workflow_id else "/executions"
    r = _api_get(path)
    r.raise_for_status()
    return r.json()


def api_create_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    r = _api_post("/workflows", json=payload)
    if r.status_code >= 400:
        raise RuntimeError(r.json().get("detail", r.text))
    return r.json()


def api_run_workflow(workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    r = _api_post(f"/workflows/{workflow_id}/run", json={"input_data": input_data})
    if r.status_code >= 400:
        raise RuntimeError(r.json().get("detail", r.text))
    return r.json()


def api_list_artifacts(workflow_id: str) -> List[Dict[str, Any]]:
    r = _api_get(f"/artifacts/{workflow_id}")
    r.raise_for_status()
    return r.json().get("artifacts", [])


def api_get_audit_log(execution_id: str) -> Optional[str]:
    r = _api_get(f"/executions/{execution_id}/audit-log")
    if r.status_code == 200:
        return r.json().get("content", "")
    return None


def api_download_artifact(workflow_id: str, task_id: str, artifact_id: str) -> bytes:
    r = _api_get(f"/artifacts/{workflow_id}/{task_id}/{artifact_id}/download")
    r.raise_for_status()
    return r.content


# ── Sidebar ───────────────────────────────────────────────────────────────

def render_sidebar() -> str:
    """Render the navigation sidebar."""
    st.sidebar.title("🏦 FinAgentFlow")
    st.sidebar.markdown("*Automated Banking Task Orchestration*")
    st.sidebar.caption(f"API: `{API_BASE}`")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Dashboard", "➕ Create Workflow", "▶️ Execute Workflow", "📊 Results", "📋 Audit Logs"],
        index=0,
    )
    st.sidebar.divider()
    online = api_health()
    st.sidebar.markdown(
        f"**Backend:** {'🟢 online' if online else '🔴 offline'}"
    )
    st.sidebar.caption("FinAgentFlow v0.1.0 | MIT License")
    return page


# ── Dashboard Page ────────────────────────────────────────────────────────

def page_dashboard():
    """Main dashboard showing overview and system status."""
    st.title("🏠 Dashboard")
    st.markdown("Welcome to **FinAgentFlow** — your AI-powered banking task orchestration platform.")

    online = api_health()
    workflows: List[Dict[str, Any]] = []
    executions: List[Dict[str, Any]] = []
    if online:
        try:
            workflows = api_list_workflows()
            executions = api_list_executions()
        except Exception as e:
            st.warning(f"Failed to load dashboard data: {e}")

    completed = sum(1 for ex in executions if ex.get("status") == "completed")
    failed = sum(1 for ex in executions if ex.get("status") == "failed")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Workflows", len(workflows))
    col2.metric("Executions", len(executions))
    col3.metric("Completed", completed)
    col4.metric("System Status", "🟢 Online" if online else "🔴 Offline")

    st.divider()

    if workflows:
        st.subheader("Registered Workflows")
        st.dataframe(
            [
                {
                    "ID": w["id"],
                    "Name": w["name"],
                    "Tasks": w["task_count"],
                    "Continue on Failure": w.get("continue_on_failure", False),
                }
                for w in workflows
            ],
            use_container_width=True,
        )

    if executions:
        st.subheader("Recent Executions")
        st.dataframe(
            [
                {
                    "Execution ID": ex["execution_id"],
                    "Workflow ID": ex["workflow_id"],
                    "Status": ex["status"],
                    "Duration (s)": ex.get("duration_seconds"),
                    "Error": ex.get("error") or "",
                }
                for ex in executions[-10:]
            ],
            use_container_width=True,
        )

    st.divider()
    st.subheader("Quick Start")
    st.markdown(
        "1. **Create a Workflow** — Define your banking tasks and their dependencies.\n"
        "2. **Execute** — Run the workflow with your input data.\n"
        "3. **Review Results** — View structured data artifacts and AI-generated reports.\n"
        "4. **Audit** — Browse step-by-step execution logs."
    )


# ── Create Workflow Page ──────────────────────────────────────────────────

def page_create_workflow():
    """Workflow creation form — POSTs to /workflows."""
    st.title("➕ Create Workflow")
    st.caption("Define a sequence of banking tasks. Task IDs are auto-generated.")

    with st.form("create_workflow_form"):
        name = st.text_input("Workflow Name", placeholder="e.g., Q1 Banking Review")
        description = st.text_area(
            "Description (optional)", placeholder="Describe the workflow purpose..."
        )
        continue_on_failure = st.checkbox(
            "Continue on task failure",
            value=False,
            help="If enabled, remaining tasks still run when one fails.",
        )

        st.subheader("Tasks")
        num_tasks = st.number_input("Number of tasks", min_value=1, max_value=10, value=1)

        tasks = []
        for i in range(int(num_tasks)):
            st.markdown(f"**Task {i + 1}**")
            col1, col2 = st.columns(2)
            with col1:
                task_id = st.text_input(
                    "Task ID (for dependencies)",
                    key=f"task_id_{i}",
                    placeholder=f"task-{i + 1}",
                )
                task_name = st.text_input("Task name", key=f"task_name_{i}")
                task_type = st.selectbox("Task type", TASK_TYPES, key=f"task_type_{i}")
            with col2:
                task_desc = st.text_input("Description", key=f"task_desc_{i}")
                task_deps = st.text_input(
                    "Dependencies (comma-separated IDs)", key=f"task_deps_{i}"
                )
                task_params = st.text_area(
                    "Parameters (JSON)", value="{}", height=80, key=f"task_params_{i}"
                )

            task: Dict[str, Any] = {
                "type": task_type,
                "name": task_name or f"Task {i + 1}",
                "description": task_desc or None,
                "dependencies": [d.strip() for d in task_deps.split(",") if d.strip()],
            }
            if task_id.strip():
                task["id"] = task_id.strip()
            try:
                task["parameters"] = json.loads(task_params or "{}")
            except json.JSONDecodeError:
                task["parameters"] = {}
                st.warning(f"Task {i + 1}: invalid JSON in parameters, using empty dict.")
            tasks.append(task)

        submitted = st.form_submit_button("Create Workflow", type="primary")

    if submitted:
        if not name:
            st.error("Workflow name is required.")
            return
        payload = {
            "name": name,
            "description": description or None,
            "continue_on_failure": continue_on_failure,
            "tasks": tasks,
        }
        try:
            wf = api_create_workflow(payload)
            st.success(f"Workflow '{wf['name']}' created (id={wf['id']})")
            st.json(wf)
            st.info("Copy the workflow ID to execute it on the Execute Workflow page.")
        except Exception as e:
            st.error(f"Create failed: {e}")


# ── Execute Workflow Page ─────────────────────────────────────────────────

def page_execute_workflow():
    """Workflow execution interface — POSTs /workflows/{id}/run."""
    st.title("▶️ Execute Workflow")

    try:
        workflows = api_list_workflows()
    except Exception as e:
        st.error(f"Failed to load workflows: {e}")
        workflows = []

    if not workflows:
        st.info("No workflows found. Create one on the **Create Workflow** page first.")
        return

    options = {f"{w['name']} ({w['id']})": w["id"] for w in workflows}
    label = st.selectbox("Select workflow", list(options.keys()))
    workflow_id = options[label]

    sample_path = os.path.join("data", "samples")
    default_input: Dict[str, Any] = {}
    try:
        bank_path = os.path.join(sample_path, "bank_statement.json")
        ledger_path = os.path.join(sample_path, "ledger_transactions.json")
        if os.path.exists(bank_path) and os.path.exists(ledger_path):
            with open(bank_path, encoding="utf-8") as f:
                default_input["bank_statement"] = json.load(f)
            with open(ledger_path, encoding="utf-8") as f:
                default_input["ledger_transactions"] = json.load(f)
    except Exception:
        default_input = {}

    with st.form("execute_form"):
        input_json = st.text_area(
            "Input Data (JSON)",
            value=json.dumps(default_input, indent=2) if default_input
                  else '{\n  "bank_statement": [],\n  "ledger_transactions": []\n}',
            height=240,
        )
        submitted = st.form_submit_button("Execute Workflow", type="primary")

    if submitted:
        try:
            input_data = json.loads(input_json)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            return

        with st.spinner(f"Executing workflow {workflow_id}..."):
            try:
                result = api_run_workflow(workflow_id, input_data)
            except Exception as e:
                st.error(f"Execution failed: {e}")
                return

        status = result.get("status", "unknown")
        if status == "completed":
            st.success(f"Execution {result['execution_id']} completed")
        elif status == "failed":
            st.error(f"Execution {result['execution_id']} failed: {result.get('error')}")
        else:
            st.warning(f"Execution finished with status: {status}")

        st.metric("Duration (s)", f"{result.get('duration_seconds') or 0:.2f}")
        st.subheader("Task Results")
        st.json(result.get("results", {}))

        # Session storage so Results page can pick it up immediately
        st.session_state["last_execution"] = result


# ── Results Page ──────────────────────────────────────────────────────────

def page_results():
    """Workflow results viewer with artifact download."""
    st.title("📊 Results")

    try:
        workflows = api_list_workflows()
    except Exception as e:
        st.error(f"Failed to load workflows: {e}")
        return

    if not workflows:
        st.info("No workflows yet. Create and execute one first.")
        return

    options = {f"{w['name']} ({w['id']})": w["id"] for w in workflows}
    label = st.selectbox("Workflow", list(options.keys()))
    workflow_id = options[label]

    try:
        executions = api_list_executions(workflow_id)
    except Exception as e:
        st.error(f"Failed to load executions: {e}")
        return

    if not executions:
        st.info("No executions for this workflow yet.")
        return

    exec_options = {
        f"{ex['execution_id']} — {ex['status']}": ex for ex in executions
    }
    ex_label = st.selectbox("Execution", list(exec_options.keys()))
    execution = exec_options[ex_label]

    col1, col2, col3 = st.columns(3)
    col1.metric("Status", execution["status"])
    col2.metric("Duration (s)", f"{execution.get('duration_seconds') or 0:.2f}")
    col3.metric("Tasks", len(execution.get("results", {})))

    if execution.get("error"):
        st.error(execution["error"])

    st.subheader("Task Outputs")
    st.json(execution.get("results", {}))

    st.subheader("Artifacts")
    try:
        artifacts = api_list_artifacts(workflow_id)
    except Exception as e:
        st.warning(f"Could not list artifacts: {e}")
        artifacts = []

    if not artifacts:
        st.caption("No artifacts stored for this workflow yet.")
        return

    for art in artifacts:
        with st.expander(f"{art['name']} ({art['type']}) — {art['artifact_id']}"):
            st.caption(f"Created: {art.get('created_at', '')}")
            st.caption(f"File: {art.get('file_path', '')}")
            task_id = None
            if art.get("file_path"):
                # file_path: .../artifacts/<workflow_id>/<task_id>/<file>
                parts = art["file_path"].replace("\\", "/").split("/")
                if len(parts) >= 3:
                    task_id = parts[-2]
            if task_id:
                try:
                    data = api_download_artifact(workflow_id, task_id, art["artifact_id"])
                    st.download_button(
                        label="⬇️ Download",
                        data=data,
                        file_name=os.path.basename(art.get("file_path") or art["artifact_id"]),
                        key=f"dl_{art['artifact_id']}",
                    )
                except Exception as e:
                    st.warning(f"Download unavailable: {e}")


# ── Audit Logs Page ──────────────────────────────────────────────────────

def page_audit_logs():
    """Audit log viewer — fetches /executions/{id}/audit-log."""
    st.title("📋 Audit Logs")

    try:
        executions = api_list_executions()
    except Exception as e:
        st.error(f"Failed to load executions: {e}")
        return

    if not executions:
        st.info("No executions available yet.")
        return

    exec_options = {
        f"{ex['execution_id']} — wf={ex['workflow_id']} — {ex['status']}": ex["execution_id"]
        for ex in executions
    }
    label = st.selectbox("Execution", list(exec_options.keys()))
    execution_id = exec_options[label]

    content = api_get_audit_log(execution_id)
    if content is None:
        st.warning("Audit log file not found for this execution.")
        return

    st.download_button(
        "⬇️ Download audit log",
        data=content,
        file_name=f"workflow_{execution_id}.log",
    )
    st.code(content, language="text")


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
