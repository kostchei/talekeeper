# Non-Combat Encounter Resolution - REVISED UI Plan

## Executive Summary

This document revises the original non-combat encounter plan to use **existing UI buttons** instead of creating a new dialog:

- **Influence** button triggers Parlay system
- **Search** button replaced with **Flee** button
- **Study** button reveals monster capabilities (already working)
- **Hide** button triggers stealth avoidance (already partially working)

## Current UI State

### Existing Buttons in Encounter Panel

```
+-----------------------------------------------+
| [Generate Encounter] dropdown menu            |
+-----------------------------------------------+
| [Influence] [Search] [Study] [Hide]          |
+-----------------------------------------------+
```

**Current Behavior:**
- **Influence**: Emits `exploration_action` signal with "influence" - NOT CONNECTED
- **Search**: Emits `exploration_action` signal with "search" - NOT CONNECTED
- **Study**: Working! Shows Nature/INT check to reveal monster info
- **Hide**: Triggers stealth check, shows "Flee Undetected" button if successful

### Study Button (Reference Implementation)

**Already Working** - shows how to integrate:
```
[14:31:45] Exploration: study
[14:31:45] [STUDY] Nature check: d20(2) +-2 INT +2 prof = 2 vs DC 10
[14:31:45] [STUDY] Failed to identify the creature..
```

Location: Line ~700 in encounter_panel.py

---

## Revised Implementation Plan

### Phase 1: Replace Search Button with Flee Button

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**Current (Line 704-706)**:
```python
self.search_btn = QPushButton("Search")
self.search_btn.clicked.connect(lambda: self.exploration_action.emit("search"))
encounter_actions_layout.addWidget(self.search_btn)
```

**Replace With**:
```python
self.flee_btn = QPushButton("Flee")
self.flee_btn.clicked.connect(self._attempt_flee_encounter)
encounter_actions_layout.addWidget(self.flee_btn)
```

**New Method**:
```python
def _attempt_flee_encounter(self):
    """Flee from encounter (no XP, no combat)."""
    if not self.encounter_instances:
        self._log_monster_action("[FLEE] No active encounter to flee from")
        return

    monsters = [inst.to_dict() for inst in self.encounter_instances.values()]
    monster_names = ', '.join([m.get('name', 'Unknown') for m in monsters[:3]])

    self._log_monster_action(f"[FLEE] You retreat from the {monster_names} without engaging")
    self._log_monster_action("[FLEE] No XP gained, no combat")

    # Clear encounter
    self._clear_monster_cards()
    self.update_scene_description("You carefully retreat, avoiding confrontation.")
```

---

### Phase 2: Connect Influence Button to Parlay System

#### Step 2.1: Enhance ParlaySystem Service

**File**: `src/talekeeper/services/parlay_system.py`

**Add Intelligence/Alignment-Based Skill Selection**:

