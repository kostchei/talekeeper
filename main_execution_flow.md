# TaleKeeper Main.py Execution Flow Documentation

## Overview
TaleKeeper Desktop is a single-player D&D 2024 tactical RPG built with Python + PyQt6, using IndexedDB simulation for data persistence. This document details the complete execution flow when `main.py` is run.

## 1. Application Entry Point (`main.py`)

### Initial Setup (Lines 21-38)
1. **Import Dependencies**: Core Python modules, PyQt6 components, and TaleKeeper modules
2. **Path Configuration**: Add project root to `sys.path` for proper imports
3. **Core Imports**:
   - `core.database_indexeddb`: Database initialization and migration utilities
   - `core.game_engine_indexeddb`: Central game coordinator
   - `ui.main_window`: Main application window

### Logging Configuration (`setup_logging()` - Lines 39-53)
1. **Remove Default Handler**: Clear loguru defaults
2. **File Logging**: 
   - Creates `talekeeper.log` with 10MB rotation, 7-day retention
   - INFO level with detailed format including module/function/line
3. **Console Logging**: 
   - stderr output for WARNING+ levels
   - Simplified time format for console

### Main Function Execution (`main()` - Lines 56-131)

#### Step 1: PyQt6 Application Setup (Lines 58-80)
1. **Create QApplication**: Initialize PyQt6 application instance
2. **Set Fusion Style**: Consistent cross-platform theming
3. **Font Loading**:
   - Load custom "IM Fell Great Primer Roman" from `art/` directory
   - Fallback to "Times New Roman" if custom font unavailable
   - Set application-wide font at 12pt size

#### Step 2: IndexedDB Database Initialization (Lines 82-102)
1. **Initialize IndexedDB**: Call `init_indexeddb_database()`
   - Creates object stores (tables): races, classes, backgrounds, monsters, items, characters, save_slots, etc.
   - Sets up indexes for efficient querying
2. **SQLite Migration Check**: 
   - Scans for existing SQLite databases in predefined paths
   - Attempts migration to IndexedDB if found and no IndexedDB exists
   - Supports migration from multiple legacy database locations

#### Step 3: Game Engine and UI Creation (Lines 104-113)
1. **GameEngineIndexedDB**: Initialize central game coordinator
2. **MainWindow**: Create and configure main application window
3. **Show Window**: Display the main interface
4. **Event Loop**: Start PyQt6's `app.exec()` for GUI interaction

#### Step 4: Error Handling and Shutdown (Lines 115-131)
1. **Exception Catching**: Comprehensive error handling with logging
2. **Error Dialog**: Show GUI error message if possible
3. **Graceful Shutdown**: Ensure proper application termination

## 2. Database Initialization (`core/database_indexeddb.py`)

### IndexedDBSimulator Class (Lines 37-208)
1. **Connection Management**: Async connection to JSON file-based storage
2. **Object Store Creation**: Equivalent to database tables
3. **Index Management**: For efficient querying by various fields
4. **CRUD Operations**: Add, get, update, delete operations
5. **Data Persistence**: JSON serialization to disk

### Database Setup (`init_indexeddb_database()` - Lines 302-354)
1. **Object Store Configuration**:
   - races, classes, subclasses, backgrounds (game data)
   - monsters, items (content data)
   - characters, save_slots, game_states (player data)
   - combat_sessions, character_inventory (session data)
2. **Index Creation**: Optimized queries for character lookups, monster CR, item types
3. **Initial Data Loading**: Populate database with D&D 2024 content

### Data Loading Functions (Lines 357-506)
1. **Race Loading**: `_load_indexeddb_races()` - Player character races
2. **Class Loading**: `_load_indexeddb_classes()` - Character classes and subclasses
3. **Background Loading**: `_load_indexeddb_backgrounds()` - Character backgrounds
4. **Monster Loading**: `_load_indexeddb_monsters()` - Creatures and NPCs
5. **Equipment Loading**: `_load_indexeddb_equipment()` - Items, weapons, armor

## 3. Game Engine Initialization (`core/game_engine_indexeddb.py`)

### GameEngineIndexedDB Class (Lines 34-660)
1. **Service Initialization**: 
   - DiceRoller for all random generation
   - Character, Monster, SaveSlot DTOs for data transfer
2. **State Management**:
   - Current character tracking
   - Active save slot management
   - Game state persistence
   - Combat session handling
3. **Settings Management**: Load/save application configuration from `config/settings.json`

### Core Functions
1. **Character Management**:
   - Create new characters with full D&D stats calculation
   - Load/save characters to/from IndexedDB
   - Character progression and leveling
