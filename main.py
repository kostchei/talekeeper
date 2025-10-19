# unsure
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
import subprocess
from pathlib import Path
from loguru import logger

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont

from talekeeper.paths import get_database_path, get_assets_path, get_logs_path, get_root_path
from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.ui.main_window import MainWindow
from talekeeper.ui.layout_profiles import BASELINE_PROFILE, LayoutProfile


def setup_logging():
    logger.remove()
    log_file = get_logs_path("talekeeper.log")
    logger.add(
        log_file,
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


def start_ollama_server():
    """Start Ollama server in background if not already running."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()

        if result == 0:
            logger.info("Ollama server already running")
            return

        logger.info("Starting Ollama server in background...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        logger.info("Ollama server started")
    except FileNotFoundError:
        logger.warning("Ollama not installed - narrative generation will use fallback text")
    except Exception as e:
        logger.warning(f"Could not start Ollama: {e} - narrative generation will use fallback text")


def main(layout_profile: LayoutProfile | None = None):
    try:
        setup_logging()
        logger.info("Starting TaleKeeper Desktop Application")

        start_ollama_server()

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        font_path = Path(get_assets_path("art/IMFellGreatPrimer-Regular.ttf"))
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

        from talekeeper.database.database_init import DatabaseInitializer

        db_path = get_database_path()
        db_initializer = DatabaseInitializer(db_path)

        if not Path(db_path).exists():
            logger.info("No database found - initializing new database...")

            dev_mode = "--dev" in sys.argv or os.environ.get("TALEKEEPER_DEV") == "true"

            if not db_initializer.initialize(dev_mode=dev_mode):
                error_msg = "Failed to initialize database. Please check the logs."
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            logger.info("Database initialized successfully")
        else:
            logger.info("Checking for database updates...")
            if not db_initializer.check_and_apply_migrations():
                logger.warning("Failed to apply migrations, continuing with existing database")

        if not db_initializer.verify_database():
            error_msg = "Database verification failed. The database may be corrupted."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        game_engine = GameEngineSQLite()

        profile = layout_profile or BASELINE_PROFILE
        window = MainWindow(layout_profile=profile)
        window.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        window.show()

        logger.info("Starting PyQt6 GUI application")
        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"Fatal error starting application: {e}")
        try:
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
