# Monster Non-Attack Abilities - Implementation Status

## Summary

We have successfully implemented the foundation for monster non-attack abilities including breath weapons, limited use abilities (X/Day), and save-based effects with automatic condition application.

## What's Been Implemented

### 1. Core Systems

#### Monster Ability Manager Service
**File:** [src/talekeeper/services/monster_ability_manager.py](../src/talekeeper/services/monster_ability_manager.py)

- **AbilityType Enum**: Recharge, Limited Use, At-Will, Legendary
- **RechargeType Enum**: 5-6, 4-6, 6, None
- **MonsterAbility Dataclass**: Full ability definition with saves, damage, conditions
- **AbilityState Dataclass**: Runtime state tracking (available, uses remaining, last roll)

#### Key Features:
- `initialize_ability()` - Set up ability tracking for an encounter
- `attempt_recharge()` - Roll d6 for breath weapon recharge
- `use_ability()` - Mark ability as used, decrement limited uses
- `execute_ability()` - Full execution with saves, damage, condition application
- `reset_daily_abilities()` - Long rest reset for X/Day abilities
- `get_ability_state()` - Check current availability

### 2. Database Schema
**Migration:** [database/migrations/041_monster_abilities_system.sql](../database/migrations/041_monster_abilities_system.sql)

#### Tables Added:

```sql
monster_ability_tracker (
    encounter_id, monster_id, ability_name,
    ability_type, recharge_requirement,
    max_uses, uses_remaining, is_available,
    last_recharge_roll
)

monster_ability_effects (
    effect_id, encounter_id, source_monster_id,
    ability_name, target_id, effect_type,
    save_dc, duration_type, can_repeat_save,
    save_ability, created_round
)
```

### 3. Integration Points

#### Existing Systems Used:
- **ConditionManager**: Applies conditions (frightened, paralyzed, charmed, etc.)
- **DiceRoller**: Handles damage rolls and recharge dice
- **Existing Save System**: Uses proficiency_system for save bonuses

#### Condition Types Supported:
- Blinded, Charmed, Deafened
- Frightened, Grappled, Incapacitated
- Paralyzed, Petrified, Poisoned
- Prone, Restrained, Stunned, Unconscious

### 4. Predefined Abilities

Currently implemented in `PREDEFINED_ABILITIES`:

1. **Fire Breath** - Recharge 5-6, 18d6 fire, DC 19 Dex, 60ft cone
2. **Lightning Breath** - Recharge 5-6, 12d10 lightning, DC 19 Dex, 90ft line
3. **Acid Breath** - Recharge 5-6, 12d8 acid, DC 18 Dex, 60ft line
4. **Sleep Breath** - Recharge 5-6, unconscious condition, DC 18 Con
5. **Frightful Presence** - At-Will, frightened condition, DC 19 Wis, 120ft radius
6. **Dominate Mind** - 2/Day, charmed condition, DC 16 Wis (Aboleth)
7. **Petrifying Gaze** - At-Will, restrained->petrified, DC 14 Con (Basilisk)
8. **Paralyzing Touch** - At-Will, paralyzed, DC 13 Con (Ghoul)

### 5. Test Coverage
**File:** [tests/services/test_monster_ability_manager.py](../tests/services/test_monster_ability_manager.py)

All tests passing:
- test_initialize_recharge_ability
- test_recharge_mechanics
- test_limited_use_ability
- test_execute_ability_with_save
- test_execute_breath_weapon_damage
- test_condition_application
- test_reset_daily_abilities
- test_get_all_monster_abilities

## How It Works

### Automatic Save System (No Player Prompts)

**Key Design**: Saves work exactly like weapon attacks - fully automatic, no UI prompts needed.

**Flow:**
1. Monster uses ability (e.g., Dragon uses Fire Breath)
2. System looks up player's save modifier from character stats
3. Auto-rolls: d20 + ability modifier + proficiency (if proficient)
4. Compares total to DC
5. Applies results automatically to combat log

**Just like weapon attacks:**
- Weapon attack: Roll + bonus vs AC → Hit/Miss → Apply damage
- Save ability: Roll + save bonus vs DC → Success/Fail → Apply damage + condition

**No dialogs, no prompts** - monster uses ability, results appear in combat log instantly.

### Example: Dragon Fire Breath

```python
from talekeeper.services.monster_ability_manager import (
    MonsterAbilityManager,
    PREDEFINED_ABILITIES
)

manager = MonsterAbilityManager()

# Initialize ability for encounter
fire_breath = PREDEFINED_ABILITIES['fire_breath']
manager.initialize_ability("encounter_1", "red_dragon_1", fire_breath)

# At start of dragon's turn
success, roll = manager.attempt_recharge("encounter_1", "red_dragon_1", "Fire Breath")
print(f"Recharge roll: {roll}, Success: {success}")

# Use the ability
if success:
    result = manager.execute_ability(
        encounter_id="encounter_1",
        monster_id="red_dragon_1",
        monster_name="Adult Red Dragon",
        ability=fire_breath,
        target_id="player_char_1",
        target_data={
            'dexterity': 14,
            'proficiency_bonus': 3,
            'save_proficiencies': ['dexterity']
        }
    )

    # Result contains:
    # - save_roll, save_total, save_success, save_dc
    # - damage, damage_type (half damage on save)
    # - messages (array of combat log strings)
```

### Example: Aboleth Dominate Mind (2/Day)

