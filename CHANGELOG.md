# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-09

### Added

- **Package Structure**: Reorganized into proper Python package (`src/teams_active/`)
- **Pydantic Configuration**: Type-safe config with validation
  - Bounds checking for intervals (check: 10-3600s, activity: 30-3600s)
  - URL validation for Teams domains
  - Path expansion for directories
- **Exponential Backoff**: Smart retry logic for failures
  - Configurable initial backoff (5s default)
  - Maximum backoff cap (5 minutes)
  - Jitter (±10%) to prevent thundering herd
- **macOS Notifications**: Native alerts for important events
  - Session failure notifications (after threshold)
  - Recovery notifications
  - Critical error alerts
  - Rate limiting (1 per minute)
- **Health Monitoring**: Real-time status tracking
  - Status file at `~/Library/Application Support/TeamsActiveStatus/status.json`
  - CLI command: `python -m teams_active status`
  - Tracks uptime, activities, success rate
- **CLI Improvements**:
  - Subcommands: `run`, `status`
  - `--verbose` flag for debug logging
  - `--config` flag for custom config path
  - `--version` flag
- **Randomized Intervals**: Human-like behavior (±20% randomization)
- **Log Rotation**: 5MB max file size, 3 backups
- **CI/CD**: GitHub Actions workflow
  - Linting (ruff, black)
  - Testing (pytest with coverage)
  - Type checking (mypy)
  - Multi-Python version testing (3.9-3.12)
- **Pre-commit Hooks**: Automated code quality checks
- **Full Type Hints**: Complete type annotations throughout

### Changed

- **Python Version**: Now requires Python 3.9+ (was 3.8+)
- **Dependencies**: Added pydantic>=2.0.0
- **Entry Point**: Now uses `python -m teams_active` (backward-compatible script available)
- **Config Options**: Added `randomize_intervals`, `enable_notifications`, `max_consecutive_failures`

### Fixed

- Proper exception handling with specific exception types
- Session recovery logic improvements
- Cleaner shutdown handling

## [0.1.0] - 2025-01-08

### Added

- Initial release
- Basic Teams status keeper functionality
- Selenium WebDriver integration
- macOS LaunchAgent support
- Persistent Chrome profile for session management
- JSON configuration file support
- Basic logging to file and console
