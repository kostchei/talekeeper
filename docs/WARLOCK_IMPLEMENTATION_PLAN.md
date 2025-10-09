# Warlock Implementation Plan - SRD 2024 Complete

**Date:** 2025-10-09
**Status:** PLANNING

---

## Current State Analysis

### Spells in Database vs SRD 2024

**Current Coverage: 26/78 spells (33%)**

#### Cantrips (Level 0) - **7/7 COMPLETE**
- [x] Chill Touch
- [x] Eldritch Blast
- [x] Mage Hand
- [x] Minor Illusion
- [x] Poison Spray
- [x] Prestidigitation
- [x] True Strike

#### Level 1 - **14/14 COMPLETE**
- [x] Bane
- [x] Charm Person
- [x] Comprehend Languages
- [x] Detect Magic
- [x] Expeditious Retreat
- [x] Hellish Rebuke
- [x] Hex
- [x] Hideous Laughter (Tasha's)
- [x] Illusory Script
- [x] Protection from Evil and Good
- [x] Speak with Animals
- [x] Unseen Servant
- [x] Burning Hands (in DB, but NOT in SRD Warlock list - remove?)
- [x] Command (in DB, but NOT in SRD Warlock list - remove?)

#### Level 2 - **0/10 MISSING**
- [ ] Darkness
- [ ] Enthrall
- [ ] Hold Person
- [ ] Invisibility
- [ ] Mind Spike
- [ ] Mirror Image
- [ ] Misty Step
- [ ] Ray of Enfeeblement
- [ ] Spider Climb
- [ ] Suggestion

#### Level 3 - **3/10 MISSING 7**
- [x] Counterspell (need to verify in DB)
- [x] Dispel Magic
- [ ] Fear
- [ ] Fly
- [ ] Gaseous Form
- [ ] Hypnotic Pattern
- [x] Magic Circle
- [ ] Major Image
- [x] Remove Curse
- [ ] Tongues
- [ ] Vampiric Touch

#### Level 4 - **1/5 MISSING 4**
- [x] Banishment
- [ ] Blight
- [ ] Charm Monster
- [ ] Dimension Door
- [ ] Hallucinatory Terrain

#### Level 5 - **1/7 MISSING 6**
- [ ] Contact Other Plane
- [ ] Dream
- [x] Geas (need to verify)
- [ ] Hold Monster
- [ ] Mislead
- [ ] Planar Binding
- [ ] Scrying
- [ ] Teleportation Circle

#### Level 6 - **0/4 MISSING 4**
- [ ] Circle of Death
- [ ] Create Undead
- [ ] Eyebite
- [ ] True Seeing

#### Level 7 - **0/4 MISSING 4**
- [ ] Etherealness
- [ ] Finger of Death
- [ ] Forcecage
- [ ] Plane Shift

#### Level 8 - **0/5 MISSING 5**
- [ ] Befuddlement
- [ ] Demiplane
- [ ] Dominate Monster
- [ ] Glibness
- [ ] Power Word Stun

#### Level 9 - **0/7 MISSING 7**
- [ ] Astral Projection
- [ ] Foresight
- [ ] Gate
- [ ] Imprisonment
- [ ] Power Word Kill
- [ ] True Polymorph
- [ ] Weird

**Missing: 52 spells (levels 2-9)**

---

### Invocations in Database vs SRD 2024

**Current Coverage: 14/28 invocations (50%)**

#### Implemented
1. [x] Agonizing Blast
2. [x] Armor of Shadows
3. [x] Ascendant Step
4. [x] Devil's Sight
5. [x] Devouring Blade
6. [x] Eldritch Mind
7. [x] Eldritch Smite
8. [x] Fiendish Vigor
9. [x] Gift of the Depths
10. [x] Gift of the Protectors
11. [x] Investment of the Chain Master
12. [x] Lessons of the First Ones
13. [x] Thirsting Blade
14. [x] Visions of Distant Realms

#### Missing (14 invocations)
15. [ ] Eldritch Spear (Prereq: Level 2+, damage cantrip; Range +30*level)
16. [ ] Gaze of Two Minds (Prereq: Level 5+; Perceive through willing creature)
17. [ ] Lifedrinker (Prereq: Level 9+, Pact Blade; +1d6 damage, heal with HD)
18. [ ] Mask of Many Faces (Prereq: Level 2+; Disguise Self at will)
19. [ ] Master of Myriad Forms (Prereq: Level 5+; Alter Self at will)
20. [ ] Misty Visions (Prereq: Level 2+; Silent Image at will)
21. [ ] One with Shadows (Prereq: Level 5+; Invisibility in dim light/darkness)
22. [ ] Otherworldly Leap (Prereq: Level 2+; Jump at will)
23. [ ] Pact of the Blade (PACT BOON - special)
24. [ ] Pact of the Chain (PACT BOON - special)
25. [ ] Pact of the Tome (PACT BOON - special)
26. [ ] Repelling Blast (Prereq: Level 2+, attack cantrip; Push 10ft)
27. [ ] Whispers of the Grave (Prereq: Level 7+; Speak with Dead at will)
28. [ ] Witch Sight (Prereq: Level 15+; Truesight 30ft)

**Note:** Pact Boons (Blade/Chain/Tome) are technically invocations in 2024 rules

---

## Implementation Plan

### Phase 1: Complete Warlock Spell List (Priority: HIGH)

**Goal:** Add all 52 missing Warlock spells to database

#### Step 1.1: Add Missing Level 2 Spells (10 spells)
```sql
-- Migration: 033_warlock_spells_level_2.sql
INSERT INTO spells (id, name, level, school, ...) VALUES
('darkness', 'Darkness', 2, 'Evocation', ...),
('enthrall', 'Enthrall', 2, 'Enchantment', ...),
-- ... etc
```

#### Step 1.2: Add Missing Level 3 Spells (7 spells)
```sql
-- Migration: 034_warlock_spells_level_3.sql
-- Fear, Fly, Gaseous Form, Hypnotic Pattern, Major Image, Tongues, Vampiric Touch
```

#### Step 1.3: Add Missing Level 4 Spells (4 spells)
```sql
-- Migration: 035_warlock_spells_level_4.sql
-- Blight, Charm Monster, Dimension Door, Hallucinatory Terrain
```

#### Step 1.4: Add Missing Level 5-9 Spells (31 spells)
```sql
-- Migration: 036_warlock_spells_level_5_9.sql
-- All high-level spells (5-9)
```

**Alternative Approach (Recommended):**
Create ONE comprehensive migration file that adds all 52 spells at once:
```sql
-- Migration: 033_warlock_complete_spell_list.sql
```

---

### Phase 2: Complete Eldritch Invocations (Priority: HIGH)

**Goal:** Add all 14 missing invocations

#### Step 2.1: Add Missing At-Will Spell Invocations (7 invocations)
These grant unlimited casting of specific spells:
- Eldritch Spear (cantrip modifier)
- Mask of Many Faces (Disguise Self)
- Master of Myriad Forms (Alter Self)
- Misty Visions (Silent Image)
- One with Shadows (Invisibility in dim light)
- Otherworldly Leap (Jump)
- Whispers of the Grave (Speak with Dead)

```sql
-- Migration: 037_warlock_invocations_at_will_spells.sql
INSERT INTO invocations (id, name, description, prerequisites, effect_type, effect_data) VALUES
('mask_of_many_faces', 'Mask of Many Faces', ..., '{"level": 2}', 'active', '{"spell": "disguise_self", "cost": "none"}'),
-- ... etc
```

#### Step 2.2: Add Missing Passive/Utility Invocations (4 invocations)
- Gaze of Two Minds (bonus action ability)
- Lifedrinker (Pact Blade damage boost)
- Repelling Blast (cantrip modifier)
- Witch Sight (Truesight)

```sql
-- Migration: 038_warlock_invocations_passive.sql
```

#### Step 2.3: Implement Pact Boons as Invocations (3 pact boons)
In D&D 2024, Pact Boons are actually **invocations** you choose at level 1 (not level 3 like in 5e).

**From SRD 2024:** Eldritch Invocations table shows "1" at level 1, and the three pacts are in the invocations list.

**Current System Issue:** We treat pact boons as a separate choice at level 3.

**Fix Needed:**
- Update invocations formula: `{"1":1, "2":3, ...}` (gain 1 at level 1, 2 more at level 2)
- Add pact boons to invocations table
- Update level-up to offer pact boon as first invocation choice at level 1

```sql
-- Migration: 039_pact_boons_as_invocations.sql
INSERT INTO invocations (id, name, description, prerequisites, effect_type, effect_data) VALUES
('pact_of_the_blade', 'Pact of the Blade', 'Conjure pact weapon as bonus action...', '{}', 'active', '{"pact": "blade"}'),
('pact_of_the_chain', 'Pact of the Chain', 'Cast Find Familiar...', '{}', 'active', '{"pact": "chain"}'),
('pact_of_the_tome', 'Pact of the Tome', 'Conjure Book of Shadows...', '{}', 'active', '{"pact": "tome"}');

-- Update formula
UPDATE ability_scaling_formulas
SET formula_data = '{"1":1,"2":3,"3":3,"4":3,"5":5,"6":5,...}'
WHERE formula_name = 'invocations_by_level';
```

---

### Phase 3: Add Invocation Abilities to Unified System (Priority: MEDIUM)

**Goal:** Ensure all invocations grant usable abilities

Add the 14 missing invocations as `class_abilities`:

```sql
-- Migration: 040_warlock_invocation_abilities_complete.sql
INSERT INTO class_abilities (ability_id, class_name, ability_name, description, level_gained, feature_type, usage_type, mechanics) VALUES

-- At-will spell invocations
('invocation_mask_of_many_faces', 'Warlock', 'Mask of Many Faces (Invocation)', 'Cast Disguise Self at will', 1, 'action', 'unlimited', '{"invocation_id":"mask_of_many_faces","spell":"disguise_self","cost":"none","requires_invocation":true}'),

-- Cantrip modifiers
('invocation_eldritch_spear', 'Warlock', 'Eldritch Spear (Invocation)', 'Increase cantrip range by 30*level', 1, 'passive', 'permanent', '{"invocation_id":"eldritch_spear","modifies":"damage_cantrip","range_bonus":"30*level","requires_invocation":true}'),

('invocation_repelling_blast', 'Warlock', 'Repelling Blast (Invocation)', 'Push target 10ft on cantrip hit', 1, 'passive', 'permanent', '{"invocation_id":"repelling_blast","modifies":"attack_cantrip","effect":"push","distance":10,"requires_invocation":true}'),

-- Special abilities
('invocation_lifedrinker', 'Warlock', 'Lifedrinker (Invocation)', 'Deal +1d6 damage, heal with Hit Die', 1, 'special', 'unlimited', '{"invocation_id":"lifedrinker","trigger":"pact_weapon_hit","damage":"1d6","damage_types":["necrotic","psychic","radiant"],"heal":"hit_die","requires":"pact_blade","requires_invocation":true}'),

('invocation_witch_sight', 'Warlock', 'Witch Sight (Invocation)', 'Truesight 30 feet', 1, 'passive', 'permanent', '{"invocation_id":"witch_sight","truesight":30,"requires_invocation":true}'),

-- ... etc for all 14
```

---

### Phase 4: Fix Pact Boon System (Priority: MEDIUM)

**Issue:** Current system treats pact boons as separate from invocations, chosen at level 3.
**SRD 2024:** Pact boons ARE invocations, chosen at level 1.

#### Changes Needed:

1. **Update Invocations Formula** in database:
```sql
-- Level 1 Warlocks get 1 invocation (typically a pact boon)
-- Level 2 Warlocks get 2 MORE (total 3)
UPDATE ability_scaling_formulas
SET formula_data = '{"1":1,"2":3,"3":3,"4":3,"5":5,...}'
WHERE formula_name = 'invocations_by_level';
```

2. **Remove Pact Boon Choice from Level 3** in `unified_level_up.py`:
```python
# DELETE THIS:
if new_level == 3:
    choices.append({
        "type": "pact_boon",
        "options": ["blade", "chain", "tome"],
        "level": 3
    })
```

3. **Filter Invocation Choices** to show pact boons first at level 1:
```python
# In UI or service layer
if level == 1 and invocations_count == 1:
    # Show only pact boons (blade, chain, tome)
    available_invocations = [inv for inv in all_invocations
                            if inv['id'] in ['pact_of_the_blade', 'pact_of_the_chain', 'pact_of_the_tome']]
```

---

### Phase 5: Character Creation Integration (Priority: LOW)

**Goal:** Ensure Warlock character creation follows 2024 rules

#### Level 1 Warlock Should Have:
- 2 cantrips (Eldritch Blast + 1)
- 2 spells prepared (Charm Person + Hex recommended)
- 1 invocation (Pact Boon: Blade, Chain, or Tome)
- 1 pact slot (level 1)

#### Update Character Creation Flow:
- Prompt for pact boon selection (as invocation choice)
- Prompt for 2 cantrips
- Prompt for 2 spells known
- Initialize `warlock_features` table with pact boon

---

## Implementation Order (Recommended)

### Immediate (Fixes for Leshan at Level 2)
1. ✅ Invocation selection at level-up - DONE
2. ✅ Spell selection at level-up - DONE
3. ✅ At-will casting for invocations - DONE (Armor of Shadows works)

### Short Term (Complete Spell List)
4. [ ] Migration 033: Add all 52 missing Warlock spells
5. [ ] Test spell selection UI with complete list

### Medium Term (Complete Invocations)
6. [ ] Migration 037-038: Add 14 missing invocations
7. [ ] Migration 040: Add invocation abilities to unified system
8. [ ] Test invocation selection with complete list

### Long Term (Fix Pact Boon System)
9. [ ] Migration 039: Convert pact boons to invocations
10. [ ] Update invocations formula (1 at level 1, 3 at level 2)
11. [ ] Update level-up service to remove level 3 pact boon choice
12. [ ] Update character creation to prompt for pact boon at level 1

---

## File Changes Required

### New Migrations
- `database/migrations/033_warlock_complete_spell_list.sql` (52 spells)
- `database/migrations/037_warlock_invocations_at_will_spells.sql` (7 invocations)
- `database/migrations/038_warlock_invocations_passive.sql` (4 invocations)
- `database/migrations/039_pact_boons_as_invocations.sql` (3 invocations + formula update)
- `database/migrations/040_warlock_invocation_abilities_complete.sql` (14 abilities)

### Code Changes
- `src/talekeeper/services/unified_level_up.py` - Remove level 3 pact boon, filter level 1 invocations
- Character creation service - Add pact boon prompt at level 1

### Documentation Updates
- `docs/WARLOCK_IMPLEMENTATION_PLAN.md` (this file)
- `docs/UNIFIED_CLASS_ABILITIES_IMPLEMENTATION_COMPLETE.md` - Update invocation count

---

## Testing Checklist

### Spell List Testing
- [ ] All 78 Warlock spells in database
- [ ] Spell selection UI shows correct spells by level
- [ ] Warlock can learn spells up to pact slot level
- [ ] Mystic Arcanum shows level 6-9 spells only

### Invocation Testing
- [ ] All 28 invocations in database
- [ ] Invocation selection respects prerequisites (level, pact, spell)
- [ ] At-will spell invocations create action cards
- [ ] Passive invocations apply effects (Devil's Sight, Witch Sight, etc.)
- [ ] Cantrip modifiers work (Agonizing Blast, Eldritch Spear, Repelling Blast)

### Pact Boon Testing
- [ ] Level 1 Warlock prompted for pact boon
- [ ] Pact boon counts as 1 invocation
- [ ] Level 2 Warlock gets 2 MORE invocations (total 3)
- [ ] Pact-dependent invocations only show when boon selected (Thirsting Blade, etc.)

### Level-Up Testing (Leshan Case)
- [ ] Level 1 → 2: Gain 2 invocations (total 3), 1 spell (total 3), 1 pact slot (2 slots total)
- [ ] Invocation abilities appear as action cards
- [ ] At-will spells work without consuming slots
- [ ] Spell selection shows level 0-1 spells only

---

## Estimated Effort

- **Phase 1 (Spells):** 4-6 hours (data entry, testing)
- **Phase 2 (Invocations):** 2-3 hours (data entry, testing)
- **Phase 3 (Abilities):** 1-2 hours (SQL generation)
- **Phase 4 (Pact Boon Fix):** 2-3 hours (code + migration)
- **Phase 5 (Character Creation):** 2-3 hours (UI integration)

**Total:** 11-17 hours

---

## Notes

- Many spells will be shared with other classes (Wizard, Sorcerer, Bard)
- Spell implementation may already exist, just need to add to `spell_class_lists`
- Invocation prerequisites need validation logic in `ElditchInvocationService`
- D&D 2024 rules differ from 5e: Pact Boons are now invocations chosen at level 1
- "Prepared spells" in 2024 Warlock terminology = "Spells known" in our system
