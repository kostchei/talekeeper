# Parlay & Pickpocket System - Implementation Summary

## Overview

Complete non-combat encounter resolution system with intelligence-based parlay and optional pickpocketing.

---

## System Components

### 1. Parlay System (Intelligence/Alignment-Based)

**Trigger**: Influence button during monster encounter

**4 Parlay Categories**:

| Category | Intelligence | Alignment | Skills | Disadvantage |
|----------|--------------|-----------|--------|--------------|
| **Diplomatic** | 4+ | Non-evil | 2 CHA + 1 INT/WIS (random) | None |
| **Dangerous** | 4+ | Evil | Deception + Intimidation + 1 random* | First check only |
| **Animal Handling** | ≤3 | Non-evil | Nature + Survival + 1 limited** | None |
| **Desperate** | ≤3 | Evil | Nature + Survival + 1 very limited*** | All checks |

*Random includes any skill OR tool proficiency
**Limited: Medicine, Insight, Persuasion, Intimidation
***Very limited: Insight, Persuasion, Intimidation (no Medicine)

**Special Case**: "any" alignment = 1/3 chance of being evil

**Rewards**:
- **Success**: 50% XP of strongest monster, no combat
- **Failure**: Combat begins normally
- **Refuse**: Walk away, no XP, no combat

---

### 2. Pickpocket System (Dual Skill Checks)

**Requirements**:
- Character has BOTH Deception AND Sleight of Hand proficiency
- Available after:
  - Successful parlay, OR
  - Successfully hidden via stealth

**Mechanics**:
- **Check 1**: Deception vs Monster Insight (distract)
- **Check 2**: Sleight of Hand vs Monster Perception (steal)
- **Both must succeed** to pickpocket successfully

**DC Calculation**:
- If monster has skill listed: DC = 10 + skill bonus
- If monster doesn't have skill: DC = raw Wisdom score (NOT modifier)

**Rewards**:
- **75% XP** (same as parlay success)
- **Individual treasure** from most powerful monster (CR-based rarity)

**Risk**:
- Either check fails → Detected → Combat begins

---

## Implementation Files

### Backend Services

#### `src/talekeeper/services/parlay_system.py`
**New Methods**:
- `_determine_if_evil(alignment)` - Handle "any" alignment (1/3 chance evil)
- `get_parlay_skills_for_encounter(monsters)` - Intelligence/alignment-based skill selection
- `_get_intelligent_non_evil_skills()` - 2 CHA + 1 INT/WIS
- `_get_intelligent_evil_skills()` - Deception + Intimidation + random
- `_get_simple_non_evil_skills()` - Nature + Survival + limited
- `_get_simple_evil_skills()` - Nature + Survival + very limited
- `_get_monster_insight(monster)` - Skill or raw WIS
- `_get_monster_perception(monster)` - Skill or raw WIS
- `execute_pickpocket_attempt()` - Dual check system
- `_generate_individual_treasure()` - CR-based loot
- `_award_pickpocket_xp()` - 75% XP award
- `_add_treasure_to_inventory()` - Add item to character

**Modified Methods**:
- `create_parlay_challenge()` - Now uses enhanced skill selection, stores disadvantage mode

#### `src/talekeeper/services/skill_challenge_manager.py`
**Modified Methods**:
- `attempt_skill()` - Now supports disadvantage via AdvantageSystem

**New Methods**:
- `_get_session_disadvantage_mode()` - Read metadata for disadvantage

**Modified Dataclass**:
- `SkillAttemptResult` - Added `roll_breakdown` field

### UI Components

#### `src/talekeeper/ui/encounter_pane/encounter_panel.py`
**New Methods**:
- `_handle_exploration_action(action)` - Route Influence button
- `_attempt_parlay()` - Main parlay flow
- `_show_parlay_skill_challenge(session, xp_reward)` - Display skill widget
- `_on_parlay_completed(outcome, reward_text, xp_reward)` - Handle success/failure
- `_on_parlay_refused(refuse_cost)` - Handle refusal
- `_check_pickpocket_opportunity()` - Check for parlay/stealth pickpocket
- `_on_stealth_success()` - Add pickpocket check after stealth
- `_restore_parlay_monsters_for_combat()` - Restore encounter on failure

**New Properties**:
- `_parlay_monsters` - Stores monsters after successful parlay
- `_stealth_monsters` - Stores monsters after successful stealth

#### `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`
**Modified Methods**:
- `display_attempt_result()` - Show disadvantage rolls in log

#### `src/talekeeper/ui/action_cards/action_panel.py`
**New Methods**:
- `_check_for_pickpocket_card()` - Create pickpocket action card
- `_execute_pickpocket()` - Execute dual skill checks, handle results

---

## Database Changes

### New Table: `skill_challenge_metadata`
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

