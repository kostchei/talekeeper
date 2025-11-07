# Fighter Character Progression Testing Framework
## Comprehensive Test Plan - LOCKED FOR IMPLEMENTATION

**Version:** 1.0
**Date:** 2025-11-07
**Status:** Locked - Ready for Implementation
**Ruleset:** D&D 5e SRD 2024

---

## Overview

Create an automated testing system that creates Fighter characters (Champion subclass) from levels 1-20, using actual backend functions (not direct database manipulation), and records all choices made during character progression.

**Key Principles:**
- ✅ Use backend APIs only (`ProgrammaticCharacterCreator`, `UnifiedLevelUpService`, etc.)
- ✅ Test against REAL production database with archive/unarchive mechanism
- ✅ Record all choices and progression in JSON/YAML format
- ✅ Random species and background selection for variety
- ✅ Weapon Masteries: Assume ALL masteries known (simplified)
- ✅ Generate human-readable reports of progression

---

## Phase 1: Database Archive System

### 1.1 Create Database Archive/Unarchive Scripts ✅

**File to create:** `tests/helpers/database_archiver.py`

**Purpose:** Safe backup and restore of production database for testing

**Features:**
```python
class DatabaseArchiver:
    def archive(db_path: str) -> str:
        """
        Archives the database to timestamped backup
        Returns: Path to archive file
        """

    def unarchive(archive_path: str, db_path: str):
        """
        Restores database from archive
        """

    def list_archives() -> List[str]:
        """
        Lists available archives
        """
```

**Archive naming convention:** `talekeeper.db.archive.YYYYMMDD_HHMMSS`

**Safety features:**
- Verify archive integrity before unarchiving
- Prevent overwriting existing DB without confirmation
- Store archives in `tests/archives/` directory
- Log all archive/unarchive operations

### 1.2 Test Archive System ✅

**File to create:** `tests/test_database_archiver.py`

**Tests:**
- Archive creates valid backup
- Unarchive restores correctly
- Data integrity maintained
- Handles missing files gracefully

---

## Phase 2: Choice Configuration System

### 2.1 Define Choice Schema ✅

**File to create:** `tests/fixtures/progression_choices_schema.yaml`

**Schema definition:**
```yaml
character_template:
  name: string
  class: string
  subclass: string
  species: string | "random"
  background: string | "random"
  ability_scores:
    method: "standard_array" | "point_buy" | "manual"
    values:
      strength: int
      dexterity: int
      constitution: int
      intelligence: int
      wisdom: int
      charisma: int
  starting_equipment: "default" | "custom"

progression_choices:
  level_1:
    fighting_style: string  # "dueling", "defense", etc.
  level_3:
    subclass: string  # "champion"
  level_4:
    choice_type: "asi" | "feat"
    asi:
      ability_1: string
      ability_1_increase: int
      ability_2: string | null
      ability_2_increase: int | null
    feat: string | null
  # ... repeat for ASI levels
  champion_level_7:
    additional_fighting_style: string
```

### 2.2 Create Fighter Choice Templates ✅

**File to create:** `tests/fixtures/fighter_champion_choices.yaml`

**Example configuration:**
```yaml
character_template:
  name: "Testhammer the Brave"
  class: "fighter"
  subclass: "champion"
  species: "random"  # Randomly select from available species
  background: "random"  # Randomly select from available backgrounds
  ability_scores:
    method: "standard_array"
    values:
      strength: 15
      dexterity: 14
      constitution: 13
      intelligence: 12
      wisdom: 10
      charisma: 8
  starting_equipment: "default"

progression_choices:
  level_1:
    fighting_style: "dueling"

  level_3:
    subclass: "champion"

  level_4:
    choice_type: "asi"
    asi:
      ability_1: "strength"
      ability_1_increase: 2

  level_6:
    choice_type: "asi"
    asi:
      ability_1: "strength"
      ability_1_increase: 2

  champion_level_7:
    additional_fighting_style: "defense"

  level_8:
    choice_type: "asi"
    asi:
      ability_1: "constitution"
      ability_1_increase: 2

  level_12:
    choice_type: "feat"
    feat: "great_weapon_master"

  level_14:
    choice_type: "asi"
    asi:
      ability_1: "dexterity"
      ability_1_increase: 2

  level_16:
    choice_type: "asi"
    asi:
      ability_1: "constitution"
      ability_1_increase: 2
```

