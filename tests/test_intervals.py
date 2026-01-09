"""Tests for interval randomization functionality."""

from __future__ import annotations

from teams_active.retry import randomize_interval


class TestIntervalRandomization:
    """Tests for the interval randomization function."""

    def test_randomize_interval_within_bounds(self) -> None:
        """Test that randomized interval stays within expected bounds."""
        base_interval = 100.0
        factor = 0.2

        for _ in range(100):
            result = randomize_interval(base_interval, factor)
            assert 80.0 <= result <= 120.0

    def test_randomize_interval_default_factor(self) -> None:
        """Test that default factor (0.2) is applied correctly."""
        base_interval = 60.0

        for _ in range(100):
            result = randomize_interval(base_interval)
            assert 48.0 <= result <= 72.0  # ±20%

    def test_randomize_interval_zero_factor(self) -> None:
        """Test that zero factor returns the base interval."""
        base_interval = 100.0

        result = randomize_interval(base_interval, factor=0.0)

        assert result == base_interval

    def test_randomize_interval_varies_output(self) -> None:
        """Test that randomization produces varied outputs."""
        base_interval = 100.0
        results = {randomize_interval(base_interval) for _ in range(50)}

        # Should produce multiple different values
        assert len(results) > 1

    def test_randomize_interval_with_small_base(self) -> None:
        """Test randomization with small base interval."""
        base_interval = 1.0
        factor = 0.2

        for _ in range(100):
            result = randomize_interval(base_interval, factor)
            assert 0.8 <= result <= 1.2


class TestRetryState:
    """Tests for RetryState tracking."""

    def test_initial_state(self) -> None:
        """Test initial retry state values."""
        from teams_active.retry import RetryState

        state = RetryState()

        assert state.consecutive_failures == 0
        assert state.total_failures == 0
        assert state.total_successes == 0
        assert state.last_failure_time is None

    def test_record_success_resets_consecutive(self) -> None:
        """Test that recording success resets consecutive failures."""
        from teams_active.retry import RetryState

        state = RetryState()
        state.record_failure()
        state.record_failure()
        assert state.consecutive_failures == 2

        state.record_success()
        assert state.consecutive_failures == 0
        assert state.total_successes == 1
        assert state.total_failures == 2

    def test_backoff_calculation(self) -> None:
        """Test exponential backoff calculation."""
        from teams_active.retry import RetryState

        state = RetryState()

        # No failures = no backoff
        assert state.get_backoff_seconds() == 0.0

        # First failure
        state.record_failure()
        backoff1 = state.get_backoff_seconds()
        assert 4.0 <= backoff1 <= 6.0  # ~5s with jitter

        # Second failure (exponential increase)
        state.record_failure()
        backoff2 = state.get_backoff_seconds()
        assert backoff2 > backoff1

    def test_should_retry(self) -> None:
        """Test should_retry logic."""
        from teams_active.retry import RetryState

        state = RetryState()

        # Should retry initially
        assert state.should_retry(max_attempts=3) is True

        # After max failures, should not retry
        state.record_failure()
        state.record_failure()
        state.record_failure()
        assert state.should_retry(max_attempts=3) is False
