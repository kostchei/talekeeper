# Hex Map Exploration System

## Overview
A standalone hex-based wilderness exploration system for TaleKeeper. Each character has their own unique exploration experience with hexes generated on-demand as they travel. The system tracks combat, loot, and narrative events for each hex, creating a visual journey log.

## Features Implemented

### 1. Core Systems
- **Axial Coordinate System**: Industry-standard hexagonal grid mathematics
- **Just-in-Time Generation**: Hexes only generate when adjacent to player
- **Per-Character Maps**: Each character has unique exploration data
- **Event Logging**: Complete history of combat, loot, and discoveries
- **Skill-Based Scouting**: Automatic skill checks reveal hex information

### 2. UI Integration
- **'M' Key**: Opens/closes hex map overlay
- **Visual Map**: PyQt6-based hex grid display
- **Click to Travel**: Select adjacent hexes to move
- **Info Panel**: Shows hex details with skill-based information
- **Statistics**: Track exploration progress

### 3. Skill System Integration
Uses the same skill-based knowledge system as encounter tooltips ([monster_knowledge.py](../src/talekeeper/services/monster_knowledge.py)):

**Scouting Skills:**
- **Nature**: Identify terrain features, flora/fauna, natural hazards
- **Survival**: Assess travel difficulty, find shelter, track creatures
- **Perception**: Spot encounters before entering hex
- **Arcana**: Identify magical creatures and phenomena
- **Religion**: Detect undead and unholy influences
- **History**: Recognize civilizations, giants, dragons

**Information Revealed:**
- **DC 10-15**: Basic terrain type and movement difficulty
- **DC 12-18**: Encounter detection (monster name + CR, vendor, or hazard)
- **DC 15+**: Detailed terrain features (resources, shelter, dangers)
- **DC 18+**: Specific encounter details

### 3. Database Schema
```sql
character_hex_map           # Per-character hex tiles
character_hex_position      # Current player position
hex_events                  # Event history
hex_combat_log              # Combat details
hex_loot_log                # Items found
hex_narrative_log           # Story events
```

## Architecture

### Files Created
```
src/talekeeper/
├── services/
│   ├── hex_coordinate_system.py    # Hex math & neighbors
│   ├── hex_map_service.py          # Core generation & state
│   ├── hex_event_logger.py         # Event tracking
│   └── hex_scouting_service.py     # Skill-based hex scouting
└── ui/
    └── hex_map/
        ├── __init__.py
        └── hex_map_widget.py       # Main map UI

database/
└── migrations/
    └── 010_hex_map_system.sql      # Database tables
```

