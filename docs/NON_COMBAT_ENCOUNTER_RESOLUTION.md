# Non-Combat Encounter Resolution - UI Integration Plan

## Executive Summary

TaleKeeper has three non-combat encounter resolution systems, but only one is accessible during monster encounters:

- [YES] **Skill Challenge System**: Fully accessible via encounter dropdown - works as standalone encounter type
- [NO] **Parlay System**: Fully implemented backend, but NO UI integration - never offered during monster encounters
- [NO] **Stealth Avoidance System**: Fully implemented backend, but NO UI integration - automatic check only, no player choice

**The Problem**: When players encounter monsters, they are immediately put into combat mode with no option to attempt parlay or stealth avoidance. The backend systems exist and work, but there's no pre-combat decision point in the UI.

**The Solution**: Add an encounter options dialog that appears after generating a monster encounter, offering choices to parlay, sneak past, fight, or flee - before combat begins.

This document details the plan to integrate the parlay and stealth systems into monster encounters, giving players meaningful tactical choices.

## Current State Analysis

### Implemented Backend Systems

#### 1. Skill Challenge System
**Status**: [COMPLETE] Fully Implemented & UI-Integrated
**Location**: `src/talekeeper/services/skill_challenge_manager.py`
**UI Access**: Encounter dropdown -> "Skill Challenge" option (as standalone encounter type)
**Usage**: Currently works as a standalone encounter type (not integrated with monster encounters)
**Functionality**:
- 3 successes before 3 failures mechanic
- DC escalation on repeated skill use
- Information hiding (75% success revealed, 50% failure revealed)
- Database tracking via `skill_challenge_sessions` and `skill_challenge_attempts`
- Rewards via `SkillChallengeRewards` service
- Widget: `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

**Note**: The skill challenge system is accessible, but only as a separate encounter type. It is NOT currently used for parlay during monster encounters - that's what needs to be integrated.

#### 2. Parlay System
**Status**: [PARTIAL] Implemented But Not UI-Integrated (Requires Enhancement)
**Location**: `src/talekeeper/services/parlay_system.py`
**UI Access**: None - no trigger during encounters
**Current Implementation**: Basic 3 CHA + 1 INT/WIS skill selection
**Required Enhancement**: Intelligence and alignment-based skill selection rules

**Functionality**:
- `can_parlay_with_encounter(monsters)` - checks if encounter is non-evil
- 75% chance non-evil monsters accept parlay
- Creates dynamic skill challenge based on monster intelligence and alignment
- XP reward: 50% of most powerful monster's XP
- Three outcomes:
  - **Success**: Peaceful resolution, 1/2 XP, no combat
  - **Failure**: Negotiations fail, normal combat begins
  - **Refuse**: Walk away, no XP, no combat

**New Parlay Rules (Intelligence & Alignment-Based)**:

| Monster Type | Intelligence | Alignment | Skill 1 | Skill 2 | Skill 3 | Disadvantage | Example Monsters |
|-------------|--------------|-----------|---------|---------|---------|--------------|------------------|
| **Intelligent Non-Evil** | 4+ | Non-Evil | Random CHA | Random CHA | Random INT/WIS | None | Centaur, Sprite, Treant, Merfolk |
| **Intelligent Evil** | 4+ | Evil | Deception | Intimidation | Random (any + tools) | First check only | Mind Flayer, Vampire, Rakshasa, Devil |
| **Simple Non-Evil** | 3 or less | Non-Evil | Nature | Survival | Random (Med/Ins/Per/Int) | None | Dire Wolf, Giant Eagle, Awakened Tree |
| **Simple Evil** | 3 or less | Evil | Nature | Survival | Random (Ins/Per/Int) | ALL checks | Zombie, Skeleton, Giant Spider, Swarm |

**Quick Reference**:
- **INT 4+ = Intelligent** (can reason, negotiate)
- **INT 3 or less = Simple** (instinct-driven, use Nature/Survival)
- **Evil = Harder** (disadvantage applies)
- **Non-Evil = Fair** (no disadvantage)

**Detailed Skill Selection Rules**:

1. **Non-Evil, Intelligence 4+** (Diplomatic)
   - Skills: 2 random CHA skills + 1 random INT/WIS skill
   - CHA Pool: Deception, Intimidation, Performance, Persuasion
   - INT/WIS Pool: Arcana, History, Investigation, Nature, Religion, Animal Handling, Insight, Medicine, Perception, Survival
   - Disadvantage: None
   - Example: Persuasion + Performance + Insight

2. **Evil, Intelligence 4+** (Dangerous Negotiation)
   - Skills: Deception + Intimidation + 1 random skill (any type)
   - Random Pool: All skills (including Athletics, Acrobatics, etc.) + tool proficiencies + gaming sets
   - Disadvantage: First skill check only
   - Example: Deception (disadvantage) + Intimidation + Sleight of Hand

3. **Non-Evil, Intelligence 3 or less** (Animal/Beast Handling)
   - Skills: Nature + Survival + 1 random from limited pool
   - Random Pool: Medicine, Insight, Persuasion, Intimidation
   - Disadvantage: None
   - Example: Nature + Survival + Medicine

4. **Evil, Intelligence 3 or less** (Extremely Dangerous)
   - Skills: Nature + Survival + 1 random from limited pool
   - Random Pool: Insight, Persuasion, Intimidation (no Medicine)
   - Disadvantage: All skill checks
   - Example: Nature (disadvantage) + Survival (disadvantage) + Intimidation (disadvantage)

**Key Methods**:

*Existing (no changes needed)*:
```python
can_parlay_with_encounter(monsters) -> (bool, str)  # Already exists
calculate_parlay_xp_reward(monsters) -> int  # Already exists
apply_parlay_success(character_id, xp_reward) -> dict  # Already exists
```

*Require Changes*:
```python
# BEFORE (current implementation):
get_parlay_skills() -> List[str]  # No parameters, simple CHA skills

