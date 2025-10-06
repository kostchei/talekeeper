# Spell Self-Targeting Implementation

## Overview
Buff spells (Divine Favor, Bless, Mage Armor, Shield of Faith, etc.) can now be cast without requiring an enemy target. When no target is selected, these spells automatically apply to the player character.

## Implementation Details

### 1. Database Enhancement
Added `is_buff` column to the `spells` table to explicitly mark buff/support spells:

```sql
ALTER TABLE spells ADD COLUMN is_buff BOOLEAN DEFAULT FALSE;
```

**19 spells marked as buffs:**
- **Cantrips (3):** Guidance, Resistance, Spare the Dying
- **Level 1 (14):** Bless, Cure Wounds, Divine Favor, Expeditious Retreat, False Life, Healing Word, Heroism, Jump, Longstrider, Mage Armor, Protection from Evil and Good, Sanctuary, Shield, Shield of Faith
- **Level 3 (2):** Water Breathing, Water Walk

### 2. Code Changes

#### `_is_self_targeting_spell()` ([action_panel.py:4648-4678](src/talekeeper/ui/action_cards/action_panel.py#L4648))
Detection logic with three-tier approach:
1. **Database Check:** If `spell_data['is_buff'] == True`, immediately return `True`
2. **Offensive Detection:** Check for attack rolls or saving throws (returns `False`)
3. **Keyword Fallback:** Check for buff keywords (gain, bonus, advantage, AC, healing, etc.) or touch/self range

#### `_handle_spell_attack()` ([action_panel.py:5098-5123](src/talekeeper/ui/action_cards/action_panel.py#L5098))
Three targeting scenarios:
1. **No target + buff spell:** Routes to `_handle_spell_utility()`
2. **No target + attack spell:** Shows warning
3. **Enemy targeted + buff spell:** Shows warning and redirects to self

#### `_handle_spell_utility()` ([action_panel.py:5320-5338](src/talekeeper/ui/action_cards/action_panel.py#L5320))
Enhanced with:
- Formatted buff effect descriptions for 11+ common spells
- Concentration indicators
- Duration information

### 3. Spell Effect Descriptions

The system provides detailed descriptions for:
- Divine Favor (+1d4 radiant damage)
- Bless (+1d4 to attacks/saves)
- Mage Armor (AC = 13 + Dex)
- Shield of Faith (+2 AC)
- Protection from Evil and Good (full protection suite)
- Shield (+5 AC for 1 round)
- Longstrider (+10 ft speed)
- Jump (triple jump distance)
- Expeditious Retreat (Dash as bonus action)
- False Life (temporary HP)
- Heroism (immune to frightened + temp HP)

## Usage Examples

### Before
```
Player casts Divine Favor without selecting target
Result: "Divine Favor cast but no target selected"
```

### After
```
Player casts Divine Favor without selecting target
Result:
  "Galahad casts Divine Favor on self"
  "  +1d4 radiant damage to weapon attacks"
  "  Duration: 1 minute (concentration)"
  "  Requires concentration"
```

### Safety Check
```
Player has enemy selected and tries to cast Bless
Result:
  "Cannot cast Bless on enemies! Casting on self instead."
  "Galahad casts Bless on self"
  "  +1d4 to attack rolls and saving throws"
  "  Duration: 1 minute (concentration)"
```

## Testing

Test file: [test_spell_self_targeting.py](../test/test_spell_self_targeting.py)

**Test Results:**
- ✅ Divine Favor: self-targeting = True
- ✅ Bless: self-targeting = True
- ✅ Mage Armor: self-targeting = True
- ✅ Shield of Faith: self-targeting = True
- ✅ Protection from Evil and Good: self-targeting = True
- ✅ Fire Bolt: self-targeting = False
- ✅ Sacred Flame: self-targeting = False
- ✅ Cure Wounds: self-targeting = True

All 8 tests passing.

## Database Cleanup

**Removed:** Outdated `data/database/` folder
**Active Database:** `talekeeper.db` in root directory
- Contains full spellcasting system
- 22 active characters
- All recent updates

## Future Enhancements

1. **Actual Buff Application:** Currently shows effects but doesn't apply mechanical bonuses (would require character state tracking)
2. **Concentration Management:** Integrate with existing `character_concentration` table
3. **Duration Tracking:** Track buff durations during combat
4. **Stacking Rules:** Prevent incompatible buffs from stacking
5. **Visual Indicators:** Show active buffs on character sheet

## Related Systems

- **Concentration System:** `src/talekeeper/services/concentration_system.py`
- **Condition Manager:** `src/talekeeper/services/condition_manager.py`
- **Spellcasting Service:** `src/talekeeper/services/spellcasting_service.py`
- **Spell Registry:** `src/talekeeper/services/spell_registry.py`