### Integration Points
- [main_window.py:25](src/talekeeper/ui/main_window.py#L25) - Import HexMapWidget
- [main_window.py:58](src/talekeeper/ui/main_window.py#L58) - Lazy hex map initialization
- [main_window.py:1839-1874](src/talekeeper/ui/main_window.py#L1839-L1874) - Keyboard handling & toggle methods

## Usage

### For Players
1. **Open Map**: Press `M` key (requires loaded character)
2. **Travel**: Click adjacent hex to move
3. **View History**: Click any visited hex to see events
4. **Close Map**: Press `M` or `ESC`

### For Developers

#### Generate Hexes Manually
```python
from talekeeper.services.hex_map_service import HexMapService

hex_service = HexMapService('talekeeper.db')
hex_service.initialize_character_position(character_id)

# Travel to a hex
hex_data = hex_service.travel_to_hex(character_id, 1, 0)
print(f"Terrain: {hex_data['biome']}")
```

#### Log Events
```python
from talekeeper.services.hex_event_logger import HexEventLogger

logger = HexEventLogger('talekeeper.db')

# Log combat
combat_result = {
    'won': True,
    'rounds': 5,
    'character_level': 5,
    'damage_dealt': 42,
    'damage_taken': 18,
    'enemies': [
        {'name': 'Goblin', 'cr': 1, 'quantity': 3, 'killed': 3}
    ],
    'loot': [
        {'name': 'Gold', 'type': 'currency', 'quantity': 50, 'value': 50}
    ]
}

event_id = logger.log_combat_event(character_id, q, r, combat_result)
```

#### Retrieve Hex History
```python
# Get all events for a specific hex
events = logger.get_hex_events(character_id, q, r)
for event in events:
    print(f"{event['event_type']}: {event['narrative']}")
```

## Hex Generation

### Terrain Types
- `plains` - Open grasslands (30% encounter rate)
- `forest` - Dense woods (50% encounter rate)
- `mountain` - Rocky peaks (40% encounter rate)
- `hills` - Rolling terrain (35% encounter rate)
- `swamp` - Wetlands (60% encounter rate)
- `desert` - Arid wastes (20% encounter rate)

### Visibility States
1. **Ungenerated** (dark gray): Doesn't exist yet
2. **Generated but Hidden** (dimmed): Exists but not revealed
3. **Revealed** (normal): Player can see terrain
4. **Visited** (bright): Player has been there

### Coordinate System
- Axial coordinates (q, r)
- Player starts at (0, 0)
- 6 directions: E, NE, NW, W, SW, SE
- Distance formula: `(|q1-q2| + |q1+r1-q2-r2| + |r1-r2|) / 2`

## Future Enhancements

### Planned Features (Not Yet Implemented)
1. **Encounter System Integration**
   - Trigger existing encounter UI from hex travel
   - Pass monster data from hex to combat
   - Update hex as "cleared" after combat victory

2. **Perception-Based Scouting**
   - Skill checks to reveal encounter details before entering
   - Survival checks for terrain info
   - Surprise encounters vs. revealed encounters

3. **Resource Management**
   - Travel time (2-3 hours per hex)
   - Food/water consumption
   - Rest/camping mechanics
   - Day/night cycle

4. **Enhanced Terrain**
   - Difficult terrain (movement penalties)
   - Natural hazards
   - Weather effects
   - Landmarks and points of interest

5. **Quest Integration**
   - Quest objectives reveal distant hexes
   - Marked waypoints
   - Story-specific encounters

6. **Visual Improvements**
   - Hex icons (combat, loot, landmarks)
   - Path highlighting
   - Zoom levels (tactical, regional, strategic)
   - Minimap during normal play

## Testing

### Running Tests
```bash
# Core functionality test
python test_hex_map.py

# Expected output:
# - Coordinate system working
# - Hex generation successful
# - Travel mechanics functional
# - Event logging operational
# - All tests passed!
```

### Test Coverage
- Hex coordinate mathematics
- Hex generation (deterministic seeds)
- Character position tracking
- Travel validation (adjacent only)
- Event logging (travel, combat, resources)
- Database persistence
- Multi-hex visibility

## Design Decisions

### Why Per-Character Maps?
- Each player's exploration is unique
- Allows different play styles (cautious vs. aggressive)
- Prevents shared "fog of war" exploits
- Enables solo-focused design

### Why Just-in-Time Generation?
- Scales infinitely (no pre-gen limits)
- Deterministic (same coords = same terrain)
- Memory efficient
- Player-paced discovery

### Why Standalone System?
- No impact on existing combat/encounter code
- Can be enabled/disabled independently
- Easier to test and debug
- Modular architecture for future expansion

### Why Axial Coordinates?
- Industry standard for hex grids
- Simple neighbor calculations
- Easy distance formulas
- Natural for flat-top orientation

## Database Migration

The hex map system uses migration `010_hex_map_system.sql`. It runs automatically on application startup via the existing migration system.

### Manual Migration
```bash
sqlite3 talekeeper.db < database/migrations/010_hex_map_system.sql
```

### Tables Created
- `character_hex_map` (per-character tiles)
- `character_hex_position` (current position)
- `hex_events` (event history)
- `hex_combat_log` (combat details)
- `hex_loot_log` (items found)
- `hex_narrative_log` (story text)

## Integration with Existing Systems

### Current State
- **Standalone**: Does not modify existing systems
- **Independent**: Own database tables
- **Parallel**: Can generate encounters OR use map
- **Safe**: Fully isolated testing

### Future Integration Points
1. **Encounter System** - Hex encounters trigger `encounter_pane`
2. **Combat Manager** - Results logged back to hex
3. **Action Economy** - Travel costs time
4. **Rest System** - Camping in hexes
5. **Quest System** - Objectives reveal hexes

## Performance Notes

### Optimizations
- Lazy hex generation (only when needed)
- Connection pooling for database
- Efficient neighbor queries
- Deterministic seeds (no duplicate generation)

### Scalability
- Tested with 100+ hexes per character
- Each character's map is independent
- No cross-character queries
- Minimal memory footprint

## Encounter Generation

The hex map uses TaleKeeper's standard random encounter system, accessed through hexes rather than direct generation:

**Integration Pattern:**
1. Player clicks adjacent hex to scout
2. Skill checks run automatically (Nature, Survival, Perception)
3. If encounter present: Shows "Monster Name (CR X)" or "Vendor" or "Possible hazard"
4. Player clicks again to travel
5. Standard encounter system triggers (if combat/vendor/hazard present)
6. Results logged back to hex event history

**Encounter Types:**
- **Combat**: Uses existing monster tables and CR scaling
- **Vendor**: Traveling merchant encounters
- **Hazard**: Natural dangers (traps, environmental)
- **Landmark**: Points of interest
- **Empty**: Safe travel

**Skill Check Reference:**
Based on [monster_knowledge.py](../src/talekeeper/services/monster_knowledge.py) system:
- Same DC calculations (DC = 10 + CR for monsters)
- Same skill-to-monster-type mappings
- Same information reveal tiers
- Integrated with character proficiencies

## Known Limitations

1. **No Encounter Triggering Yet**: Skill checks show info but don't trigger combat UI
2. **No Time Tracking**: Travel is instant
3. **Basic UI**: No icons, zoom, or minimap yet
4. **No Quest Integration**: Manual reveal only

## Next Steps for Integration

To connect hex map with existing encounter system:

1. **In `hex_map_widget.py`**:
   - Emit signal when player enters hex with encounter
   - Pass monster data to main window

2. **In `main_window.py`**:
   - Connect hex travel signal to encounter generation
   - Pass hex encounter to `encounter_pane.add_encounter()`

3. **In `hex_map_service.py`**:
   - Add encounter generation logic
   - Use existing monster CR tables
   - Scale difficulty by distance from origin

4. **In `hex_event_logger.py`**:
   - Connect to combat completion signals
   - Auto-log combat results from encounter pane

## References

- [Hex Coordinate Systems](https://www.redblobgames.com/grids/hexagons/)
- [PyQt6 Graphics View Framework](https://doc.qt.io/qt-6/graphicsview.html)
- D&D 2024 Exploration rules (Player's Handbook Chapter 7)
