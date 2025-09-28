# Spellcaster Combat Flow Design
*How spellcasters use spells during combat in TaleKeeper*

## Current Infrastructure

### Existing Systems (Already Implemented)
1. **Action Card System** - Cards displayed at bottom of screen
2. **Action Economy Tracking** - Tracks action/bonus action/reaction per turn
3. **Spell Action Types** - `SPELL_ATTACK`, `SPELL_UTILITY`, `SPELL_REACTION` defined
4. **Spell Card Creation** - `_create_spell_action_cards()` method exists
5. **Spell Casting Hook** - `_cast_spell()` method called when spell card clicked
6. **Spellcasting Service** - Backend service for spell logic exists

### Current Combat Flow (Non-Spellcasters)
```
1. Player Turn Starts
   ↓
2. Action Cards Displayed (Attack, Second Wind, etc.)
   ↓
3. Player Clicks Action Card
   ↓
4. Action Triggered (attack roll, damage, etc.)
   ↓
5. Action Economy Updated (action consumed)
   ↓
6. Combat Log Updated
   ↓
7. Enemy Turn / Next Round
```

## Spellcaster Combat Flow

### Phase 1: Spell Preparation (Before Combat)

**For Prepared Casters (Cleric, Paladin, Wizard)**:
```
Character Sheet → Spell Management Tab
   ↓
View All Known Spells
   ↓
Select Spells to Prepare (up to Int/Wis/Cha mod + level)
   ↓
Confirm Preparation
   ↓
Prepared Spells Available in Combat
```

**For Known Casters (Warlock)**:
```
All Known Spells Always Available
(No preparation step needed)
```

### Phase 2: Combat Starts

**Action Panel Population**:
```python
def on_combat_start(character_id):
    # Clear old cards
    clear_action_cards()

    # Create weapon attack cards (if applicable)
    create_weapon_cards()

    # Create class feature cards (Second Wind, Rage, etc.)
    create_feature_cards()

    # CREATE SPELL CARDS FOR PREPARED/KNOWN SPELLS
    create_spell_cards()

    # Refresh display
    refresh_action_panel()
```

**Spell Card Display**:
- Each prepared/known spell gets its own action card
- Card shows: Icon, Spell Name (Level), Brief Description
- Card availability based on spell slots remaining
- Grouped by spell level or alphabetically

### Phase 3: Player Turn - Selecting a Spell

**UI Flow**:
```
Player's Turn Starts
   ↓
Action Panel Shows Available Actions:
   - [Attack with Longsword]
   - [Sacred Flame] ✨ (cantrip - always available)
   - [Cure Wounds (Lvl 1)] ❤️ (available - 3 slots remaining)
   - [Bless (Lvl 1)] ⚔️🛡️ (available - 3 slots remaining)
   - [Guiding Bolt (Lvl 1)] 💫 (available - 3 slots remaining)
   - [Second Wind] (available - 1 use remaining)
   ↓
Player Hovers Over Spell Card
   ↓
Tooltip Shows Full Details:
   "Cure Wounds (Level 1)
    Heal 1d8 + 3 hit points
    Range: Touch
    Action

    Available Slots: ●●●○○ (3 remaining)"
   ↓
Player Clicks [Cure Wounds] Card
```

### Phase 4: Spell Level Selection (Leveled Spells Only)

**For Level 1+ Spells with Higher Slots Available**:
```
Player Clicks [Cure Wounds (Lvl 1)]
   ↓
MODAL DIALOG APPEARS:
   ┌─────────────────────────────┐
   │  Cast Cure Wounds           │
   │                             │
   │  Select Spell Slot Level:   │
   │  ○ Level 1 (●●●○○) - 1d8+3  │
   │  ○ Level 2 (●●○○○) - 2d8+3  │
   │  ○ Level 3 (●○○○○) - 3d8+3  │
   │                             │
   │  [Cancel]  [Cast Spell]     │
   └─────────────────────────────┘
   ↓
Player Selects Level 2
   ↓
Clicks [Cast Spell]
```

**For Cantrips**:
```
No spell level selection needed
Proceeds directly to targeting
```

### Phase 5: Target Selection

**Different Targeting Types**:

#### A. Self-Target Spells (Mage Armor, Shield, False Life)
```
No targeting UI needed
Spell immediately cast on self
Skip to Phase 6
```

