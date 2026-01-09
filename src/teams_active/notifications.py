"""macOS notifications for Teams Active Status Keeper."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum

from .constants import APP_NAME

logger = logging.getLogger(__name__)


class NotificationSound(Enum):
    """Available notification sounds."""

    DEFAULT = "default"
    BASSO = "Basso"
    BLOW = "Blow"
    BOTTLE = "Bottle"
    FROG = "Frog"
    FUNK = "Funk"
    GLASS = "Glass"
    HERO = "Hero"
    MORSE = "Morse"
    PING = "Ping"
    POP = "Pop"
    PURR = "Purr"
    SOSUMI = "Sosumi"
    SUBMARINE = "Submarine"
    TINK = "Tink"
    NONE = ""


@dataclass
class Notification:
    """A macOS notification."""

    title: str
    message: str
    subtitle: str = ""
    sound: NotificationSound = NotificationSound.DEFAULT


def send_notification(notification: Notification) -> bool:
    """
    Send a macOS notification using osascript.

    Args:
        notification: The notification to send.

    Returns:
        True if notification was sent successfully, False otherwise.
    """
    try:
        # Build the AppleScript command
        script_parts = [
            f'display notification "{_escape_string(notification.message)}"',
            f'with title "{_escape_string(notification.title)}"',
        ]

        if notification.subtitle:
            script_parts.append(f'subtitle "{_escape_string(notification.subtitle)}"')

        if notification.sound and notification.sound != NotificationSound.NONE:
            sound_name = (
                notification.sound.value
                if notification.sound != NotificationSound.DEFAULT
                else "default"
            )
            script_parts.append(f'sound name "{sound_name}"')

        script = " ".join(script_parts)

        # Execute the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            logger.warning("Notification failed: %s", result.stderr)
            return False

        logger.debug("Notification sent: %s", notification.title)
        return True

    except subprocess.TimeoutExpired:
        logger.warning("Notification timed out")
        return False
    except FileNotFoundError:
        logger.warning("osascript not found - notifications not available")
        return False
    except Exception as e:
        logger.warning("Failed to send notification: %s", e)
        return False


def _escape_string(s: str) -> str:
    """Escape a string for use in AppleScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


class NotificationManager:
    """Manages notifications with rate limiting and state tracking."""

    def __init__(self, enabled: bool = True, min_interval_seconds: float = 60.0) -> None:
        """
        Initialize the notification manager.

        Args:
            enabled: Whether notifications are enabled.
            min_interval_seconds: Minimum time between notifications.
        """
        self.enabled = enabled
        self.min_interval_seconds = min_interval_seconds
        self._last_notification_time: float = 0.0

    def notify_session_failure(self, consecutive_failures: int) -> bool:
        """
        Send a notification about session failures.

        Args:
            consecutive_failures: Number of consecutive failures.

        Returns:
            True if notification was sent.
        """
        import time  # noqa: PLC0415

        if not self.enabled:
            return False

        current_time = time.time()
        if current_time - self._last_notification_time < self.min_interval_seconds:
            logger.debug("Skipping notification due to rate limiting")
            return False

        notification = Notification(
            title=APP_NAME,
            message=f"Session check failed {consecutive_failures} times. Will retry with backoff.",
            subtitle="Session Issue",
            sound=NotificationSound.BASSO,
        )

        if send_notification(notification):
            self._last_notification_time = current_time
            return True
        return False

    def notify_session_recovered(self) -> bool:
        """
        Send a notification that session has recovered.

        Returns:
            True if notification was sent.
        """
        if not self.enabled:
            return False

        notification = Notification(
            title=APP_NAME,
            message="Session has been restored successfully.",
            subtitle="Recovered",
            sound=NotificationSound.GLASS,
        )

        return send_notification(notification)

    def notify_critical_failure(self, error_message: str) -> bool:
        """
        Send a notification about a critical failure.

        Args:
            error_message: Description of the failure.

        Returns:
            True if notification was sent.
        """
        if not self.enabled:
            return False

        notification = Notification(
            title=f"{APP_NAME} - Critical Error",
            message=error_message[:200],  # Truncate long messages
            subtitle="Action Required",
            sound=NotificationSound.SOSUMI,
        )

        return send_notification(notification)

    def notify_started(self) -> bool:
        """
        Send a notification that the service has started.

        Returns:
            True if notification was sent.
        """
        if not self.enabled:
            return False

        notification = Notification(
            title=APP_NAME,
            message="Service started and monitoring Teams status.",
            subtitle="Started",
            sound=NotificationSound.NONE,
        )

        return send_notification(notification)
