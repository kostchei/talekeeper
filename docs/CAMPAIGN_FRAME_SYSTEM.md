# Campaign Frame System Documentation

## Overview

The Campaign Frame system in TaleKeeper provides a flexible framework for defining encounter generation parameters and campaign-specific rules. It controls monster distribution, difficulty curves, alignment restrictions, and other encounter mechanics to create consistent campaign experiences.

## Architecture

### Core Components

- **`CampaignFrame`** (`encounter_pane/campaign_frame.py`) - Data structure for campaign settings
- **`EncounterGenerator`** (`encounter_pane/encounter_generator.py`) - Encounter generation engine
- **Monster Database** - SQLite database with full monster statistics
- **RandomBag System** - Ensures encounter variety while respecting campaign rules

### Key Features

- Monster type distribution control
- Difficulty encounter probability curves
- Alignment-based monster filtering
- CR-based level scaling
- XP budget management
- Encounter variety through RandomBag mechanics

## CampaignFrame Structure

### Configuration Parameters

```python
{
    "name": "Campaign Name",
    "monster_type_weights": {
        "humanoid": 0.3,
        "beast": 0.2,
        "monstrosity": 0.2,
        "undead": 0.15,
        "fiend": 0.15
    },
    "difficulty_distribution": {
        "low": 0.4,
        "moderate": 0.5,
        "high": 0.1
    },
    "monster_alignment_rules": {
        "allow_evil": true,
        "allow_humanoid_not_good": true
    },
    "rest_rules": {
        "short_rest_frequency": 0.3,
        "long_rest_required": 8
    },
    "style": "classic",
    "available_classes": ["fighter", "rogue", "barbarian"],
    "guaranteed_hoards": false
}
```

### Parameter Details

#### Monster Type Weights
Controls the probability distribution of monster types in encounters:
- **Purpose**: Defines campaign themes (undead-heavy horror, beast-focused wilderness, etc.)
- **Format**: Dictionary mapping monster types to relative weights (0.0-1.0)
- **Behavior**: Higher weights increase probability of that type appearing
- **Supported Types**: humanoid, beast, monstrosity, undead, fiend, dragon, aberration, celestial, construct, elemental, fey, giant, ooze, plant

#### Difficulty Distribution
Sets the probability curve for encounter difficulty levels:
- **low**: Easy encounters (typically multiple weak monsters)
- **moderate**: Balanced encounters (mixed groups or moderate threats)
- **high**: Hard encounters (single strong monster or overwhelming numbers)

#### Monster Alignment Rules
Controls which monsters can appear based on alignment:
- **allow_evil**: If true, explicitly evil monsters can appear
- **allow_humanoid_not_good**: If true, non-good humanoids (bandits, cultists) can appear

#### Rest Rules (Future Implementation)
- **short_rest_frequency**: Probability of short rest opportunities
- **long_rest_required**: Hours required for long rest

## Encounter Generation System

### XP Budget System

The system uses D&D-standard XP budgets for each party level and difficulty:

```python
XP_BUDGETS = [
    {"Level": 1, "Low": 50, "Moderate": 75, "High": 100},
    {"Level": 2, "Low": 100, "Moderate": 150, "High": 200},
    {"Level": 3, "Low": 150, "Moderate": 225, "High": 400},
    {"Level": 4, "Low": 250, "Moderate": 375, "High": 500},
    {"Level": 5, "Low": 500, "Moderate": 750, "High": 1100},
    {"Level": 6, "Low": 600, "Moderate": 1000, "High": 1400},
    {"Level": 7, "Low": 750, "Moderate": 1300, "High": 1700},
    {"Level": 8, "Low": 900, "Moderate": 1600, "High": 2100},
    {"Level": 9, "Low": 1100, "Moderate": 1900, "High": 2600},
    {"Level": 10, "Low": 1300, "Moderate": 2300, "High": 3100},
    {"Level": 11, "Low": 1600, "Moderate": 2700, "High": 3700},
    {"Level": 12, "Low": 1900, "Moderate": 3200, "High": 4300},
    {"Level": 13, "Low": 2200, "Moderate": 3700, "High": 5000},
    {"Level": 14, "Low": 2600, "Moderate": 4300, "High": 5800},
    {"Level": 15, "Low": 3000, "Moderate": 5000, "High": 6700},
    {"Level": 16, "Low": 3500, "Moderate": 5800, "High": 7800},
    {"Level": 17, "Low": 4000, "Moderate": 6700, "High": 9000},
    {"Level": 18, "Low": 4700, "Moderate": 7800, "High": 10500},
    {"Level": 19, "Low": 5400, "Moderate": 9000, "High": 12100},
    {"Level": 20, "Low": 6300, "Moderate": 10500, "High": 14100}
]
```

### CR Scaling Rules

Monster selection follows challenge rating caps based on party level:
- **Levels 1-4**: CR cap = 0.25 × level
- **Levels 5+**: CR cap = 0.5 × level

### Encounter Structure Patterns

#### High Difficulty Encounters
- **Pattern**: Single strong monster approach
- **Selection**: Monster XP ≥ 80% of total budget
- **Rationale**: Boss-style encounters with individual threats

