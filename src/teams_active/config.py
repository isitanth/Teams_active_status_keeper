"""Configuration management with Pydantic validation."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .constants import (
    DEFAULT_ACTIVITY_INTERVAL,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_TEAMS_URL,
)

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """Application configuration with validation."""

    teams_url: str = Field(
        default=DEFAULT_TEAMS_URL,
        description="Microsoft Teams URL to monitor",
    )
    check_interval: int = Field(
        default=DEFAULT_CHECK_INTERVAL,
        ge=10,
        le=3600,
        description="Session health check interval in seconds (10-3600)",
    )
    activity_interval: int = Field(
        default=DEFAULT_ACTIVITY_INTERVAL,
        ge=30,
        le=3600,
        description="Activity simulation interval in seconds (30-3600)",
    )
    headless: bool = Field(
        default=True,
        description="Run Chrome in headless mode",
    )
    user_data_dir: str = Field(
        default="",
        description="Chrome user data directory for persistent sessions",
    )
    randomize_intervals: bool = Field(
        default=True,
        description="Randomize intervals for more human-like behavior",
    )
    enable_notifications: bool = Field(
        default=True,
        description="Enable macOS notifications on failures",
    )
    max_consecutive_failures: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Max consecutive failures before notification",
    )

    @field_validator("teams_url")
    @classmethod
    def validate_teams_url(cls, v: str) -> str:
        """Validate that the URL is a valid Teams URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("teams_url must start with http:// or https://")
        if "teams.microsoft.com" not in v and "teams.live.com" not in v:
            logger.warning("URL does not appear to be a Microsoft Teams URL: %s", v)
        return v

    @field_validator("user_data_dir")
    @classmethod
    def expand_user_data_dir(cls, v: str) -> str:
        """Expand ~ in user data directory path."""
        if v:
            return str(Path(v).expanduser())
        return str(Path.home() / "Library" / "Application Support" / "TeamsActiveStatus")

    model_config = {"extra": "ignore"}


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".teams_active_config.json"


def load_config(config_path: Path | str | None = None) -> AppConfig:
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to the configuration file. Uses default if None.

    Returns:
        Validated AppConfig instance.
    """
    config_path = get_default_config_path() if config_path is None else Path(config_path)

    config_data: dict[str, Any] = {}

    if config_path.exists():
        try:
            with config_path.open() as f:
                config_data = json.load(f)
                logger.info("Loaded config from %s", config_path)
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON in config file: %s. Using defaults.", e)
        except OSError as e:
            logger.warning("Could not read config file: %s. Using defaults.", e)
    else:
        logger.info("Config file not found at %s. Creating with defaults.", config_path)

    # Create validated config
    config = AppConfig(**config_data)

    # Save config if it didn't exist (creates default config file)
    if not config_path.exists():
        save_config(config, config_path)

    return config


def save_config(config: AppConfig, config_path: Path | str | None = None) -> None:
    """
    Save configuration to a JSON file.

    Args:
        config: AppConfig instance to save.
        config_path: Path to save to. Uses default if None.
    """
    config_path = get_default_config_path() if config_path is None else Path(config_path)

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w") as f:
        json.dump(config.model_dump(), f, indent=2)

    logger.info("Saved config to %s", config_path)
