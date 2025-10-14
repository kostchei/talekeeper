# Conan Campaign Variants - Summary

## Overview

Two Conan-themed campaign variants have been created with different monster selection criteria:

### Conan-Core
**89 monsters** - Curated list from original campaign design
- Hand-picked monsters for authentic Conan sword-and-sorcery feel
- Includes 5 boss monsters
- Balanced progression from CR 0 to CR 10
- Level ranges: 1-16

### Conan-Like
**290 monsters** - Expanded thematic list
- All monsters that fit Conan themes
- Much larger variety for encounter generation
- Includes all Conan-Core monsters PLUS 203 additional
- Level ranges: 1-20+

## Monster Type Inclusion Rules

### Conan-Core (89 monsters)
- Manually curated list
- Focus on iconic Conan themes

### Conan-Like (290 monsters)
Includes these monster types:
- ✅ **Aberrations** - All (e.g., Aboleths, Gibbering Mouthers)
- ✅ **Fiends** - All (e.g., Demons, Devils)
- ✅ **Oozes** - All (e.g., Black Pudding, Gelatinous Cube)
- ✅ **Monstrosities** - All (e.g., Basilisks, Manticores)
- ✅ **Humanoids** - All (e.g., Bandits, Cultists, Tribal Warriors)
- ✅ **Giants** - All (e.g., Hill Giants, Frost Giants)
- ✅ **Constructs** - All EXCEPT Modrons
- ✅ **Beasts** - CR 1 and higher only (no CR 0-1/2 animals)
- ✅ **Undead** - All (e.g., Skeletons, Vampires, Liches)

### Excluded Types
- ❌ **Dragons** - Too high fantasy for Conan
- ❌ **Celestials** - Too divine/angelic
- ❌ **Fey** - Wrong thematic feel
- ❌ **Elementals** - Generally excluded
- ❌ **Plants** - Not thematic
- ❌ **Modrons** - Too mechanical/planar

## Campaign Statistics

### Conan-Core
| Metric | Count |
|--------|-------|
| Total Monsters | 89 |
| Boss Monsters | 5 |
| CR 0-1/2 | 17 |
| CR 1-4 | 36 |
| CR 5-8 | 25 |
| CR 9-12 | 11 |

**Top Monster Types:**
1. Humanoid: 38
2. Monstrosity: 11
3. Undead: 9
4. Beast: 8
5. Fiend: 7

**Boss Monsters:**
- Cultist Hierophant (CR 10) - Levels 11-16
- Warrior Commander (CR 10) - Levels 11-16
- Aboleth (CR 10) - Levels 11-16
- Berserker Commander (CR 8) - Levels 9-14
- Vampire Nightbringer (CR 8) - Levels 9-14

### Conan-Like
| Metric | Count |
|--------|-------|
| Total Monsters | 290 |
| Boss Monsters | 0 (uses weighted random) |
| CR 0-1/2 | 48 |
| CR 1-4 | 134 |
| CR 5-8 | 64 |
| CR 9-12 | 25 |
| CR 13+ | 19 |

**Top Monster Types:**
1. Humanoid: 71
2. Monstrosity: 57
3. Fiend: 43
4. Beast: 34
5. Undead: 27

**Additional Content (vs Conan-Core):**
- +203 unique monsters
- +19 high-CR monsters (13+)
- +33 humanoid variants
- +46 monstrosities
- +36 fiends

## Use Cases

### When to Use Conan-Core
- **Curated experience**: Want hand-picked, thematically perfect encounters
- **Narrative focus**: Specific monsters chosen for story beats
- **Boss encounters**: Need designated boss monsters
- **Levels 1-16**: Standard campaign length
- **Tighter balance**: More predictable difficulty

### When to Use Conan-Like
- **Maximum variety**: Want diverse random encounters
- **Sandbox campaigns**: Players explore freely, need many options
- **Long campaigns**: Levels 1-20+ with ongoing content
- **West Marches style**: Need large monster pool for procedural generation
- **Replayability**: Different encounters each playthrough

## Query Examples

### Get Level-Appropriate Monsters
```sql
SELECT m.name, m.type, m.challenge_rating
FROM campaign_monsters cm
JOIN monsters m ON cm.monster_id = m.id
WHERE cm.campaign_id = 'conan-core'  -- or 'conan-like'
  AND cm.min_party_level <= 5
  AND cm.max_party_level >= 5
ORDER BY RANDOM()
LIMIT 5;
```

### Get Monsters by Type
```sql
SELECT m.name, m.challenge_rating
FROM campaign_monsters cm
JOIN monsters m ON cm.monster_id = m.id
WHERE cm.campaign_id = 'conan-like'
  AND LOWER(m.type) = 'fiend'
ORDER BY m.challenge_rating;
```

### Get Boss Monsters
```sql
SELECT m.name, m.type, m.challenge_rating
FROM campaign_monsters cm
JOIN monsters m ON cm.monster_id = m.id
WHERE cm.campaign_id = 'conan-core'
  AND cm.is_boss = 1
ORDER BY m.challenge_rating;
```

### Compare Monster Overlap
```sql
-- Monsters ONLY in Conan-Like
SELECT m.name, m.type, m.challenge_rating
FROM campaign_monsters cm
JOIN monsters m ON cm.monster_id = m.id
WHERE cm.campaign_id = 'conan-like'
  AND cm.monster_id NOT IN (
      SELECT monster_id FROM campaign_monsters
      WHERE campaign_id = 'conan-core'
  )
ORDER BY m.challenge_rating;
```

## Implementation Details

### Database Tables
1. **campaigns** - Campaign definitions
   - `conan-core`: Conan Core campaign
   - `conan-like`: Conan-Like campaign

2. **campaign_monsters** - Junction table linking campaigns to monsters
   - 89 entries for conan-core
   - 290 entries for conan-like
   - Includes level ranges, boss flags, encounter weights

3. **monsters** - 476 total monsters in database
   - All Conan-Core monsters present
   - All Conan-Like monsters present
   - Properly typed and CR-rated

### Scripts Created
1. **create_conan_campaigns.py** - Creates both campaigns
2. **show_conan_campaigns.py** - Displays comparison and stats
3. **populate_campaign_monsters.py** - Original Conan population script

### Files
- [scripts/database_tools/create_conan_campaigns.py](../../scripts/database_tools/create_conan_campaigns.py)
- [scripts/database_tools/show_conan_campaigns.py](../../scripts/database_tools/show_conan_campaigns.py)
- [docs/campaign_monsters_design.md](campaign_monsters_design.md)

## Integration with TaleKeeper

### Encounter Generation
The campaign monsters system integrates with encounter generation:
1. Select campaign (conan-core or conan-like)
2. Query monsters by party level
3. Apply encounter weights
4. Generate balanced encounters

### Future Enhancements
- **Terrain-based filtering**: Desert vs mountain encounters
- **Faction system**: Bandit encounters vs cult encounters
- **Difficulty scaling**: Easy/medium/hard/deadly options
- **Monster groups**: Pre-defined thematic groups
- **Dynamic CR adjustment**: Scale monsters to party level

## Conclusion

Both Conan campaigns are now fully populated and ready to use:
- **Conan-Core**: Tight, curated 89-monster list with boss encounters
- **Conan-Like**: Expansive 290-monster list for maximum variety

Total database size: **476 monsters** (+6.3% from start)
Campaign coverage: **100% of original 92-monster list**
Additional content: **+203 thematic monsters** available in Conan-Like