```python
dominate = PREDEFINED_ABILITIES['dominate_mind']
manager.initialize_ability("encounter_1", "aboleth_1", dominate)

# Use first time
result1 = manager.execute_ability(...) # Uses remaining: 1

# Use second time
result2 = manager.execute_ability(...) # Uses remaining: 0

# Try third time
result3 = manager.execute_ability(...) # Returns {'success': False, 'error': 'Ability not available'}

# After long rest
manager.reset_daily_abilities("encounter_1", "aboleth_1") # Uses remaining: 2
```

## What's Next

### Immediate Next Steps:

1. **UI Integration** - Display abilities in monster action cards
2. **Area of Effect** - Implement cone/line/radius targeting for multi-target abilities
3. **Combat Log Integration** - Show recharge rolls and ability usage
4. **Auto-execute in Combat** - Wire up to monster AI turn system

### Phase 2: Additional Abilities

Need to add to PREDEFINED_ABILITIES:
- Poison Breath (Green Dragon)
- Repulsion Breath (Bronze Dragon)
- Slowing Breath (Copper Dragon)
- Weakening Breath (Gold Dragon)
- Ankheg Acid Spray (Recharge 6)
- Behir Lightning Breath
- Duergar Enlarge (Recharge 4-6)

### Phase 3: UI Components

#### Monster Action Card
Need to show:
```
+----------------------------------+
| Adult Red Dragon                 |
+----------------------------------+
| BITE          +14    2d10+8 piercing
| CLAW          +14    2d6+8 slashing
|
| FIRE BREATH   [RECHARGE 5-6]
|   60 ft. cone, DC 19 Dex save
|   63 (18d6) fire damage
|   [READY] / [USED - Last roll: 3]
+----------------------------------+
```

#### Combat Log Output (Automatic)
Monster ability execution appears in combat log:
```
Adult Red Dragon uses Fire Breath!
Conan makes a Dexterity saving throw...
  Roll: 12 + Modifier: 5 = 17 vs DC 19
  FAILED!
Conan takes 63 fire damage!

(Next turn - recharge attempt)
Fire Breath recharge: rolled 5 - SUCCESS! Fire Breath is ready!
```

### Phase 4: Advanced Features

- Legendary Actions (costs action points, used between turns)
- Lair Actions (initiative count 20)
- Swallow/Engulf mechanics
- Progressive saves (Petrification: fail once = restrained, twice = petrified)
- Summoning (demons, elementals)
- Shapechange/Polymorph

## Architecture Benefits

### Clean Separation
- **MonsterAbilityManager**: Handles ability state and execution
- **ConditionManager**: Handles condition effects and mechanics
- **DiceRoller**: Handles all random rolls
- **ProficiencySystem**: Calculates save bonuses

### Extensible Design
- Easy to add new abilities to PREDEFINED_ABILITIES
- MonsterAbility dataclass supports all D&D ability patterns
- Database tracks state per encounter (no cross-contamination)

### Testable
- All components unit tested
- Integration with existing systems verified
- Easy to mock for UI testing

## Performance Considerations

- Abilities initialized only once per encounter
- State queries use indexed lookups (encounter_id, monster_id)
- No expensive computations during combat
- Save system reuses existing proficiency calculations

## Database Queries

Most common queries:

```sql
-- Check if ability is available
SELECT is_available, uses_remaining
FROM monster_ability_tracker
WHERE encounter_id = ? AND monster_id = ? AND ability_name = ?

-- Get all abilities for monster
SELECT * FROM monster_ability_tracker
WHERE encounter_id = ? AND monster_id = ?

-- Reset daily abilities
UPDATE monster_ability_tracker
SET uses_remaining = max_uses, is_available = 1
WHERE encounter_id = ? AND monster_id = ?
AND ability_type = 'limited_use'
```

## Integration Checklist

To fully integrate into TaleKeeper:

- [ ] Add ability definitions to monster database (actions JSON)
- [ ] Update encounter panel to initialize monster abilities on encounter start
- [ ] Create monster ability action cards UI (show available abilities)
- [ ] Display recharge status in monster action cards ([READY] / [USED - Roll: 3])
- [ ] Show ability usage in combat log (auto-execute, no prompts)
- [ ] Integrate with turn manager for automatic recharge rolls
- [ ] Add long rest trigger for reset_daily_abilities
- [ ] Add ability usage to monster AI decision making (when to use breath vs attack)
- [ ] Create visual indicators for area effects (cones, lines) - optional
- [ ] Support multi-target abilities (AoE breath hits all characters in range)

## Example Monsters with Abilities

### Dragons
- All chromatic/metallic dragons have breath weapons
- All adult/ancient dragons have Frightful Presence
- Each color has unique breath type and damage

### Aberrations
- Aboleth: Dominate Mind (2/Day), Consume Memories
- Beholder: Eye Rays (varies by type)
- Mind Flayer: Mind Blast (Recharge 5-6)

### Undead
- Ghoul: Paralyzing Touch (with claw attack)
- Vampire: Charm (at-will)
- Mummy: Rotting Fist (curse on hit)

### Oozes
- Black Pudding: Split (when damaged by certain types)
- Gelatinous Cube: Engulf

### Special Conan Monsters
- Sorcerers: Various spell-like abilities
- Demons: Frightening aura, summon allies
- Ancient guardians: Petrifying gaze, life drain

## Documentation References

- **Design Doc**: [CONAN_NON_ATTACK_ABILITIES.md](CONAN_NON_ATTACK_ABILITIES.md)
- **Condition System**: Already implemented in condition_manager.py
- **Save System**: Already implemented in proficiency_system.py
- **D&D SRD**: [SRD_CC_v5.2.1.md](SRD_CC_v5.2.1.md)

---

**Status**: Core system implemented and tested (✓)
**Next**: UI integration for monster abilities and player save prompts
**ETA**: Ready for encounter panel integration
