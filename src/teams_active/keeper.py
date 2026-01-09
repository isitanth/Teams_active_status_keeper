"""Main orchestrator for Teams Active Status Keeper."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from .activity import ActivitySimulator, SessionState
from .config import AppConfig, load_config
from .constants import INITIAL_LOAD_WAIT, SESSION_RELOAD_WAIT
from .driver import DriverManager
from .health import HealthMonitor
from .notifications import NotificationManager
from .retry import RetryState, randomize_interval

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class TeamsActiveKeeper:
    """Keeps Teams web version active by simulating periodic activity."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        """
        Initialize the Teams Active Keeper.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config: AppConfig = load_config(config_path)
        self.driver_manager = DriverManager(self.config)
        self.activity_simulator: ActivitySimulator | None = None
        self.session_state = SessionState()
        self.retry_state = RetryState()
        self.notification_manager = NotificationManager(enabled=self.config.enable_notifications)
        self.health_monitor = HealthMonitor()
        self._running = False

    def _get_interval(self, base_interval: float) -> float:
        """
        Get interval with optional randomization.

        Args:
            base_interval: The base interval in seconds.

        Returns:
            The interval (randomized if enabled in config).
        """
        if self.config.randomize_intervals:
            return randomize_interval(base_interval)
        return base_interval

    def _handle_session_failure(self) -> None:
        """Handle a session check failure with backoff and notifications."""
        self.session_state.record_failure()
        self.retry_state.record_failure()

        consecutive = self.session_state.consecutive_failures

        # Update health monitor
        self.health_monitor.update_session_stats(
            consecutive_failures=consecutive,
            success_rate=self.session_state.success_rate,
            current_url=self.driver_manager.get_current_url(),
        )
        self.health_monitor.set_error(f"Session check failed ({consecutive} consecutive)")

        # Notify on threshold
        if consecutive >= self.config.max_consecutive_failures:
            self.notification_manager.notify_session_failure(consecutive)

        # Calculate backoff
        backoff = self.retry_state.get_backoff_seconds()

        logger.warning(
            "Session failure #%d. Backing off for %.1fs before reload.",
            consecutive,
            backoff,
        )

        if backoff > 0:
            time.sleep(backoff)

        # Attempt to reload
        self.driver_manager.navigate(self.config.teams_url)
        time.sleep(SESSION_RELOAD_WAIT)

    def _handle_session_success(self) -> None:
        """Handle a successful session check."""
        was_failed = self.session_state.consecutive_failures > 0

        self.session_state.record_success()
        self.retry_state.record_success()

        # Update health monitor
        self.health_monitor.update_session_stats(
            consecutive_failures=0,
            success_rate=self.session_state.success_rate,
            current_url=self.driver_manager.get_current_url(),
        )
        self.health_monitor.clear_error()
        self.health_monitor.heartbeat()

        # Notify recovery if we were in a failed state
        if was_failed:
            logger.info("Session recovered after %d failures", was_failed)
            self.notification_manager.notify_session_recovered()

    def run(self) -> None:
        """Run the main monitoring loop."""
        logger.info("Starting Teams Active Status Keeper")
        self._running = True

        try:
            # Set up driver
            self.driver_manager.setup()
            self.activity_simulator = ActivitySimulator(self.driver_manager)

            # Navigate to Teams
            logger.info("Navigating to %s", self.config.teams_url)
            if not self.driver_manager.navigate(self.config.teams_url):
                raise RuntimeError("Failed to navigate to Teams URL")

            # Wait for initial load/login
            logger.info("Waiting for Teams to load (you may need to log in manually on first run)")
            time.sleep(INITIAL_LOAD_WAIT)

            # Notify that service has started
            self.notification_manager.notify_started()
            self.health_monitor.heartbeat()

            # Get intervals
            check_interval = float(self.config.check_interval)
            activity_interval = float(self.config.activity_interval)
            last_activity = time.time()

            logger.info(
                "Starting monitoring loop (check every ~%ds, activity every ~%ds)",
                int(check_interval),
                int(activity_interval),
            )

            while self._running:
                current_time = time.time()

                # Check session health
                if not self.activity_simulator.check_session():
                    self._handle_session_failure()
                    continue

                self._handle_session_success()

                # Simulate activity at specified intervals
                time_for_activity = current_time - last_activity >= activity_interval
                if time_for_activity and self.activity_simulator.simulate():
                    last_activity = current_time
                    # Randomize next activity interval
                    activity_interval = self._get_interval(float(self.config.activity_interval))
                    # Update health monitor
                    self.health_monitor.record_activity()

                # Wait before next check (with randomization)
                sleep_time = self._get_interval(check_interval)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down...")
        except Exception as e:
            logger.error("Unexpected error in main loop: %s", e)
            self.health_monitor.set_error(str(e))
            self.notification_manager.notify_critical_failure(str(e))
            raise
        finally:
            self._running = False
            self.health_monitor.shutdown()
            self.driver_manager.quit()
            logger.info(
                "Shutdown complete. Stats: %d activities, %.1f%% session success rate",
                self.activity_simulator.activity_count if self.activity_simulator else 0,
                self.session_state.success_rate,
            )

    def stop(self) -> None:
        """Stop the monitoring loop gracefully."""
        logger.info("Stop requested")
        self._running = False
