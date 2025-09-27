# Spell Selection & Management Implementation Plan

## Executive Summary

**Goal**: Complete the spell selection experience for TaleKeeper's spellcasting classes (Cleric, Wizard, Paladin, Warlock)

**Status**: Core spellcasting infrastructure exists but lacks UI and spell data

**Timeline**: 5-7 days

---

## Current State Analysis

### ✅ What Exists (Working)

1. **Database Schema** - ALL TABLES ALREADY EXIST ✅
   - ✅ `spells` table with full spell definitions
   - ✅ `character_spells` table for known/prepared spells (tracks per-character spell knowledge and preparation)
   - ✅ `wizard_spellbook` table for wizard-specific spellbook tracking
   - ✅ `character_spell_slots` table for slot tracking
   - ✅ `character_spellcasting` table for casting stats
   - ✅ `spell_class_lists` table (exists but empty - optional, spells.classes JSON works)

2. **Backend Services**
   - ✅ `services/spellcasting_service.py` - Core spell mechanics
   - ✅ `services/spell_registry.py` - Spell definitions registry
   - ✅ `services/ritual_casting_service.py` - Ritual casting
   - ✅ `services/concentration_system.py` - Concentration tracking
   - ✅ Warlock/Wizard/Cleric/Paladin ability services

3. **UI Integration**
   - ✅ Spell action cards generation
   - ✅ Spell slot displays in character sheet
   - ✅ Combat spell casting
   - ✅ Concentration tracking in combat

4. **Character Creation**
   - ✅ Class selection
   - ✅ Skill proficiency selection
   - ✅ Fighting style/invocation selection for Fighter/Warlock
   - ❌ **NO cantrip selection**
   - ❌ **NO spell selection**

### ❌ Critical Gaps

1. **Spell Data** (HIGHEST PRIORITY)
   - Only 15 spells in database (need ~200+ core spells)
   - Missing cantrips for all classes
   - Missing essential level 1-5 spells
   - `spell_class_lists` table is empty

2. **Character Creation UI**
   - No cantrip selection step
   - No spell selection step
   - No spell preparation interface
   - Classes created with empty spell lists

3. **Spell Management UI**
   - No way to learn new spells (Wizard spellbook)
   - No way to prepare spells (Cleric/Wizard/Paladin)
   - No way to swap prepared spells
   - No level-up spell selection

4. **Class-Specific Features**
   - Warlock: Invocation selection works (level 1) but needs spell selection
   - Wizard: No spellbook UI
   - Cleric: No prepared spell selection
   - Paladin: No prepared spell selection

---

## Implementation Phases

### Phase 1: Spell Data Population (Days 1-2) 🔴 CRITICAL

**📋 See detailed plan: [`PHASE_1_SPELL_DATA_DETAILED_PLAN.md`](PHASE_1_SPELL_DATA_DETAILED_PLAN.md)**

**Goal**: Populate database with D&D 2024 core spells for level 1 character creation

**Scope Change**: Focus on cantrips + level 1 spells only (60 spells total) - enough for character creation

#### Step 1.1: Create Cantrip Seed File (Day 1)
- [ ] Create `database/seeds/010_spells_cantrips.sql` (20 cantrips)
  - [ ] Combat cantrips: Eldritch Blast, Fire Bolt, Sacred Flame, etc. (8 spells)
  - [ ] Utility cantrips: Mage Hand, Light, Guidance, Prestidigitation, etc. (12 spells)
  - [ ] Source: SRD lines 3570-3580 (Cleric), 6609-6617 (Warlock), 6974-6990 (Wizard)

#### Step 1.2: Create Level 1 Spell Seed File (Days 1-2)
- [ ] Create `database/seeds/011_spells_level1.sql` (40 level-1 spells)
  - [ ] Universal: Shield, Mage Armor, Bless, Healing Word, etc. (10 spells)
  - [ ] Wizard-specific: Find Familiar, Burning Hands, Feather Fall, etc. (15 spells)
  - [ ] Cleric-specific: Guiding Bolt, Inflict Wounds, Shield of Faith, etc. (8 spells)
  - [ ] Warlock-specific: Hex, Hellish Rebuke, Charm Person, etc. (5 spells)
  - [ ] Paladin-specific: Heroism, Searing Smite (2 spells)
  - [ ] Source: SRD lines 3581-3597 (Cleric), 4997-5012 (Paladin), 6618-6631 (Warlock), 6991-7021 (Wizard)

