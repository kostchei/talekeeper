# 🪓 Barbarian

## Core Barbarian Traits

- **Primary Ability:** Strength  
- **Hit Die:** 1d12 per Barbarian level  
- **Saving Throw Proficiencies:** Strength, Constitution  
- **Skill Proficiencies (Choose 2):**  
  Animal Handling, Athletics, Intimidation, Nature, Perception, Survival  
- **Weapon Proficiencies:** Simple and Martial weapons  
- **Armor Training:** Light armor, Medium armor, Shields  
- **Starting Equipment (Choose A or B):**  
  - **A:** Greataxe, 4 Handaxes, Explorer’s Pack, 15 GP  
  - **B:** 75 GP

## Multiclassing

- Gain the Barbarian's **Hit Die**, **Martial Weapon Proficiency**, and **Shield Training**
- Gain the **Level 1 Features** of the Barbarian

## Class Features by Level

| Level | Proficiency Bonus | Class Features                                                                 | Rages | Rage Damage | Weapon Mastery |
|-------|-------------------|--------------------------------------------------------------------------------|--------|--------------|----------------|
| 1     | +2                | Rage, Unarmored Defense, Weapon Mastery                                        | 2      | +2           | 2              |
| 2     | +2                | Danger Sense, Reckless Attack                                                  | 2      | +2           | 2              |
| 3     | +2                | Subclass, Primal Knowledge                                                     | 3      | +2           | 2              |
| 4     | +2                | Ability Score Improvement                                                      | 3      | +2           | 3              |
| 5     | +3                | Extra Attack, Fast Movement                                                    | 3      | +2           | 3              |
| 6     | +3                | Subclass Feature                                                               | 4      | +2           | 3              |
| 7     | +3                | Feral Instinct, Instinctive Pounce                                             | 4      | +2           | 3              |
| 8     | +3                | Ability Score Improvement                                                      | 4      | +2           | 3              |
| 9     | +4                | Brutal Strike                                                                  | 4      | +3           | 3              |
| 10    | +4                | Subclass Feature                                                               | 4      | +3           | 4              |
| 11    | +4                | Relentless Rage                                                                | 4      | +3           | 4              |
| 12    | +4                | Ability Score Improvement                                                      | 5      | +3           | 4              |
| 13    | +5                | Improved Brutal Strike                                                         | 5      | +3           | 4              |
| 14    | +5                | Subclass Feature                                                               | 5      | +3           | 4              |
| 15    | +5                | Persistent Rage                                                                | 5      | +3           | 4              |
| 16    | +5                | Ability Score Improvement                                                      | 5      | +4           | 4              |
| 17    | +6                | Improved Brutal Strike                                                         | 6      | +4           | 4              |
| 18    | +6                | Indomitable Might                                                              | 6      | +4           | 4              |
| 19    | +6                | Epic Boon                                                                       | 6      | +4           | 4              |
| 20    | +6                | Primal Champion                                                                | 6      | +4           | 4              |

## Level Features

### Level 1: Rage
- Bonus Action to enter Rage (if not wearing Heavy armor)
- While raging:
  - Resistance to Bludgeoning, Piercing, Slashing damage
  - Rage Damage Bonus to Strength-based attacks
  - Advantage on Strength checks and saves
  - No Spellcasting or Concentration
  - Ends early if you don Heavy armor or become Incapacitated
- Extend rage by:
  - Making an attack roll
  - Forcing a saving throw
  - Taking a Bonus Action to extend
- Max duration: 10 minutes

#### TaleKeeper Implementation Notes
- Rage is tracked through the action card resource system. Activating the [RAGE] action card consumes a use, marks the character as raging, and refreshes melee weapon cards so the bonus is visible immediately.
- Damage bonuses now come directly from the active combat context instead of a database lookup. This guarantees the correct +2 / +3 / +4 scaling based on barbarian level and ensures Cleave follow-up attacks inherit the Rage state.
- If an attack is ineligible (ranged or thrown), combat logs include a debug message explaining why the Rage bonus was skipped, which helps QA and table rulings.

### Level 1: Unarmored Defense
- AC = 10 + Dex + Con (can use a shield)

