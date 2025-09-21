# Safe Implementation Roadmap for Barbarian Enhancements

## Overview
This roadmap implements the three enhancement systems (Conditions, Action Economy, Subclass) in careful stages with testing gates and rollback points. Each stage builds on the previous without breaking existing functionality.

## Guiding Principles
1. **Never break working features** - All existing Barbarian features must continue working
2. **Test at every stage** - Each checkpoint includes validation tests
3. **Rollback capability** - Git commits at each stable point
4. **Incremental enhancement** - Add new systems alongside old, then migrate
5. **User-facing last** - Backend first, UI changes only after proven stable

---

## Phase 1: Condition System Foundation (Lowest Risk)
*The condition system is mostly new code with minimal integration points*

### Stage 1.1: Core Condition Infrastructure ✅ COMPLETE
**Goal**: Build condition system without touching existing code

- [x] Create `services/condition_manager.py` as new service
- [x] Add condition database tables (non-breaking additions)
- [x] Implement ConditionType enum with D&D 2024 conditions
- [x] Build ActiveCondition dataclass
- [x] Create ConditionEffects mapping

**Testing Checkpoint 1.1**:
```python
# test/services/test_condition_manager.py
def test_condition_manager_standalone():
    """Test condition system in isolation"""
    # Apply conditions
    # Check mechanical effects
    # Verify duration tracking
    # Test save mechanics
```

**Rollback Point**: Delete new files if issues arise

### Stage 1.2: Incapacitated Condition Integration ✅ COMPLETE
**Goal**: Connect Danger Sense to formal condition system

- [x] Add `has_incapacitating_condition()` method to condition_manager
- [x] Create wrapper in `barbarian_abilities.py`:
  ```python
  def check_danger_sense_with_conditions(character_id):
      # Keep existing check
      if not self.has_feature(character_id, "Danger Sense"):
          return False

      # Add new condition check
      from services.condition_manager import condition_manager
      if condition_manager.has_incapacitating_condition(character_id):
          return False

      return True
  ```
- [x] Update `encounter_panel.py` to use new check (keep old as fallback)

**Testing Checkpoint 1.2**:
```bash
# Run existing Barbarian tests - must all still pass
cd test && python -m pytest services/test_barbarian_abilities.py -v

# New condition integration test
python test_danger_sense_conditions.py
```

### Stage 1.3: Condition UI Display (Read-Only) ✅ COMPLETE
**Goal**: Show conditions without affecting gameplay

- [x] Add condition display to character sheet (informational only)
- [x] Create condition icons/indicators
- [x] Add tooltips showing condition effects
- [x] Log panel shows condition applied/removed messages

**Testing Checkpoint 1.3**:
- [ ] Visual inspection - conditions display correctly
- [ ] Apply test conditions via debug command
- [ ] Verify no impact on existing combat flow

### Stage 1.4: Full Condition Integration ✅ COMPLETE
**Goal**: Conditions affect combat mechanics

- [x] Hook conditions into advantage system
- [x] Apply movement restrictions from conditions
- [x] Integrate with action economy (blocks actions when incapacitated)
- [x] Add condition saves at turn start/end

**Testing Checkpoint 1.4**: ✅ PASSED (2024-09-21)
```bash
# Full combat simulation with conditions
python test/test_stage_1_4_integration.py  # ✅ All tests passing

# Regression test - vanilla Barbarian combat
python test/test_barbarian_combat_original.py
```

**✅ PHASE 1 COMPLETE (2024-09-21)**:
- All existing Barbarian features working
- Danger Sense correctly checks incapacitated
- Conditions display and mechanically function
- Git tag: `v1.0-conditions-complete`

**📋 SCALABLE ARCHITECTURE IMPLEMENTED (2024-09-21)**:
- Modular subclass directory structure for 44+ subclasses
- SubclassRegistry with lazy loading and caching
- Enhanced feature system with types and action costs
- Champion Fighter implemented as architecture test case
- Ready to scale across 11 classes efficiently
- See: `docs/SCALABLE_SUBCLASS_ARCHITECTURE.md`

