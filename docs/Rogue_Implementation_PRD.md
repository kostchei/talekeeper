# Rogue Class Implementation PRD
**Product Requirements Document**
**Version:** 1.0
**Date:** September 21, 2025
**Status:** Planning Phase

## Executive Summary

This PRD outlines the implementation strategy for the Rogue class in TaleKeeper, building upon the successful architectural patterns established by the Fighter and Barbarian implementations. The Rogue class presents unique technical challenges including complex Sneak Attack mechanics, Cunning Strike resource management, and sophisticated stealth/advantage tracking systems.

## Project Context & Analysis

### Current Implementation Status

**✅ Existing Foundation:**
- Database schema: `rogue_features` table with basic structure
- Feature definitions: Levels 1-2 partially defined in `core/feature_definitions.py:336-384`
- Class registration: Present in seeds and class selection systems
- Weapon mastery: Unlimited access already implemented (`WeaponAttackService`)
- Basic action cards: Infrastructure exists but Rogue-specific cards missing

**⚠️ Implementation Gaps:**
- **Backend Services**: No `RogueAbilitiesService` (critical dependency)
- **Feature System**: Only 2/20 levels implemented in feature definitions
- **Cunning Strike**: Complex resource system not implemented
- **Subclass System**: Arcane Trickster registered but no mechanics
- **Action Cards**: No Rogue-specific action cards (Cunning Action, Steady Aim, etc.)
- **Combat Integration**: Sneak Attack trigger detection incomplete

### Architecture Reference Analysis

**Fighter Implementation Success Patterns:**
- ✅ Service-first architecture (`services/fighter_abilities.py`, 692 lines)
- ✅ Comprehensive resource management (Second Wind, Action Surge, Indomitable)
- ✅ Action card integration with live resource updates
- ✅ Database-driven feature loading with scaling
- ✅ 95%+ test coverage including UI integration tests

**Barbarian Implementation Success Patterns:**
- ✅ Complex state management (Rage persistence, multi-turn effects)
- ✅ Condition system integration (resistances, advantages)
- ✅ Advanced resource scaling (uses increase by level)
- ✅ Subclass feature automation (4 Berserker features)
- ✅ Combat state integration for persistent effects

**Rogue-Specific Technical Challenges:**
1. **Sneak Attack Complexity**: Conditional damage requiring ally detection and advantage calculation
2. **Cunning Strike Resource Model**: Variable dice costs (1d6-6d6) with multiple simultaneous effects
3. **Stealth Mechanics**: Hide action integration with encounter state
4. **Evasion System**: Dexterity save modification requiring save system integration
5. **Expertise Scaling**: Dynamic skill bonus calculations

## Technical Requirements

### Priority 1: Core Backend Services (Levels 1-7)

#### RogueAbilitiesService Architecture
**File:** `services/rogue_abilities.py`

**Core Service Interface:**
```python
class RogueAbilitiesService:
    # Resource Management
    def get_rogue_level(self, character_id: str) -> int
    def update_rogue_resources_for_level(self, character_id: str, level: int) -> None
    def rest_rogue_resources(self, character_id: str, rest_type: str) -> None

    # Level 1-2 Features
    def apply_expertise(self, character_id: str, skill_name: str) -> Dict[str, Any]
    def calculate_sneak_attack_damage(self, character_id: str, level: int) -> str
    def check_sneak_attack_eligibility(self, character_id: str, target_id: str, context: Dict) -> bool
    def use_cunning_action(self, character_id: str, action_type: str) -> Dict[str, Any]

    # Level 3-7 Features
    def use_steady_aim(self, character_id: str) -> Dict[str, Any]
    def use_uncanny_dodge(self, character_id: str, damage: int) -> Dict[str, Any]
    def apply_evasion(self, character_id: str, save_result: Dict) -> Dict[str, Any]
    def apply_reliable_talent(self, character_id: str, skill_roll: int) -> int
```

