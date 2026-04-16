"""
Logging configuration — sets up structured logging with audit trail support.

Every workflow execution gets its own log file for full auditability.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings, LOGS_DIR


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure the root logger with console and file handlers.

    Args:
        level: Log level override (e.g. "DEBUG"). Falls back to settings.
    """
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)

    # Ensure log directory exists
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)

    # Formatter
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(fmt)

    # File handler (rotating daily)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        Path(settings.log_dir) / f"finagentflow_{today}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(fmt)

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(console)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger scoped under the app namespace."""
    return logging.getLogger(f"finagentflow.{name}")


def get_audit_logger(workflow_id: str) -> logging.Logger:
    """
    Create a dedicated audit logger for a specific workflow execution.

    Each workflow gets its own log file under `logs/audit/`.

    Args:
        workflow_id: Unique identifier for the workflow execution.

    Returns:
        A logger that writes to both console and a workflow-specific file.
    """
    audit_dir = Path(settings.log_dir) / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"finagentflow.audit.{workflow_id}")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh = logging.FileHandler(
            audit_dir / f"workflow_{workflow_id}.log",
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
