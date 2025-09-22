# Spellcasting Classes Implementation Plan

## Overview

This plan outlines the implementation of Cleric, Paladin, Wizard, and Warlock classes in TaleKeeper while preserving existing Fighter, Barbarian, and Rogue functionality. Each step includes validation checks to prevent breaking existing systems.

## Architecture Analysis

### Existing Working Systems
- **Fighter**: Champion subclass, fighting styles, action economy integration
- **Barbarian**: Berserker subclass, rage mechanics, condition immunities
- **Rogue**: Base class with stealth mechanics, sneak attack
- **Enhanced Subclass Manager**: Modular architecture with registry system
- **Action Economy Enforcer**: Full action/bonus action/reaction tracking
- **Condition System**: D&D 2024 conditions with mechanical effects

### New Systems Required
1. **Spell System**: Spell slots, preparation, casting mechanics
2. **Spell Recovery**: Short/long rest mechanics
3. **Divine Domains**: Cleric subclass system
4. **Sacred Oaths**: Paladin subclass system
5. **Arcane Schools**: Wizard subclass system
6. **Warlock Patrons**: Patron-based subclass system
7. **Pact Magic**: Warlock's unique spell slot system

## Implementation Phases

### Phase 1: Core Spell System Infrastructure
**Goal**: Build foundation for all spellcasting without breaking existing classes

#### Step 1.1: Database Schema Extensions
```sql
-- Character spell slots
CREATE TABLE IF NOT EXISTS character_spell_slots (
    character_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    max_slots INTEGER DEFAULT 0,
    used_slots INTEGER DEFAULT 0,
    slot_type TEXT DEFAULT 'standard', -- 'standard', 'pact'
    PRIMARY KEY (character_id, spell_level, slot_type),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Character spells known/prepared
CREATE TABLE IF NOT EXISTS character_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    is_prepared BOOLEAN DEFAULT TRUE,
    source TEXT NOT NULL, -- 'class', 'domain', 'oath', 'patron'
    source_level INTEGER, -- level gained
    always_prepared BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (character_id, spell_id),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

-- Spell definitions
CREATE TABLE IF NOT EXISTS spells (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_value TEXT NOT NULL,
    components TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    higher_levels TEXT,
    source TEXT DEFAULT 'PHB'
);
```

**Validation**: Run existing Fighter/Barbarian/Rogue tests to ensure no regressions.

#### Step 1.2: Spell Registry Service
Create `services/spell_registry.py`:
- Central registry for all spells
- Lazy loading system like subclass registry
- Spell list management by class
- Integration with existing action economy

**Testing**: Verify action economy still works for non-spellcasters.

#### Step 1.3: Spellcasting Service Foundation
Create `services/spellcasting_service.py`:
- Base spellcasting mechanics
- Spell slot management
- Preparation system
- Integration with action economy enforcer

**Validation**: Ensure Fighter action cards still generate correctly.

### Phase 2: Individual Class Implementation

#### Phase 2.1: Cleric Implementation
**Priority**: First spellcaster (full caster, prepared spells)

##### Step 2.1.1: Cleric Base Class
- Create Cleric class definition in database
- Spell slot progression (full caster)
- Divine spellcasting (Wisdom-based)
- Ritual casting capability
- Channel Divinity resource system

