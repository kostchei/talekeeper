# Narrative Display System - Usage Guide

## Overview
The narrative display system allows combat logs to show both mechanical details (rolls, damage) and AI-generated narrative descriptions that match your campaign's style.

## Configuration

### Settings Dialog
Access via: **Game Menu > Settings > Narrative Generation**

Available options:
- **Enable Combat Narratives**: Generate narrative descriptions for combat actions (attacks, spells, etc.)
- **Show Round Summaries**: Generate narrative summaries at the end of each combat round
- **Show Victory Descriptions**: Generate narrative descriptions when combat ends victoriously
- **Show Only Narratives (hide mechanics)**: Hide mechanical details and show only narrative text

### Programmatic Configuration
```python
from core.config import get_config

config = get_config()

# Enable/disable narratives
config.narrative.enable_combat_narratives = True
config.narrative.enable_round_summaries = True
config.narrative.enable_victory_narratives = True
config.narrative.show_only_narratives = False

# Save changes
config.save_config()
```

## Log Panel Integration

### Log Levels
The log panel now supports a `NARRATIVE` log level:

```python
from log.log_panel import LogPanel, LogLevel

log_panel = LogPanel()

# Regular combat messages
log_panel.log_combat("Fighter attacks Goblin")
log_panel.log_dice("Roll: 18+5=23 vs AC 15 - HIT!")
log_panel.log_combat("Damage: 1d8+3 = 11")

# Narrative message (appears with >> prefix)
log_panel.log_narrative("Your blade carves through goblin flesh with savage precision.\nThe creature shrieks as steel bites deep.")
```

### Display Format
Narrative messages appear with:
- **Prefix**: `>>` (identifies narrative text)
- **Color**: Light blue (#a0d0ff)
- **Style**: Italic
- **Timestamp**: Standard log timestamp

Example output:
```
[14:32:15] [COMBAT] Fighter attacks Goblin
[14:32:15] [DICE] Roll: 18+5=23 vs AC 15 - HIT!
[14:32:15] [COMBAT] Damage: 1d8+3 = 11
[14:32:15] >> Your blade carves through goblin flesh with savage precision.
           The creature shrieks as steel bites deep.
```

## Combat Integration

### From Combat Manager
When processing combat actions, the combat manager should:

1. Log mechanical details (attack roll, damage)
2. Generate narrative using `CampaignDescriptionService`
3. Log narrative using `log_narrative()`

```python
from services.campaign_description_service import CampaignDescriptionService

# Log mechanics
self.log_panel.log_combat(f"{attacker_name} attacks {target_name}")
self.log_panel.log_dice(f"Roll: {roll}+{bonus}={total} vs AC {target_ac} - {'HIT' if hit else 'MISS'}!")

if hit:
    self.log_panel.log_combat(f"Damage: {damage_roll} = {damage_total}")

    # Generate and log narrative
    if self.description_service and self.campaign_frame:
        combat_event = {
            "attacker": attacker_name,
            "target": target_name,
            "hit": hit,
            "damage": damage_total,
            "critical": is_critical
        }
        narrative = self.description_service.generate_combat_narrative(
            [combat_event],
            self.campaign_frame
        )
        if narrative:
            self.log_panel.log_narrative(narrative)
```

### Round Summaries
At the end of each combat round:

```python
# Log round summary narrative
if self.config.narrative.enable_round_summaries:
    summary = self.description_service.generate_round_summary(
        round_events,
        self.campaign_frame
    )
    if summary:
        self.log_panel.log_narrative(f"\n{summary}")
```

### Victory Narratives
When combat ends:

```python
if victory and self.config.narrative.enable_victory_narratives:
    combat_summary = {
        "duration_rounds": round_count,
        "enemies_defeated": defeated_count,
        "damage_taken": total_damage
    }
    narrative = self.description_service.generate_victory_narrative(
        combat_summary,
        self.campaign_frame
    )
    if narrative:
        self.log_panel.log_narrative(f"\n{narrative}")
```

## Campaign-Specific Narratives

Narratives are generated based on the active campaign frame's prompts:

### Conan (Brutal Sword & Sorcery)
```
[14:32:15] >> Steel screams as your blade carves through the goblin's crude armor.
           Dark blood sprays across ancient stone.
```

### Golden Age (Heroic High Fantasy)
```
[14:32:15] >> Your righteous blade strikes true, felling the vile goblin with
           a single heroic blow that echoes through the halls!
```

### Dark Sun (Gritty Survival)
```
[14:32:15] >> Your obsidian blade finds flesh, drawing precious blood in this
           unforgiving wasteland. The goblin staggers, gasping in the scorching air.
```

## Configuration Storage

Settings are stored in `talekeeper_config.json`:

```json
{
  "narrative": {
    "enable_combat_narratives": true,
    "enable_round_summaries": true,
    "enable_victory_narratives": true,
    "show_only_narratives": false,
    "narrative_display_delay": 0.5,
    "max_narrative_cache": 50,
    "fallback_to_mechanical": true
  }
}
```

## Graceful Degradation

If Ollama is not running or narrative generation fails:
- Mechanical details are always shown (unless `show_only_narratives` is true)
- No error messages clutter the log
- Combat continues normally
- Silent fallback to mechanical descriptions

## Visual Identification

The `>>` prefix makes narratives easy to identify for:
- **Users**: Clearly distinguishes flavor text from mechanics
- **Developers**: Easy to parse for testing/debugging
- **Future systems**: Can be filtered or extracted programmatically

## Testing

Test narrative display:
```bash
python test_narrative_log.py
```

This will open a log panel window with sample combat and narrative messages.

## Next Steps

Once the narrative system is fully integrated:
1. Combat actions will automatically generate narratives
2. Round summaries will appear between rounds
3. Victory descriptions will celebrate triumphs
4. All controllable via Settings dialog

The system is designed to be:
- **Non-intrusive**: Can be disabled completely
- **Performant**: Async generation prevents UI blocking
- **Campaign-aware**: Narratives match the selected campaign style
- **Graceful**: Falls back to mechanics if LLM unavailable
