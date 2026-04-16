"""
Core module — Configuration, logging, and shared utilities.
"""

from app.core.config import settings
from app.core.logging import setup_logging, get_logger

__all__ = ["settings", "setup_logging", "get_logger"]