```python
def get_parlay_skills_for_encounter(self, monsters: List[Dict]) -> Tuple[List[str], str]:
    """
    Get parlay skills based on monster intelligence and alignment.

    Returns:
        Tuple of (skills_list, disadvantage_mode)
        disadvantage_mode: 'none', 'first', 'all'
    """
    if not monsters:
        return [], 'none'

    # Use most powerful monster to determine parlay type
    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))

    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', '').lower()
    is_evil = 'evil' in alignment

    # Determine parlay category
    if intelligence >= 4:
        if not is_evil:
            # Intelligent Non-Evil: 2 CHA + 1 INT/WIS
            return self._get_intelligent_non_evil_skills(), 'none'
        else:
            # Intelligent Evil: Deception + Intimidation + 1 random
            return self._get_intelligent_evil_skills(), 'first'
    else:
        if not is_evil:
            # Simple Non-Evil: Nature + Survival + 1 limited
            return self._get_simple_non_evil_skills(), 'none'
        else:
            # Simple Evil: Nature + Survival + 1 very limited
            return self._get_simple_evil_skills(), 'all'

def _get_intelligent_non_evil_skills(self) -> List[str]:
    """2 random CHA skills + 1 random INT/WIS skill."""
    cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
    int_wis_skills = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion',
                      'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival']

    selected_cha = random.sample(cha_skills, 2)
    selected_int_wis = random.choice(int_wis_skills)

    return selected_cha + [selected_int_wis]

def _get_intelligent_evil_skills(self) -> List[str]:
    """Deception + Intimidation + 1 random skill (including tools)."""
    all_skills = [
        'Athletics', 'Acrobatics', 'Sleight of Hand', 'Stealth',
        'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
        'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival',
        'Performance', 'Persuasion'
    ]

    tool_proficiencies = [
        "Thieves' Tools", "Smith's Tools", "Brewer's Supplies",
        "Gaming Set (Dice)", "Gaming Set (Cards)", "Gaming Set (Dragonchess)"
    ]

    all_options = all_skills + tool_proficiencies
    random_skill = random.choice(all_options)

    return ['Deception', 'Intimidation', random_skill]

def _get_simple_non_evil_skills(self) -> List[str]:
    """Nature + Survival + 1 from limited pool."""
    limited_pool = ['Medicine', 'Insight', 'Persuasion', 'Intimidation']
    random_skill = random.choice(limited_pool)

    return ['Nature', 'Survival', random_skill]

def _get_simple_evil_skills(self) -> List[str]:
    """Nature + Survival + 1 from very limited pool."""
    very_limited_pool = ['Insight', 'Persuasion', 'Intimidation']
    random_skill = random.choice(very_limited_pool)

    return ['Nature', 'Survival', random_skill]
```

**Update create_parlay_challenge() signature**:
```python
def create_parlay_challenge(self, character_id: str, monsters: List[Dict]) -> Optional[str]:
    """
    Create a skill challenge for parlay attempt.
    Now uses intelligence/alignment-based skill selection.
    """
    # Get skills and disadvantage mode based on monster type
    parlay_skills, disadvantage_mode = self.get_parlay_skills_for_encounter(monsters)

    if not parlay_skills:
        return None

    # ... rest of existing code ...
    # Store disadvantage_mode in session metadata for widget to use
```

#### Step 2.2: Add Disadvantage Support to Skill Challenge Widget

**File**: `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

**Add properties**:
```python
class SkillChallengeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = SkillChallengeManager()
        self.current_session: Optional[SkillChallengeSession] = None
        self.character_data: Optional[Dict] = None
        self.skill_buttons: Dict[str, SkillButton] = {}

        # NEW: Disadvantage tracking
        self.disadvantage_mode = 'none'  # 'none', 'first', 'all'
        self.attempt_count = 0

        self.setup_ui()

    def set_disadvantage_mode(self, mode: str):
        """Set disadvantage mode: 'none', 'first', 'all'."""
        self.disadvantage_mode = mode
        self.attempt_count = 0

        if mode != 'none':
            self._show_disadvantage_warning(mode)

    def _show_disadvantage_warning(self, mode: str):
        """Display warning about disadvantage in description."""
        if mode == 'first':
            warning = "\n\nWARNING: Your first skill check will be made with DISADVANTAGE"
        elif mode == 'all':
            warning = "\n\nWARNING: ALL skill checks will be made with DISADVANTAGE"
        else:
            return

        current_text = self.description_text.toPlainText()
        self.description_text.setPlainText(current_text + warning)
```

**Modify _perform_skill_check() to support disadvantage** (find existing method and update):
```python
def _perform_skill_check(self, skill_name: str):
    """Perform skill check with optional disadvantage."""
    self.attempt_count += 1

    # Determine if this check has disadvantage
    has_disadvantage = False
    if self.disadvantage_mode == 'all':
        has_disadvantage = True
    elif self.disadvantage_mode == 'first' and self.attempt_count == 1:
        has_disadvantage = True

    # Roll d20 (or 2d20 for disadvantage)
    if has_disadvantage:
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        d20_roll = min(roll1, roll2)

        # Log disadvantage
        log_message = f"[DISADVANTAGE] {skill_name}: rolled {roll1}, {roll2} -> taking {d20_roll}"
        self._add_log_message(log_message)
    else:
        d20_roll = random.randint(1, 20)
        log_message = f"[ROLL] {skill_name}: {d20_roll}"
        self._add_log_message(log_message)

    # Continue with existing skill check logic...
    # (rest of method unchanged)
