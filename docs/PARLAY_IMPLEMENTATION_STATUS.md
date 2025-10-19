# Parlay & Pickpocket Implementation Status

## Completed (Backend Services)

### 1. Enhanced parlay_system.py

**File**: `src/talekeeper/services/parlay_system.py`

#### New Methods
- `_determine_if_evil(alignment)` - Handle "any" alignment (1/3 chance evil)
- `_get_most_powerful_monster(monsters)` - Get monster with highest XP
- `get_parlay_skills_for_encounter(monsters)` - Intelligence/alignment-based skill selection with 4 parlay types
- `_get_intelligent_non_evil_skills()` - 2 CHA + 1 INT/WIS (Diplomatic)
- `_get_intelligent_evil_skills()` - Deception + Intimidation + random (Dangerous)
- `_get_simple_non_evil_skills()` - Nature + Survival + limited (Animal Handling)
- `_get_simple_evil_skills()` - Nature + Survival + very limited (Desperate)
- `_get_monster_insight(monster)` - DC from skill or raw WIS
- `_get_monster_perception(monster)` - DC from skill or raw WIS
- `execute_pickpocket_attempt(character_id, monsters)` - Dual skill check system
- `_get_character_skill_bonus(character_id, skill_name)` - Calculate skill bonus
- `_generate_individual_treasure(monster)` - CR-based loot generation
- `_award_pickpocket_xp(character_id, xp_amount)` - Award 75% XP
- `_add_treasure_to_inventory(character_id, treasure)` - Add item to inventory

#### Updated Methods
- `calculate_parlay_xp_reward(monsters)` - Now uses TOTAL encounter XP (sum of all monsters)
- `create_parlay_challenge(character_id, monsters)` - Uses enhanced skill selection, stores disadvantage mode in metadata

### 2. Enhanced skill_challenge_manager.py

**File**: `src/talekeeper/services/skill_challenge_manager.py`

#### Updated Dataclass
- `SkillAttemptResult` - Added `roll_breakdown` field for disadvantage display

#### Updated Methods
- `attempt_skill(session_id, skill_name, character_data)` - Now supports disadvantage via AdvantageSystem

#### New Methods
- `_get_session_disadvantage_mode(template_id)` - Read disadvantage mode from metadata

### 3. Database Migration

**File**: `database/migrations/040_skill_challenge_metadata.sql`

Created new table:
```sql
CREATE TABLE IF NOT EXISTS skill_challenge_metadata (
    template_id TEXT NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    PRIMARY KEY (template_id, metadata_key),
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_challenge_metadata_template
ON skill_challenge_metadata(template_id);
```

**Status**: Migration has been run successfully.

## Parlay System Features

### 4 Parlay Categories

| Category | Intelligence | Alignment | Skills | Disadvantage |
|----------|--------------|-----------|--------|--------------|
| **Diplomatic** | 4+ | Non-evil | 2 CHA + 1 INT/WIS (random) | None |
| **Dangerous** | 4+ | Evil | Deception + Intimidation + 1 random* | First check only |
| **Animal Handling** | ≤3 | Non-evil | Nature + Survival + 1 limited** | None |
| **Desperate** | ≤3 | Evil | Nature + Survival + 1 very limited*** | All checks |

*Random includes any skill OR tool proficiency
**Limited: Medicine, Insight, Persuasion, Intimidation
***Very limited: Insight, Persuasion, Intimidation

### XP Rewards
- **Parlay Success**: 50% of TOTAL encounter XP
- **Pickpocket Success**: 75% of TOTAL encounter XP + individual treasure

### Pickpocket Mechanics
- **Requirements**: Deception + Sleight of Hand proficiency
- **Availability**: After successful parlay OR successful stealth
- **Check 1**: Deception vs Monster Insight
- **Check 2**: Sleight of Hand vs Monster Perception
- **Both must succeed**
- **DC Calculation**:
  - If monster has skill: DC = 10 + skill bonus
  - If no skill: DC = raw Wisdom score (not modifier)