**Purpose**: Store disadvantage mode ('none', 'first', 'all') for parlay challenges

---

## Example Flows

### Flow 1: Diplomatic Parlay with Centaur

```
[ENCOUNTER] Generated: 1x Centaur (CR 2, XP 450)
[Player presses Influence button]

[PARLAY] Type: Diplomatic Negotiation
[PARLAY] Target: Centaur
[PARLAY] INT: 9, Alignment: Neutral Good
[PARLAY] Skills: Persuasion, Performance, Insight
[PARLAY] Potential reward: 225 XP (50% of strongest)

[Skill Challenge Widget appears]
[Player attempts Persuasion] SUCCESS (1/3)
[Player attempts Performance] SUCCESS (2/3)
[Player attempts Insight] SUCCESS (3/3)

[PARLAY SUCCESS] Peaceful resolution - gain 225 XP without combat
[XP] Diplomatic success! Gained 225 XP through peaceful negotiation.
[PICKPOCKET] You notice an opportunity during the negotiation...
[PICKPOCKET] Check your action cards for 'Pickpocket' ability
```

### Flow 2: Dangerous Parlay with Mind Flayer (Evil)

```
[ENCOUNTER] Generated: 1x Mind Flayer (CR 7, XP 2,900)
[Player presses Influence button]

[PARLAY] Type: Dangerous Negotiation
[PARLAY] Target: Mind Flayer
[PARLAY] INT: 19, Alignment: Lawful Evil
[PARLAY] Skills: Deception, Intimidation, Thieves' Tools
[PARLAY] WARNING: First skill check at DISADVANTAGE
[PARLAY] Potential reward: 1,450 XP (50% of strongest)

[Skill Challenge Widget appears]
WARNING: Your first skill check will be made with DISADVANTAGE

[Player attempts Deception]
[DISADVANTAGE] Rolling Deception with disadvantage
[ROLLS] 15, 8 -> taking 8
[ROLL] Deception: 8 + 3 CHA + 2 prof = 13 vs DC 15
FAILURE (0/3, 1/3)

[Player attempts Intimidation] SUCCESS (1/3, 1/3)
[Player attempts Thieves' Tools] SUCCESS (2/3, 1/3)
[Player attempts Deception again] SUCCESS (3/3, 1/3)

[PARLAY SUCCESS] Successfully negotiated with dangerous creature!
```

### Flow 3: Pickpocket After Stealth

```
[ENCOUNTER] Generated: 1x Goblin (CR 1/4, XP 50)
[Player presses Hide button]

[STEALTH] Stealth check: d20(18) +5 DEX +2 prof = 25 vs DC 15
[STEALTH SUCCESS] You remain undetected
[HIDDEN] You can make a surprise attack or flee.
[PICKPOCKET] While hidden, you notice an opportunity...
[PICKPOCKET] You can attempt to pickpocket during negotiation

[Pickpocket action card appears]

[Player clicks Pickpocket]
[PICKPOCKET] Deception: d20(14) +3 CHA +2 prof = 19 vs Insight DC 8
[PICKPOCKET] Deception Total: 19 - SUCCESS
[PICKPOCKET] Sleight of Hand: d20(16) +5 DEX +2 prof = 23 vs Perception DC 8
[PICKPOCKET] Sleight of Hand Total: 23 - SUCCESS

[PICKPOCKET SUCCESS] Successfully pickpocketed Goblin!
[XP] Gained 37 XP (75% of parlay reward)
[TREASURE] Found: Leather Armor (Common)
```

### Flow 4: Failed Pickpocket → Combat

```
[PICKPOCKET] Deception: d20(14) +3 CHA +2 prof = 19 vs Insight DC 12
[PICKPOCKET] Deception Total: 19 - SUCCESS
[PICKPOCKET] Sleight of Hand: d20(5) +4 DEX +2 prof = 11 vs Perception DC 20
[PICKPOCKET] Sleight of Hand Total: 11 - FAILURE

[PICKPOCKET FAILED] Sleight of Hand failed - creature noticed you
[COMBAT] You were caught! The creatures attack!
[COMBAT] Rolling initiative...
```

---

## Testing Checklist

### Parlay System
- [ ] Intelligent Non-Evil (Centaur, INT 9) → 2 CHA + 1 INT/WIS, no disadvantage
- [ ] Intelligent Evil (Mind Flayer, INT 19) → Deception + Intimidation + random, first disadvantage
- [ ] Simple Non-Evil (Dire Wolf, INT 3) → Nature + Survival + random, no disadvantage
- [ ] Simple Evil (Zombie, INT 3) → Nature + Survival + random, all disadvantage
- [ ] "Any" alignment → 1/3 chance evil (test multiple encounters)
- [ ] INT threshold: 3 vs 4 boundary
- [ ] Disadvantage displays correctly in skill widget
- [ ] Success awards 50% XP
- [ ] Failure starts combat
- [ ] Refuse works correctly

