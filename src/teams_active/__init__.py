"""
Teams Active Status Keeper.

A background service that keeps Microsoft Teams web version showing as active (green dot).
"""

from __future__ import annotations

from .activity import ActivitySimulator, SessionState
from .config import AppConfig, load_config, save_config
from .constants import (
    APP_NAME,
    DEFAULT_ACTIVITY_INTERVAL,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_TEAMS_URL,
)
from .driver import DriverManager
from .health import HealthMonitor, HealthStatus, format_health_report, read_health_status
from .keeper import TeamsActiveKeeper
from .logging_config import setup_logging
from .notifications import NotificationManager, send_notification
from .retry import RetryConfig, RetryState, randomize_interval, retry_with_backoff

__version__ = "1.0.0"

__all__ = [
    "APP_NAME",
    "DEFAULT_ACTIVITY_INTERVAL",
    "DEFAULT_CHECK_INTERVAL",
    "DEFAULT_TEAMS_URL",
    "ActivitySimulator",
    "AppConfig",
    "DriverManager",
    "HealthMonitor",
    "HealthStatus",
    "NotificationManager",
    "RetryConfig",
    "RetryState",
    "SessionState",
    "TeamsActiveKeeper",
    "__version__",
    "format_health_report",
    "load_config",
    "main",
    "randomize_interval",
    "read_health_status",
    "retry_with_backoff",
    "save_config",
    "send_notification",
    "setup_logging",
]


def main() -> None:
    """Entry point for the application."""
    setup_logging()
    keeper = TeamsActiveKeeper()
    keeper.run()
