"""Tests for configuration loading and management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from teams_active.config import AppConfig, load_config, save_config


class TestAppConfig:
    """Tests for AppConfig validation."""

    def test_default_config_values(self) -> None:
        """Test that default config values are correct."""
        config = AppConfig()

        assert config.teams_url == "https://teams.microsoft.com"
        assert config.check_interval == 60
        assert config.activity_interval == 300
        assert config.headless is True
        assert config.randomize_intervals is True
        assert config.enable_notifications is True

    def test_config_with_custom_values(self) -> None:
        """Test creating config with custom values."""
        config = AppConfig(
            teams_url="https://teams.live.com",
            check_interval=120,
            activity_interval=600,
            headless=False,
        )

        assert config.teams_url == "https://teams.live.com"
        assert config.check_interval == 120
        assert config.activity_interval == 600
        assert config.headless is False

    def test_check_interval_validation(self) -> None:
        """Test that check_interval has valid bounds."""
        # Too low
        with pytest.raises(ValueError):
            AppConfig(check_interval=5)

        # Too high
        with pytest.raises(ValueError):
            AppConfig(check_interval=5000)

        # Valid bounds
        config_min = AppConfig(check_interval=10)
        config_max = AppConfig(check_interval=3600)
        assert config_min.check_interval == 10
        assert config_max.check_interval == 3600

    def test_activity_interval_validation(self) -> None:
        """Test that activity_interval has valid bounds."""
        # Too low
        with pytest.raises(ValueError):
            AppConfig(activity_interval=20)

        # Valid
        config = AppConfig(activity_interval=30)
        assert config.activity_interval == 30

    def test_teams_url_validation(self) -> None:
        """Test that teams_url must be a valid URL."""
        with pytest.raises(ValueError):
            AppConfig(teams_url="not-a-url")

        # Valid URLs
        config1 = AppConfig(teams_url="https://teams.microsoft.com")
        config2 = AppConfig(teams_url="https://teams.live.com")
        assert "teams.microsoft.com" in config1.teams_url
        assert "teams.live.com" in config2.teams_url

    def test_user_data_dir_expansion(self) -> None:
        """Test that ~ is expanded in user_data_dir."""
        config = AppConfig(user_data_dir="~/test/path")
        assert "~" not in config.user_data_dir
        assert config.user_data_dir.startswith("/")


class TestConfigLoading:
    """Tests for configuration file loading."""

    def test_load_config_from_file(self, config_file: Path, sample_config: dict[str, Any]) -> None:
        """Test that configuration is loaded correctly from a file."""
        config = load_config(config_file)

        assert config.teams_url == sample_config["teams_url"]
        assert config.check_interval == sample_config["check_interval"]
        assert config.activity_interval == sample_config["activity_interval"]
        assert config.headless == sample_config["headless"]

    def test_creates_default_config_when_missing(self, temp_config_path: Path) -> None:
        """Test that a default config file is created when none exists."""
        assert not temp_config_path.exists()

        config = load_config(temp_config_path)

        assert temp_config_path.exists()
        assert config.teams_url == "https://teams.microsoft.com"
        assert config.check_interval == 60

    def test_partial_config_uses_defaults(self, tmp_path: Path) -> None:
        """Test that missing config values fall back to defaults."""
        partial_config = {"teams_url": "https://teams.live.com"}
        config_path = tmp_path / "partial_config.json"

        with open(config_path, "w") as f:
            json.dump(partial_config, f)

        config = load_config(config_path)

        assert config.teams_url == "https://teams.live.com"
        assert config.check_interval == 60  # default
        assert config.activity_interval == 300  # default

    def test_invalid_json_uses_defaults(self, tmp_path: Path) -> None:
        """Test that invalid JSON config falls back to defaults."""
        config_path = tmp_path / "invalid_config.json"
        with open(config_path, "w") as f:
            f.write("{ invalid json }")

        config = load_config(config_path)

        assert config.teams_url == "https://teams.microsoft.com"
        assert config.check_interval == 60


class TestConfigSaving:
    """Tests for configuration file saving."""

    def test_save_config(self, tmp_path: Path) -> None:
        """Test saving configuration to file."""
        config_path = tmp_path / "saved_config.json"
        config = AppConfig(check_interval=120)

        save_config(config, config_path)

        assert config_path.exists()
        with open(config_path) as f:
            saved_data = json.load(f)
        assert saved_data["check_interval"] == 120
