## TASK - Project overview

TASK for "Teams Active Status Keeper" is a macOS background service that maintains an active status (green dot) on Microsoft Teams web version by simulating periodic user activity using Selenium WebDriver and Chrome.

## Architecture

### Core component
- **`teams_active.py`**: Single-file Python script containing the `TeamsActiveKeeper` class
  - Uses Selenium WebDriver to control a headless Chrome instance
  - Maintains persistent Chrome profile for session management (no re-login needed)
  - Simulates activity via JavaScript event dispatching (mouse movement, focus, scroll)
  - Two-loop system: health checks (60s default) and activity simulation (300s default)

### Configuration system
- **Location**: `~/.teams_active_config.json` (auto-generated on first run)
- **Template**: `config.example.json` in repo
- JSON-based with 5 key parameters: `teams_url`, `check_interval`, `activity_interval`, `headless`, `user_data_dir`
- Chrome profile data stored at `~/Library/Application Support/TeamsActiveStatus` for session persistence

### MacOS LaunchAgent integration
- **Service**: `com.teamsactive.keeper.plist`
- Auto-starts on login, restarts on failure (`KeepAlive` with `SuccessfulExit: false`)
- ThrottleInterval of 10 seconds prevents rapid restart loops
- Logs redirected to `~/Library/Logs/TeamsActiveStatus/`

## Development commands

### Installation & setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run automated installation (creates LaunchAgent)
./install.sh
```

### Testing & running
```bash
# Manual test run (useful for development/debugging)
python3 teams_active.py

# Run in non-headless mode (for initial teams login or debugging)
# First, edit ~/.teams_active_config.json: set "headless": false
python3 teams_active.py
```

### Service management
```bash
# Start service
launchctl start com.teamsactive.keeper

# Stop service
launchctl stop com.teamsactive.keeper

# Reload after code changes
launchctl unload ~/Library/LaunchAgents/com.teamsactive.keeper.plist
launchctl load ~/Library/LaunchAgents/com.teamsactive.keeper.plist

# Check if service is running
launchctl list | grep teamsactive

# View real-time logs
tail -f ~/Library/Logs/TeamsActiveStatus/teams_active.log
tail -f ~/Library/Logs/TeamsActiveStatus/stderr.log
```

### Debugging
```bash
# Clear chrome profile data (forces re-login)
rm -rf ~/Library/Application\ Support/TeamsActiveStatus

# Reset configuration
rm ~/.teams_active_config.json

# Check python/chrome versions
python3 --version
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

## Key implementation details

### Activity simulation strategy
The script uses JavaScript execution rather than Selenium's built-in click/move methods to avoid triggering unwanted UI interactions:
- Dispatches `MouseEvent('mousemove')` to simulate presence
- Calls `window.focus()` to maintain window focus state
- Performs minimal scroll operations (1px up/down) for activity signals
- Executes `document.body.click()` as a gentle interaction

### Session management
- Chrome's `--user-data-dir` flag maintains login cookies/session between runs
- Health check validates `teams.microsoft.com` remains in URL
- Failed health checks trigger automatic page reload, not full restart

### Logging architecture
Three log files:
- `teams_active.log`: Application-level events (activity simulation, session checks)
- `stdout.log`: LaunchAgent stdout capture
- `stderr.log`: LaunchAgent stderr capture

## Common modifications

### Changing activity intervals
Edit `~/.teams_active_config.json`:
- `check_interval`: How often to verify Teams session (in seconds)
- `activity_interval`: How often to simulate activity (in seconds)

### Adding new activity patterns
Modify the `simulate_activity()` method in `TeamsActiveKeeper` class. JavaScript execution is preferred over Selenium actions to maintain subtlety.

### Supporting different URLs/services
Update `teams_url` in config. The `check_session()` method validates domain presence - adjust this check if supporting non-Teams URLs.

## Dependencies

- **Selenium**: WebDriver automation (≥4.15.0)
- **Webdriver-manager**: Automatic ChromeDriver management (≥4.0.0)
- **Python**: 3.8+ required
- **Chrome**: Must be installed at `/Applications/Google Chrome.app`

## File structure

```
.
├── teams_active.py              # Main script
├── com.teamsactive.keeper.plist # LaunchAgent configuration
├── install.sh                   # Automated setup script
├── requirements.txt             # Python dependencies
├── config.example.json          # Configuration template
└── README.md                    # User documentation
```

## Important notes

- The script requires initial manual login to Teams (run non-headless once)
- macOS may require Automation permissions: System Preferences → Security & Privacy → Privacy → Automation
- LaunchAgent runs under user context, not root
- Chrome profile isolation prevents conflicts with regular Chrome usage
- Script designed for web Teams only, not desktop app
