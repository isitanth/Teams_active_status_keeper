"""Health check mechanism for Teams Active Status Keeper."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .constants import APP_NAME

logger = logging.getLogger(__name__)


def get_status_file_path() -> Path:
    """Get the path to the status file."""
    return Path.home() / "Library" / "Application Support" / APP_NAME / "status.json"


@dataclass
class HealthStatus:
    """Health status information."""

    is_running: bool = False
    started_at: float | None = None
    last_heartbeat: float | None = None
    last_activity: float | None = None
    total_activities: int = 0
    consecutive_failures: int = 0
    session_success_rate: float = 100.0
    current_url: str | None = None
    error_message: str | None = None
    pid: int | None = None
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthStatus:
        """Create from dictionary."""
        # Filter only known fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

    @property
    def uptime_seconds(self) -> float:
        """Get uptime in seconds."""
        if self.started_at is None:
            return 0.0
        return time.time() - self.started_at

    @property
    def time_since_heartbeat(self) -> float | None:
        """Get time since last heartbeat in seconds."""
        if self.last_heartbeat is None:
            return None
        return time.time() - self.last_heartbeat

    @property
    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        if not self.is_running:
            return False
        if self.last_heartbeat is None:
            return False
        # Consider unhealthy if no heartbeat in last 5 minutes
        if self.time_since_heartbeat and self.time_since_heartbeat > 300:
            return False
        # Consider unhealthy if too many consecutive failures
        return self.consecutive_failures < 10


@dataclass
class HealthMonitor:
    """Monitors and reports health status."""

    status: HealthStatus = field(default_factory=HealthStatus)
    _status_file: Path = field(default_factory=get_status_file_path)

    def __post_init__(self) -> None:
        """Initialize the health monitor."""
        import os  # noqa: PLC0415

        self.status.pid = os.getpid()
        self.status.started_at = time.time()
        self.status.is_running = True

    def heartbeat(self) -> None:
        """Record a heartbeat."""
        self.status.last_heartbeat = time.time()
        self._write_status()

    def record_activity(self) -> None:
        """Record an activity simulation."""
        self.status.last_activity = time.time()
        self.status.total_activities += 1
        self._write_status()

    def update_session_stats(
        self,
        consecutive_failures: int,
        success_rate: float,
        current_url: str | None = None,
    ) -> None:
        """Update session statistics."""
        self.status.consecutive_failures = consecutive_failures
        self.status.session_success_rate = success_rate
        self.status.current_url = current_url
        self._write_status()

    def set_error(self, error_message: str) -> None:
        """Set an error message."""
        self.status.error_message = error_message
        self._write_status()

    def clear_error(self) -> None:
        """Clear any error message."""
        self.status.error_message = None
        self._write_status()

    def shutdown(self) -> None:
        """Mark the service as shut down."""
        self.status.is_running = False
        self._write_status()

    def _write_status(self) -> None:
        """Write status to file."""
        try:
            self._status_file.parent.mkdir(parents=True, exist_ok=True)
            with self._status_file.open("w") as f:
                json.dump(self.status.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning("Failed to write status file: %s", e)


def read_health_status() -> HealthStatus | None:
    """
    Read the current health status from file.

    Returns:
        HealthStatus if file exists, None otherwise.
    """
    status_file = get_status_file_path()

    if not status_file.exists():
        return None

    try:
        with status_file.open() as f:
            data = json.load(f)
        return HealthStatus.from_dict(data)
    except Exception as e:
        logger.warning("Failed to read status file: %s", e)
        return None


def format_health_report(status: HealthStatus | None) -> str:
    """
    Format a human-readable health report.

    Args:
        status: Health status to format.

    Returns:
        Formatted health report string.
    """
    if status is None:
        return "Status: Unknown (no status file found)"

    lines = [
        "Teams Active Status Keeper - Health Report",
        "=" * 45,
        "",
        f"Status:     {'Running' if status.is_running else 'Stopped'}",
        f"Healthy:    {'Yes' if status.is_healthy else 'No'}",
        f"PID:        {status.pid or 'N/A'}",
        f"Version:    {status.version}",
        "",
    ]

    if status.started_at:
        uptime = status.uptime_seconds
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        lines.append(f"Uptime:     {hours}h {minutes}m {seconds}s")

    if status.last_heartbeat:
        heartbeat_ago = status.time_since_heartbeat
        if heartbeat_ago:
            lines.append(f"Last heartbeat: {int(heartbeat_ago)}s ago")

    lines.extend(
        [
            "",
            f"Activities: {status.total_activities}",
            f"Success rate: {status.session_success_rate:.1f}%",
            f"Consecutive failures: {status.consecutive_failures}",
        ]
    )

    if status.current_url:
        lines.append(f"Current URL: {status.current_url}")

    if status.error_message:
        lines.extend(["", f"Error: {status.error_message}"])

    return "\n".join(lines)
