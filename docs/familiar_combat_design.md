# Familiar Combat System Design

## Overview
Implement Pact of the Chain familiar (quasit) combat participation in TaleKeeper.

## Design Points

### 1. Data Model Extension
- [ ] Add `companion_of` field to `Combatant` dataclass (links familiar to owner)
- [ ] Add `companion_type` field to `Combatant` dataclass (familiar, beast_companion, steed)
- [ ] Add `is_companion` boolean flag
- [ ] Familiar shares initiative with owner (inserted after owner in turn order)

### 2. Database Schema
- [x] Check if active companions table exists - **NO** existing companion tracking
- [x] Check if character_combat_state can track familiars - Can use character_features.mechanics JSON
- [ ] Add familiar_type field to character_features mechanics JSON
- [ ] Add familiar_hp and familiar_status to track persistent familiar state
- **DECISION:** Store familiar info in character_features.mechanics JSON to avoid new tables

### 3. Monster Stat Blocks
- [x] Verify quasit exists in monsters table - **EXISTS** in data/monsters/monsters_extracted.json
- [x] Verify imp exists in monsters table - **EXISTS** in data/monsters/monsters_extracted.json
- [x] Verify pseudodragon exists in monsters table - **EXISTS** in data/monsters/monsters_extracted.json
- [x] Verify sprite exists in monsters table - **EXISTS** in data/monsters/monsters_extracted.json
- [x] All Pact of Chain familiar options present in JSON data

### 4. Warlock Feature Integration
- [x] Check existing Pact of Chain implementation - Exists in warlock_service.py:89-100
- [x] Current implementation grants "Pact of the Chain" feature but no familiar selection
- [ ] Add select_familiar() method to warlock_service.py
- [ ] Update mechanics JSON: {"source": "warlock_pact", "pact_type": "chain", "familiar_type": "quasit", "familiar_hp": 25, "familiar_alive": true}
- [ ] Add get_active_familiar() method to retrieve familiar data for combat

### 5. Combat Manager Integration
- [ ] Modify `add_player_combatant()` to check for familiar feature
- [ ] Spawn familiar as separate Combatant when detected
- [ ] Insert familiar into initiative order after owner
- [ ] Handle familiar turn in combat flow
- [ ] Add familiar death/dismissal handling

### 6. Action Economy
- [ ] Familiar has independent action/bonus action/reaction
- [ ] Owner can command familiar with bonus action (2024 rules)
- [ ] Familiar can act independently on its turn
- [ ] Track familiar action usage per turn

### 7. UI Integration
- [x] **Familiar Summoning Dialog** - Shows after short rest if Pact of Chain warlock without familiar
- [x] **Selection Interface** - Lists all 4 familiar options with stats and descriptions
- [ ] Display familiar in combatant list (familiar already appears in combat automatically)
- [ ] Show familiar HP/status in UI
- [ ] Allow commanding familiar during player turn
- [ ] Show familiar actions in attack UI

## Implementation Findings

### Existing Infrastructure (Reusable)
1. **Monster Data**: All 4 familiar types exist in data/monsters/monsters_extracted.json
   - Quasit: AC 13, HP 25, DEX +3, has Rend attack, Invisibility, Scare ability
   - Imp, Pseudodragon, Sprite: Also present with full stat blocks

2. **Character Features System**: Already exists and loads mechanics JSON
   - Located in character_features table
   - Mechanics field stores JSON: `{"source": "warlock_pact", "pact_type": "chain"}`
   - Can extend to include: `{"familiar_type": "quasit", "familiar_hp": 25, "familiar_alive": true}`

3. **Warlock Service**: Pact of Chain already grants "Pact of the Chain" feature
   - File: warlock_service.py:89-100
   - Just needs familiar selection method added

4. **Combat Manager**: Already has add_monster_combatant() method
   - Can reuse to spawn familiar as Combatant
   - Combatant dataclass at line 51 needs companion fields added

### New Code Needed (Minimal)
1. Extend Combatant dataclass with 3 fields: companion_of, companion_type, is_companion
2. Add select_familiar() method to WarlockService
3. Add get_active_familiar() helper method to WarlockService
4. Modify add_player_combatant() to check for familiar and spawn it
5. Load familiar monster data from JSON and pass to add_monster_combatant()