### 2.3 Create Choice Loader ✅

**File to create:** `tests/helpers/choice_loader.py`

**Purpose:** Load and validate choice configurations from YAML/JSON

**Features:**
```python
class ChoiceLoader:
    def load_from_yaml(file_path: str) -> dict:
        """Load choices from YAML file"""

    def load_from_json(file_path: str) -> dict:
        """Load choices from JSON file"""

    def validate_choices(choices: dict) -> bool:
        """Validate against schema"""

    def get_choice_for_level(choices: dict, level: int) -> dict:
        """Get specific level choices"""
```

---

## Phase 3: Progression Test Infrastructure

### 3.1 Create Progress Recorder ✅

**File to create:** `tests/helpers/progression_recorder.py`

**Purpose:** Record all character state changes and choices during progression

**Features:**
```python
class ProgressionRecorder:
    def __init__(self, character_id: str, output_dir: str):
        """Initialize recorder with output directory"""

    def record_level_snapshot(self, level: int, character_data: dict):
        """Record complete character state at level"""

    def record_choice(self, level: int, choice_type: str, choice_data: dict):
        """Record a choice made during progression"""

    def record_features_granted(self, level: int, features: List[str]):
        """Record features granted at level"""

    def generate_json_report(self) -> str:
        """Generate JSON progression log"""

    def generate_markdown_report(self) -> str:
        """Generate human-readable markdown report"""
```

**Output files:**
- `fighter_progression_[timestamp].json` - Machine-readable log
- `fighter_progression_[timestamp].md` - Human-readable report

### 3.2 Create Species/Background Randomizer ✅

**File to create:** `tests/helpers/random_selector.py`

**Purpose:** Randomly select species and backgrounds for test variety

**Features:**
```python
class RandomSelector:
    def get_random_species(db_path: str) -> str:
        """Query database for available species, return random choice"""

    def get_random_background(db_path: str) -> str:
        """Query database for available backgrounds, return random choice"""

    def get_species_list(db_path: str) -> List[str]:
        """List all available species"""

    def get_background_list(db_path: str) -> List[str]:
        """List all available backgrounds"""
```

---

## Phase 4: Character Progression Implementation

### 4.1 Create Progression Test Framework ✅

**File to create:** `tests/test_fighter_progression_complete.py`

**Main test class:**
```python
class TestFighterProgression:

    @classmethod
    def setup_class(cls):
        """Archive database before tests"""
        cls.archive_path = DatabaseArchiver.archive("talekeeper.db")
        cls.recorder = ProgressionRecorder("fighter_test", "tests/output")
        cls.choices = ChoiceLoader.load_from_yaml(
            "tests/fixtures/fighter_champion_choices.yaml"
        )

    @classmethod
    def teardown_class(cls):
        """Unarchive database after tests"""
        DatabaseArchiver.unarchive(cls.archive_path, "talekeeper.db")

    def test_01_create_character(self):
        """Create level 1 Fighter using ProgrammaticCharacterCreator"""

    def test_02_level_up_to_2(self):
        """Level up to 2, verify Action Surge"""

    def test_03_level_up_to_3_champion(self):
        """Level up to 3, select Champion subclass"""

    def test_04_level_up_to_4_asi(self):
        """Level up to 4, apply first ASI"""

    # ... tests for each level through 20

    def test_21_generate_reports(self):
        """Generate final progression reports"""
```

### 4.2 Backend Function Wrappers ✅

**Create wrappers in test class:**

```python
def _create_fighter_level_1(self, choices: dict) -> str:
    """
    Uses: ProgrammaticCharacterCreator
    Returns: character_id
    """
    # Handle random species/background
    # Create character template
    # Call create_from_dict()
    # Verify in database
    # Record initial state

def _add_xp_for_level(self, character_id: str, target_level: int):
    """
    Uses: GameEngine.update_experience_points()
    Calculates XP needed for target level
    """

def _level_up_character(self, character_id: str, level: int, choices: dict):
    """
    Uses: UnifiedLevelUpService.level_up_character()
    Handles subclass selection, ASI/Feat choices
    Records choices made
    Verifies features granted
    """
```

---

## Phase 5: Fighter-Specific Progression Logic

### 5.1 Level-by-Level Implementation

