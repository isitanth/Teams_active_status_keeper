"""Tests for activity simulation and session checking."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch


class TestSessionState:
    """Tests for SessionState tracking."""

    def test_initial_state(self) -> None:
        """Test initial session state values."""
        from teams_active.activity import SessionState

        state = SessionState()

        assert state.consecutive_failures == 0
        assert state.total_checks == 0
        assert state.success_rate == 100.0

    def test_record_success(self) -> None:
        """Test recording successful session checks."""
        from teams_active.activity import SessionState

        state = SessionState()
        state.record_success()
        state.record_success()

        assert state.consecutive_failures == 0
        assert state.total_checks == 2
        assert state.success_rate == 100.0

    def test_record_failure(self) -> None:
        """Test recording failed session checks."""
        from teams_active.activity import SessionState

        state = SessionState()
        state.record_failure()
        state.record_failure()

        assert state.consecutive_failures == 2
        assert state.total_checks == 2
        assert state.success_rate == 0.0

    def test_mixed_results(self) -> None:
        """Test mixed success and failure tracking."""
        from teams_active.activity import SessionState

        state = SessionState()
        state.record_success()
        state.record_success()
        state.record_failure()
        state.record_success()

        assert state.consecutive_failures == 0
        assert state.total_checks == 4
        assert state.success_rate == 75.0

    def test_just_recovered(self) -> None:
        """Test just_recovered flag after recovery."""
        from teams_active.activity import SessionState

        state = SessionState()
        state.record_failure()
        state.record_failure()

        assert state.just_recovered is False

        state.record_success()
        assert state.just_recovered is True

        state.record_success()
        assert state.just_recovered is False


class TestActivitySimulator:
    """Tests for ActivitySimulator."""

    def test_simulate_success(self, driver_manager_with_mock: Any) -> None:
        """Test that simulate returns True on success."""
        from teams_active.activity import ActivitySimulator

        simulator = ActivitySimulator(driver_manager_with_mock)

        result = simulator.simulate()

        assert result is True
        assert simulator.activity_count == 1

    def test_simulate_increments_count(self, driver_manager_with_mock: Any) -> None:
        """Test that activity count increments."""
        from teams_active.activity import ActivitySimulator

        simulator = ActivitySimulator(driver_manager_with_mock)
        simulator.simulate()
        simulator.simulate()
        simulator.simulate()

        assert simulator.activity_count == 3

    def test_simulate_without_active_driver(self, mock_config: MagicMock) -> None:
        """Test that simulate fails without active driver."""
        from teams_active.activity import ActivitySimulator
        from teams_active.driver import DriverManager

        manager = DriverManager(mock_config)
        simulator = ActivitySimulator(manager)

        result = simulator.simulate()

        assert result is False
        assert simulator.activity_count == 0

    def test_check_session_valid_url(self, driver_manager_with_mock: Any) -> None:
        """Test check_session with valid Teams URL."""
        from teams_active.activity import ActivitySimulator

        driver_manager_with_mock._driver.current_url = "https://teams.microsoft.com/v2/"
        simulator = ActivitySimulator(driver_manager_with_mock)

        result = simulator.check_session()

        assert result is True

    def test_check_session_invalid_url(self, driver_manager_with_mock: Any) -> None:
        """Test check_session with non-Teams URL."""
        from teams_active.activity import ActivitySimulator

        driver_manager_with_mock._driver.current_url = "https://login.microsoft.com/"
        simulator = ActivitySimulator(driver_manager_with_mock)

        result = simulator.check_session()

        assert result is False


class TestDriverManager:
    """Tests for DriverManager."""

    def test_is_active_with_driver(self, driver_manager_with_mock: Any) -> None:
        """Test is_active returns True when driver is responsive."""
        assert driver_manager_with_mock.is_active is True

    def test_is_active_without_driver(self, mock_config: MagicMock) -> None:
        """Test is_active returns False without driver."""
        from teams_active.driver import DriverManager

        manager = DriverManager(mock_config)

        assert manager.is_active is False

    def test_navigate_success(self, driver_manager_with_mock: Any) -> None:
        """Test successful navigation."""
        result = driver_manager_with_mock.navigate("https://teams.microsoft.com")

        assert result is True
        driver_manager_with_mock._driver.get.assert_called_once_with("https://teams.microsoft.com")

    def test_execute_script(self, driver_manager_with_mock: Any) -> None:
        """Test script execution."""
        result = driver_manager_with_mock.execute_script("console.log('test')")

        assert result is True
        driver_manager_with_mock._driver.execute_script.assert_called_once()

    def test_quit_cleans_up(self, driver_manager_with_mock: Any) -> None:
        """Test that quit cleans up the driver."""
        driver_manager_with_mock.quit()

        assert driver_manager_with_mock._driver is None

    def test_context_manager(self, mock_config: MagicMock) -> None:
        """Test DriverManager as context manager."""
        from teams_active.driver import DriverManager

        with patch("teams_active.driver.webdriver.Chrome") as mock_chrome:
            mock_driver = MagicMock()
            mock_chrome.return_value = mock_driver

            with DriverManager(mock_config) as manager:
                assert manager.driver is not None

            mock_driver.quit.assert_called_once()
