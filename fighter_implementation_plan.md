# Fighter Implementation Plan

## Core Principles
1. **Database-driven**: Store all values in database tables
2. **UI Updates**: Call UI updates when values change
3. **Log Effects**: Record all ability uses and effects in log
4. **Single Responsibility**: One function per action, called from multiple places
5. **Comment Old Code**: Comment out redundant code rather than delete

## Database Schema Requirements

### Existing Tables to Modify
- `characters`: Add columns for fighter-specific resources
  - `second_wind_uses_current` (INT)
  - `second_wind_uses_max` (INT)
  - `action_surge_uses_current` (INT)
  - `action_surge_uses_max` (INT)
  - `indomitable_uses_current` (INT)
  - `indomitable_uses_max` (INT)
  - `weapon_mastery_count` (INT)
  - `weapon_mastery_selections` (JSON) - List of weapon types

### New Tables Needed
- `character_weapon_masteries`
  - `character_id` (FK)
  - `weapon_type` (TEXT)
  - `mastery_property` (TEXT)
  
- `character_combat_state`
  - `character_id` (FK)
  - `studied_target_id` (TEXT) - For Studied Attacks
  - `last_miss_turn` (INT)
  - `heroic_warrior_active` (BOOL)
  - `survivor_active` (BOOL)

## Implementation Order & Location

### Phase 1: Core Fighter Features (Level 1-2)

#### 1. Fighting Style (Level 1)
**Location**: `services/feat_effects.py` (already partially exists)
**Actions**:
- Check existing implementation
- Consolidate duplicate code
- Ensure all styles work:
  - Defense: +1 AC (passive)
  - Dueling: +2 damage (check in combat_engine.py)
  - Great Weapon Fighting: Reroll 1-2s (check in combat_engine.py)
  - Two-Weapon Fighting: Add ability mod to off-hand
  - Archery: +2 attack with ranged
  - Others as needed

#### 2. Second Wind (Level 1)
**Location**: Create `services/fighter_abilities.py`
**Database**: Add to `characters` table
**UI**: Add action card in `action_cards/`
**Implementation**:
```python
def use_second_wind(character_id):
    # Check uses remaining
    # Roll 1d10 + fighter_level
    # Heal HP
    # Decrement uses
    # Update UI
    # Log effect
```

#### 3. Weapon Mastery (Level 1)
**Location**: `core/combat_engine.py` + new `services/weapon_mastery.py`
**Database**: `character_weapon_masteries` table
**Implementation**:
- Auto-apply mastery effects based on equipped weapon
- Properties to implement:
  - Nick: Extra attack as part of Attack action
  - Push: Move target 10 feet
  - Sap: Disadvantage on next attack
  - Slow: -10 speed
  - Graze: Damage on miss
  - Cleave: Hit adjacent enemy
  - Topple: CON save or prone
  - Vex: Advantage on next attack

#### 4. Action Surge (Level 2)
**Location**: `services/fighter_abilities.py`
**UI**: Add action card
**Implementation**:
```python
def use_action_surge(character_id):
    # Check uses remaining
    # Grant additional action (except Magic)
    # Update combat state
    # Log effect
```

#### 5. Tactical Mind (Level 2)
**Location**: `services/fighter_abilities.py`
**Trigger**: On failed ability check
**Implementation**:
```python
def use_tactical_mind(character_id, check_result):
    # Expend Second Wind use
    # Roll 1d10
    # Add to check
    # If still fails, refund Second Wind
```

### Phase 2: Champion Subclass (Level 3+)

#### 1. Improved Critical (Level 3)
**Location**: `core/combat_engine.py`
**Implementation**: Modify critical range check

#### 2. Remarkable Athlete (Level 3)
**Location**: `services/feat_effects.py`
**Effects**:
- Advantage on Initiative
- Advantage on Athletics
- Increased jump distance

### Phase 3: Mid-Level Features (Level 5-13)

#### 1. Extra Attack (Level 5, 11, 20)
**Location**: `core/combat_engine.py`
**Implementation**: Check fighter level for attack count

#### 2. Tactical Shift (Level 5)
**Location**: Modify `use_second_wind()`
**Effect**: Half movement without opportunity attacks

#### 3. Indomitable (Level 9)
**Location**: `services/fighter_abilities.py`
**Implementation**: Reroll failed saves with bonus

#### 4. Tactical Master (Level 9)
**Location**: `services/weapon_mastery.py`
**Implementation**: Allow swapping mastery properties

#### 5. Studied Attacks (Level 13)
**Location**: `core/combat_engine.py`
**Database**: Track misses in `character_combat_state`
**Implementation**: Grant advantage after miss

### Phase 4: High-Level Features (Level 15+)

#### 1. Superior Critical (Level 15)
**Location**: `core/combat_engine.py`
**Implementation**: Crit on 18-20

#### 2. Heroic Warrior (Level 10) & Survivor (Level 18)
**Location**: `services/fighter_abilities.py`
**Trigger**: Start of turn
**Implementation**: Auto-heal when below half HP

