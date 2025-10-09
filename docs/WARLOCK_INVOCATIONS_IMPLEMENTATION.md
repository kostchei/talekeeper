# Warlock Eldritch Invocations - Implementation Guide

**Date:** 2025-10-09
**Status:** ⚠️ **PARTIALLY IMPLEMENTED** - Selection works, effects not applied

## Current State

✅ **Working:**
- Invocations stored in database (`invocations` table with 25 invocations - updated 2025-10-09)
- Selection during level-up via `WarlockLevelUpDialog`
- Saved to `warlock_invocations` table
- Displayed in character sheet (as of 2025-10-09)
- All D&D 2024 SRD invocations now included

❌ **Not Working:**
- Invocation effects are NOT applied
- Data exists (`effect_type`, `effect_data`) but no system uses it

---

## All Invocations (25 Total)

| ID | Name | Min Level | Prerequisites | Effect Type | Description |
|----|------|-----------|---------------|-------------|-------------|
| `armor_of_shadows` | Armor of Shadows | - | - | active | Cast mage armor at will |
| `fiendish_vigor` | Fiendish Vigor | - | - | active | Cast false life at will (max HP) |
| `agonizing_blast` | Agonizing Blast | 2 | Damage cantrip | spell_modification | Add CHA to cantrip damage |
| `devils_sight` | Devils Sight | 2 | - | passive | See in darkness (magical) 120ft |
| `eldritch_mind` | Eldritch Mind | 2 | - | passive | Advantage on concentration saves |
| `eldritch_spear` | Eldritch Spear | 2 | Damage cantrip | spell_modification | +30ft range per level |
| `lessons_of_the_first_ones` | Lessons of the First Ones | 2 | - | passive | Gain Origin feat (repeatable) |
| `mask_of_many_faces` | Mask of Many Faces | 2 | - | active | Cast disguise self at will |
| `misty_visions` | Misty Visions | 2 | - | active | Cast silent image at will |
| `otherworldly_leap` | Otherworldly Leap | 2 | - | active | Cast jump at will (self) |
| `repelling_blast` | Repelling Blast | 2 | Attack cantrip | spell_modification | Push 10ft on hit (repeatable) |
| `ascendant_step` | Ascendant Step | 5 | - | active | Cast levitate at will (self) |
| `eldritch_smite` | Eldritch Smite | 5 | Pact of Blade | active | 1d8 force per slot level + prone |
| `gaze_of_two_minds` | Gaze of Two Minds | 5 | - | active | Perceive through ally's senses |
| `gift_of_the_depths` | Gift of the Depths | 5 | - | passive | Breathe underwater, swim speed |
| `investment_of_chain_master` | Investment of Chain Master | 5 | Pact of Chain | passive | Enhance familiar |
| `master_of_myriad_forms` | Master of Myriad Forms | 5 | - | active | Cast alter self at will |
| `one_with_shadows` | One with Shadows | 5 | - | active | Cast invisibility at will (self, dim/dark) |
| `thirsting_blade` | Thirsting Blade | 5 | Pact of Blade | passive | Extra Attack with pact weapon |
| `whispers_of_the_grave` | Whispers of the Grave | 7 | - | active | Cast speak with dead at will |
| `gift_of_the_protectors` | Gift of the Protectors | 9 | Pact of Tome | passive | Prevent death, drop to 1 HP |
| `lifedrinker` | Lifedrinker | 9 | Pact of Blade | passive | +1d6 damage + heal HD on hit |
| `visions_of_distant_realms` | Visions of Distant Realms | 9 | - | active | Cast arcane eye at will |
| `devouring_blade` | Devouring Blade | 12 | Thirsting Blade | passive | Extra Attack = 2 attacks not 1 |
| `witch_sight` | Witch Sight | 15 | - | passive | Truesight 30ft |

---

## Effect Data Structure (from database)

```json
// Spell Modification (Agonizing Blast)
{
  "spell": "eldritch_blast",
  "damage_bonus": "charisma"
}

// Active Spell (Armor of Shadows)
{
  "spell": "mage_armor",
  "cost": "none",
  "target": "self"
}

// Passive Bonus (Devil's Sight)
{
  "darkvision": 120,
  "magical_darkness": true
}

// Attack Modification (Eldritch Smite)
{
  "damage_per_slot_level": "1d8",
  "damage_type": "force",
  "base_dice": 1,
  "can_knock_prone": true,
  "size_limit": "Huge"
}
```

---

## Implementation Strategy - Use Existing Systems

### Option 1: Extend `class_abilities_service.py` (RECOMMENDED)

**Why:** Invocations are class abilities. Reuse existing infrastructure.

**Changes needed:**
1. Add invocations to `class_abilities` table:
   ```sql
   INSERT INTO class_abilities (ability_id, class_name, ability_name, ability_type, ...)
   SELECT
     'invocation_' || id,
     'Warlock',
     name,
     effect_type,
     effect_data,
     NULL as uses_formula, -- Most are passive/unlimited
     NULL as reset_type
   FROM invocations;
   ```