#### Low/Moderate Difficulty Encounters
- **Pattern**: Multiple monster groups
- **Constraints**: Maximum 4 monsters, total XP ≤ budget
- **Building**: Iterative addition until budget constraint reached

### RandomBag Mechanics

The RandomBag system ensures encounter variety:

```python
class RandomBag:
    def __init__(self, items: List[Any]):
        self.original = items[:]
        self.pool = items[:]

    def draw(self):
        if not self.pool:
            self.pool = self.original[:]  # Refill when empty
        item = random.choice(self.pool)
        self.pool.remove(item)  # Remove to prevent immediate repeats
        return item
```

**Benefits:**
- Prevents immediate monster repetition
- Ensures all qualified monsters appear eventually
- Maintains randomness while improving variety

## Current Implementation Issues

### Critical Problems Identified

1. ✅ **XP Budget Table** - FIXED
   - ✅ Extended XP_BUDGETS to cover levels 1-20
   - ✅ No more "Unknown level" errors for high-level characters

2. **Alignment Filtering Logic** - NOT USED
   - Campaign uses either all monsters or evil-only filtering
   - Good-only campaigns not currently needed

3. **Non-Functional Monster Type Weights** - INVESTIGATION NEEDED
   - Type weights are defined but may not be used in monster selection
   - All monsters may have equal probability regardless of type weights
   - **Current Code**: `RandomBag(allowed if allowed else [m for m in MONSTER_DB if m["cr"] <= cr_cap])`
   - **Missing**: Type-weighted selection during bag creation

4. ✅ **Difficulty Distribution** - FIXED
   - ✅ Updated to proper 40% low, 50% moderate, 10% high distribution
   - ✅ Campaign frame JSON files updated with correct probabilities

### Alignment Logic Fix Needed

Current broken logic:
```python
# BROKEN: Only adds monsters for special cases
if self.frame.monster_alignment_rules.get("allow_evil", False):
    if "E" in alignment:
        allowed.append(m)
        continue

if self.frame.monster_alignment_rules.get("allow_humanoid_not_good", False):
    if m["type"] == "humanoid" and "G" not in alignment:
        allowed.append(m)
        continue
```

Should be:
```python
# Check if monster should be excluded based on alignment rules
exclude_monster = False

# If evil not allowed, exclude evil monsters
if not self.frame.monster_alignment_rules.get("allow_evil", False):
    if "E" in alignment:
        exclude_monster = True

# If non-good humanoids not allowed, exclude them
if not self.frame.monster_alignment_rules.get("allow_humanoid_not_good", False):
    if m["type"] == "humanoid" and "G" not in alignment:
        exclude_monster = True

if not exclude_monster:
    allowed.append(m)
```

## Testing and Validation

### Test Coverage

The test suite (`test/test_monster_distribution.py`) validates:

- **Monster database loading** and structure
- **XP budget calculations** for all difficulty levels
- **CR filtering** based on party level caps
- **Alignment filtering** according to campaign rules
- **Difficulty distribution** probabilities
- **Encounter structure patterns** (single vs. multiple monsters)
- **Monster type distribution** according to weights
- **RandomBag variety mechanics**
- **Campaign simulation** over multiple levels

### Test Results Summary

**✅ Working Correctly:**
- Monster database loading (451 monsters)
- Basic encounter generation structure
- XP calculation accuracy
- RandomBag variety system
- Campaign frame serialization

**❌ Currently Broken:**
- XP budgets beyond level 7
- Alignment filtering logic
- Monster type weight application
- Difficulty distribution probability matching
- CR filtering for levels 8+

## Usage Examples

### Creating Campaign Frames

#### Classic Balanced Campaign
```python
balanced_campaign = CampaignFrame({
    'monster_type_weights': {
        'humanoid': 0.25,
        'beast': 0.20,
        'monstrosity': 0.15,
        'undead': 0.15,
        'fiend': 0.10,
        'dragon': 0.05,
        'aberration': 0.10
    },
    'difficulty_distribution': {
        'low': 0.25,
        'moderate': 0.50,
        'high': 0.25
    },
    'monster_alignment_rules': {
        'allow_evil': True,
        'allow_humanoid_not_good': True
    }
})
```

#### Good-Aligned Campaign
```python
heroic_campaign = CampaignFrame({
    'monster_type_weights': {
        'beast': 0.40,
        'monstrosity': 0.30,
        'humanoid': 0.20,
        'construct': 0.10
    },
    'difficulty_distribution': {
        'low': 0.40,
        'moderate': 0.50,
        'high': 0.10
    },
    'monster_alignment_rules': {
        'allow_evil': False,
        'allow_humanoid_not_good': False
    }
})
```

#### Horror Campaign
```python
horror_campaign = CampaignFrame({
    'monster_type_weights': {
        'undead': 0.40,
        'aberration': 0.25,
        'fiend': 0.20,
        'monstrosity': 0.15
    },
    'difficulty_distribution': {
        'low': 0.10,
        'moderate': 0.30,
        'high': 0.60
    },
    'monster_alignment_rules': {
        'allow_evil': True,
        'allow_humanoid_not_good': True
    }
})
```