### Level 1: Weapon Mastery
- Gain access to mastery in all weapons

### Level 2: Danger Sense
- Advantage on Dex saves (unless Incapacitated)

### Level 2: Reckless Attack
- On your first attack of the turn:
  - Advantage on Strength attack rolls
  - Enemies have Advantage to hit you until your next turn

### Level 3: Primal Knowledge
- Gain one more skill from your class list
- While Raging, you can use Strength for:
  - Acrobatics, Intimidation, Perception, Stealth, Survival

### Level 4, 8, 12, 16: Ability Score Improvement
- Take ASI or feat of your choice

### Level 5: Extra Attack
- Make two attacks on Attack action

### Level 5: Fast Movement
- +10 ft movement (if not wearing Heavy armor)

### Level 7: Feral Instinct
- Advantage on Initiative rolls

### Level 7: Instinctive Pounce
- When entering Rage, move up to half your speed

### Level 9: Brutal Strike
- If you use Reckless Attack, you can forgo Advantage:
  - On hit, deal +1d10 and apply one:
    - Forceful Blow: Push 15 ft & move toward target
    - Hamstring Blow: -15 ft Speed until next turn

### Level 11: Relentless Rage
- Drop to 0 HP → make DC 10 Con save
  - On success, drop to HP = 2 × Barbarian level instead
  - DC increases by 5 each time (resets after rest)

### Level 13: Improved Brutal Strike
- Add 2 new effects to Brutal Strike:
  - Staggering Blow: Target has Disadvantage on next save & can’t make Opportunity Attacks
  - Sundering Blow: Next attack roll vs target gains +5

### Level 15: Persistent Rage
- Regain all Rage uses when rolling Initiative (once per Long Rest)
- Rage now lasts 10 minutes without extension actions
- Ends only if you fall Unconscious or don Heavy armor

### Level 17: Brutal Strike Upgrade
- Brutal Strike damage increases to 2d10
- You can apply two different effects per use

### Level 18: Indomitable Might
- If your Strength check/save is lower than your Strength score, use your score instead

### Level 19: Epic Boon
- Gain an Epic Boon feat or any other qualified feat  
  Recommended: Boon of Irresistible Offense

### Level 20: Primal Champion
- Strength and Constitution increase by +4 (max 25)

## Barbarian Subclass: Path of the Berserker

### Level 3: Frenzy
- When you Reckless Attack while Raging:
  - Add d6s equal to Rage Damage Bonus to first hit

### Level 6: Mindless Rage
- While Raging:  
  - Immune to Charmed and Frightened  
  - If already affected, it ends on entering Rage

### Level 10: Retaliation
- When damaged by a creature within 5 ft:
  - Use Reaction to make 1 melee weapon/unarmed attack

### Level 14: Intimidating Presence
- As Bonus Action:
  - 30 ft emanation → Wis Save DC (8 + Str mod + Prof)
  - On fail: Frightened for 1 minute (repeat save each turn)
  - Use again after Long Rest or by expending a Rage use

## Barbarian Implementation Plan

Based on analysis of the Fighter implementation patterns in TaleKeeper, this plan provides a comprehensive approach to implementing the Barbarian class following the same architectural patterns and quality standards.

### Implementation Analysis from Fighter Patterns

#### Key Fighter Implementation Components:
1. **Database Layer**: `fighter_features` table + `FighterAbilitiesService`
2. **Backend Services**: `services/fighter_abilities.py` with resource management
3. **Frontend UI**: Action cards in `action_cards/action_panel.py`
4. **Feature Integration**: Core feature system via `core/feature_integration.py`
5. **Testing Framework**: Comprehensive test suite in `test/features/`

#### Critical Success Patterns Identified:
- **Resource Management**: Uses unified resource system with current/max tracking
- **Action Cards**: Barbarian features already partially implemented (Rage, Reckless Attack)
- **Database Schema**: `barbarian_features` table exists but needs expansion
- **Combat Integration**: Rage damage bonuses integrated into weapon attack calculations
- **State Tracking**: Combat state persistence during encounters

### Database Implementation Plan

#### Phase 1: Expand `barbarian_features` Table
**File**: `database/migrations/002_expand_barbarian_features.sql`

