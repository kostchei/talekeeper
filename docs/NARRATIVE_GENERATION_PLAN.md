# Narrative Generation System - Implementation Plan

## Overview
Extend TaleKeeper's Ollama integration to generate campaign-styled narrative descriptions of combat events by parsing combat logs and feeding structured data through LLM prompts customized per campaign frame.

## Current State (v1.0 - Static Entities)

### What Works
- **CampaignDescriptionService** generates descriptions for static entities:
  - Monsters (when encounter spawned)
  - Hazards (when hazard generated)
  - Traps (when trap triggered)
  - Vendors (when shop opened)
- **Campaign-specific prompts** via `narrative_prompt` field in campaign JSON
- **Graceful fallback** to deterministic text when Ollama unavailable
- **LoRA adapter support** (configured but not yet utilized)

### Architecture
```
EncounterPanel
    |
    +-- CampaignDescriptionService (Ollama client)
    |       |
    |       +-- generate_description(entity_type, entity_data, campaign_frame)
    |
    +-- EncounterGenerator
            |
            +-- Adds 'narrative_description' field to entities
```

### Files
- `services/campaign_description_service.py` - LLM integration
- `encounter_pane/campaign_frame.py` - Campaign configuration
- `encounter_pane/encounter_panel.py` - UI integration
- `encounter_pane/encounter_generator.py` - Encounter spawning
- `encounter_pane/campaign/*.json` - Campaign configurations

## Target State (v2.0 - Dynamic Combat Narratives)

### Goals
1. **Parse combat logs** into structured event data
2. **Generate campaign-styled narratives** from combat events
3. **Display alongside mechanical results** in encounter details
4. **Support LoRA adapters** for fine-tuned campaign prose

### Example Flow
```
Player attacks Goblin with Longsword
    |
    V
Combat Manager resolves attack
    |
    V
Log Entry: "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. HIT! Damage: 1d8+3 = 11"
    |
    V
CombatLogParser extracts structured data:
    {
        "attacker": "Fighter",
        "target": "Goblin",
        "action": "Attack",
        "weapon": "Longsword",
        "attack_roll": 23,
        "target_ac": 15,
        "hit": true,
        "damage": 11,
        "critical": false
    }
    |
    V
CampaignDescriptionService generates narrative:
    "Your blade carves through goblin flesh with savage precision.
    The creature shrieks as steel bites deep, dark blood pooling
    beneath its feet."
    |
    V
Display in encounter_details_text
```

## Implementation Components

### 1. Combat Log Parser
**File**: `services/combat_log_parser.py`

**Responsibility**: Extract structured event data from combat text

**Key Methods**:
```python
class CombatLogParser:
    def parse_attack_event(self, log_text: str) -> Dict[str, Any]:
        """Extract attack data from log entry."""
        return {
            "attacker": str,
            "target": str,
            "action": str,
            "weapon": str,
            "attack_roll": int,
            "target_ac": int,
            "hit": bool,
            "damage": int,
            "damage_type": str,
            "critical": bool,
            "advantage": bool | None
        }

    def parse_spell_event(self, log_text: str) -> Dict[str, Any]:
        """Extract spell casting data."""
        return {
            "caster": str,
            "spell_name": str,
            "spell_level": int,
            "targets": List[str],
            "save_dc": int,
            "save_results": Dict[str, bool],
            "damage": int,
            "effects": List[str]
        }

    def parse_condition_event(self, log_text: str) -> Dict[str, Any]:
        """Extract condition application/removal."""
        return {
            "entity": str,
            "condition": str,
            "applied": bool,  # True = applied, False = removed
            "source": str
        }

    def parse_death_event(self, log_text: str) -> Dict[str, Any]:
        """Extract entity death."""
        return {
            "entity": str,
            "killer": str,
            "killing_blow": str
        }

    def parse_combat_round(self, log_entries: List[str]) -> List[Dict[str, Any]]:
        """Parse entire combat round into event list."""
        # Identifies event types and routes to appropriate parser
```

**Event Types to Support**:
- Attacks (melee, ranged, spell attacks)
- Damage (weapon, spell, conditions)
- Saves (success/failure)
- Conditions (applied, removed)
- Healing (potions, spells, class features)
- Deaths (player down, monster killed)
- Special actions (dash, hide, disengage, second wind, rage)

### 2. Enhanced Campaign Description Service
**File**: `services/campaign_description_service.py`

