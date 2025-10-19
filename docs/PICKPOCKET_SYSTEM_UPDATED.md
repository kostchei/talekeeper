# Pickpocket System - Updated Design

## Overview

Updated pickpocket mechanics based on feedback:

### Key Changes from Original Design
1. ✅ **75% XP reward** (not gold formula)
2. ✅ **Individual treasure generation** from most powerful monster
3. ✅ **Dual skill check**: Deception vs Insight AND Sleight of Hand vs Perception (both must succeed)
4. ✅ Uses monster's actual Insight/Perception values from database

---

## Pickpocket Mechanics

### Requirements
- Character must have **both** Deception and Sleight of Hand proficiency
- Available **only** after:
  - **Successful parlay** (peaceful resolution), OR
  - **Successfully hidden** via stealth (undetected)

### Skill Checks (Both Must Succeed)
1. **Deception vs Monster Insight** - Distract the creature
2. **Sleight of Hand vs Monster Perception** - Steal without being noticed

**Both checks must succeed** to pickpocket successfully.

### Rewards
- **75% of parlay XP** (same as parlay success XP)
- **Individual treasure** from most powerful monster (based on CR rarity)

### Risk
If either check fails → Detected → Combat begins

---

## Implementation

### File: `src/talekeeper/services/parlay_system.py`

**UPDATE** existing methods with corrected mechanics:

