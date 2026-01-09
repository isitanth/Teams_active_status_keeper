#!/bin/bash

# Teams Active Status Keeper Installation Script
# This script sets up the LaunchAgent for automatic startup

set -e

echo "🚀 Teams Active Status Keeper - Installation Script"
echo "=================================================="
echo ""

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="com.teamsactive.keeper.plist"
PLIST_PATH="$SCRIPT_DIR/$PLIST_FILE"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
DEST_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"
LOG_DIR="$HOME/Library/Logs/TeamsActiveStatus"

# Check if Python 3 is installed
echo "📋 Checking requirements..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check if Chrome is installed
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo "⚠️  Warning: Google Chrome not found."
    echo "Please install Chrome: brew install --cask google-chrome"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Google Chrome found"
fi

# Create and activate virtual environment
echo ""
echo "📦 Setting up virtual environment..."
VENV_DIR="$SCRIPT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
else
    python3 -m venv "$VENV_DIR" || {
        echo "❌ Error: Failed to create virtual environment."
        exit 1
    }
    echo "✅ Virtual environment created"
fi

# Install Python dependencies in virtual environment
echo ""
echo "📦 Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" || {
    echo "❌ Error: Failed to install dependencies."
    exit 1
}
echo "✅ Dependencies installed"

# Make the script executable
echo ""
echo "🔧 Making script executable..."
chmod +x "$SCRIPT_DIR/run_teams_active.py"
echo "✅ Script is now executable"

# Create log directory
echo ""
echo "📁 Creating log directory..."
mkdir -p "$LOG_DIR"
echo "✅ Log directory created at $LOG_DIR"

# Get Python path from virtual environment
PYTHON_PATH="$VENV_DIR/bin/python3"
echo ""
echo "🔍 Using virtual environment Python: $PYTHON_PATH"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Create a temporary plist with the correct paths
echo ""
echo "📝 Creating LaunchAgent configuration..."
TEMP_PLIST="/tmp/com.teamsactive.keeper.plist"

cat > "$TEMP_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.teamsactive.keeper</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>-m</string>
        <string>teams_active</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR/src</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/stderr.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

# Copy the plist to LaunchAgents
cp "$TEMP_PLIST" "$DEST_PLIST"
rm "$TEMP_PLIST"
echo "✅ LaunchAgent configuration created"

# Unload existing service if running
echo ""
echo "🔄 Checking for existing service..."
if launchctl list | grep -q "com.teamsactive.keeper"; then
    echo "Stopping existing service..."
    launchctl unload "$DEST_PLIST" 2>/dev/null || true
fi

# Load the LaunchAgent
echo ""
echo "🚀 Loading LaunchAgent..."
launchctl load "$DEST_PLIST"

# Check if it loaded successfully
sleep 2
if launchctl list | grep -q "com.teamsactive.keeper"; then
    echo "✅ Service loaded successfully!"
else
    echo "⚠️  Service may not have loaded. Check the logs for details."
fi

echo ""
echo "=================================================="
echo "✨ Installation Complete! ✨"
echo "=================================================="
echo ""
echo "The Teams Active Status Keeper is now running in the background."
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. For the first run, you may need to log in to Teams:"
echo "   - Edit ~/.teams_active_config.json and set \"headless\": false"
echo "   - Run: launchctl stop com.teamsactive.keeper"
echo "   - Run: cd $SCRIPT_DIR/src && $VENV_DIR/bin/python3 -m teams_active"
echo "   - Log in to Teams in the browser window"
echo "   - Stop the script (Ctrl+C) and set \"headless\": true again"
echo "   - Run: launchctl start com.teamsactive.keeper"
echo ""
echo "2. View logs: tail -f $LOG_DIR/teams_active.log"
echo ""
echo "3. Control the service:"
echo "   - Start:  launchctl start com.teamsactive.keeper"
echo "   - Stop:   launchctl stop com.teamsactive.keeper"
echo "   - Unload: launchctl unload $DEST_PLIST"
echo ""
echo "📖 For more information, see README.md"
echo ""
