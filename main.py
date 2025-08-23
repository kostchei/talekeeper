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
import tkinter as tk
from pathlib import Path
from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Enable DPI awareness on Windows
if sys.platform.startswith('win'):
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass  # Ignore if not available

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
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Create main window
        root = tk.Tk()
        root.title("TaleKeeper - D&D 2024 Adventure")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Initialize game engine
        game_engine = GameEngine()
        
        # Create main application window
        app = MainWindow(root, game_engine)
        
        # Start the GUI event loop
        logger.info("Starting GUI application")
        root.mainloop()
        
    except Exception as e:
        logger.exception(f"Fatal error starting application: {e}")
        # Show error dialog if possible
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Fatal Error", f"Failed to start TaleKeeper:\n\n{str(e)}")
        except:
            print(f"Fatal error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("TaleKeeper Desktop Application shutting down")


if __name__ == "__main__":
    main()