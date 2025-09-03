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
├── run_game.py          # Safe launcher with dependency checks
├── core/                # Core game systems (IndexedDB engine)
├── models/              # Dataclass models for IndexedDB
├── services/            # Business logic (dice, combat)
├── ui/                  # PyQt6 user interface
├── data/                # D&D 2024 game data (JSON)
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

## 📈 Version History

### v0.01 (Initial Release)
- Complete D&D 2024 character creation system
- Turn-based combat with initiative and actions
- Location-based exploration with random encounters
- Save/load system with multiple character slots
- Single-file Windows executable

## ToDo
- Check 2 weapon fighting, dueling,  
- Check nick, vex, sap,
- Advantage/Disadvantage
- level progression ( fighter, barbarian, rogue to 20 )
- towns for selling stuff
- items on monsters for use
- training costs
- images characters, monsters and items
- a way of parsing combat to a story
- ollama connectivity to local storytelling version
- skills
- skill encounters
- traps
- hazards
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
