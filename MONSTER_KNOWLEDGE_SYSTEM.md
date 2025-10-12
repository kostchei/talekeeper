# Monster Knowledge System

A D&D 5e-style monster identification and lore system for TaleKeeper.

## Overview

Players can make skill checks to identify monsters and learn information about them. The difficulty and amount of information revealed depends on their skill check result relative to the monster's Challenge Rating.

## System Rules

### DC Calculation
```
DC = 10 + CR
```

**Examples:**
- CR 1/4 monster = DC 10
- CR 1 monster = DC 11
- CR 3 monster = DC 13
- CR 5 monster = DC 15

### Information Revealed by Success Margin

| Check Result | Information Revealed |
|--------------|---------------------|
| **DC Exactly** | Name, Type, Size, CR |
| **DC + 2** | + Vulnerabilities, Resistances, Immunities |
| **DC + 4** | + Armor Class, Hit Points |
| **DC + 6** | + Special Abilities, Attacks |
| **DC + 8** | + Ability Scores, Senses, Languages, Saving Throws, Skills |

### Skill to Monster Type Mapping

Players use different skills depending on the monster's type:

| Monster Type | Applicable Skills |
|--------------|------------------|
| **Aberration** | Arcana |
| **Beast** | Nature, Survival |
| **Celestial** | Religion |
| **Construct** | Arcana, Investigation |
| **Dragon** | Arcana, History |
| **Elemental** | Arcana, Nature |
| **Fey** | Arcana, Nature |
| **Fiend** | Religion |
| **Giant** | History, Insight |
| **Humanoid** | History, Insight |
| **Monstrosity** | Nature |
| **Ooze** | Arcana, Nature |
| **Plant** | Nature, Survival |
| **Undead** | Religion |

## Files Created

### Core Service
**[src/talekeeper/services/monster_knowledge.py](src/talekeeper/services/monster_knowledge.py:1)**
- `MonsterKnowledgeService`: Main service class
- `MonsterKnowledge`: Dataclass for storing check results
- `MONSTER_KNOWLEDGE_SKILLS`: Dict mapping monster types to skills

Key methods:
- `get_applicable_skills(monster_type)`: Returns list of skills that can identify this monster type
- `calculate_dc(challenge_rating)`: Calculates the DC for the knowledge check
- `check_knowledge(monster_data, skill_check_result, skill_used)`: Performs check and returns revealed info
- `format_tooltip_html(knowledge, skill_used, roll_result)`: Generates HTML for tooltip display

### UI Components
**[src/talekeeper/ui/monster_knowledge_label.py](src/talekeeper/ui/monster_knowledge_label.py:1)**

Two main widgets:

1. **`MonsterKnowledgeDialog`**: Dialog for making knowledge checks
   - Skill selection dropdown (shows only applicable skills)
   - Roll input with auto-roll button
   - Automatic modifier calculation based on character stats
   - Result display with color-coded success/failure

2. **`MonsterKnowledgeLabel`**: Clickable label with hover tooltip
   - Displays monster name
   - Shows hint tooltip on hover (DC and applicable skills)
   - Opens knowledge check dialog on click
   - Stores and displays knowledge check results
   - Emits `knowledge_checked` signal when check completes

### Demo/Test Script
**[test_monster_knowledge.py](test_monster_knowledge.py:1)**

Standalone PyQt6 application that demonstrates the system:
- Loads monsters from database
- Shows interactive monster labels
- Allows clicking to make knowledge checks
- Displays check results in console

## Usage Example

### In Code

```python
from talekeeper.services.monster_knowledge import monster_knowledge_service
from talekeeper.ui.monster_knowledge_label import MonsterKnowledgeLabel

# Create a clickable monster label
monster_data = {
    'name': 'Adult Red Dragon',
    'type': 'dragon',
    'challenge_rating': '17',
    'armor_class': 19,
    'hit_points': 256,
    # ... other monster data
}

character_data = {
    'level': 10,
    'intelligence': 16,
    'wisdom': 14,
    'class_id': 'wizard'
}

# Create label widget
label = MonsterKnowledgeLabel(monster_data, character_data)
label.knowledge_checked.connect(on_knowledge_complete)

# Or perform check directly
knowledge = monster_knowledge_service.check_knowledge(
    monster_data,
    skill_check_result=20,
    skill_used='arcana'
)

print(f"DC: {knowledge.dc}")
print(f"Success: {knowledge.success}")
print(f"Margin: {knowledge.margin}")
for category, value in knowledge.revealed_info:
    print(f"{category}: {value}")
```

### Running the Demo

```bash
python test_monster_knowledge.py
```

The demo will:
1. Load monsters from the database
2. Display them as clickable labels
3. Allow you to click and make knowledge checks
4. Show results in both the UI and console

## Integration with Encounter Panel

To integrate with your encounter panel, replace regular monster name labels with `MonsterKnowledgeLabel`:

```python
from talekeeper.ui.monster_knowledge_label import MonsterKnowledgeLabel

# Instead of:
monster_label = QLabel(monster_name)

# Use:
monster_label = MonsterKnowledgeLabel(
    monster_data=monster_dict,
    character_data=current_character_dict
)

# Listen for knowledge checks
monster_label.knowledge_checked.connect(
    lambda k: print(f"Player learned about {monster_name}")
)
```

## Features

### Automatic Skill Modifier Calculation
The dialog automatically calculates skill modifiers based on:
- Character's ability scores (Int for Arcana, Wis for Nature, etc.)
- Proficiency bonus (calculated from level)
- Simplified proficiency check (assumes Int skills for wizards, etc.)

### Progressive Information Reveal
Information is revealed gradually:
1. **Basic** (DC): Just enough to know what you're facing
2. **+2**: Tactical advantages (resistances/vulnerabilities)
3. **+4**: Combat stats (AC, HP)
4. **+6**: Abilities and attacks
5. **+8**: Complete stat block

### Rich HTML Tooltips
Tooltips use color-coded HTML:
- Green for successful checks
- Red for failures
- Categorized information display
- Professional dark theme styling

## Design Philosophy

1. **Player Agency**: Players choose when to make checks
2. **Risk/Reward**: Low rolls reveal nothing, high rolls reveal everything
3. **Skill Diversity**: Different monster types reward different knowledge skills
4. **Progressive Reveal**: Information scales with success
5. **Tactical Value**: Knowing resistances/vulnerabilities matters in combat

## Future Enhancements

Possible additions:
- Store knowledge checks per character (remember what you've learned)
- Passive checks (auto-reveal basic info if passive skill is high enough)
- Group checks (multiple party members can try)
- Retry penalties (harder to re-check the same monster)
- Bardic lore bonuses
- Creature type expertise (ranger favored enemy, etc.)

## Testing

Run the test script to verify:
```bash
python test_monster_knowledge.py
```

Expected behavior:
- Lists 10 sample monsters from database
- Shows CR, type, and applicable skills
- Clicking opens knowledge check dialog
- Dialog shows auto-calculated modifiers
- Results display properly formatted information
- Console shows detailed check results
