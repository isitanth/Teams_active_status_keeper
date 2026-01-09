"""Logging configuration for Teams Active Status Keeper."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .constants import APP_NAME, LOG_BACKUP_COUNT, LOG_MAX_BYTES


def get_log_dir() -> Path:
    """Get the log directory path."""
    log_dir = Path.home() / "Library" / "Logs" / APP_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_file() -> Path:
    """Get the log file path."""
    return get_log_dir() / "teams_active.log"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging with file rotation and console output.

    Args:
        level: Logging level (default: INFO).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("teams_active")
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(
        get_log_file(),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
