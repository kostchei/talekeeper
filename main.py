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
from PyQt6.QtGui import QFontDatabase, QFont

from core.database_indexeddb import init_indexeddb_database, migrate_from_sqlite
from core.game_engine_indexeddb import GameEngineIndexedDB
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
        app.setStyle('Fusion')  # Use Fusion style for consistent theming
        
        # Load custom IM Fell Great Primer Roman font
        font_path = project_root / "art" / "IMFellGreatPrimer-Regular.ttf"
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)[0]
                app.setFont(QFont(family, 12))
                logger.info(f"Loaded custom font: {family}")
            else:
                logger.warning(f"Failed to load font from {font_path}")
                app.setFont(QFont("Times New Roman", 12))  # Fallback font
        else:
            logger.warning(f"Font file not found at {font_path}")
            app.setFont(QFont("Times New Roman", 12))  # Fallback font
        
        # Initialize IndexedDB database
        logger.info("Initializing IndexedDB database...")
        init_indexeddb_database()
        
        # Check for existing SQLite databases and offer migration
        sqlite_paths = [
            Path("characters.db"),
            Path("tests_demo/archive/talekeeper_sqlite_original.db"),
            Path("tests_demo/talekeeper.db")
        ]
        
        for sqlite_db_path in sqlite_paths:
            if sqlite_db_path.exists() and not Path("talekeeper.idb").exists():
                logger.info(f"Found SQLite database {sqlite_db_path}, attempting migration...")
                try:
                    migrate_from_sqlite(str(sqlite_db_path))
                    logger.info("SQLite to IndexedDB migration completed successfully")
                    break
                except Exception as e:
                    logger.warning(f"Migration from {sqlite_db_path} failed, trying next: {e}")
        
        # Initialize IndexedDB game engine
        game_engine = GameEngineIndexedDB()
        
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