```python
def execute_pickpocket_attempt(
    self,
    character_id: str,
    monsters: List[Dict],
    character_data: Dict
) -> Dict:
    """
    Execute pickpocket attempt with dual skill checks.

    Mechanics:
    1. Deception check vs Monster Insight (distract)
    2. Sleight of Hand check vs Monster Perception (steal)
    3. BOTH must succeed

    Rewards:
    - 75% XP (same as parlay success)
    - Individual treasure from most powerful monster

    Args:
        character_id: Character ID
        monsters: List of monsters
        character_data: Character stat dict

    Returns:
        Dict with success, xp_gained, treasure, checks, message
    """
    from talekeeper.services.proficiency_bonus import get_proficiency_bonus
    from talekeeper.services.advantage_system import AdvantageSystem, AdvantageState, RollType

    if not monsters:
        return {
            'success': False,
            'message': 'No monsters to pickpocket',
            'xp_gained': 0,
            'treasure': None
        }

    # Get most powerful monster (target)
    target_monster = max(monsters, key=lambda m: m.get('experience_points', 0))

    # Get monster's Insight and Perception
    monster_insight = self._get_monster_insight(target_monster)
    monster_perception = self._get_monster_perception(target_monster)

    # Get character stats
    cha_mod = (character_data.get('charisma', 10) - 10) // 2
    dex_mod = (character_data.get('dexterity', 10) - 10) // 2
    prof_bonus = get_proficiency_bonus(character_data.get('level', 1))

    # Context for advantage/disadvantage
    context = {'character_id': character_id}

    # ===================
    # CHECK 1: Deception vs Insight
    # ===================

    deception_context = {**context, 'skill_name': 'Deception'}
    deception_adv_sources = AdvantageSystem.get_common_advantage_sources(
        RollType.SKILL_CHECK, deception_context
    )
    deception_dis_sources = AdvantageSystem.get_common_disadvantage_sources(
        RollType.SKILL_CHECK, deception_context
    )
    deception_state = AdvantageSystem.calculate_advantage_state(
        deception_adv_sources, deception_dis_sources
    )

    deception_modifier = cha_mod + prof_bonus
    deception_total, deception_breakdown = AdvantageSystem.roll_d20_with_advantage(
        deception_state, deception_modifier
    )

    deception_success = deception_total >= monster_insight

    # ===================
    # CHECK 2: Sleight of Hand vs Perception
    # ===================

    sleight_context = {**context, 'skill_name': 'Sleight of Hand'}
    sleight_adv_sources = AdvantageSystem.get_common_advantage_sources(
        RollType.SKILL_CHECK, sleight_context
    )
    sleight_dis_sources = AdvantageSystem.get_common_disadvantage_sources(
        RollType.SKILL_CHECK, sleight_context
    )
    sleight_state = AdvantageSystem.calculate_advantage_state(
        sleight_adv_sources, sleight_dis_sources
    )

    sleight_modifier = dex_mod + prof_bonus
    sleight_total, sleight_breakdown = AdvantageSystem.roll_d20_with_advantage(
        sleight_state, sleight_modifier
    )

    sleight_success = sleight_total >= monster_perception

    # ===================
    # RESULT: Both must succeed
    # ===================

    overall_success = deception_success and sleight_success

    if overall_success:
        # Calculate XP reward (75% of parlay XP)
        parlay_xp = self.calculate_parlay_xp_reward(monsters)
        pickpocket_xp = int(parlay_xp * 0.75)

        # Generate individual treasure
        treasure = self._generate_individual_treasure(character_id, character_data, target_monster)

        # Award XP
        self._award_pickpocket_xp(character_id, pickpocket_xp)

        # Award treasure (add to inventory)
        if treasure:
            self._add_treasure_to_inventory(character_id, treasure)

        return {
            'success': True,
            'xp_gained': pickpocket_xp,
            'treasure': treasure,
            'deception_check': {
                'total': deception_total,
                'dc': monster_insight,
                'success': True,
                'breakdown': deception_breakdown
            },
            'sleight_check': {
                'total': sleight_total,
                'dc': monster_perception,
                'success': True,
                'breakdown': sleight_breakdown
            },
            'message': f"Successfully pickpocketed {target_monster['name']}!"
        }
    else:
        # Determine which check failed
        if not deception_success and not sleight_success:
            failure_reason = "Both Deception and Sleight of Hand failed"
        elif not deception_success:
            failure_reason = "Deception check failed - creature wasn't distracted"
        else:
            failure_reason = "Sleight of Hand failed - creature noticed you"

        return {
            'success': False,
            'xp_gained': 0,
            'treasure': None,
            'deception_check': {
                'total': deception_total,
                'dc': monster_insight,
                'success': deception_success,
                'breakdown': deception_breakdown
            },
            'sleight_check': {
                'total': sleight_total,
                'dc': monster_perception,
                'success': sleight_success,
                'breakdown': sleight_breakdown
            },
            'message': f"Pickpocket failed! {failure_reason}"
        }

def _get_monster_insight(self, monster: Dict) -> int:
    """
    Get monster's Insight value.

    If monster has Insight skill listed, use that.
    Otherwise, use raw Wisdom score (not modifier).

    Args:
        monster: Monster dict

    Returns:
        Insight DC
    """
    # Check if monster has explicit Insight skill
    skills = monster.get('skills')
    if skills:
        # Skills can be JSON string or dict
        if isinstance(skills, str):
            import json
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                skills = {}

        if isinstance(skills, dict):
            insight_value = skills.get('insight')
            if insight_value:
                # Skills stored as "+X" format, convert to DC
                if isinstance(insight_value, str):
                    try:
                        # "+5" becomes DC 15 (10 + 5)
                        return 10 + int(insight_value.replace('+', '').strip())
                    except ValueError:
                        pass

    # Fallback: Use raw Wisdom score (not modifier)
    wisdom = monster.get('wisdom', 10)
    return wisdom

def _get_monster_perception(self, monster: Dict) -> int:
    """
    Get monster's Perception value.

    If monster has Perception skill listed, use that.
    Otherwise, use raw Wisdom score (not modifier).

    Args:
        monster: Monster dict

    Returns:
        Perception DC
    """
    # Check if monster has explicit Perception skill
    skills = monster.get('skills')
    if skills:
        # Skills can be JSON string or dict
        if isinstance(skills, str):
            import json
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                skills = {}

        if isinstance(skills, dict):
            perception_value = skills.get('perception')
            if perception_value:
                # Skills stored as "+X" format, convert to DC
                if isinstance(perception_value, str):
                    try:
                        # "+5" becomes DC 15 (10 + 5)
                        return 10 + int(perception_value.replace('+', '').strip())
                    except ValueError:
                        pass

    # Fallback: Use raw Wisdom score (not modifier)
    wisdom = monster.get('wisdom', 10)
    return wisdom

def _generate_individual_treasure(
    self,
    character_id: str,
    character_data: Dict,
    monster: Dict
) -> Optional[Dict]:
    """
    Generate individual treasure from monster.

    Uses LootDropService with CR-based rarity.

    Args:
        character_id: Character ID
        character_data: Character stats
        monster: Target monster

    Returns:
        Treasure item dict or None
    """
    from talekeeper.services.loot_drop_service import LootDropService

    # Get monster CR
    cr = monster.get('challenge_rating', 0)

    # Convert CR to numeric
    if isinstance(cr, str):
        if '/' in cr:
            # Fractional CR (1/4, 1/2, etc.)
            numerator, denominator = cr.split('/')
            cr_numeric = float(numerator) / float(denominator)
        else:
            cr_numeric = float(cr)
    else:
        cr_numeric = float(cr) if cr else 0

    # Get rarity from CR
    loot_service = LootDropService(self.db_path)
    rarity = loot_service.cr_to_rarity(cr_numeric)

    # Generate treasure
    treasure = loot_service.drop_loot(character_id, character_data, rarity)

    return treasure

def _award_pickpocket_xp(self, character_id: str, xp_amount: int):
    """Award XP for successful pickpocket."""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE characters
            SET experience_points = experience_points + ?
            WHERE id = ?
        ''', (xp_amount, character_id))

        conn.commit()

    except Exception as e:
        print(f"Error awarding pickpocket XP: {e}")
    finally:
        if conn:
            conn.close()

def _add_treasure_to_inventory(self, character_id: str, treasure: Dict):
    """Add treasure item to character inventory."""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        from uuid import uuid4
        item_id = str(uuid4())

        cursor.execute('''
            INSERT INTO character_inventory
            (id, character_id, item_name, item_type, quantity, is_equipped)
            VALUES (?, ?, ?, ?, 1, 0)
        ''', (
            item_id,
            character_id,
            treasure['name'],
            treasure.get('type', 'treasure')
        ))

        conn.commit()

    except Exception as e:
        print(f"Error adding treasure to inventory: {e}")
    finally:
        if conn:
            conn.close()
```

