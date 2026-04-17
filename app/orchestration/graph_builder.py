"""
Graph Builder — Constructs a LangGraph StateGraph for workflow execution.

Translates a WorkflowDefinition into a LangGraph execution graph where
each node is a task agent and edges represent dependencies.
"""

import asyncio
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.registry import AgentRegistry
from app.core.logging import get_logger
from app.models.task import TaskDefinition, TaskResult
from app.orchestration.dependency_resolver import resolve_dependencies

logger = get_logger("GraphBuilder")


class WorkflowState(TypedDict, total=False):
    """State that flows through the LangGraph workflow."""
    input_data: Dict[str, Any]
    results: Dict[str, Dict[str, Any]]
    logs: List[str]
    current_task: str
    status: str
    failed_tasks: List[str]


def build_workflow_graph(
    tasks: List[TaskDefinition],
    continue_on_failure: bool = False,
) -> StateGraph:
    """
    Build a LangGraph StateGraph from a list of task definitions.

    Each task becomes a node in the graph. Edges follow the dependency
    order determined by the dependency resolver.

    Args:
        tasks: List of task definitions for the workflow.
        continue_on_failure: If True, a failing task is recorded in the
            shared state and execution continues with downstream tasks.
            If False, the exception propagates and the workflow aborts.

    Returns:
        A compiled LangGraph StateGraph ready for execution.
    """
    task_map = {t.id: t for t in tasks}
    execution_levels = resolve_dependencies(tasks)

    logger.info(
        f"Building graph with {len(tasks)} tasks in {len(execution_levels)} levels "
        f"(continue_on_failure={continue_on_failure})"
    )

    # ── Create the graph ──────────────────────────────────────────────────
    graph = StateGraph(WorkflowState)

    # Create a node function for each task
    for task in tasks:

        def make_node(task_def: TaskDefinition):
            """Create a closure for the task node."""

            async def node_fn(state: WorkflowState) -> WorkflowState:
                agent = AgentRegistry.get(task_def.type.value)

                # Collect context from upstream results
                context = {}
                for dep_id in task_def.dependencies:
                    if dep_id in state["results"]:
                        context[dep_id] = state["results"][dep_id]

                try:
                    result: TaskResult = await agent.run(
                        task_def, state["input_data"], context
                    )
                except Exception as e:
                    if not continue_on_failure:
                        raise
                    logger.warning(
                        f"Task '{task_def.id}' raised but continue_on_failure=True: {e}"
                    )
                    state.setdefault("failed_tasks", []).append(task_def.id)
                    state["results"][task_def.id] = {"error": str(e)}
                    state["logs"].append(
                        f"[{task_def.id}] FAILED: {e}"
                    )
                    state["current_task"] = task_def.id
                    state["status"] = "failed"
                    return state

                state["results"][task_def.id] = result.output_data
                state["logs"].extend(result.logs)
                state["current_task"] = task_def.id
                state["status"] = result.status.value
                if result.status.value == "failed":
                    state.setdefault("failed_tasks", []).append(task_def.id)
                return state

            return node_fn

        graph.add_node(task.id, make_node(task))

    # ── Wire edges based on dependency levels ─────────────────────────────
    flat_order = [tid for level in execution_levels for tid in level]

    if flat_order:
        graph.set_entry_point(flat_order[0])

        for i in range(len(flat_order) - 1):
            graph.add_edge(flat_order[i], flat_order[i + 1])

        graph.add_edge(flat_order[-1], END)

    logger.info("Workflow graph constructed successfully")
    return graph.compile()
