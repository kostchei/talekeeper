# Paladin Implementation Plan - D&D 2024

## Current Status Assessment

The paladin class has a **partial implementation** in TaleKeeper with significant gaps in core features, UI integration, and database support.

### ✅ Currently Implemented
- Basic paladin class definition in database (`classes` table)
- `PaladinAbilitiesService` with Divine Smite calculation logic
- Divine Smite UI dialog (`divine_smite_dialog.py`)
- Devotion oath subclass framework via enhanced subclass system
- Basic spellcasting integration through `SpellcastingService`
- Some oath spell handling
- Divine Smite spell integration

### ❌ Missing Critical Features
- **No UI action cards** for Lay on Hands, Channel Divinity, or aura abilities
- **No backend database tables** for paladin-specific features (lay_on_hands pool, channel_divinity uses)
- **No aura mechanics implementation** (Protection, Courage, Devotion)
- **Incomplete spell system** - missing prepared spell management
- **No Faithful Steed implementation**
- **Missing higher-level features** (Radiant Strikes, Restoring Touch, Aura Expansion)

## D&D 2024 Paladin Feature Reference

### Core Class Features by Level

| Level | Feature | Action Type | Resources | Current Status |
|-------|---------|-------------|-----------|----------------|
| 1 | Lay on Hands | Bonus Action | 5×level HP pool | ❌ **Missing UI/DB** |
| 1 | Spellcasting | - | Spell slots (Level 2+) | ⚠️ **Partial** |
| 1 | Weapon Mastery | - | - | ❌ **Missing** |
| 2 | Fighting Style | - | - | ❌ **Missing** |
| 2 | Paladin's Smite | - | 1/Long Rest free Divine Smite | ⚠️ **Partial** |
| 3 | Channel Divinity | Action/Bonus | 2 uses/short rest | ❌ **Missing UI** |
| 3 | Sacred Oath | - | Subclass features | ⚠️ **Partial** |
| 5 | Extra Attack | - | - | ❌ **Missing** |
| 5 | Faithful Steed | - | Find Steed always prepared | ❌ **Missing** |
| 6 | Aura of Protection | Passive | 10ft radius | ❌ **Missing** |
| 9 | Abjure Foes | Magic Action | Channel Divinity | ❌ **Missing** |
| 10 | Aura of Courage | Passive | Fear immunity in aura | ❌ **Missing** |
| 11 | Radiant Strikes | Passive | +1d8 radiant on attacks | ❌ **Missing** |
| 14 | Restoring Touch | - | Enhanced Lay on Hands | ❌ **Missing** |
| 18 | Aura Expansion | Passive | Auras become 30ft | ❌ **Missing** |

### Oath of Devotion Features

| Level | Feature | Action Type | Resources | Current Status |
|-------|---------|-------------|-----------|----------------|
| 3 | Sacred Weapon | Attack action | Channel Divinity | ⚠️ **Framework only** |
| 3 | Turn the Unholy | Action | Channel Divinity | ⚠️ **Framework only** |
| 7 | Aura of Devotion | Passive | Charm immunity in aura | ❌ **Missing** |
| 15 | Smite of Protection | Passive | Half cover after Divine Smite | ❌ **Missing** |
| 20 | Holy Nimbus | Bonus Action | 1/Long Rest transformation | ⚠️ **Framework only** |

### Spellcasting Details
- **Half-caster**: Spell slots start at level 2
- **Charisma-based**: Spell save DC = 8 + prof + Cha mod
- **Prepared spells**: Cha mod + half paladin level (minimum 1)
- **Oath spells**: Always prepared, don't count against limit
- **Focus**: Holy symbol

## Implementation Priority Plan

### Phase 1: Core Foundation (HIGH PRIORITY)
**Goal**: Make paladins fully playable with essential features

