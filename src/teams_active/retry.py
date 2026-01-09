"""Retry logic with exponential backoff."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

from .constants import (
    BACKOFF_JITTER_FACTOR,
    BACKOFF_MULTIPLIER,
    INITIAL_BACKOFF_SECONDS,
    INTERVAL_RANDOMIZATION_FACTOR,
    MAX_BACKOFF_SECONDS,
    MAX_RETRY_ATTEMPTS,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryState:
    """Tracks retry state for exponential backoff."""

    consecutive_failures: int = 0
    last_failure_time: float | None = None
    total_failures: int = 0
    total_successes: int = 0

    def record_success(self) -> None:
        """Record a successful operation, resetting consecutive failures."""
        self.consecutive_failures = 0
        self.total_successes += 1

    def record_failure(self) -> None:
        """Record a failed operation."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_time = time.time()

    def get_backoff_seconds(self) -> float:
        """
        Calculate backoff time based on consecutive failures.

        Uses exponential backoff with jitter.

        Returns:
            Number of seconds to wait before retrying.
        """
        if self.consecutive_failures == 0:
            return 0.0

        # Exponential backoff: initial * (multiplier ^ (failures - 1))
        backoff = INITIAL_BACKOFF_SECONDS * (BACKOFF_MULTIPLIER ** (self.consecutive_failures - 1))

        # Cap at maximum
        backoff = min(backoff, MAX_BACKOFF_SECONDS)

        # Add jitter (±10%)
        jitter = backoff * BACKOFF_JITTER_FACTOR
        backoff = backoff + random.uniform(-jitter, jitter)

        return max(0.0, backoff)

    def should_retry(self, max_attempts: int = MAX_RETRY_ATTEMPTS) -> bool:
        """
        Check if we should retry based on failure count.

        Args:
            max_attempts: Maximum number of consecutive failures before giving up.

        Returns:
            True if we should retry, False if we've exceeded max attempts.
        """
        return self.consecutive_failures < max_attempts


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = MAX_RETRY_ATTEMPTS
    initial_backoff: float = INITIAL_BACKOFF_SECONDS
    max_backoff: float = MAX_BACKOFF_SECONDS
    multiplier: float = BACKOFF_MULTIPLIER
    jitter_factor: float = BACKOFF_JITTER_FACTOR
    exceptions_to_retry: tuple[type[Exception], ...] = field(default_factory=lambda: (Exception,))


def retry_with_backoff(
    func: Callable[[], T],
    config: RetryConfig | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> T:
    """
    Execute a function with retry and exponential backoff.

    Args:
        func: Function to execute.
        config: Retry configuration. Uses defaults if None.
        on_retry: Optional callback called before each retry with
                  (attempt_number, exception, backoff_seconds).

    Returns:
        Result of the function if successful.

    Raises:
        The last exception if all retries are exhausted.
    """
    if config is None:
        config = RetryConfig()

    last_exception: Exception | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return func()
        except config.exceptions_to_retry as e:
            last_exception = e

            if attempt >= config.max_attempts:
                logger.error(
                    "All %d retry attempts exhausted. Last error: %s",
                    config.max_attempts,
                    e,
                )
                raise

            # Calculate backoff
            backoff = config.initial_backoff * (config.multiplier ** (attempt - 1))
            backoff = min(backoff, config.max_backoff)

            # Add jitter
            jitter = backoff * config.jitter_factor
            backoff = backoff + random.uniform(-jitter, jitter)
            backoff = max(0.0, backoff)

            logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %.1fs...",
                attempt,
                config.max_attempts,
                e,
                backoff,
            )

            if on_retry:
                on_retry(attempt, e, backoff)

            time.sleep(backoff)

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected state in retry_with_backoff")


def randomize_interval(
    base_interval: float,
    factor: float = INTERVAL_RANDOMIZATION_FACTOR,
) -> float:
    """
    Randomize an interval by a given factor to appear more human-like.

    Args:
        base_interval: The base interval in seconds.
        factor: The randomization factor (0.2 = ±20%).

    Returns:
        The randomized interval.
    """
    min_interval = base_interval * (1 - factor)
    max_interval = base_interval * (1 + factor)
    return random.uniform(min_interval, max_interval)
