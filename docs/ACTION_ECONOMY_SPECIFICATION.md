# D&D 5e Action Economy Implementation

## Overview

This document specifies the implementation of D&D 5e action economy rules in TaleKeeper. The action economy system enforces the core rule that each creature can only take **one action, one bonus action, and one reaction per round**.

## Core Rules

### Action Types and Limits

1. **Action** (1 per turn)
   - Attack, Cast a Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use an Object
   - Resets at the start of each creature's turn

2. **Bonus Action** (1 per turn, if available)
   - Only available if a class feature, spell, or other ability specifically grants a bonus action
   - Examples: Fighter's Second Wind, Rogue's Cunning Action, certain spells
   - Resets at the start of each creature's turn

3. **Reaction** (1 per round, not per turn)
   - Available to interrupt other creatures' actions
   - Examples: Opportunity attacks, Counterspell, Shield spell
   - Resets at the start of the creature's next turn (not every turn in initiative)

4. **Free Actions/Object Interactions** (unlimited, but DM discretion)
   - Drawing/sheathing weapons, opening doors, simple object interactions
   - No formal limit in D&D 5e

5. **Movement** (speed pool per turn)
   - Each creature has a movement speed (typically 30 feet)
   - Can be split before and after actions
   - Resets each turn

### Special Cases

#### Action Surge (Fighter Feature)
- Grants one additional **Action** on the turn it's used
- Does not grant additional bonus actions or reactions
- Once per short/long rest

#### Multiple Attacks
- Extra Attack feature allows multiple attacks within a single **Action**
- Still only consumes one action slot per turn

## Implementation Architecture

### Data Models

#### `ActionEconomyState` (per combatant)
```python
@dataclass
class ActionEconomyState:
    combatant_id: str
    current_round: int
    action_available: bool          # Resets each turn
    bonus_action_available: bool    # Resets each turn  
    reaction_available: bool        # Resets at start of creature's turn
    movement_used: int              # Out of movement_speed, resets each turn
    actions_taken_this_turn: List[Dict]
```

#### `CombatActionEconomy` (per combat)
```python
@dataclass 
class CombatActionEconomy:
    current_round: int
    current_turn: int
    turn_order: List[str]           # Initiative order
    combatant_states: Dict[str, ActionEconomyState]
```

### Database Integration

#### Combat Session Enhancement
- `CombatSession` now includes `action_economy: CombatActionEconomy`
- All combat actions are validated against action economy before execution
- Failed actions are logged with reasons

#### Persistence
- Action economy state persists with combat sessions in IndexedDB
- Turn and round progression saved automatically
- Action history maintained for audit trail

### User Interface Integration

#### Action Panel (`action_cards/action_panel.py`)
- Real-time action economy status display: `"R3 | Action: ✗ | Bonus: ✓ | Reaction: ✓ | Move: 25ft"`
- Action cards disabled when action type not available
- Tooltip updates showing economy restrictions
- Visual feedback for failed action attempts

#### Action Card States
- **Available**: Normal appearance, clickable
- **Used**: Grayed out, not clickable, tooltip shows "Action used this turn"
- **Unavailable**: Dimmed, shows specific reason in tooltip

## Workflow

### Combat Initialization
1. **Roll Initiative**: Establish turn order
2. **Create Combat Session**: Initialize with action economy tracking
3. **Add Combatants**: Create `ActionEconomyState` for each participant
4. **Start First Turn**: Reset action economy for first combatant

### Turn Progression
1. **Start Turn**: Reset action and bonus action, movement pool
2. **Action Attempts**: Validate against action economy before execution
3. **Action Execution**: Mark action type as used, log to combat history
4. **End Turn**: Move to next combatant in initiative order
5. **Round Transition**: Reset reactions when creature's turn comes up again

### Action Validation Flow
```
User clicks action → Check action economy → 
  ✓ Available: Execute action, update economy, log, refresh UI
  ✗ Used: Show feedback, log attempt, do not execute
```

## Code Integration Points

### GameEngine Integration
- `update_character_hp()`: Uses action economy to validate healing actions
- `start_combat()`: Initializes action economy tracking
- `next_turn()`: Advances action economy state

### UI Component Updates
- **EncounterPanel**: Integrates with action economy for monster actions
- **ActionPanel**: Shows economy status, validates player actions
- **LogPanel**: Records action economy events and restrictions

### Database Schema
```json
{
  "combat_sessions": {
    "session_id": {
      "action_economy": {
        "current_round": 3,
        "current_turn": 1,
        "turn_order": ["character_id", "monster_1", "monster_2"],
        "combatant_states": {
          "character_id": {
            "action_available": false,
            "bonus_action_available": true,
            "reaction_available": false,
            "movement_used": 20,
            "actions_taken_this_turn": [...]
          }
        }
      }
    }
  }
}
```

## Benefits

### Game Rules Compliance
- Enforces official D&D 5e action economy rules
- Prevents common player mistakes (multiple actions per turn)
- Maintains game balance and tactical decision-making

### Player Experience
- Clear visual feedback on available actions
- Prevents confusion about what can be done each turn
- Educational tool for learning D&D 5e combat rules

### Data Integrity
- Complete audit trail of all combat actions
- Database consistency for action usage
- Proper state management across save/load cycles

## Future Enhancements

### Advanced Features
- **Action Surge Tracking**: Automatic detection of Fighter levels
- **Spell Slot Integration**: Track spell slot usage with bonus action spells
- **Concentration Tracking**: Link with spell concentration mechanics
- **Condition Effects**: Handle paralyzed, stunned conditions that affect actions

### UI Improvements
- **Turn Timer**: Optional turn timers for pacing
- **Action Queue**: Allow pre-planning actions for faster combat
- **Undo System**: Limited undo for accidental action usage

## Testing Scenarios

### Basic Action Economy
1. Start combat, verify all actions available
2. Use main action (Attack), verify action disabled
3. Use bonus action (Second Wind), verify bonus action disabled
4. End turn, verify actions reset for next turn

### Reaction Testing
1. Use reaction (Opportunity Attack) on Round 1
2. Verify reaction unavailable for rest of Round 1
3. Start creature's next turn, verify reaction resets

### Multi-Round Combat
1. Combat lasting 3+ rounds
2. Verify proper reset behavior each round
3. Verify action history preserved across rounds

### Edge Cases
1. Action Surge usage (Fighter only)
2. No bonus actions available (non-caster classes)
3. Combat ending mid-round
4. Save/load during active combat

This specification ensures TaleKeeper correctly implements D&D 5e action economy, providing an authentic and balanced combat experience while maintaining data integrity and user experience standards.