**New Methods**:
```python
class CampaignDescriptionService:
    def generate_combat_narrative(
        self,
        combat_events: List[Dict[str, Any]],
        campaign_frame: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate narrative from structured combat events.

        Parameters
        ----------
        combat_events:
            List of parsed combat events from CombatLogParser
        campaign_frame:
            Campaign configuration with narrative_combat_prompt
        context:
            Optional additional context (location, mood, stakes)

        Returns
        -------
        Narrative description of combat events in campaign style
        """

    def generate_round_summary(
        self,
        round_events: List[Dict[str, Any]],
        campaign_frame: Any
    ) -> str:
        """Generate end-of-round narrative summary."""

    def generate_victory_narrative(
        self,
        combat_summary: Dict[str, Any],
        campaign_frame: Any
    ) -> str:
        """Generate post-combat victory description."""
```

**New Prompt Templates**:
```python
self._combat_event_prompt = Template("""
You are narrating a $campaign_style D&D combat encounter.

Combat Events (this action):
$events_json

Write 1-2 vivid sentences describing these events. Keep under 50 words.
Focus on action, stakes, and atmosphere. Avoid repeating mechanical details.
Style: $campaign_description
""")

self._round_summary_prompt = Template("""
You are narrating a $campaign_style D&D combat round.

All Events This Round:
$round_events_json

Write 2-3 sentences summarizing the chaos of this combat round.
Keep under 70 words. Emphasize momentum shifts and dramatic moments.
Style: $campaign_description
""")

self._victory_prompt = Template("""
You are narrating a $campaign_style D&D combat victory.

Combat Summary:
$combat_summary_json

Write 2-3 sentences describing the aftermath of victory.
Keep under 70 words. Focus on cost of victory and spoils.
Style: $campaign_description
""")
```

### 3. Campaign Frame Extensions
**Files**: `encounter_pane/campaign/*.json`

**New Fields**:
```json
{
  "name": "Conan",
  "description": "A savage sword-and-sorcery world...",
  "style": "conan",
  "llm_model": "mistral:7b-instruct",

  // NEW: Combat narrative prompts
  "narrative_combat_prompt": "Narrate this Conan-style combat action in muscular, visceral prose. Events: $events_json. Write 1-2 sentences under 50 words focusing on blood, steel, and savage violence.",

  "narrative_round_summary_prompt": "Summarize this combat round in Conan style. Events: $round_events_json. Write 2-3 sentences under 70 words capturing the brutal chaos.",

  "narrative_victory_prompt": "Describe the aftermath of this Conan-style victory. Summary: $combat_summary_json. Write 2-3 sentences under 70 words about blood-soaked triumph.",

  // NEW: Optional LoRA adapter for fine-tuned prose
  "lora_adapter": null,  // Path to .gguf LoRA file or null

  // Existing fields...
  "monster_type_weights": {...}
}
```

**Example Campaign Variations**:

**Conan** (Savage Sword & Sorcery):
```json
"narrative_combat_prompt": "Write brutal, visceral combat prose. Focus on blood, steel, primal fury. 1-2 sentences, under 50 words."
```

**Golden Age** (High Fantasy):
```json
"narrative_combat_prompt": "Write heroic, epic combat prose. Focus on valor, legendary deeds, magical wonder. 1-2 sentences, under 50 words."
```

**Dark Sun** (Gritty Survival):
```json
"narrative_combat_prompt": "Write desperate, brutal combat prose. Focus on survival, harsh environment, scarce resources. 1-2 sentences, under 50 words."
```

### 4. Integration Points

#### A. Encounter Panel Integration
**File**: `encounter_pane/encounter_panel.py`

**Changes**:
```python
class EncounterPanel(QWidget):
    def __init__(self, ...):
        # Existing
        self.description_service = CampaignDescriptionService()

        # NEW: Add combat log parser
        self.combat_log_parser = CombatLogParser()
        self.combat_round_events = []  # Accumulate events for round summary

    def _apply_combat_action(self, action_result: Dict[str, Any]):
        """Called when combat action resolves."""
        # Existing: Update HP, conditions, etc.

        # NEW: Parse the action into structured event
        event = self.combat_log_parser.parse_attack_event(action_result)
        self.combat_round_events.append(event)

        # NEW: Generate narrative for this action
        if self.description_service and self.campaign_frame:
            narrative = self.description_service.generate_combat_narrative(
                [event],
                self.campaign_frame
            )

            # Display alongside mechanical results
            current_text = self.encounter_details_text.toPlainText()
            self.encounter_details_text.setPlainText(
                f"{current_text}\n\n{narrative}"
            )

    def _end_combat_round(self):
        """Called at end of round."""
        # NEW: Generate round summary narrative
        if self.combat_round_events and self.description_service:
            summary = self.description_service.generate_round_summary(
                self.combat_round_events,
                self.campaign_frame
            )
            self.encounter_details_text.appendPlainText(f"\n\n--- {summary} ---\n")
            self.combat_round_events = []  # Reset for next round

    def _end_combat(self, victory: bool):
        """Called when combat ends."""
        # NEW: Generate victory/defeat narrative
        if victory and self.description_service:
            combat_summary = {
                "duration_rounds": self.combat_round,
                "enemies_defeated": len(self.defeated_monsters),
                "damage_taken": self.total_damage_taken,
                "resources_spent": self.resources_used
            }
            narrative = self.description_service.generate_victory_narrative(
                combat_summary,
                self.campaign_frame
            )
            self.encounter_details_text.appendPlainText(f"\n\n{narrative}\n")
```

