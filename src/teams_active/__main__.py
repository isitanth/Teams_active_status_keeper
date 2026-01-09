"""Command-line entry point for Teams Active Status Keeper."""

from __future__ import annotations

import argparse
import sys

from . import __version__, setup_logging
from .health import format_health_report, read_health_status
from .keeper import TeamsActiveKeeper


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="teams-active",
        description="Keep Microsoft Teams web version showing as active (green dot).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command (default)
    run_parser = subparsers.add_parser("run", help="Run the status keeper (default)")
    run_parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file (default: ~/.teams_active_config.json)",
    )
    run_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    # Status command
    subparsers.add_parser("status", help="Check service health status")

    return parser.parse_args()


def cmd_run(args: argparse.Namespace) -> int:
    """Run the Teams Active Keeper."""
    import logging  # noqa: PLC0415

    level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    setup_logging(level=level)

    logger = logging.getLogger(__name__)

    try:
        config_path = getattr(args, "config", None)
        keeper = TeamsActiveKeeper(config_path=config_path)
        keeper.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error("Fatal error: %s", e)
        return 1


def cmd_status() -> int:
    """Show service health status."""
    status = read_health_status()
    report = format_health_report(status)
    print(report)

    if status is None:
        return 2  # Unknown status
    return 0 if status.is_healthy else 1


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Default to 'run' if no command specified
    if args.command is None or args.command == "run":
        return cmd_run(args)
    elif args.command == "status":
        return cmd_status()
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