---

## Integration Points

### Pickpocket Availability Triggers

Pickpocket is available in **two scenarios**:

#### 1. After Successful Parlay
**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

Already implemented in `_on_parlay_completed()`:
```python
def _on_parlay_completed(self, outcome: str, reward_text: str, xp_reward: int):
    # ... existing code ...

    if outcome == 'success':
        # ... award XP, update display ...

        # Store monsters for pickpocket opportunity
        self._parlay_monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

        # Check for pickpocket opportunity
        self._check_pickpocket_opportunity()
```

#### 2. After Successful Stealth Hide
**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**ADD** to stealth success handler (find where Hide button succeeds):

```python
def _on_stealth_success(self):
    """
    Handle successful stealth check.

    Character is hidden - offer pickpocket if they have the skills.
    """
    # Existing stealth success code...
    # (sets player_hidden flag, shows "Flee Undetected" button, etc.)

    # Check for pickpocket opportunity while hidden
    if self.encounter_instances:
        # Store monsters for pickpocket
        self._stealth_monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

        # Check if character can pickpocket
        self._check_pickpocket_opportunity()
```

### Unified Pickpocket Check

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**UPDATE** `_check_pickpocket_opportunity()` to handle both scenarios:

```python
def _check_pickpocket_opportunity(self):
    """
    Check if character can pickpocket after successful parlay OR stealth.

    Sets flag that action panel will detect.
    """
    from talekeeper.services.parlay_system import ParlaySystem

    character_data = self._get_current_character_data()
    if not character_data:
        return

    # Check which monsters are available
    monsters = None
    context = None

    if hasattr(self, '_parlay_monsters'):
        monsters = self._parlay_monsters
        context = "parlay"
    elif hasattr(self, '_stealth_monsters'):
        monsters = self._stealth_monsters
        context = "stealth"

    if not monsters:
        return

    parlay_system = ParlaySystem('talekeeper.db')
    can_pickpocket, reason = parlay_system.can_pickpocket(character_data['id'])

    if can_pickpocket:
        if context == "parlay":
            self._log_monster_action("[PICKPOCKET] You notice an opportunity during the negotiation...")
        elif context == "stealth":
            self._log_monster_action("[PICKPOCKET] While hidden, you notice an opportunity...")

        self._log_monster_action(f"[PICKPOCKET] {reason}")
        self._log_monster_action("[PICKPOCKET] Check your action cards for 'Pickpocket' ability")

        # Signal action panel to add pickpocket card
        # (Action panel checks for _parlay_monsters or _stealth_monsters)
    else:
        # Clear stored monsters - no pickpocket opportunity
        if hasattr(self, '_parlay_monsters'):
            delattr(self, '_parlay_monsters')
        if hasattr(self, '_stealth_monsters'):
            delattr(self, '_stealth_monsters')
```