```

#### Step 2.3: Connect Influence Button to Parlay

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**Find where exploration_action signal is connected and add handler**:

```python
def __init__(self, parent=None, profile: LayoutProfile = BASELINE_PROFILE):
    # ... existing code ...

    # Connect exploration actions
    self.exploration_action.connect(self._handle_exploration_action)

def _handle_exploration_action(self, action: str):
    """Handle exploration button actions."""
    if action == "influence":
        self._attempt_parlay()
    elif action == "search":
        # Old search functionality (if any)
        pass
    # study and hide already have their own handlers
```

**Add parlay handler**:
```python
def _attempt_parlay(self):
    """Attempt to parlay with encounter monsters using Influence."""
    from talekeeper.services.parlay_system import ParlaySystem

    if not self.encounter_instances:
        self._log_monster_action("[PARLAY] No active encounter to parlay with")
        return

    character_data = self._get_current_character_data()
    if not character_data:
        self._log_monster_action("[PARLAY] No active character")
        return

    character_id = character_data['id']

    # Get monsters from current encounter
    monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

    # Initialize parlay system
    parlay_system = ParlaySystem('talekeeper.db')

    # Check if parlay is possible
    can_parlay, reason = parlay_system.can_parlay_with_encounter(monsters)
    if not can_parlay:
        self._log_monster_action(f"[PARLAY] {reason}")
        return

    # Determine monster characteristics for logging
    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))
    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', 'neutral')
    is_evil = 'evil' in alignment.lower()

    # Determine parlay type
    if intelligence >= 4 and not is_evil:
        parlay_type = "Diplomatic Negotiation"
    elif intelligence >= 4 and is_evil:
        parlay_type = "Dangerous Negotiation"
    elif intelligence <= 3 and not is_evil:
        parlay_type = "Animal Handling"
    else:
        parlay_type = "Desperate Parlay"

    # Log parlay attempt
    monster_names = ', '.join([m.get('name', 'Unknown') for m in monsters[:3]])
    self._log_monster_action(f"[PARLAY] Type: {parlay_type}")
    self._log_monster_action(f"[PARLAY] Target: {monster_names}")
    self._log_monster_action(f"[PARLAY] Intelligence: {intelligence}, Alignment: {alignment}")

    # Get skills and disadvantage mode
    skills, disadvantage_mode = parlay_system.get_parlay_skills_for_encounter(monsters)

    # Log skill selection
    skills_text = ', '.join(skills)
    if disadvantage_mode == 'first':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text} (FIRST CHECK AT DISADVANTAGE)")
    elif disadvantage_mode == 'all':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text} (ALL CHECKS AT DISADVANTAGE)")
    else:
        self._log_monster_action(f"[PARLAY] Skills: {skills_text}")

    # Calculate potential XP reward
    xp_reward = parlay_system.calculate_parlay_xp_reward(monsters)
    self._log_monster_action(f"[PARLAY] Potential reward: {xp_reward} XP (50% of strongest monster)")

    # Create parlay skill challenge
    session_id = parlay_system.create_parlay_challenge(character_id, monsters)

    if not session_id:
        self._log_monster_action("[PARLAY] Failed to create parlay challenge")
        return

    # Get session from skill challenge manager
    skill_manager = SkillChallengeManager('talekeeper.db')
    session = skill_manager.get_active_session(character_id)

    if not session:
        self._log_monster_action("[PARLAY] Failed to load parlay session")
        return

    # Show skill challenge widget
    self._show_parlay_skill_challenge(session, xp_reward, disadvantage_mode)

