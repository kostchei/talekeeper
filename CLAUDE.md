# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaleKeeper is a single-player D&D 2024 tactical RPG desktop application for Windows. It's built with Python + Tkinter for the GUI, SQLite + SQLAlchemy for data persistence, and can be packaged into a standalone Windows executable using PyInstaller.

## Development Commands

### Running the Application
```bash
# Safe launcher with dependency checks and better error handling
python run_game.py

# Direct launch (main entry point)
python main.py
```

### Building Executable
```bash
# Install dependencies and build Windows executable
build.bat

# Manual build process
pip install -r requirements.txt
pyinstaller build.spec
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Core dependencies: sqlalchemy, loguru, alembic, pyinstaller
# Development/testing: pytest, black, flake8
```

### Testing
```bash
# Run tests (if pytest tests exist)
pytest

# Code formatting
black .

# Linting
flake8
```

## Architecture Overview

### Core Systems
- **`core/game_engine.py`** - Central coordinator for all game systems, manages application state
- **`core/database.py`** - SQLite database setup with SQLAlchemy ORM, table initialization
- **`services/dice.py`** - D&D dice rolling mechanics and probability systems

### Data Layer
- **`models/`** - SQLAlchemy ORM models for characters, monsters, items, combat, game state
- **`data/`** - JSON files containing D&D 2024 game data (races, classes, backgrounds, monsters, equipment)
- **`talekeeper.db`** - SQLite database file created automatically on first run

### User Interface
- **`ui/main_window.py`** - Main Tkinter application window and navigation
- **`ui/character_creator.py`** - Character creation interface with D&D 2024 rules
- **`ui/combat_screen.py`** - Turn-based combat interface
- **`ui/game_screen.py`** - Main gameplay and exploration interface

### Application Flow
1. `main.py` initializes logging, database, and starts the GUI
2. `core/game_engine.py` coordinates all game systems and state management
3. UI components interact with the game engine to perform game operations
4. All game data is persisted to SQLite database via SQLAlchemy models

### Key Design Patterns
- **MVC Architecture**: UI components (View) → GameEngine (Controller) → Models/Database (Model)
- **ORM Pattern**: All database operations go through SQLAlchemy models
- **Service Layer**: Business logic encapsulated in services (dice, combat, etc.)
- **State Management**: Centralized through GameEngine with database persistence

### Database Schema
- Characters, monsters, items use SQLAlchemy declarative models
- Save slots support multiple character saves with metadata
- Combat sessions track initiative, actions, and state
- Game data loaded from JSON files into database on initialization

### Build System
- **`build.spec`** - PyInstaller configuration for Windows executable
- **`build.bat`** - Windows batch script for automated building
- Bundles all dependencies, data files, and assets into single `.exe`
- Uses UPX compression and excludes unnecessary modules to reduce size