#### B. Action Panel Integration
**File**: `action_cards/action_panel.py`

**Changes**:
```python
def _execute_attack_action(self, action: Dict[str, Any]):
    """Execute attack and generate narrative."""
    # Existing: Roll attack, calculate damage
    result = self.combat_engine.resolve_attack(...)

    # NEW: Return structured data for parsing
    return {
        "type": "attack",
        "attacker": character_name,
        "target": target_name,
        "weapon": weapon_name,
        "attack_roll": total_roll,
        "target_ac": target_ac,
        "hit": hit,
        "damage": damage_dealt,
        "critical": is_critical
    }
```

#### C. Combat Manager Integration
**File**: `core/combat_manager.py`

**Changes**:
```python
class CombatManager:
    def __init__(self, ...):
        self.log_parser = CombatLogParser()
        self.combat_events = []  # Track all events for narrative

    def process_turn(self, entity_id: str) -> List[Dict[str, Any]]:
        """Process entity turn and return structured events."""
        events = []

        # Existing turn logic...

        # NEW: Track events for narrative generation
        for action in turn_actions:
            event = self._action_to_event(action)
            events.append(event)
            self.combat_events.append(event)

        return events
```

### 5. LoRA Adapter System (Optional Enhancement)

**Purpose**: Fine-tune narrative style per campaign beyond base prompts

**Setup**:
1. **Collect training data** - Sample prose for each campaign style
   - Conan: Robert E. Howard excerpts
   - Golden Age: Classic D&D adventure prose
   - Dark Sun: Gritty survival narratives

2. **Train LoRA adapters** using Ollama:
   ```bash
   # Create Modelfile with LoRA
   FROM mistral:7b-instruct
   ADAPTER /path/to/conan-style-lora.gguf

   # Create custom model
   ollama create conan-narrator -f Modelfile
   ```

3. **Reference in campaign JSON**:
   ```json
   {
     "llm_model": "conan-narrator",
     "lora_adapter": null  // Built into model
   }
   ```

**Training Data Format**:
```
### Combat Event
Fighter attacks Goblin with longsword. Roll: 18+5=23 vs AC 15. Hit! Damage: 11.

### Narrative
Steel screams as your blade carves through the goblin's crude armor, dark blood spraying across stone. The creature's death-shriek echoes through ancient halls.

### Combat Event
Wizard casts Fireball at 3 goblins. DC 15 Dex save. 2 fail, 1 succeeds. Damage: 28 to failures, 14 to success.

### Narrative
Arcane fire erupts in crimson fury, consuming goblin flesh in an instant. Two collapse as charred husks while a third, singed but living, scrambles clear of the inferno.
```

### 6. Configuration & Settings

**File**: `core/config.py`

**New Settings**:
```python
class NarrativeConfig:
    enable_combat_narratives: bool = True
    enable_round_summaries: bool = True
    enable_victory_narratives: bool = True
    narrative_display_delay: float = 0.5  # Seconds before showing narrative
    max_narrative_cache: int = 50  # Prevent memory bloat
    fallback_to_mechanical: bool = True  # Show mechanics if LLM fails
```

**UI Toggle** (in encounter panel):
```python
self.narrative_toggle = QCheckBox("Show Campaign Narratives")
self.narrative_toggle.setChecked(config.narrative.enable_combat_narratives)
```

## Implementation Phases

### Phase 1: Core Infrastructure ✅ COMPLETED (2025-10-02)
- [x] Create `services/combat_log_parser.py`
- [x] Implement attack event parsing
- [x] Implement damage/healing parsing
- [x] Write unit tests for parser (17/17 passing)