---

## Phase 2: Subclass Architecture (Medium Risk)
*Enhances existing SubclassManager without breaking current Berserker*

### Stage 2.1: Enhanced Subclass Definitions ✅ COMPLETE
**Goal**: Create new subclass system alongside existing

- [x] Create `services/enhanced_subclass_manager.py` (new file)
- [x] Define SubclassFeature and SubclassDefinition classes
- [x] Implement Berserker with new structure
- [x] Add feature type handlers (passive, activated, triggered, reaction)

**Testing Checkpoint 2.1**: ✅ PASSED (2024-09-21)
```bash
python test/test_stage_2_1_subclass_definitions.py  # ✅ All tests passing
```

### Stage 2.2: Berserker Feature Migration ✅ COMPLETE
**Goal**: Migrate Berserker features to new system

- [x] Implement Mindless Rage with condition immunity
- [x] Create Retaliation reaction handler
- [x] Add Intimidating Presence as activated feature
- [x] Keep existing Berserker code as fallback

**Testing Checkpoint 2.2**: ✅ PASSED (2024-09-21)
```bash
# Test new Berserker features
python test/test_stage_2_2_berserker_migration.py  # ✅ All tests passing
```

### Stage 2.3: UI Integration for Subclass Features 🎨 Visual Only
**Goal**: Display subclass features in UI

- [ ] Add subclass feature panel to character sheet
- [ ] Show feature availability indicators
- [ ] Display resource tracking (uses remaining)
- [ ] Add feature tooltips with descriptions

**Testing Checkpoint 2.3**:
- [ ] Visual test - all Berserker features display
- [ ] Verify feature states update correctly
- [ ] Check resource tracking displays

### Stage 2.4: Feature Activation System 🔄 Careful
**Goal**: Hook features into action system

- [ ] Connect Retaliation to reaction system
- [ ] Implement Intimidating Presence action
- [ ] Add Mindless Rage automatic triggers
- [ ] Integrate with action cards

**Testing Checkpoint 2.4**:
```python
# Full Berserker combat test
def test_berserker_complete():
    # Test Mindless Rage immunity
    # Test Retaliation reaction
    # Test Intimidating Presence
    # Verify all base Barbarian features still work
```

**✅ PHASE 2 COMPLETE GATE**:
- Berserker fully implemented with all features
- Original Barbarian features intact
- Subclass system ready for other subclasses
- Git tag: `v2.0-subclass-complete`

---

## Phase 3: Action Economy Integration (Highest Risk)
*Most complex - touches core combat flow*

### Stage 3.1: Action Registry System ✅ New Addition
**Goal**: Create action registry without modifying combat

- [ ] Create `services/action_registry.py`
- [ ] Define ClassActionDefinition structure
- [ ] Register all Barbarian actions (Rage, Reckless, Brutal Strike)
- [ ] Build validation system for action prerequisites

**Testing Checkpoint 3.1**:
```python
def test_action_registry():
    """Test registry in isolation"""
    # Register Barbarian actions
    # Validate action definitions
    # Test prerequisite checking
```

### Stage 3.2: Economy Tracking Enhancement 📊 Parallel Tracking
**Goal**: Track action usage alongside existing system

- [ ] Extend ActionEconomyState for class actions
- [ ] Add action usage logging
- [ ] Create resource consumption tracking
- [ ] Build duration management for effects

**Testing Checkpoint 3.2**:
```bash
# Verify tracking without breaking combat
python test/test_action_tracking.py

# Existing combat must still work
python test/test_combat_original.py
```

### Stage 3.3: Action Validation Layer 🛡️ Safety Layer
**Goal**: Add validation without blocking existing actions