```sql
-- Expand barbarian_features table for all features
ALTER TABLE barbarian_features ADD COLUMN fast_movement_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN feral_instinct_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN brutal_strike_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN brutal_strike_uses_max INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN relentless_rage_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN relentless_rage_uses_max INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN persistent_rage_recharge_used BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN primal_knowledge_skills TEXT; -- JSON array
ALTER TABLE barbarian_features ADD COLUMN instinctive_pounce_available BOOLEAN DEFAULT FALSE;

-- Path of the Berserker features
ALTER TABLE barbarian_features ADD COLUMN frenzy_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN mindless_rage_active BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN retaliation_available BOOLEAN DEFAULT FALSE;
ALTER TABLE barbarian_features ADD COLUMN intimidating_presence_uses_current INTEGER DEFAULT 0;
ALTER TABLE barbarian_features ADD COLUMN intimidating_presence_uses_max INTEGER DEFAULT 0;
```

#### Phase 2: Feature Definitions
**File**: `core/feature_definitions.py` (expand BARBARIAN_FEATURES)

Features 3-20 need to be added to match the level table in the documentation.

#### Phase 3: Class Features Data
**File**: `database/seeds/008_barbarian_class_features.sql`

```sql
-- Insert all Barbarian class features into class_features table
INSERT INTO class_features (class_id, level, feature_name, description, mechanics, action_type, uses_per_rest, rest_type) VALUES
('barbarian', 3, 'Primal Knowledge', 'Gain one skill and use Strength for certain skills while Raging', '{"skills": ["animal_handling", "athletics", "intimidation", "nature", "perception", "survival"], "rage_strength_substitution": true}', 'passive', NULL, NULL),
('barbarian', 5, 'Extra Attack', 'Make two attacks when taking the Attack action', '{"attacks": 2}', 'passive', NULL, NULL),
('barbarian', 5, 'Fast Movement', 'Speed increases by 10 feet if not wearing Heavy armor', '{"speed_bonus": 10, "requires": "no_heavy_armor"}', 'passive', NULL, NULL),
-- ... continue for all levels
```

### Backend Services Implementation Plan

#### Phase 1: Create BarbarianAbilitiesService
**File**: `services/barbarian_abilities.py`

Follow Fighter pattern with these core methods:
```python
class BarbarianAbilitiesService:
    def get_barbarian_level(self, character_id: str) -> int
    def update_barbarian_resources_for_level(self, character_id: str, level: int) -> None
    def use_rage(self, character_id: str) -> Dict[str, Any]
    def end_rage(self, character_id: str) -> Dict[str, Any]
    def use_reckless_attack(self, character_id: str) -> Dict[str, Any]
    def use_brutal_strike(self, character_id: str, strike_type: str) -> Dict[str, Any]
    def check_relentless_rage(self, character_id: str, damage: int) -> Dict[str, Any]
    def rest_barbarian_resources(self, character_id: str, rest_type: str) -> None
    def process_berserker_turn_start(self, character_id: str) -> Dict[str, Any]
```

#### Phase 2: Rage System Integration
**References**:
- `action_cards/action_panel.py:4778-4810` (existing _use_rage implementation)
- `docs/Barbarian_Class.md:62-66` (TaleKeeper Implementation Notes)

**Key Requirements**:
- Rage damage bonus applied from active combat context
- Resource tracking independent per character
- Proper Cleave follow-up attack inheritance
- Debug logging for ineligible attacks (ranged/thrown)

#### Phase 3: Combat State Management
**File**: Expand `character_combat_state` table

```sql
ALTER TABLE character_combat_state ADD COLUMN raging BOOLEAN DEFAULT FALSE;
ALTER TABLE character_combat_state ADD COLUMN rage_damage_bonus INTEGER DEFAULT 0;
ALTER TABLE character_combat_state ADD COLUMN reckless_attack_active BOOLEAN DEFAULT FALSE;
ALTER TABLE character_combat_state ADD COLUMN frenzy_active BOOLEAN DEFAULT FALSE;
```

### Frontend UI Implementation Plan

#### Phase 1: Action Cards Enhancement
**File**: `action_cards/action_panel.py`

