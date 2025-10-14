# Campaign Monster System Update - Documentation

## Overview
Transitioned from weighted monster type distribution to campaign-specific curated monster lists using the `campaign_monsters` junction table.

## Date
October 2025

---

## Problem Statement

**Previous System:**
- Campaigns used `monster_type_weights` to randomly select monsters based on type percentages
- Example: `{"humanoid": 0.43, "monstrosity": 0.12, "undead": 0.10, ...}`
- Resulted in generic monster distributions that didn't reflect campaign themes
- Monster selection was algorithmic rather than curated

**Issues:**
- No direct control over which specific monsters appeared in campaigns
- Percentage distributions were calculated but not meaningful to users
- Couldn't create thematic campaign bestiaries with hand-picked monsters

---

## Solution

**New System:**
- Uses `campaign_monsters` junction table to define exact monster lists per campaign
- Database-driven approach with proper many-to-many relationship
- Falls back to all monsters for campaigns without specific lists
- Maintains backwards compatibility

---

## Database Schema

### campaign_monsters Junction Table

```sql
CREATE TABLE campaign_monsters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,

    encounter_weight INTEGER DEFAULT 1,
    min_party_level INTEGER DEFAULT 1,
    max_party_level INTEGER DEFAULT 20,

    environment_override TEXT,
    notes TEXT,
    variant_rules TEXT,
    is_boss INTEGER DEFAULT 0,

    added_date TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (monster_id) REFERENCES monsters(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, monster_id)
);
```

### Indexes
- `idx_campaign_monsters_campaign` - Fast campaign lookups
- `idx_campaign_monsters_monster` - Fast monster lookups
- `idx_campaign_monsters_level` - Level-appropriate queries
- `idx_campaign_monsters_boss` - Boss filtering

---

## Code Changes

### 1. CampaignFrame Class
**File:** `src/talekeeper/ui/encounter_pane/campaign_frame.py`

**Changes:**
- Added `campaign_id` attribute (extracted from `style` field)
- Used by encounter generator to query monster list

```python
# Line 10 (dict initialization)
self.campaign_id = data.get('style', '')

# Line 26 (parameter initialization)
self.campaign_id = style

# Line 43 (serialization)
"campaign_id": self.campaign_id,
```

### 2. Monster Loading Function
**File:** `src/talekeeper/ui/encounter_pane/encounter_generator.py`

**Changes:**
- Modified `load_monsters()` to accept optional `campaign_id`
- Queries `campaign_monsters` junction table when campaign_id provided
- Falls back to all monsters if campaign not found in junction table

```python
def load_monsters(campaign_id: Optional[str] = None):
    """Load monsters from database, optionally filtered by campaign"""
    import sqlite3
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()

    if campaign_id:
        # Try to load campaign-specific monsters
        cursor.execute("""
            SELECT m.* FROM monsters m
            JOIN campaign_monsters cm ON m.id = cm.monster_id
            WHERE cm.campaign_id = ?
        """, (campaign_id,))
        monster_rows = cursor.fetchall()

        # Fallback if campaign not found in junction table
        if not monster_rows:
            cursor.execute("SELECT * FROM monsters")
            monster_rows = cursor.fetchall()
    else:
        # Load all monsters
        cursor.execute("SELECT * FROM monsters")
        monster_rows = cursor.fetchall()

    # ... rest of processing
```

### 3. EncounterGenerator Class
**File:** `src/talekeeper/ui/encounter_pane/encounter_generator.py`

**Changes:**
- Changed from global `MONSTER_DB` to instance variable `self.monster_db`
- Loads campaign-specific monsters in `__init__()`
- Updated `_get_available_monsters()` to use `self.monster_db`

```python
# Line 205 - Constructor
def __init__(self, frame: CampaignFrame, description_service: Optional["CampaignDescriptionService"] = None):
    self.frame = frame
    self.bags: Dict[int, RandomBag] = {}
    self.description_service = description_service
    self.monster_db = load_monsters(frame.campaign_id) if frame.campaign_id else load_monsters()

# Line 247 - Monster filtering
for m in self.monster_db:  # Changed from MONSTER_DB
    if m["cr"] > cr_cap:
        continue
    # ...
```

