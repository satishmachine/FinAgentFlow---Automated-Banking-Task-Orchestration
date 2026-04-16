"""
Custom exceptions for FinAgentFlow.

Provides a hierarchy of domain-specific exceptions for clean error handling
across all modules.
"""


class FinAgentFlowError(Exception):
    """Base exception for all FinAgentFlow errors."""

    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


# ── Workflow Errors ────────────────────────────────────────────────────────

class WorkflowError(FinAgentFlowError):
    """Error during workflow orchestration."""
    pass


class WorkflowNotFoundError(WorkflowError):
    """Requested workflow does not exist."""
    pass


class CircularDependencyError(WorkflowError):
    """Task dependency graph contains a cycle."""
    pass


class TaskExecutionError(WorkflowError):
    """A task within a workflow failed to execute."""

    def __init__(self, task_id: str, message: str):
        self.task_id = task_id
        super().__init__(f"Task '{task_id}' failed: {message}")


# ── Agent Errors ───────────────────────────────────────────────────────────

class AgentError(FinAgentFlowError):
    """Error within an agent's execution."""
    pass


class AgentNotFoundError(AgentError):
    """Requested agent type is not registered."""
    pass


# ── AI Generation Errors ──────────────────────────────────────────────────

class GenerationError(FinAgentFlowError):
    """Error during AI content generation."""
    pass


class APIRateLimitError(GenerationError):
    """AI API rate limit reached."""
    pass


class APIAuthenticationError(GenerationError):
    """Invalid or missing API credentials."""
    pass


# ── Storage Errors ─────────────────────────────────────────────────────────

class StorageError(FinAgentFlowError):
    """Error during data storage operations."""
    pass


class ArtifactNotFoundError(StorageError):
    """Requested artifact does not exist."""
    pass


# ── Validation Errors ─────────────────────────────────────────────────────

class ValidationError(FinAgentFlowError):
    """Input validation error."""
    pass