**Current Status**: Rage and Reckless Attack partially implemented
**Needed Additions**:
1. **Brutal Strike Cards** (Level 9+):
   ```python
   # Add to _create_feature_cards()
   if brutal_strike_feature and level >= 9:
       for strike_type in ['forceful', 'hamstring', 'staggering', 'sundering']:
           if self._has_brutal_strike_option(strike_type, level):
               card = ActionCard(ActionType.BRUTAL_STRIKE, f"[{strike_type.upper()}]",
                               f"Brutal Strike ({strike_type.title()})", description)
   ```

2. **Instinctive Pounce Card** (Level 7+):
   ```python
   if instinctive_pounce_feature and level >= 7:
       card = ActionCard(ActionType.INSTINCTIVE_POUNCE, "[POUNCE]", "Instinctive Pounce",
                        "Move half speed when entering Rage")
   ```

3. **Intimidating Presence Card** (Level 14+ Berserker):
   ```python
   if intimidating_presence_feature and subclass == 'berserker' and level >= 14:
       card = ActionCard(ActionType.INTIMIDATING_PRESENCE, "[FEAR]", "Intimidating Presence",
                        "Frighten enemies in 30 ft (Wis save)")
   ```

#### Phase 2: Combat UI Integration
**Files**:
- `character_sheet/character_panel.py` (AC calculation for Unarmored Defense)
- `encounter_pane/encounter_panel.py` (resistance application)

**Key Features**:
1. **Unarmored Defense AC Display**: Show "AC = 10 + DEX + CON" when not wearing armor
2. **Rage Status Indicator**: Visual indicator during rage with turns remaining
3. **Damage Resistance Visual**: Show half damage for physical damage types during rage

### Feature System Integration Plan

#### Phase 1: Core Feature System
**File**: `core/class_features.py`

Add Barbarian feature classes following Fighter pattern:
```python
class RageFeature(Feature):
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool

class BrutalStrikeFeature(Feature):
    def apply(self, character: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]
    def can_use(self, character: Dict[str, Any], context: Optional[Dict] = None) -> bool
```

#### Phase 2: Subclass System
**File**: `services/subclass_manager.py`

Expand for Berserker features:
```python
def process_berserker_frenzy(self, character_id: str, attack_result: Dict) -> Dict[str, Any]
def use_berserker_retaliation(self, character_id: str, attacker_id: str) -> Dict[str, Any]
```

### Testing Implementation Plan

#### Phase 1: Database Test Framework
**File**: `test/fixtures/barbarian_test_database.py`

Following Fighter pattern from `test/fixtures/fighter_test_database.py`:
```python
class BarbarianTestDatabase:
    def create_test_barbarian(self, level: int, subclass: str = 'berserker') -> str
    def setup_barbarian_equipment(self, character_id: str, level: int) -> None
    def verify_barbarian_features(self, character_id: str, level: int) -> bool
```

#### Phase 2: Feature Test Suites
**Files**: `test/features/test_barbarian_*.py`

Based on Fighter test structure:
1. **test_barbarian_rage.py**: Rage activation, duration, damage bonus, resistance
2. **test_barbarian_reckless_attack.py**: Advantage mechanics, enemy advantage tracking
3. **test_barbarian_brutal_strike.py**: Strike types, Reckless Attack interaction
4. **test_barbarian_unarmored_defense.py**: AC calculation, armor interactions
5. **test_berserker_subclass.py**: Frenzy, Mindless Rage, Retaliation, Intimidating Presence

#### Phase 3: Combat Integration Tests
**File**: `test/features/test_barbarian_combat_flow.py`

End-to-end combat scenarios:
- Rage → Reckless Attack → weapon attacks with damage bonus
- Brutal Strike combinations at different levels
- Resistance application during damage
- Resource recovery after rests

### Implementation Issues & Solutions from Fighter Analysis

#### Issue 1: Resource Tracking Complexity
**Fighter Solution**: Unified resource system in `services/character_resources.py`
**Barbarian Application**:
- Rage uses scale with level (2→3→4→5→6)
- Brutal Strike uses based on Reckless Attack usage
- Berserker features have independent resource pools