## Implementation Status
- Created: 2025-11-10
- Status: **IMPLEMENTED** ✓

## Implementation Summary

### Completed Components

1. **Combatant Dataclass Extension** ([combat_manager.py:92-95](d:/Code/TaleKeeper/src/talekeeper/core/combat_manager.py#L92-L95))
   - Added `companion_of`, `companion_type`, and `is_companion` fields
   - Allows familiars to be tracked as companions in combat

2. **Warlock Service Methods** ([warlock_service.py:102-173](d:/Code/TaleKeeper/src/talekeeper/services/warlock_service.py#L102-L173))
   - `select_familiar(character_id, familiar_type)` - Select quasit/imp/pseudodragon/sprite
   - `get_active_familiar(character_id)` - Retrieve active familiar data
   - `update_familiar_hp(character_id, new_hp)` - Persist familiar HP to database
   - Updated `_grant_find_familiar()` to initialize mechanics JSON with familiar fields

3. **Monster Data Loader** ([combat_manager.py:248-261](d:/Code/TaleKeeper/src/talekeeper/core/combat_manager.py#L248-L261))
   - `_load_monster_from_json(monster_name)` - Loads familiar stat blocks from JSON

4. **Familiar Spawning** ([combat_manager.py:184-220](d:/Code/TaleKeeper/src/talekeeper/core/combat_manager.py#L184-L220))
   - `_spawn_familiar_if_present()` - Checks character features and spawns familiar
   - Integrated into `add_player_combatant()` workflow
   - Sets companion flags on familiar Combatant

5. **Initiative Sharing** ([combat_manager.py:374-385](d:/Code/TaleKeeper/src/talekeeper/core/combat_manager.py#L374-L385))
   - Companions skip initiative roll and share owner's initiative
   - Companions inserted immediately after owner in turn order
   - Logs familiar initiative sharing

6. **HP Persistence** ([combat_manager.py:263-277](d:/Code/TaleKeeper/src/talekeeper/core/combat_manager.py#L263-L277))
   - `_update_familiar_hp_if_needed()` - Updates database when familiar takes damage or dies
   - Integrated into damage application in `execute_player_attack()`
   - Handles both normal damage and Fire's Burn bonus damage

7. **UI Integration** ([action_panel.py:8801-8941](d:/Code/TaleKeeper/src/talekeeper/ui/action_cards/action_panel.py#L8801-L8941))
   - `_check_familiar_summoning()` - Checks for Pact of Chain after short rest
   - `_show_familiar_selection_dialog()` - Displays familiar selection UI
   - `_summon_familiar()` - Calls warlock_service to summon selected familiar
   - Integrated into short rest workflow after abilities restore

### How It Works

1. **Pact Selection**: Warlock selects Pact of Chain at level 3 (grants "Pact of the Chain" feature)
2. **First Summon**: After taking a short rest, UI automatically shows familiar selection dialog
3. **Choose Familiar**: Player selects from Quasit, Imp, Pseudodragon, or Sprite
4. **Storage**: Familiar type and HP stored in character_features.mechanics JSON
5. **Combat Entry**: When warlock enters combat, familiar automatically spawns as Combatant
6. **Turn Order**: Familiar shares initiative with warlock, acts right after them
7. **Combat**: Familiar can attack like any monster, has own action economy
8. **HP Tracking**: Damage persists to database, familiar dies at 0 HP
9. **Resummon**: On next short rest, if familiar is dead, dialog shows again to resummon at full HP

### Testing Steps

**Setup:**
1. Create a warlock character and level to 3
2. Select Pact of Chain as pact boon

**UI Testing:**
1. Take a short rest - familiar selection dialog should appear
2. Verify all 4 familiar options are shown with stats
3. Select a familiar (quasit recommended)
4. Verify confirmation message appears in log
5. Take another short rest - dialog should NOT appear (already have familiar)

**Combat Testing:**
1. Start combat and verify familiar appears in initiative order
2. Verify familiar is right after warlock in turn order
3. Verify familiar shares same initiative roll as warlock
4. Attack familiar and verify HP decreases
5. Check database: familiar HP should persist

**Death & Resummon:**
1. Kill familiar (reduce to 0 HP)
2. Exit combat
3. Take short rest - dialog should appear again
4. Select same or different familiar
5. Verify familiar returns at full HP