def _show_parlay_skill_challenge(self, session, xp_reward: int, disadvantage_mode: str):
    """Display skill challenge widget for parlay."""
    # Hide monster cards during parlay
    self.monsters_frame.setVisible(False)

    # Create skill challenge widget
    self.skill_challenge_widget = SkillChallengeWidget()
    self.skill_challenge_widget.set_character_data(self._get_current_character_data())

    # Set disadvantage mode
    if hasattr(self.skill_challenge_widget, 'set_disadvantage_mode'):
        self.skill_challenge_widget.set_disadvantage_mode(disadvantage_mode)

    # Connect completion signals
    self.skill_challenge_widget.challenge_completed.connect(
        lambda outcome, reward_text: self._on_parlay_completed(outcome, reward_text, xp_reward)
    )
    self.skill_challenge_widget.challenge_refused.connect(self._on_parlay_refused)

    # Start challenge
    self.skill_challenge_widget.start_challenge(session.template)

    # Add to layout
    self.encounters_layout.addWidget(self.skill_challenge_widget)

def _on_parlay_completed(self, outcome: str, reward_text: str, xp_reward: int):
    """Handle parlay completion."""
    from talekeeper.services.parlay_system import ParlaySystem

    character_data = self._get_current_character_data()
    parlay_system = ParlaySystem('talekeeper.db')

    if outcome == 'success':
        # Peaceful resolution - award XP
        self._log_monster_action(f"[PARLAY SUCCESS] {reward_text}")

        result = parlay_system.apply_parlay_success(character_data['id'], xp_reward)
        self._log_monster_action(f"[XP] {result['message']}")

        # Update character display
        character_data['experience_points'] += xp_reward
        self._update_character_display(character_data)

        # Clear encounter
        self._clear_monster_cards()
        self.update_scene_description("The creatures accept your terms and depart peacefully.")

    elif outcome == 'failure':
        # Negotiations failed - combat begins
        self._log_monster_action(f"[PARLAY FAILURE] {reward_text}")
        self._log_monster_action("[COMBAT] Negotiations break down - combat begins!")

        # Show monsters and start combat
        self.monsters_frame.setVisible(True)
        self.set_encounter_mode()

    # Clean up widget
    if self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget = None

def _on_parlay_refused(self, refuse_cost: str):
    """Handle parlay refusal."""
    self._log_monster_action("[PARLAY REFUSED] You decide not to negotiate")
    self._log_monster_action("[PARLAY] No XP gained, encounter remains")

    # Show monsters again but don't start combat
    self.monsters_frame.setVisible(True)

    # Clean up widget
    if self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget = None
