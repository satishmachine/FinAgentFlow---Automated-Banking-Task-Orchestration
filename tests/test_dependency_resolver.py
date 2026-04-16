"""
Unit tests for the dependency resolver.
"""

import pytest
from app.models.task import TaskDefinition, TaskType
from app.orchestration.dependency_resolver import resolve_dependencies
from app.core.exceptions import CircularDependencyError


class TestDependencyResolver:
    """Tests for the topological sort dependency resolver."""

    def test_no_dependencies(self):
        tasks = [
            TaskDefinition(id="a", type=TaskType.RECONCILIATION, name="A"),
            TaskDefinition(id="b", type=TaskType.COMPLIANCE, name="B"),
        ]
        levels = resolve_dependencies(tasks)
        assert len(levels) == 1
        assert set(levels[0]) == {"a", "b"}

    def test_linear_dependencies(self):
        tasks = [
            TaskDefinition(id="a", type=TaskType.RECONCILIATION, name="A"),
            TaskDefinition(id="b", type=TaskType.COMPLIANCE, name="B", dependencies=["a"]),
            TaskDefinition(id="c", type=TaskType.COMMUNICATION, name="C", dependencies=["b"]),
        ]
        levels = resolve_dependencies(tasks)
        assert levels == [["a"], ["b"], ["c"]]

    def test_diamond_dependencies(self):
        tasks = [
            TaskDefinition(id="a", type=TaskType.RECONCILIATION, name="A"),
            TaskDefinition(id="b", type=TaskType.COMPLIANCE, name="B", dependencies=["a"]),
            TaskDefinition(id="c", type=TaskType.COMPLIANCE, name="C", dependencies=["a"]),
            TaskDefinition(id="d", type=TaskType.COMMUNICATION, name="D", dependencies=["b", "c"]),
        ]
        levels = resolve_dependencies(tasks)
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}
        assert levels[2] == ["d"]

    def test_circular_dependency_raises(self):
        tasks = [
            TaskDefinition(id="a", type=TaskType.RECONCILIATION, name="A", dependencies=["b"]),
            TaskDefinition(id="b", type=TaskType.COMPLIANCE, name="B", dependencies=["a"]),
        ]
        with pytest.raises(CircularDependencyError):
            resolve_dependencies(tasks)

    def test_single_task(self):
        tasks = [
            TaskDefinition(id="a", type=TaskType.RECONCILIATION, name="A"),
        ]
        levels = resolve_dependencies(tasks)
        assert levels == [["a"]]