#### B. Single-Target Spells (Cure Wounds, Guiding Bolt, Fire Bolt)
```
Spell Level Selected
   ↓
UI PROMPT: "Select Target for Cure Wounds"
   ↓
OPTIONS DISPLAYED:
   [Self] [Ally 1] [Ally 2] ... [Enemy 1] [Enemy 2] ...
   ↓
Player Clicks [Ally 1]
   ↓
Target Confirmed
```

**Current UI Limitation**: Only "target monster" exists
**Solution**: Show target selector:
- For healing/buffs: Show allies + self
- For attacks: Show enemies
- Highlight valid targets
- Gray out invalid targets

#### C. Multi-Target Spells (Bless, Magic Missile)
```
Spell Level Selected (Bless Lvl 1 = 3 targets)
   ↓
UI PROMPT: "Select 3 Targets for Bless"
   ↓
Player Clicks [Self] → Selected (1/3)
Player Clicks [Ally 1] → Selected (2/3)
Player Clicks [Enemy 1] → Error: "Must target ally"
Player Clicks [Ally 2] → Selected (3/3)
   ↓
[Confirm] Button Appears
   ↓
Player Clicks [Confirm]
```

#### D. Area-of-Effect Spells (Burning Hands, Thunderwave)
```
Spell Level Selected
   ↓
UI PROMPT: "Burning Hands affects all creatures in 15-foot cone"
   ↓
DISPLAY: All enemies in encounter automatically targeted
   ↓
[Cast on All Enemies] [Cancel]
   ↓
Player Confirms
```

**Future Enhancement**: Grid-based positioning for tactical AoE
**Current Solution**: Auto-target all enemies in encounter

### Phase 6: Spell Resolution

**A. Attack Roll Spells (Fire Bolt, Guiding Bolt, Inflict Wounds)**:
```
Target Confirmed
   ↓
Roll Spell Attack:
   d20 + Spell Attack Bonus vs Target AC
   ↓
HIT:
   Roll Damage Dice
   Apply Damage to Target
   Log: "Fire Bolt hits Goblin for 7 fire damage"
   ↓
MISS:
   Log: "Fire Bolt misses Goblin"
   ↓
Consume Spell Slot (even on miss)
Update Action Economy (action used)
Refresh Spell Cards (show reduced slots)
```

**B. Saving Throw Spells (Sacred Flame, Burning Hands, Bane)**:
```
Target(s) Confirmed
   ↓
Calculate Spell Save DC: 8 + Proficiency + Spell Modifier
   ↓
For Each Target:
   Roll Saving Throw: d20 + Save Bonus
   ↓
   SAVE FAILED:
      Apply Full Effect (damage/condition)
      Log: "Goblin fails save, takes 8 radiant damage"
   ↓
   SAVE SUCCEEDED:
      Apply Partial Effect (half damage) or No Effect
      Log: "Goblin saves, takes 4 fire damage"
   ↓
Consume Spell Slot
Update Action Economy
Refresh Spell Cards
```

**C. Auto-Effect Spells (Magic Missile, Healing)**:
```
Target(s) Confirmed
   ↓
NO ROLL NEEDED
   ↓
Apply Effect Directly:
   Healing: Restore HP
   Magic Missile: Auto-hit damage
   Buff: Apply condition
   ↓
Log Results
   ↓
Consume Spell Slot
Update Action Economy
Refresh Spell Cards
```

### Phase 7: Special Spell Mechanics

#### Concentration Spells (Bless, Shield of Faith, Hex)
```
Spell Cast Successfully
   ↓
CHECK: Is caster already concentrating?
   ↓
   YES: End previous concentration spell
        Remove previous effects
        Log: "Concentration on Bless ends"
   ↓
   NO: Continue
   ↓
START NEW CONCENTRATION:
   Apply spell effects
   Mark caster as concentrating on this spell
   Add concentration icon to character sheet
   ↓
DURING SUBSEQUENT TURNS:
   If caster takes damage:
      Roll Constitution Save (DC = 10 or half damage, whichever higher)
      ↓
      FAIL: Concentration breaks, spell ends
      PASS: Concentration maintained
```

**UI Indicator**:
```
Character Sheet Shows:
   🧠 Concentrating on: Bless (8 rounds remaining)

Action Panel Shows:
   [Cure Wounds] ✓ Available
   [Bless] ❌ Unavailable (already concentrating)
```