**Priority Spells by Class:**
- **Warlock**: Eldritch Blast, Hex, Armor of Agathys, Hellish Rebuke
- **Wizard**: Fire Bolt, Mage Armor, Shield, Magic Missile, Fireball
- **Cleric**: Sacred Flame, Healing Word, Cure Wounds, Bless, Spirit Guardians
- **Paladin**: Bless, Shield of Faith, Smite spells

**Minimum Viable Spell Count**:
- Cantrips: 20-30
- Level 1: 40-50
- Level 2-5: 20-30 each
- **Total**: ~150-200 spells

#### Step 1.2: Run Seed Script
```bash
sqlite3 talekeeper.db < database/seeds/spells_cantrips.sql
sqlite3 talekeeper.db < database/seeds/spells_level1.sql
# ... etc
```

**Validation**:
```bash
sqlite3 talekeeper.db "SELECT level, COUNT(*) FROM spells GROUP BY level"
```

---

### Phase 2: Character Creation - Spell Selection UI (Days 3-4)

**Goal**: Add spell/cantrip selection during character creation

#### Step 2.1: Add Spellcasting Step to Character Creation

**File**: `encounter_pane/encounter_panel.py`

Current steps:
1. Class Selection
2. Class Features (Fighting Style, Invocations, etc.)
3. Background & Species
4. Ability Scores
5. Equipment
6. Final Review

**New structure**:
1. Class Selection
2. Class Features (Fighting Style, Invocations, etc.)
3. **🆕 Spells & Cantrips** (NEW STEP - only shown for spellcasters)
4. Background & Species
5. Ability Scores
6. Equipment
7. Final Review

#### Step 2.2: Create Spell Selection Widget

Create `encounter_pane/spell_selection_widget.py`:

```python
class SpellSelectionWidget(QWidget):
    """Widget for selecting cantrips and spells during character creation."""

    def __init__(self, character_class: str, level: int = 1):
        # Load spell requirements from database
        # Display cantrip selection (combo boxes)
        # Display spell selection (checkboxes with limits)
        # Filter by class availability
        # Show spell details on hover/click
```

**Features**:
- Separate sections for cantrips and spells
- Spell filtering by class
- Spell level grouping
- Spell description preview
- Selection count tracking (e.g., "Selected: 2 / 2 cantrips")
- Validation before proceeding

#### Step 2.3: Class-Specific Spell Requirements (D&D 2024)

**Wizard (Level 1)** - Per D&D 2024 Table:
- Cantrips: 3 (from wizard list) → Save to `character_spells` (always_prepared=1)
- Spellbook: 6 level-1 spells → Save to `wizard_spellbook` table
- Prepared: 4 spells from spellbook (Int mod + level, shown as base 4) → Mark in `character_spells` (is_prepared=1)
- Spell Slots: 2 level-1 slots

**Cleric (Level 1)**:
- Cantrips: 3 (from cleric list) → Save to `character_spells` (always_prepared=1)
- Prepared: Int mod + level (estimate 4-5 at level 1) from entire cleric spell list
- Always prepared: Domain spells (2 at level 1) → Save with `always_prepared=1`
- Spell Slots: 2 level-1 slots

**Warlock (Level 1)**:
- Cantrips: 2 (from warlock list) → Save to `character_spells` (always_prepared=1)
- Spells Known: 2 (from warlock list, level 1 only) → Save to `character_spells` (always prepared for warlocks)
- Invocations: 1 (already implemented ✅) → Save to `warlock_invocations` table
- Pact Slots: 1 level-1 slot (recovers on short rest)

**Paladin (Level 1)** - Per D&D 2024 Table:
- NO cantrips at level 1 (can get 2 via Blessed Warrior fighting style at level 2)
- Prepared: 2 level-1 Paladin spells → Save to `character_spells` (is_prepared=1)
- Spell Slots: 2 level-1 slots
- Note: Paladins prepare from entire Paladin spell list (like Clerics)

#### Step 2.4: Integration with Character Creation Flow

**File**: `encounter_pane/encounter_panel.py`

