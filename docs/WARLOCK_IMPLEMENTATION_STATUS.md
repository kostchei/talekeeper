# Warlock Implementation Status - D&D 2024 SRD
**Updated**: 2025-10-09
**Status**: In Progress - Foundation Complete, Mechanics Implementation Phase

---

## Current Status Summary

### ✅ COMPLETED
1. **Character Creation**: Warlock can be created at level 1
2. **Database Schema**: Basic warlock_features table exists
3. **Inline Patron Features**: Fiend patron features (levels 3, 6, 10, 14) - simplified implementation
4. **Database Lock Fix**: Removed external service calls during character creation
5. **Core Integration**: Warlock class in game_engine_sqlite.py

### 🔄 IN PROGRESS
1. **Pact Magic Mechanics**: Need to implement short rest recovery
2. **Eldritch Invocations**: Level 1 invocation selection not yet functional
3. **Spell Slot System**: Pact Magic slots exist but need proper UI/UX

### ❌ NOT STARTED
1. **Magical Cunning** (Level 2 feature)
2. **Contact Patron** (Level 9 feature)
3. **Mystic Arcanum** (Levels 11, 13, 15, 17)
4. **Eldritch Master** (Level 20 feature)
5. **Invocation effects** (passive abilities, spell modifications)
6. **Pact Boon selection** (Level 3 - though stored in patron features)

---

## D&D 2024 SRD Rules Reference

### Level Progression (Correct from SRD)

| Level | Invocations | Cantrips | Prepared Spells | Spell Slots | Slot Level | Class Features |
|-------|-------------|----------|-----------------|-------------|------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 1st | Eldritch Invocations, Pact Magic |
| 2 | 3 | 2 | 3 | 2 | 1st | Magical Cunning |
| 3 | 3 | 2 | 4 | 2 | 2nd | Warlock Subclass (Patron) |
| 4 | 3 | 3 | 5 | 2 | 2nd | ASI |
| 5 | 5 | 3 | 6 | 2 | 3rd | — |
| 6 | 5 | 3 | 7 | 2 | 3rd | Subclass feature |
| 7 | 6 | 3 | 8 | 2 | 4th | — |
| 8 | 6 | 3 | 9 | 2 | 4th | ASI |
| 9 | 7 | 3 | 10 | 2 | 5th | Contact Patron |
| 10 | 7 | 4 | 10 | 2 | 5th | Subclass feature |
| 11 | 7 | 4 | 11 | 3 | 5th | Mystic Arcanum (6th) |
| 12 | 8 | 4 | 11 | 3 | 5th | ASI |
| 13 | 8 | 4 | 12 | 3 | 5th | Mystic Arcanum (7th) |
| 14 | 8 | 4 | 12 | 3 | 5th | Subclass feature |
| 15 | 9 | 4 | 13 | 3 | 5th | Mystic Arcanum (8th) |
| 16 | 9 | 4 | 13 | 3 | 5th | ASI |
| 17 | 9 | 4 | 14 | 4 | 5th | Mystic Arcanum (9th) |
| 18 | 10 | 4 | 14 | 4 | 5th | — |
| 19 | 10 | 4 | 15 | 4 | 5th | Epic Boon |
| 20 | 10 | 4 | 15 | 4 | 5th | Eldritch Master |

---

## Core Mechanics to Implement

### 1. Pact Magic (Level 1) ✅ Partial
**Current State**: Slots tracked in database
**Needs**:
- Short rest recovery (ALL slots recovered on short rest)
- Long rest recovery
- Integration with spell casting UI
- Automatic upcasting to slot level

**Implementation**:
```python
def short_rest(character_id):
    # Warlock: Restore ALL Pact Magic slots
    # Other classes: Restore limited resources
```

### 2. Eldritch Invocations (Level 1) ❌
**What**: Choose 1 invocation at level 1, gain more as you level
**Needs**:
- Invocation selection UI during character creation
- Invocation replacement on level up
- Invocation prerequisite checking
- Apply invocation effects (passive/active/spell modifications)

**Key Invocations for Level 1**:
- Pact of the Tome (signature, grants Book of Shadows)
- Pact of the Blade (signature, grants pact weapon ability)
- Pact of the Chain (signature, grants enhanced familiar)
- Agonizing Blast (add CHA to Eldritch Blast damage)
- Armor of Shadows (cast Mage Armor at will)
- Eldritch Mind (advantage on Concentration saves)
- Fiendish Vigor (cast False Life at will)

### 3. Magical Cunning (Level 2) ❌
**What**: 1-minute ritual to regain spell slots (half max, round up)
**Usage**: Once per long rest
**Level 20**: Eldritch Master makes this restore ALL slots

**Implementation**:
```python
def use_magical_cunning(character_id):
    level = get_warlock_level(character_id)
    max_slots = get_max_pact_slots(character_id)
    current_slots = get_current_pact_slots(character_id)

    if level >= 20:
        # Eldritch Master: restore all
        slots_restored = max_slots - current_slots
    else:
        # Restore half (round up)
        slots_restored = min((max_slots + 1) // 2, max_slots - current_slots)

    update_pact_slots(character_id, current_slots + slots_restored)
    mark_magical_cunning_used(character_id)
```