#### 1.1 Database Schema Updates
```sql
-- Create paladin-specific features table
CREATE TABLE IF NOT EXISTS paladin_features (
    character_id TEXT PRIMARY KEY,
    level INTEGER NOT NULL,
    sacred_oath TEXT NOT NULL DEFAULT 'devotion',
    lay_on_hands_pool_current INTEGER NOT NULL DEFAULT 0,
    lay_on_hands_pool_max INTEGER NOT NULL DEFAULT 0,
    channel_divinity_uses_current INTEGER NOT NULL DEFAULT 0,
    channel_divinity_uses_max INTEGER NOT NULL DEFAULT 0,
    channel_divinity_last_reset TEXT,
    spells_prepared INTEGER NOT NULL DEFAULT 0,
    max_spells_prepared INTEGER NOT NULL DEFAULT 1,
    faithful_steed_summoned BOOLEAN DEFAULT FALSE,
    radiant_strikes_active BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Add paladin-specific resource tracking
CREATE TABLE IF NOT EXISTS paladin_resources (
    character_id TEXT PRIMARY KEY,
    free_divine_smite_used BOOLEAN DEFAULT FALSE,
    last_long_rest TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

#### 1.2 Action Cards Implementation
**Files to create/modify:**
- `action_cards/lay_on_hands_dialog.py` - NEW: Healing point selection UI
- `action_cards/channel_divinity_dialog.py` - NEW: Channel Divinity options UI
- `action_cards/action_panel.py` - MODIFY: Add paladin action card generation

```python
# lay_on_hands_dialog.py structure
class LayOnHandsDialog(QDialog):
    def __init__(self, character_data, max_pool, current_pool):
        # UI for selecting healing amount (1-5 points)
        # Option to cure poison (5 points)
        # Show remaining pool

# channel_divinity_dialog.py structure
class ChannelDivinityDialog(QDialog):
    def __init__(self, character_data, available_options):
        # List available Channel Divinity options
        # Divine Sense (all paladins)
        # Oath-specific options (Sacred Weapon, Turn Unholy, etc.)
```

#### 1.3 Backend Service Expansion
**Files to modify:**
- `services/paladin_abilities.py` - EXPAND: Add missing methods
- `core/game_engine_sqlite.py` - MODIFY: Integrate paladin resource management

```python
# New methods needed in PaladinAbilitiesService:
def create_lay_on_hands_action_card(character_id: str) -> dict
def create_channel_divinity_action_cards(character_id: str) -> list
def apply_lay_on_hands_healing(character_id: str, target_id: str, points: int) -> dict
def use_channel_divinity_divine_sense(character_id: str) -> dict
def get_aura_effects(character_id: str) -> dict
```

### Phase 2: Aura System (MEDIUM PRIORITY)
**Goal**: Implement passive aura effects that benefit party members

#### 2.1 Aura Framework
**Files to create:**
- `services/aura_manager.py` - NEW: Central aura effect system
- `core/aura_effects.py` - NEW: Aura calculation and application

```python
# Aura types to implement:
class AuraType:
    PROTECTION = "protection"      # +Cha mod to saves
    COURAGE = "courage"            # Fear immunity
    DEVOTION = "devotion"          # Charm immunity

class AuraManager:
    def calculate_aura_range(paladin_level: int) -> int:
        return 30 if paladin_level >= 18 else 10

    def get_active_auras(character_id: str) -> list:
        # Return all auras affecting a character

    def apply_aura_bonus(character_id: str, save_type: str) -> int:
        # Calculate bonus from Aura of Protection
```

#### 2.2 Combat Integration
**Files to modify:**
- `core/combat_engine.py` - MODIFY: Apply aura effects to saves and conditions
- `encounter_pane/encounter_panel.py` - MODIFY: Show aura effects in UI

### Phase 3: Advanced Features (LOW PRIORITY)
**Goal**: Complete high-level paladin features

#### 3.1 Faithful Steed System
- Integration with existing spell system
- Find Steed always prepared
- Free casting 1/long rest

#### 3.2 Radiant Strikes & Restoring Touch
- Automatic +1d8 radiant damage on melee hits (level 11+)
- Enhanced Lay on Hands condition removal (level 14+)

#### 3.3 Epic Level Features
- Aura expansion to 30ft (level 18)
- Holy Nimbus transformation (level 20 for Devotion)

### Phase 4: Oath Expansion (FUTURE)
**Goal**: Add additional Sacred Oaths

#### 4.1 Additional Oaths
- Oath of the Ancients (nature-focused)
- Oath of Vengeance (damage-focused)
- Oath of Redemption (protection-focused)
- Oath of Glory (performance-focused)

Each oath requires:
- Oath spell lists
- Unique Channel Divinity options
- Oath-specific aura effects
- Capstone transformation abilities

## Technical Implementation Details

### Database Integration Points
```python
# Character creation flow updates needed:
# 1. Initialize paladin_features table when creating paladin
# 2. Calculate initial Lay on Hands pool (5 × level)
# 3. Set Channel Divinity uses based on level
# 4. Add oath spells to character_spells as always_prepared=TRUE