**Level 1 - Character Creation:**
- **Choices:**
  - Fighting Style: From choices YAML
  - Species: Random or specified
  - Background: Random or specified
  - Ability Scores: From choices YAML (standard array recommended)
- **Weapon Masteries:** ALL MASTERIES (no selection needed - simplified)
- **Verify:**
  - Character exists in `characters` table
  - Fighter entry in `character_class_levels`
  - Fighting style in `fighter_features.fighting_style`
  - Second Wind uses = 2
  - Weapon mastery count = ALL (no tracking needed)
- **Record:**
  - Character ID
  - Fighting style chosen
  - Species and background selected
  - Starting ability scores

**Level 2 - Action Surge:**
- **Choices:** None
- **Verify:**
  - `fighter_features.action_surge_uses = 1`
  - Feature "Action Surge" in `character_features`
  - Feature "Tactical Mind" in `character_features`
- **Record:**
  - Features granted
  - Resource counts

**Level 3 - Champion Subclass:**
- **Choices:**
  - Subclass: Champion (from choices YAML)
- **Verify:**
  - Entry in `character_subclasses` (character_id, class_id='fighter', subclass_id='champion')
  - `character_combat_state.critical_range_min = 19` (Improved Critical)
  - Features: "Improved Critical", "Remarkable Athlete"
- **Record:**
  - Subclass selection
  - Subclass features granted
  - Critical range change

**Level 4 - First ASI:**
- **Choices:**
  - ASI or Feat (from choices YAML)
  - If ASI: ability score increases
  - If Feat: feat name
- **Verify:**
  - Ability scores updated in `characters` table (if ASI)
  - Feat entry in `character_feats` (if feat)
  - Second Wind uses = 3
- **Record:**
  - Choice type (ASI/Feat)
  - Ability scores after increase
  - OR feat selected

**Level 5 - Extra Attack:**
- **Choices:** None
- **Verify:**
  - `fighter_features.extra_attacks = 2`
  - Features: "Extra Attack", "Tactical Shift"
- **Record:**
  - Extra attacks count
  - Features granted

**Level 6 - Second ASI:**
- **Choices:** ASI or Feat (from choices YAML)
- **Verify:** Same as level 4
- **Record:** Same as level 4

**Level 7 - Champion Additional Fighting Style:**
- **Choices:**
  - Additional Fighting Style (from choices YAML - must be different from level 1)
- **Verify:**
  - Second fighting style stored (exact storage mechanism varies by implementation)
  - Feature "Additional Fighting Style" granted
- **Record:**
  - Second fighting style chosen
  - Both fighting styles active

**Level 8 - Third ASI:**
- **Choices:** ASI or Feat (from choices YAML)
- **Verify:** Same as level 4
- **Record:** Same as level 4

**Level 9 - Indomitable:**
- **Choices:** None
- **Verify:**
  - Indomitable uses = 1 (stored in appropriate table)
  - Features: "Indomitable", "Tactical Master"
- **Record:**
  - Features granted
  - Resource counts

**Level 10 - Champion Heroic Warrior:**
- **Choices:** None
- **Verify:**
  - Second Wind uses = 4
  - Champion feature "Heroic Warrior" granted
- **Record:**
  - Champion feature granted
  - Resource updates

**Level 11 - Two Extra Attacks:**
- **Choices:** None
- **Verify:**
  - `fighter_features.extra_attacks = 3`
  - Feature updated
- **Record:**
  - Extra attacks count

**Level 12 - Fourth ASI:**
- **Choices:** ASI or Feat (from choices YAML)
- **Verify:** Same as level 4
- **Record:** Same as level 4

**Level 13 - Indomitable Improvement:**
- **Choices:** None
- **Verify:**
  - Indomitable uses = 2
  - Feature "Studied Attacks" granted
- **Record:**
  - Resource updates
  - Features granted

**Level 14 - Fifth ASI:**
- **Choices:** ASI or Feat (from choices YAML)
- **Verify:** Same as level 4
- **Record:** Same as level 4

**Level 15 - Champion Superior Critical:**
- **Choices:** None
- **Verify:**
  - `character_combat_state.critical_range_min = 18` (Superior Critical replaces Improved)
  - Feature "Superior Critical" granted (replaces "Improved Critical")
- **Record:**
  - Critical range change
  - Feature upgrade