### 4. Contact Patron (Level 9) ❌
**What**: Always have Contact Other Plane prepared
**Special**: Can cast once per long rest without slot, auto-succeed on save

**Implementation**: Add to always-prepared spells list with special flag

### 5. Mystic Arcanum (Levels 11+) ❌
**What**: Learn one 6th/7th/8th/9th level spell, cast once per long rest (no slot)

| Level | Spell Level | Feature |
|-------|-------------|---------|
| 11 | 6th | Mystic Arcanum (6th) |
| 13 | 7th | Mystic Arcanum (7th) |
| 15 | 8th | Mystic Arcanum (8th) |
| 17 | 9th | Mystic Arcanum (9th) |

**Implementation**: Separate from Pact Magic slots, track per-spell usage

---

## Fiend Patron Features (Already Implemented)

✅ **Level 3**: Dark One's Blessing - Temp HP on kill
✅ **Level 3**: Fiend Spells - Always prepared spell list
✅ **Level 6**: Dark One's Own Luck - Add d10 to check/save
✅ **Level 10**: Fiendish Resilience - Choose damage resistance
✅ **Level 14**: Hurl Through Hell - 8d10 psychic + incapacitated

---

## Next Implementation Steps

### Priority 1: Make Warlock Playable (Basic)
1. ✅ Fix character creation (database lock) - DONE
2. ⏭️ Implement Pact Magic short rest recovery
3. ⏭️ Add Eldritch Invocation selection at level 1
4. ⏭️ Implement Magical Cunning (level 2)
5. ⏭️ Test level 1-3 Warlock in combat

### Priority 2: Level 1-10 Features
6. Implement Contact Patron (level 9)
7. Add invocation replacement on level up
8. Implement key invocations (Agonizing Blast, Armor of Shadows, etc.)
9. Test Fiend patron features in combat
10. UI for spell slot display (Pact Magic vs standard)

### Priority 3: High-Level Features (11+)
11. Implement Mystic Arcanum system
12. Add Mystic Arcanum spell selection UI
13. Implement Eldritch Master (level 20)
14. Full regression test levels 1-20

---

## Database Schema Status

### Existing Tables
```sql
-- Already exists
warlock_features (
    character_id, level, patron, pact_boon,
    invocations_known, mystic_arcanum_spells,
    last_pact_reset, pact_slots_current,
    pact_slots_max, pact_slot_level
)

warlock_invocations (
    character_id, invocation_id, learned_at_level
)

invocations (
    id, name, description, prerequisites,
    effect_type, effect_data
)

warlock_pact_progression (
    level, num_slots, slot_level,
    invocations_known, cantrips_known, spells_known
)
```

### Needed Additions
```sql
-- Add to warlock_features
ALTER TABLE warlock_features ADD COLUMN magical_cunning_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN last_magical_cunning TEXT;
ALTER TABLE warlock_features ADD COLUMN contact_patron_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_6_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_7_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_8_used BOOLEAN DEFAULT 0;
ALTER TABLE warlock_features ADD COLUMN arcanum_9_used BOOLEAN DEFAULT 0;
```

---

## Testing Checklist

### Level 1-3 (Basic Functionality)
- [ ] Create level 1 Warlock with Fiend patron
- [ ] Select 1 Eldritch Invocation during creation
- [ ] Cast spell using Pact Magic slot
- [ ] Short rest restores Pact Magic slots
- [ ] Level 2: Use Magical Cunning to restore half slots
- [ ] Level 3: Gain Fiend patron features (Dark One's Blessing, Fiend Spells)

### Level 4-10 (Intermediate)
- [ ] Level 4: Gain 1 additional cantrip
- [ ] Level 5: Gain 2 more invocations (total 5)
- [ ] Level 6: Use Dark One's Own Luck
- [ ] Level 9: Contact Patron spell available
- [ ] Level 10: Set Fiendish Resilience damage type, gain 1 more cantrip

### Level 11-20 (Advanced)
- [ ] Level 11: Select 6th level Mystic Arcanum, gain 3rd pact slot
- [ ] Level 13: Select 7th level Mystic Arcanum
- [ ] Level 14: Use Hurl Through Hell
- [ ] Level 15: Select 8th level Mystic Arcanum
- [ ] Level 17: Select 9th level Mystic Arcanum, gain 4th pact slot
- [ ] Level 20: Eldritch Master restores all slots with Magical Cunning

---

## Implementation Notes

### Simplified Architecture Decision
**Decision**: Use inline patron features (like Paladin) instead of external service architecture
**Rationale**:
- Avoids database lock issues
- Simpler to maintain
- Patron features only activate at levels 3, 6, 10, 14 (not at level 1)
- Matches existing Paladin pattern

### Pact Magic vs Standard Spellcasting
- **Separate system**: Use warlock_features table, not standard spell slots
- **Recovery**: Short rest (Warlock) vs Long rest (other casters)
- **Slots**: All same level (auto-upcast) vs multiple levels
- **Multiclassing**: Pact Magic and Spellcasting slots kept separate per RAW

### Invocations as Features
Store invocations in character_features table with:
- `feature_type = 'eldritch_invocation'`
- `mechanics` JSON with effect data
- Check prerequisites on learn/replace

---

*Last Updated: 2025-10-09 after database lock fix and SRD review*