# AFTER (enhanced implementation):
get_parlay_skills_for_encounter(monsters) -> Tuple[List[str], str]
# Returns (skills_list, disadvantage_mode)
# disadvantage_mode: 'none', 'first', 'all'

# BEFORE:
create_parlay_challenge(character_id, monsters) -> session_id

# AFTER:
create_parlay_challenge(character_id, monsters, skills, disadvantage_mode) -> session_id
```

*New Methods to Add*:
```python
get_parlay_difficulty_modifier(monsters) -> int  # DC modifier for evil/low-INT
_get_intelligent_non_evil_skills() -> List[str]  # Helper method
_get_intelligent_evil_skills() -> List[str]  # Helper method
_get_simple_non_evil_skills() -> List[str]  # Helper method
_get_simple_evil_skills() -> List[str]  # Helper method
```

#### 3. Encounter Avoidance System
**Status**: [PARTIAL] Implemented But Not UI-Integrated
**Location**: `src/talekeeper/services/encounter_avoidance.py`
**UI Access**: Automatic stealth check only - no player choice
**Functionality**:
- Requires Stealth proficiency
- Stealth check (DC 15) vs monster Perception
- Uses existing `StealthMechanicsService` for equipment modifiers
- XP reward: 33% of total encounter XP
- Accounts for:
  - Heavy armor disadvantage
  - Elven cloak advantage
  - Mithral armor (no disadvantage)
  - DEX modifier + proficiency

**Key Methods**:
```python
can_attempt_avoidance(character_id, monsters) -> (bool, str)
attempt_avoidance(character_id, character_data, monsters) -> dict
get_encounter_difficulty(monsters, character_level) -> str
_calculate_avoidance_xp(monsters) -> int  # 33% of total
```

### Current Encounter Flow

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

```python
def _generate_monster_encounter(self):  # Line 4494
    # 1. Generate encounter data
    # 2. Create monster cards
    # 3. Check stealth automatically (line 4650)
    # 4. Switch to encounter mode
    # MISSING: Player choice for parlay/avoidance
```

**Problem**: Players never see options to attempt parlay or avoidance.

## XP Balance Analysis

For a typical 100 XP encounter:

| Resolution Method | XP Award | Outcome |
|------------------|----------|---------|
| **Combat Victory** | 100 XP (100%) | Fight and win |
| **Parlay Success** | 50 XP (50%) | Avoid combat via negotiation |
| **Stealth Success** | 33 XP (33%) | Avoid combat via stealth |
| **Parlay Failure** | -> Combat | Failed negotiation -> fight |
| **Stealth Failure** | -> Combat | Detected -> fight |
| **Refuse/Flee** | 0 XP | Walk away peacefully |

**Design Philosophy**:
- **Success = Avoid Combat**: Trade lower XP for avoiding the fight
- **Failure = Combat**: Attempt fails, you end up fighting anyway
- **Refuse = Walk Away**: Safe exit with no reward

## Implementation Plan

### Phase 1: Pre-Combat Decision UI

#### 1.1 Encounter Options Dialog
**Location**: New file `src/talekeeper/ui/encounter_pane/encounter_options_dialog.py`

**Purpose**: Modal dialog presented after encounter generation, before combat begins.

**UI Layout**:
```
+-----------------------------------------------+
|  Encounter Options                            |
+-----------------------------------------------+
|                                               |
|  You encounter: 2x Goblins, 1x Hobgoblin     |
|  Difficulty: Medium (150 XP)                  |
|                                               |
|  Choose your approach:                        |
|                                               |
|  +-----------------------------------------+  |
|  | [FIGHT] Begin Combat                    |  |
|  | Full XP if victorious                   |  |
|  | Risk: High                              |  |
|  +-----------------------------------------+  |
|                                               |
|  +-----------------------------------------+  |
|  | [PARLAY] Attempt Parlay (Available)     |  |
|  | These creatures might negotiate         |  |
|  | Reward: 75 XP (50% of strongest)        |  |
|  | Skill Challenge: 3 CHA + 1 INT/WIS skill|  |
|  | Failure: Combat with disadvantage       |  |
|  +-----------------------------------------+  |
|                                               |
|  +-----------------------------------------+  |
|  | [STEALTH] Attempt Stealth Avoidance     |  |
|  | Sneak past undetected                   |  |
|  | Reward: 50 XP (33% of total)            |  |
|  | Requires: Stealth proficiency           |  |
|  | Check: Stealth vs Perception            |  |
|  | Failure: Normal combat                  |  |
|  +-----------------------------------------+  |
|                                               |
|  +-----------------------------------------+  |
|  | [FLEE] Flee Encounter                   |  |
|  | Retreat without engagement              |  |
|  | Reward: 0 XP                            |  |
|  +-----------------------------------------+  |
|                                               |
|                         [Cancel]             |
+-----------------------------------------------+
```

**Dynamic Option Availability**:
- **Parlay**: Only if `parlay_system.can_parlay_with_encounter(monsters)` returns True
- **Stealth**: Only if `avoidance_system.can_attempt_avoidance(character_id, monsters)` returns True
- **Combat**: Always available
- **Flee**: Always available

**Grayed-Out States**:
```
+-----------------------------------------+
| [PARLAY] Attempt Parlay (Unavailable)   |
| These creatures are too evil to negotiate|
+-----------------------------------------+

