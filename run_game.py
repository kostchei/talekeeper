#!/usr/bin/env python3
"""
Safe launcher for TaleKeeper Desktop.
Handles common startup issues and provides better error messages.
"""

import sys
import os
from pathlib import Path
import traceback


def setup_environment():
    """Setup the Python environment for running TaleKeeper."""
    # Add project root to Python path
    project_root = Path(__file__).parent.resolve()
    sys.path.insert(0, str(project_root))

    # Set working directory to project root
    os.chdir(project_root)

    print(f"Project root: {project_root}")
    print(f"Working directory: {Path.cwd()}")


def check_requirements():
    """Check if required packages are installed."""
    required_packages = {
        "sqlalchemy": "SQLAlchemy",
        "loguru": "Loguru",
        "alembic": "Alembic",
        "PySide6": "PySide6",
    }

    missing = []

    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[ERROR] {name} (missing)")
            missing.append(package)

    if missing:
        print("\n" + "=" * 50)
        print("MISSING DEPENDENCIES")
        print("=" * 50)
        print("Please install missing packages:")
        print(f"pip install {' '.join(missing)}")
        print("=" * 50)
        return False

    return True


def check_data_files():
    """Check if required data files exist."""
    required_files = [
        "data/races.json",
        "data/classes.json",
        "data/backgrounds.json",
        "data/monsters.json",
        "data/equipment.json",
    ]

    missing = []

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} (missing)")
            missing.append(file_path)

    if missing:
        print("\n" + "=" * 50)
        print("MISSING DATA FILES")
        print("=" * 50)
        print("The following data files are required:")
        for file_path in missing:
            print(f"  - {file_path}")
        print("=" * 50)
        return False

    return True


def run_game():
    """Run the main TaleKeeper application."""
    try:
        print("\n" + "=" * 50)
        print("STARTING TALEKEEPER")
        print("=" * 50)

        # Import and run the main application
        import main

        main.main()

    except ImportError as e:
        print(f"\n[ERROR] Import Error: {e}")
        print("\nThis usually means:")
        print("1. You're not in the correct directory")
        print("2. Required packages are missing")
        print("3. File paths are incorrect")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        return False

    return True


def main():
    """Main launcher function."""
    print("TaleKeeper Desktop Launcher")
    print("=" * 50)

    # Setup environment
    setup_environment()

    # Check dependencies
    print("\nChecking dependencies...")
    if not check_requirements():
        input("\nPress Enter to exit...")
        return

    # Check data files
    print("\nChecking data files...")
    if not check_data_files():
        input("\nPress Enter to exit...")
        return

    # Try to run the game
    print("\nAll checks passed!")
    if not run_game():
        input("\nPress Enter to exit...")
        return

    print("\nTaleKeeper closed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\nLauncher error: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
