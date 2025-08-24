"""
Qt entry point for TaleKeeper.

This replaces the previous Tkinter-based launcher and sets up the
application using PySide6.
"""

from __future__ import annotations

import sys
from pathlib import Path
from loguru import logger
from PySide6.QtWidgets import QApplication

# Ensure project root on path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import init_database
from core.game_engine import GameEngine
from ui_qt.main_window_qt import MainWindow


def setup_logging() -> None:
    """Configure logging for the application."""
    logger.remove()
    logger.add(
        "talekeeper.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    )
    logger.add(
        sys.stderr, level="WARNING", format="{time:HH:mm:ss} | {level} | {message}"
    )


def main() -> None:
    try:
        setup_logging()
        logger.info("Starting TaleKeeper Desktop Application")

        init_database()

        app = QApplication(sys.argv)
        engine = GameEngine()
        window = MainWindow(engine)
        window.show()
        logger.info("Starting Qt event loop")
        app.exec()

    except Exception as e:  # pragma: no cover - log unexpected startup errors
        logger.exception(f"Fatal error starting application: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("TaleKeeper Desktop Application shutting down")


if __name__ == "__main__":  # pragma: no cover
    main()