2. Link to characters via `character_ability_usage`:
   ```sql
   INSERT INTO character_ability_usage (character_id, ability_id, ...)
   SELECT character_id, 'invocation_' || invocation_id, ...
   FROM warlock_invocations;
   ```

3. Modify `ClassAbilitiesService.get_character_abilities()` to:
   - Load invocations from `warlock_invocations`
   - Join with `invocations` table for effect data
   - Return as abilities

**Pros:**
- Reuses all existing ability infrastructure
- Works with action cards automatically
- Consistent with Fighter/Barbarian/Rogue abilities

**Cons:**
- Need to migrate `warlock_invocations` → `class_abilities` pattern
- Some invocations (like passive modifiers) don't fit ability model

---

### Option 2: Create `InvocationEffectsService` (simpler for passives)

**Why:** Many invocations are passive modifiers, not activated abilities.

**Implementation:**
```python
# src/talekeeper/services/invocation_effects.py

class InvocationEffectsService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_character_invocations(self, character_id: str) -> List[Dict]:
        """Get all invocations with effect data"""
        # Query: warlock_invocations JOIN invocations
        pass

    def apply_passive_effects(self, character_id: str) -> Dict:
        """Apply passive invocation bonuses"""
        # Devil's Sight → darkvision
        # Eldritch Mind → concentration advantage
        # Thirsting Blade → extra attack
        pass

    def get_at_will_spells(self, character_id: str) -> List[str]:
        """Return list of at-will spells from invocations"""
        # Armor of Shadows → mage_armor
        # Fiendish Vigor → false_life
        # Ascendant Step → levitate
        pass

    def apply_spell_modification(self, spell_id: str, character_id: str, damage: int) -> int:
        """Modify spell damage (Agonizing Blast)"""
        # If spell = eldritch_blast AND has agonizing_blast
        # Return damage + CHA modifier
        pass
```

**Integration points:**
1. **Character stats calculation** - Call `apply_passive_effects()` when loading character
2. **Spell list** - Add `get_at_will_spells()` to available spells
3. **Damage calculation** - Call `apply_spell_modification()` in spell damage formula
4. **Action cards** - Add at-will spells as action cards (unlimited uses)

**Pros:**
- Simpler, more focused service
- Easier to handle passive modifiers
- Doesn't require migrating existing data

**Cons:**
- Yet another service (not unified)
- Duplicate code with `ClassAbilitiesService`

---

## Recommended Implementation Plan

### Phase 1: Passive Effects (Simplest)
Use existing code where possible, following the user's directive.

1. **Modify character loading to add at-will spells:**
   ```python
   # In action_panel.py _get_character_castable_spells():
   # Add after loading normal spells
   cursor.execute("""
       SELECT i.effect_data FROM warlock_invocations wi
       JOIN invocations i ON wi.invocation_id = i.id
       WHERE wi.character_id = ? AND i.effect_type = 'active'
   """, (character_id,))

   for row in cursor.fetchall():
       effect = json.loads(row[0])
       if 'spell' in effect and effect.get('cost') == 'none':
           spell_id = effect['spell']
           # Fetch spell details and add to spell list
           # Mark as unlimited uses (at-will)
   ```

2. **Modify spell damage calculation:**
   ```python
   # In spellcasting_service.py or wherever spell damage is calculated:
   if spell_id == 'eldritch_blast':
       cursor.execute("""
           SELECT 1 FROM warlock_invocations
           WHERE character_id=? AND invocation_id='agonizing_blast'
       """, (character_id,))
       if cursor.fetchone():
           damage += cha_modifier  # Add CHA to damage
   ```

3. **Add passive bonuses to character stats:**
   ```python
   # In game_engine_sqlite.py when loading character:
   # Check for Devil's Sight
   cursor.execute("""
       SELECT 1 FROM warlock_invocations
       WHERE character_id=? AND invocation_id='devils_sight'
   """, (character_id,))
   if cursor.fetchone():
       character['darkvision'] = max(character.get('darkvision', 0), 120)
   ```

### Phase 2: Active Abilities (Later)
- Eldritch Smite as action card
- Gift of the Protectors death prevention
- Requires more complex UI integration

---

## Quick Win Implementation (30 minutes)

**Goal:** Make Agonizing Blast and Armor of Shadows work NOW.

**Files to modify:**

1. `src/talekeeper/services/spellcasting_service.py` - Add CHA to Eldritch Blast damage
2. `src/talekeeper/ui/action_cards/action_panel.py` - Add at-will spells to spell list

**No new files needed - paste code into existing functions.**

---

## Testing Checklist

- [ ] Agonizing Blast adds CHA to damage
- [ ] Armor of Shadows grants Mage Armor spell (at-will)
- [ ] Devil's Sight shows in character description
- [ ] Eldritch Mind provides advantage on concentration saves
- [ ] Thirsting Blade grants Extra Attack
- [ ] At-will spells appear as action cards with unlimited uses
- [ ] Invocation effects persist across sessions
- [ ] Level-up correctly adds new invocations

---

**Next Steps:**
Choose implementation strategy and proceed with Phase 1 passive effects using existing code paths.
