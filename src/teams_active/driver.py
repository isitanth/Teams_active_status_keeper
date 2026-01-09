"""Selenium WebDriver management."""

from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .config import AppConfig  # noqa: TC001 - needed at runtime

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class DriverManager:
    """Manages the Selenium WebDriver lifecycle."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the driver manager.

        Args:
            config: Application configuration.
        """
        self.config = config
        self._driver: WebDriver | None = None

    @property
    def driver(self) -> WebDriver | None:
        """Get the current WebDriver instance."""
        return self._driver

    @property
    def is_active(self) -> bool:
        """Check if the driver is active and responsive."""
        if self._driver is None:
            return False
        try:
            # Try to get the current URL to check if driver is responsive
            _ = self._driver.current_url
            return True
        except Exception:
            return False

    def setup(self) -> WebDriver:
        """
        Set up and return a Chrome WebDriver.

        Returns:
            Configured WebDriver instance.

        Raises:
            RuntimeError: If driver setup fails.
        """
        chrome_options = self._build_chrome_options()

        try:
            self._driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome driver initialized successfully")
            return self._driver
        except Exception as e:
            logger.error("Failed to initialize Chrome driver: %s", e)
            raise RuntimeError(f"Failed to initialize Chrome driver: {e}") from e

    def _build_chrome_options(self) -> Options:
        """
        Build Chrome options based on configuration.

        Returns:
            Configured Chrome Options instance.
        """
        chrome_options = Options()

        # Headless mode
        if self.config.headless:
            chrome_options.add_argument("--headless=new")

        # Standard options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Persistent user data directory
        if self.config.user_data_dir:
            user_data_path = Path(self.config.user_data_dir)
            user_data_path.mkdir(parents=True, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={user_data_path}")

        # Suppress logging
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return chrome_options

    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to.

        Returns:
            True if navigation was successful.
        """
        if self._driver is None:
            logger.error("Cannot navigate: driver not initialized")
            return False

        try:
            self._driver.get(url)
            logger.info("Navigated to %s", url)
            return True
        except Exception as e:
            logger.error("Failed to navigate to %s: %s", url, e)
            return False

    def get_current_url(self) -> str | None:
        """
        Get the current URL.

        Returns:
            Current URL or None if unavailable.
        """
        if self._driver is None:
            return None
        try:
            return self._driver.current_url
        except Exception as e:
            logger.error("Failed to get current URL: %s", e)
            return None

    def execute_script(self, script: str) -> bool:
        """
        Execute JavaScript in the browser.

        Args:
            script: JavaScript code to execute.

        Returns:
            True if execution was successful.
        """
        if self._driver is None:
            logger.error("Cannot execute script: driver not initialized")
            return False

        try:
            self._driver.execute_script(script)
            return True
        except Exception as e:
            logger.error("Failed to execute script: %s", e)
            return False

    def quit(self) -> None:
        """Quit the WebDriver and clean up resources."""
        if self._driver is not None:
            with contextlib.suppress(Exception):
                self._driver.quit()
            self._driver = None
            logger.info("Driver closed")

    def __enter__(self) -> DriverManager:
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> None:
        """Context manager exit."""
        self.quit()