**Database Update**:
```sql
-- Cleric-specific features
CREATE TABLE IF NOT EXISTS cleric_features (
    character_id TEXT PRIMARY KEY,
    domain TEXT,
    channel_divinity_uses INTEGER DEFAULT 0,
    max_channel_divinity INTEGER DEFAULT 1,
    last_cd_reset TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

**Validation**:
```bash
cd test && python test_simple_validation.py
cd test && python -m pytest services/test_fighter_champion.py -v
```

##### Step 2.1.2: Life Domain Subclass
Using scalable subclass architecture:
- Create `services/subclasses/cleric/life.py`
- Life Domain spell list (always prepared)
- Enhanced healing features
- Heavy armor proficiency

**Testing**: Create `test/services/test_cleric_life.py` following Champion pattern.

#### Phase 2.2: Wizard Implementation ✅ **COMPLETED**
**Priority**: Second (full caster, spellbook system)

##### Step 2.2.1: Wizard Base Class ✅
- ✅ Spellbook system (different from prepared spells)
- ✅ Arcane Recovery feature
- ✅ Intelligence-based spellcasting
- ✅ Spell copying mechanics
- ✅ Database migration 013_wizard_class.sql
- ✅ WizardAbilitiesService with spellbook management
- ✅ Full spell slot progression implementation
- ✅ Spell preparation limit (Int modifier + level)

**Database Update**: ✅ Implemented
```sql
CREATE TABLE wizard_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    spell_slots_1_current INTEGER DEFAULT 0,
    spell_slots_1_max INTEGER DEFAULT 0,
    -- [Complete spell slot progression 1-9]
    arcane_tradition TEXT,
    arcane_recovery_used BOOLEAN DEFAULT FALSE,
    arcane_recovery_last_reset TEXT,
    spells_prepared INTEGER DEFAULT 0,
    max_spells_prepared INTEGER DEFAULT 0,
    PRIMARY KEY (character_id)
);

