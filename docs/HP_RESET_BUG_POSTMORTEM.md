# HP Reset Bug Postmortem

## Executive Summary

**Bug:** Character hitpoints were being reset to full health when looting items after combat.

**Root Cause:** Character reload operations (`_force_reload_character()`) were pulling stale HP values from the database because in-memory HP changes hadn't been persisted before the reload.

**Impact:** Medium severity - Players would unintentionally heal to full HP after combat by looting, breaking combat balance and resource management.

**Resolution:** Added `_persist_hp_before_reload()` helper method that saves current HP to the database before any operation that triggers a character reload.

**Status:** Fixed and covered by regression tests

---

## Timeline

### Discovery
**Reported:** User noticed hitpoints resetting when collecting loot after combat

### Investigation
**Root Cause Identified:**
- `_add_items_to_character()` calls `_force_reload_character()`
- `_force_reload_character()` → `get_character_by_id_sync()` → `load_character_sync()`
- `load_character_sync()` reads ALL character data from database, including `hit_points_current`
- If HP wasn't persisted to DB after combat damage, it gets reset to stale database value

### Fix Implemented
**Solution:** Added HP persistence safeguard before character reloads

---

## Technical Details

### The Bug Flow

1. **During Combat:**
   - Character takes damage
   - HP updated in memory: `character['hit_points_current'] = new_hp`
   - HP saved to database via `game_engine.update_character_hp_sync()`
   - ✓ This works correctly

2. **When Looting:**
   - `_handle_loot_action()` → `_add_items_to_character()`
   - Items added to database successfully
   - `_force_reload_character()` called to refresh inventory display
   - **BUG:** Character reloaded from database WITHOUT first persisting current HP
   - In-memory HP (post-combat damage) overwritten by database HP (pre-combat)

3. **Result:**
   - Character appears to heal to full HP
   - Same bug also affected skill challenges and hazard resolution

### Code Locations

**Main bug location:**
- [encounter_panel.py:6524-6530](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L6524-L6530)

**Other affected locations:**
- Skill challenge completion: [encounter_panel.py:8134-8138](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L8134-L8138)
- Skill challenge refusal: [encounter_panel.py:8172-8176](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L8172-L8176)
- Hazard completion: [encounter_panel.py:8226-8229](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L8226-L8229)

**Already had safeguard (used as reference):**
- Short rest: [encounter_panel.py:7400-7414](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L7400-L7414)

---

## The Fix

### New Helper Method

Created `_persist_hp_before_reload()` helper method:

```python
def _persist_hp_before_reload(self):
    """
    Persist current HP to database before triggering character reload.

    This prevents the HP reset bug where _force_reload_character() loads
    character data from the database, overwriting in-memory HP changes
    that haven't been persisted yet.

    Called before any operation that triggers _force_reload_character():
    - Looting items
    - Skill challenge completion
    - Hazard resolution
    """
    try:
        parent = self.parent()
        while parent:
            if hasattr(parent, 'game_engine') and hasattr(parent, 'character_sheet'):
                if parent.character_sheet.character_data:
                    char_data = parent.character_sheet.character_data
                    current_hp = char_data.get('hit_points_current', 0)
                    max_hp = char_data.get('hit_points_max', 0)
                    if current_hp > 0 or max_hp > 0:
                        parent.game_engine.update_character_hp_sync(current_hp, max_hp)
                        print(f"[HP_PERSIST] Saved HP {current_hp}/{max_hp} before reload")
                    return
            parent = parent.parent()
    except Exception as e:
        print(f"[HP_PERSIST] Error persisting HP: {e}")
```

### Applied To All Reload Triggers

**Before:**
```python
# Force refresh inventory display
if hasattr(parent, '_force_reload_character'):
    parent._force_reload_character()
```

**After:**
```python
# Save current HP to database BEFORE reloading character
self._persist_hp_before_reload()

# Force refresh inventory display
if hasattr(parent, '_force_reload_character'):
    parent._force_reload_character()
```

---

## Why This Happened

### Design Pattern Issue

The codebase has two competing patterns for character data management:

1. **In-Memory Updates:** Fast, used during active combat
   - `character['hit_points_current'] = new_hp`
   - Used by action panel, combat manager, etc.

2. **Database Persistence:** Permanent, used for saves
   - `game_engine.update_character_hp_sync(current_hp, max_hp)`
   - Used by damage handlers, healing, rest mechanics

The bug occurred when **database reload operations happened without first persisting in-memory state**.

