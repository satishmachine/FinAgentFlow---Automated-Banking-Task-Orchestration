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


class WorkflowState(TypedDict):
    """State that flows through the LangGraph workflow."""
    input_data: Dict[str, Any]
    results: Dict[str, Dict[str, Any]]
    logs: List[str]
    current_task: str
    status: str


def build_workflow_graph(
    tasks: List[TaskDefinition],
) -> StateGraph:
    """
    Build a LangGraph StateGraph from a list of task definitions.

    Each task becomes a node in the graph. Edges follow the dependency
    order determined by the dependency resolver.

    Args:
        tasks: List of task definitions for the workflow.

    Returns:
        A compiled LangGraph StateGraph ready for execution.
    """
    task_map = {t.id: t for t in tasks}
    execution_levels = resolve_dependencies(tasks)

    logger.info(
        f"Building graph with {len(tasks)} tasks in {len(execution_levels)} levels"
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

                result: TaskResult = await agent.run(
                    task_def, state["input_data"], context
                )

                state["results"][task_def.id] = result.output_data
                state["logs"].extend(result.logs)
                state["current_task"] = task_def.id
                state["status"] = result.status.value
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