- [ ] Implement `can_use_class_action()` checks
- [ ] Add warning logs for invalid actions (don't block yet)
- [ ] Create action availability calculator
- [ ] Build feedback system for unavailable actions

**Testing Checkpoint 3.3**:
- [ ] Run combat with validation warnings
- [ ] Verify no actions are incorrectly blocked
- [ ] Check warning accuracy

### Stage 3.4: UI Action Card Integration 🎯 Visual First
**Goal**: Update action cards based on economy

- [ ] Generate action cards from registry
- [ ] Show availability based on economy state
- [ ] Display resource costs on cards
- [ ] Add disabled states with reasons

**Testing Checkpoint 3.4**:
- [ ] Visual test - cards show correct states
- [ ] Verify Rage uses bonus action
- [ ] Check Brutal Strike availability with Reckless
- [ ] Ensure Retaliation shows reaction cost

### Stage 3.5: Full Economy Enforcement 🚦 Final Integration
**Goal**: Enforce action economy rules

- [ ] Enable action blocking for invalid attempts
- [ ] Consume resources on action use
- [ ] Update economy state after actions
- [ ] Integrate with combat flow

**Testing Checkpoint 3.5**:
```python
def test_full_action_economy():
    # Test Rage consumes bonus action
    # Verify can't use two bonus actions
    # Check reaction usage and reset
    # Validate resource consumption
    # Full combat with all rules enforced
```

**✅ PHASE 3 COMPLETE GATE**:
- Full action economy working
- All Barbarian features integrated
- No regression in existing features
- Git tag: `v3.0-action-economy-complete`

---

## Final Integration Phase

### Stage 4.1: System Integration Testing 🔬
- [ ] Run comprehensive test suite
- [ ] Test all three systems together
- [ ] Verify Barbarian levels 1-20
- [ ] Test multiclass scenarios
- [ ] Performance testing

### Stage 4.2: Polish and Optimization ✨
- [ ] Optimize database queries
- [ ] Improve UI responsiveness
- [ ] Add configuration options
- [ ] Create debug commands

### Stage 4.3: Documentation and Release 📚
- [ ] Update CLAUDE.md with new systems
- [ ] Create feature documentation
- [ ] Add example usage code
- [ ] Release notes

---

## Emergency Procedures

### Rollback Plan
If any stage fails critically:
1. `git stash` current changes
2. `git checkout <last-stable-tag>`
3. Identify issue in isolated test
4. Fix and retry stage
5. Never proceed to next stage with failures

### Testing Commands Quick Reference
```bash
# Quick sanity check
python test/test_barbarian_sanity.py

# Full regression suite
python test/run_barbarian_regression.py

# Specific system tests
python test/test_conditions_only.py
python test/test_subclass_only.py
python test/test_action_economy_only.py

# Integration test
python test/test_barbarian_complete.py
```

### Safe Development Pattern
```python
# Always use feature flags for new code
if settings.USE_ENHANCED_CONDITIONS:
    # New condition system
    return condition_manager.check_incapacitated(character_id)
else:
    # Original implementation
    return self.check_old_incapacitated(character_id)
```

---

## Success Metrics
Each phase is successful when:
1. ✅ All existing tests pass
2. ✅ New feature tests pass
3. ✅ No performance degradation
4. ✅ UI remains responsive
5. ✅ Can play full combat encounter
6. ✅ Rollback is still possible

## Recommended Order
1. **Start with Conditions** (Phase 1) - Lowest risk, mostly additive
2. **Then Subclass** (Phase 2) - Enhances existing system
3. **Finally Action Economy** (Phase 3) - Most complex, touches core combat

## Time Estimates
- Phase 1 (Conditions): 2-3 days
- Phase 2 (Subclass): 3-4 days
- Phase 3 (Action Economy): 4-5 days
- Integration & Testing: 2-3 days
- **Total: 11-15 days** for full implementation

This staged approach ensures we never lose functionality and can always rollback to a working state!