+-----------------------------------------+
| [STEALTH] Stealth Avoidance (Unavailable)|
| You lack Stealth proficiency            |
+-----------------------------------------+
```

#### 1.2 Dialog Implementation

**Class Structure**:
```python
class EncounterOptionsDialog(QDialog):
    option_selected = pyqtSignal(str)  # "combat", "parlay", "stealth", "flee"

    def __init__(self, monsters: List[Dict], character_data: dict, parent=None):
        self.monsters = monsters
        self.character_data = character_data
        self.parlay_system = ParlaySystem()
        self.avoidance_system = EncounterAvoidanceSystem()

        self._setup_ui()
        self._check_option_availability()

    def _check_option_availability(self):
        # Check parlay eligibility
        can_parlay, parlay_reason = self.parlay_system.can_parlay_with_encounter(self.monsters)

        # Check stealth eligibility
        can_stealth, stealth_reason = self.avoidance_system.can_attempt_avoidance(
            self.character_data['id'], self.monsters
        )

        # Enable/disable buttons with tooltips

    def _on_option_clicked(self, option: str):
        self.option_selected.emit(option)
        self.accept()
```

**Integration Point**:
```python
# In encounter_panel.py, line ~4650
def _generate_monster_encounter(self):
    # ... existing code ...

    # Show encounter options dialog BEFORE switching to encounter mode
    self._show_encounter_options_dialog(encounter_data['monsters'])

def _show_encounter_options_dialog(self, monsters: List[Dict]):
    character_data = self._get_current_character_data()

    dialog = EncounterOptionsDialog(monsters, character_data, self)
    dialog.option_selected.connect(self._handle_encounter_option)
    dialog.exec()

def _handle_encounter_option(self, option: str):
    if option == "combat":
        self.set_encounter_mode()
    elif option == "parlay":
        self._attempt_parlay()
    elif option == "stealth":
        self._attempt_stealth_avoidance()
    elif option == "flee":
        self._flee_encounter()
```

### Phase 2: Parlay System Enhancement

#### 2.0 Update ParlaySystem Service
**Location**: `src/talekeeper/services/parlay_system.py`

**CRITICAL**: The existing `get_parlay_skills()` method must be updated to accept monster data and determine skills based on intelligence and alignment.

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

    # Use the most powerful monster to determine parlay type
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
            # Intelligent Evil: Deception + Intimidation + 1 random (any)
            return self._get_intelligent_evil_skills(), 'first'
    else:
        if not is_evil:
            # Simple Non-Evil: Nature + Survival + 1 random (limited)
            return self._get_simple_non_evil_skills(), 'none'
        else:
            # Simple Evil: Nature + Survival + 1 random (very limited)
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
    """Deception + Intimidation + 1 random skill (any type)."""
    all_skills = [
        'Athletics', 'Acrobatics', 'Sleight of Hand', 'Stealth',
        'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
        'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival',
        'Performance', 'Persuasion'
    ]

    # Can also include tool proficiencies
    tool_proficiencies = [
        "Thieves' Tools", "Smith's Tools", "Brewer's Supplies",
        "Gaming Set (Dice)", "Gaming Set (Cards)", "Gaming Set (Dragonchess)"
    ]

    all_options = all_skills + tool_proficiencies
    random_skill = random.choice(all_options)

    return ['Deception', 'Intimidation', random_skill]

def _get_simple_non_evil_skills(self) -> List[str]:
    """Nature + Survival + 1 random from limited pool."""
    limited_pool = ['Medicine', 'Insight', 'Persuasion', 'Intimidation']
    random_skill = random.choice(limited_pool)

    return ['Nature', 'Survival', random_skill]

def _get_simple_evil_skills(self) -> List[str]:
    """Nature + Survival + 1 random from very limited pool."""
    very_limited_pool = ['Insight', 'Persuasion', 'Intimidation']
    random_skill = random.choice(very_limited_pool)

    return ['Nature', 'Survival', random_skill]

def get_parlay_difficulty_modifier(self, monsters: List[Dict]) -> int:
    """
    Get DC modifier based on monster type.

    Evil creatures and low-intelligence creatures may have higher DCs.
    """
    if not monsters:
        return 0

    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))
    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', '').lower()
    is_evil = 'evil' in alignment

    modifier = 0

    # Evil creatures are harder to negotiate with
    if is_evil:
        modifier += 2

    # Low intelligence creatures are unpredictable
    if intelligence <= 3:
        modifier += 1

    return modifier
```

#### 2.1 Parlay Attempt Handler
**Location**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