2. **Data Access**:
   - Race, class, background retrieval for character creation
   - Equipment and monster queries
   - Save slot management
3. **Game Logic**:
   - Dice rolling integration
   - Combat coordination
   - Auto-save functionality

## 4. Main Window Creation (`ui/main_window.py`)

### MainWindow Class (Lines 28-619)
1. **UI Component Initialization**:
   - Game menu (top-left) for character/game management
   - Character panel (left column) for character stats
   - Encounter panel (center) for exploration/combat
   - Log panel (top-right) for system messages
   - Equipment panel (bottom-right) for inventory
   - Action panel (bottom-left) for combat actions
2. **Theme Management**: Light/dark theme switching with CSS
3. **Signal Connections**: Wire UI component interactions

### Character Loading Flow (Lines 343-382)
1. **Auto-load Last Character**: Try to load most recently played character
2. **Fallback to Recent**: If no last character, find most recent save
3. **Demo Data**: Load test data if no saved characters exist
4. **Error Handling**: Graceful fallback to demo mode

## 5. Service Layer Components

### Dice System (`services/dice.py`)
- **DiceRoller Class**: Comprehensive D&D dice mechanics
- **Standard Notation**: Supports "1d20+5", "2d6", etc.
- **Advantage/Disadvantage**: D&D 5e mechanics for d20 rolls  
- **Special Mechanics**: Exploding dice, rerolls, stat generation
- **Combat Integration**: Initiative, attack rolls, saving throws

## 6. Data Models

### Character Model (`models/character_indexeddb.py`)
- **Dataclass Structure**: Pure Python classes for IndexedDB compatibility
- **D&D Stats**: All 6 ability scores with calculated modifiers
- **Combat Stats**: HP, AC, death saves, conditions
- **Equipment**: Main/off-hand weapons, armor, shield slots
- **Progression**: Level, XP, proficiencies, features

## 7. File Dependencies and Data Flow

### Required Data Files (Loaded at startup):
- `data/races.json` → Character creation options
- `data/classes.json` → Character classes and subclasses  
- `data/backgrounds.json` → Character backgrounds
- `data/monsters.json` → Creatures for encounters
- `data/equipment.json` → Weapons, armor, items

### Generated Files:
- `talekeeper.idb` → IndexedDB JSON database
- `talekeeper.log` → Application logs
- `config/settings.json` → User preferences

## 8. Alternative Launch Path

### Safe Launcher (`run_game.py`)
1. **Environment Setup**: Path configuration and working directory
2. **Dependency Check**: Verify required packages installed
3. **Data File Validation**: Ensure all JSON files exist
4. **Error Handling**: Better error messages than direct main.py execution
5. **Launch**: Import and execute main.py with error recovery

## Summary

The complete execution flow follows this sequence:
1. **Logging Setup** → Configure application logging
2. **PyQt6 Initialization** → Create GUI application with custom fonts
3. **Database Setup** → Initialize IndexedDB with game data
4. **Game Engine Creation** → Central coordinator for all systems
5. **UI Creation** → Main window with all interface panels
6. **Character Loading** → Auto-load last character or demo data
7. **Event Loop** → Begin interactive GUI operation

The application uses a clean MVC architecture where the GameEngineIndexedDB acts as the controller, IndexedDB provides the model layer, and PyQt6 components handle the view layer.

## Clean Production Codebase

As of 2025-08-29, the codebase has been cleaned up with unused files archived. The production system now consists of **20 core Python files**:

### Core System (4 files)
- `main.py` - Application entry point
- `run_game.py` - Safe launcher
- `core/database_indexeddb.py` - Database system  
- `core/game_engine_indexeddb.py` - Game coordinator

### Data Models (5 files)
- `models/character_indexeddb.py` - Character model
- `models/combat_indexeddb.py` - Combat model
- `models/game_indexeddb.py` - Game state model
- `models/items_indexeddb.py` - Items model  
- `models/monsters_indexeddb.py` - Monster model

### Services (1 file)
- `services/dice.py` - Dice system

### User Interface (8 files)
- `ui/main_window.py` - Main window
- `ui/themes.py` - Theme system
- `menu/game_menu.py` - Game menu
- `character_sheet/character_panel.py` - Character panel
- `encounter_pane/encounter_panel.py` - Encounter panel  
- `log/log_panel.py` - Log panel
- `equipment_layout/equipment_panel.py` - Equipment panel
- `action_cards/action_panel.py` - Action panel

### Support (2 files)
- `core/dtos.py` - Data transfer objects
- All `__init__.py` files for Python imports

**33 legacy/unused files** (62% of original codebase) have been archived to `archive/` directory with full documentation for potential future restoration.