#### Reaction Spells (Shield, Hellish Rebuke)

**Current System**: Reactions not fully implemented
**Needed System**:
```
Enemy Attacks Player
   ↓
BEFORE DAMAGE RESOLUTION:
   ↓
   Check: Does player have Shield spell prepared?
   Check: Does player have reaction available?
   Check: Does player have spell slot?
   ↓
   YES TO ALL:
      ↓
      POPUP PROMPT:
         ┌─────────────────────────────┐
         │  Enemy Attack Roll: 18      │
         │  Your AC: 16                │
         │                             │
         │  Use Shield spell?          │
         │  +5 AC until your next turn │
         │  Uses reaction & 1st level  │
         │  spell slot                 │
         │                             │
         │  New AC would be: 21        │
         │  This would block the attack│
         │                             │
         │  [Yes] [No]                 │
         └─────────────────────────────┘
      ↓
      Player Chooses [Yes]
      ↓
      Cast Shield
      Recalculate attack vs new AC
      Consume reaction
      Consume spell slot
      Log: "Shield spell cast! AC +5. Attack misses!"
```

#### Bonus Action Spells (Healing Word, Divine Favor, Shield of Faith)
```
Player's Turn
   ↓
Player Clicks [Healing Word] Card
   ↓
CHECK: Bonus Action Available?
   ↓
   NO: Error message "Bonus action already used"
   ↓
   YES: Proceed with spell
      ↓
      Select target, cast spell
      ↓
      Consume BONUS ACTION (not action)
      ↓
      Action Still Available!
      ↓
      Player can now [Attack with Longsword]
```

**UI Indicator**:
```
Action Economy Display:
   Action: ✓ Available
   Bonus: ❌ Used (Healing Word)
   Reaction: ✓ Available
```

### Phase 8: End of Turn Cleanup

```
Player Ends Turn
   ↓
Update Concentration Duration:
   Bless: 9 rounds → 8 rounds remaining
   ↓
Remove Expired Effects:
   Shield spell (until start of turn) → Removed
   AC returns to normal
   ↓
Reset Action Economy:
   Action: ✓ Available (for next turn)
   Bonus Action: ✓ Available
   Reaction: ✓ Available
   ↓
Enemy Turn Begins
```

## UI Components Needed

### 1. Spell Slot Tracker (Character Sheet)
```
┌─────────────────────────────────┐
│  Spell Slots                    │
│                                 │
│  Level 1: ●●●○○ (3/5)          │
│  Level 2: ●●○○○ (2/5)          │
│  Level 3: ●○○○○ (1/5)          │
│                                 │
│  [Short Rest] [Long Rest]       │
└─────────────────────────────────┘
```

### 2. Spell Level Selection Dialog
```
┌─────────────────────────────────┐
│  Cast Cure Wounds               │
│                                 │
│  Select Spell Slot Level:       │
│  ○ Level 1 (●●●○○) - 1d8+3     │
│  ○ Level 2 (●●○○○) - 2d8+3     │
│  ○ Level 3 (●○○○○) - 3d8+3     │
│                                 │
│  [Cancel]  [Cast]               │
└─────────────────────────────────┘
```

### 3. Target Selection UI
```
┌─────────────────────────────────┐
│  Select Target for Fire Bolt    │
│                                 │
│  Enemies:                       │
│  [Goblin 1] HP: 7/7            │
│  [Goblin 2] HP: 4/7  ← Damaged │
│                                 │
│  [Cancel]                       │
└─────────────────────────────────┘
```

### 4. Concentration Indicator
```
Character Sheet Top:
   🧠 Concentrating on Bless (8 rounds)

Hover Shows:
   "Concentration: Bless
    Duration: 8 rounds remaining
    Targets: Self, Ally 1, Ally 2
    Effect: +1d4 to attacks and saves

    Concentration breaks if:
    - You cast another concentration spell
    - You take damage and fail Con save
    - You are incapacitated"
```

