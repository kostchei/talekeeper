"""
File: main_indexeddb.py
Path: /main_indexeddb.py

TaleKeeper Desktop - IndexedDB Version Entry Point
Single-player D&D 2024 tactical RPG for Windows with IndexedDB backend.

This version uses IndexedDB through a Python wrapper for more complex
database operations while maintaining compatibility with the existing codebase.

Pseudo Code:
1. Initialize logging and configuration
2. Setup IndexedDB database and migrate from SQLite if needed
3. Load game data (races, classes, monsters) from JSON files
4. Initialize and start the main GUI application
5. Handle graceful shutdown and save state

AI Agents: This is the IndexedDB version entry point. Uses IndexedDB instead of SQLite.
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
from core.game_engine import GameEngine
from tests_demo.test_full_ui import FullUITestWindow


def setup_logging():
    """Configure logging for the IndexedDB version."""
    logger.remove()  # Remove default handler
    logger.add(
        "talekeeper_indexeddb.log",
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
    """Main application entry point for IndexedDB version."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting TaleKeeper Desktop Application (PyQt6 + IndexedDB)")
        
        # Create PyQt6 application first
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for dark theme
        
        # Initialize IndexedDB database
        logger.info("Initializing IndexedDB database...")
        init_indexeddb_database()
        
        # Check for existing SQLite database and offer migration
        sqlite_db_path = Path("talekeeper.db")
        if sqlite_db_path.exists():
            logger.info("Found existing SQLite database, attempting migration...")
            try:
                migrate_from_sqlite("talekeeper.db")
                logger.info("SQLite to IndexedDB migration completed successfully")
            except Exception as e:
                logger.warning(f"Migration failed, continuing with fresh IndexedDB: {e}")
        
        # Initialize game engine (will use IndexedDB backend)
        game_engine = GameEngine()
        
        # Create main application window
        window = FullUITestWindow()
        window.setWindowTitle("TaleKeeper - D&D 2024 Adventure (IndexedDB)")
        window.show()
        
        # Start the GUI event loop
        logger.info("Starting PyQt6 GUI application with IndexedDB backend")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception(f"Fatal error starting IndexedDB application: {e}")
        # Show error dialog if possible
        try:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Fatal Error")
            msg.setText(f"Failed to start TaleKeeper (IndexedDB):\n\n{str(e)}")
            msg.exec()
        except:
            print(f"Fatal error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("TaleKeeper Desktop Application (IndexedDB) shutting down")


if __name__ == "__main__":
    main()