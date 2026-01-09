"""Pytest configuration and fixtures."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    """Provide a temporary path for config file."""
    return tmp_path / "test_config.json"


@pytest.fixture
def sample_config() -> dict[str, Any]:
    """Provide a sample configuration dictionary."""
    return {
        "teams_url": "https://teams.microsoft.com",
        "check_interval": 60,
        "activity_interval": 300,
        "headless": True,
        "user_data_dir": "/tmp/test_teams_data",
        "randomize_intervals": True,
        "enable_notifications": False,
        "max_consecutive_failures": 5,
    }


@pytest.fixture
def config_file(tmp_path: Path, sample_config: dict[str, Any]) -> Path:
    """Create a temporary config file with sample configuration."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(sample_config, f)
    return config_path


@pytest.fixture
def mock_webdriver() -> Generator[MagicMock, None, None]:
    """Mock the Selenium WebDriver."""
    with patch("teams_active.driver.webdriver.Chrome") as mock_chrome:
        mock_driver = MagicMock()
        mock_driver.current_url = "https://teams.microsoft.com/v2/"
        mock_chrome.return_value = mock_driver
        yield mock_driver


@pytest.fixture
def mock_config(sample_config: dict[str, Any]) -> MagicMock:
    """Create a mock AppConfig."""
    from teams_active.config import AppConfig

    return AppConfig(**sample_config)


@pytest.fixture
def driver_manager_with_mock(
    mock_config: MagicMock, mock_webdriver: MagicMock
) -> Generator[Any, None, None]:
    """Create a DriverManager with mocked Chrome driver."""
    from teams_active.driver import DriverManager

    manager = DriverManager(mock_config)
    manager._driver = mock_webdriver
    yield manager