**Files Created:**
- `services/combat_log_parser.py` - Event parsing from combat logs
- `tests/test_combat_log_parser.py` - Comprehensive unit tests

### Phase 2: Service Extension ✅ COMPLETED (2025-10-02)
- [x] Extend `CampaignDescriptionService` with combat methods
- [x] Add combat prompt templates (`_combat_event_prompt`, `_round_summary_prompt`, `_victory_prompt`)
- [x] Add `generate_combat_narrative()` method
- [x] Add `generate_round_summary()` method
- [x] Add `generate_victory_narrative()` method
- [x] Verify fallback behavior (graceful degradation)

**Files Modified:**
- `services/campaign_description_service.py` - Extended with combat narrative methods

### Phase 3: Integration 🔄 IN PROGRESS
- [x] Update `encounter_panel.py` to initialize parser and service
- [ ] **NEXT STEP:** Update `action_panel.py` to return structured events
- [ ] **NEXT STEP:** Hook combat event parsing into attack resolution
- [ ] **NEXT STEP:** Display narratives alongside mechanical results in UI
- [ ] Wire round summary generation (end of round)
- [ ] Wire victory narrative generation (combat end)
- [ ] Test live combat with actual encounters

**Files Modified:**
- `encounter_pane/encounter_panel.py` - Added `CombatLogParser` initialization

**Remaining Integration Work:**
1. Modify `action_panel.py` to capture combat actions as structured events
2. Pass events to `combat_log_parser` for parsing
3. Call `description_service.generate_combat_narrative()` with parsed events
4. Display narrative in `encounter_details_text` alongside mechanics
5. Wire up round/victory narratives at appropriate trigger points

### Phase 4: Campaign Configuration ✅ COMPLETED (2025-10-02)
- [x] Update campaign JSON files with combat prompts (Conan, Golden Age)
- [x] Create campaign-specific narrative prompt variations
  - Conan: Brutal, visceral, savage violence
  - Golden Age: Heroic, epic, legendary deeds
- [ ] Test each campaign frame for narrative quality (pending live integration)
- [ ] Document prompt engineering guidelines

**Files Modified:**
- `encounter_pane/campaign/conan.json` - Added combat narrative prompts
- `encounter_pane/campaign/golden.json` - Added combat narrative prompts

### Phase 5: Polish & Optimization (Not Started)
- [ ] Add UI toggle for narratives
- [ ] Implement narrative caching
- [ ] Add configuration options in `core/config.py`
- [ ] Performance testing (ensure <200ms generation)
- [ ] Error handling improvements
- [ ] Async generation to avoid UI blocking

### Phase 6: LoRA Adapters (Optional - Future)
- [ ] Collect training data for 3 campaign styles
- [ ] Train LoRA adapters using Ollama
- [ ] Test adapter integration
- [ ] Document adapter creation process

## Testing Strategy

### Unit Tests
**File**: `tests/test_combat_log_parser.py`
```python
def test_parse_attack_hit():
    parser = CombatLogParser()
    log = "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. HIT! Damage: 1d8+3 = 11"
    event = parser.parse_attack_event(log)

    assert event["attacker"] == "Fighter"
    assert event["target"] == "Goblin"
    assert event["hit"] == True
    assert event["damage"] == 11

def test_parse_attack_miss():
    log = "Fighter attacks Goblin: Roll 7+5=12 vs AC 15. MISS!"
    event = parser.parse_attack_event(log)
    assert event["hit"] == False
    assert event["damage"] == 0
```

**File**: `tests/test_campaign_description_service.py`
```python
def test_generate_combat_narrative():
    service = CampaignDescriptionService()
    campaign = CampaignFrame(data={
        "name": "Test",
        "style": "heroic",
        "narrative_combat_prompt": "Describe: $events_json"
    })

    event = {"attacker": "Fighter", "target": "Goblin", "hit": True, "damage": 11}
    narrative = service.generate_combat_narrative([event], campaign)

    assert narrative is not None
    assert len(narrative) > 20  # Not empty or trivial
    assert len(narrative.split()) < 70  # Under word limit
```

### Integration Tests
**File**: `tests/test_narrative_integration.py`
```python
def test_combat_with_narratives():
    """Full combat flow with narrative generation."""
    # Create character, start encounter
    # Execute attack action
    # Verify narrative appears in encounter_details_text
    # Verify mechanical details also present
```