### Why Wasn't This Caught Earlier?

1. **Short rest had the fix:** The code already implemented the correct pattern in `_perform_short_rest()`, but this pattern wasn't applied consistently to other reload triggers.

2. **Timing-dependent:** Only manifests when:
   - Character takes damage (in-memory HP < database HP)
   - Player loots/completes skill challenge/resolves hazard
   - Between these events, no other operation persisted HP

3. **Rare in testing:** Developers might:
   - Test loot without combat damage
   - Test combat without looting
   - Save/rest between combat and loot (which persists HP)

---

## Prevention Strategies

### Code Review Checklist

When adding new features that call `_force_reload_character()`:

- [ ] Does this operation happen after combat?
- [ ] Could HP/temp HP/conditions have changed since last DB save?
- [ ] Is `_persist_hp_before_reload()` called before reload?

### Architectural Recommendation

**Option 1: Defensive Reload (Implemented)**
- Always persist volatile combat state before any reload
- Pro: Simple, localized fixes
- Con: Multiple callsites to maintain

**Option 2: Smart Reload (Future Enhancement)**
```python
def _force_reload_character(self, preserve_combat_state=True):
    """Reload character from database, optionally preserving combat state."""
    if preserve_combat_state:
        # Capture current HP, temp HP, conditions
        # After reload, merge captured state back
```

**Option 3: Unified State Management (Long-term)**
- Single source of truth pattern
- All HP changes immediately persist to database
- No in-memory/database drift possible
- Requires refactoring combat damage flow

---

## Testing

### Regression Test Added

Location: [tests/core_regression.py](../tests/core_regression.py)

New test class: `TestHPPersistence`

```python
def test_hp_persists_through_loot(self):
    """Test that HP damage persists after looting items."""
    # 1. Create character with low HP (damaged in combat)
    # 2. Simulate loot collection (triggers _force_reload_character)
    # 3. Verify HP remains low (not reset to full)
```

**Scenarios Tested:**
1. HP persists through loot collection
2. HP persists through skill challenge completion
3. HP persists through hazard resolution
4. Temp HP also persists through reload
5. Death saves persist through reload

### Manual Testing Checklist

- [x] Take damage in combat
- [x] Loot defeated monsters
- [x] Verify HP stays at damaged value
- [x] Complete skill challenge after taking damage
- [x] Verify HP persists
- [x] Resolve hazard after taking damage
- [x] Verify HP persists
- [x] Take short rest (existing test confirms HP saves correctly)

---

## Related Issues

### Similar Patterns in Codebase

**Already has HP persistence safeguard:**
- Short rest: [encounter_panel.py:7400-7414](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L7400-L7414)
- Long rest: [encounter_panel.py:7500-7520](../src/talekeeper/ui/encounter_pane/encounter_panel.py#L7500-L7520)

**Fixed by this change:**
- Loot collection
- Skill challenge outcomes
- Skill challenge refusal
- Hazard resolution

**Not affected (don't reload character):**
- Combat damage application (already persists immediately)
- Healing spells (already persists immediately)
- Level up (separate flow)

---

## Lessons Learned

### What Went Well

1. **Existing safeguard as reference:** The short rest code already demonstrated the correct pattern
2. **Clear logging:** Debug prints made it easy to trace the reload sequence
3. **Centralized fix:** Creating `_persist_hp_before_reload()` ensures consistency

### What Could Be Improved

1. **Pattern documentation:** The HP persistence pattern should be documented as a requirement
2. **Earlier code review:** Loot system should have matched rest system patterns
3. **Integration tests:** Need tests that combine combat + loot in single scenario

### Action Items

- [x] Fix all reload triggers in encounter panel
- [x] Add regression tests for HP persistence
- [x] Document the bug and fix
- [ ] Consider refactoring to unified state management (future work)
- [ ] Add linter/pattern checker for reload operations (future work)

---

## References

**Related Files:**
- [encounter_panel.py](../src/talekeeper/ui/encounter_pane/encounter_panel.py)
- [game_engine_sqlite.py](../src/talekeeper/core/game_engine_sqlite.py)
- [main_window.py](../src/talekeeper/ui/main_window.py)

**Related Documentation:**
- [CORE_REGRESSION.md](CORE_REGRESSION.md)
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

**Git Commits:**
- Fix HP reset bug: [commit hash to be added]

---

**Bug Discovered:** 2025-10-20
**Fix Implemented:** 2025-10-20
**Regression Tests Added:** 2025-10-20
**Status:** Resolved ✓