---

## Action Panel Integration

### File: `src/talekeeper/ui/action_cards/action_panel.py`

**UPDATE** pickpocket execution:

```python
def _execute_pickpocket(self):
    """Execute pickpocket attempt with dual skill checks."""
    from talekeeper.services.parlay_system import ParlaySystem

    encounter_panel = self.parent().encounter_panel

    # Get monsters from either parlay or stealth context
    monsters = None
    if hasattr(encounter_panel, '_parlay_monsters'):
        monsters = encounter_panel._parlay_monsters
    elif hasattr(encounter_panel, '_stealth_monsters'):
        monsters = encounter_panel._stealth_monsters

    if not monsters:
        self._log_action("[PICKPOCKET] No pickpocket opportunity available")
        return
    parlay_system = ParlaySystem('talekeeper.db')

    # Execute pickpocket
    result = parlay_system.execute_pickpocket_attempt(
        self.character_data['id'],
        monsters,
        self.character_data
    )

    # Log Deception check
    dec_check = result.get('deception_check', {})
    dec_breakdown = dec_check.get('breakdown', {})

    if dec_breakdown.get('type') == 'disadvantage':
        rolls = dec_breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Deception (DISADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {dec_breakdown['d20_result']} "
            f"vs Insight DC {dec_check['dc']}"
        )
    elif dec_breakdown.get('type') == 'advantage':
        rolls = dec_breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Deception (ADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {dec_breakdown['d20_result']} "
            f"vs Insight DC {dec_check['dc']}"
        )
    else:
        self._log_action(
            f"[PICKPOCKET] Deception: d20({dec_breakdown.get('d20_result', '?')}) "
            f"vs Insight DC {dec_check['dc']}"
        )

    self._log_action(
        f"[PICKPOCKET] Deception Total: {dec_check['total']} - "
        f"{'SUCCESS' if dec_check['success'] else 'FAILURE'}"
    )

    # Log Sleight of Hand check
    sleight_check = result.get('sleight_check', {})
    sleight_breakdown = sleight_check.get('breakdown', {})

    if sleight_breakdown.get('type') == 'disadvantage':
        rolls = sleight_breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand (DISADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {sleight_breakdown['d20_result']} "
            f"vs Perception DC {sleight_check['dc']}"
        )
    elif sleight_breakdown.get('type') == 'advantage':
        rolls = sleight_breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand (ADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {sleight_breakdown['d20_result']} "
            f"vs Perception DC {sleight_check['dc']}"
        )
    else:
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand: d20({sleight_breakdown.get('d20_result', '?')}) "
            f"vs Perception DC {sleight_check['dc']}"
        )

    self._log_action(
        f"[PICKPOCKET] Sleight of Hand Total: {sleight_check['total']} - "
        f"{'SUCCESS' if sleight_check['success'] else 'FAILURE'}"
    )

    # Overall result
    if result['success']:
        # Success - log rewards
        self._log_action(f"[PICKPOCKET SUCCESS] {result['message']}")
        self._log_action(f"[XP] Gained {result['xp_gained']} XP (75% of parlay reward)")

        treasure = result.get('treasure')
        if treasure:
            self._log_action(
                f"[TREASURE] Found: {treasure['name']} "
                f"({treasure.get('rarity', 'Common')})"
            )
        else:
            self._log_action("[TREASURE] No treasure found")

        # Update character display
        if hasattr(self.parent(), 'character_sheet'):
            self.parent().character_sheet.load_character(self.character_data['id'])

        # Update inventory display if exists
        if hasattr(self.parent(), 'equipment_panel'):
            self.parent().equipment_panel.refresh_inventory()

        # Clean up - remove pickpocket opportunity
        if hasattr(encounter_panel, '_parlay_monsters'):
            delattr(encounter_panel, '_parlay_monsters')
        if hasattr(encounter_panel, '_stealth_monsters'):
            delattr(encounter_panel, '_stealth_monsters')

        # Remove pickpocket card
        self._refresh_action_cards()

    else:
        # Failure - detected!
        self._log_action(f"[PICKPOCKET FAILED] {result['message']}")
        self._log_action("[COMBAT] You were caught! The creatures attack!")

        # Restore monsters and start combat
        if hasattr(encounter_panel, '_parlay_monsters'):
            encounter_panel._restore_parlay_monsters_for_combat()
        elif hasattr(encounter_panel, '_stealth_monsters'):
            # If from stealth, monsters are already there, just start combat
            # Player loses hidden status
            encounter_panel.player_hidden = False

        encounter_panel.set_encounter_mode()

        # Clean up
        if hasattr(encounter_panel, '_parlay_monsters'):
            delattr(encounter_panel, '_parlay_monsters')
        if hasattr(encounter_panel, '_stealth_monsters'):
            delattr(encounter_panel, '_stealth_monsters')

        # Remove pickpocket card
        self._refresh_action_cards()
```

