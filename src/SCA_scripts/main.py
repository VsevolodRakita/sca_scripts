"""
Your Project CLI

Usage:
    python main.py <command> [options]

Features:
    - Reads version dynamically from pyproject.toml
    - Supports multiple subcommands
    - Includes professional logging system with --verbose flag
"""

import argparse
import sys
import logging
from pathlib import Path
import json
from urllib.request import urlopen
import webbrowser
import platform
import tomllib  

# Import your script modules
import SCA_scripts.financial_analysis.balance_sheet as balance_sheet
import SCA_scripts.financial_analysis.p_and_l as pnl


GITHUB_REPO = "VsevolodRakita/sca_scripts"
GITHUB_LATEST_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
# ---------------------------
# Utility Functions
# ---------------------------

def parse_version(v: str) -> tuple[int, ...]:
    """Very small semantic-version parser: '1.2.3' -> (1, 2, 3)."""
    return tuple(int(part) for part in v.strip().lstrip("v").split("."))


def get_latest_release_info():
    """Query GitHub for the latest release info."""
    logging.debug("Checking GitHub for latest release: %s", GITHUB_LATEST_URL)
    with urlopen(GITHUB_LATEST_URL) as resp:
        data = json.load(resp)

    tag = data["tag_name"]          # e.g. "v0.2.0"
    version = tag.lstrip("v")       # "0.2.0"
    html_url = data["html_url"]     # release page
    assets = data.get("assets", []) # list of assets (installers, binaries, etc.)

    return version, html_url, assets


def run_update(_args):
    current = get_version()
    logging.info("Current version: %s", current)

    try:
        latest, release_url, _assets = get_latest_release_info()
    except Exception as e:
        logging.error("Failed to check for updates: %s", e)
        print("Could not check for updates. Please try again later.")
        return

    logging.info("Latest version on GitHub: %s", latest)

    if parse_version(latest) <= parse_version(current):
        print(f"You are up to date (version {current}).")
        return

    print(f"A newer version is available: {latest} (you have {current}).")
    print("Opening the GitHub release page so you can download the installer...")
    webbrowser.open(release_url)

def get_version() -> str:
    """Read project version from pyproject.toml (Poetry)."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "unknown"


def setup_logging(verbose: bool = False, log_file: str = "app.log"):
    """Configure logging for console and file output."""
    level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),   # Console output
            logging.FileHandler(log_file, mode="a", encoding="utf-8")  # Log file
        ]
    )

    # Log startup
    logging.debug("Logging initialized (verbose=%s, log_file=%s)", verbose, log_file)


# ---------------------------
# Main Entry Point
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="SCA_scripts",
        description="Useful scripts for SCA",
        epilog="Use 'SCA_scripts <command> --help' for detailed command info."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )

    parser.add_argument(
        "--verbose", "-V",
        action="store_true",
        help="Enable detailed (debug-level) logging."
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
        help="Available commands"
    )

    # ---- Analyze BS command ----
    parser_bs = subparsers.add_parser(
        "bs",
        help="Analyze the balance sheet in the given excel file."
    )
    parser_bs.add_argument("--input", "-i", required=True, help="Path to input excel file.")
    parser_bs.add_argument("--tab_name", "-t", help="Optional name of the tab where the balance sheet is located. If not provided, will assume active tab.")
    parser_bs.add_argument("--output", "-o", help="Optional path for analysis output.")
    parser_bs.set_defaults(func=balance_sheet.run)

    # ---- Analyze P&L command ----
    parser_pnl = subparsers.add_parser(
        "pnl",
        help="Convert files between formats."
    )
    parser_pnl.add_argument("--input", "-i", required=True, help="Path to input excel file.")
    parser_pnl.add_argument("--tab_name", "-t", help="Optional name of the tab where the balance sheet is located. If not provided, will assume active tab.")
    parser_pnl.add_argument("--output", "-o", help="Optional path for analysis output.")
    parser_pnl.set_defaults(func=pnl.run)

    # ---- NEW: update command ----
    parser_update = subparsers.add_parser(
        "update",
        help="Check GitHub for a newer version and open the installer page.",
    )
    parser_update.set_defaults(func=run_update)

    # ---- Parse Arguments ----
    args = parser.parse_args()

    # ---- Setup Logging ----
    setup_logging(args.verbose)

    logging.info("Starting Project CLI (version %s)", get_version())
    logging.debug("Command arguments: %s", vars(args))

    try:
        args.func(args)
        logging.info("✅ Command '%s' completed successfully.", args.command)
    except AttributeError:
        parser.print_help()
    except Exception as e:
        logging.exception("❌ An error occurred while executing '%s': %s", args.command, e)
        sys.exit(1)


if __name__ == "__main__":
    main()