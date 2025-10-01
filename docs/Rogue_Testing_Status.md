# Rogue Class Testing Status & Implementation Gaps

**Last Updated:** October 1, 2025
**Status:** Partial Implementation - UI Cards Complete, Integration Gaps Remain

---

## Test Coverage Summary

### Completed Tests

#### 1. Basic Validation Tests
**File:** [test/test_rogue_validation.py](../test/test_rogue_validation.py)
**Status:** PASSING (6/6 tests)

- Service import verification
- Sneak Attack dice scaling (levels 1-20)
- Weapon eligibility (finesse/ranged detection)
- WeaponAttackService integration
- ActionType definitions
- Feature definitions completeness

#### 2. Unit Tests (Service Layer)
**File:** [test/services/test_rogue_abilities.py](../test/services/test_rogue_abilities.py)
**Status:** PASSING (All tests)

- Rogue level detection
- Sneak Attack dice calculation
- Resource management (level-based)
- Cunning Action mechanics
- Steady Aim mechanics
- Uncanny Dodge damage reduction
- Reliable Talent (minimum roll 10)
- Stroke of Luck (failed roll -> 20)
- Rest resource restoration

#### 3. UI Action Card Tests
**File:** [test/test_rogue_ui_action_cards.py](../test/test_rogue_ui_action_cards.py)
**Status:** PASSING (12/12 tests)

- Cunning Action cards (level 2+)
- Steady Aim card (level 3+)
- Cunning Strike cards (level 5+)
- Uncanny Dodge card (level 5+)
- Devious Strikes cards (level 14+)
- Stroke of Luck card (level 20+)
- Card generation scaling by level
- Action usage simulation
- Card visibility after resource depletion

---

## Implementation Status

### Backend Services

#### RogueAbilitiesService
**File:** [services/rogue_abilities.py](../services/rogue_abilities.py)
**Status:** IMPLEMENTED (518 lines)

**Implemented:**
- Level detection and resource management
- Sneak Attack damage calculation
- Cunning Action (Dash, Disengage, Hide)
- Steady Aim (advantage + movement restriction)
- Uncanny Dodge (halve damage)
- Evasion (Dex save damage modification)
- Reliable Talent (minimum skill roll 10)
- Stroke of Luck (turn failed roll to 20)
- Rest resource restoration

**Working Methods:**
```python
get_rogue_level(character_id)
calculate_sneak_attack_damage(character_id)
check_sneak_attack_eligibility(character_id, target_id, context)
use_cunning_action(character_id, action_type)
use_steady_aim(character_id)
use_uncanny_dodge(character_id, incoming_damage)
apply_evasion(character_id, save_result)
apply_reliable_talent(character_id, skill_roll, skill_name)
use_stroke_of_luck(character_id, original_roll)
rest_rogue_resources(character_id, rest_type)
```

### UI Action Cards

#### Action Card Generation
**File:** [action_cards/action_panel.py](../action_cards/action_panel.py)
**Lines:** 654-743
**Status:** IMPLEMENTED

**Action Types Defined:**
- CUNNING_DASH, CUNNING_DISENGAGE, CUNNING_HIDE (level 2+)
- STEADY_AIM (level 3+)
- UNCANNY_DODGE (level 5+)
- CUNNING_STRIKE_POISON, TRIP, WITHDRAW (level 5+)
- CUNNING_STRIKE_DAZE, KNOCK_OUT, OBSCURE (level 14+)
- STROKE_OF_LUCK (level 20+)

**Card Generation Logic:**
- Cards appear based on character level
- Feature data integration via `_get_feature_data()`
- Signal connections to `_trigger_rogue_action()`
- Resource-based visibility (e.g., Stroke of Luck uses)

### Combat Integration

#### Weapon Attack Service
**File:** [services/weapon_attack_service.py](../services/weapon_attack_service.py)
**Status:** HAS INTEGRATION POINT

**Integration Method:**
```python
_apply_sneak_attack_if_eligible(character_id, weapon, target_id, context)
```

**Verified:** Method exists (test_rogue_validation.py confirms)

---

## Known Gaps & WIP Items

### 1. Cunning Strike System
**Priority:** HIGH
**Status:** PARTIAL IMPLEMENTATION

**Implemented:**
- UI cards for all 6 Cunning Strike effects
- Cost information displayed on cards
- Action type definitions