### 4. Campaign JSON Files

**Removed:** `monster_type_weights` objects from campaign files

**Updated Descriptions:**
- `conan.json`: "Only monsters from the Conan stories."
- `conan-like.json`: "Wider selection in the style and theme of Robert E. Howard."
- `golden.json`: "Classic heroic fantasy with all monster types and guaranteed treasure hoards."

---

## Campaign Configurations

### 1. Conan (Core)
**File:** `src/talekeeper/ui/encounter_pane/campaign/conan.json`

- **Campaign ID:** `conan`
- **Monsters:** 89 (curated from Conan stories)
- **Guaranteed Hoards:** No
- **Theme:** Savage sword-and-sorcery, humanoids, beasts, rare horrors
- **Narrative Style:** Brutal, visceral prose focused on blood and steel

**Monster Sources:**
- Populated via `campaign_monsters` junction table
- Includes: Bandits, warriors, cultists, aberrations, undead, beasts
- Boss monsters: Berserker Commander, Vampire Nightbringer, Cultist Hierophant, etc.

### 2. Conan-Like
**File:** `src/talekeeper/ui/encounter_pane/campaign/conan-like.json`

- **Campaign ID:** `conan-like`
- **Monsters:** 290 (expanded sword-and-sorcery)
- **Guaranteed Hoards:** No
- **Theme:** Sword-and-sorcery with fantasy elements
- **Narrative Style:** Balance of savage violence and magical wonder

**Monster Sources:**
- Expanded beyond core Conan to include diverse fantasy threats
- Includes: Fiends, aberrations, constructs, exotic monsters
- Wider selection in Robert E. Howard style and theme

### 3. Golden Age
**File:** `src/talekeeper/ui/encounter_pane/campaign/golden.json`

- **Campaign ID:** `golden`
- **Monsters:** 476 (all monsters in database)
- **Guaranteed Hoards:** Yes
- **Theme:** Classic heroic fantasy
- **Narrative Style:** Heroic deeds, epic quests, timeless adventure

**Monster Sources:**
- No entry in `campaign_monsters` table
- Falls back to all monsters in database
- Comprehensive monster selection for traditional D&D experience

---

## Behavioral Changes

### Before
```python
# Campaign specified monster types with weights
"monster_type_weights": {
    "humanoid": 0.43,
    "monstrosity": 0.12,
    "undead": 0.10,
    "beast": 0.09,
    # ...
}

# System randomly selected monsters of those types
# Result: Generic, algorithmic monster selection
```

### After
```python
# Campaign uses curated list from database
# System: "Load monsters for campaign_id='conan'"
# Database returns 89 specific monsters

# Result: Hand-picked, thematic monster selection
```

---

## Query Examples

### Get all monsters for a campaign
```sql
SELECT m.* FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan';
```

### Get level-appropriate monsters
```sql
SELECT m.* FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan'
  AND cm.min_party_level <= 5
  AND cm.max_party_level >= 5
ORDER BY RANDOM()
LIMIT 1;
```

### Get boss monsters
```sql
SELECT m.name, m.challenge_rating FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan'
  AND cm.is_boss = 1
  AND cm.min_party_level <= 8
  AND cm.max_party_level >= 8;
```

### Weighted random encounter
```sql
SELECT m.* FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan'
  AND cm.min_party_level <= ?
  AND cm.max_party_level >= ?
ORDER BY (RANDOM() * cm.encounter_weight) DESC
LIMIT 1;
```

---

## Testing Results

### Campaign Monster Counts
```
Conan (Core):     89 monsters (curated list)
Conan-Like:      290 monsters (curated list)
Golden Age:      476 monsters (all monsters - fallback)
```

### Sample Encounter Generation
```
Conan Level 5 Low: Giant Spider (CR 1), Yuan-ti Infiltrator (CR 1)
Conan Level 5 Mod: Lion (CR 1), Bandit Captain (CR 2)

Golden Level 5 Mod: Will-o'-Wisp (CR 2), Animated Armor (CR 1)
```