Modify `_setup_character_creation_steps()`:
```python
def _setup_character_creation_steps(self):
    self.class_step = self._create_class_selection_step()
    self.creation_stack.addWidget(self.class_step)

    self.class_features_step = self._create_class_features_step()
    self.creation_stack.addWidget(self.class_features_step)

    # NEW: Spells step (conditionally shown)
    self.spells_step = self._create_spells_step()
    self.creation_stack.addWidget(self.spells_step)
    self.spells_step_index = 2  # Track index

    # ... rest of steps
```

Modify `_update_creation_step()`:
```python
def _update_creation_step(self):
    # Show/hide spell step based on class
    selected_class = self.character_creation_data.get('class')
    if selected_class:
        class_name = selected_class.get('name', '')
        is_spellcaster = class_name in ['Wizard', 'Cleric', 'Warlock', 'Paladin']

        # Skip spell step for non-spellcasters only
        # NOTE: In D&D 2024, Paladins get spells at level 1 (2 prepared spells, 2 slots)
        if not is_spellcaster:
            # Adjust step navigation to skip spell step
            pass

    self.creation_stack.setCurrentIndex(self.creation_step)
    # ... rest of method
```

#### Step 2.5: Save Selected Spells

**File**: `encounter_pane/encounter_panel.py`

Modify `_finalize_character_creation()`:
```python
final_character = {
    # ... existing fields
    'selected_cantrips': self.character_creation_data.get('selected_cantrips', []),
    'selected_spells': self.character_creation_data.get('selected_spells', []),
    'prepared_spells': self.character_creation_data.get('prepared_spells', []),
}
```

**File**: `core/game_engine_sqlite.py`

Modify `_initialize_wizard_features()`, `_initialize_cleric_features()`, etc.:
```python
def _initialize_wizard_features(self, cursor, character_id, character_data):
    # ... existing code

    # Save selected cantrips
    selected_cantrips = character_data.get('selected_cantrips', [])
    for cantrip_id in selected_cantrips:
        cursor.execute("""
            INSERT INTO character_spells
            (character_id, spell_id, spell_level, is_prepared, source, always_prepared)
            VALUES (?, ?, 0, 1, 'class', 1)
        """, (character_id, cantrip_id))

    # Save spellbook (for wizard)
    if 'selected_spells' in character_data:
        for spell_id in character_data['selected_spells']:
            cursor.execute("""
                INSERT INTO wizard_spellbook
                (character_id, spell_id, spell_level, learned_at_level, source)
                VALUES (?, ?, 1, 1, 'level_up')
            """, (character_id, spell_id))

    # ... rest of initialization
```

---

### Phase 3: Spell Management UI (Days 5-6)

**Goal**: Allow players to manage spells after character creation

#### Step 3.1: Spell Preparation Dialog

Create `ui/spell_preparation_dialog.py`:

```python
class SpellPreparationDialog(QDialog):
    """Dialog for preparing spells (Cleric, Wizard, Paladin)."""

    def __init__(self, character_id: str, class_name: str):
        # Load character's known spells
        # Show currently prepared spells
        # Allow toggling preparation status
        # Enforce preparation limits
        # Save changes to database
```

**Features**:
- List all known spells
- Toggle prepared status
- Show preparation limit (e.g., "6 / 8 prepared")
- Always-prepared spells (domains, invocations) marked differently
- Sort by level, name, or school
- Search/filter spells

#### Step 3.2: Wizard Spellbook UI

Create `ui/wizard_spellbook_dialog.py`:

```python
class WizardSpellbookDialog(QDialog):
    """Dialog for wizard spellbook management."""

    def __init__(self, character_id: str):
        # Display spellbook spells
        # Show spell copying interface
        # Calculate gold/time costs
        # Add new spells to spellbook
```

**Features**:
- View all spellbook spells
- Copy spells from scrolls/other spellbooks
- Gold cost calculation (50 gp × spell level)
- Time calculation (2 hours × spell level)
- Integration with inventory (need scroll/spellbook item)

#### Step 3.3: Add Menu/Button to Access Spell Management

**File**: `ui/main_window.py` or `character_sheet/character_panel.py`

Add button to character sheet:
- "Manage Spells" button (for spellcasters)
- Opens appropriate dialog based on class
- Shows spell preparation for Cleric/Wizard/Paladin
- Shows spellbook for Wizard
- Shows invocations for Warlock (if needed)

#### Step 3.4: Level-Up Spell Selection

**File**: Wherever level-up logic exists