```python
def _attempt_parlay(self):
    """Initiate parlay attempt with current encounter monsters."""
    character_data = self._get_current_character_data()
    character_id = character_data['id']

    # Get monsters from current encounter
    monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

    # Check eligibility (should already be checked, but verify)
    can_parlay, reason = self.parlay_system.can_parlay_with_encounter(monsters)
    if not can_parlay:
        self._log_monster_action(f"[PARLAY] Failed: {reason}")
        return

    # Determine parlay type based on monster intelligence/alignment
    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))
    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', 'neutral')
    is_evil = 'evil' in alignment.lower()

    # Log monster characteristics
    self._log_monster_action(f"[PARLAY] Target: {primary_monster['name']}")
    self._log_monster_action(f"[PARLAY] Intelligence: {intelligence}, Alignment: {alignment}")

    # Determine parlay category
    if intelligence >= 4 and not is_evil:
        parlay_type = "Diplomatic Negotiation"
    elif intelligence >= 4 and is_evil:
        parlay_type = "Dangerous Negotiation"
    elif intelligence <= 3 and not is_evil:
        parlay_type = "Animal Handling"
    else:
        parlay_type = "Desperate Parlay"

    self._log_monster_action(f"[PARLAY] Type: {parlay_type}")

    # Get skills and disadvantage mode
    skills, disadvantage_mode = self.parlay_system.get_parlay_skills_for_encounter(monsters)

    # Log skill selection
    skills_text = ', '.join(skills)
    if disadvantage_mode == 'first':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text} (FIRST CHECK AT DISADVANTAGE)")
    elif disadvantage_mode == 'all':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text} (ALL CHECKS AT DISADVANTAGE)")
    else:
        self._log_monster_action(f"[PARLAY] Skills: {skills_text}")

    # Create parlay skill challenge with enhanced parameters
    session_id = self.parlay_system.create_parlay_challenge(
        character_id, monsters, skills, disadvantage_mode
    )

    if not session_id:
        self._log_monster_action("[PARLAY] Failed to create parlay challenge")
        return

    # Get the session to display
    session = self.skill_challenge_manager.get_active_session(character_id)

    # Calculate potential rewards for display
    xp_reward = self.parlay_system.calculate_parlay_xp_reward(monsters)

    # Log parlay attempt
    monster_names = ', '.join([m.get('name', 'Unknown') for m in monsters[:3]])
    self._log_monster_action(f"[PARLAY] Attempting {parlay_type} with {monster_names}")
    self._log_monster_action(f"[PARLAY] Potential reward: {xp_reward} XP")

    # Show skill challenge widget
    self._show_parlay_skill_challenge(session, xp_reward, disadvantage_mode)

def _show_parlay_skill_challenge(self, session: SkillChallengeSession, xp_reward: int, disadvantage_mode: str):
    """Display skill challenge widget for parlay."""
    # Hide monster cards
    self.monsters_frame.setVisible(False)

    # Create skill challenge widget
    self.skill_challenge_widget = SkillChallengeWidget()
    self.skill_challenge_widget.set_character_data(self._get_current_character_data())

    # Set disadvantage mode for parlay
    if hasattr(self.skill_challenge_widget, 'set_disadvantage_mode'):
        self.skill_challenge_widget.set_disadvantage_mode(disadvantage_mode)

    # Connect signals
    self.skill_challenge_widget.challenge_completed.connect(
        lambda outcome, reward_text: self._on_parlay_completed(outcome, reward_text, xp_reward)
    )
    self.skill_challenge_widget.challenge_refused.connect(self._on_parlay_refused)

    # Start the challenge
    self.skill_challenge_widget.start_challenge(session.template)

    # Add to layout
    self.encounters_layout.addWidget(self.skill_challenge_widget)
```

#### 2.2 Skill Challenge Widget Enhancement
**Location**: `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

**CRITICAL**: The skill challenge widget must support disadvantage on skill checks for parlay.

```python
class SkillChallengeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.disadvantage_mode = 'none'  # 'none', 'first', 'all'
        self.attempt_count = 0  # Track which attempt we're on

    def set_disadvantage_mode(self, mode: str):
        """
        Set disadvantage mode for skill checks.

        Args:
            mode: 'none', 'first' (first check only), 'all' (all checks)
        """
        self.disadvantage_mode = mode
        if mode != 'none':
            self._update_disadvantage_warning(mode)

    def _update_disadvantage_warning(self, mode: str):
        """Display warning about disadvantage."""
        if mode == 'first':
            warning = "WARNING: Your first skill check will be made with DISADVANTAGE"
        elif mode == 'all':
            warning = "WARNING: ALL skill checks will be made with DISADVANTAGE"
        else:
            return

        # Add warning label to UI
        if hasattr(self, 'info_label'):
            current_text = self.info_label.text()
            self.info_label.setText(f"{current_text}\n\n{warning}")

    def _perform_skill_check(self, skill_name: str):
        """Perform a skill check with optional disadvantage."""
        self.attempt_count += 1

        # Determine if this check has disadvantage
        has_disadvantage = False
        if self.disadvantage_mode == 'all':
            has_disadvantage = True
        elif self.disadvantage_mode == 'first' and self.attempt_count == 1:
            has_disadvantage = True

        if has_disadvantage:
            # Roll 2d20, take lower
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll_result = min(roll1, roll2)

            # Log both rolls
            self._log_action(f"[DISADVANTAGE] Rolling {skill_name} with disadvantage")
            self._log_action(f"[ROLLS] {roll1}, {roll2} -> taking {roll_result}")
        else:
            # Normal roll
            roll_result = random.randint(1, 20)
            self._log_action(f"[ROLL] {skill_name}: {roll_result}")

        # Continue with normal skill check logic
        # ... (existing code)
```


#### 2.2 Parlay Outcome Handlers

```python
def _on_parlay_completed(self, outcome: str, reward_text: str, xp_reward: int):
    """Handle parlay skill challenge completion."""
    character_data = self._get_current_character_data()

    if outcome == 'success':
        # Peaceful resolution
        self._log_monster_action(f"[PARLAY SUCCESS] {reward_text}")

        # Award XP
        result = self.parlay_system.apply_parlay_success(character_data['id'], xp_reward)
        self._log_monster_action(f"[XP] {result['message']}")

        # Update character data
        character_data['experience_points'] += xp_reward
        self._update_character_display(character_data)

        # Clear encounter
        self._clear_monster_cards()
        self.update_scene_description("The creatures accept your terms and depart peacefully.")

    elif outcome == 'failure':
        # Combat begins normally
        self._log_monster_action(f"[PARLAY FAILURE] {reward_text}")
        self._log_monster_action("[COMBAT] Negotiations break down - combat begins!")

        # Begin combat normally (no penalties)
        self.set_encounter_mode()
        self.monsters_frame.setVisible(True)

    # Clean up skill challenge widget
    if self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget = None

