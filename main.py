"""
File: main.py
Path: /main.py

TaleKeeper Desktop - Entry Point
Single-player D&D 2024 tactical RPG for Windows with IndexedDB backend.

This version uses IndexedDB through a Python wrapper for more complex
database operations while maintaining compatibility with the existing codebase.

Pseudo Code:
1. Initialize logging and configuration
2. Setup IndexedDB database and migrate from SQLite if needed
3. Load game data (races, classes, monsters) from JSON files
4. Initialize and start the main GUI application
5. Handle graceful shutdown and save state

AI Agents: This is the main entry point. Uses IndexedDB for enhanced database operations.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.database_indexeddb import init_indexeddb_database, migrate_from_sqlite
from core.database import init_database
from core.game_engine import GameEngine
from ui.main_window import MainWindow


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
        logger.info("Starting TaleKeeper Desktop Application")
        
        # Create PyQt6 application first
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for dark theme
        
        # Initialize IndexedDB database
        logger.info("Initializing IndexedDB database...")
        init_indexeddb_database()
        
        # Initialize SQLite database (still needed for GameEngine)
        logger.info("Initializing SQLite database...")
        init_database()
        
        # Check for existing SQLite database backup and offer migration
        sqlite_db_path = Path("tests_demo/archive/talekeeper_sqlite_original.db")
        if sqlite_db_path.exists() and not Path("talekeeper.idb").exists():
            logger.info("Found SQLite backup database, attempting migration...")
            try:
                migrate_from_sqlite("tests_demo/archive/talekeeper_sqlite_original.db")
                logger.info("SQLite to IndexedDB migration completed successfully")
            except Exception as e:
                logger.warning(f"Migration failed, continuing with fresh IndexedDB: {e}")
        
        # Initialize game engine (uses SQLite backend)
        game_engine = GameEngine()
        
        # Create main application window
        window = MainWindow()
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