### 5. Reaction Prompt
```
OVERLAY POPUP (appears mid-combat):
┌─────────────────────────────────┐
│  ⚠️  REACTION AVAILABLE         │
│                                 │
│  Goblin attacks you!            │
│  Attack Roll: 18 vs AC 16       │
│                                 │
│  Use Shield spell?              │
│  +5 AC (new AC: 21)             │
│  Costs: Reaction + 1st level   │
│         spell slot              │
│                                 │
│  ⏱️ Decide quickly!             │
│                                 │
│  [USE SHIELD] [LET IT HIT]     │
└─────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Basic Spell Casting (Week 1-2)
- ✓ Spell card creation (already done)
- ✓ Spell casting hook (already done)
- ⚠️ **Spell slot tracking** (database + UI)
- ⚠️ **Cantrip implementation** (damage scaling)
- ⚠️ **Simple single-target spells** (Fire Bolt, Cure Wounds)
- ⚠️ **Combat log integration**

### Phase 2: Spell Levels & Slots (Week 2-3)
- ⚠️ **Spell level selection dialog**
- ⚠️ **Slot consumption on cast**
- ⚠️ **Scaling calculations** (XdY based on slot level)
- ⚠️ **Slot recovery** (short rest, long rest)

### Phase 3: Target Selection (Week 3-4)
- ⚠️ **Self-targeting** (auto-apply)
- ⚠️ **Single-target selector** (ally/enemy list)
- ⚠️ **Multi-target selector** (select X creatures)
- ⚠️ **AoE auto-targeting** (all enemies in encounter)

### Phase 4: Concentration (Week 4-5)
- ⚠️ **Concentration tracking system**
- ⚠️ **Concentration UI indicator**
- ⚠️ **Concentration breaking** (damage, incapacitated)
- ⚠️ **Con saves on damage**

### Phase 5: Reactions (Week 5-6)
- ⚠️ **Reaction prompt system**
- ⚠️ **Trigger detection** (on attack, on damage, etc.)
- ⚠️ **Reaction spell casting**
- ⚠️ **Retroactive effect application** (Shield blocks attack)

### Phase 6: Bonus Actions (Week 6)
- ⚠️ **Bonus action tracking**
- ⚠️ **Bonus action spells** (Healing Word, etc.)
- ⚠️ **Action economy display**

### Phase 7: Polish & Testing (Week 7-8)
- Testing all spell types
- Edge case handling
- UI polish
- Performance optimization

## Key Design Decisions

### Decision 1: When to Show Spell Cards?
**CHOSEN**: Show all prepared/known spell cards at all times
- **Pros**: Player can see all options, plan ahead
- **Cons**: Many cards on screen
- **Alternative Rejected**: "Cast Spell" button → submenu
  - Requires extra clicks
  - Hides options from player

### Decision 2: How to Handle Spell Levels?
**CHOSEN**: Popup dialog when casting leveled spell with multiple slot levels available
- **Pros**: Clear, explicit choice with preview
- **Cons**: Extra click for higher-level casts
- **Alternative Rejected**: Separate card for each spell level
  - Too many cards
  - Cluttered UI

### Decision 3: Target Selection UI?
**CHOSEN**: Simple list-based selection
- **Pros**: Works with current combat system (no positioning)
- **Cons**: Not as tactical as grid-based
- **Future Enhancement**: Grid-based targeting when positioning implemented

### Decision 4: Reaction Spell Timing?
**CHOSEN**: Interrupt combat flow with popup prompt
- **Pros**: Clear decision point, shows all info
- **Cons**: Breaks flow slightly
- **Alternative Rejected**: Auto-cast reactions
  - Removes player agency
  - Wrong for tactical game

### Decision 5: Concentration Tracking?
**CHOSEN**: Visual indicator on character sheet + prevent casting second concentration spell
- **Pros**: Clear, prevents mistakes
- **Cons**: Requires extra UI element
- **Alternative Rejected**: No visual indicator
  - Players would forget
  - Lead to errors

## Summary

Spellcasters use spells in combat through this flow:

1. **Spell cards appear** in action panel (like weapon attacks)
2. **Player clicks spell card** on their turn
3. **Spell level selection** (if higher slots available)
4. **Target selection** (based on spell type)
5. **Spell resolves** (attack roll/save/auto-effect)
6. **Effects applied**, slot consumed, action economy updated
7. **Special mechanics** handled (concentration, reactions, bonus actions)

The system leverages existing action card infrastructure while adding:
- Spell slot tracking
- Level selection dialog
- Target selection UI
- Concentration system
- Reaction prompts

This provides a smooth, intuitive experience that feels like playing D&D at a table, where you announce your spell, choose targets, roll dice, and apply effects.