### Generating Encounters

```python
# Create generator with campaign frame
generator = EncounterGenerator(campaign_frame)

# Generate encounter for level 5 party
encounter = generator.generate_encounter(5)

# Encounter structure:
{
    "level": 5,
    "difficulty": "moderate",
    "monsters": [
        {
            "name": "Orc",
            "cr": 1,
            "xp": 200,
            "type": "humanoid",
            "alignment": "C, E",
            "average_hp": 15,
            "hp_formula": "2d8 + 6"
        }
    ],
    "total_xp": 200
}
```

## Database Schema

### Monster Table Structure

```sql
CREATE TABLE monsters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    subtype TEXT,
    size TEXT,
    alignment TEXT,
    armor_class INTEGER,
    hit_points INTEGER,
    speed TEXT,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    challenge_rating TEXT,
    experience_points INTEGER,
    proficiency_bonus INTEGER,
    saving_throws TEXT,
    skills TEXT,
    damage_resistances TEXT,
    damage_immunities TEXT,
    condition_immunities TEXT,
    senses TEXT,
    languages TEXT,
    special_abilities TEXT,
    actions TEXT,
    legendary_actions TEXT,
    reactions TEXT,
    environment TEXT
);
```

### Monster Data Loading

The `load_monsters()` function processes database data into encounter-ready format:

```python
def load_monsters():
    # Connects to talekeeper.db
    # Parses complex CR data (handles JSON/dict formats)
    # Converts CR to numeric values for comparison
    # Maps CR to XP values using CR_TO_XP table
    # Returns normalized monster list for encounter generation
```

## Integration Points

### UI Integration
- **Encounter Pane** (`encounter_pane/encounter_panel.py`) - Displays generated encounters
- **Campaign Selection** - Future UI for campaign frame selection
- **Encounter History** - Tracks generated encounters per campaign

### Game Engine Integration
- **Combat System** - Receives monsters from encounter generator
- **XP Awards** - Uses encounter XP for character progression
- **Save System** - Persists active campaign frame in character data

## Future Enhancements

### Planned Features

1. **Extended XP Budget Table**
   - Complete level 1-20 XP budgets
   - Epic level support (21-30)

2. **Monster Type Weight Implementation**
   - Weighted random selection based on type preferences
   - Dynamic type availability based on environment

3. **Environment-Based Encounters**
   - Location-specific monster filtering
   - Terrain-appropriate encounters

4. **Campaign Templates**
   - Pre-built campaign frames for common themes
   - Template inheritance and customization

5. **Dynamic Difficulty Scaling**
   - Adaptive encounter difficulty based on party performance
   - Encounter history influence on future generation

6. **Rest Integration**
   - Short/long rest frequency control
   - Resource depletion encounters

### Technical Improvements

1. **Performance Optimization**
   - Cache filtered monster lists per level
   - Lazy loading of monster database

2. **Validation System**
   - Campaign frame validation rules
   - Encounter generation error handling

3. **Testing Expansion**
   - Performance benchmarks
   - Statistical distribution validation
   - Edge case coverage

## Development Commands

### Running Tests
```bash
# Run comprehensive monster distribution tests
python test/test_monster_distribution.py

# Run specific test class
python -m pytest test/test_monster_distribution.py::TestMonsterDistribution -v

# Run with coverage
python -m pytest test/test_monster_distribution.py --cov=encounter_pane
```

### Database Operations
```bash
# Check monster count
sqlite3 talekeeper.db "SELECT COUNT(*) FROM monsters;"

# View monster types
sqlite3 talekeeper.db "SELECT DISTINCT type FROM monsters ORDER BY type;"

# Check alignment distribution
sqlite3 talekeeper.db "SELECT alignment, COUNT(*) FROM monsters GROUP BY alignment ORDER BY COUNT(*) DESC;"
```

### Development Validation
```bash
# Validate campaign frame serialization
python -c "
from encounter_pane.campaign_frame import CampaignFrame
frame = CampaignFrame({'name': 'test'})
print(frame.to_dict())
"

# Test encounter generation
python -c "
from encounter_pane.encounter_generator import EncounterGenerator
from encounter_pane.campaign_frame import CampaignFrame
frame = CampaignFrame({'difficulty_distribution': {'low': 0.3, 'moderate': 0.5, 'high': 0.2}})
gen = EncounterGenerator(frame)
print(gen.generate_encounter(3))
"
```

## Conclusion

The Campaign Frame system provides a powerful foundation for customizable encounter generation in TaleKeeper. While the current implementation has several critical issues that need resolution, the architecture is sound and extensible.

The test suite reveals both the system's capabilities and its current limitations, providing a clear roadmap for fixes and improvements. Once the core issues are resolved, the system will enable rich, varied campaign experiences tailored to specific themes and play styles.

For immediate development priorities:
1. Fix XP budget table completeness
2. Repair alignment filtering logic
3. Implement monster type weight application
4. Validate difficulty distribution mechanics

The system's modular design allows for incremental improvements while maintaining backwards compatibility with existing campaign data.