**Critical Dependencies:**
- `services/character_resources.py` - Resource tracking integration
- `services/advantage_system.py` - Advantage/disadvantage detection for Sneak Attack
- `core/combat_manager.py` - Ally detection within 5 feet
- `services/condition_manager.py` - Hide condition and stealth state

#### Database Schema Expansion
**File:** `database/migrations/003_expand_rogue_features.sql`

**Required Fields:**
```sql
-- Cunning Strike System (Level 5+)
ALTER TABLE rogue_features ADD COLUMN cunning_strike_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN cunning_strike_effects_known TEXT; -- JSON array

-- Advanced Features (Level 7+)
ALTER TABLE rogue_features ADD COLUMN reliable_talent_active BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN reliable_talent_minimum INTEGER DEFAULT 10;

-- Level 11+ Features
ALTER TABLE rogue_features ADD COLUMN improved_cunning_strike BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN devious_strikes_available BOOLEAN DEFAULT FALSE;

-- Level 14+ Advanced Cunning Strikes
ALTER TABLE rogue_features ADD COLUMN daze_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN knock_out_available BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN obscure_available BOOLEAN DEFAULT FALSE;

-- Level 15+ Features
ALTER TABLE rogue_features ADD COLUMN slippery_mind_active BOOLEAN DEFAULT FALSE;
ALTER TABLE rogue_features ADD COLUMN elusive_active BOOLEAN DEFAULT FALSE;

-- Level 20 Capstone
ALTER TABLE rogue_features ADD COLUMN stroke_of_luck_uses_current INTEGER DEFAULT 0;
ALTER TABLE rogue_features ADD COLUMN stroke_of_luck_uses_max INTEGER DEFAULT 1;
```

### Priority 2: Sneak Attack & Combat Integration

#### Sneak Attack Detection System
**Integration Points:**
- `services/weapon_attack_service.py` - Damage calculation integration
- `action_cards/action_panel.py` - Attack flow modification
- `core/combat_manager.py` - Ally detection logic

**Technical Requirements:**
1. **Weapon Eligibility**: Finesse or ranged weapon detection
2. **Advantage Detection**: Integration with existing advantage system
4. **Once-Per-Turn Enforcement**: Turn-based resource tracking
5. **Damage Integration**: Seamless addition to weapon damage rolls

**Implementation Strategy:**
```python
# In WeaponAttackService.calculate_attack_damage()
def _apply_sneak_attack_if_eligible(self, character_id: str, weapon: Dict,
                                   target_id: str, attack_context: Dict) -> Dict:
    rogue_service = RogueAbilitiesService(self.db_path)

    # Check weapon eligibility (finesse or ranged)
    if not self._is_sneak_attack_weapon(weapon):
        return {"sneak_attack_damage": "0d6", "reason": "weapon_ineligible"}

    # Check advantage or ally proximity
    if not rogue_service.check_sneak_attack_eligibility(character_id, target_id, attack_context):
        return {"sneak_attack_damage": "0d6", "reason": "conditions_not_met"}

    # Apply damage if eligible
    level = rogue_service.get_rogue_level(character_id)
    damage_dice = rogue_service.calculate_sneak_attack_damage(character_id, level)

    return {
        "sneak_attack_damage": damage_dice,
        "reason": "applied",
        "mechanics": attack_context.get("advantage_source", "ally_proximity")
    }
```

#### Cunning Strike System Architecture
**Complexity Level:** High - Variable resource costs with multiple simultaneous effects

**Core Mechanics:**
- **Resource Model**: Pay Sneak Attack dice (1d6-6d6) for effects
- **Effect Stacking**: Level 11+ allows multiple effects per attack
- **Save DC Calculation**: 8 + DEX mod + proficiency bonus
- **Conditional Requirements**: Poisoner's Kit for Poison effect

