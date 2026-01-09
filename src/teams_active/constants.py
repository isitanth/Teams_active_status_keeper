"""Constants for Teams Active Status Keeper."""

from __future__ import annotations

# Timing constants (in seconds)
DEFAULT_CHECK_INTERVAL = 60
DEFAULT_ACTIVITY_INTERVAL = 300  # 5 minutes
INITIAL_LOAD_WAIT = 30
SESSION_RELOAD_WAIT = 10

# Randomization
INTERVAL_RANDOMIZATION_FACTOR = 0.2  # ±20%

# Retry/backoff constants
MAX_RETRY_ATTEMPTS = 5
INITIAL_BACKOFF_SECONDS = 5.0
MAX_BACKOFF_SECONDS = 300.0  # 5 minutes
BACKOFF_MULTIPLIER = 2.0
BACKOFF_JITTER_FACTOR = 0.1  # ±10% jitter

# Logging constants
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# URLs
DEFAULT_TEAMS_URL = "https://teams.microsoft.com"
TEAMS_DOMAIN = "teams.microsoft.com"

# Application info
APP_NAME = "TeamsActiveStatus"
APP_BUNDLE_ID = "com.teamsactive.keeper"
