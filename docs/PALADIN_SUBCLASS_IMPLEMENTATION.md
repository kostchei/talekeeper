# Paladin Subclass Implementation Plan

## Overview
Implement three Paladin subclasses with full mechanical support:
1. Oath of Devotion (SRD)
2. Oath of Glory (D&D 2024)
3. Oath of the Unbroken (Custom)

## Database Schema

### Subclass Features Table
```sql
CREATE TABLE IF NOT EXISTS subclass_features (
    id TEXT PRIMARY KEY,
    subclass_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_type TEXT NOT NULL, -- 'passive', 'channel_divinity', 'action', 'bonus_action', 'aura', 'capstone'
    description TEXT NOT NULL,
    mechanics TEXT, -- JSON for mechanical effects
    usage_type TEXT, -- 'unlimited', 'channel_divinity', 'long_rest', 'short_rest'
    uses_per_rest INTEGER DEFAULT NULL,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);
```

### Character Feature Instances (Already exists)
Track active features per character with current uses.

### Oath Spells Table
```sql
CREATE TABLE IF NOT EXISTS subclass_spells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_id TEXT NOT NULL,
    spell_name TEXT NOT NULL,
    paladin_level INTEGER NOT NULL,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);
```

## Implementation Phases

### Phase 1: Database Setup
**Files**: `database/migrations/XXX_paladin_subclass_features.sql`

**Tasks**:
1. Create `subclass_features` table
2. Create `subclass_spells` table
3. Insert Oath of Devotion features and spells
4. Insert Oath of Glory features (minimal for now)
5. Insert Oath of the Unbroken features (minimal for now)

**Oath of Devotion Features**:
- Level 3: Sacred Weapon (Channel Divinity)
- Level 3: Oath Spells (spell grants)
- Level 7: Aura of Devotion (passive aura)
- Level 15: Smite of Protection (passive enhancement)
- Level 20: Holy Nimbus (bonus action capstone)

### Phase 2: Feature Mechanics System
**Files**:
- `services/paladin_subclass_service.py` (new)
- `services/subclass_feature_manager.py` (new)

**Services Needed**:

#### SubclassFeatureManager
```python
class SubclassFeatureManager:
    def get_subclass_features_for_level(character_id, subclass_id, level) -> List[Feature]
    def grant_subclass_feature(character_id, feature_id)
    def get_active_features(character_id) -> List[Feature]
    def apply_feature_effect(character_id, feature_id, context)
```

#### PaladinSubclassService
```python
class PaladinSubclassService:
    def apply_sacred_weapon(character_id, weapon_id) -> dict
    def check_aura_of_devotion(character_id, target_id) -> bool
    def apply_smite_of_protection(character_id) -> dict
    def activate_holy_nimbus(character_id) -> dict
    def get_oath_spells(character_id, subclass_id, level) -> List[str]
```

### Phase 3: Feature Integration
**Files**:
- `core/combat_engine.py` (modify)
- `action_cards/action_panel.py` (modify)
- `services/aura_manager.py` (new)

**Integration Points**:

1. **Channel Divinity Integration**
   - Add to action cards when available
   - Track uses (existing system)
   - Apply effects in combat

2. **Aura System** (NEW)
   - Calculate 10ft/30ft radius from paladin position
   - Apply aura effects to allies in range
   - Check aura conditions each turn
   - Visual indicator in UI (future)

3. **Combat Modifications**
   - Sacred Weapon: Add CHA to attack rolls, choose damage type
   - Smite of Protection: Grant half cover when Divine Smite used
   - Holy Nimbus: Radiant damage at start of enemy turns

4. **Spell Grants**
   - Auto-prepare oath spells at specified levels
   - Don't count against prepared spell limit

### Phase 4: Action Card Implementation
**Files**: `action_cards/paladin_subclass_actions.py` (new)

**Action Cards Needed**:

1. **Sacred Weapon** (Channel Divinity)
   - Button in action panel
   - Select weapon to imbue
   - Duration: 10 minutes
   - Visual: glowing weapon indicator

2. **Holy Nimbus** (Level 20 Capstone)
   - Bonus action activation
   - Duration: 10 minutes (1 minute in combat)
   - Track: 1/long rest or 5th level slot

3. **Mind's Razor** (Oath of Unbroken)
   - Channel Divinity option
   - Use after hitting with weapon attack
   - Bypass resistance/immunity

4. **Unbroken Resolve** (Oath of Unbroken)
   - Bonus action
   - Grant temp HP and advantage on WIS saves

