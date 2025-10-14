# Campaign Monsters System - Design Document

## Overview
Junction table approach for tracking which monsters appear in which campaigns, with campaign-specific metadata.

## Database Schema

### Table: `campaign_monsters`
```sql
CREATE TABLE campaign_monsters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    monster_id TEXT NOT NULL,

    -- Encounter generation
    encounter_weight INTEGER DEFAULT 1,    -- Higher = more likely to spawn
    min_party_level INTEGER DEFAULT 1,     -- Minimum party level
    max_party_level INTEGER DEFAULT 20,    -- Maximum party level

    -- Campaign-specific metadata
    environment_override TEXT,             -- Override monster's default environment
    notes TEXT,                            -- Campaign-specific notes
    variant_rules TEXT,                    -- Special rules for this campaign
    is_boss INTEGER DEFAULT 0,             -- Boss/mini-boss flag

    -- Timestamps
    added_date TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (monster_id) REFERENCES monsters(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, monster_id)
);
```

### Indexes
- `idx_campaign_monsters_campaign` - Fast lookups by campaign
- `idx_campaign_monsters_monster` - Fast lookups by monster
- `idx_campaign_monsters_level` - Fast level-appropriate queries
- `idx_campaign_monsters_boss` - Fast boss filtering

## Example Queries

### Get all monsters for a campaign
```sql
SELECT m.* FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan'
ORDER BY m.challenge_rating;
```

### Get level-appropriate monsters
```sql
SELECT m.*, cm.is_boss FROM monsters m
JOIN campaign_monsters cm ON m.id = cm.monster_id
WHERE cm.campaign_id = 'conan'
  AND cm.min_party_level <= 5
  AND cm.max_party_level >= 5
ORDER BY RANDOM()
LIMIT 1;
```

### Get boss monsters for a level range
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

### Find all campaigns using a specific monster
```sql
SELECT cm.campaign_id, cm.min_party_level, cm.max_party_level
FROM campaign_monsters cm
WHERE cm.monster_id = (SELECT id FROM monsters WHERE name = 'Shadow Demon');
```

## Python Helper Functions

```python
class CampaignMonsterManager:
    def get_campaign_monsters(self, campaign_id, party_level=None):
        '''Get all monsters for campaign, optionally filtered by party level'''

    def get_random_encounter(self, campaign_id, party_level, count=1, exclude_bosses=True):
        '''Get random encounter(s) appropriate for party level'''

    def get_boss_monsters(self, campaign_id, party_level):
        '''Get boss monsters appropriate for party level'''

    def add_monster_to_campaign(self, campaign_id, monster_name, min_level, max_level, is_boss=False):
        '''Add a monster to a campaign'''

    def remove_monster_from_campaign(self, campaign_id, monster_name):
        '''Remove a monster from a campaign'''

    def get_campaigns_for_monster(self, monster_name):
        '''Find all campaigns that use a specific monster'''
```

## Conan Campaign Example

Currently populated with 89 monsters:
- **Boss monsters**: 5
  - Berserker Commander (CR 8)
  - Vampire Nightbringer (CR 8)
  - Cultist Hierophant (CR 10)
  - Warrior Commander (CR 10)
  - Aboleth (CR 10)

- **Level ranges**:
  - Levels 1-5: 23 monsters (CR 0-1/4)
  - Levels 2-7: 14 monsters (CR 1/2-1)
  - Levels 3-8: 11 monsters (CR 2)
  - Levels 4-9: 9 monsters (CR 3)
  - Levels 5-10: 7 monsters (CR 4)
  - Levels 6-11: 9 monsters (CR 5)
  - Levels 7-12: 5 monsters (CR 6)
  - Levels 8-13: 4 monsters (CR 7)
  - Levels 9-14: 8 monsters (CR 8)
  - Levels 10-15: 5 monsters (CR 9)
  - Levels 11-16: 6 monsters (CR 10)

## Advantages of This Design

### 1. Flexibility
- Same monster can appear in multiple campaigns with different configurations
- Campaign-specific variants without duplicating monster data
- Easy to add/remove monsters from campaigns

### 2. Encounter Generation
- Level-appropriate encounters automatically filtered
- Weighted random selection for variety
- Boss flag for special encounters

### 3. Scalability
- Can support unlimited campaigns
- Can support unlimited monsters per campaign
- Indexes ensure fast queries even with large datasets

### 4. Data Integrity
- Foreign key ensures monster exists
- Unique constraint prevents duplicates
- Cascade delete cleans up when monsters removed

### 5. Future Features
- Campaign bestiary UI (filtered monster list)
- Encounter difficulty calculator
- Monster rarity/frequency tracking
- Campaign-specific monster variants
- Terrain/environment-based encounter tables

## Alternative Approaches (Not Recommended)

### Column in monsters table
```sql
ALTER TABLE monsters ADD COLUMN campaigns TEXT;
```
**Problems:**
- Violates normalization
- Hard to query campaigns using a monster
- No campaign-specific metadata
- Messy with many campaigns

### JSON in campaigns table
```sql
ALTER TABLE campaigns ADD COLUMN monster_list TEXT; -- JSON array
```
**Problems:**
- Can't use foreign keys
- Can't index monster references
- Hard to query monsters by level
- No relational integrity

## Conclusion

The junction table approach is the proper relational database design for many-to-many relationships. It provides flexibility, performance, and scalability while maintaining data integrity.

**Current Status**: Implemented and populated for Conan campaign with 89 monsters.