```

---

### Phase 3: Pickpocket System (Action Card)

**New Feature**: Characters with Deception + Sleight of Hand proficiency can pickpocket during successful parlay.

#### Step 3.1: Add Pickpocket Check to Parlay Success

**File**: `src/talekeeper/services/parlay_system.py`

```python
def can_pickpocket(self, character_id: str) -> Tuple[bool, str]:
    """
    Check if character can attempt pickpocketing.
    Requires BOTH Deception AND Sleight of Hand proficiency.
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get character proficiencies
        cursor.execute('''
            SELECT skill_name FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill'
        ''', (character_id,))

        proficiencies = [row[0] for row in cursor.fetchall()]

        has_deception = 'Deception' in proficiencies
        has_sleight = 'Sleight of Hand' in proficiencies

        if has_deception and has_sleight:
            return True, "You can attempt to pickpocket during parlay"
        elif has_deception:
            return False, "Need Sleight of Hand proficiency to pickpocket"
        elif has_sleight:
            return False, "Need Deception proficiency to pickpocket"
        else:
            return False, "Need both Deception and Sleight of Hand proficiencies"

    except Exception as e:
        print(f"Error checking pickpocket eligibility: {e}")
        return False, "Error checking proficiencies"
    finally:
        if conn:
            conn.close()

def calculate_pickpocket_loot(self, monsters: List[Dict]) -> int:
    """
    Calculate gold from pickpocketing.

    Roll 1d4 per monster CR (minimum 1).
    """
    total_gold = 0

    for monster in monsters:
        cr = monster.get('challenge_rating', 0)

        # Convert CR to integer (CR 1/4 = 0, CR 1/2 = 0, CR 1+ = value)
        if isinstance(cr, str) and '/' in cr:
            cr_value = 0
        else:
            cr_value = max(1, int(float(cr)))

        # Roll 1d4 per CR
        for _ in range(cr_value):
            total_gold += random.randint(1, 4)

    return total_gold
```

#### Step 3.2: Update Parlay Success Handler to Offer Pickpocket

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

Modify `_on_parlay_completed`:

```python
def _on_parlay_completed(self, outcome: str, reward_text: str, xp_reward: int):
    """Handle parlay completion."""
    from talekeeper.services.parlay_system import ParlaySystem

    character_data = self._get_current_character_data()
    parlay_system = ParlaySystem('talekeeper.db')

    if outcome == 'success':
        # Peaceful resolution - award XP
        self._log_monster_action(f"[PARLAY SUCCESS] {reward_text}")

        result = parlay_system.apply_parlay_success(character_data['id'], xp_reward)
        self._log_monster_action(f"[XP] {result['message']}")

        # Update character display
        character_data['experience_points'] += xp_reward
        self._update_character_display(character_data)

        # Check if character can pickpocket
        can_pickpocket, pickpocket_reason = parlay_system.can_pickpocket(character_data['id'])

        if can_pickpocket:
            # Store monsters for pickpocket action card
            self._parlay_monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

            self._log_monster_action("[PICKPOCKET] You notice an opportunity...")
            self._log_monster_action(f"[PICKPOCKET] {pickpocket_reason}")
            self._log_monster_action("[PICKPOCKET] Use 'Pickpocket' action card to attempt")

            # Trigger action card generation (will be handled in action panel)
            self.pickpocket_available.emit(True)

        # Clear encounter
        self._clear_monster_cards()
        self.update_scene_description("The creatures accept your terms and depart peacefully.")

    # ... rest of method unchanged ...
```

#### Step 3.3: Create Pickpocket Action Card

**File**: `src/talekeeper/ui/action_cards/action_panel.py`

**Add pickpocket action card**:

```python
def _create_pickpocket_card(self) -> Optional[ActionCard]:
    """
    Create Pickpocket action card (appears after successful parlay).

    Requires: Deception + Sleight of Hand proficiency
    Cost: Action
    """
    from talekeeper.services.parlay_system import ParlaySystem

    if not hasattr(self.parent(), 'encounter_panel'):
        return None

    encounter_panel = self.parent().encounter_panel

    # Check if pickpocket is available
    if not hasattr(encounter_panel, '_parlay_monsters'):
        return None

    parlay_system = ParlaySystem('talekeeper.db')
    character_id = self.character_data['id']

    can_pickpocket, reason = parlay_system.can_pickpocket(character_id)
    if not can_pickpocket:
        return None

    # Get DEX modifier for display
    dex_mod = (self.character_data.get('dexterity', 10) - 10) // 2
    prof_bonus = get_proficiency_bonus(self.character_data.get('level', 1))

    total_bonus = dex_mod + prof_bonus
    bonus_text = f"+{total_bonus}" if total_bonus >= 0 else str(total_bonus)

    card = ActionCard(
        name="Pickpocket",
        action_type="action",
        description=f"Attempt to steal gold from creatures during parlay\n"
                   f"Sleight of Hand check: {bonus_text}\n"
                   f"Risk: If detected, negotiations fail and combat begins",
        icon_path=None
    )

    card.clicked.connect(lambda: self._execute_pickpocket())

    return card

def _execute_pickpocket(self):
    """Execute pickpocket attempt."""
    from talekeeper.services.parlay_system import ParlaySystem

    encounter_panel = self.parent().encounter_panel

    if not hasattr(encounter_panel, '_parlay_monsters'):
        self._log_action("[PICKPOCKET] No parlay encounter to pickpocket")
        return

    monsters = encounter_panel._parlay_monsters
    parlay_system = ParlaySystem('talekeeper.db')

    # Get character stats
    dex_mod = (self.character_data.get('dexterity', 10) - 10) // 2
    prof_bonus = get_proficiency_bonus(self.character_data.get('level', 1))

    # Roll Sleight of Hand
    d20_roll = random.randint(1, 20)
    sleight_total = d20_roll + dex_mod + prof_bonus

    # DC = 10 + average monster Perception
    avg_perception = 10  # Most monsters have ~10 passive perception
    dc = 10 + avg_perception

    self._log_action(f"[PICKPOCKET] Sleight of Hand: d20({d20_roll}) +{dex_mod} DEX +{prof_bonus} prof = {sleight_total}")
    self._log_action(f"[PICKPOCKET] DC: {dc}")

    if sleight_total >= dc:
        # Success - steal gold
        gold_stolen = parlay_system.calculate_pickpocket_loot(monsters)

        self._log_action(f"[PICKPOCKET SUCCESS] You stealthily steal {gold_stolen} gold!")

        # Add gold to character
        # (Assuming gold is tracked in character_data or inventory)
        # Update character gold here

        # Clean up
        del encounter_panel._parlay_monsters

    else:
        # Failure - detected! Combat begins
        self._log_action(f"[PICKPOCKET FAILED] You were detected!")
        self._log_action("[COMBAT] The creatures attack!")

        # Restore monsters and start combat
        encounter_panel._restore_parlay_monsters_for_combat()
        encounter_panel.set_encounter_mode()
```

---

## Summary of Changes

### Existing UI Buttons - New Functions

| Button | Old Function | New Function | Implementation |
|--------|-------------|--------------|----------------|
| **Influence** | Not connected | Trigger Parlay System | ✅ Detailed plan |
| **Search** | Not connected | REPLACE with **Flee** | ✅ Simple implementation |
| **Study** | ✅ Working | No change (reveal monster info) | Already done |
| **Hide** | ✅ Partially working | No change (stealth check) | Already done |

### New Systems

1. **Enhanced Parlay System**
   - Intelligence/alignment-based skill selection
   - 4 parlay categories (Diplomatic, Dangerous, Animal, Desperate)
   - Disadvantage mechanics for evil creatures

2. **Disadvantage Support in Skill Widget**
   - 2d20 take-lower rolls
   - Visual warnings
   - Three modes: none, first, all

3. **Pickpocket Action Card**
   - Requires Deception + Sleight of Hand proficiency
   - Appears after successful parlay
   - Risk: Detection triggers combat
   - Reward: 1d4 gold per monster CR

---

## Implementation Priority

### Sprint 1: Core Parlay System (Week 1)
- [ ] Add `get_parlay_skills_for_encounter()` to ParlaySystem
- [ ] Add 4 helper methods for skill selection
- [ ] Update `create_parlay_challenge()` to pass disadvantage mode

### Sprint 2: Skill Widget Disadvantage (Week 2)
- [ ] Add `disadvantage_mode` property to SkillChallengeWidget
- [ ] Add `set_disadvantage_mode()` method
- [ ] Modify `_perform_skill_check()` for 2d20 rolls
- [ ] Add disadvantage warning display

### Sprint 3: UI Integration (Week 3)
- [ ] Replace Search button with Flee button
- [ ] Connect Influence button to `_attempt_parlay()`
- [ ] Add `_show_parlay_skill_challenge()` method
- [ ] Add `_on_parlay_completed()` and `_on_parlay_refused()` handlers

### Sprint 4: Pickpocket System (Week 4)
- [ ] Add `can_pickpocket()` to ParlaySystem
- [ ] Add `calculate_pickpocket_loot()` to ParlaySystem
- [ ] Create Pickpocket action card
- [ ] Add pickpocket execution logic
- [ ] Add gold tracking/award

### Sprint 5: Testing & Polish (Week 5)
- [ ] Test all 4 parlay categories
- [ ] Test disadvantage mechanics
- [ ] Test pickpocket success/failure
- [ ] Add database tracking tables
- [ ] Write unit tests

---

## Total Estimated Time: 5 Weeks

Much simpler than original 7-week plan because:
- ✅ No dialog creation needed
- ✅ UI buttons already exist
- ✅ Study button shows pattern to follow
- ✅ Hide button shows stealth integration
- ✅ No "Search" functionality to preserve

---

## Next Steps

1. Implement Sprint 1 (Parlay System Enhancement)
2. Test with different monster types
3. Move to Sprint 2 (Disadvantage Support)
4. Integrate into UI (Sprint 3)
5. Add Pickpocket bonus feature (Sprint 4)