**Level 16 - Sixth ASI:**
- **Choices:** ASI or Feat (from choices YAML)
- **Verify:** Same as level 4
- **Record:** Same as level 4

**Level 17 - Resource Improvements:**
- **Choices:** None
- **Verify:**
  - Action Surge uses = 2
  - Indomitable uses = 3
- **Record:**
  - Resource updates

**Level 18 - Champion Survivor:**
- **Choices:** None
- **Verify:**
  - Feature "Survivor" granted (Defy Death, Heroic Rally mechanics)
- **Record:**
  - Champion capstone feature

**Level 19 - Epic Boon:**
- **Choices:** Epic Boon selection (from choices YAML)
- **Verify:**
  - Epic Boon feat in `character_feats`
  - Feature "Epic Boon" granted
- **Record:**
  - Epic Boon selected

**Level 20 - Three Extra Attacks:**
- **Choices:** None
- **Verify:**
  - `fighter_features.extra_attacks = 4`
  - Maximum Fighter level reached
- **Record:**
  - Final extra attacks count
  - Character progression complete

### 5.2 Feature Verification Matrix

**Create verification helper:**
```python
EXPECTED_FEATURES_BY_LEVEL = {
    1: ["fighting_style", "second_wind", "weapon_mastery"],
    2: ["action_surge", "tactical_mind"],
    3: ["improved_critical", "remarkable_athlete"],
    5: ["extra_attack", "tactical_shift"],
    7: ["additional_fighting_style"],
    9: ["indomitable", "tactical_master"],
    10: ["heroic_warrior"],
    11: ["two_extra_attacks"],
    13: ["studied_attacks"],
    15: ["superior_critical"],
    18: ["survivor"],
    19: ["epic_boon"],
    20: ["three_extra_attacks"],
}

EXPECTED_RESOURCES_BY_LEVEL = {
    1: {"second_wind": 2, "action_surge": 0, "indomitable": 0},
    2: {"second_wind": 2, "action_surge": 1, "indomitable": 0},
    4: {"second_wind": 3, "action_surge": 1, "indomitable": 0},
    9: {"second_wind": 3, "action_surge": 1, "indomitable": 1},
    10: {"second_wind": 4, "action_surge": 1, "indomitable": 1},
    13: {"second_wind": 4, "action_surge": 1, "indomitable": 2},
    17: {"second_wind": 4, "action_surge": 2, "indomitable": 3},
}

EXPECTED_EXTRA_ATTACKS = {
    1: 1, 5: 2, 11: 3, 20: 4
}

EXPECTED_CRITICAL_RANGE = {
    1: 20, 3: 19, 15: 18
}
```

---

## Phase 6: Report Generation

### 6.1 JSON Output Format ✅

**File:** `tests/output/fighter_progression_[timestamp].json`

**Structure:**
```json
{
  "character_id": "fighter_test_12345",
  "character_name": "Testhammer the Brave",
  "class": "fighter",
  "subclass": "champion",
  "species": "dwarf",
  "background": "soldier",
  "test_timestamp": "2025-11-07T14:30:00Z",
  "final_level": 20,

  "initial_state": {
    "ability_scores": {
      "strength": 15,
      "dexterity": 14,
      "constitution": 13,
      "intelligence": 12,
      "wisdom": 10,
      "charisma": 8
    },
    "fighting_style": "dueling",
    "starting_hp": 10
  },

  "progression": [
    {
      "level": 1,
      "xp_required": 0,
      "choices_made": {
        "fighting_style": "dueling",
        "species": "dwarf",
        "background": "soldier"
      },
      "features_granted": [
        "fighting_style",
        "second_wind",
        "weapon_mastery"
      ],
      "resources": {
        "second_wind_uses": 2,
        "action_surge_uses": 0,
        "indomitable_uses": 0
      },
      "ability_scores": {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8
      },
      "hp_max": 10,
      "extra_attacks": 1,
      "critical_range_min": 20
    },
    {
      "level": 2,
      "xp_required": 300,
      "choices_made": {},
      "features_granted": [
        "action_surge",
        "tactical_mind"
      ],
      "resources": {
        "second_wind_uses": 2,
        "action_surge_uses": 1,
        "indomitable_uses": 0
      },
      "ability_scores": { /* same */ },
      "hp_max": 16,
      "extra_attacks": 1,
      "critical_range_min": 20
    },
    {
      "level": 3,
      "xp_required": 900,
      "choices_made": {
        "subclass": "champion"
      },
      "features_granted": [
        "improved_critical",
        "remarkable_athlete"
      ],
      "resources": { /* same */ },
      "ability_scores": { /* same */ },
      "hp_max": 22,
      "extra_attacks": 1,
      "critical_range_min": 19
    },
    // ... levels 4-20
  ],

  "summary": {
    "total_features_gained": 45,
    "asi_taken": 4,
    "feats_taken": 2,
    "final_ability_scores": {
      "strength": 20,
      "dexterity": 16,
      "constitution": 17,
      "intelligence": 12,
      "wisdom": 10,
      "charisma": 8
    },
    "final_resources": {
      "second_wind_uses": 4,
      "action_surge_uses": 2,
      "indomitable_uses": 3
    },
    "final_extra_attacks": 4,
    "final_critical_range_min": 18
  }
}
```