**Missing:**
- Dice cost deduction from Sneak Attack damage
- Save DC calculation and enforcement
- Condition application (Poisoned, Prone, Blinded, Unconscious, Dazed)
- Multiple effect stacking (level 11+)
- Poisoner's Kit requirement check for Poison effect
- Integration with combat damage flow

**Test Coverage:** NONE
**Needs:** `test/test_rogue_cunning_strike.py`

**Complexity:** High - Variable resource costs (1d6-6d6) with combat integration

---

### 2. Sneak Attack Automatic Trigger
**Priority:** HIGH
**Status:** BACKEND READY, COMBAT INTEGRATION INCOMPLETE

**Implemented:**
- Damage calculation (scales 1d6-10d6)
- Weapon eligibility check (finesse/ranged)
- Eligibility logic (advantage or ally proximity)
- Integration point in WeaponAttackService

**Missing:**
- Actual combat damage application
- Once-per-turn enforcement tracking
- Visual feedback when Sneak Attack triggers
- Log messages for why Sneak Attack did/didn't apply
- Ally proximity detection (requires combat positioning system)

**Test Coverage:** Unit tests only, no integration tests
**Needs:** `test/test_rogue_sneak_attack_combat.py`

**Example Test Scenarios:**
```python
def test_sneak_attack_with_advantage():
    # Rogue with advantage should add sneak attack damage

def test_sneak_attack_with_ally_nearby():
    # Ally within 5ft should trigger sneak attack

def test_sneak_attack_once_per_turn():
    # Multiple attacks should only apply sneak attack once

def test_sneak_attack_with_disadvantage_fails():
    # Disadvantage should prevent sneak attack even with ally
```

---

### 3. Action Economy Integration
**Priority:** MEDIUM
**Status:** PARTIALLY IMPLEMENTED

**Implemented:**
- Cunning Action cards marked as bonus actions
- Steady Aim bonus action card
- Uncanny Dodge reaction card

**Missing:**
- Bonus action availability checking before use
- Reaction availability checking (Uncanny Dodge)
- Turn-based reset of per-turn abilities
- Movement tracking for Steady Aim restriction
- Visual indicators for action economy state

**Test Coverage:** NONE
**Needs:** Integration with existing action economy system

**Related:** [docs/ACTION_ECONOMY_SPECIFICATION.md](ACTION_ECONOMY_SPECIFICATION.md)

---

### 4. Subclass Implementation: Arcane Trickster
**Priority:** MEDIUM
**Status:** STUB ONLY

**Implemented:**
- Subclass registered in database seeds
- Subclass selection at level 3

**Missing:**
- Spellcasting integration (Wizard spell list)
- Mage Hand Legerdemain mechanics
- Magical Ambush (advantage on spell saves when hidden)
- Versatile Trickster (Mage Hand grants attack advantage)
- Spell slot management UI
- Cantrip action cards

**Test Coverage:** NONE
**Needs:** Full subclass implementation

**Complexity:** HIGH - Requires spell system integration

**Reference:** [Rogue_subclass.md](Rogue_subclass.md)

---

### 5. Expertise System
**Priority:** ✅ COMPLETE
**Status:** FULLY FUNCTIONAL