def _on_parlay_refused(self, refuse_cost: str):
    """Handle parlay refusal (walk away)."""
    self._log_monster_action(f"[PARLAY REFUSED] You decide to walk away cautiously")
    self._log_monster_action("[ENCOUNTER] No XP gained, no combat")

    # Clear encounter
    self._clear_monster_cards()
    self.update_scene_description("You carefully retreat from the encounter without engaging.")

    # Clean up widget
    if self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget = None
```

### Phase 3: Stealth Avoidance Flow Implementation

#### 3.1 Stealth Avoidance Handler

```python
def _attempt_stealth_avoidance(self):
    """Attempt to avoid encounter using stealth."""
    character_data = self._get_current_character_data()
    character_id = character_data['id']

    # Get monsters from current encounter
    monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

    # Check eligibility
    can_attempt, reason = self.avoidance_system.can_attempt_avoidance(character_id, monsters)
    if not can_attempt:
        self._log_monster_action(f"[STEALTH] Failed: {reason}")
        return

    # Get encounter difficulty for context
    difficulty = self.avoidance_system.get_encounter_difficulty(
        monsters, character_data.get('level', 1)
    )

    # Log attempt
    self._log_monster_action(f"[STEALTH] Attempting to sneak past ({difficulty} encounter)...")

    # Perform stealth check
    result = self.avoidance_system.attempt_avoidance(character_id, character_data, monsters)

    # Handle result
    self._handle_stealth_result(result)

def _handle_stealth_result(self, result: dict):
    """Handle stealth avoidance check result."""
    stealth_total = result['stealth_total']
    highest_perception = result['highest_perception']

    if result['success']:
        # Successful avoidance
        xp_reward = result['xp_reward']
        self._log_monster_action(f"[STEALTH SUCCESS] Your stealth ({stealth_total}) beats their perception ({highest_perception})")
        self._log_monster_action(f"[XP] {result['message']}")

        # Display detailed breakdown
        if 'breakdown' in result:
            breakdown = result['breakdown']
            if 'stealth_result' in breakdown:
                stealth_info = breakdown['stealth_result']
                if 'breakdown' in stealth_info:
                    details = stealth_info['breakdown']
                    sources = details.get('sources', [])
                    if sources:
                        self._log_monster_action(f"[STEALTH] Modifiers: {', '.join(sources)}")

        # Update character XP display
        character_data = self._get_current_character_data()
        self._update_character_display(character_data)

        # Clear encounter
        self._clear_monster_cards()
        self.update_scene_description("You slip past the creatures undetected, avoiding confrontation.")

    else:
        # Failed avoidance - combat begins
        self._log_monster_action(f"[STEALTH FAILURE] Your stealth ({stealth_total}) fails to beat their perception ({highest_perception})")
        self._log_monster_action(f"[COMBAT] {result['message']}")

        # Display which monster spotted you
        if 'breakdown' in result and 'monster_perceptions' in result['breakdown']:
            for monster_check in result['breakdown']['monster_perceptions']:
                if monster_check['result']['spotted']:
                    name = monster_check['name']
                    perc = monster_check['result']['total']
                    self._log_monster_action(f"[SPOTTED] {name} notices you (Perception: {perc})")

        # Begin combat normally
        self.set_encounter_mode()
```

### Phase 4: UI Polish & Feedback

#### 4.1 Enhanced Encounter Description

Update encounter description to include resolution options:

```python
def _update_encounter_description_with_options(self, encounter_data: dict):
    """Add available resolution options to encounter description."""
    base_desc = self._format_encounter_description(encounter_data)

    character_data = self._get_current_character_data()
    monsters = encounter_data['monsters']

    # Check available options
    options = []

    # Check parlay
    can_parlay, parlay_reason = self.parlay_system.can_parlay_with_encounter(monsters)
    if can_parlay:
        xp_reward = self.parlay_system.calculate_parlay_xp_reward(monsters)
        options.append(f"[PARLAY] Parlay Available - {xp_reward} XP reward")

    # Check stealth
    can_stealth, stealth_reason = self.avoidance_system.can_attempt_avoidance(
        character_data['id'], monsters
    )
    if can_stealth:
        xp_reward = self.avoidance_system._calculate_avoidance_xp(monsters)
        options.append(f"[STEALTH] Stealth Avoidance Available - {xp_reward} XP reward")

    if options:
        options_text = "\n".join([f"  * {opt}" for opt in options])
        full_desc = f"{base_desc}\n\n== Resolution Options ==\n{options_text}"
    else:
        full_desc = base_desc

    return full_desc
```

#### 4.2 Log Panel Integration

Enhanced logging for non-combat resolutions:

```
[ENCOUNTER] Medium difficulty encounter (150 XP)
[ENCOUNTER] 2x Goblin, 1x Hobgoblin
[OPTIONS] Parlay available (75 XP), Stealth available (50 XP)

