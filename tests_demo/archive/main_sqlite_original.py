"""
File: main.py
Path: /main.py

TaleKeeper Desktop - Entry Point
Single-player D&D 2024 tactical RPG for Windows.

Pseudo Code:
1. Initialize logging and configuration
2. Setup SQLite database and create tables
3. Load game data (races, classes, monsters) from JSON files
4. Initialize and start the main GUI application
5. Handle graceful shutdown and save state

AI Agents: This is the application entry point. Start here for understanding program flow.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# PyQt6 handles DPI awareness automatically - no manual setup needed

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.database import init_database
from core.game_engine import GameEngine
from tests_demo.test_full_ui import FullUITestWindow


def setup_logging():
    """Configure logging for the application."""
    logger.remove()  # Remove default handler
    logger.add(
        "talekeeper.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
    )
    logger.add(
        sys.stderr,
        level="WARNING",
        format="{time:HH:mm:ss} | {level} | {message}"
    )


def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting TaleKeeper Desktop Application (PyQt6)")
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Create PyQt6 application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for dark theme
        
        # Initialize game engine
        game_engine = GameEngine()
        
        # Create main application window (using our working PyQt6 interface)
        window = FullUITestWindow()
        window.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        window.show()
        
        # Start the GUI event loop
        logger.info("Starting PyQt6 GUI application")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception(f"Fatal error starting application: {e}")
        # Show error dialog if possible
        try:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Fatal Error")
            msg.setText(f"Failed to start TaleKeeper:\n\n{str(e)}")
            msg.exec()
        except:
            print(f"Fatal error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("TaleKeeper Desktop Application shutting down")


if __name__ == "__main__":
    main()