**Data Structure:**
```python
CUNNING_STRIKE_EFFECTS = {
    "basic": {  # Level 5+
        "poison": {"cost": "1d6", "save": "constitution", "condition": "poisoned", "duration": "1_minute", "requires": "poisoners_kit"},
        "trip": {"cost": "1d6", "save": "dexterity", "condition": "prone", "size_limit": "large"},
        "withdraw": {"cost": "1d6", "movement": "half_speed", "no_opportunity_attacks": True}
    },
    "devious": {  # Level 14+
        "daze": {"cost": "2d6", "save": "constitution", "effect": "limited_actions", "duration": "next_turn"},
        "knock_out": {"cost": "6d6", "save": "constitution", "condition": "unconscious", "duration": "1_minute"},
        "obscure": {"cost": "3d6", "save": "dexterity", "condition": "blinded", "duration": "next_turn"}
    }
}
```

### Priority 3: Action Card System Enhancement

#### New Action Cards Required
**File:** `action_cards/action_panel.py`

**Level 2: Cunning Action Cards**
```python
def _create_cunning_action_cards(self, level: int) -> List[ActionCard]:
    cards = []
    if level >= 2:
        cards.extend([
            ActionCard(ActionType.CUNNING_DASH, "[DASH]", "Cunning Dash",
                      "Dash as bonus action", action_cost="bonus"),
            ActionCard(ActionType.CUNNING_DISENGAGE, "[DISENGAGE]", "Cunning Disengage",
                      "Disengage as bonus action", action_cost="bonus"),
            ActionCard(ActionType.CUNNING_HIDE, "[HIDE]", "Cunning Hide",
                      "Hide as bonus action", action_cost="bonus")
        ])
    return cards
```

**Level 3: Steady Aim Card**
```python
def _create_steady_aim_card(self, level: int) -> Optional[ActionCard]:
    if level >= 3:
        return ActionCard(ActionType.STEADY_AIM, "[AIM]", "Steady Aim",
                         "Gain advantage on next attack (cannot move)",
                         action_cost="bonus", restrictions=["no_movement"])
    return None
```

**Level 5+: Cunning Strike Cards**
```python
def _create_cunning_strike_cards(self, level: int) -> List[ActionCard]:
    cards = []
    if level >= 5:
        # Basic effects
        for effect_name, effect_data in CUNNING_STRIKE_EFFECTS["basic"].items():
            card = ActionCard(ActionType.CUNNING_STRIKE, f"[{effect_name.upper()}]",
                             f"Cunning Strike: {effect_name.title()}",
                             f"Cost: {effect_data['cost']} sneak attack dice",
                             dice_cost=effect_data['cost'])
            cards.append(card)

    if level >= 14:
        # Devious strikes
        for effect_name, effect_data in CUNNING_STRIKE_EFFECTS["devious"].items():
            card = ActionCard(ActionType.CUNNING_STRIKE, f"[{effect_name.upper()}]",
                             f"Devious Strike: {effect_name.title()}",
                             f"Cost: {effect_data['cost']} sneak attack dice",
                             dice_cost=effect_data['cost'])
            cards.append(card)

    return cards
```

