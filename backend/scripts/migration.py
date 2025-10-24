#!/usr/bin/env python
"""
Alembic migration helper script.

This script provides helper functions to create and run Alembic migrations.
"""
import argparse
import os
import subprocess
import sys

# Add the project root directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def create_migration(message):
    """Create a new migration with the given message."""
    print(f"Creating migration: {message}")
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error creating migration: {result.stderr}")
        return False
    print(result.stdout)
    return True


def run_migrations():
    """Apply all pending migrations."""
    print("Applying migrations")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error applying migrations: {result.stderr}")
        return False
    print(result.stdout)
    return True


def show_history():
    """Show migration history."""
    print("Migration history:")
    result = subprocess.run(
        ["alembic", "history"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error retrieving history: {result.stderr}")
        return False
    print(result.stdout)
    return True


def show_current():
    """Show current migration version."""
    print("Current migration version:")
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error retrieving current version: {result.stderr}")
        return False
    print(result.stdout)
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Alembic migration helper")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create migration
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Run migrations
    subparsers.add_parser("run", help="Apply all pending migrations")

    # Show history
    subparsers.add_parser("history", help="Show migration history")

    # Show current version
    subparsers.add_parser("current", help="Show current migration version")

    args = parser.parse_args()

    if args.command == "create":
        create_migration(args.message)
    elif args.command == "run":
        run_migrations()
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
