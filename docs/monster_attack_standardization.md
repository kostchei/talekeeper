# Monster Attack Standardization Plan

## Problem Statement

Our current monster database uses D&D Beyond's JSON format with complex text descriptions that require sophisticated regex parsing. This leads to:
- **Parsing Complexity**: Multiple regex patterns for slight variations
- **Fragility**: New monster formats might not parse correctly
- **Maintenance Burden**: Adding new patterns as we find edge cases

## Proposed Solution: Structured Attack Format

Instead of parsing complex text, standardize all monster attacks to use a structured JSON format that explicitly defines mechanics.

## Current vs. Proposed Format

### Current Format (Complex Text)
```json
{
  "name": "Bite",
  "entries": [
    "{@atk mw} {@hit 5} to hit, reach 5 ft., one creature. {@h}7 ({@damage 1d8 + 3}) piercing damage, and the target must make a {@dc 11} Constitution saving throw, taking 9 ({@damage 2d8}) poison damage on a failed save, or half as much damage on a successful one. If the poison damage reduces the target to 0 hit points, the target is stable but {@condition poisoned} for 1 hour, even after regaining hit points, and is {@condition paralyzed} while {@condition poisoned} in this way."
  ]
}
```

### Proposed Format (Structured)
```json
{
  "name": "Bite",
  "attack_type": "melee",
  "attack_bonus": 5,
  "reach": 5,
  "damage": {
    "primary": {
      "dice": "1d8+3",
      "type": "piercing"
    }
  },
  "effects": [
    {
      "type": "save_or_damage",
      "save_dc": 11,
      "save_ability": "constitution",
      "damage_fail": {
        "dice": "2d8",
        "type": "poison"
      },
      "damage_success": {
        "dice": "1d4",
        "type": "poison"
      }
    },
    {
      "type": "conditional_condition",
      "trigger": "reduced_to_0_hp_by_poison",
      "condition": "poisoned",
      "duration": "1 hour"
    },
    {
      "type": "linked_condition",
      "while_condition": "poisoned",
      "also_condition": "paralyzed"
    }
  ],
  "description": "Venomous bite that can poison and paralyze victims."
}
```

## Benefits of Standardization

### 1. **Parsing Simplicity**
```python
# Instead of complex regex
attack_bonus = extract_attack_bonus_with_regex(text)

# Simple property access
attack_bonus = attack_data["attack_bonus"]
```

### 2. **Type Safety**
```python
# Current: string parsing can fail
save_dc = int(re.search(r'DC (\d+)', text).group(1))  # Might crash

# Proposed: guaranteed structure
save_dc = effect["save_dc"]  # Always an integer
```

### 3. **Extensibility**
```python
# Easy to add new effect types
{
  "type": "area_effect",
  "shape": "cone",
  "size": 30,
  "save_dc": 15,
  "save_ability": "dexterity"
}
```

### 4. **Multilingual Support**
```python
# Description can be localized while mechanics stay consistent
{
  "name": "Bite",
  "attack_bonus": 5,
  "description": {
    "en": "Venomous bite attack",
    "es": "Mordida venenosa"
  }
}
```

## Complete Effect Type Catalog

### Basic Effects
```json
{
  "type": "automatic_condition",
  "condition": "grappled",
  "escape_dc": 13
}
```

### Save Effects
```json
{
  "type": "save_or_condition",
  "save_dc": 12,
  "save_ability": "constitution",
  "condition": "paralyzed",
  "duration": "1 minute",
  "save_frequency": "end_of_turn"
}
```

### Damage Effects
```json
{
  "type": "save_or_damage",
  "save_dc": 15,
  "save_ability": "dexterity",
  "damage_fail": {"dice": "6d6", "type": "fire"},
  "damage_success": {"dice": "3d6", "type": "fire"}
}
```

### Size-Based Effects
```json
{
  "type": "size_condition",
  "max_size": "large",
  "condition": "grappled",
  "escape_dc": 14
}
```

### Area Effects
```json
{
  "type": "area_save",
  "shape": "cone",
  "size": 30,
  "save_dc": 18,
  "save_ability": "constitution",
  "damage_fail": {"dice": "10d8", "type": "cold"},
  "damage_success": {"dice": "5d8", "type": "cold"}
}
```

### Movement Effects
```json
{
  "type": "forced_movement",
  "distance": 20,
  "direction": "away",
  "condition_on_impact": "prone"
}
```

## Migration Strategy

### Phase 1: Core Monsters (High Priority)
Update monsters commonly encountered in early gameplay:
- **Giant Spider** (Web + Poison)
- **Goblin** variants
- **Wolf**, **Bear** (basic attacks)
- **Skeleton**, **Zombie** (undead)
- **Orc** variants

