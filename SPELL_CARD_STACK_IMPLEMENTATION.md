# Spell Card Stack System - Implementation Complete

## What It Is

A **stackable spell card** system where each spell level gets its own deck of cards that you can flip through by clicking on the card.

## Visual Layout

```
┌─────────────────────┐
│    Lv 1 3/3 (1/2)  │  ← Header: Level, slots, position in stack
├─────────────────────┤
│   Divine Favor      │  ← Current spell name (bold)
├─────────────────────┤
│ Self                │
│ 1d4 radiant per     │  ← Spell effect description
│ strike              │
├─────────────────────┤
│      [Cast]         │  ← Cast button (auto-targets self if range=self)
└─────────────────────┘
```

## How It Works

### 1. Card Organization
- **Separate stacks** for each (level, casting time) combination
- **Bonus action spells** → Bonus tab
  - Lv 1 stack: Divine Favor, Shield of Faith
- **Action spells** → Action tab
  - Lv 1 stack: Heroism, Protection from Evil and Good
- **Reaction spells** → Reaction tab

### 2. Flipping Through Cards
- **Click anywhere on the card** (except Cast button) to cycle to next spell
- **Counter shows** your position: `Lv 1 3/3 (1/2)` = "Spell 1 of 2"
- **Name changes** to show current spell
- **Description updates** to show current spell effect

### 3. Casting
- **Click "Cast" button** on the card
- **Self-targeting spells** (Divine Favor, Shield of Faith) cast immediately
- **Ranged spells** show "select target..." message
- **Slot consumed** automatically
- **Card updates** to show `Lv 1 2/3` after casting

### 4. Slot Tracking
- Header shows `Lv 1 3/3` = "3 slots available out of 3 total"
- Updates in real-time when spells are cast
- When slots = 0, Cast button is disabled
- Cantrips show `Cantrips` (no slot tracking)

## Example: Galahad's Level 1 Spells

### Bonus Tab
```
┌─────────────────────┐
│   Lv 1 3/3 (1/2)   │
├─────────────────────┤
│  Divine Favor       │
├─────────────────────┤
│ Self                │
│ 1d4 radiant per     │
│ strike              │
├─────────────────────┤
│      [Cast]         │
└─────────────────────┘

[Click card body to flip]

┌─────────────────────┐
│   Lv 1 3/3 (2/2)   │
├─────────────────────┤
│ Shield of Faith     │
├─────────────────────┤
│ +2 AC (60 ft)       │
├─────────────────────┤
│      [Cast]         │
└─────────────────────┘
```

### Action Tab
```
┌─────────────────────┐
│   Lv 1 3/3 (1/2)   │
├─────────────────────┤
│     Heroism         │
├─────────────────────┤
│ Immune Frightened   │
│ Touch               │
├─────────────────────┤
│      [Cast]         │
└─────────────────────┘

[Click to flip]

┌─────────────────────┐
│   Lv 1 3/3 (2/2)   │
├─────────────────────┤
│ Protection from     │
│ Evil and Good       │
├─────────────────────┤
│ Touch               │
├─────────────────────┤
│      [Cast]         │
└─────────────────────┘
```

## Technical Details

### Files Modified
1. `spell_card_stack.py` - NEW widget for stackable cards
2. `action_panel.py` - Updated to create SpellCardStack instead of ActionCard
3. `spell_preparation_dialog.py` - Dialog for preparing spells after long rest

### Key Features
- ✅ No Unicode characters (uses "Lv" not "⭐")
- ✅ Click to cycle through spells
- ✅ Shows position in stack (1/2, 2/2)
- ✅ Separate stacks per action type
- ✅ Real-time slot consumption tracking
- ✅ Auto-cast for self-targeting spells
- ✅ 2024 D&D rules compliant

### Spell Preparation
- Take a long rest → Dialog opens
- Select which spells to prepare (Cha mod + level/2 for Paladins)
- Oath spells always prepared (don't count toward limit)
- Cards refresh automatically after preparation

## Testing

Load the Paladin "Galahad" character and:
1. Check **Bonus** tab - should see Lv 1 3/3 card
2. **Click the card** - it flips to Shield of Faith
3. **Click again** - cycles back to Divine Favor
4. **Click Cast** - casts the current spell, slot goes to 2/3
5. Take a **long rest** - preparation dialog appears
6. **Prepare different spells** - cards refresh
