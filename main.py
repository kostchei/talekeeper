"""
TaleKeeper Desktop - Main Entry Point

Single-player D&D 2024 tactical RPG for Windows built with PyQt6 and IndexedDB.

Application Flow:
1. Initialize logging system
2. Create PyQt6 application with custom fonts
3. Setup IndexedDB database (migrate from SQLite if needed)
4. Load D&D 2024 game data from JSON files
5. Initialize game engine coordinator
6. Create and display main GUI window
7. Start event loop and handle graceful shutdown
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

from core.game_engine_sqlite import GameEngineSQLite
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
        
        # Check if SQLite database exists, otherwise create it from IndexedDB
        sqlite_db_path = Path("talekeeper.db")
        if not sqlite_db_path.exists():
            logger.info("No SQLite database found - checking for IndexedDB to migrate...")
            indexeddb_path = Path("talekeeper.idb")
            if indexeddb_path.exists():
                logger.info("Found IndexedDB file - running migration to SQLite...")
                # Run our migration script
                import subprocess
                try:
                    result = subprocess.run(["python", "migrate_to_sqlite.py"], 
                                          capture_output=True, text=True, check=True)
                    logger.info("IndexedDB to SQLite migration completed successfully")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Migration failed: {e}")
                    logger.info("Creating empty SQLite database...")
                    # Create empty database with schema
                    import sqlite3
                    conn = sqlite3.connect("talekeeper.db")
                    with open("database_schema.sql", "r") as f:
                        schema_sql = f.read()
                    conn.executescript(schema_sql)
                    conn.close()
            else:
                logger.info("No existing data found - creating fresh SQLite database...")
                # Create fresh database with schema
                import sqlite3
                conn = sqlite3.connect("talekeeper.db")
                with open("database_schema.sql", "r") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.close()
        
        # Initialize SQLite game engine
        game_engine = GameEngineSQLite()
        
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