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
- **`ui/main_window.py`** - Main PyQt6 application window with integrated component panels
- **`ui/themes.py`** - Light/dark theme system with CSS styling
- **`menu/game_menu.py`** - Game menu component for character/save management
- **`character_sheet/character_panel.py`** - Character statistics and information panel
- **`encounter_pane/encounter_panel.py`** - Exploration and combat encounter interface
- **`log/log_panel.py`** - System message and event logging panel
- **`equipment_layout/equipment_panel.py`** - Equipment and inventory management panel
- **`action_cards/action_panel.py`** - Combat action selection interface

### Application Flow
1. `main.py` initializes logging system and creates PyQt6 application
2. IndexedDB database setup with D&D 2024 game data loading from JSON files
3. `core/game_engine_indexeddb.py` coordinates all game systems and state management
4. `ui/main_window.py` creates integrated UI with all component panels
5. UI components communicate via signals to game engine for operations
6. All game data persisted to `talekeeper.idb` JSON file via dataclass models

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

## Clean Production Architecture (2025-08-29)

After codebase cleanup, TaleKeeper now consists of **20 core Python files** organized as:

### Core System (4 files)
- `main.py` - Application entry point with PyQt6 setup
- `run_game.py` - Safe launcher with dependency validation
- `core/database_indexeddb.py` - JSON-based database system
- `core/game_engine_indexeddb.py` - Central game coordinator

### Data Models (5 files)
All use dataclasses for IndexedDB storage:
- `models/character_indexeddb.py` - Character stats and progression
- `models/combat_indexeddb.py` - Combat sessions and actions
- `models/game_indexeddb.py` - Game state and save slots
- `models/items_indexeddb.py` - Equipment and inventory
- `models/monsters_indexeddb.py` - Creatures and NPCs

### Services (1 file)
- `services/dice.py` - D&D dice mechanics and probability

### User Interface (8 files)
All use PyQt6 with signal-based communication:
- `ui/main_window.py` + `ui/themes.py` - Main window and theming
- `menu/game_menu.py` - Character/save management
- `character_sheet/character_panel.py` - Character display
- `encounter_pane/encounter_panel.py` - Exploration/combat
- `log/log_panel.py` - System messages
- `equipment_layout/equipment_panel.py` - Inventory
- `action_cards/action_panel.py` - Combat actions

### Support (2 files)
- `core/dtos.py` - Data transfer objects
- All `__init__.py` files - Python package structure

**33 legacy files** (62% of original codebase) archived to `archive/` directory.

## UI Styling Notes

### PyQt6 CSS Priority Issues
- **Global Theme Override Problem**: The global theme from `ui/themes.py` is applied to the entire application AFTER individual widget stylesheets are set, causing it to override local CSS even with `!important` declarations
- **Solution**: For critical styling that must override global themes, apply CSS directly to the widget using `widget.setStyleSheet()` instead of relying on class-level CSS in `_apply_styles()`
- **Example**: Character sheet expand button required direct styling to match equipment panel styling due to global theme interference
- **Best Practice**: Use direct widget styling for UI elements that need consistent appearance across theme changes