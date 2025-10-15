# Hex Map Skill-Based Scouting System

## Overview
The hex map's scouting system is integrated with TaleKeeper's existing monster knowledge skill system, providing consistent skill-based information reveal across the game.

## Integration with Monster Knowledge System

### Shared Foundation
Both systems use [monster_knowledge.py](../src/talekeeper/services/monster_knowledge.py) as the reference:

**Skill-to-Monster-Type Mapping:**
```python
MONSTER_KNOWLEDGE_SKILLS = {
    'aberration': ['arcana'],
    'beast': ['nature', 'survival'],
    'celestial': ['religion'],
    'construct': ['arcana', 'investigation'],
    'dragon': ['arcana', 'history'],
    'elemental': ['arcana', 'nature'],
    'fey': ['arcana', 'nature'],
    'fiend': ['religion'],
    'giant': ['history', 'insight'],
    'humanoid': ['history', 'insight'],
    'monstrosity': ['nature'],
    'ooze': ['arcana', 'nature'],
    'plant': ['nature', 'survival'],
    'undead': ['religion']
}
```

### Hex Scouting Skills
[hex_scouting_service.py](../src/talekeeper/services/hex_scouting_service.py) extends this system:

**Terrain Scouting:**
- **Nature**: Identify terrain features, flora, fauna, natural resources
- **Survival**: Assess travel difficulty, find shelter, camping suitability

**Encounter Scouting:**
- **Perception**: Base check to detect encounters (DC = 10 + CR)
- **Type-Specific Skills**: Same as monster knowledge tooltips
  - Arcana for magical creatures
  - Religion for undead/celestial/fiend
  - History for giants/dragons/humanoids
  - Nature/Survival for beasts/plants

## How It Works

### 1. Player Clicks Adjacent Hex
When selecting an adjacent revealed hex:
```python
scouting_info = self.scouting_service.scout_hex(character_id, q, r, hex_data)
```

### 2. Automatic Skill Checks Run
The service performs three checks:
```python
nature_roll = d20() + character_nature_bonus
survival_roll = d20() + character_survival_bonus
perception_roll = d20() + character_perception_bonus
```

### 3. Information Revealed by Success

**Terrain Information (Nature/Survival):**
- **Success**: Basic terrain type and movement cost
- **+3 margin**: Flora/fauna details, resources
- **+5 margin**: Shelter locations, camping suitability

**Encounter Information (Perception):**
- **Success (margin 0+)**: Show encounter name and CR
  - Example: "Hill Giant (CR 5)"
  - Or: "Vendor: signs of a traveling merchant"
  - Or: "Possible hazard detected"

**Simple Display:**
- Combat encounters: `Monster Name (CR X)`
- Vendors: `Vendor: signs of a traveling merchant`
- Hazards: `Possible hazard` (basic) or type if high roll
- Landmarks: `Landmark: Location Name`

## Skill Check Calculations

### DC Determination
```python
# Terrain checks
terrain_dc = {
    'plains': 10,
    'forest': 12,
    'mountain': 15,
    'hills': 12,
    'swamp': 14,
    'desert': 13
}

# Encounter checks
encounter_dc = 10 + monster_cr
# +2 DC for stealthy types (aberration, fey)
```

### Character Bonuses
```python
# Same as monster knowledge system
ability_score = character[skill_ability]  # INT for Nature, WIS for Survival
modifier = (ability_score - 10) // 2

# Check character_proficiencies table
if proficient_in_skill:
    modifier += proficiency_bonus

total = d20() + modifier
```

## UI Display

### Info Panel Format
```
[Forest Terrain]

Nature: 18 vs DC 12 ✓
Survival: 14 vs DC 12 ✓

Terrain:
• Dense woodland with limited sightlines
• Ancient trees provide shelter and resources
• Good places to make camp under the canopy

Danger Detected:
• Hill Giant (CR 5)

[Click again to travel here]
```

### Color Coding
- **Success**: Green (✓)
- **Failure**: Red (✗)
- **Danger Levels**:
  - Low (CR 0-2): Green
  - Moderate (CR 3-5): Yellow
  - High (CR 6-8): Orange
  - Extreme (CR 9+): Red

## Example Scenarios

### Scenario 1: High Perception, Low Nature
**Character**: Rogue with Perception +7, Nature +0
- Perception roll: 19 → Detects "Goblin Ambush (CR 1)"
- Nature roll: 8 → Only knows it's forest terrain
- **Result**: Knows about threat, but no terrain details

### Scenario 2: Ranger with High Survival
**Character**: Ranger with Survival +8, Perception +5
- Survival roll: 21 → Full terrain details + camping info
- Perception roll: 12 → Misses hidden Owlbear (DC 15)
- **Result**: Thinks hex is safe, surprise encounter possible

### Scenario 3: Wizard Scouting for Undead
**Character**: Cleric with Religion +6, Perception +3
- Perception roll: 18 vs DC 13 → Detects presence
- Religion applies to undead → Shows "Wight (CR 3)"
- **Result**: Prepared for undead encounter

## Integration Notes

### Character Proficiencies
The system reads from `character_proficiencies` table:
```sql
SELECT 1 FROM character_proficiencies
WHERE character_id = ?
  AND proficiency_type = 'skill'
  AND proficiency_name = ?
```

### Consistent with Tooltips
- Monster knowledge tooltips: Click monster name → skill dialog
- Hex scouting: Automatic checks when viewing adjacent hex
- **Same DCs, same skill mappings, same information tiers**

### Future: Manual Scout Action
Could add "Scout Hex" action card:
- Costs action or bonus action
- Allows reroll with different skill
- Higher DC but more detailed info
- Currently: Automatic free scouting when selecting hex

## References

- [monster_knowledge.py](../src/talekeeper/services/monster_knowledge.py) - Base skill system
- [monster_knowledge_label.py](../src/talekeeper/ui/monster_knowledge_label.py) - Tooltip UI reference
- [hex_scouting_service.py](../src/talekeeper/services/hex_scouting_service.py) - Hex implementation
- D&D 2024 Knowledge Check rules (Player's Handbook, Chapter 7)