---

## Action Card Description Update

**UPDATE** pickpocket card creation:

```python
def _check_for_pickpocket_card(self) -> Optional[ActionCard]:
    """
    Check if pickpocket action card should be available.

    Available after successful parlay OR successful stealth hide.
    """
    from talekeeper.services.parlay_system import ParlaySystem

    # Check if encounter panel has monsters stored
    if not hasattr(self.parent(), 'encounter_panel'):
        return None

    encounter_panel = self.parent().encounter_panel

    # Check for parlay monsters OR stealth monsters
    monsters = None
    context = None

    if hasattr(encounter_panel, '_parlay_monsters'):
        monsters = encounter_panel._parlay_monsters
        context = "parlay"
    elif hasattr(encounter_panel, '_stealth_monsters'):
        monsters = encounter_panel._stealth_monsters
        context = "stealth"

    if not monsters:
        return None

    # Check if character can pickpocket
    parlay_system = ParlaySystem('talekeeper.db')
    character_id = self.character_data['id']

    can_pickpocket, reason = parlay_system.can_pickpocket(character_id)
    if not can_pickpocket:
        return None

    # Get modifiers for display
    cha_mod = (self.character_data.get('charisma', 10) - 10) // 2
    dex_mod = (self.character_data.get('dexterity', 10) - 10) // 2
    from talekeeper.services.proficiency_bonus import get_proficiency_bonus
    prof_bonus = get_proficiency_bonus(self.character_data.get('level', 1))

    deception_bonus = cha_mod + prof_bonus
    sleight_bonus = dex_mod + prof_bonus

    deception_text = f"+{deception_bonus}" if deception_bonus >= 0 else str(deception_bonus)
    sleight_text = f"+{sleight_bonus}" if sleight_bonus >= 0 else str(sleight_bonus)

    # Get target monster info
    monsters = encounter_panel._parlay_monsters
    target = max(monsters, key=lambda m: m.get('experience_points', 0))

    monster_insight = parlay_system._get_monster_insight(target)
    monster_perception = parlay_system._get_monster_perception(target)

    # Calculate potential XP
    parlay_xp = parlay_system.calculate_parlay_xp_reward(monsters)
    pickpocket_xp = int(parlay_xp * 0.75)

    # Create description based on context
    if context == "parlay":
        context_text = f"during negotiation with {target['name']}"
    else:  # stealth
        context_text = f"while hidden from {target['name']}"

    # Create pickpocket action card
    card = ActionCard(
        name="Pickpocket",
        action_type="action",
        description=(
            f"Attempt to steal treasure {context_text}\n\n"
            f"REQUIRES BOTH CHECKS TO SUCCEED:\n"
            f"1. Deception {deception_text} vs Insight DC {monster_insight}\n"
            f"2. Sleight of Hand {sleight_text} vs Perception DC {monster_perception}\n\n"
            f"SUCCESS:\n"
            f"  - {pickpocket_xp} XP (75% of parlay reward)\n"
            f"  - Individual treasure (CR-based rarity)\n\n"
            f"FAILURE: Detected - combat begins immediately"
        ),
        icon_path=None
    )

    card.clicked.connect(lambda: self._execute_pickpocket())

    return card
```

