# REAL IMPLEMENTATION PLAN - Multiple Attacks Per Turn

## THE ROOT PROBLEM
`_trigger_monster_counter_attacks()` is called immediately after EVERY attack, ending the player's turn. We need to batch multiple attacks before calling this function.

## SOLUTION: Turn State System

### Step 1: Add Turn State Tracking
Add these variables to `ActionPanel.__init__()`:
```python
self.player_turn_active = False
self.pending_attacks = []  # List of attacks to execute in sequence
self.turn_ended_callback = None  # Function to call when turn actually ends
```

### Step 2: Modify Attack Execution Chain
Instead of immediately calling `_trigger_monster_counter_attacks()`, we:
1. Check if there are potential follow-up attacks (off-hand, Nick)
2. If yes: present options and stay in turn
3. If no: end turn and call monsters

### Step 3: Key Functions to Modify

#### `_execute_attack_without_initiative()` (line ~1197)
- Remove direct call to `_trigger_monster_counter_attacks()`
- Instead call `_check_for_followup_attacks()`

#### NEW: `_check_for_followup_attacks()`
```python
def _check_for_followup_attacks(self, last_attack_type, context, encounter_panel):
    followup_options = []
    
    # Check for off-hand attack if main-hand was light weapon
    if last_attack_type == ActionType.ATTACK_MAIN_HAND:
        if self._can_make_offhand_attack(context):
            followup_options.append('offhand')
    
    # Check for Nick mastery
    if self._can_use_nick_mastery(context):
        followup_options.append('nick')
    
    if followup_options:
        self._present_followup_options(followup_options, context, encounter_panel)
    else:
        self._end_player_turn(encounter_panel)
```

#### NEW: `_can_make_offhand_attack(context)`
```python
def _can_make_offhand_attack(self, context):
    # Check if main-hand weapon is light
    weapon_props = context.get('weapon_properties', [])
    is_light = 'light' in [prop.lower() for prop in weapon_props]
    
    # Check if off-hand weapon exists and is light
    off_hand_weapon = self.equipped_weapons.get('off_hand')
    if not off_hand_weapon or not is_light:
        return False
        
    # Check if already used bonus action this turn
    return not self.used_bonus_action_this_turn
```

#### NEW: `_can_use_nick_mastery(context)`
```python  
def _can_use_nick_mastery(self, context):
    # Check if weapon has Nick mastery
    weapon_masteries = context.get('weapon_masteries', [])
    if 'Nick' not in weapon_masteries:
        return False
        
    # Check if already used bonus action
    return not self.used_bonus_action_this_turn
```

#### NEW: `_present_followup_options(options, context, encounter_panel)`
- Temporarily highlight available follow-up action cards
- Set flag to prevent monster attacks until turn completed
- When option selected OR timeout: call `_end_player_turn()`

#### NEW: `_end_player_turn(encounter_panel)`
```python
def _end_player_turn(self, encounter_panel):
    # Reset turn state
    self.player_turn_active = False
    self.used_bonus_action_this_turn = False
    
    # NOW call monster attacks
    self._trigger_monster_counter_attacks(encounter_panel)
```

## IMPLEMENTATION ORDER

### Phase 1: Basic Two-Weapon Fighting
1. Add turn state variables
2. Modify `_execute_attack_without_initiative()` to not immediately call monsters
3. Add `_can_make_offhand_attack()` logic
4. Add simple prompt: "Make off-hand attack?" button
5. Test: Main-hand → Off-hand → Monsters (once)

### Phase 2: Add Nick Mastery  
1. Add `_can_use_nick_mastery()` logic
2. Integrate with follow-up system
3. Test: Nick weapon → Nick bonus attack → Monsters

### Phase 3: Combined System
1. Handle both off-hand AND Nick options
2. Add proper UI for multiple options
3. Test all combinations

## KEY FILES TO MODIFY
- `test/action_cards/action_panel.py` - Main logic
- No new files needed, just modify existing functions

## TESTING APPROACH
Create simple test script that:
1. Equips two light weapons (Scimitar + Shortsword)
2. Starts combat
3. Makes main-hand attack
4. Verifies off-hand option appears
5. Verifies monsters don't attack until after off-hand