# Level up integration:
# 1. Update Lay on Hands pool maximum
# 2. Increase Channel Divinity uses at levels 7, 15
# 3. Add new oath spells when reaching thresholds
# 4. Grant new class features
```

### UI Integration Requirements
```python
# Action panel updates:
# 1. Generate Lay on Hands card when pool > 0
# 2. Generate Channel Divinity cards when uses available
# 3. Show aura status indicators
# 4. Display spell slots and prepared spells

# Character sheet updates:
# 1. Show Lay on Hands pool (current/max)
# 2. Display Channel Divinity uses
# 3. List active auras and their effects
# 4. Show oath-specific features
```

### Combat System Integration
```python
# Auto-applied effects:
# 1. Aura of Protection: +Cha mod to all saves for allies in range
# 2. Aura of Courage: Fear immunity for allies in range
# 3. Radiant Strikes: +1d8 radiant damage on melee attacks (level 11+)

# Manual abilities:
# 1. Divine Smite: Bonus radiant damage using spell slots
# 2. Lay on Hands: Bonus action healing
# 3. Channel Divinity: Various oath-specific effects
```

## Testing Strategy

### Unit Tests Required
- `test/services/test_paladin_abilities.py` - Core functionality
- `test/features/test_paladin_auras.py` - Aura mechanics
- `test/ui/test_paladin_action_cards.py` - UI components

### Integration Tests Required
- `test/integration/test_paladin_level_progression.py` - Level 1-20 validation
- `test/integration/test_paladin_spellcasting.py` - Spell slot and preparation
- `test/integration/test_paladin_combat.py` - Combat ability usage

### Manual Testing Scenarios
1. **Character Creation**: Create level 1 paladin, verify Lay on Hands pool
2. **Level 2**: Gain spellcasting, verify Divine Smite availability
3. **Level 3**: Choose oath, verify Channel Divinity options and oath spells
4. **Level 6**: Verify Aura of Protection affects party members
5. **Combat**: Use all paladin abilities in encounter

## File Structure Summary

### New Files to Create
```
services/aura_manager.py                    # Central aura system
core/aura_effects.py                        # Aura calculations
action_cards/lay_on_hands_dialog.py         # Healing UI
action_cards/channel_divinity_dialog.py     # Channel Divinity UI
test/services/test_paladin_abilities.py     # Unit tests
test/features/test_paladin_auras.py         # Aura tests
database/migrations/020_paladin_features.sql # Database schema
```

### Files to Modify
```
services/paladin_abilities.py               # Expand functionality
action_cards/action_panel.py                # Add paladin cards
core/game_engine_sqlite.py                  # Resource management
core/combat_engine.py                       # Aura integration
character_sheet/character_panel.py          # Display paladin resources
encounter_pane/encounter_panel.py           # Show aura effects
```

## Success Criteria

### Phase 1 Complete When:
- ✅ Paladins can use Lay on Hands with proper resource tracking
- ✅ Channel Divinity options appear as action cards
- ✅ Divine Smite integrates with spell slot system
- ✅ Basic oath features function (Sacred Weapon, Turn Unholy)

### Full Implementation Complete When:
- ✅ All auras properly affect party members in combat
- ✅ Faithful Steed spell integration works
- ✅ Radiant Strikes automatically applies to attacks
- ✅ All Devotion oath features implemented
- ✅ Level 1-20 progression fully tested
- ✅ Multiclass paladin integration works correctly

This implementation plan provides a systematic approach to completing the paladin class with proper database support, UI integration, and mechanical functionality matching D&D 2024 rules.