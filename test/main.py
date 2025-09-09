"""
TaleKeeper Desktop - Main Entry Point

Single-player D&D 2024 tactical RPG for Windows built with PyQt6 and SQLite.

Application Flow:
1. Initialize logging system
2. Create PyQt6 application with custom fonts
3. Setup SQLite database
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
        else:
            logger.warning(f"Font file not found at {font_path}")
        
        # Initialize database if needed
        from database.database_init import DatabaseInitializer
        
        db_initializer = DatabaseInitializer("talekeeper.db")
        
        # Check if database exists
        if not Path("talekeeper.db").exists():
            logger.info("No database found - initializing new database...")
            
            # Check for dev mode
            dev_mode = "--dev" in sys.argv or os.environ.get("TALEKEEPER_DEV") == "true"
            
            if not db_initializer.initialize(dev_mode=dev_mode):
                error_msg = "Failed to initialize database. Please check the logs."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            logger.info("Database initialized successfully")
        else:
            # Database exists, check for migrations
            logger.info("Checking for database updates...")
            if not db_initializer.check_and_apply_migrations():
                logger.warning("Failed to apply migrations, continuing with existing database")
        
        # Verify database integrity
        if not db_initializer.verify_database():
            error_msg = "Database verification failed. The database may be corrupted."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Check critical equipment data still exists (hasn't been migrated yet)
        #required_data_files = [
        #    "data/equipment.json"
        ]
        
        missing_files = []
        for file_path in required_data_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            error_msg = f"Missing required data files:\n" + "\n".join(f"- {f}" for f in missing_files)
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
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