#### Resource Display Integration
**Requirements:**
- Show current Sneak Attack dice available
- Display Cunning Strike effect costs
- Track once-per-turn usage (Uncanny Dodge, Sneak Attack)
- Visual indicators for conditional requirements (Poisoner's Kit)

### Priority 4: Feature System Completion

#### Complete Feature Definitions
**File:** `core/feature_definitions.py` - Expand `ROGUE_FEATURES`

**Missing Levels (3-20):**
```python
ROGUE_FEATURES = {
    # ... existing levels 1-2 ...
    3: [
        FeatureDefinition(name="Rogue Subclass", level_acquired=3, feature_type="subclass"),
        FeatureDefinition(name="Steady Aim", level_acquired=3, feature_type="bonus_action",
                         mechanics={"grants_advantage": True, "movement_restriction": True})
    ],
    5: [
        FeatureDefinition(name="Cunning Strike", level_acquired=5, feature_type="triggered",
                         mechanics={"dice_costs": {"poison": 1, "trip": 1, "withdraw": 1}}),
        FeatureDefinition(name="Uncanny Dodge", level_acquired=5, feature_type="reaction",
                         mechanics={"damage_reduction": "half", "uses_per_turn": 1})
    ],
    # ... continue through level 20 ...
}
```

#### Subclass Implementation: Arcane Trickster
**File:** `services/subclasses/arcane_trickster.py`

**Key Features:**
- **Spellcasting**: Wizard spell list (Enchantment/Illusion focus)
- **Mage Hand Legerdemain**: Enhanced Mage Hand cantrip
- **Magical Ambush**: Advantage on spell saves when hidden
- **Versatile Trickster**: Mage Hand grants advantage on attacks

### Priority 5: Testing Framework

#### Test Architecture Pattern
**Reference:** Fighter test structure (`test/features/test_fighter_*.py`)

**Required Test Files:**
1. `test/features/test_rogue_sneak_attack.py` - Damage calculation, condition detection
2. `test/features/test_rogue_cunning_action.py` - Bonus action mechanics
3. `test/features/test_rogue_cunning_strike.py` - Resource costs, effect application
4. `test/features/test_rogue_defensive_features.py` - Uncanny Dodge, Evasion
5. `test/features/test_arcane_trickster.py` - Subclass feature integration

**Critical Test Scenarios:**
```python
class TestSneakAttack:
    def test_sneak_attack_with_advantage(self):
        """Test Sneak Attack triggers with advantage"""
        # Setup rogue with finesse weapon and advantage
        # Verify damage includes sneak attack dice

    def test_sneak_attack_with_ally_proximity(self):
        """Test Sneak Attack triggers with ally within 5 feet"""
        # Position ally within 5 feet of target
        # Verify sneak attack applies without advantage

    def test_sneak_attack_once_per_turn_enforcement(self):
        """Test Sneak Attack only applies once per turn"""
        # Multiple attacks in same turn
        # Verify only first eligible attack gets sneak attack

class TestCunningStrike:
    def test_cunning_strike_dice_cost_deduction(self):
        """Test proper dice cost deduction from sneak attack"""
        # Level 9 rogue (5d6 sneak attack)
        # Use Trip (1d6 cost) -> verify 4d6 damage + trip effect

    def test_multiple_cunning_strikes_level_11(self):
        """Test multiple effects at level 11+"""
        # Level 11+ rogue with sufficient dice
        # Apply Trip (1d6) + Poison (1d6) -> verify both effects
```

## Implementation Timeline

### Phase 1: Backend Foundation (5-7 days)
**Priority:** Critical Path
1. **Day 1-2**: `RogueAbilitiesService` creation with core methods
2. **Day 2-3**: Database schema expansion and migration
3. **Day 3-4**: Feature definitions completion (levels 3-20)
4. **Day 4-5**: Sneak Attack integration with `WeaponAttackService`
5. **Day 5-7**: Basic action cards (Cunning Action, Steady Aim)

**Deliverables:**
- ✅ Functional Rogue levels 1-7 with core features
- ✅ Sneak Attack damage integration
- ✅ Basic resource management

### Phase 2: Advanced Features (4-6 days)
**Priority:** High
1. **Day 1-2**: Cunning Strike system implementation
2. **Day 2-3**: Advanced defensive features (Uncanny Dodge, Evasion)
3. **Day 3-4**: High-level features (Reliable Talent, Slippery Mind, Elusive)
4. **Day 4-5**: Stroke of Luck and Epic Boon integration
5. **Day 5-6**: Feature scaling and resource updates

**Deliverables:**
- ✅ Complete Rogue levels 1-20
- ✅ Cunning Strike resource system
- ✅ All defensive and utility features

### Phase 3: Subclass & Polish (3-5 days)
**Priority:** Medium-High
1. **Day 1-2**: Arcane Trickster subclass implementation
2. **Day 2-3**: UI polish and action card refinement
3. **Day 3-4**: Integration testing and bug fixes
4. **Day 4-5**: Performance optimization and documentation

**Deliverables:**
- ✅ Arcane Trickster subclass fully functional
- ✅ Polished UI experience
- ✅ Comprehensive documentation

### Phase 4: Testing & Validation (2-4 days)
**Priority:** Critical
1. **Day 1-2**: Unit test suite completion
2. **Day 2-3**: Integration test scenarios
3. **Day 3-4**: UI testing and edge case validation

**Deliverables:**
- ✅ 90%+ test coverage
- ✅ All edge cases validated
- ✅ Performance benchmarks met

**Total Estimated Timeline:** 14-22 days

## Risk Assessment & Mitigation

### High-Risk Areas

#### 1. Cunning Strike Complexity
**Risk:** Resource system complexity may cause performance issues or bugs
**Mitigation:**
- Implement simplified version first, then add complexity
- Extensive unit testing for dice cost calculations
- Performance profiling for resource updates

#### 2. Sneak Attack Condition Detection
**Risk:** Complex advantage/ally detection may have edge cases
**Mitigation:**
- Reuse existing advantage system infrastructure
- Create comprehensive test scenarios for all trigger conditions
- Debug logging for condition evaluation

#### 3. Combat State Integration
**Risk:** Turn-based restrictions may conflict with existing combat flow
**Mitigation:**
- Follow Barbarian Rage implementation patterns for persistent state
- Integrate with existing turn management system
- Test with various encounter scenarios

### Medium-Risk Areas

#### 4. Action Economy Complexity
**Risk:** Multiple bonus actions may conflict with action economy system
**Mitigation:**
- Build on Fighter/Barbarian action economy patterns
- Clear UI indicators for action availability
- Validation logic for action conflicts

#### 5. Subclass Spellcasting
**Risk:** Arcane Trickster requires spell system integration
**Mitigation:**
- Implement basic version without full spell system first
- Use Wizard spell list infrastructure if available
- Consider simplified spellcasting for initial release

## Success Metrics

### Functional Completeness
- ✅ All 20 Rogue levels implemented and tested
- ✅ Sneak Attack triggers correctly in 100% of valid scenarios
- ✅ Cunning Strike resource system handles all cost combinations
- ✅ Arcane Trickster subclass functional with core features

### Performance Standards
- ✅ Sneak Attack calculations complete within 50ms
- ✅ Action card refresh after resource usage < 100ms
- ✅ Database updates for feature progression < 200ms
- ✅ Memory usage increase < 5% during extended combat

### Code Quality Standards
- ✅ 90%+ unit test coverage for all Rogue features
- ✅ Integration tests for all major feature combinations
- ✅ Type hints and documentation for all public methods
- ✅ Performance profiling for critical paths

### User Experience Standards
- ✅ Intuitive action card layout with clear resource costs
- ✅ Immediate visual feedback for successful feature usage
- ✅ Clear error messages for invalid actions
- ✅ Consistent UI patterns with Fighter/Barbarian implementations

## Technical Dependencies

### Internal Dependencies
- `services/character_resources.py` - Resource tracking infrastructure
- `services/advantage_system.py` - Advantage/disadvantage detection
- `core/combat_manager.py` - Turn management and ally detection
- `services/weapon_attack_service.py` - Damage calculation integration
- `action_cards/action_panel.py` - UI action card system

### External Dependencies
- SQLite database for persistence
- PyQt6 for UI components
- Existing spell system (for Arcane Trickster)
- Combat grid system (for ally proximity detection)

## Conclusion

The Rogue implementation represents a significant but achievable extension to TaleKeeper's class system. By following the proven architectural patterns from Fighter and Barbarian implementations while addressing Rogue-specific complexities (Sneak Attack, Cunning Strike, stealth mechanics), we can deliver a comprehensive and polished Rogue experience.

The phased approach ensures core functionality is delivered first, with advanced features and polish following in subsequent phases. The risk mitigation strategies address the most complex technical challenges, while the testing framework ensures reliability and maintainability.

**Recommendation:** Proceed with implementation following this PRD, with regular milestone reviews to ensure quality and timeline adherence.