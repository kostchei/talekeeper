# PyQt6 Integration Plan for TaleKeeper

## Overview
This plan outlines the integration of the new PyQt6 UI widgets with the existing TaleKeeper game engine and data models, replacing the current Tkinter-based interface.

## Current Architecture Analysis

### Existing Components (Keep)
- **GameEngine** (`core/game_engine.py`) - Central game coordinator ✅
- **Models** (`models/`) - SQLAlchemy ORM models for all game data ✅
- **Services** (`services/`) - Dice rolling, combat logic ✅
- **Database** (`core/database.py`) - SQLite + SQLAlchemy setup ✅
- **Game Data** (`data/`) - JSON files for races, classes, monsters ✅

### Components to Replace
- **UI System** - Replace Tkinter (`ui/`) with PyQt6 widgets
- **Main Window** - Replace `MainWindow` with PyQt6 version
- **Game Screen** - Replace `GameScreen` with integrated widget layout

## Integration Plan

### Phase 1: Core UI Replacement

#### 1.1 PyQt6 Main Application Window
```python
# Create new file: ui/pyqt_main_window.py
class TaleKeeperMainWindow(QMainWindow):
    - Replaces ui/main_window.py
    - Uses existing GameEngine instance
    - Manages all PyQt6 widgets
    - Handles character loading/saving
```

#### 1.2 Widget Integration Manager
```python
# Create new file: ui/widget_manager.py
class WidgetManager:
    - Coordinates data flow between widgets
    - Connects GameEngine events to UI updates
    - Manages widget state synchronization
```

### Phase 2: Data Connections

#### 2.1 Character Sheet Widget → Character Model
**Data Flow:**
- `Character.to_dict()` → `CharacterPanel.load_character_data()`
- Real-time HP updates via GameEngine
- Skill calculations from ability scores + proficiencies
- Experience tracking and level-up detection

**Implementation:**
```python
def connect_character_data(character_panel, game_engine):
    character = game_engine.current_character
    if character:
        char_data = character.to_dict()
        # Transform to expected format
        formatted_data = {
            'name': char_data['name'],
            'level': char_data['level'],
            'race_name': char_data['race'],
            'class_name': char_data['character_class'],
            'current_hit_points': character.hit_points_current,
            'hit_points': character.hit_points_max,
            'armor_class': character.armor_class,
            'strength': char_data['ability_scores']['strength'],
            # ... etc for all abilities
        }
        character_panel.load_character_data(formatted_data)
```

#### 2.2 Equipment Panel → Character Equipment
**Data Sources:**
- Character equipment slots (weapon, armor, etc.)
- Character inventory items
- Item stats and effects

**Implementation:**
```python
def connect_equipment_data(equipment_panel, game_engine):
    character = game_engine.current_character
    
    # Load equipped items (would need to add to Character model)
    equipped_items = {
        'main_hand': character.main_hand_weapon,  # Add these fields
        'armor': character.armor,
        # ... etc
    }
    
    # Load inventory (would need inventory system)
    inventory_items = character.inventory_items  # Add this relationship
    
    equipment_panel.load_equipment_data(equipped_items, inventory_items)
```

#### 2.3 Encounter Pane → GameEngine Combat
**Data Sources:**
- `Monster` model from database
- `CombatSession` for active combat
- GameEngine encounter generation

**Implementation:**
```python
def connect_encounter_data(encounter_panel, game_engine):
    # Set exploration mode initially
    encounter_panel.set_exploration_mode()
    
    # Connect to combat events
    @game_engine.on_encounter_started
    def handle_encounter(monsters):
        encounter_data = {
            'name': f"Combat vs {len(monsters)} enemies",
            'difficulty': calculate_encounter_difficulty(monsters),
            'creatures': [m.name for m in monsters]
        }
        encounter_panel.add_encounter(encounter_data)
        encounter_panel.set_encounter_mode()
```

#### 2.4 Menu → GameEngine Operations
**Connections:**
- Character creation → GameEngine.create_character()
- Load game → GameEngine.load_character()
- Save game → GameEngine.save_game()
- Settings → GameEngine.settings

#### 2.5 Log Panel → GameEngine Events
**Event Sources:**
- Combat actions and results
- Dice rolls
- Character actions (rest, level up)
- System messages

**Implementation:**
```python
def connect_logging(log_panel, game_engine):
    # Connect to dice roller
    @game_engine.dice_roller.on_roll
    def log_dice_roll(roll_result):
        log_panel.log_dice(f"Rolled {roll_result}")
    
    # Connect to combat events
    @game_engine.on_combat_action
    def log_combat(action):
        log_panel.log_combat(action)
```

### Phase 3: Missing Data Model Extensions