[PARLAY] Attempting diplomatic resolution with Goblin, Hobgoblin
[PARLAY] Skills: Persuasion, Deception, Intimidation, Insight
[PARLAY] Base DC: 15
[PARLAY] Attempting Persuasion...
[PARLAY] Roll: 14 + 3 CHA + 2 Prof = 19 vs DC 15 - SUCCESS (1/3)
[PARLAY] Attempting Insight...
[PARLAY] Roll: 8 + 1 WIS + 2 Prof = 11 vs DC 15 - FAILURE (1/3, 1/3)
...
[PARLAY SUCCESS] The creatures accept your terms
[XP] Gained 75 XP through peaceful negotiation
```

### Phase 5: Testing Strategy

#### 5.1 Unit Tests

**New Test Files**:
```
tests/ui/test_encounter_options_dialog.py
tests/integration/test_parlay_integration.py
tests/integration/test_stealth_avoidance_integration.py
```

**Test Cases**:
1. Encounter options dialog displays correct options
2. Parlay button only enabled for non-evil monsters
3. Stealth button only enabled with proficiency
4. Parlay success awards correct XP
5. Parlay failure triggers combat with disadvantage
6. Stealth success awards 33% XP and clears encounter
7. Stealth failure triggers normal combat
8. Flee option clears encounter with no XP

#### 5.2 Integration Tests

**File**: `tests/integration/test_non_combat_resolution.py`

```python
def test_full_parlay_flow():
    """Test complete parlay flow from encounter to resolution."""
    # Generate encounter with non-evil monsters
    # Open options dialog
    # Select parlay
    # Complete skill challenge successfully
    # Verify XP awarded
    # Verify encounter cleared

def test_stealth_avoidance_flow():
    """Test complete stealth avoidance flow."""
    # Generate encounter
    # Character has Stealth proficiency
    # Attempt stealth avoidance
    # Verify XP awarded on success
    # Verify combat begins on failure

def test_option_availability():
    """Test option availability based on conditions."""
    # Evil monsters: parlay unavailable
    # No stealth prof: stealth unavailable
    # Non-evil + stealth prof: both available
```

#### 5.3 Regression Tests

Add to `tests/run_regression_tests.py`:

```python
def test_non_combat_resolution_systems():
    """Test non-combat encounter resolution."""
    # Test parlay system
    # Test stealth avoidance
    # Test skill challenge integration
    # Verify XP awards
```

### Phase 6: Database Schema Updates

#### 6.1 Encounter Tracking

Add resolution method tracking to encounters:

```sql
-- Migration: XXX_add_encounter_resolution_tracking.sql

ALTER TABLE encounters ADD COLUMN resolution_method TEXT;
-- Values: 'combat', 'parlay', 'stealth', 'fled', null

ALTER TABLE encounters ADD COLUMN resolution_xp INTEGER DEFAULT 0;
-- XP awarded for resolution

ALTER TABLE encounters ADD COLUMN resolution_timestamp TEXT;
-- When resolution occurred

-- Track parlay attempts
CREATE TABLE IF NOT EXISTS parlay_attempts (
    id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    character_id TEXT NOT NULL,
    monsters_json TEXT NOT NULL,
    can_parlay BOOLEAN NOT NULL,
    parlay_reason TEXT,
    outcome TEXT, -- 'success', 'failure', 'refused', 'not_attempted'
    xp_reward INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Track stealth avoidance attempts
CREATE TABLE IF NOT EXISTS stealth_avoidance_attempts (
    id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    character_id TEXT NOT NULL,
    stealth_total INTEGER NOT NULL,
    highest_perception INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    breakdown_json TEXT, -- Detailed results
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);
```

#### 6.2 Analytics Queries

```sql
-- Character's preferred resolution methods
SELECT
    resolution_method,
    COUNT(*) as times_used,
    SUM(resolution_xp) as total_xp
FROM encounters
WHERE character_id = ?
GROUP BY resolution_method;

-- Parlay success rate
SELECT
    outcome,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM parlay_attempts WHERE character_id = ?), 2) as percentage
FROM parlay_attempts
WHERE character_id = ?
GROUP BY outcome;

-- Stealth avoidance success rate
SELECT
    success,
    COUNT(*) as count,
    AVG(stealth_total) as avg_stealth,
    AVG(highest_perception) as avg_perception
FROM stealth_avoidance_attempts
WHERE character_id = ?
GROUP BY success;
```

### Phase 7: Configuration & Settings

#### 7.1 Feature Toggles

Add to `core/config.py`:

```python
class EncounterResolutionConfig:
    """Configuration for non-combat encounter resolution."""

    # Feature flags
    enable_parlay_system: bool = True
    enable_stealth_avoidance: bool = True
    show_encounter_options_dialog: bool = True

    # Parlay settings
    parlay_xp_multiplier: float = 0.5  # 50% of strongest monster
    parlay_non_evil_chance: float = 0.75  # 75% of non-evil accept parlay
    parlay_failure_starts_combat: bool = True  # Failed parlay leads to combat

    # Stealth settings
    stealth_xp_multiplier: float = 0.33  # 33% of total XP
    stealth_base_dc: int = 15

    # UI settings
    auto_show_options_dialog: bool = True
    show_xp_preview: bool = True
    show_risk_warnings: bool = True
