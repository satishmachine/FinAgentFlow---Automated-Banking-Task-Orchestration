"""
FinAgentFlow — Main Entry Point

Provides CLI commands to start the FastAPI backend, Streamlit frontend,
or run a demo workflow.

Usage:
    python main.py api        # Start the FastAPI backend
    python main.py ui         # Start the Streamlit frontend
    python main.py demo       # Run a demo workflow
    python main.py --help     # Show help
"""

import argparse
import asyncio
import json
import sys
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger


def start_api():
    """Start the FastAPI backend server."""
    from app.api.app import create_app

    setup_logging()
    logger = get_logger("main")
    logger.info(f"Starting {settings.app_name} API on {settings.api_host}:{settings.api_port}")

    app = create_app()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


def start_ui():
    """Start the Streamlit frontend."""
    import subprocess

    setup_logging()
    logger = get_logger("main")
    logger.info(f"Starting Streamlit UI on port {settings.streamlit_port}")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/streamlit_app.py",
        "--server.port", str(settings.streamlit_port),
        "--server.headless", "true",
    ])


async def run_demo():
    """Run a demo workflow showing the full pipeline."""
    from pathlib import Path

    setup_logging()
    logger = get_logger("demo")
    logger.info("=" * 60)
    logger.info("FinAgentFlow — Demo Workflow")
    logger.info("=" * 60)

    # Load sample data
    samples_dir = Path("data/samples")
    with open(samples_dir / "ledger_transactions.json") as f:
        ledger = json.load(f)
    with open(samples_dir / "bank_statement.json") as f:
        bank = json.load(f)

    logger.info(f"Loaded {len(ledger)} ledger transactions and {len(bank)} bank transactions")

    # Create workflow
    from app.models.task import TaskDefinition, TaskType
    from app.orchestration.workflow_manager import WorkflowManager

    manager = WorkflowManager()
    workflow = manager.create_workflow(
        name="Q1 2026 Banking Review (Demo)",
        description="Demo workflow: reconcile → compliance → communication",
        tasks=[
            TaskDefinition(
                id="reconcile",
                type=TaskType.RECONCILIATION,
                name="Reconcile Q1 Transactions",
                parameters={"period": "2026-Q1", "source": "ledger", "target": "bank_statement"},
            ),
            TaskDefinition(
                id="comply",
                type=TaskType.COMPLIANCE,
                name="Run Compliance Checks",
                dependencies=["reconcile"],
            ),
            TaskDefinition(
                id="draft",
                type=TaskType.COMMUNICATION,
                name="Draft Customer Report",
                parameters={"template": "quarterly_review", "customer_name": "Demo Customer"},
                dependencies=["comply"],
            ),
        ],
    )

    logger.info(f"Created workflow: {workflow.name} (id={workflow.id})")

    # Execute
    logger.info("Executing workflow...")
    execution = await manager.run_workflow(
        workflow.id,
        input_data={
            "source_transactions": ledger,
            "target_transactions": bank,
            "transactions": ledger,
        },
    )

    # Print results
    logger.info(f"Execution completed: status={execution.status.value}")
    logger.info(f"Duration: {execution.duration_seconds:.2f}s")

    for task_id, result in execution.results.items():
        logger.info(f"\n{'─' * 40}")
        logger.info(f"Task: {task_id}")
        logger.info(f"Status: {result.status.value}")
        logger.info(f"Output: {json.dumps(result.output_data, indent=2, default=str)[:500]}")

    # Save artifacts
    from app.storage.artifact_store import ArtifactStore
    from app.models.artifact import Artifact, ArtifactType

    store = ArtifactStore()
    for task_id, result in execution.results.items():
        artifact = Artifact(
            workflow_id=workflow.id,
            task_id=task_id,
            type=ArtifactType.JSON_DATA,
            name=f"{task_id}_output",
            content=result.output_data,
        )
        path = store.save_artifact(artifact)
        logger.info(f"Artifact saved: {path}")

    logger.info("=" * 60)
    logger.info("Demo complete!")
    logger.info("=" * 60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FinAgentFlow — Automated Banking Task Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  api     Start the FastAPI backend server
  ui      Start the Streamlit frontend
  demo    Run a demo workflow with sample data

Examples:
  python main.py api
  python main.py ui
  python main.py demo
        """,
    )
    parser.add_argument(
        "command",
        choices=["api", "ui", "demo"],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "api":
        start_api()
    elif args.command == "ui":
        start_ui()
    elif args.command == "demo":
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()