## File Structure Changes

### New Files
- `services/fighter_abilities.py` - Fighter-specific abilities
- `services/weapon_mastery.py` - Weapon mastery system
- `ui/fighter_resources_panel.py` - Display Second Wind, Action Surge uses

### Files to Modify
- `core/game_engine_sqlite.py` - Add fighter resource management
- `core/combat_engine.py` - Attack calculations, critical ranges
- `services/feat_effects.py` - Consolidate fighting styles
- `action_cards/` - Add fighter ability cards
- `character_sheet/` - Display fighter resources
- `ui/main_window.py` - Connect fighter UI updates

## Testing Requirements

### Unit Tests Needed
1. Each fighting style effect
2. Second Wind healing calculation
3. Weapon mastery triggers
4. Extra attack counts per level
5. Critical hit ranges
6. Resource usage/recovery

### Integration Tests
1. Full combat with fighter abilities
2. Rest recovery of resources
3. Level progression updates
4. UI synchronization

## Common Functions Library

### Resource Management
```python
# In game_engine_sqlite.py
def update_fighter_resource(character_id, resource_type, delta):
    """Central function for all fighter resource updates"""
    
def get_fighter_resources(character_id):
    """Get all current fighter resources"""
    
def reset_fighter_resources(character_id, rest_type):
    """Reset resources on rest"""
```

### Combat Modifications
```python
# In combat_engine.py
def get_attack_count(character):
    """Calculate number of attacks based on class/level"""
    
def check_critical_range(character, roll):
    """Check if roll is critical based on features"""
    
def apply_weapon_mastery(attacker, target, weapon, hit_result):
    """Apply weapon mastery effects"""
```

### UI Updates
```python
# In main_window.py
def refresh_fighter_resources():
    """Update all fighter resource displays"""
    
def log_fighter_ability(ability_name, effect):
    """Log fighter ability usage"""
```

## Migration Strategy

1. **Backup database** before changes
2. **Add new columns** with defaults for existing characters
3. **Comment out old code** when replacing
4. **Test each feature** independently
5. **Run full test suite** after each phase

## ACTUAL IMPLEMENTATION RESULTS & CONFLICTS FOUND

### ❌ Major Issues Discovered During Implementation

#### 1. **No Central Combat Engine**
- **PLANNED**: Modify `core/combat_engine.py` for attack calculations
- **REALITY**: File doesn't exist! Combat logic scattered across `action_cards/action_panel.py`
- **IMPACT**: Attack flow spread across multiple methods (_execute_attack, _new_execute_attack)
- **CONFLICT**: Two parallel attack systems running simultaneously

#### 2. **Weapon Mastery Already Exists**
- **PLANNED**: Create new `services/weapon_mastery.py`
- **REALITY**: `services/weapon_mastery_effects.py` already implemented with Graze, Topple, Sap, etc.
- **IMPACT**: No new file needed, system already integrated into action_panel.py
- **CONFLICT**: Our plan duplicated existing functionality

#### 3. **Character Context Missing ID**
- **PLANNED**: Use character_id for service calls
- **REALITY**: `character_context` doesn't consistently include ID
- **IMPACT**: Had to modify UI loading flow to ensure ID is passed
- **CONFLICT**: Services require ID but UI doesn't always provide it

#### 4. **Feature System Complexity**
- **PLANNED**: Simple feature integration
- **REALITY**: Multiple overlapping systems:
  - Old ability_uses system
  - character_features table
  - New feature_integration.py
  - Fighter-specific tables
- **CONFLICT**: Had to work around 3 different feature tracking systems

#### 5. **Critical Hit Logic Missing**
- **PLANNED**: Modify critical range check in combat_engine.py
- **REALITY**: No critical hit logic existed anywhere
- **IMPACT**: Had to implement from scratch in attack execution
- **CONFLICT**: No centralized place for combat mechanics

### ✅ What Worked as Planned

#### 1. **Database-First Approach**
- Migration scripts worked perfectly
- Resource columns added successfully
- Service architecture clean and maintainable

#### 2. **Action Card Integration**
- UI integration straightforward
- Second Wind and Action Surge cards working
- Proper logging and resource tracking

#### 3. **Service Pattern**
- `fighter_abilities.py` provides clean API
- Centralized resource management
- Database-driven state management

### ⚠️ Partially Implemented

#### 1. **Extra Attacks**
- **STATUS**: Not implemented
- **REASON**: Attack flow too complex to modify safely
- **NEEDS**: Combat system refactor first

#### 2. **Studied Attacks**
- **STATUS**: Database tracking ready, not integrated
- **REASON**: Attack flow modification required
- **NEEDS**: Combat event system

#### 3. **Rest Integration**
- **STATUS**: Service methods ready, not connected
- **REASON**: Rest system integration point unclear
- **NEEDS**: Find where rest is processed

### 🔧 Required Fixes for Future Classes

#### 1. **Combat System Refactor**
```python
# NEEDED: Central combat coordinator
class CombatEngine:
    def execute_attack(self, attacker, target, weapon):
        # Centralized attack logic
        # Handle extra attacks here
        # Apply all modifiers consistently
```

