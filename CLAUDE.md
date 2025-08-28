# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaleKeeper is a single-player D&D 2024 tactical RPG desktop application for Windows. It's built with Python + PyQt6 for the GUI, IndexedDB simulation for data persistence, and can be packaged into a standalone Windows executable using PyInstaller.

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

# Core dependencies: PyQt6, loguru, pyinstaller
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
- **`core/game_engine_indexeddb.py`** - Central coordinator for all game systems, manages application state with IndexedDB
- **`core/database_indexeddb.py`** - IndexedDB simulation setup and data management
- **`services/dice.py`** - D&D dice rolling mechanics and probability systems

### Data Layer
- **`models/*_indexeddb.py`** - Python dataclass models for characters, monsters, items, combat, game state
- **`data/`** - JSON files containing D&D 2024 game data (races, classes, backgrounds, monsters, equipment)
- **`talekeeper.idb`** - IndexedDB JSON file created automatically on first run

### User Interface
- **`ui/main_window.py`** - Main PyQt6 application window and navigation
- **`ui/character_creator.py`** - Character creation interface with D&D 2024 rules
- **`ui/combat_screen.py`** - Turn-based combat interface
- **`ui/game_screen.py`** - Main gameplay and exploration interface

### Application Flow
1. `main.py` initializes logging, IndexedDB database, and starts the GUI
2. `core/game_engine_indexeddb.py` coordinates all game systems and state management
3. UI components interact with the game engine to perform game operations
4. All game data is persisted to IndexedDB JSON file via dataclass models

### Key Design Patterns
- **MVC Architecture**: UI components (View) → GameEngineIndexedDB (Controller) → Dataclass Models/IndexedDB (Model)
- **Dataclass Pattern**: All database operations use Python dataclasses with JSON serialization
- **Service Layer**: Business logic encapsulated in services (dice, combat, etc.)
- **State Management**: Centralized through GameEngineIndexedDB with IndexedDB persistence

### Database Schema
- Characters, monsters, items use Python dataclass models
- Save slots support multiple character saves with metadata
- Combat sessions track initiative, actions, and state
- Game data loaded from JSON files into IndexedDB on initialization

### Build System
- **`build.spec`** - PyInstaller configuration for Windows executable
- **`build.bat`** - Windows batch script for automated building
- Bundles all dependencies, data files, and assets into single `.exe`
- Uses UPX compression and excludes unnecessary modules to reduce size