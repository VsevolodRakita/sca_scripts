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
import tomllib  # For Python 3.11+. Use `import tomli as tomllib` if older.

# Import your script modules
import SCA_scripts.financial_analysis.balance_sheet as balance_sheet
import SCA_scripts.financial_analysis.p_and_l as pnl

# ---------------------------
# Utility Functions
# ---------------------------

def get_version() -> str:
    """Read project version from pyproject.toml (Poetry)."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]
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