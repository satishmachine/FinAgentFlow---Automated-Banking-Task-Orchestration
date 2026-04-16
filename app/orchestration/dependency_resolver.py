"""
Dependency Resolver — Topological sort of task dependencies.

Resolves the execution order of tasks within a workflow by performing
a topological sort on the dependency graph. Detects circular dependencies.
"""

from typing import Dict, List, Set

from app.core.exceptions import CircularDependencyError
from app.core.logging import get_logger
from app.models.task import TaskDefinition

logger = get_logger("DependencyResolver")


def resolve_dependencies(tasks: List[TaskDefinition]) -> List[List[str]]:
    """
    Resolve task execution order using topological sort.

    Returns a list of "levels", where each level contains task IDs
    that can be executed in parallel (all their dependencies are in
    prior levels).

    Args:
        tasks: List of task definitions with dependency information.

    Returns:
        A list of lists, where each inner list contains task IDs
        that can run in parallel.

    Raises:
        CircularDependencyError: If the dependency graph has cycles.

    Example:
        >>> tasks = [
        ...     TaskDefinition(id="a", type="reconciliation", name="A"),
        ...     TaskDefinition(id="b", type="compliance", name="B", dependencies=["a"]),
        ...     TaskDefinition(id="c", type="communication", name="C", dependencies=["b"]),
        ... ]
        >>> resolve_dependencies(tasks)
        [["a"], ["b"], ["c"]]
    """
    # Build adjacency and in-degree maps
    task_ids: Set[str] = {t.id for t in tasks}
    in_degree: Dict[str, int] = {t.id: 0 for t in tasks}
    dependents: Dict[str, List[str]] = {t.id: [] for t in tasks}

    for task in tasks:
        for dep_id in task.dependencies:
            if dep_id not in task_ids:
                logger.warning(
                    f"Task '{task.id}' depends on unknown task '{dep_id}'. Ignoring."
                )
                continue
            in_degree[task.id] += 1
            dependents[dep_id].append(task.id)

    # Kahn's algorithm — topological sort by levels
    levels: List[List[str]] = []
    current_level = [tid for tid, deg in in_degree.items() if deg == 0]

    processed = 0
    while current_level:
        levels.append(sorted(current_level))  # sorted for determinism
        next_level = []
        for tid in current_level:
            processed += 1
            for dependent in dependents[tid]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_level.append(dependent)
        current_level = next_level

    if processed != len(task_ids):
        remaining = [tid for tid, deg in in_degree.items() if deg > 0]
        raise CircularDependencyError(
            f"Circular dependency detected among tasks: {remaining}"
        )

    logger.info(f"Resolved {len(task_ids)} tasks into {len(levels)} execution levels")
    return levels
