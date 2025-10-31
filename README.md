# Teams Active Status Keeper

A lightweight background script for macOS that keeps your Microsoft Teams web version showing as active (green dot) by simulating periodic user activity.

## Features

- 🟢 Maintains active status on Microsoft Teams web version
- 🔄 Runs automatically in the background via macOS LaunchAgent
- ⚙️ Configurable activity intervals
- 📝 Comprehensive logging
- 🔒 Persistent login session (no need to re-login)
- 🎯 Headless mode for minimal resource usage

## Requirements

- macOS (tested on macOS 10.15+)
- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed)

## Installation

### 1. Clone or Download the Repository

```bash
cd ~/projects
git clone <repository-url> teams-active-status
cd teams-active-status
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Install Chrome and ChromeDriver

If you don't have Chrome installed:
```bash
brew install --cask google-chrome
```

ChromeDriver will be automatically managed by the script using `webdriver-manager`.

### 4. Configure the Script (Optional)

The script will automatically create a configuration file at `~/.teams_active_config.json` on first run. You can customize it:

```json
{
  "teams_url": "https://teams.microsoft.com",
  "check_interval": 60,
  "activity_interval": 300,
  "headless": true,
  "user_data_dir": "~/Library/Application Support/TeamsActiveStatus"
}
```

**Configuration Options:**
- `teams_url`: The Teams URL to navigate to
- `check_interval`: How often to check session health (seconds)
- `activity_interval`: How often to simulate activity (seconds)
- `headless`: Run Chrome in headless mode (true/false)
- `user_data_dir`: Directory to store Chrome profile data

### 5. Run the Installation Script

```bash
./install.sh
```

This will:
- Make the script executable
- Update the LaunchAgent plist with your username
- Copy the plist to `~/Library/LaunchAgents/`
- Load the LaunchAgent to start the script

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Make the script executable
chmod +x teams_active.py

# Update the plist file with your username
# Edit com.teamsactive.keeper.plist and replace paths

# Copy to LaunchAgents
cp com.teamsactive.keeper.plist ~/Library/LaunchAgents/

# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.teamsactive.keeper.plist
```

## Usage

### Starting the Service

The script will start automatically on login. To start it manually:

```bash
launchctl start com.teamsactive.keeper
```

### Stopping the Service

```bash
launchctl stop com.teamsactive.keeper
```

### Unloading the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.teamsactive.keeper.plist
```

### Running Manually (for testing)

```bash
python3 teams_active.py
```

For the first run, you may need to run in non-headless mode to log in to Teams:
1. Edit `~/.teams_active_config.json` and set `"headless": false`
2. Run the script manually: `python3 teams_active.py`
3. Log in to Teams in the browser window that opens
4. Once logged in, you can stop the script and set `"headless": true` again

## Logs

Logs are stored in `~/Library/Logs/TeamsActiveStatus/`:
- `teams_active.log` - Main application log
- `stdout.log` - Standard output from LaunchAgent
- `stderr.log` - Error output from LaunchAgent

View logs in real-time:
```bash
tail -f ~/Library/Logs/TeamsActiveStatus/teams_active.log
```

## How It Works

1. The script uses Selenium WebDriver to control a Chrome browser instance
2. It navigates to Microsoft Teams web version
3. It maintains a persistent Chrome profile so you stay logged in
4. Every 5 minutes (configurable), it simulates user activity by:
   - Dispatching mouse movement events
   - Focusing the window
   - Performing minimal scroll actions
5. It checks session health every minute to ensure the browser is still on Teams

## Troubleshooting

### Script Not Starting
Check if the LaunchAgent is loaded:
```bash
launchctl list | grep teamsactive
```

### Chrome Issues
Make sure Chrome is installed and updated:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

### Permission Issues
The script may need accessibility permissions. Go to:
System Preferences → Security & Privacy → Privacy → Automation

### Log Out of Session
If you need to log out and log back in:
```bash
# Stop the service
launchctl stop com.teamsactive.keeper

# Remove stored Chrome data
rm -rf ~/Library/Application\ Support/TeamsActiveStatus

# Start again to re-login
launchctl start com.teamsactive.keeper
```

## Uninstallation

```bash
# Stop and unload the service
launchctl unload ~/Library/LaunchAgents/com.teamsactive.keeper.plist

# Remove the LaunchAgent file
rm ~/Library/LaunchAgents/com.teamsactive.keeper.plist

# Remove configuration and data
rm ~/.teams_active_config.json
rm -rf ~/Library/Application\ Support/TeamsActiveStatus
rm -rf ~/Library/Logs/TeamsActiveStatus

# Remove the project directory
rm -rf ~/projects/teams-active-status
```

## Disclaimer

This tool is for personal use only. Please ensure that using such a tool complies with your organization's policies and Microsoft Teams' terms of service. The author is not responsible for any consequences of using this tool.

## License

MIT License - feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