### 6.2 Markdown Report Format ✅

**File:** `tests/output/fighter_progression_[timestamp].md`

**Structure:**
```markdown
# Fighter (Champion) Progression Test Report

**Character:** Testhammer the Brave
**Species:** Dwarf
**Background:** Soldier
**Test Date:** 2025-11-07 14:30:00
**Result:** ✅ PASSED ALL LEVELS

---

## Initial Character State

| Attribute | Value |
|-----------|-------|
| STR | 15 |
| DEX | 14 |
| CON | 13 |
| INT | 12 |
| WIS | 10 |
| CHA | 8 |
| HP | 10 |
| Fighting Style | Dueling |

---

## Progression by Level

### Level 1 - Fighter Base

**XP Required:** 0
**Features Gained:**
- Fighting Style (Dueling)
- Second Wind (2 uses)
- Weapon Mastery (All Masteries)

**Choices Made:**
- Fighting Style: Dueling
- Species: Dwarf (random)
- Background: Soldier (random)

**Resources:**
- Second Wind: 2 uses
- Action Surge: 0 uses

**Status:** ✅ PASS

---

### Level 2 - Action Surge

**XP Required:** 300
**Features Gained:**
- Action Surge (1 use)
- Tactical Mind

**Choices Made:** None

**Resources:**
- Second Wind: 2 uses
- Action Surge: 1 use

**Status:** ✅ PASS

---

### Level 3 - Champion Subclass

**XP Required:** 900
**Features Gained:**
- Improved Critical (19-20)
- Remarkable Athlete

**Choices Made:**
- Subclass: Champion

**Combat Changes:**
- Critical Range: 20 → 19

**Status:** ✅ PASS

---

<!-- Continue for all 20 levels -->

---

## Final Summary

### Ability Score Progression

| Ability | Start | Final | Total Increase |
|---------|-------|-------|----------------|
| STR | 15 | 20 | +5 |
| DEX | 14 | 16 | +2 |
| CON | 13 | 17 | +4 |
| INT | 12 | 12 | +0 |
| WIS | 10 | 10 | +0 |
| CHA | 8 | 8 | +0 |

### ASI/Feat Choices

| Level | Choice | Details |
|-------|--------|---------|
| 4 | ASI | STR +2 (15→17) |
| 6 | ASI | STR +2 (17→19, racial +1→20) |
| 8 | ASI | CON +2 (13→15) |
| 12 | Feat | Great Weapon Master |
| 14 | ASI | DEX +2 (14→16) |
| 16 | ASI | CON +2 (15→17) |

### Feature Summary

**Total Features Gained:** 45
**Fighting Styles:** Dueling, Defense
**Extra Attacks:** 4
**Critical Range:** 18-20

**Resources (Max):**
- Second Wind: 4 uses per short rest
- Action Surge: 2 uses per short rest
- Indomitable: 3 uses per long rest

### Test Statistics

- **Total Tests Run:** 20
- **Tests Passed:** 20
- **Tests Failed:** 0
- **Duration:** 45.2 seconds

**Overall Result:** ✅ ALL TESTS PASSED
```

---

## Phase 7: Execution Plan

### 7.1 Implementation Order

1. **Database Archiver** (Day 1)
   - Create `database_archiver.py`
   - Create `test_database_archiver.py`
   - Test archive/unarchive functionality

2. **Choice System** (Day 1-2)
   - Create `progression_choices_schema.yaml`
   - Create `fighter_champion_choices.yaml`
   - Create `choice_loader.py`
   - Create `random_selector.py`

