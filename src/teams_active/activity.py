"""Activity simulation for Teams Active Status Keeper."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING

from .constants import TEAMS_DOMAIN

if TYPE_CHECKING:
    from .driver import DriverManager

logger = logging.getLogger(__name__)

# JavaScript for simulating user activity
ACTIVITY_SCRIPT = """
// Dispatch mousemove event
const event = new MouseEvent('mousemove', {
    bubbles: true,
    cancelable: true,
    view: window,
    clientX: Math.random() * window.innerWidth,
    clientY: Math.random() * window.innerHeight
});
document.dispatchEvent(event);

// Focus on the window
window.focus();

// Scroll slightly and back
window.scrollBy(0, 1);
window.scrollBy(0, -1);
"""

CLICK_SCRIPT = "document.body.click();"


class ActivitySimulator:
    """Simulates user activity to keep Teams active."""

    def __init__(self, driver_manager: DriverManager) -> None:
        """
        Initialize the activity simulator.

        Args:
            driver_manager: The driver manager instance.
        """
        self.driver_manager = driver_manager
        self._activity_count = 0

    @property
    def activity_count(self) -> int:
        """Get the total number of activities simulated."""
        return self._activity_count

    def simulate(self) -> bool:
        """
        Simulate user activity to keep status active.

        Returns:
            True if activity was simulated successfully, False otherwise.
        """
        if not self.driver_manager.is_active:
            logger.error("Cannot simulate activity: driver not active")
            return False

        try:
            # Execute main activity script
            if not self.driver_manager.execute_script(ACTIVITY_SCRIPT):
                return False

            # Gentle body click (suppressed if it fails)
            with contextlib.suppress(Exception):
                self.driver_manager.execute_script(CLICK_SCRIPT)

            self._activity_count += 1
            logger.info("Simulated activity successfully (total: %d)", self._activity_count)
            return True

        except Exception as e:
            logger.error("Failed to simulate activity: %s", e)
            return False

    def check_session(self) -> bool:
        """
        Check if Teams session is still active.

        Returns:
            True if session is active on Teams domain, False otherwise.
        """
        current_url = self.driver_manager.get_current_url()

        if current_url is None:
            logger.error("Cannot check session: unable to get current URL")
            return False

        if TEAMS_DOMAIN not in current_url:
            logger.warning("Not on Teams domain. Current URL: %s", current_url)
            return False

        logger.debug("Session check passed: %s", current_url)
        return True


class SessionState:
    """Tracks session state and health."""

    def __init__(self) -> None:
        """Initialize session state."""
        self._consecutive_failures = 0
        self._total_checks = 0
        self._successful_checks = 0
        self._was_previously_failed = False

    @property
    def consecutive_failures(self) -> int:
        """Get the number of consecutive failures."""
        return self._consecutive_failures

    @property
    def total_checks(self) -> int:
        """Get the total number of session checks."""
        return self._total_checks

    @property
    def success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self._total_checks == 0:
            return 100.0
        return (self._successful_checks / self._total_checks) * 100

    @property
    def just_recovered(self) -> bool:
        """Check if session just recovered from a failure state."""
        return self._was_previously_failed and self._consecutive_failures == 0

    def record_success(self) -> None:
        """Record a successful session check."""
        self._was_previously_failed = self._consecutive_failures > 0
        self._consecutive_failures = 0
        self._total_checks += 1
        self._successful_checks += 1

    def record_failure(self) -> None:
        """Record a failed session check."""
        self._was_previously_failed = False
        self._consecutive_failures += 1
        self._total_checks += 1

    def reset(self) -> None:
        """Reset all state counters."""
        self._consecutive_failures = 0
        self._total_checks = 0
        self._successful_checks = 0
        self._was_previously_failed = False