### Phase 2: Condition-Heavy Monsters
Focus on monsters with complex condition effects:
- **Basilisk** (Petrifying Gaze)
- **Ghast** (Paralysis)
- **Ankheg** (Grapple)
- **Air Elemental** (Whirlwind)
- **Medusa** (Petrification)

### Phase 3: High-Level Monsters
Dragons, powerful creatures with multiple complex attacks:
- **Adult Dragons** (Frightful Presence + Breath Weapons)
- **Beholders** (Eye Rays)
- **Liches** (Spell-like attacks)

### Phase 4: Specialized Monsters
Unique mechanics and edge cases:
- **Mimics** (Adhesive)
- **Rust Monsters** (Rust Metal)
- **Gelatinous Cubes** (Engulf)

## Implementation Plan

### Step 1: Create Migration Script
```python
def migrate_monster_attacks():
    # Read current monster data
    # Convert to standardized format
    # Validate new format
    # Update database
```

### Step 2: Update Parser
```python
class StandardizedAttackParser:
    def parse_attack(self, attack_data: dict) -> ParsedAttack:
        # Direct property access instead of regex
        return ParsedAttack(
            name=attack_data["name"],
            attack_bonus=attack_data["attack_bonus"],
            effects=[self.parse_effect(e) for e in attack_data.get("effects", [])]
        )
```

### Step 3: Backward Compatibility
Keep both parsers during transition:
```python
def parse_monster_attack(attack_data):
    if "attack_bonus" in attack_data:  # New format
        return StandardizedAttackParser().parse(attack_data)
    else:  # Old format
        return LegacyAttackParser().parse(attack_data)
```

## Example Migrations

### Giant Spider Bite
**Before:**
```json
{
  "name": "Bite",
  "entries": ["{@atk mw} {@hit 5} to hit, reach 5 ft., one creature. {@h}7 ({@damage 1d8 + 3}) piercing damage, and the target must make a {@dc 11} Constitution saving throw, taking 9 ({@damage 2d8}) poison damage on a failed save, or half as much damage on a successful one..."]
}
```

**After:**
```json
{
  "name": "Bite",
  "attack_type": "melee",
  "attack_bonus": 5,
  "reach": 5,
  "damage": {"primary": {"dice": "1d8+3", "type": "piercing"}},
  "effects": [
    {
      "type": "save_or_damage",
      "save_dc": 11,
      "save_ability": "constitution",
      "damage_fail": {"dice": "2d8", "type": "poison"},
      "damage_success": {"dice": "1d4", "type": "poison"}
    },
    {
      "type": "conditional_condition",
      "trigger": "reduced_to_0_hp_by_poison",
      "condition": "poisoned",
      "duration": "1 hour"
    }
  ]
}
```

### Ankheg Bite with Grapple
**Before:**
```json
{
  "name": "Bite",
  "entries": ["{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}10 ({@damage 2d6 + 3}) slashing damage plus 3 ({@damage 1d6}) acid damage. If the target is a Large or smaller creature, it is {@condition grappled} (escape {@dc 13})."]
}
```

**After:**
```json
{
  "name": "Bite",
  "attack_type": "melee",
  "attack_bonus": 5,
  "reach": 5,
  "damage": {
    "primary": {"dice": "2d6+3", "type": "slashing"},
    "additional": [{"dice": "1d6", "type": "acid"}]
  },
  "effects": [
    {
      "type": "size_condition",
      "max_size": "large",
      "condition": "grappled",
      "escape_dc": 13
    }
  ]
}
```

## Success Metrics

### Before Migration
- **Parser Complexity**: 200+ lines of regex patterns
- **Test Coverage**: 15 test cases covering edge cases
- **Failure Rate**: ~5% of attacks fail to parse correctly
- **Maintenance**: Adding new monsters requires regex updates

### After Migration
- **Parser Complexity**: 50 lines of simple property access
- **Test Coverage**: 5 test cases (structure validation)
- **Failure Rate**: 0% (guaranteed structure)
- **Maintenance**: Adding new monsters requires no parser changes

## Timeline

- **Week 1**: Design standardized format (✅ Complete)
- **Week 2**: Create migration scripts for top 20 monsters
- **Week 3**: Update parser to handle both formats
- **Week 4**: Migrate remaining monsters in batches
- **Week 5**: Remove legacy parser, finalize system

This standardization will make TaleKeeper's monster system much more robust, maintainable, and extensible while ensuring perfect parsing reliability.