**Implemented:**
- ✅ Level-based grants (2 at level 1, 4 at level 6) - [services/level_up.py:431-504](../services/level_up.py#L431-L504)
- ✅ Database tracking in `rogue_features.expertise_count` and `character_proficiencies`
- ✅ Proficiency system integration - [services/proficiency_system.py:220-248](../services/proficiency_system.py#L220-L248)
- ✅ Character sheet display with star (★) indicator - [character_sheet/character_panel.py:1430-1435](../character_sheet/character_panel.py#L1430-L1435)
- ✅ Double proficiency bonus calculation (2x prof bonus)
- ✅ Feature description updates on level up
- ✅ **Character creation UI** - [encounter_pane/encounter_panel.py:2021-2272](../encounter_pane/encounter_panel.py#L2021-L2272)
  - Checkbox interface for selecting 2 expertise skills
  - Enforces 2 skill limit with counter "Selected: 0 / 2"
  - Dynamically updates based on proficient skills
  - Only shows skills character is proficient in
  - `_on_expertise_skill_toggled()` handler stores selections
- ✅ **Level-up UI (Level 6)** - [encounter_pane/town_encounter.py:311-330](../encounter_pane/town_encounter.py#L311-L330)
  - Shows expertise selection frame when Rogue levels 5→6
  - Checkbox interface for selecting 2 additional expertise skills
  - Excludes already-expertised skills from selection
  - Enforces 2 skill limit with validation
  - Stores selections in `character_proficiencies` with type `skill_expertise`
  - Shows in advancement summary before confirmation

**Test Coverage:** 7/8 tests passing
**File:** [test/test_rogue_expertise_progression.py](../test/test_rogue_expertise_progression.py)

**How It Works:**
1. **Character Creation (Level 1):**
   - Rogue creation shows "Expertise" section below class skills
   - Checkboxes appear for all proficient skills (class + background + species)
   - Player selects exactly 2 skills (enforced by UI)
   - Stored in `character_creation_data['rogue_features']['expertise_skills']`
   - Saved to `character_proficiencies` with type `skill_expertise`

2. **Level 6 Advancement:**
   - `level_up.py` updates `expertise_count` to 4
   - Feature description changes to "4 skills"
   - ⚠️ No UI prompt for selecting 2 additional skills yet

3. **Display & Calculation:**
   - Character sheet reads `skill_expertise` proficiencies
   - Shows ★ next to expertise skills
   - Applies double proficiency bonus (e.g., +3 prof → +6 expertise)

---

### 6. Stealth & Hide Mechanics
**Priority:** LOW-MEDIUM
**Status:** ACTION CARD ONLY

**Implemented:**
- Cunning Hide action card (bonus action)

**Missing:**
- Stealth check mechanics
- Hidden condition tracking
- Advantage from being hidden
- Reveal/detection mechanics
- Integration with Steady Aim
- Magical Ambush (Arcane Trickster)

**Test Coverage:** NONE
**Dependencies:** Condition system, combat positioning

---

### 7. Reliable Talent Integration
**Priority:** LOW
**Status:** BACKEND ONLY

**Implemented:**
- Service method `apply_reliable_talent()`
- Logic for minimum roll of 10

**Missing:**
- Skill check system integration
- Automatic application on rolls
- Proficiency detection per skill
- UI feedback when Reliable Talent applies

**Test Coverage:** Unit test only, no integration

---

### 8. Evasion Integration
**Priority:** LOW
**Status:** BACKEND ONLY

**Implemented:**
- Service method `apply_evasion()`
- Dex save damage modification logic

**Missing:**
- Saving throw system integration
- Automatic application on Dex saves
- Incapacitated condition check
- UI feedback when Evasion applies

**Test Coverage:** Unit test only, no integration

---

### 9. Level 15+ Features
**Priority:** LOW
**Status:** DATABASE FLAGS ONLY

**Features:**
- Slippery Mind (Wisdom/Charisma save proficiency)
- Elusive (no advantage against rogue)
- Epic Boon (level 19)

**Missing:** Complete implementation and testing

---

## Test Scenarios Needed

### High Priority

#### Cunning Strike Combat Flow
```python
# test/test_rogue_cunning_strike_combat.py

def test_cunning_strike_poison_reduces_damage():
    # Rogue level 5, 3d6 sneak attack
    # Use Poison Strike (cost 1d6)
    # Verify: 2d6 damage dealt, target gets Con save, Poisoned on fail

def test_cunning_strike_trip():
    # Use Trip Strike (cost 1d6)
    # Verify: Target gets Dex save, Prone on fail

def test_cunning_strike_withdraw():
    # Use Withdraw Strike (cost 1d6)
    # Verify: Rogue moves half speed without opportunity attacks

def test_multiple_cunning_strikes_level_11():
    # Rogue level 11, 6d6 sneak attack
    # Use Trip (1d6) + Poison (1d6)
    # Verify: 4d6 damage, both effects applied

def test_knock_out_strike_high_cost():
    # Rogue level 20, 10d6 sneak attack
    # Use Knock Out (6d6)
    # Verify: 4d6 damage, target Unconscious on failed Con save

def test_cunning_strike_without_sneak_attack():
    # Attack without sneak attack eligibility
    # Verify: Cunning Strike cards disabled/grayed out

def test_poison_strike_without_poisoners_kit():
    # Attempt Poison Strike without Poisoner's Kit
    # Verify: Error message, action fails
```

#### Sneak Attack Combat Integration
```python
# test/test_rogue_sneak_attack_integration.py

def test_sneak_attack_triggers_with_advantage():
    # Rogue level 5 with advantage on attack
    # Verify: 3d6 sneak attack damage added

def test_sneak_attack_ally_proximity():
    # Ally within 5ft of target
    # Verify: Sneak attack applies without advantage

def test_sneak_attack_once_per_turn():
    # Extra Attack or Nick mastery
    # Verify: Only first attack gets sneak attack

def test_sneak_attack_with_disadvantage_blocked():
    # Disadvantage even with ally nearby
    # Verify: No sneak attack damage

def test_sneak_attack_non_finesse_weapon():
    # Attack with greataxe
    # Verify: No sneak attack

def test_sneak_attack_visual_feedback():
    # Successful sneak attack
    # Verify: Log message shows sneak attack damage
```

### Medium Priority

#### Action Economy Integration
```python
# test/test_rogue_action_economy.py

def test_cunning_action_consumes_bonus_action():
    # Use Cunning Dash
    # Verify: Bonus action consumed, other bonus actions unavailable

def test_steady_aim_prevents_movement():
    # Use Steady Aim
    # Verify: Speed = 0, cannot move this turn

def test_uncanny_dodge_consumes_reaction():
    # Use Uncanny Dodge
    # Verify: Reaction consumed, cannot use opportunity attacks

def test_cunning_action_and_nick_mastery_conflict():
    # Try to use both Cunning Action and Nick in same turn
    # Verify: Only one available
```

#### Expertise Skill Checks
```python
# test/test_rogue_expertise.py

def test_expertise_selection_level_1():
    # Rogue level 1
    # Verify: Can select 2 skills for expertise

def test_expertise_selection_level_6():
    # Rogue level 6
    # Verify: Can select 2 additional skills (4 total)

def test_expertise_skill_check_bonus():
    # Expertise in Stealth, +3 proficiency
    # Verify: +6 bonus applied to Stealth check

def test_reliable_talent_with_expertise():
    # Level 7+ rogue, expertise in Investigation
    # Roll 5 on Investigation check
    # Verify: Becomes 10, then add expertise bonus
```

### Low Priority

#### Evasion & Slippery Mind
```python
# test/test_rogue_defensive_features.py

def test_evasion_success_no_damage():
    # Dex save vs Fireball, success
    # Verify: 0 damage taken (not half)

def test_evasion_failure_half_damage():
    # Dex save vs Fireball, failure
    # Verify: Half damage taken (not full)

def test_slippery_mind_wisdom_save():
    # Level 15+ rogue, Wisdom save
    # Verify: Proficiency bonus applied

def test_elusive_blocks_advantage():
    # Enemy tries to attack with advantage
    # Verify: Advantage negated (unless rogue incapacitated)
```

---

## TODO List

### Immediate (High Priority)

- [ ] **Implement Cunning Strike resource system**
  - [ ] Dice cost deduction logic
  - [ ] Save DC calculation (8 + DEX + prof)
  - [ ] Condition application integration
  - [ ] Poisoner's Kit requirement check
  - [ ] Multiple effect stacking (level 11+)

- [ ] **Complete Sneak Attack combat integration**
  - [ ] Ally proximity detection
  - [ ] Once-per-turn enforcement
  - [ ] Visual feedback in combat log
  - [ ] Integration with WeaponAttackService damage flow

- [ ] **Action economy integration**
  - [ ] Bonus action availability checking
  - [ ] Reaction availability checking
  - [ ] Turn-based reset of per-turn abilities
  - [ ] Movement tracking for Steady Aim

### Short-Term (Medium Priority)

- [ ] **Expertise system UI**
  - [ ] Skill selection interface (level 1)
  - [ ] Additional selection (level 6)
  - [ ] Skill check bonus application
  - [ ] Character sheet display

- [ ] **Stealth & Hide mechanics**
  - [ ] Stealth check integration
  - [ ] Hidden condition tracking
  - [ ] Advantage from hidden state
  - [ ] Detection mechanics

- [ ] **Arcane Trickster subclass**
  - [ ] Spellcasting integration
  - [ ] Mage Hand Legerdemain
  - [ ] Magical Ambush
  - [ ] Versatile Trickster

### Long-Term (Low Priority)

- [ ] **Evasion integration**
  - [ ] Saving throw system hook
  - [ ] Automatic application
  - [ ] UI feedback

- [ ] **Reliable Talent integration**
  - [ ] Skill check system hook
  - [ ] Automatic application
  - [ ] UI feedback

- [ ] **Level 15+ features**
  - [ ] Slippery Mind (save proficiencies)
  - [ ] Elusive (no advantage)
  - [ ] Epic Boon selection

- [ ] **Additional subclasses**
  - [ ] Thief
  - [ ] Assassin
  - [ ] Other PHB subclasses

---

## UI Testing Checklist

### Visual Verification Needed

- [ ] Action cards appear at correct levels
- [ ] Card icons and descriptions are clear
- [ ] Resource costs displayed on Cunning Strike cards
- [ ] Cards gray out when resources depleted
- [ ] Cards disappear when not applicable
- [ ] Hover tooltips show full feature descriptions
- [ ] Combat log messages for each ability use
- [ ] Error messages for invalid actions

### Interactive Testing Scenarios

1. **Create level 2 Rogue**
   - Verify 3 Cunning Action cards appear
   - Use each Cunning Action, verify bonus action consumed

2. **Create level 5 Rogue**
   - Verify Cunning Strike cards appear
   - Attack with Sneak Attack eligible weapon
   - Attempt to use Cunning Strike options
   - Verify Uncanny Dodge card appears

3. **Create level 14 Rogue**
   - Verify Devious Strikes cards appear
   - Check cost information (2d6, 3d6, 6d6)

4. **Create level 20 Rogue**
   - Verify Stroke of Luck card appears
   - Use Stroke of Luck, verify card disappears
   - Rest, verify card reappears

---

## Performance Benchmarks

### Target Metrics
- Sneak Attack calculation: < 50ms
- Action card generation: < 100ms
- Cunning Strike application: < 150ms
- Resource updates: < 200ms

### Current Status
- NOT BENCHMARKED

### Needs Performance Testing
- [ ] Sneak Attack damage calculation
- [ ] Cunning Strike with multiple effects
- [ ] Action card refresh after resource use
- [ ] Large combat with multiple rogues

---

## Documentation Updates Needed

- [ ] Update CLAUDE.md with Rogue testing commands
- [ ] Add Cunning Strike usage examples to Rogue_Class.md
- [ ] Document action economy interactions
- [ ] Add Sneak Attack trigger conditions to combat docs
- [ ] Create Rogue playtesting guide

---

## Integration Dependencies

### Systems Required for Full Functionality

1. **Combat Positioning System** (for ally proximity)
2. **Condition Manager** (for Cunning Strike conditions)
3. **Saving Throw System** (for Evasion, Cunning Strike)
4. **Action Economy System** (for bonus action/reaction management)
5. **Skill Check System** (for Expertise, Reliable Talent)
6. **Spell System** (for Arcane Trickster)

### Current Blockers

- **Ally Proximity Detection:** No combat positioning system implemented
- **Condition Application:** Cunning Strike can't apply Poisoned/Prone/etc.
- **Save DCs:** No unified save system for Cunning Strike effects

---

## Test Execution Commands

```bash
# Run all Rogue tests
python test/test_rogue_validation.py
python test/services/test_rogue_abilities.py
python test/test_rogue_ui_action_cards.py
python test/test_rogue_level_progression.py

# Run new tests (once created)
python test/test_rogue_sneak_attack_integration.py
python test/test_rogue_cunning_strike_combat.py
python test/test_rogue_action_economy.py
python test/test_rogue_expertise.py

# Run regression suite (quick)
python tests/run_regression_tests.py --quick

# Add Rogue to regression suite
# Edit tests/run_regression_tests.py to include rogue tests
```

---

## Conclusion

**Current State:** Rogue class has solid backend foundation and UI action cards, but lacks critical combat integration for signature features (Sneak Attack, Cunning Strike).

**Playable:** Partially - Basic abilities work, but Sneak Attack and Cunning Strike (the class's core features) are not fully functional in combat.

**Recommended Next Steps:**
1. Implement Cunning Strike combat integration (highest impact)
2. Complete Sneak Attack automatic triggering
3. Add action economy enforcement
4. Build comprehensive combat integration tests

**Estimated Completion:** 3-5 days for core combat features, 7-10 days for full polish including subclasses.