3. **Recording System** (Day 2)
   - Create `progression_recorder.py`
   - Test JSON and Markdown output

4. **Main Test Implementation** (Day 3-4)
   - Create `test_fighter_progression_complete.py`
   - Implement character creation wrapper
   - Implement XP addition wrapper
   - Implement level-up wrapper
   - Implement verification helpers

5. **Level-by-Level Tests** (Day 4-5)
   - Implement tests for levels 1-5
   - Implement tests for levels 6-10
   - Implement tests for levels 11-15
   - Implement tests for levels 16-20

6. **Verification & Reports** (Day 5-6)
   - Run complete test suite
   - Generate reports
   - Validate against SRD 2024 rules
   - Debug any failures

### 7.2 Running the Tests

**Command:**
```bash
python -m pytest tests/test_fighter_progression_complete.py -v -s
```

**Options:**
- `-v` : Verbose output
- `-s` : Show print statements
- `--tb=short` : Short traceback format
- `-k test_03` : Run specific test by name

**Expected output:**
```
tests/test_fighter_progression_complete.py::TestFighterProgression::test_01_create_character PASSED
tests/test_fighter_progression_complete.py::TestFighterProgression::test_02_level_up_to_2 PASSED
tests/test_fighter_progression_complete.py::TestFighterProgression::test_03_level_up_to_3_champion PASSED
...
tests/test_fighter_progression_complete.py::TestFighterProgression::test_20_level_up_to_20 PASSED
tests/test_fighter_progression_complete.py::TestFighterProgression::test_21_generate_reports PASSED

==================== 21 passed in 45.23s ====================
```

### 7.3 Test Artifacts

**Generated files:**
- `tests/archives/talekeeper.db.archive.[timestamp]` - Database backup
- `tests/output/fighter_progression_[timestamp].json` - JSON log
- `tests/output/fighter_progression_[timestamp].md` - Markdown report
- `talekeeper.db` - Restored to original state

---

## Success Criteria

- ✅ Database archiver creates and restores backups correctly
- ✅ Tests run against real production database
- ✅ Character created using `ProgrammaticCharacterCreator` (backend API)
- ✅ All levels 1-20 completed successfully
- ✅ Champion subclass selected at level 3
- ✅ All ASI/Feat choices from YAML applied correctly
- ✅ Species and background randomly selected (when specified as "random")
- ✅ Weapon masteries simplified (all masteries assumed)
- ✅ All features verified against expected values
- ✅ All resource counts correct at all levels
- ✅ JSON and Markdown reports generated
- ✅ Database restored to original state after tests
- ✅ All 21 tests pass without errors

---

## Future Extensions

Once Fighter progression is working, this framework can be extended to:
- **Other Fighter Subclasses:** Battle Master, Eldritch Knight, etc.
- **Other Classes:** Rogue, Wizard, Cleric, Barbarian, etc.
- **Multiclass Testing:** Fighter/Rogue, Paladin/Warlock, etc.
- **Edge Cases:** Death saves, condition tracking, etc.
- **Performance Testing:** Time to create 100 characters

**Extension pattern:**
1. Copy `fighter_champion_choices.yaml` to `rogue_thief_choices.yaml`
2. Modify choices for Rogue-specific features
3. Create `test_rogue_progression_complete.py` based on Fighter test
4. Reuse all infrastructure (archiver, recorder, loader)

---

## Notes & Decisions

### Why Real Database?
Using the real production database ensures we're testing against:
- Actual schema with all constraints
- Real foreign key relationships
- Production triggers and indexes
- Actual data types and validations

Archive/unarchive mechanism provides safety while maintaining realism.

### Why Simplify Weapon Masteries?
SRD 2024 has extensive weapon mastery lists and Fighters can swap them frequently. For testing character progression mechanics, we can assume all masteries are known without impacting the validity of testing:
- Level-up mechanics
- Feature granting
- Resource calculations
- ASI/Feat choices
- Subclass features

This simplification reduces test complexity while maintaining comprehensive coverage of the progression system.

### Why Random Species/Background?
Random selection adds test variety and ensures the system works with different starting conditions. Each test run will have slightly different initial states, improving coverage of edge cases.

---

**PLAN STATUS: LOCKED - READY FOR IMPLEMENTATION**