### Manual Testing Checklist
- [ ] Generate monster encounter in Conan campaign
- [ ] Execute attack and verify narrative appears
- [ ] Verify narrative matches Conan style (savage, visceral)
- [ ] Switch to Golden Age campaign
- [ ] Verify narrative changes to heroic style
- [ ] Test with Ollama stopped (fallback to mechanical)
- [ ] Test round summary generation
- [ ] Test victory narrative generation
- [ ] Verify no performance degradation (<200ms)

## Performance Considerations

### Latency Budget
- **LLM Generation**: 500-2000ms (acceptable - player reading previous text)
- **Log Parsing**: <10ms (negligible)
- **UI Update**: <50ms (imperceptible)

### Optimization Strategies
1. **Async Generation**: Don't block UI while waiting for LLM
2. **Batch Events**: Generate narrative for multiple events together
3. **Cache Results**: Store narratives for identical event patterns
4. **Timeout**: Fall back to mechanical if LLM takes >3s
5. **Event Filtering**: Only generate narratives for "interesting" events

### Memory Management
- Limit narrative cache to 50 entries
- Clear combat events after round summary
- Don't store raw log text long-term

## User Experience

### Display Format
```
Encounter Details Panel:

=== ROUND 1 ===

Fighter attacks Goblin
Roll: 18+5=23 vs AC 15 - HIT!
Damage: 1d8+3 = 11

>> Your blade carves through goblin flesh with savage precision.
   The creature shrieks as steel bites deep.

Goblin attacks Fighter
Roll: 12+4=16 vs AC 18 - MISS!

>> The goblin's crude blade clangs uselessly against your shield.

--- Round 1 ends in a clash of steel and fury.
    Blood stains the stones as you press your advantage. ---

=== ROUND 2 ===
...
```

### Configuration Options
```
Settings > Narrative Generation
  [x] Enable Combat Narratives
  [x] Show Round Summaries
  [x] Show Victory Descriptions
  [ ] Show Only Narratives (hide mechanics)

  Narrative Style: [Campaign Default ▼]
  Generation Timeout: [3] seconds
```

## Documentation Requirements

### User Documentation
**File**: `docs/NARRATIVE_GENERATION_GUIDE.md`
- What are campaign narratives?
- How to enable/disable
- How to customize per campaign
- Troubleshooting (Ollama connection, slow generation)

### Developer Documentation
**File**: `docs/NARRATIVE_GENERATION_DEVELOPER.md`
- Architecture overview
- Adding new event types
- Creating campaign prompts
- Training LoRA adapters
- Testing narrative generation

### Campaign Creation Guide
**File**: `docs/CAMPAIGN_NARRATIVE_PROMPTS.md`
- Prompt engineering best practices
- Example prompts per genre
- Template variables reference
- Testing prompt quality

## Future Enhancements

### Post-v2.0 Ideas
1. **Location-aware narratives** - Different prose for dungeons vs wilderness
2. **Character personality integration** - Narratives reflect PC background/class
3. **Dynamic difficulty** - Adjust narrative tension based on PC health
4. **NPC dialogue generation** - Monster taunts, vendor banter
5. **Quest narrative summaries** - Session recap generation
6. **Image generation** - DALL-E style scene illustrations (via Stable Diffusion)
7. **Audio narration** - TTS reading narratives aloud
8. **Multi-turn context** - LLM remembers previous combat rounds
9. **Branching narratives** - Different outcomes based on tactics
10. **Player choice integration** - Narratives acknowledge stealth, diplomacy, etc.

## Success Metrics

### Technical Metrics
- [ ] 95%+ log parsing accuracy
- [ ] <2s average narrative generation time
- [ ] <5% LLM failure rate (with fallback)
- [ ] Zero UI blocking during generation

### Quality Metrics
- [ ] Narratives match campaign tone (user survey)
- [ ] No mechanical detail repetition
- [ ] Word count within limits (50-70 words)
- [ ] Readability (Flesch-Kincaid Grade 8-10)

### User Adoption
- [ ] 70%+ users enable narratives
- [ ] Positive feedback in playtesting
- [ ] No performance complaints

## Risks & Mitigations

### Risk: LLM Generation Too Slow
**Mitigation**: Async generation, timeout fallback, smaller model option (phi:3b)

### Risk: Narratives Don't Match Tone
**Mitigation**: LoRA adapters, extensive prompt testing, user feedback iteration

### Risk: Log Parsing Fails
**Mitigation**: Robust regex patterns, extensive test coverage, graceful degradation

### Risk: Memory Bloat
**Mitigation**: Event cache limits, clear after rounds, monitor in testing