```

#### 7.2 User Preferences

Add to settings dialog:

```
[X] Enable Parlay System
[X] Enable Stealth Avoidance
[X] Show Encounter Options Before Combat
[ ] Auto-attempt Stealth (skip dialog)
[X] Show XP Previews in Options
```

## Implementation Priority

### Sprint 1: Parlay System Enhancement (Week 1)
**PREREQUISITE**: Must be completed before UI work
- [ ] **RENAME** `get_parlay_skills()` -> `get_parlay_skills_for_encounter(monsters)`
- [ ] Add `monsters` parameter and return disadvantage mode as tuple
- [ ] Implement intelligence and alignment-based skill selection logic
- [ ] Add `_get_intelligent_non_evil_skills()` helper method
- [ ] Add `_get_intelligent_evil_skills()` helper method
- [ ] Add `_get_simple_non_evil_skills()` helper method
- [ ] Add `_get_simple_evil_skills()` helper method
- [ ] Add `get_parlay_difficulty_modifier(monsters)` method
- [ ] Update `create_parlay_challenge()` signature to accept `skills` and `disadvantage_mode` parameters
- [ ] Write unit tests for all four parlay categories
- [ ] Test disadvantage mode assignment ('none', 'first', 'all')

### Sprint 2: Skill Challenge Widget Enhancement (Week 2)
**PREREQUISITE**: Needed for disadvantage support
- [ ] Add `disadvantage_mode` property to `SkillChallengeWidget`
- [ ] Implement `set_disadvantage_mode()` method
- [ ] Add `attempt_count` tracking
- [ ] Modify `_perform_skill_check()` to support disadvantage
- [ ] Add disadvantage warning display in UI
- [ ] Implement 2d20 take-lower roll logic
- [ ] Add detailed logging for disadvantage rolls
- [ ] Test first-check-only disadvantage
- [ ] Test all-checks disadvantage

### Sprint 3: Core UI (Week 3)
- [ ] Create `EncounterOptionsDialog` class
- [ ] Integrate dialog into `_generate_monster_encounter()`
- [ ] Add option selection handlers
- [ ] Display monster intelligence and alignment in dialog
- [ ] Show parlay type (Diplomatic, Dangerous, Animal Handling, Desperate)
- [ ] Indicate disadvantage in parlay option text
- [ ] Basic styling and layout

### Sprint 4: Parlay Flow Integration (Week 4)
- [ ] Implement `_attempt_parlay()` method in encounter panel
- [ ] Connect to enhanced `ParlaySystem` service
- [ ] Pass disadvantage mode to skill challenge widget
- [ ] Handle parlay success/failure/refuse outcomes
- [ ] Handle parlay failure transition to combat
- [ ] Add detailed parlay logging with monster stats
- [ ] Test all four parlay categories end-to-end

### Sprint 5: Stealth Avoidance (Week 5)
- [ ] Implement `_attempt_stealth_avoidance()` method
- [ ] Connect to `EncounterAvoidanceSystem` service
- [ ] Handle stealth success/failure outcomes
- [ ] Add stealth logging with detailed breakdown
- [ ] Test stealth flow end-to-end

### Sprint 6: Database & Analytics (Week 6)
- [ ] Add database schema migrations
- [ ] Track resolution attempts in database
- [ ] Track parlay category types
- [ ] Store disadvantage mode used
- [ ] Create analytics queries
- [ ] Add configuration settings

### Sprint 7: Testing & Polish (Week 7)
- [ ] Write unit tests for all parlay categories
- [ ] Test intelligence threshold (3 vs 4)
- [ ] Test alignment detection
- [ ] Write integration tests for flows
- [ ] Add regression tests
- [ ] UI polish and feedback improvements
- [ ] Documentation updates

## Parlay System Test Cases

### Required Test Coverage

#### Intelligence & Alignment Categories
1. **Intelligent Non-Evil** (Intelligence 4+, Non-Evil)
   - Test with Centaur (INT 9, Neutral Good)
   - Verify: 2 CHA skills + 1 INT/WIS skill
   - Verify: No disadvantage

2. **Intelligent Evil** (Intelligence 4+, Evil)
   - Test with Mind Flayer (INT 19, Lawful Evil)
   - Verify: Deception + Intimidation + 1 random skill
   - Verify: First check has disadvantage
   - Verify: Random skill can be tool/game

3. **Simple Non-Evil** (Intelligence 3 or less, Non-Evil)
   - Test with Giant Eagle (INT 8... wait, that's 4+)
   - Test with Dire Wolf (INT 3, Unaligned)
   - Verify: Nature + Survival + 1 from [Medicine, Insight, Persuasion, Intimidation]
   - Verify: No disadvantage

4. **Simple Evil** (Intelligence 3 or less, Evil)
   - Test with Zombie (INT 3, Neutral Evil)
   - Verify: Nature + Survival + 1 from [Insight, Persuasion, Intimidation]
   - Verify: No Medicine option
   - Verify: ALL checks have disadvantage

#### Edge Cases
- Test INT exactly 3 (should use simple rules)
- Test INT exactly 4 (should use intelligent rules)
- Test neutral alignment (should NOT trigger evil rules)
- Test "Neutral Evil" alignment (should trigger evil rules)
- Test unaligned creatures (should treat as non-evil)
- Test missing intelligence stat (default to 10)
- Test mixed-alignment encounters (use most powerful monster)

#### Disadvantage Mechanics
- First-check disadvantage: Roll 2d20, verify lower is used
- All-checks disadvantage: Verify all 6 potential rolls use disadvantage
- No disadvantage: Verify only 1d20 rolled
- Verify disadvantage displayed in UI warning
- Verify disadvantage logged correctly

## Success Metrics

### Functional Requirements
- [DONE] Encounter options dialog appears before combat
- [DONE] Parlay option only available for non-evil monsters
- [DONE] Stealth option only available with proficiency
- [DONE] XP awards match specification (50%, 33%)
- [DONE] Failed parlay transitions to normal combat
- [DONE] Failed stealth triggers normal combat
- [DONE] All outcomes properly logged

### User Experience
- [DONE] Clear indication of available options
- [DONE] XP rewards displayed upfront
- [DONE] Risk/reward clearly communicated
- [DONE] Detailed feedback in log panel
- [DONE] Smooth transitions between states
- [DONE] No UI freezing or delays

### Technical Quality
- [DONE] All regression tests pass
- [DONE] New tests achieve >90% coverage
- [DONE] Database migrations run cleanly
- [DONE] No memory leaks from widgets
- [DONE] Configuration system integrated

## Risk Analysis

### High Risk
1. **Parlay Disadvantage Implementation**: Initiative system may need modifications to support disadvantage
   - **Mitigation**: Add `_parlay_failed_disadvantage` flag, check during initiative roll

2. **Widget Cleanup**: Skill challenge widget must be properly disposed
   - **Mitigation**: Use existing `_cleanup_encounter_widgets()` pattern

### Medium Risk
1. **Dialog Blocking**: Modal dialog may interfere with encounter flow
   - **Mitigation**: Use non-modal if issues arise, emit signals for selection

2. **XP Calculation Edge Cases**: Empty monster lists, null XP values
   - **Mitigation**: Add defensive checks, default to 0 XP

### Low Risk
1. **UI Layout**: Dialog may need adjustments for different screen sizes
   - **Mitigation**: Use flexible layouts, test on 1920x1080 target

## Future Enhancements

### Post-MVP Features
1. **Intimidation Option**: Threaten monsters to flee (WIS save)
2. **Bribery System**: Offer gold/items to avoid combat
3. **Animal Handling**: Befriend beast-type creatures
4. **Reputation System**: Track parlay history, affects future attempts
5. **Group Stealth**: Support for party-based stealth (multiplayer prep)
6. **Parlay Dialogue Trees**: More complex negotiation options
7. **Monster Memory**: Remember which monster types accept parlay
8. **Achievement Tracking**: "Pacifist" runs, stealth master, etc.

## Documentation Updates Required

### Files to Update
- `CLAUDE.md` - Add non-combat resolution section
- `README.md` - Feature list update
- `docs/ENCOUNTER_SYSTEM.md` - Full flow documentation
- `docs/TESTING_GUIDE.md` - New test procedures

### New Documentation
- `docs/NON_COMBAT_RESOLUTION_GUIDE.md` - Player-facing guide
- `docs/PARLAY_SYSTEM_SPEC.md` - Technical specification
- `docs/STEALTH_MECHANICS.md` - Stealth system deep dive

## Conclusion

This implementation plan leverages the existing backend systems (`ParlaySystem`, `EncounterAvoidanceSystem`, `SkillChallengeManager`) while significantly enhancing the parlay system with intelligence and alignment-based mechanics.

### What Already Exists (Tested & Working)
- [YES] **Skill Challenge System** - Complete and accessible (standalone encounter type)
- [YES] **Skill Challenge Widget** - Complete UI component that can be reused for parlay
- [YES] **Encounter Avoidance System** - Complete backend, no UI
- [YES] **Basic Parlay System** - Complete backend, needs enhancement + UI integration

### What Needs to Be Built

#### Backend Enhancements
1. **ParlaySystem Service** - Add intelligence/alignment-based skill selection
2. **SkillChallengeWidget** - Add disadvantage support for checks

#### New UI Components
1. **EncounterOptionsDialog** - Pre-combat decision interface
2. **Encounter Panel Integration** - Wire up parlay and stealth flows

### Key Implementation Changes from Original Design

**Original Parlay Design**:
- Simple: 3 CHA skills + 1 INT/WIS skill
- No disadvantage mechanics
- No intelligence consideration

**Enhanced Parlay Design** (Current):
- **4 distinct parlay categories** based on monster intelligence and alignment
- **Disadvantage mechanics**: First-check or all-checks based on danger level
- **Thematic skill selection**:
  - Diplomatic talks for intelligent non-evil
  - Dangerous negotiations for intelligent evil
  - Animal handling for simple non-evil
  - Desperate parlays for simple evil

### Development Estimates

| Component | Complexity | Time Estimate | Risk |
|-----------|-----------|---------------|------|
| Parlay Enhancement | Medium | 1 week | Low |
| Skill Widget Disadvantage | Low | 1 week | Low |
| Encounter Options Dialog | Medium | 1 week | Low |
| Integration & Testing | Medium | 2 weeks | Low |
| Stealth Integration | Low | 1 week | Very Low |
| Database & Analytics | Low | 1 week | Very Low |

**Total Estimated Development Time**: 6-7 weeks
**Complexity**: Medium (significant backend enhancement required)
**Impact**: Very High (adds rich tactical variety with meaningful monster differences)
**Risk**: Low-Medium (new disadvantage mechanics need careful testing)

### Why This Design is Better

1. **Thematic Depth**: Intelligent evil creatures require different approach than beasts
2. **Risk/Reward Balance**: Evil creatures harder to parlay with (disadvantage) but worth trying
3. **Character Build Variety**:
   - Nature/Survival builds can handle beasts
   - Social builds excel with intelligent creatures
   - All builds struggle with evil creatures
4. **D&D Authenticity**: Intelligence and alignment matter mechanically
5. **Emergent Gameplay**: Players learn which creatures to parlay with vs avoid vs fight

### Critical Path

```
Week 1: Parlay Service Enhancement
  |-> Week 2: Skill Widget Disadvantage
      |-> Week 3: Encounter Options Dialog
          |-> Week 4: Parlay Integration & Testing
              |-> Week 5: Stealth Integration
                  |-> Week 6-7: Polish & Analytics
```

**First Playable Milestone**: End of Week 4 (Parlay system fully functional)
**Feature Complete**: End of Week 5 (All three systems accessible)
**Polished Release**: End of Week 7 (Analytics, configuration, comprehensive testing)