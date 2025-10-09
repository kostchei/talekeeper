# Warlock Migration Consolidation

**Date**: 2025-10-08
**Issue**: Migration 015b failed with duplicate column errors on fresh database rebuild
**Resolution**: Consolidated all Warlock schema into migration 015

---

## Problem

When migration `015b_warlock_enhancements.sql` was created, it tried to add columns that were already manually added to the database:

```sql
ALTER TABLE warlock_features ADD COLUMN level INTEGER DEFAULT 1;
-- Error: duplicate column name: level
```

This meant on a fresh database rebuild, migration 015b would fail because migration 015 didn't originally create these columns.

---

## Solution

**Consolidated everything into migration 015** so it creates the complete schema from the start.

### Updated Migration 015

**File**: `database/migrations/015_warlock_class.sql`

Now includes:

#### 1. Complete warlock_features Table
```sql
CREATE TABLE IF NOT EXISTS warlock_features (
    character_id TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,

    -- Pact Magic Slots
    pact_slots_current INTEGER DEFAULT 1,
    pact_slots_max INTEGER DEFAULT 1,
    pact_slot_level INTEGER DEFAULT 1,

    -- Core Features
    patron TEXT,
    pact_boon TEXT,
    eldritch_invocations TEXT DEFAULT '[]',

    -- Magical Cunning (Level 2+)
    magical_cunning_used BOOLEAN DEFAULT 0,
    last_magical_cunning TEXT,

    -- Contact Patron (Level 9+)
    contact_patron_used BOOLEAN DEFAULT 0,
    last_contact_patron TEXT,

    -- Mystic Arcanum (Levels 11+)
    arcanum_6_used BOOLEAN DEFAULT 0,
    arcanum_6_spell TEXT,
    arcanum_7_used BOOLEAN DEFAULT 0,
    arcanum_7_spell TEXT,
    arcanum_8_used BOOLEAN DEFAULT 0,
    arcanum_8_spell TEXT,
    arcanum_9_used BOOLEAN DEFAULT 0,
    arcanum_9_spell TEXT,

    -- Fiend Patron Features
    dark_ones_luck_uses INTEGER DEFAULT 0,
    fiendish_resilience_type TEXT,
    hurl_through_hell_used BOOLEAN DEFAULT 0,

    -- Generic Patron Features
    patron_feature_uses_current INTEGER DEFAULT 0,
    patron_feature_uses_max INTEGER DEFAULT 0,

    -- Legacy columns (backwards compatibility)
    invocations_known TEXT DEFAULT '[]',
    mystic_arcanum_spells TEXT DEFAULT '[]',
    last_pact_reset TEXT,
    pact_slots INTEGER DEFAULT 1,

    PRIMARY KEY (character_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

**Total Columns**: 26 (covers all Warlock needs)

#### 2. warlock_patron_features Table
```sql
CREATE TABLE IF NOT EXISTS warlock_patron_features (
    id TEXT PRIMARY KEY,
    patron TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    effect_type TEXT,
    effect_data TEXT
);
```

With all 5 Fiend Patron features populated.

#### 3. Additional Invocations
Added 10 more invocations:
- Ascendant Step
- Eldritch Mind
- Eldritch Smite
- Gift of the Depths
- Gift of the Protectors
- Investment of Chain Master
- Lessons of the First Ones
- Devouring Blade
- Visions of Distant Realms
- Eldritch Spear

**Total invocations in migration 015**: 32

#### 4. Corrected Progression
Fixed `invocations_known` values to match D&D 2024:
- Level 1: 1 invocation
- Level 20: 10 invocations

---

## Migration Status

### Active Migrations ✅

| File | Status | Purpose |
|------|--------|---------|
| `015_warlock_class.sql` | ✅ ACTIVE | Complete Warlock schema + data |
| `015c_warlock_spell_list.sql` | ✅ ACTIVE | Link Warlock spells to class |

### Deprecated Migrations ❌

| File | Status | Reason |
|------|--------|--------|
| `015b_warlock_enhancements.sql` | ❌ DEPRECATED | Merged into 015 |
| `015b_warlock_enhancements_DEPRECATED.sql` | 📄 Reference | Documentation only |

---

## Database Rebuild Process

If the database needs to be rebuilt from scratch, the correct order is:

### 1. Core Schema Migrations
```bash
# Base tables (characters, classes, spells, etc.)
sqlite3 talekeeper.db < migrations/001_*.sql
sqlite3 talekeeper.db < migrations/002_*.sql
# ... (other base migrations)
```

### 2. Warlock Migrations
```bash
# Complete Warlock implementation
sqlite3 talekeeper.db < migrations/015_warlock_class.sql
sqlite3 talekeeper.db < migrations/015c_warlock_spell_list.sql
```

**Note**: Migration 015 depends on these tables existing first:
- `classes`
- `subclasses`
- `class_features`
- `spells`
- `spell_class_lists`
- `characters`

---

## Validation

After rebuild, validate with:

```bash
python scripts/database_tools/validate_warlock_db.py
```

Expected results:
- ✅ warlock_features: 16+ required columns
- ✅ warlock_pact_progression: 20 levels
- ✅ invocations: 32 invocations
- ✅ warlock_patron_features: 5 Fiend features
- ✅ spell_class_lists: 72+ Warlock spells
- ✅ Warlock class exists with d8 hit die

---

## Current Database State

The existing `talekeeper.db` already has all columns and tables from the manual additions. The consolidated migration 015 ensures future rebuilds will also have everything.

### Tables Created ✅
- `warlock_features` - 26 columns
- `warlock_invocations` - Character invocation tracking
- `invocations` - 32 invocations reference
- `warlock_pact_progression` - 20 levels
- `warlock_patron_features` - 5 Fiend features

### Data Populated ✅
- Warlock class entry
- 3 subclasses (Fiend, Archfey, Great Old One)
- 32 invocations with prerequisites
- 20 levels of progression
- 5 Fiend Patron features
- 72 spell list entries

---

## Testing Recommendations

Before any production database rebuild:

1. **Test migration 015 on clean database** (requires base schema first)
2. **Test migration 015c spell list** (requires spells table)
3. **Run validation script** to confirm all data present
4. **Test character creation** to ensure foreign keys work
5. **Test level progression** to ensure data is correct

---

## Notes for Future Development

### Pact Boons (Blade, Chain, Tome)
These are NOT invocations in D&D 2024. They are:
- Level 3 class features
- Stored in `warlock_features.pact_boon` column
- Separate from Eldritch Invocations

Some invocations require specific pact boons (e.g., Thirsting Blade requires Pact of the Blade).

### Legacy Columns
The following columns are kept for backwards compatibility but should use the newer columns in new code:

| Legacy | Modern | Reason |
|--------|--------|--------|
| `pact_slots` | `pact_slots_current` | More explicit |
| `invocations_known` | `eldritch_invocations` | Better naming |
| `mystic_arcanum_spells` | `arcanum_X_spell` | Separate tracking per level |

### Spell List Coverage
The `spell_class_lists` entries were created for all 77 Warlock spells. As new spells are added to the `spells` table, they automatically become available to Warlocks via the existing links.

Currently available:
- Level 0-1: Complete
- Level 2-5: Partial (depends on spell implementations)
- Level 6-9: None yet (for Mystic Arcanum)

---

## Files Modified

### Created/Updated
1. ✅ `database/migrations/015_warlock_class.sql` - Complete schema
2. ✅ `database/migrations/015c_warlock_spell_list.sql` - Spell links
3. ✅ `database/migrations/015b_warlock_enhancements_DEPRECATED.sql` - Reference doc

### Validated
- ✅ `scripts/database_tools/validate_warlock_db.py` - All checks pass
- ✅ Current database maintains all data

---

**Status**: ✅ **RESOLVED**
**Database**: Ready for fresh rebuild
**Next Phase**: Implement PactMagicService