#### 3.1 Character Equipment System
**Add to Character model:**
```python
class Character:
    # Equipment slots
    main_hand_weapon_id = Column(Integer, ForeignKey('items.id'))
    off_hand_item_id = Column(Integer, ForeignKey('items.id'))
    armor_id = Column(Integer, ForeignKey('items.id'))
    # ... other equipment slots
    
    # Relationships
    main_hand_weapon = relationship("Item", foreign_keys=[main_hand_weapon_id])
    # ... etc
```

#### 3.2 Inventory System
```python
class InventoryItem:
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, default=1)
    
class Character:
    inventory_items = relationship("InventoryItem", back_populates="character")
```

#### 3.3 Item Database
```python
class Item:
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)  # weapon, armor, consumable, etc.
    armor_class = Column(Integer)  # for armor
    attack_bonus = Column(Integer)  # for weapons
    weight = Column(Float)
    value = Column(Integer)  # gold pieces
```

### Phase 4: Event System Integration

#### 4.1 GameEngine Event Emitters
```python
class GameEngine:
    def __init__(self):
        self.events = EventEmitter()  # Add event system
    
    def emit_character_update(self):
        self.events.emit('character_updated', self.current_character)
    
    def emit_combat_action(self, action, results):
        self.events.emit('combat_action', action, results)
```

#### 4.2 Widget Event Handlers
```python
def setup_event_handlers(game_engine, widgets):
    @game_engine.events.on('character_updated')
    def update_character_widgets(character):
        widgets.character_panel.load_character_data(character.to_dict())
        widgets.equipment_panel.update_equipment(character)
        widgets.menu.update_character_info(character)
```

### Phase 5: Main Application Integration

#### 5.1 New Main Window
```python
# ui/pyqt_main_window.py
class TaleKeeperMainWindow(QMainWindow):
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.setup_ui()
        self.connect_data()
        
    def setup_ui(self):
        # Create all widgets like test_full_ui.py
        self.menu = GameMenu(self)
        self.character_sheet = CharacterPanel(self)
        self.encounter_pane = EncounterPanel(self)
        self.log_panel = LogPanel(self)
        self.equipment_panel = EquipmentPanel(self)
        self.action_panel = ActionPanel(self)
        
        # Position them with fixed positioning
        self.position_widgets()
        
    def connect_data(self):
        # Connect all widgets to game data
        connect_character_data(self.character_sheet, self.game_engine)
        connect_equipment_data(self.equipment_panel, self.game_engine)
        # ... etc
```

#### 5.2 Updated main.py
```python
def main():
    # Setup logging and database (keep existing)
    setup_logging()
    init_database()
    
    # Create PyQt6 application instead of Tkinter
    app = QApplication(sys.argv)
    
    # Initialize game engine
    game_engine = GameEngine()
    
    # Create PyQt6 main window
    main_window = TaleKeeperMainWindow(game_engine)
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())
```

## Implementation Order

1. **Create PyQt6 main window structure** (`ui/pyqt_main_window.py`)
2. **Add missing data models** (Item, InventoryItem, equipment slots)
3. **Create widget manager** for data coordination
4. **Connect character sheet** to Character model
5. **Connect equipment panel** to inventory system
6. **Connect encounter pane** to combat system
7. **Connect menu and logging** to GameEngine
8. **Update main.py** to use PyQt6
9. **Test with real character data**
10. **Add missing game features** (inventory management, equipment effects)

## Benefits of This Integration

- ✅ **Keeps existing game logic** - No need to rewrite GameEngine, models, services
- ✅ **Rich UI experience** - Professional PyQt6 interface with animations
- ✅ **Real-time data sync** - UI automatically updates with game state changes
- ✅ **Expandable panels** - Character sheet and equipment details on demand
- ✅ **Centralized data flow** - All widgets get data from single GameEngine source
- ✅ **Event-driven updates** - Combat, dice rolls, character changes propagate to UI

## File Structure After Integration

```
TaleKeeper/
├── main.py                     # Updated to use PyQt6
├── core/                       # Keep existing
│   ├── game_engine.py         # Enhanced with events
│   └── database.py            # Keep existing
├── models/                     # Enhanced with equipment
│   ├── character.py           # Add equipment relationships
│   ├── items.py               # New - item database
│   └── ...                    # Keep existing
├── ui/                         # Replace with PyQt6
│   ├── pyqt_main_window.py    # New - main PyQt6 window
│   ├── widget_manager.py      # New - data coordination
│   └── ...                    # Remove old Tkinter files
├── character_sheet/           # Keep - connect to Character
├── equipment_layout/          # Keep - connect to inventory
├── encounter_pane/            # Keep - connect to combat
├── menu/                      # Keep - connect to GameEngine
├── log/                       # Keep - connect to events
└── action_cards/              # Keep - connect to combat actions
```

This plan maintains all existing game functionality while providing a modern, expandable UI that integrates seamlessly with the existing architecture.