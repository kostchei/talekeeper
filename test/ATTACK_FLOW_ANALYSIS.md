# ACTUAL ATTACK EXECUTION FLOW ANALYSIS

## What ACTUALLY Happens When You Click "Longsword" Attack

### Step 1: Button Click
- User clicks Longsword action card
- `ActionCard._trigger_action()` called (line ~4884)
- Emits `action_triggered` signal with `ActionType.ATTACK_MAIN_HAND`

### Step 2: Signal Routing  
- `ActionPanel._trigger_action(ActionType.ATTACK_MAIN_HAND, context)` called (line ~849)
- Checks if action is available with `_is_action_available()`
- Adds character context and weapon data to context

### Step 3: Attack Routing Decision
- Line 862: Checks if `action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]`
- Line 870: Checks if `self.target_monster_id` exists
- Line 878: Calls `_new_execute_attack(action_type, full_context)` 
- Line 881: **RETURNS** - doesn't fall through to old system

### Step 4: New Attack System
- `_new_execute_attack()` called (line 1044)
- Line 1064: Calls `_check_and_roll_initiative()` 
- Line 1070: Calls `_get_attack_count()` for Fighter Extra Attack
- Line 1072-1077: Single attack vs Multiple attacks decision

### Step 5: Single Attack Execution  
- Line 1074: Calls `_execute_attack_without_initiative()`
- This function does the actual attack roll, damage, etc.

### Step 6: Combat End Check
- After attack execution, checks if monsters are defeated
- If monsters alive: Line 1042 calls `_trigger_monster_counter_attacks()`
- **This ends the player's turn immediately after ONE attack**

## KEY INSIGHT: THE PROBLEM
- Each attack immediately triggers `_trigger_monster_counter_attacks()`
- There's no concept of "multiple attacks in one turn"
- Off-hand attacks are separate action cards that each trigger monster responses
- Nick mastery is a separate bonus action card

## FUNCTIONS INVOLVED IN ATTACK FLOW

1. `ActionCard._trigger_action()` - Button click handler
2. `ActionPanel._trigger_action()` - Signal receiver
3. `ActionPanel._new_execute_attack()` - Main attack coordinator
4. `ActionPanel._execute_attack_without_initiative()` - Actual attack execution
5. `ActionPanel._trigger_monster_counter_attacks()` - **TURN ENDER**

## CURRENT OFF-HAND ATTACK SYSTEM
- Off-hand is a completely separate ActionCard 
- Lives in BONUS action category (line ~797)
- When clicked, goes through same flow as main-hand
- Results in: Main-hand → Monsters → Off-hand → Monsters (WRONG!)

## CURRENT NICK MASTERY SYSTEM  
- Nick is a separate ActionCard in bonus actions
- Line 547: `_trigger_feature_action()` handles Nick
- Results in: Attack → Monsters → Nick → Monsters (WRONG!)