#### 2. **Character Context Standardization**
```python
# NEEDED: Ensure all contexts include:
{
    'id': character_id,           # CRITICAL for service calls
    'class_id': class_name,       # For class-specific logic
    'level': character_level,     # For level-based features
    # ... other standard fields
}
```

#### 3. **Feature System Unification**
```python
# NEEDED: Single feature tracking system
# Replace: ability_uses, character_features, class-specific tables
# With: unified feature_states table
```

### 📋 Updated Implementation Order

#### Phase 1: Core Infrastructure ✅ DONE
- Database migrations ✅
- Fighter service ✅
- Action cards ✅
- Basic UI integration ✅

#### Phase 2: Combat Integration ⚠️ PARTIALLY DONE
- Critical hits ✅
- Extra attacks ❌ (needs combat refactor)
- Weapon mastery integration ✅ (already existed)

#### Phase 3: Advanced Features ❌ BLOCKED
- Studied Attacks ❌ (needs combat events)
- Tactical Mind ❌ (needs ability check system)
- Indomitable ❌ (needs saving throw system)

#### Phase 4: System Integration ❌ NOT STARTED
- Rest system integration ❌
- Level progression updates ❌
- Testing framework ❌

## Known Integration Points

### Existing Code Actually Found
- ✅ `services/weapon_mastery_effects.py`: Fully implemented weapon masteries
- ✅ `action_cards/action_panel.py`: Contains all attack logic (lines 839-923)
- ✅ `core/feature_integration.py`: Existing feature system with fighter support
- ❌ `core/combat_engine.py`: **DOES NOT EXIST**
- ⚠️ `services/feat_effects.py`: Partial fighting styles implementation

### Actual Conflicts Found
- 🔴 **Two attack systems**: _execute_attack vs _new_execute_attack
- 🔴 **Three feature systems**: ability_uses + character_features + class tables
- 🔴 **Scattered combat logic**: No single source of truth
- 🔴 **Inconsistent character context**: ID sometimes missing
- 🔴 **Resource tracking inconsistencies**: Old vs new systems

## LESSONS LEARNED FOR BARBARIAN IMPLEMENTATION

### 🎯 What to Do Differently

#### 1. **Code Discovery First**
- ✅ **DO**: Search entire codebase for existing implementations BEFORE planning
- ❌ **DON'T**: Assume files exist or functionality is missing
- 🔍 **CHECK**: Use Grep extensively to find all related code

#### 2. **Combat Integration Strategy**
- ✅ **DO**: Work within existing `action_panel.py` structure
- ❌ **DON'T**: Try to refactor combat system while implementing class
- 🎯 **FOCUS**: Service layer for resources, UI integration for abilities

#### 3. **Character Context Requirements**
- ✅ **DO**: Ensure character ID flows through all contexts
- ❌ **DON'T**: Assume UI components have all needed data
- 🔧 **FIX**: Update UI loading to guarantee service requirements met

#### 4. **Feature System Approach**
- ✅ **DO**: Use service pattern for class-specific resources
- ❌ **DON'T**: Try to unify all feature systems at once
- 🏗️ **STRATEGY**: Build alongside existing systems, not replace them

### 📊 Success Criteria (Updated)

#### ✅ **ACHIEVED**
1. ✅ Database-driven resource management
2. ✅ UI updates immediately when resources change
3. ✅ All effects logged in combat log
4. ✅ Service pattern provides clean API
5. ✅ Basic fighter abilities functional

#### ❌ **NOT ACHIEVED** 
1. ❌ No duplicate code (found 2 attack systems)
2. ❌ Single source of truth (3 feature systems)
3. ❌ All fighter features working (missing Extra Attack, etc.)
4. ❌ Tests implemented

#### ⚠️ **PARTIALLY ACHIEVED**
1. ⚠️ D&D 2024 rules compliance (basic features work, advanced features missing)

### 🚀 **Recommended Approach for Barbarian**

#### Phase 1: Discovery & Planning ✅
1. ✅ Search for existing Rage implementation
2. ✅ Map out all Barbarian features (levels 1-20)
3. ✅ Check action_panel.py for existing integration
4. ✅ Verify character context includes ID

#### Phase 2: Core Implementation 🎯
1. 🏗️ Create `services/barbarian_abilities.py`
2. 🗃️ Add Barbarian resource columns to database
3. 🎮 Integrate Rage action card (may already exist)
4. 📝 Ensure combat log integration

#### Phase 3: Combat Features ⚠️
1. 🗡️ Work within existing attack damage system
2. 💪 Add Rage damage to existing bonus calculations
3. 🛡️ Add Unarmored Defense to AC calculations
4. ⚔️ Integrate Reckless Attack into advantage system

#### Phase 4: Advanced Features 🔄
1. 🎯 Use lessons from Fighter implementation
2. 🧩 Build incrementally, test each piece
3. 📊 Document what works and what doesn't