When character levels up:
1. Calculate new cantrips/spells known
2. Show spell selection dialog if gained new slots
3. For Wizard: Add 2 spells to spellbook
4. For Warlock: Update invocations if applicable
5. Save selections to database

---

### Phase 4: Testing & Refinement (Day 7)

**Goal**: Validate all spell selection works correctly

#### Step 4.1: Character Creation Tests

- [ ] Create Warlock - verify 2 cantrips + 2 spells + 1 invocation selected
- [ ] Create Wizard - verify 3 cantrips + 6 spellbook + 4 prepared
- [ ] Create Cleric - verify 3 cantrips + prepared spells + domain spells
- [ ] Create Paladin - verify NO cantrips + 2 prepared spells (D&D 2024: spells start at level 1)
- [ ] Create Fighter - verify spell step skipped

#### Step 4.2: Spell Management Tests

- [ ] Prepare/unprepare spells as Cleric
- [ ] Add spells to wizard spellbook
- [ ] Cast spells in combat (use spell slots)
- [ ] Verify concentration works
- [ ] Verify ritual casting works

#### Step 4.3: Database Validation

```bash
# Check spell counts
sqlite3 talekeeper.db "SELECT level, COUNT(*) FROM spells GROUP BY level"

# Check character has spells
sqlite3 talekeeper.db "SELECT * FROM character_spells WHERE character_id = '...'"

# Check spell slots
sqlite3 talekeeper.db "SELECT * FROM character_spell_slots WHERE character_id = '...'"
```

#### Step 4.4: Edge Cases

- [ ] Multiclassing (if applicable)
- [ ] Replacing spells on level-up
- [ ] Swapping prepared spells during long rest
- [ ] Invalid spell selections (wrong class, too high level)

---

## Implementation Checklist

### Phase 1: Spell Data 🔴 CRITICAL
- [ ] Create cantrip seed file (20-30 cantrips)
- [ ] Create level 1 spell seed file (40-50 spells)
- [ ] Create level 2-5 spell seed files (20-30 each)
- [ ] Run all seed scripts
- [ ] Verify spell counts in database
- [ ] Verify class associations are correct

### Phase 2: Character Creation UI
- [ ] Add spell selection step to character creation
- [ ] Create spell selection widget
- [ ] Implement cantrip selection UI
- [ ] Implement spell selection UI (checkboxes with limits)
- [ ] Add spell descriptions/tooltips
- [ ] Integrate with Warlock character creation
- [ ] Integrate with Wizard character creation
- [ ] Integrate with Cleric character creation
- [ ] Skip for Paladin at level 1
- [ ] Save selected spells to database
- [ ] Update `_initialize_warlock_features()` to save spells
- [ ] Update `_initialize_wizard_features()` to save spells
- [ ] Update `_initialize_cleric_features()` to save spells
- [ ] Test character creation flow end-to-end

### Phase 3: Spell Management UI
- [ ] Create spell preparation dialog
- [ ] Add "Manage Spells" button to character sheet
- [ ] Implement prepare/unprepare toggle
- [ ] Enforce preparation limits
- [ ] Create wizard spellbook dialog
- [ ] Implement spell copying mechanics
- [ ] Add level-up spell selection
- [ ] Test spell management workflows

### Phase 4: Testing & Polish
- [ ] Test all 4 spellcasting classes in character creation
- [ ] Test spell casting in combat
- [ ] Test spell slot depletion/recovery
- [ ] Test concentration mechanics
- [ ] Test ritual casting
- [ ] Test edge cases
- [ ] Performance testing with 200+ spells
- [ ] Update CLAUDE.md with spell selection commands

---

## Database Schema Reference

### Spells Table (Existing ✅)
```sql
CREATE TABLE spells (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,  -- 0 = cantrip
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_value TEXT NOT NULL,
    components TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    higher_levels TEXT,
    source TEXT DEFAULT 'PHB',
    classes TEXT  -- JSON array: ["wizard", "cleric"]
);
```

### Character Spells Table (Existing ✅)
```sql
CREATE TABLE character_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    is_prepared BOOLEAN DEFAULT TRUE,
    source TEXT NOT NULL,  -- 'class', 'domain', 'oath'
    source_level INTEGER,
    always_prepared BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (character_id, spell_id)
);
```

