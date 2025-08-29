# TaleKeeper Archive Directory

This directory contains files that were part of the TaleKeeper codebase but are no longer used by the current production system. They have been preserved for historical reference and potential future use.

## Archive Organization

### `legacy_sqlite_system/`
**SQLAlchemy-based system files** - Replaced by IndexedDB system
- `database.py` - Original SQLite database setup with SQLAlchemy
- `game_engine.py` - SQLAlchemy-based game engine  
- `character.py` - SQLAlchemy character model
- `combat.py` - SQLAlchemy combat model
- `game.py` - SQLAlchemy game state model  
- `items.py` - SQLAlchemy items model
- `monsters.py` - SQLAlchemy monsters model

**Replacement:** Current system uses `*_indexeddb.py` versions for better performance and simpler data handling.

### `legacy_ui_tkinter/`
**Tkinter-based UI components** - Replaced by PyQt6 system
- `character_creator.py` - Tkinter character creation interface
- `combat_screen.py` - Tkinter combat interface  
- `game_screen.py` - Tkinter main game screen

**Replacement:** Current system uses PyQt6 with `ui/main_window.py` and component panels.

### `standalone_utilities/`
**Development and debugging tools** - Not part of main application
- `combat.py` - Standalone combat service (unused by production)
- `check_database_characters.py` - Database inspection utility
- `debug_expansion.py` - Character sheet debugging tool

**Note:** These were development utilities that aren't integrated into the main application flow.

### `development_tests/`
**Complete tests_demo folder** - Development and testing files
- Contains all test files, combat demos, and UI component tests
- Includes the original `archive/` subdirectory with historical versions
- All `.py` files in this directory were standalone test/demo scripts

**Note:** These files were valuable for development but aren't part of the production application.

## Current Production System

After archiving, the production system consists of:

### Core Files (4 files)
- `main.py` - Main entry point
- `run_game.py` - Safe launcher with dependency checks  
- `core/database_indexeddb.py` - IndexedDB database system
- `core/game_engine_indexeddb.py` - Central game coordinator

### Data Models (5 files)  
- `models/character_indexeddb.py` - Character data model
- `models/combat_indexeddb.py` - Combat session model
- `models/game_indexeddb.py` - Game state model
- `models/items_indexeddb.py` - Items and equipment model
- `models/monsters_indexeddb.py` - Monster data model

### Services (1 file)
- `services/dice.py` - Dice rolling system

### User Interface (7 files)
- `ui/main_window.py` - Main application window
- `ui/themes.py` - Theme system  
- `menu/game_menu.py` - Game menu component
- `character_sheet/character_panel.py` - Character display panel
- `encounter_pane/encounter_panel.py` - Encounter/exploration panel
- `log/log_panel.py` - System log panel
- `equipment_layout/equipment_panel.py` - Equipment panel
- `action_cards/action_panel.py` - Combat actions panel

### Support Files
- `core/dtos.py` - Data transfer objects
- All `__init__.py` files for Python package structure

## Total Files Archived

**33 Python files** representing 62% of the original codebase have been archived, leaving a clean production system of **20 core files**.

## Restoration

If any archived functionality is needed in the future:
1. Copy the relevant files back to their original locations
2. Update imports and dependencies as needed
3. Test integration with the current IndexedDB system
4. Consider if the functionality should be ported to IndexedDB instead

## Archive Date

Files archived on: 2025-08-29