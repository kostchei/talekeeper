# Tarot Card System

## Overview
TaleKeeper's narrative generation system uses tarot cards to inspire encounter descriptions. Each encounter draws a random tarot card that influences the atmosphere and tone of the generated narrative.

## How It Works

### 1. Card Drawing
When an encounter is generated, the system:
1. Draws a random tarot card from 16 available cards
2. Determines if the card is upright or reversed
3. Selects one of three aspects: place, situation, or creature
4. Extracts a detail that inspires the narrative

### 2. Narrative Generation
The tarot inspiration is passed to the LLM along with:
- Monster information (names, types, CR, alignment)
- Campaign style and description
- Encounter level and difficulty

The LLM is instructed to create a structured description:
1. **Begin with the tarot inspiration** to set the atmospheric tone
2. **Describe the place and situation** where monsters are encountered (2-3 sentences)
3. **List each unique monster type** with a bullet point and 1-sentence appearance description

Example output structure:
```
In a world twisted by sorcery, a desolate canyon echoes with ancient magic.
At the heart of this forsaken land, a cave entrance yawns ominously.

- Goblin: Malicious green-skinned imps with yellow eyes gleaming
- Hobgoblin: A hulking battle-scarred figure with a twisted sneer
```

### 3. Shared Description
All monsters in an encounter receive the same `encounter_description` field, ensuring they appear together in a unified scene rather than as separate entities.

## Available Tarot Cards

### BALANCE
- **Upright**: Symmetrical spaces, careful choices, fair judgment
- **Reversed**: Unbalanced chaos, clouded judgment, bias

### BEAST
- **Upright**: Primal wilderness, survival instinct, natural predators
- **Reversed**: Corrupted nature, maddened rage, uncontrolled fury

### CAMPFIRE
- **Upright**: Warm refuge, fellowship, protective guardians
- **Reversed**: Cold abandonment, betrayal, false friends

### CAVERN
- **Upright**: Underground secrets, hidden depths, lair defenders
- **Reversed**: Collapsing tunnels, trapped darkness, blind predators

### CORPSE
- **Upright**: Learning from death, endings and beginnings
- **Reversed**: Senseless slaughter, meaningless death, undead

### DRAGON
- **Upright**: Legendary lairs, overwhelming might, primordial majesty
- **Reversed**: Ruined greed, mad tyrants, destructive power

### FLAMES
- **Upright**: Cleansing fire, transformation, elemental fury
- **Reversed**: Uncontrolled inferno, indiscriminate devastation

### MAZE
- **Upright**: Challenging puzzles, cunning guardians, secret ways
- **Reversed**: Maddening loops, endless confusion, lost souls

### MONSTROSITY
- **Upright**: Broken natural laws, aberrant existence
- **Reversed**: Spreading corruption, growing chaos, abominations

### RUINS
- **Upright**: Lost glory, surviving remnants, fallen civilizations
- **Reversed**: Crumbling decay, crushing failure, inevitable decline

### SKULL
- **Upright**: Mortality's focus, purposeful death, death incarnate
- **Reversed**: Meaningless carnage, paralyzing fear, mocking undeath

### TAVERN
- **Upright**: Lively rumors, social opportunities, hospitable hosts
- **Reversed**: Dens of vice, deceptive dealings, predatory figures

### TOWER
- **Upright**: Strongholds, sudden revelations, proud defenders
- **Reversed**: Crumbling ambition, catastrophic collapse, fallen powers

### UNDEAD
- **Upright**: Death's refusal, unfinished business, restless spirits
- **Reversed**: Mindless hunger, consuming past, spreading corruption

### VOID
- **Upright**: Pregnant emptiness, terrifying wonder, cosmic beings
- **Reversed**: Nihilistic despair, cosmic indifference, eldritch horrors

### WARRIOR
- **Upright**: Honorable combat, tested courage, skilled fighters
- **Reversed**: Senseless brutality, purposeless aggression, berserkers

## Usage Example

```python
from services.campaign_description_service import CampaignDescriptionService
from encounter_pane.campaign_frame import CampaignFrame

frame_data = {
    "name": "Conan",
    "style": "savage sword and sorcery",
    "description": "A brutal world of steel and blood"
}

frame = CampaignFrame(frame_data)
service = CampaignDescriptionService()

monsters = [
    {"name": "Goblin", "type": "humanoid", "cr_str": "1/4"},
    {"name": "Hobgoblin", "type": "humanoid", "cr_str": "1/2"}
]

description = service.generate_encounter_description(
    monsters,
    frame,
    level=1,
    difficulty="moderate"
)
```

## Customization

### Campaign-Specific Prompts
You can override the default encounter prompt in your campaign JSON:

```json
{
  "name": "Dark Sun",
  "narrative_encounter_prompt": "You are narrating a $campaign_style encounter in a harsh desert wasteland. Monsters: $monsters_json. Tarot: $tarot_inspiration. Write 3-4 sentences about the place, emphasizing brutal survival, then 1 sentence per monster. Keep under 100 words."
}
```

### Available Template Variables
- `$campaign_name` - Campaign name
- `$campaign_style` - Campaign style descriptor
- `$campaign_description` - Full campaign description
- `$monsters_json` - JSON array of monster data
- `$tarot_inspiration` - The drawn tarot detail
- `$tarot_card` - The card name (e.g., "WARRIOR")
- `$tarot_orientation` - "upright" or "reversed"

## Implementation Details

### Files
- `services/tarot_cards.py` - Card definitions and drawing logic
- `services/campaign_description_service.py` - Integration with LLM
- `encounter_pane/encounter_generator.py` - Encounter generation

### Key Functions
- `draw_tarot_card()` - Returns a random card with all metadata
- `get_tarot_inspiration(card)` - Extracts the detail text
- `generate_encounter_description()` - Creates unified narrative

### Data Structure
```python
card = {
    "name": "WARRIOR",
    "orientation": "upright",
    "aspect": "place",
    "detail": "A battlefield where courage is tested",
    "full_meanings": {
        "place": "...",
        "situation": "...",
        "creature": "..."
    }
}
```

## Inspiration Source
The tarot system draws inspiration from the [pleb repository](https://github.com/kostchei/pleb) by kostchei, which uses tarot cards to generate narrative hooks for D&D character creation. TaleKeeper adapts this concept for encounter generation, using simplified card meanings focused on place, situation, and creature aspects.

## Future Enhancements
- Expand to full 78-card tarot deck
- Add major arcana for legendary encounters
- Support drawing multiple cards for complex encounters
- Allow DMs to manually select cards
- Track card history to avoid repetition
- Add suit associations (e.g., Swords for combat-heavy)