### Wizard Spellbook Table (Existing ✅)
```sql
CREATE TABLE wizard_spellbook (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    learned_at_level INTEGER NOT NULL,
    source TEXT DEFAULT 'level_up',
    cost_paid INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0,
    PRIMARY KEY (character_id, spell_id)
);
```

---

## API Reference

### Spell Registry (Existing ✅)
```python
from services.spell_registry import spell_registry

# Get spell by ID
spell = spell_registry.get_spell('fireball')

# Get spells for class
wizard_spells = spell_registry.get_spells_for_class('wizard', max_level=3)

# Get cantrips
cantrips = spell_registry.get_spells_by_level(0)
```

### Spellcasting Service (Existing ✅)
```python
from services.spellcasting_service import SpellcastingService

service = SpellcastingService()

# Initialize spellcasting
service.initialize_character_spellcasting(character_id, 'wizard')

# Get spell slots
slots = service.get_spell_slots(character_id)

# Cast spell
result = service.cast_spell(character_id, spell_id, slot_level)
```

---

## Risk Mitigation

### Database Integrity
- Always use transactions when modifying spell data
- Back up `talekeeper.db` before running new seed scripts
- Validate spell IDs match between tables

### UI Responsiveness
- Load spells lazily (don't load all 200+ at once)
- Use pagination for spell lists
- Cache frequently accessed spells

### Testing Strategy
```bash
# Before starting
cp talekeeper.db talekeeper_backup_before_spells.db

# After Phase 1 (spell data)
cp talekeeper.db talekeeper_backup_phase1.db

# After Phase 2 (character creation)
cp talekeeper.db talekeeper_backup_phase2.db
```

---

## Success Criteria

### Phase 1 Complete
- [ ] Database contains 150+ spells
- [ ] All cantrips for main 4 classes present
- [ ] Level 1-5 spells adequately represented
- [ ] Spell-to-class mappings correct

### Phase 2 Complete
- [ ] Can create Warlock with cantrips + spells + invocation
- [ ] Can create Wizard with cantrips + spellbook
- [ ] Can create Cleric with cantrips + prepared spells
- [ ] Can create Paladin (no spells at level 1)
- [ ] All selected spells saved to database correctly
- [ ] Character sheet shows learned spells

### Phase 3 Complete
- [ ] Can prepare/unprepare spells
- [ ] Can add spells to wizard spellbook
- [ ] Spell management UI is intuitive
- [ ] Level-up spell selection works

### Phase 4 Complete
- [ ] All character creation tests pass
- [ ] Spell casting in combat works
- [ ] No regressions in existing features
- [ ] Performance acceptable with full spell list

---

## Notes

### Design Decisions

**Why separate spell selection step?**
- Spell selection is complex enough to warrant its own step
- Cleaner separation of concerns
- Easier to skip for non-spellcasters

**Why not use spell_class_lists table?**
- Spells already store classes as JSON array
- Simpler to maintain single source of truth
- Can migrate later if needed

**Why prioritize character creation over spell management?**
- Character creation is blocking issue (can't create spellcasters properly)
- Spell management can be worked around (manual database edits)
- Better user experience to complete creation flow first

### Future Enhancements (Post-MVP)

- [ ] Spell favorites/hotkeys
- [ ] Spell damage calculator preview
- [ ] Spell range visualization
- [ ] Multiclass spell slot calculation
- [ ] Spell scroll creation (wizards)
- [ ] Expanded spell list (200+ → 500+)
- [ ] Homebrew spell support

---

## Timeline Summary

| Phase | Days | Status |
|-------|------|--------|
| Phase 1: Spell Data Population | 1-2 | ⏳ Not Started |
| Phase 2: Character Creation UI | 3-4 | ⏳ Not Started |
| Phase 3: Spell Management UI | 5-6 | ⏳ Not Started |
| Phase 4: Testing & Refinement | 7 | ⏳ Not Started |

**Total**: 7 days

---

## Getting Started

### Immediate Next Steps
1. ✅ Complete this planning document
2. ⏳ Create spell seed files (start with cantrips)
3. ⏳ Populate database with core spells
4. ⏳ Test spell queries work correctly
5. ⏳ Begin character creation UI modifications

### Command to Begin
```bash
# Create spell seed file
touch database/seeds/spells_cantrips.sql

# Start editing
# (Add INSERT statements for all D&D 2024 cantrips)
```

---

*This plan prioritizes getting spellcasters functional in character creation first, then adds convenience features for spell management.*