### Pickpocket System
- [ ] Only available with both Deception + Sleight of Hand proficiency
- [ ] Available after successful parlay
- [ ] Available after successful stealth
- [ ] NOT available otherwise
- [ ] Both checks must succeed
- [ ] Deception fail → Pickpocket fail → Combat
- [ ] Sleight fail → Pickpocket fail → Combat
- [ ] Success awards 75% XP
- [ ] Success generates treasure based on CR
- [ ] Treasure added to inventory
- [ ] Monster Perception skill read correctly from JSON
- [ ] Monster without Perception uses raw WIS
- [ ] Monster without Insight uses raw WIS
- [ ] Action card disappears after use

### Integration
- [ ] Influence button triggers parlay
- [ ] Parlay type logged correctly
- [ ] Monster stats logged correctly
- [ ] Skill challenge widget appears
- [ ] XP and inventory displays update
- [ ] Failed pickpocket restores monsters for combat
- [ ] Stealth pickpocket failure removes hidden status

---

## Design Rationale

### Why Intelligence/Alignment-Based Parlay?

**Thematic Depth**: Different creatures require different approaches
- Intelligent creatures: Social skills
- Beasts: Nature/animal handling
- Evil creatures: Harder, riskier (disadvantage)

**Character Build Variety**:
- CHA builds excel with intelligent non-evil
- WIS builds handle beasts better
- All builds struggle with evil (but can try)

### Why Dual Skill Checks for Pickpocket?

**Thematic Appropriateness**:
- Deception = Social distraction
- Sleight of Hand = Physical theft
- Both required = More realistic

**Balance**:
- Harder than single check (as it should be)
- Rewards skilled characters (need both proficiencies)
- Risk matches reward (75% XP + treasure vs combat)

### Why Use Raw Wisdom (Not Modifier)?

**Game Balance**:
- WIS 8 → DC 8 (easier for low-WIS creatures)
- WIS 15 → DC 15 (harder for high-WIS creatures)
- Creates realistic difficulty range (5-20)

**Simplicity**:
- No calculation needed
- Directly from monster stat block
- Clear DC progression

---

## Implementation Timeline

### Week 1: Parlay Enhancement
- Day 1-2: Add intelligence/alignment logic to ParlaySystem
- Day 3-4: Integrate with skill challenge manager (disadvantage)
- Day 5: Testing all 4 parlay categories

### Week 2: UI Integration
- Day 1-2: Wire Influence button to parlay
- Day 3-4: Update skill widget for disadvantage display
- Day 5: Testing parlay flow end-to-end

### Week 3: Pickpocket System
- Day 1-2: Add dual skill check logic to ParlaySystem
- Day 3: Create pickpocket action card
- Day 4: Integrate with stealth system
- Day 5: Testing pickpocket flows

### Week 4: Polish & Testing
- Day 1-2: Database migration
- Day 3-4: Comprehensive testing
- Day 5: Bug fixes and edge cases

**Total: 4 weeks**

---

## Success Metrics

### Functional
- ✅ All 4 parlay categories work correctly
- ✅ Disadvantage applied correctly (first/all)
- ✅ Pickpocket available in correct contexts
- ✅ Dual checks both required
- ✅ XP awards correct (50% parlay, 75% pickpocket)
- ✅ Treasure generation works
- ✅ Combat triggers on failure

### User Experience
- ✅ Clear monster info logging
- ✅ Disadvantage warnings visible
- ✅ Action card shows accurate DCs
- ✅ Smooth transitions between states
- ✅ Inventory/XP displays update

### Code Quality
- ✅ Uses existing AdvantageSystem
- ✅ Leverages existing LootDropService
- ✅ Minimal database changes
- ✅ No code duplication
- ✅ Clear error handling

---

## Future Enhancements

### Post-MVP Features
1. **Bribery System**: Offer gold to avoid combat
2. **Intimidation Option**: Threaten creatures to flee
3. **Reputation System**: Past parlay success affects future attempts
4. **Group Pickpocket**: Multiple targets
5. **Improved Treasure**: Specific monster-themed loot tables
6. **Parlay Dialogue Trees**: More complex negotiation
7. **Achievement Tracking**: "Pacifist" runs, pickpocket master

---

## Summary

This system adds **meaningful tactical variety** to encounters:

- **4 distinct parlay types** based on monster intelligence/alignment
- **Disadvantage mechanics** make evil creatures risky but possible
- **Dual skill checks** for pickpocket reward skilled characters
- **Multiple entry points** (parlay OR stealth) for pickpocket
- **Balanced rewards** (50% XP parlay, 75% XP + treasure pickpocket)

**Key Benefit**: Players have **real choices** in how to approach encounters, with each choice having distinct risks, rewards, and skill requirements.