#### Issue 2: Combat State Persistence
**Fighter Solution**: `character_combat_state` table with turn-by-turn tracking
**Barbarian Application**:
- Rage persists across multiple turns (10 minutes)
- Reckless Attack advantage/disadvantage tracking
- Frenzy and Mindless Rage state management

#### Issue 3: Level-Dependent Feature Scaling
**Fighter Solution**: `update_fighter_resources_for_level()` method
**Barbarian Application**:
```python
def update_barbarian_resources_for_level(self, character_id: str, level: int) -> None:
    rage_uses = 2 if level < 3 else (3 if level < 6 else (4 if level < 12 else (5 if level < 17 else 6)))
    rage_damage = 2 if level < 9 else (3 if level < 16 else 4)
    # Update barbarian_features table
```

### Integration Priority Order

#### Priority 1: Core Barbarian Features (Levels 1-5)
1. Complete Rage system (already 70% implemented)
2. Unarmored Defense AC calculation
3. Reckless Attack (already 60% implemented)
4. Danger Sense passive integration
5. Fast Movement speed bonus

#### Priority 2: Mid-Level Features (Levels 6-10)
1. Primal Knowledge skill system
2. Extra Attack (reuse Fighter implementation)
3. Feral Instinct initiative advantage
4. Instinctive Pounce movement on Rage

#### Priority 3: Advanced Features (Levels 11-20)
1. Brutal Strike action cards and mechanics
2. Relentless Rage death save system
3. Persistent Rage resource recovery
4. Indomitable Might ability substitution
5. Primal Champion stat increases

#### Priority 4: Berserker Subclass
1. Frenzy damage bonus (Level 3)
2. Mindless Rage condition immunity (Level 6)
3. Retaliation reaction attacks (Level 10)
4. Intimidating Presence area effect (Level 14)

### Quality Assurance Plan

#### Code Quality Standards
**Reference**: Fighter implementation quality patterns
- Follow existing service class patterns
- Use type hints and proper error handling
- Database transactions with rollback on failure
- Qt signal/slot patterns for UI integration

#### Testing Coverage Requirements
**Reference**: Fighter test coverage (~95%)
- Unit tests for all service methods
- Integration tests for combat scenarios
- UI tests for action card interactions
- Database tests for resource persistence

#### Performance Considerations
**Reference**: Fighter performance benchmarks
- Database queries optimized with proper indexes
- UI updates batched to prevent lag
- Memory management for long combat encounters

### Development Timeline Estimate

#### Phase 1 (Database & Backend): 2-3 days
- Database schema expansion
- BarbarianAbilitiesService implementation
- Core feature definitions

#### Phase 2 (Frontend Integration): 2-3 days
- Action card enhancements
- Combat UI updates
- Character sheet integration

#### Phase 3 (Testing Framework): 2-3 days
- Test database setup
- Feature test implementation
- Integration test scenarios

#### Phase 4 (Polish & Documentation): 1-2 days
- Bug fixes and optimization
- Documentation updates
- Final testing validation

**Total Estimated Timeline**: 7-11 days

### References and Code Locations

#### Key Implementation Files:
- **Fighter Service**: `services/fighter_abilities.py:20-692`
- **Fighter Tests**: `test/README_FIGHTER_TESTING.md:1-202`
- **Action Cards**: `action_cards/action_panel.py:427-448` (Rage/Reckless)
- **Database Schema**: `database/schema/001_current_schema.sql` (barbarian_features table)
- **Feature Definitions**: `core/feature_definitions.py:149-200` (partial Barbarian)

#### Testing Framework References:
- **Test Database**: `test/fixtures/fighter_test_database.py`
- **Feature Tests**: `test/features/test_fighter_*.py`
- **Test Runner**: `test/run_fighter_tests.py`

#### Combat Integration References:
- **Damage Application**: `action_cards/action_panel.py:4778-4810` (_use_rage)
- **Resource System**: `services/character_resources.py`
- **Combat State**: Database table `character_combat_state`

This implementation plan follows the proven Fighter architecture while addressing the unique complexity of Barbarian features, particularly the Rage system's multi-turn state management and the scaling resource requirements across 20 levels.