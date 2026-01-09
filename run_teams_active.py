#!/usr/bin/env python3
"""
Backward-compatible entry point for Teams Active Status Keeper.

This script provides backward compatibility for direct script execution.
For new usage, prefer: python -m teams_active
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for direct script execution
sys.path.insert(0, str(Path(__file__).parent / "src"))

from teams_active import main, setup_logging

if __name__ == "__main__":
    setup_logging()
    main()