---

## Testing Checklist

### Dual Skill Checks
- [ ] Both Deception and Sleight of Hand succeed → Pickpocket success
- [ ] Deception fails, Sleight succeeds → Pickpocket fails (detected)
- [ ] Deception succeeds, Sleight fails → Pickpocket fails (detected)
- [ ] Both fail → Pickpocket fails (detected)
- [ ] Verify advantage/disadvantage applied correctly to both checks

### Monster Stats
- [ ] Verify Perception read from monster skills JSON
- [ ] Verify Insight calculated from WIS modifier if not listed
- [ ] Test with monsters that have explicit Perception (e.g., Aarakocra +5)
- [ ] Test with monsters without explicit Perception (fallback to WIS)

### Rewards
- [ ] Verify XP = 75% of parlay XP (not 100%)
- [ ] Verify treasure generated based on monster CR
- [ ] Verify treasure added to inventory
- [ ] Verify treasure rarity matches CR (Common → Legendary)

### Integration
- [ ] Pickpocket card appears after successful parlay
- [ ] Pickpocket card shows correct DCs for target monster
- [ ] Success updates XP and inventory displays
- [ ] Failure triggers combat correctly
- [ ] Card disappears after use

---

## Example Scenarios

### Scenario 1: Pickpocket a Goblin (CR 1/4)
- **Target**: Goblin (WIS 8, no Insight/Perception skills listed)
- **Insight DC**: 8 (raw Wisdom)
- **Perception DC**: 8 (raw Wisdom)
- **Potential XP**: ~37 (75% of 50 XP)
- **Treasure Rarity**: Common

### Scenario 2: Pickpocket an Aboleth (CR 10)
- **Target**: Aboleth (WIS 15, Perception +10 skill listed)
- **Insight DC**: 15 (raw Wisdom, no Insight skill)
- **Perception DC**: 20 (10 + 10 from Perception skill)
- **Potential XP**: ~1,462 (75% of 1,950 XP)
- **Treasure Rarity**: Very Rare

### Scenario 3: Pickpocket After Stealth (Not Parlay)
- **Context**: Character successfully hid using Hide button, encounter not started
- **Pickpocket Available**: Yes (character is hidden)
- **Checks**: Same as normal (Deception vs Insight, Sleight vs Perception)
- **Failure**: Detected → Combat begins from hidden position advantage

### DC Calculation Summary

| Monster Stat | Has Skill Listed? | DC Calculation | Example |
|--------------|-------------------|----------------|---------|
| **Perception** | Yes | 10 + skill bonus | Aboleth has Perception +10 → DC 20 |
| **Perception** | No | Raw Wisdom score | Goblin WIS 8 → DC 8 |
| **Insight** | Yes | 10 + skill bonus | Rare (most don't have Insight) |
| **Insight** | No | Raw Wisdom score | Aboleth WIS 15 → DC 15 |

**Key Point**: If no skill listed, use the **raw Wisdom score**, not the modifier.

### Scenario 4: Failed Pickpocket
```
[PICKPOCKET] Deception: d20(14) vs Insight DC 12
[PICKPOCKET] Deception Total: 17 - SUCCESS
[PICKPOCKET] Sleight of Hand: d20(8) vs Perception DC 15
[PICKPOCKET] Sleight of Hand Total: 11 - FAILURE
[PICKPOCKET FAILED] Sleight of Hand failed - creature noticed you
[COMBAT] You were caught! The creatures attack!
```

---

## Summary of Changes

| Feature | Old Design | New Design |
|---------|-----------|-----------|
| **XP Reward** | 0 XP | 75% of parlay XP |
| **Gold Reward** | 1d4 per CR | None (replaced with treasure) |
| **Treasure** | None | Individual treasure (CR-based rarity) |
| **Skill Checks** | Single Sleight of Hand check | Dual checks: Deception + Sleight |
| **DC Calculation** | Fixed DC 20 | Monster's Insight + Perception |
| **Failure Risk** | Combat begins | Combat begins |

**Key Improvement**: More thematically appropriate - you distract (Deception) then steal (Sleight), with monster-specific difficulty based on their actual stats.