- **Risk**: Either check fails → Combat begins

## Pending Implementation (UI Integration)

### 1. encounter_panel.py Modifications

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

#### New Methods Needed
- `_handle_exploration_action(action)` - Route Influence button click
- `_attempt_parlay()` - Main parlay flow
- `_show_parlay_skill_challenge(session, xp_reward)` - Display skill challenge widget
- `_on_parlay_completed(outcome, reward_text, xp_reward)` - Handle success/failure
- `_on_parlay_refused(refuse_cost)` - Handle refusal
- `_check_pickpocket_opportunity()` - Check if pickpocket available
- `_restore_parlay_monsters_for_combat()` - Restore encounter on pickpocket failure

#### New Attributes Needed
- `_parlay_monsters` - Store monsters after successful parlay
- `_stealth_monsters` - Store monsters after successful stealth

#### Modifications Needed
- Connect Influence button to `_attempt_parlay()`
- Add pickpocket check after stealth success (around line 4753)
- Add pickpocket check after parlay success

### 2. skill_challenge_widget.py Modifications

**File**: `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

#### Modifications Needed
- Update `display_attempt_result()` to show disadvantage rolls in log
- Display `roll_breakdown` when present

### 3. action_panel.py Modifications

**File**: `src/talekeeper/ui/action_cards/action_panel.py`

#### New Methods Needed
- `_check_for_pickpocket_card()` - Create pickpocket action card
- `_execute_pickpocket()` - Execute dual skill checks, handle results

## Testing Checklist

### Backend Services (Ready to Test)
- [ ] Test `_determine_if_evil()` with "any" alignment
- [ ] Test `get_parlay_skills_for_encounter()` with all 4 categories
- [ ] Test `calculate_parlay_xp_reward()` with multiple monsters
- [ ] Test `execute_pickpocket_attempt()` dual checks
- [ ] Test monster DC calculation (skill vs raw WIS)
- [ ] Test disadvantage in `attempt_skill()`
- [ ] Test treasure generation by CR

### UI Integration (Pending)
- [ ] Influence button triggers parlay
- [ ] Skill challenge widget displays
- [ ] Disadvantage displayed in widget
- [ ] Parlay success awards XP
- [ ] Parlay failure starts combat
- [ ] Pickpocket card appears after parlay
- [ ] Pickpocket card appears after stealth
- [ ] Pickpocket success awards XP + treasure
- [ ] Pickpocket failure starts combat

## Next Steps

1. **UI Integration Sprint 1: Influence Button**
   - Wire Influence button to `_attempt_parlay()`
   - Create parlay flow handlers
   - Display skill challenge widget

2. **UI Integration Sprint 2: Disadvantage Display**
   - Update skill_challenge_widget.py
   - Show roll breakdown for disadvantage

3. **UI Integration Sprint 3: Pickpocket System**
   - Add pickpocket action card
   - Wire to parlay/stealth success
   - Handle dual check results

4. **Testing & Polish**
   - Test all 4 parlay categories
   - Test all edge cases
   - Polish UI messages

## Implementation Notes

### Key Design Decisions
- **Total Encounter XP**: Uses sum of all monsters (matches combat reward structure)
- **Existing Systems**: Leverages AdvantageSystem for disadvantage mechanics
- **Metadata Storage**: Disadvantage mode stored in skill_challenge_metadata table
- **Pickpocket Triggers**: Two paths - parlay success OR stealth success
- **Raw Wisdom DC**: Uses monster Wisdom score directly (not modifier) for balance

### File Dependencies
- `parlay_system.py` depends on:
  - `dice.py` (for rolls)
  - `skill_challenge_manager.py` (for challenges)
  - `loot_drop_service.py` (for treasure)
- `skill_challenge_manager.py` depends on:
  - `advantage_system.py` (for disadvantage)
  - `proficiency_bonus.py` (for bonuses)
  - `item_effects.py` (for item bonuses)

### Database Schema
- `skill_challenge_metadata` table created
- Stores template-level metadata (disadvantage_mode)
- Cascades on template deletion