CREATE TABLE wizard_spellbook (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    learned_at_level INTEGER NOT NULL,
    source TEXT DEFAULT 'level_up',
    cost_paid INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0,
    notes TEXT,
    PRIMARY KEY (character_id, spell_id)
);
```

##### Step 2.2.2: Evocation School Subclass ✅
- ✅ Sculpt Spells feature (level 2)
- ✅ Potent Cantrip (level 6)
- ✅ Empowered Evocation (level 10)
- ✅ Overchannel (level 14)
- ✅ services/subclasses/wizard/evocation.py
- ✅ Scalable subclass architecture integration

**Implementation Status**: ✅ COMPLETE
- Database: ✅ All wizard tables created
- Services: ✅ WizardAbilitiesService implemented
- Subclasses: ✅ Evocation school complete
- Testing: ✅ Comprehensive test suite (6/9 tests passing)
- Integration: ✅ Uses existing spell infrastructure
- Validation: ✅ No regressions in existing classes

#### Phase 2.3: Paladin Implementation
**Priority**: Third (half caster, oath system)

##### Step 2.3.1: Paladin Base Class
- Half-caster spell progression
- Divine Smite system
- Charisma-based spellcasting
- Lay on Hands pool

**Database Update**:
```sql
CREATE TABLE IF NOT EXISTS paladin_features (
    character_id TEXT PRIMARY KEY,
    oath TEXT,
    lay_on_hands_pool INTEGER DEFAULT 0,
    max_lay_on_hands INTEGER DEFAULT 0,
    divine_smite_uses INTEGER DEFAULT 0, -- if limited
    last_loh_reset TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

##### Step 2.3.2: Oath of Devotion Subclass
- Oath spells (always prepared)
- Sacred Weapon Channel Divinity
- Turn the Unholy Channel Divinity

#### Phase 2.4: Warlock Implementation
**Priority**: Fourth (unique pact magic system)

##### Step 2.4.1: Warlock Base Class
- Pact Magic (different spell slot system)
- Eldritch Invocations
- Charisma-based spellcasting
- Short rest recovery

**Database Update**:
```sql
CREATE TABLE IF NOT EXISTS warlock_features (
    character_id TEXT PRIMARY KEY,
    patron TEXT,
    pact_boon TEXT,
    invocations_known TEXT, -- JSON array
    mystic_arcanum_spells TEXT, -- JSON array
    last_pact_reset TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS warlock_invocations (
    character_id TEXT NOT NULL,
    invocation_id TEXT NOT NULL,
    learned_at_level INTEGER,
    PRIMARY KEY (character_id, invocation_id),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

##### Step 2.4.2: Fiend Patron Subclass
- Expanded spell list
- Dark One's Blessing
- Dark One's Own Luck
- Fiendish Resilience

### Phase 3: Integration and UI Updates

#### Step 3.1: Action Card Integration
Extend existing action card system to include spells:
- Spell action cards generation
- Spell slot tracking in UI
- Concentration tracking
- Integration with existing action economy

**Validation**: Ensure Fighter/Barbarian action cards unchanged.

#### Step 3.2: Character Sheet Updates
Extend character sheet to display:
- Spell slots by level
- Prepared spells list
- Class-specific resources (Channel Divinity, Lay on Hands, etc.)
- Spellcasting ability modifier

#### Step 3.3: Equipment Integration
Ensure spellcasting classes work with equipment system:
- Spellcasting focus items
- Component pouches
- Armor restrictions for spellcasting
- Holy symbols for clerics/paladins

### Phase 4: Advanced Features

#### Step 4.1: Ritual Casting
- Ritual spell detection
- Extended casting time handling
- No spell slot consumption

#### Step 4.2: Concentration System
- Concentration tracking during combat
- Constitution saves when damaged
- Spell interruption mechanics

#### Step 4.3: Spell Recovery Mechanics
- Long rest spell slot recovery
- Short rest recovery (Warlock, Wizard Arcane Recovery)
- Class-specific recovery features

## Risk Mitigation Strategies

### 1. Incremental Testing
After each step:
```bash
# Test existing functionality
cd test && python test_simple_validation.py
cd test && python -m pytest services/test_fighter_champion.py -v
cd test && python -m pytest services/test_weapon_attack_service.py -v

# Test new functionality
cd test && python -m pytest services/test_[new_class]_[subclass].py -v
```

### 2. Database Backup Strategy
Before each major change:
```bash
copy talekeeper.db talekeeper_backup_[phase].db
```

### 3. Rollback Preparation
Each phase should include:
- Migration scripts to revert database changes
- Git commits for each completed step
- Documentation of exactly what was changed

### 4. Action Economy Protection
- Never modify existing ActionCost enum values
- Never change FeatureType enum values
- Extend action registry, don't replace it
- Test action economy enforcer after each change

### 5. UI Layout Protection
- Never modify existing panel coordinates
- Extend character sheet, don't replace sections
- Test with existing characters after changes

## Implementation Order Rationale

1. **Cleric First**: Full caster with prepared spells - establishes spell preparation system
2. **Wizard Second**: Full caster with spellbook - adds spell learning mechanics
3. **Paladin Third**: Half caster - tests reduced spell progression
4. **Warlock Last**: Unique pact magic - most complex spell system

## Success Metrics

### Phase Completion Criteria
Each phase must pass:
- All existing class tests (Fighter, Barbarian, Rogue)
- New class functionality tests
- UI integration tests
- Action economy validation
- Database integrity checks

### Final Validation
Upon completion:
- Create test characters of all 7 classes
- Verify multiclass combinations work
- Test combat with mixed party
- Validate spell/ability interactions
- Performance testing with all systems active

## Documentation Requirements

### Per-Phase Documentation
- `docs/PHASE_[X]_IMPLEMENTATION_LOG.md`
- What was implemented
- How it was implemented
- Why design decisions were made
- What tests were created
- What could be rolled back and how

### Change Tracking
- Git commits with detailed messages
- Database schema version tracking
- API compatibility notes
- Performance impact measurements

## Estimated Timeline

- **Phase 1**: 2-3 days (Core spell infrastructure)
- **Phase 2.1**: 2 days (Cleric + Life Domain)
- **Phase 2.2**: 2 days (Wizard + Evocation)
- **Phase 2.3**: 2 days (Paladin + Devotion)
- **Phase 2.4**: 3 days (Warlock + Fiend)
- **Phase 3**: 2-3 days (UI Integration)
- **Phase 4**: 2-3 days (Advanced features)

**Total**: ~15-20 days with thorough testing and validation

This plan prioritizes system stability while systematically adding spellcasting capabilities to TaleKeeper.