### Fallback Behavior
- Campaign with no junction table entry → loads all 476 monsters
- Empty campaign_id → loads all 476 monsters
- Campaign with 0 results → falls back to all 476 monsters

---

## Migration Path

### Populating Campaign Monsters

**Scripts Available:**
- `scripts/database_tools/populate_campaign_monsters.py` - Add monsters to campaigns
- `scripts/database_tools/show_conan_campaigns.py` - View campaign monster lists
- `scripts/database_tools/create_conan_campaigns.py` - Create campaign definitions

**Example:**
```python
# Add a monster to a campaign
conn = sqlite3.connect('talekeeper.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO campaign_monsters (id, campaign_id, monster_id, min_party_level, max_party_level)
    VALUES (?, ?, ?, ?, ?)
""", (
    'cm_' + str(uuid.uuid4()),
    'conan',
    monster_id,
    1,
    20
))

conn.commit()
```

---

## Advantages of New System

### 1. Direct Control
- Campaign designers pick exact monsters
- No algorithmic guessing
- Theme enforcement

### 2. Flexibility
- Same monster can appear in multiple campaigns
- Campaign-specific metadata (boss flags, level ranges)
- Easy to add/remove monsters

### 3. Performance
- Database indexes for fast queries
- Level-appropriate filtering
- Efficient encounter generation

### 4. Scalability
- Unlimited campaigns supported
- Unlimited monsters per campaign
- No code changes needed to add campaigns

### 5. Data Integrity
- Foreign key constraints
- Unique constraints prevent duplicates
- Cascade deletes for cleanup

---

## Future Enhancements

### Potential Features
1. **Campaign Bestiary UI** - Browse available monsters for campaign
2. **Encounter Difficulty Calculator** - Analyze campaign balance
3. **Monster Rarity Tracking** - Track encounter frequency
4. **Environment-Based Tables** - Terrain-specific encounters
5. **Variant Rules** - Campaign-specific monster modifications
6. **Boss Encounter System** - Special handling for boss flags

### Additional Metadata
- `environment_override` - Change monster's preferred terrain
- `notes` - Campaign-specific lore
- `variant_rules` - Special abilities or modifications
- `encounter_weight` - Adjust spawn probability

---

## Backwards Compatibility

### Legacy Campaigns
- Campaigns without `campaign_id` in junction table fall back to all monsters
- `monster_type_weights` field still parsed but not used
- Old campaign files work without modification

### Migration Strategy
1. Campaign with specific list → Use junction table
2. Campaign without list → Load all monsters
3. Gradual migration - add campaigns to junction table as needed

---

## File Summary

### Modified Files
1. `src/talekeeper/ui/encounter_pane/campaign_frame.py` - Added `campaign_id` attribute
2. `src/talekeeper/ui/encounter_pane/encounter_generator.py` - Junction table queries
3. `src/talekeeper/ui/encounter_pane/campaign/conan.json` - Removed weights, updated description
4. `src/talekeeper/ui/encounter_pane/campaign/conan-like.json` - Removed weights, updated description

### New Files
5. `src/talekeeper/ui/encounter_pane/campaign/golden.json` - Golden Age campaign
6. `docs/campaign_monster_system_update.md` - This documentation

### Database Files
7. `database/migrations/003_campaign_monsters_junction.sql` - Junction table schema
8. `scripts/database_tools/populate_campaign_monsters.py` - Population script

---

## Conclusion

The campaign monster system has been successfully updated from algorithmic type-based distribution to curated database-driven monster lists. This provides campaign designers with direct control over monster selection while maintaining backwards compatibility and performance.

### Key Benefits
- **89 curated Conan monsters** vs random humanoids
- **290 Conan-like monsters** vs weighted distribution
- **476 Golden Age monsters** with guaranteed hoards
- Database-driven, scalable, flexible system
- No user-facing description changes needed

### Status
✅ Implementation complete
✅ Testing complete
✅ Three campaigns available (Conan, Conan-Like, Golden Age)
✅ Documentation complete
