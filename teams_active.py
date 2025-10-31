#!/usr/bin/env python3
"""
Teams Active Status Keeper
A background script that keeps Microsoft Teams web version showing as active (green dot).
"""

import time
import json
import logging
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Setup logging
LOG_DIR = Path.home() / "Library" / "Logs" / "TeamsActiveStatus"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "teams_active.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class TeamsActiveKeeper:
    """Keeps Teams web version active by simulating periodic activity."""
    
    def __init__(self, config_path=None):
        """Initialize the Teams Active Keeper."""
        self.config_path = config_path or Path.home() / ".teams_active_config.json"
        self.config = self.load_config()
        self.driver = None
        
    def load_config(self):
        """Load configuration from JSON file."""
        default_config = {
            "teams_url": "https://teams.microsoft.com",
            "check_interval": 60,  # seconds
            "activity_interval": 300,  # seconds (5 minutes)
            "headless": True,
            "user_data_dir": str(Path.home() / "Library" / "Application Support" / "TeamsActiveStatus")
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Could not load config file: {e}. Using defaults.")
        else:
            # Create default config file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config at {self.config_path}")
            
        return default_config
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options."""
        chrome_options = Options()
        
        if self.config.get("headless", True):
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use persistent user data directory to maintain login session
        user_data_dir = self.config.get("user_data_dir")
        if user_data_dir:
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Suppress logging
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def simulate_activity(self):
        """Simulate user activity to keep status active."""
        try:
            # Execute JavaScript to simulate mouse movement and activity
            self.driver.execute_script("""
                // Dispatch mousemove event
                const event = new MouseEvent('mousemove', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                document.dispatchEvent(event);
                
                // Focus on the window
                window.focus();
                
                // Scroll slightly and back
                window.scrollBy(0, 1);
                window.scrollBy(0, -1);
            """)
            
            # Try to find and click on a safe element (like the app bar)
            try:
                # This is a gentle interaction that won't disrupt anything
                self.driver.execute_script("document.body.click();")
            except:
                pass
                
            logger.info("Simulated activity successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to simulate activity: {e}")
            return False
    
    def check_session(self):
        """Check if Teams session is still active."""
        try:
            # Check if we're still on Teams domain
            current_url = self.driver.current_url
            if "teams.microsoft.com" not in current_url:
                logger.warning(f"Not on Teams domain. Current URL: {current_url}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check session: {e}")
            return False
    
    def run(self):
        """Main run loop."""
        logger.info("Starting Teams Active Status Keeper")
        
        try:
            self.setup_driver()
            
            # Navigate to Teams
            teams_url = self.config.get("teams_url", "https://teams.microsoft.com")
            logger.info(f"Navigating to {teams_url}")
            self.driver.get(teams_url)
            
            # Wait for user to log in if needed
            logger.info("Waiting for Teams to load (you may need to log in manually if this is the first run)")
            time.sleep(30)  # Give time for initial load/login
            
            check_interval = self.config.get("check_interval", 60)
            activity_interval = self.config.get("activity_interval", 300)
            last_activity = time.time()
            
            logger.info(f"Starting monitoring loop (check every {check_interval}s, activity every {activity_interval}s)")
            
            while True:
                current_time = time.time()
                
                # Check session health
                if not self.check_session():
                    logger.error("Session check failed. Reloading...")
                    self.driver.get(teams_url)
                    time.sleep(10)
                    continue
                
                # Simulate activity at specified intervals
                if current_time - last_activity >= activity_interval:
                    if self.simulate_activity():
                        last_activity = current_time
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver closed")


def main():
    """Entry point for the script."""
    keeper = TeamsActiveKeeper()
    keeper.run()


if __name__ == "__main__":
    main()