### Phase 5: UI Updates
**Files**:
- `encounter_pane/town_encounter.py` (subclass selection - already works)
- `character_sheet/character_sheet.py` (display active features)
- `action_cards/action_panel.py` (show subclass actions)

**UI Elements**:
1. Subclass feature list in character sheet
2. Active aura indicators
3. Channel Divinity options in action panel
4. Oath spell list display
5. Feature usage tracking (uses remaining)

### Phase 6: Testing
**Files**:
- `test/test_paladin_subclasses.py` (new)
- `test/test_aura_system.py` (new)

**Test Coverage**:
1. Subclass selection at level 3
2. Feature granting at correct levels
3. Sacred Weapon mechanics
4. Aura of Devotion (charm immunity)
5. Smite of Protection (half cover)
6. Holy Nimbus effects
7. Oath spells auto-preparation
8. Channel Divinity usage tracking

## Feature Priority

### MVP (Minimum Viable Product)
1. Database tables and seed data
2. Subclass selection working (already done)
3. Oath spells granted at level up
4. Basic feature tracking in character sheet

### Phase 1 Features
1. Sacred Weapon (Oath of Devotion)
2. Aura of Devotion (charm immunity)
3. Channel Divinity action cards

### Phase 2 Features
1. Smite of Protection
2. Holy Nimbus
3. Full aura system with positioning

### Phase 3 Features (Custom Oaths)
1. Oath of Unbroken features
2. Oath of Glory features

## Technical Challenges

### Challenge 1: Aura System
**Problem**: Need positioning system to calculate 10ft/30ft radius
**Solution**:
- Store character position in combat
- Calculate distance between characters
- Apply aura effects based on distance
- Update each turn/movement

### Challenge 2: Sacred Weapon Duration
**Problem**: Track 10-minute duration across multiple encounters
**Solution**:
- Store activation timestamp
- Check duration on each combat start
- Add to character_feature_instances with expiration

### Challenge 3: Spell Auto-Preparation
**Problem**: Oath spells always prepared, don't count against limit
**Solution**:
- Separate column in character spells: `source` = 'oath'
- Filter oath spells from preparation count
- Auto-grant on level up

### Challenge 4: Divine Smite Integration
**Problem**: Smite of Protection triggers on Divine Smite cast
**Solution**:
- Hook into existing Divine Smite code
- Check for Smite of Protection feature
- Apply half cover effect to aura radius

## Database Seed Data Structure

### Example: Sacred Weapon
```sql
INSERT INTO subclass_features (id, subclass_id, feature_name, level, feature_type, description, mechanics, usage_type, uses_per_rest) VALUES
('devotion_sacred_weapon', 'oath_of_devotion', 'Sacred Weapon', 3, 'channel_divinity',
'Imbue a melee weapon with positive energy for 10 minutes. Add Charisma modifier to attack rolls and choose radiant or normal damage.',
'{
    "duration_minutes": 10,
    "attack_bonus": "charisma_modifier",
    "damage_type_choice": ["normal", "radiant"],
    "light_radius": 20,
    "activation": "attack_action",
    "early_end": true
}',
'channel_divinity', NULL);
```

### Example: Aura of Devotion
```sql
INSERT INTO subclass_features (id, subclass_id, feature_name, level, feature_type, description, mechanics, usage_type) VALUES
('devotion_aura_of_devotion', 'oath_of_devotion', 'Aura of Devotion', 7, 'aura',
'You and allies within your aura are immune to the Charmed condition.',
'{
    "aura_radius": 10,
    "aura_radius_18": 30,
    "effect": "charm_immunity",
    "targets": "self_and_allies"
}',
'unlimited');
```

## Code Locations

### Existing Systems to Leverage
1. **Channel Divinity**: Already implemented for Paladin base class
2. **Divine Smite**: Existing in action_panel.py
3. **Condition System**: `services/condition_manager.py`
4. **Feature Registry**: `services/feature_registry.py`
5. **Level Up**: `services/unified_level_up.py`

### New Files Needed
1. `services/paladin_subclass_service.py`
2. `services/aura_manager.py`
3. `services/subclass_feature_manager.py`
4. `action_cards/paladin_subclass_actions.py`
5. `test/test_paladin_subclasses.py`
6. `database/migrations/XXX_paladin_subclass_features.sql`

## Next Steps
1. Create database migration for subclass_features and subclass_spells
2. Seed Oath of Devotion features
3. Implement SubclassFeatureManager service
4. Test feature granting at level 3
5. Implement Sacred Weapon as first feature
6. Add action card for Sacred Weapon
7. Test in combat
8. Continue with remaining features