### Risk: Ollama Not Installed
**Mitigation**: Clear setup instructions, fallback to mechanical text, optional feature

## References

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [LoRA Adapter Training Guide](https://github.com/ollama/ollama/blob/main/docs/modelfile.md#adapter)
- [Mistral 7B Model Card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- Existing Implementation: `services/campaign_description_service.py`
- Related: `docs/ENHANCED_SYSTEMS_GUIDE.md` (condition system, action economy)

---

## Next Steps for Completion

### Priority 1: Complete Action Panel Integration
**File**: `action_cards/action_panel.py`

**Objective**: Capture combat action results as structured data and generate narratives

**Steps**:
1. Locate attack resolution methods in `action_panel.py`
2. After attack resolves, create structured event dict:
   ```python
   combat_event = {
       "type": "attack",
       "attacker": character_name,
       "target": target_name,
       "weapon": weapon_name,
       "attack_roll": total_roll,
       "target_ac": target_ac,
       "hit": hit_success,
       "damage": damage_dealt,
       "critical": is_critical
   }
   ```
3. Emit event to encounter panel via signal or parent method call
4. Encounter panel receives event, stores in `self.combat_round_events`

### Priority 2: Generate and Display Narratives
**File**: `encounter_pane/encounter_panel.py`

**Objective**: Generate campaign-styled narratives from combat events

**Steps**:
1. Create method to handle combat events:
   ```python
   def _on_combat_event(self, event: Dict[str, Any]):
       # Store event for round summary
       self.combat_round_events.append(event)

       # Generate narrative for this action
       if self.description_service and self.campaign_frame:
           try:
               narrative = self.description_service.generate_combat_narrative(
                   [event],
                   self.campaign_frame
               )
               if narrative:
                   # Display narrative in encounter_details_text
                   current_text = self.encounter_details_text.toPlainText()
                   self.encounter_details_text.setPlainText(
                       f"{current_text}\n\n>> {narrative}"
                   )
           except Exception as e:
               print(f"[Narrative] Generation failed: {e}")
   ```

2. Connect action panel events to this handler
3. Test with simple attack action

### Priority 3: Round and Victory Narratives
**File**: `encounter_pane/encounter_panel.py`

**Objective**: Generate summaries at key combat milestones

**Steps**:
1. Hook into end-of-round logic:
   ```python
   def _end_combat_round(self):
       if self.combat_round_events and self.description_service:
           summary = self.description_service.generate_round_summary(
               self.combat_round_events,
               self.campaign_frame
           )
           if summary:
               self.encounter_details_text.appendPlainText(
                   f"\n\n--- {summary} ---\n"
               )
           self.combat_round_events = []  # Reset for next round
   ```

2. Hook into combat victory logic:
   ```python
   def _end_combat(self, victory: bool):
       if victory and self.description_service:
           combat_summary = {
               "duration_rounds": self.combat_round_count,
               "enemies_defeated": len(self.defeated_monsters),
               "damage_taken": self.total_damage_taken
           }
           narrative = self.description_service.generate_victory_narrative(
               combat_summary,
               self.campaign_frame
           )
           if narrative:
               self.encounter_details_text.appendPlainText(
                   f"\n\n{narrative}\n"
               )
   ```

### Priority 4: Live Testing
**Objective**: Verify narrative generation works end-to-end

**Test Scenarios**:
1. Start TaleKeeper with Conan campaign
2. Create level 1 Fighter character
3. Generate monster encounter (Goblin)
4. Execute attack action
5. Verify:
   - [ ] Mechanical details appear (roll, damage)
   - [ ] Narrative appears prefixed with `>>`
   - [ ] Narrative matches Conan style (brutal, visceral)
6. Switch to Golden Age campaign
7. Repeat and verify heroic narrative style

### Priority 5: Error Handling & Polish
**Objective**: Graceful degradation and user experience

**Steps**:
1. Add try/catch around all narrative generation
2. If Ollama unavailable, silently skip narratives (mechanics still work)
3. Add console logging for debugging: `[Narrative] Generated in 1.2s`
4. Consider adding UI toggle to enable/disable narratives
5. Test with Ollama stopped to verify fallback

---

**Document Status**: Implementation In Progress
**Last Updated**: 2025-10-02 (Phase 1-4 Complete, Phase 3 Partial)
**Author**: Claude Code + User
**Review Status**: Ready for Phase 3 Completion
**Regression Tests**: ✅ All Passing (9/9 quick tests)
