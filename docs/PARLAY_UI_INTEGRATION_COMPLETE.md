# Parlay UI Integration - Phase 1 Complete

## Summary

The Influence button is now fully wired to the parlay system! Players can attempt diplomatic resolution of encounters.

## What's Working

### 1. Influence Button Flow
- Click "Influence" button on encounter screen
- System checks if monsters can be parlayed with (non-evil, 75% chance)
- If successful, displays skill challenge widget
- If failed, shows message explaining why

### 2. Parlay Skill Challenge
- Uses intelligence and alignment of most powerful monster
- 4 parlay types:
  - **Diplomatic** (INT 4+, non-evil): 2 CHA + 1 INT/WIS skills
  - **Dangerous** (INT 4+, evil): Deception + Intimidation + random (first check disadvantage)
  - **Animal Handling** (INT 3-, non-evil): Nature + Survival + limited
  - **Desperate** (INT 3-, evil): Nature + Survival + limited (all checks disadvantage)

### 3. Parlay Outcomes
- **Success**: Awards 50% of total encounter XP, clears encounter
- **Failure**: Starts combat with the encounter
- **Refused**: Clears encounter, no XP

### 4. Files Modified

#### `src/talekeeper/ui/main_window.py`
- Updated `_handle_exploration_action()` to call `encounter_panel.attempt_parlay()`

#### `src/talekeeper/ui/encounter_pane/encounter_panel.py`
- Added `attempt_parlay()` - Main parlay entry point
- Added `_show_parlay_skill_challenge()` - Display skill widget
- Added `_on_parlay_completed()` - Handle success/failure
- Added `_on_parlay_refused()` - Handle refusal
- Added `_check_pickpocket_opportunity()` - Placeholder for pickpocket
- Added `_clear_encounter_after_parlay()` - Cleanup
- Added `_restore_parlay_encounter_for_combat()` - Combat on failure
- Added `_parlay_monsters` and `_stealth_monsters` attributes

## How to Test

1. Run the application: `python main.py`
2. Create/load a character
3. Click "Generate Encounter"
4. Click "Influence" button
5. Observe parlay eligibility check
6. If eligible, attempt skill challenge
7. Test success, failure, and refusal paths

## What's Next (Phase 2)

### Pickpocket System
- Add action card after successful parlay
- Implement dual skill check (Deception + Sleight of Hand)
- Award 75% XP + treasure on success
- Start combat on failure

### Stealth Integration
- Add pickpocket check after stealth success
- Store monsters in `_stealth_monsters`

### Disadvantage Display
- Update skill_challenge_widget.py to show roll breakdown
- Display "Rolled 2d20, took lower: [15, 8] = 8"

## Technical Notes

### XP Calculation
- Uses TOTAL encounter XP (sum of all monsters)
- Example: 4 Goblins (50 XP each) = 200 XP total → 100 XP for parlay

### Monster Data Flow
1. `encounter_instances` (EncounterInstance objects with monster_full_data)
2. Extract `monster_full_data` + add `xp` and `challenge_rating` fields
3. Pass to ParlaySystem for skill selection and XP calculation

### Disadvantage Mechanics
- Stored in `skill_challenge_metadata` table
- Read by `skill_challenge_manager` during skill checks
- Applied via existing `AdvantageSystem`

## Known Limitations

1. Pickpocket action card not yet implemented
2. Stealth → pickpocket path not yet wired
3. Disadvantage rolls not displayed in skill widget (functional but invisible)
4. No character skill proficiency check (assumes proficiency for now)

## Dependencies Verified

- `parlay_system.py` ✓
- `skill_challenge_manager.py` ✓
- `skill_challenge_widget.py` (existing, works)
- `advantage_system.py` ✓
- `loot_drop_service.py` ✓
- Database migration 040 ✓
