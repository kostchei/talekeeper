# TaleKeeper Desktop

A single-player D&D 2024 tactical RPG for Windows. Experience classic tabletop RPG gameplay with turn-based combat, character progression, and exploration - all offline on your desktop.

## 🎲 Features

### Character System
- **Full D&D 2024 Rules** - Accurate ability scores, modifiers, and mechanics
- **Complete Character Creation** - Race, class, background, and ability score generation
- **Multiple Save Slots** - Up to 10 character saves with metadata
- **Character Progression** - Experience points and level advancement

### Gameplay
- **Turn-Based Combat** - Initiative-based tactical combat with D&D mechanics  
- **Exploration System** - Location-based adventure with random encounters
- **Rest Mechanics** - Short and long rest with resource recovery
- **Monster AI** - Intelligent enemy behavior patterns

### Content
- **Races**: Human, Dwarf with racial traits
- **Classes**: Fighter, Rogue with subclasses (Champion, Battle Master, Thief, Assassin)
- **Monsters**: Goblins, Orcs, Wolves, Skeletons with full stat blocks
- **Equipment**: Weapons, armor, and gear with D&D properties

```

## 🚀 Quick Start

### From Source
```bash
# Clone the repository
git clone https://github.com/kostchei/talekeeper
cd talekeeper

# Install dependencies
pip install -r requirements.txt

# Run the game (database auto-initializes on first run)
python main.py

# Optional: Run with dev mode for test data
python main.py --dev
```

### Database Management
```bash
# Initialize/reset database
python database/database_init.py --force

# Run with development data
python database/database_init.py --dev

# Verify database integrity
python database/database_init.py --verify
```

## 🎮 How to Play

1. **Character Creation**: Choose race, class, background, and generate ability scores
2. **Exploration**: Navigate different locations and choose actions
3. **Encounters**: Face monsters in tactical turn-based combat
4. **Progression**: Gain XP, level up, and grow stronger
5. **Save/Load**: Manage multiple character saves

## 🏗️ Development

### Requirements
- Python 3.11+
- Windows 10/11 (for executable builds)

### Project Structure
```
TaleKeeper/
├── main.py              # Application entry point
├── talekeeper.db        # SQLite database (auto-created)
├── database/            # Database management
│   ├── schema/          # Database schema files
│   ├── seeds/           # Game data (classes, races, items)
│   └── migrations/      # Database updates
├── core/                # Core game systems
├── services/            # Business logic (dice, combat)
├── ui/                  # PyQt6 user interface
├── data/                # Legacy game data (JSON)
├── assets/              # Fonts and images
├── config/              # Settings and configuration
├── log/                 # Logging panel component
├── character_sheet/     # Character sheet UI component
├── encounter_pane/      # Encounter UI component
├── equipment_layout/    # Equipment UI component
├── action_cards/        # Action cards UI component
├── menu/                # Game menu component
└── archive/             # Archived legacy files
```

### Key Technologies
- **Python + PyQt6** - Desktop GUI framework
- **IndexedDB Simulation** - Local data persistence with JSON
- **PyInstaller** - Executable packaging

### Building Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the game (recommended launcher)
python run_game.py

# Or run directly
python main.py

# Build executable
pyinstaller build.spec

# Or use the batch script (Windows)
build.bat
```

## 📋 System Requirements

### For Executable
- Windows 10/11 (64-bit)
- No additional software required

### For Development
- Python 3.11+
- Windows 10/11 recommended for building executables

## 🔧 Configuration

The game creates configuration files automatically:
- `talekeeper.idb` - IndexedDB JSON file with all game data
- `config/settings.json` - Game settings
- `talekeeper.log` - Application logs

## ⚠️ Important Development Notes

### HP Tracking During Combat
**CRITICAL**: Combat HP is tracked in the character sheet UI, NOT in the database during active combat.

When implementing any healing ability (Second Wind, potions, spells, etc.):
1. **Get HP from**: `parent.character_sheet.character_data`
2. **Apply healing to**: The same character_data object
3. **Update display**: Call `parent.character_sheet.load_character_data()`
4. **NEVER**: Read HP from database or character_context during combat (will be stale)

See `action_cards/action_panel.py` methods `_apply_damage_to_player()` and Second Wind implementation for the correct pattern.

## 📈 Version History

### v0.01 (Initial Release)
- Complete D&D 2024 character creation system
- Turn-based combat with initiative and actions
- Location-based exploration with random encounters
- Save/load system with multiple character slots
- Single-file Windows executable

## ToDo
-Record all actions taken to a file for future reference 
Create a “ all monsters randomly “ dnd baseline
List all fighter abilities for each level in a doc.
Plan out how to create those mechanically in a doc.
Implement that plan.
Record the issues.
List all barbarian abilities for each level in a doc.
Look at the fighter doc
 Learn from what broke and why
Plan out how to create the barbarian abilities based on the prior knowledge 
Implement that plan.
Record the issues….
 
    ....Check 2 weapon fighting,  
- level progression ( fighter, barbarian, rogue to 20 )
- fighter, check each level for champion, make sure it all works..
- towns for selling stuff
- items on monsters for use
- images characters, monsters and items
- a way of parsing combat to a story
- skills
- encounters- towns/shops
- skill encounters
- traps
- hazards
- quest givers
- ollama connectivity to local storytelling version
- barbarian (berserker, slayer), rogue ( theif,  trader), fighter (champion, gladiator) and many subclasses but no spell casting
stealth
encounter parlay
encounter avoidance
pickpockets
multiclassing
city adventure
dungeon adventure
...
range attacks, movement..something
poisons
Release 1
campaign frame interface
modules
mounts?
