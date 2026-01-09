# Teams Active Status Keeper

A macOS background service that maintains an active status (green dot) on Microsoft Teams web version by simulating periodic user activity.

[![CI](https://github.com/yourusername/teams-active-status/workflows/CI/badge.svg)](https://github.com/yourusername/teams-active-status/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Automatic Status Maintenance**: Keeps Teams showing "Active" status
- **Headless Operation**: Runs invisibly in the background
- **Session Persistence**: Maintains login across restarts
- **Smart Retry Logic**: Exponential backoff on failures
- **macOS Notifications**: Alerts on critical issues
- **Health Monitoring**: Real-time status reporting
- **Randomized Intervals**: Human-like activity patterns

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/teams-active-status.git
cd teams-active-status

# Run the installer
./install.sh
```

The installer will:
1. Create a Python virtual environment
2. Install dependencies
3. Set up the macOS LaunchAgent for auto-start

### First Run (Login Required)

For the first run, you need to log in to Teams:

```bash
# Edit config to disable headless mode
nano ~/.teams_active_config.json
# Set: "headless": false

# Run manually
cd src && ../venv/bin/python3 -m teams_active

# Log in to Teams in the browser window
# Press Ctrl+C when done

# Re-enable headless mode
nano ~/.teams_active_config.json
# Set: "headless": true

# Start the service
launchctl start com.teamsactive.keeper
```

## Usage

### CLI Commands

```bash
# Run the keeper (default)
python -m teams_active run

# Run with verbose logging
python -m teams_active run -v

# Run with custom config
python -m teams_active run -c /path/to/config.json

# Check health status
python -m teams_active status

# Show version
python -m teams_active --version
```

### Service Management

```bash
# Start service
launchctl start com.teamsactive.keeper

# Stop service
launchctl stop com.teamsactive.keeper

# Reload service
launchctl unload ~/Library/LaunchAgents/com.teamsactive.keeper.plist
launchctl load ~/Library/LaunchAgents/com.teamsactive.keeper.plist

# Check if running
launchctl list | grep teamsactive

# View logs
tail -f ~/Library/Logs/TeamsActiveStatus/teams_active.log
```

## Configuration

Configuration file: `~/.teams_active_config.json`

```json
{
  "teams_url": "https://teams.microsoft.com",
  "check_interval": 60,
  "activity_interval": 300,
  "headless": true,
  "user_data_dir": "~/Library/Application Support/TeamsActiveStatus",
  "randomize_intervals": true,
  "enable_notifications": true,
  "max_consecutive_failures": 5
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `teams_url` | string | `https://teams.microsoft.com` | Teams URL to monitor |
| `check_interval` | int | `60` | Session health check interval (10-3600 seconds) |
| `activity_interval` | int | `300` | Activity simulation interval (30-3600 seconds) |
| `headless` | bool | `true` | Run Chrome in headless mode |
| `user_data_dir` | string | `~/Library/.../TeamsActiveStatus` | Chrome profile directory |
| `randomize_intervals` | bool | `true` | Randomize intervals by ±20% |
| `enable_notifications` | bool | `true` | Enable macOS notifications |
| `max_consecutive_failures` | int | `5` | Failures before notification |

## Architecture

### Package Structure

```
src/teams_active/
├── __init__.py         # Package exports
├── __main__.py         # CLI entry point
├── activity.py         # Activity simulation
├── config.py           # Pydantic configuration
├── constants.py        # Application constants
├── driver.py           # Selenium WebDriver management
├── health.py           # Health monitoring
├── keeper.py           # Main orchestrator
├── logging_config.py   # Logging setup
├── notifications.py    # macOS notifications
└── retry.py            # Exponential backoff
```

### How It Works

1. **Initialization**: Loads config, sets up Chrome WebDriver with persistent profile
2. **Navigation**: Opens Teams URL, waits for login/load
3. **Monitoring Loop**:
   - Health checks verify Teams domain (configurable interval)
   - Activity simulation dispatches JavaScript events
   - Failures trigger exponential backoff and retry
4. **Activity Simulation**:
   - Mouse movement events
   - Window focus
   - Minimal scroll operations
   - Gentle body click

### File Locations

| File | Location |
|------|----------|
| Config | `~/.teams_active_config.json` |
| Logs | `~/Library/Logs/TeamsActiveStatus/` |
| Chrome Profile | `~/Library/Application Support/TeamsActiveStatus/` |
| Health Status | `~/Library/Application Support/TeamsActiveStatus/status.json` |
| LaunchAgent | `~/Library/LaunchAgents/com.teamsactive.keeper.plist` |

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src/teams_active

# Run linting
ruff check src tests
black --check src tests

# Type checking
mypy src/teams_active
```

### Project Structure

```
teams-active-status/
├── src/teams_active/    # Main package
├── tests/               # Test suite
├── .github/workflows/   # CI/CD
├── pyproject.toml       # Project configuration
├── requirements.txt     # Core dependencies
├── requirements-dev.txt # Dev dependencies
├── install.sh           # Installation script
└── README.md
```

## Troubleshooting

### Service won't start

```bash
# Check logs
tail -100 ~/Library/Logs/TeamsActiveStatus/stderr.log

# Verify Chrome is installed
ls /Applications/Google\ Chrome.app

# Check Python
./venv/bin/python3 --version
```

### Login issues

```bash
# Clear Chrome profile
rm -rf ~/Library/Application\ Support/TeamsActiveStatus

# Run in non-headless mode and log in again
```

### Permission issues

Go to: System Preferences → Security & Privacy → Privacy → Automation
- Enable permissions for Terminal/iTerm

## Requirements

- **macOS** 10.15+
- **Python** 3.9+
- **Google Chrome** (installed at `/Applications/Google Chrome.app`)

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CHANGELOG.md](CHANGELOG.md) for version history.
