# Parlay System - Detailed Implementation Guide

## Overview

This document provides complete implementation details for the non-combat encounter resolution system, focusing on:
1. Parlay System Enhancement (intelligence/alignment-based)
2. Disadvantage Support (using existing AdvantageSystem)
3. Influence Button Integration
4. Pickpocket Action Card

## Component 1: Parlay System Enhancement

### Monster Alignment Logic

**Rule**: Creatures with "any" alignment have 1/3 chance of being evil, otherwise non-evil.

**Implementation Location**: `src/talekeeper/services/parlay_system.py`

```python
def _determine_if_evil(self, alignment: str) -> bool:
    """
    Determine if a creature is evil based on alignment.

    Rules:
    - "any" alignment = 1/3 chance of being evil
    - Otherwise check if "evil" in alignment string

    Args:
        alignment: Monster alignment string

    Returns:
        True if evil, False if not evil
    """
    if not alignment:
        return False

    alignment_lower = alignment.strip().lower()

    # Handle "any" alignment - random chance
    if alignment_lower == "any":
        return random.random() < 0.33  # 1/3 chance of evil

    # Check for evil keyword
    return 'evil' in alignment_lower
```

### Intelligence & Alignment-Based Skill Selection

**Monster Categories**:
1. **Intelligent Non-Evil** (INT 4+, non-evil) - Diplomatic
2. **Intelligent Evil** (INT 4+, evil) - Dangerous
3. **Simple Non-Evil** (INT ≤3, non-evil) - Animal Handling
4. **Simple Evil** (INT ≤3, evil) - Desperate

**File**: `src/talekeeper/services/parlay_system.py`

**Add after line 74** (after current `get_parlay_skills()`):

```python
def get_parlay_skills_for_encounter(self, monsters: List[Dict]) -> Tuple[List[str], str]:
    """
    Get parlay skills based on monster intelligence and alignment.

    Uses the most powerful monster to determine parlay type.

    Returns:
        Tuple of (skills_list, disadvantage_mode)
        disadvantage_mode: 'none', 'first', 'all'

    Examples:
        - Centaur (INT 9, Neutral Good) -> 2 CHA + 1 INT/WIS, no disadvantage
        - Mind Flayer (INT 19, Lawful Evil) -> Deception + Intimidation + random, first disadvantage
        - Dire Wolf (INT 3, Unaligned) -> Nature + Survival + random, no disadvantage
        - Zombie (INT 3, Neutral Evil) -> Nature + Survival + random, all disadvantage
    """
    if not monsters:
        return [], 'none'

    # Use most powerful monster for parlay determination
    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))

    # Get monster characteristics
    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', '')

    # Determine if evil (handles "any" alignment)
    is_evil = self._determine_if_evil(alignment)

    # Determine parlay category and return skills + disadvantage mode
    if intelligence >= 4:
        if not is_evil:
            # Intelligent Non-Evil: Diplomatic negotiation
            return self._get_intelligent_non_evil_skills(), 'none'
        else:
            # Intelligent Evil: Dangerous negotiation
            return self._get_intelligent_evil_skills(), 'first'
    else:
        if not is_evil:
            # Simple Non-Evil: Animal handling
            return self._get_simple_non_evil_skills(), 'none'
        else:
            # Simple Evil: Desperate parlay
            return self._get_simple_evil_skills(), 'all'

def _get_intelligent_non_evil_skills(self) -> List[str]:
    """
    Skills for intelligent non-evil creatures (diplomatic negotiation).

    Selection: 2 random CHA skills + 1 random INT/WIS skill
    """
    cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
    int_wis_skills = [
        'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
        'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival'
    ]

    # Select 2 random CHA skills
    selected_cha = random.sample(cha_skills, 2)

    # Select 1 random INT/WIS skill
    selected_int_wis = random.choice(int_wis_skills)

    return selected_cha + [selected_int_wis]

def _get_intelligent_evil_skills(self) -> List[str]:
    """
    Skills for intelligent evil creatures (dangerous negotiation).

    Selection: Deception + Intimidation + 1 random (any skill or tool)
    """
    # All skills (excluding Deception and Intimidation which are fixed)
    all_skills = [
        'Athletics', 'Acrobatics', 'Sleight of Hand', 'Stealth',
        'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
        'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival',
        'Performance', 'Persuasion'
    ]

    # Tool proficiencies can also be required
    tool_proficiencies = [
        "Thieves' Tools", "Smith's Tools", "Brewer's Supplies",
        "Alchemist's Supplies", "Carpenter's Tools", "Cartographer's Tools",
        "Gaming Set (Dice)", "Gaming Set (Cards)", "Gaming Set (Dragonchess)",
        "Herbalism Kit", "Navigator's Tools", "Poisoner's Kit"
    ]

    # Combine all options
    all_options = all_skills + tool_proficiencies

    # Select 1 random skill/tool
    random_selection = random.choice(all_options)

    return ['Deception', 'Intimidation', random_selection]

def _get_simple_non_evil_skills(self) -> List[str]:
    """
    Skills for simple non-evil creatures (animal handling).

    Selection: Nature + Survival + 1 from limited pool
    """
    limited_pool = ['Medicine', 'Insight', 'Persuasion', 'Intimidation']

    random_skill = random.choice(limited_pool)

    return ['Nature', 'Survival', random_skill]

def _get_simple_evil_skills(self) -> List[str]:
    """
    Skills for simple evil creatures (desperate parlay).

    Selection: Nature + Survival + 1 from very limited pool
    Note: No Medicine option (evil creatures won't respond to care)
    """
    very_limited_pool = ['Insight', 'Persuasion', 'Intimidation']

    random_skill = random.choice(very_limited_pool)

    return ['Nature', 'Survival', random_skill]
```

### Update create_parlay_challenge() Method

**Modify existing method** (line 88-160) to use enhanced skill selection:

**REPLACE** line 96:
```python
# OLD:
parlay_skills = self.get_parlay_skills()

# NEW:
parlay_skills, disadvantage_mode = self.get_parlay_skills_for_encounter(monsters)

if not parlay_skills:
    return None
```

**ADD** after line 108 (after template_description):
```python
# Add disadvantage mode to description
if disadvantage_mode == 'first':
    template_description += "\n\nWARNING: First skill check at DISADVANTAGE"
elif disadvantage_mode == 'all':
    template_description += "\n\nWARNING: ALL skill checks at DISADVANTAGE"
```

**ADD** metadata storage for disadvantage mode (after line 143, before commit):
```python
# Store disadvantage mode in template metadata
cursor.execute('''
    INSERT OR REPLACE INTO skill_challenge_metadata
    (template_id, metadata_key, metadata_value)
    VALUES (?, 'disadvantage_mode', ?)
''', (template_id, disadvantage_mode))
```

**Database Schema Addition**:
```sql
-- Run this migration to add metadata table
CREATE TABLE IF NOT EXISTS skill_challenge_metadata (
    template_id TEXT NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    PRIMARY KEY (template_id, metadata_key),
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id) ON DELETE CASCADE
);
```

---

## Component 2: Disadvantage Support

### Leveraging Existing AdvantageSystem

**Location**: `src/talekeeper/services/advantage_system.py` (already exists)

**Key Classes/Methods**:
- `AdvantageState.DISADVANTAGE` - enum value
- `AdvantageSystem.roll_d20_with_advantage(advantage_state, modifier)` - returns (total, breakdown)

### Modify SkillChallengeManager

**File**: `src/talekeeper/services/skill_challenge_manager.py`

**UPDATE** `attempt_skill()` method (line 245) to support disadvantage:

**BEFORE** (line 262-264):
```python
# Roll d20
roll_result = random.randint(1, 20)
total_result = roll_result + ability_modifier + proficiency_bonus
```

**AFTER**:
```python
# Get disadvantage mode from session metadata
disadvantage_mode = self._get_session_disadvantage_mode(session_id)
skill_usage_count = session.skill_usage.get(skill_name, 0)

# Determine if this check has disadvantage
has_disadvantage = False
if disadvantage_mode == 'all':
    has_disadvantage = True
elif disadvantage_mode == 'first' and skill_usage_count == 0:
    # First use of this specific skill
    has_disadvantage = True

# Roll d20 using advantage system
from talekeeper.services.advantage_system import AdvantageSystem, AdvantageState

if has_disadvantage:
    advantage_state = AdvantageState.DISADVANTAGE
else:
    advantage_state = AdvantageState.NORMAL

# Roll with advantage system
total_modifier = ability_modifier + proficiency_bonus
roll_result, breakdown = AdvantageSystem.roll_d20_with_advantage(
    advantage_state,
    total_modifier
)

# Extract d20 result for logging
d20_result = breakdown['d20_result']
total_result = breakdown['total']

# Store roll details for display
roll_breakdown = breakdown
```

**ADD** helper method to SkillChallengeManager:

```python
def _get_session_disadvantage_mode(self, session_id: str) -> str:
    """
    Get disadvantage mode for a session from template metadata.

    Returns:
        'none', 'first', or 'all'
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get template_id from session
        cursor.execute('''
            SELECT template_id FROM skill_challenge_sessions WHERE id = ?
        ''', (session_id,))

        result = cursor.fetchone()
        if not result:
            return 'none'

        template_id = result[0]

        # Get disadvantage_mode from metadata
        cursor.execute('''
            SELECT metadata_value FROM skill_challenge_metadata
            WHERE template_id = ? AND metadata_key = 'disadvantage_mode'
        ''', (template_id,))

        result = cursor.fetchone()
        return result[0] if result else 'none'

    except Exception as e:
        print(f"Error getting disadvantage mode: {e}")
        return 'none'
    finally:
        if conn:
            conn.close()
```

**UPDATE** SkillAttemptResult dataclass to include breakdown:

**Location**: Top of `skill_challenge_manager.py` (around line 60)

**MODIFY** SkillAttemptResult:
```python
@dataclass
class SkillAttemptResult:
    skill_name: str
    dc: int
    roll_result: int  # This becomes the d20 result only
    ability_modifier: int
    proficiency_bonus: int
    total_result: int
    success: bool
    session_complete: bool
    final_outcome: Optional[str] = None

    # NEW: Add roll breakdown
    roll_breakdown: Optional[Dict[str, Any]] = None
```

**UPDATE** return statement in `attempt_skill()` to include breakdown:

```python
return SkillAttemptResult(
    skill_name=skill_name,
    dc=dc,
    roll_result=d20_result,  # Changed to d20_result
    ability_modifier=ability_modifier,
    proficiency_bonus=proficiency_bonus,
    total_result=total_result,
    success=success,
    session_complete=session_complete,
    final_outcome=final_outcome,
    roll_breakdown=roll_breakdown  # NEW
)
```

### Update SkillChallengeWidget Display

**File**: `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

**UPDATE** `display_attempt_result()` method (line 246) to show disadvantage:

**REPLACE** the method:
```python
def display_attempt_result(self, result: SkillAttemptResult):
    """Display the result of a skill attempt with disadvantage support."""
    outcome = "SUCCESS" if result.success else "FAILURE"
    color = "#4CAF50" if result.success else "#f44336"

    # Build roll description
    if result.roll_breakdown:
        breakdown = result.roll_breakdown

        if breakdown['type'] == 'disadvantage':
            rolls = breakdown['rolls']
            roll_desc = f"d20({rolls[0]}, {rolls[1]}) DISADVANTAGE = {breakdown['d20_result']}"
        elif breakdown['type'] == 'advantage':
            rolls = breakdown['rolls']
            roll_desc = f"d20({rolls[0]}, {rolls[1]}) ADVANTAGE = {breakdown['d20_result']}"
        else:
            roll_desc = f"d20({breakdown['d20_result']})"
    else:
        # Fallback if no breakdown
        roll_desc = f"d20({result.roll_result})"

    result_text = (
        f"<div style='color: {color}; font-weight: bold;'>"
        f"{result.skill_name} (DC {result.dc}): {outcome}</div>"
        f"Roll: {roll_desc} + {result.ability_modifier} (ability) + "
        f"{result.proficiency_bonus} (proficiency) = {result.total_result}"
    )

    self.results_text.append(result_text)

    # Auto-scroll to bottom
    cursor = self.results_text.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    self.results_text.setTextCursor(cursor)
```

---

## Component 3: Influence Button Integration

### Wire Influence Button to Parlay System

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**Step 1: Add Signal Handler**

**Find** the signal connection (around line 700-701):
```python
self.influence_btn.clicked.connect(lambda: self.exploration_action.emit("influence"))
```

**ADD** signal handler connection in `__init__` method:
```python
# Connect exploration actions
self.exploration_action.connect(self._handle_exploration_action)
```

**Step 2: Create Handler Method**

**ADD** new method (add after encounter generation methods, around line 4900):

```python
def _handle_exploration_action(self, action: str):
    """
    Handle exploration button actions.

    Args:
        action: Action type ('influence', 'study', etc.)
    """
    if action == "influence":
        self._attempt_parlay()
    # Other actions already have dedicated handlers

def _attempt_parlay(self):
    """
    Attempt to parlay with encounter monsters using Influence button.

    Flow:
    1. Check if encounter exists
    2. Check if parlay is possible
    3. Determine parlay type (intelligence/alignment)
    4. Create skill challenge with disadvantage mode
    5. Show skill challenge widget
    """
    from talekeeper.services.parlay_system import ParlaySystem

    # Validate encounter exists
    if not self.encounter_instances:
        self._log_monster_action("[PARLAY] No active encounter to negotiate with")
        return

    # Get character data
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

    # Get primary monster for logging
    primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))
    intelligence = primary_monster.get('intelligence', 10)
    alignment = primary_monster.get('alignment', 'neutral')
    is_evil = parlay_system._determine_if_evil(alignment)

    # Determine parlay type for display
    if intelligence >= 4 and not is_evil:
        parlay_type = "Diplomatic Negotiation"
        parlay_desc = "Intelligent non-evil creature - standard negotiation"
    elif intelligence >= 4 and is_evil:
        parlay_type = "Dangerous Negotiation"
        parlay_desc = "Intelligent evil creature - first check at disadvantage"
    elif intelligence <= 3 and not is_evil:
        parlay_type = "Animal Handling"
        parlay_desc = "Simple non-evil creature - animal handling approach"
    else:
        parlay_type = "Desperate Parlay"
        parlay_desc = "Simple evil creature - all checks at disadvantage"

    # Log parlay attempt
    monster_names = ', '.join([m.get('name', 'Unknown') for m in monsters[:3]])
    self._log_monster_action(f"[PARLAY] Attempting {parlay_type}")
    self._log_monster_action(f"[PARLAY] Target: {monster_names}")
    self._log_monster_action(f"[PARLAY] INT: {intelligence}, Alignment: {alignment}")
    self._log_monster_action(f"[PARLAY] {parlay_desc}")

    # Get skills and disadvantage mode
    skills, disadvantage_mode = parlay_system.get_parlay_skills_for_encounter(monsters)

    if not skills:
        self._log_monster_action("[PARLAY] Failed to determine parlay skills")
        return

    # Log skill requirements
    skills_text = ', '.join(skills)
    if disadvantage_mode == 'first':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text}")
        self._log_monster_action(f"[PARLAY] WARNING: First skill check at DISADVANTAGE")
    elif disadvantage_mode == 'all':
        self._log_monster_action(f"[PARLAY] Skills: {skills_text}")
        self._log_monster_action(f"[PARLAY] WARNING: ALL skill checks at DISADVANTAGE")
    else:
        self._log_monster_action(f"[PARLAY] Skills: {skills_text}")

    # Calculate potential XP reward
    xp_reward = parlay_system.calculate_parlay_xp_reward(monsters)
    self._log_monster_action(f"[PARLAY] Potential reward: {xp_reward} XP (50% of strongest)")

    # Create parlay skill challenge
    session_id = parlay_system.create_parlay_challenge(character_id, monsters)

    if not session_id:
        self._log_monster_action("[PARLAY] Failed to create parlay challenge")
        return

    # Get session from skill challenge manager
    from talekeeper.services.skill_challenge_manager import SkillChallengeManager
    skill_manager = SkillChallengeManager('talekeeper.db')
    session = skill_manager.get_active_session(character_id)

    if not session:
        self._log_monster_action("[PARLAY] Failed to load parlay session")
        return

    # Show skill challenge widget
    self._show_parlay_skill_challenge(session, xp_reward)

def _show_parlay_skill_challenge(self, session, xp_reward: int):
    """
    Display skill challenge widget for parlay.

    Args:
        session: SkillChallengeSession object
        xp_reward: XP reward for success
    """
    # Hide monster cards during parlay
    if hasattr(self, 'monsters_frame') and self.monsters_frame:
        self.monsters_frame.setVisible(False)

    # Create skill challenge widget
    self.skill_challenge_widget = SkillChallengeWidget(self)
    self.skill_challenge_widget.set_character_data(self._get_current_character_data())

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
    """
    Handle parlay skill challenge completion.

    Args:
        outcome: 'success' or 'failure'
        reward_text: Text description of outcome
        xp_reward: XP amount for success
    """
    from talekeeper.services.parlay_system import ParlaySystem

    character_data = self._get_current_character_data()
    if not character_data:
        return

    parlay_system = ParlaySystem('talekeeper.db')

    if outcome == 'success':
        # Peaceful resolution - award XP
        self._log_monster_action(f"[PARLAY SUCCESS] {reward_text}")

        # Apply XP reward
        result = parlay_system.apply_parlay_success(character_data['id'], xp_reward)
        self._log_monster_action(f"[XP] {result['message']}")

        # Update character display
        character_data['experience_points'] += xp_reward
        if hasattr(self, 'parent') and hasattr(self.parent(), 'character_sheet'):
            self.parent().character_sheet.load_character(character_data['id'])

        # Clear encounter
        self._clear_monster_cards()

        # Update scene description
        self.update_scene_description(
            "The creatures accept your diplomatic terms and depart peacefully. "
            "You gained experience through negotiation rather than violence."
        )

        # Check for pickpocket opportunity
        self._check_pickpocket_opportunity()

    elif outcome == 'failure':
        # Negotiations failed - combat begins
        self._log_monster_action(f"[PARLAY FAILURE] {reward_text}")
        self._log_monster_action("[COMBAT] Negotiations break down - combat begins!")

        # Show monsters and start combat
        if hasattr(self, 'monsters_frame') and self.monsters_frame:
            self.monsters_frame.setVisible(True)

        self.set_encounter_mode()

    # Clean up skill challenge widget
    if hasattr(self, 'skill_challenge_widget') and self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget.deleteLater()
        self.skill_challenge_widget = None

def _on_parlay_refused(self, refuse_cost: str):
    """Handle parlay refusal."""
    self._log_monster_action("[PARLAY REFUSED] You decide not to negotiate")
    self._log_monster_action("[ENCOUNTER] The creatures remain, uncertain of your intentions")

    # Show monsters again but don't start combat
    if hasattr(self, 'monsters_frame') and self.monsters_frame:
        self.monsters_frame.setVisible(True)

    # Clean up widget
    if hasattr(self, 'skill_challenge_widget') and self.skill_challenge_widget:
        self.skill_challenge_widget.setParent(None)
        self.skill_challenge_widget.deleteLater()
        self.skill_challenge_widget = None
```

---

## Component 4: Pickpocket Action Card

### Check Pickpocket Opportunity

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**ADD** method after `_on_parlay_completed`:

```python
def _check_pickpocket_opportunity(self):
    """
    Check if character can pickpocket after successful parlay.

    Requires both Deception and Sleight of Hand proficiency.
    """
    from talekeeper.services.parlay_system import ParlaySystem

    character_data = self._get_current_character_data()
    if not character_data:
        return

    # Store monsters for pickpocket action card
    if hasattr(self, 'encounter_instances') and self.encounter_instances:
        self._parlay_monsters = [inst.to_dict() for inst in self.encounter_instances.values()]
    else:
        return

    parlay_system = ParlaySystem('talekeeper.db')
    can_pickpocket, reason = parlay_system.can_pickpocket(character_data['id'])

    if can_pickpocket:
        self._log_monster_action("[PICKPOCKET] You notice an opportunity...")
        self._log_monster_action(f"[PICKPOCKET] {reason}")
        self._log_monster_action("[PICKPOCKET] Check your action cards for 'Pickpocket' ability")

        # Signal action panel to add pickpocket card
        # This will be handled in action panel implementation
    else:
        # Clear stored monsters - no pickpocket opportunity
        if hasattr(self, '_parlay_monsters'):
            delattr(self, '_parlay_monsters')
```

### Add Pickpocket Methods to ParlaySystem

**File**: `src/talekeeper/services/parlay_system.py`

**ADD** at end of class:

```python
def can_pickpocket(self, character_id: str) -> Tuple[bool, str]:
    """
    Check if character can attempt pickpocketing.

    Requires BOTH Deception AND Sleight of Hand proficiency.

    Args:
        character_id: Character ID

    Returns:
        Tuple of (can_pickpocket, reason)
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get character skill proficiencies
        cursor.execute('''
            SELECT skill_name FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill'
        ''', (character_id,))

        proficiencies = [row[0] for row in cursor.fetchall()]

        has_deception = 'Deception' in proficiencies
        has_sleight = 'Sleight of Hand' in proficiencies

        if has_deception and has_sleight:
            return True, "You can attempt to pickpocket during negotiation"
        elif has_deception:
            return False, "Need Sleight of Hand proficiency to pickpocket"
        elif has_sleight:
            return False, "Need Deception proficiency to pickpocket"
        else:
            return False, "Need both Deception and Sleight of Hand proficiencies to pickpocket"

    except Exception as e:
        print(f"Error checking pickpocket eligibility: {e}")
        return False, "Error checking proficiencies"
    finally:
        if conn:
            conn.close()

def calculate_pickpocket_loot(self, monsters: List[Dict]) -> int:
    """
    Calculate gold from pickpocketing.

    Formula: Roll 1d4 per monster CR (minimum 1 die)

    Args:
        monsters: List of monster dictionaries

    Returns:
        Total gold stolen
    """
    total_gold = 0

    for monster in monsters:
        cr = monster.get('challenge_rating', 0)

        # Convert CR to integer (CR 1/4 = 0, CR 1/2 = 0, CR 1+ = value)
        if isinstance(cr, str):
            if '/' in cr:
                cr_value = 0  # Fractional CR
            else:
                cr_value = int(float(cr))
        else:
            cr_value = int(cr) if cr else 0

        # Minimum 1 die per monster
        dice_count = max(1, cr_value)

        # Roll 1d4 per CR
        for _ in range(dice_count):
            total_gold += random.randint(1, 4)

    return total_gold

def execute_pickpocket_attempt(self, character_id: str, monsters: List[Dict], character_data: Dict) -> Dict:
    """
    Execute pickpocket attempt.

    Args:
        character_id: Character ID
        monsters: List of monsters
        character_data: Character stat dict

    Returns:
        Dict with success, gold_stolen, total_roll, dc, message
    """
    from talekeeper.services.proficiency_bonus import get_proficiency_bonus

    # Get character stats
    dex_mod = (character_data.get('dexterity', 10) - 10) // 2
    prof_bonus = get_proficiency_bonus(character_data.get('level', 1))

    # Roll Sleight of Hand with advantage system
    from talekeeper.services.advantage_system import AdvantageSystem, AdvantageState, RollType

    context = {
        'character_id': character_id,
        'skill_name': 'Sleight of Hand'
    }

    # Get advantage/disadvantage sources (conditions, etc.)
    advantage_sources = AdvantageSystem.get_common_advantage_sources(RollType.SKILL_CHECK, context)
    disadvantage_sources = AdvantageSystem.get_common_disadvantage_sources(RollType.SKILL_CHECK, context)

    advantage_state = AdvantageSystem.calculate_advantage_state(advantage_sources, disadvantage_sources)

    # Roll
    total_modifier = dex_mod + prof_bonus
    total_roll, breakdown = AdvantageSystem.roll_d20_with_advantage(advantage_state, total_modifier)

    # DC = 10 + average monster Perception (assume 10 for most monsters)
    avg_monster_perception = 10
    dc = 10 + avg_monster_perception

    # Check success
    success = total_roll >= dc

    if success:
        gold_stolen = self.calculate_pickpocket_loot(monsters)

        # Award gold to character
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE characters
                SET gold = gold + ?
                WHERE id = ?
            ''', (gold_stolen, character_id))

            conn.commit()

        except Exception as e:
            print(f"Error awarding gold: {e}")
            gold_stolen = 0
        finally:
            if conn:
                conn.close()

        return {
            'success': True,
            'gold_stolen': gold_stolen,
            'total_roll': total_roll,
            'dc': dc,
            'breakdown': breakdown,
            'message': f"Successfully pickpocketed {gold_stolen} gold!"
        }
    else:
        return {
            'success': False,
            'gold_stolen': 0,
            'total_roll': total_roll,
            'dc': dc,
            'breakdown': breakdown,
            'message': "Pickpocket attempt failed - you were detected!"
        }
```

### Create Pickpocket Action Card

**File**: `src/talekeeper/ui/action_cards/action_panel.py`

**FIND** where action cards are generated (search for `_create_action_cards` or similar)

**ADD** pickpocket card check:

```python
def _check_for_pickpocket_card(self) -> Optional[ActionCard]:
    """
    Check if pickpocket action card should be available.

    Appears after successful parlay if character has Deception + Sleight of Hand.
    """
    from talekeeper.services.parlay_system import ParlaySystem

    # Check if encounter panel has parlay monsters stored
    if not hasattr(self.parent(), 'encounter_panel'):
        return None

    encounter_panel = self.parent().encounter_panel

    if not hasattr(encounter_panel, '_parlay_monsters'):
        return None

    # Check if character can pickpocket
    parlay_system = ParlaySystem('talekeeper.db')
    character_id = self.character_data['id']

    can_pickpocket, reason = parlay_system.can_pickpocket(character_id)
    if not can_pickpocket:
        return None

    # Get DEX modifier for display
    dex_mod = (self.character_data.get('dexterity', 10) - 10) // 2
    from talekeeper.services.proficiency_bonus import get_proficiency_bonus
    prof_bonus = get_proficiency_bonus(self.character_data.get('level', 1))

    total_bonus = dex_mod + prof_bonus
    bonus_text = f"+{total_bonus}" if total_bonus >= 0 else str(total_bonus)

    # Create pickpocket action card
    card = ActionCard(
        name="Pickpocket",
        action_type="action",
        description=(
            f"Attempt to steal gold from creatures during parlay\n\n"
            f"Sleight of Hand check: {bonus_text}\n"
            f"DC: 20 (10 + monster Perception)\n\n"
            f"SUCCESS: Steal 1d4 gold per monster CR\n"
            f"FAILURE: Detected - negotiations fail, combat begins"
        ),
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

    # Execute pickpocket
    result = parlay_system.execute_pickpocket_attempt(
        self.character_data['id'],
        monsters,
        self.character_data
    )

    # Log the attempt
    breakdown = result.get('breakdown', {})

    if breakdown.get('type') == 'disadvantage':
        rolls = breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand (DISADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {breakdown['d20_result']}"
        )
    elif breakdown.get('type') == 'advantage':
        rolls = breakdown['rolls']
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand (ADVANTAGE): "
            f"d20({rolls[0]}, {rolls[1]}) = {breakdown['d20_result']}"
        )
    else:
        self._log_action(
            f"[PICKPOCKET] Sleight of Hand: d20({breakdown.get('d20_result', '?')})"
        )

    self._log_action(f"[PICKPOCKET] Total: {result['total_roll']} vs DC {result['dc']}")

    if result['success']:
        # Success
        self._log_action(f"[PICKPOCKET SUCCESS] {result['message']}")

        # Update character display
        if hasattr(self.parent(), 'character_sheet'):
            self.parent().character_sheet.load_character(self.character_data['id'])

        # Clean up - remove pickpocket opportunity
        if hasattr(encounter_panel, '_parlay_monsters'):
            delattr(encounter_panel, '_parlay_monsters')

        # Remove pickpocket card
        self._refresh_action_cards()

    else:
        # Failure - detected!
        self._log_action(f"[PICKPOCKET FAILED] {result['message']}")
        self._log_action("[COMBAT] The creatures attack!")

        # Restore monsters and start combat
        encounter_panel._restore_parlay_monsters_for_combat()
        encounter_panel.set_encounter_mode()

        # Clean up
        if hasattr(encounter_panel, '_parlay_monsters'):
            delattr(encounter_panel, '_parlay_monsters')

        # Remove pickpocket card
        self._refresh_action_cards()
```

### Restore Monsters for Combat After Failed Pickpocket

**File**: `src/talekeeper/ui/encounter_pane/encounter_panel.py`

**ADD** method:

```python
def _restore_parlay_monsters_for_combat(self):
    """
    Restore monsters from parlay attempt for combat.

    Called when pickpocket fails or parlay breaks down.
    """
    if not hasattr(self, '_parlay_monsters'):
        return

    # Recreate monster cards from stored data
    # This assumes monsters were cleared after parlay success
    # and need to be restored for combat

    self._log_monster_action("[COMBAT] Restoring encounter...")

    # Show monsters frame
    if hasattr(self, 'monsters_frame') and self.monsters_frame:
        self.monsters_frame.setVisible(True)

    # Note: Monster cards should still exist in encounter_instances
    # This just makes them visible again
```

---

## Testing Checklist

### Parlay System
- [ ] Test Intelligent Non-Evil (Centaur) - 2 CHA + 1 INT/WIS, no disadvantage
- [ ] Test Intelligent Evil (Mind Flayer) - Deception + Intimidation + random, first disadvantage
- [ ] Test Simple Non-Evil (Dire Wolf) - Nature + Survival + random, no disadvantage
- [ ] Test Simple Evil (Zombie) - Nature + Survival + random, all disadvantage
- [ ] Test "any" alignment creatures (1/3 evil chance)
- [ ] Test INT exactly 3 (should use simple rules)
- [ ] Test INT exactly 4 (should use intelligent rules)

### Disadvantage System
- [ ] Verify disadvantage shows 2d20 rolls in log
- [ ] Verify "first" mode only affects first skill check
- [ ] Verify "all" mode affects all skill checks
- [ ] Verify disadvantage warning shows in UI

### UI Integration
- [ ] Influence button triggers parlay
- [ ] Parlay fails gracefully if no encounter
- [ ] Parlay shows correct monster info in log
- [ ] Skill challenge widget appears
- [ ] Success awards XP correctly
- [ ] Failure starts combat
- [ ] Refuse option works

### Pickpocket
- [ ] Only available with both proficiencies
- [ ] Shows in action cards after successful parlay
- [ ] Success awards gold (1d4 per CR)
- [ ] Failure triggers combat
- [ ] Card disappears after use

---

## Migration Scripts

### Database Migration

```sql
-- File: database/migrations/XXX_parlay_disadvantage_support.sql

-- Add metadata table for skill challenges
CREATE TABLE IF NOT EXISTS skill_challenge_metadata (
    template_id TEXT NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    PRIMARY KEY (template_id, metadata_key),
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id) ON DELETE CASCADE
);

-- Add gold column to characters if not exists
-- (This may already exist)
ALTER TABLE characters ADD COLUMN gold INTEGER DEFAULT 0;

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_skill_challenge_metadata_template
ON skill_challenge_metadata(template_id);
```

---

## Summary

This implementation:
1. ✅ Uses existing AdvantageSystem for disadvantage rolls
2. ✅ Leverages monster stats (intelligence, alignment) from database
3. ✅ Handles "any" alignment (1/3 evil chance)
4. ✅ Integrates with existing Influence button
5. ✅ Adds pickpocket as bonus feature for skilled characters
6. ✅ No Hero Mode changes (skipped as requested)

**Estimated Implementation Time**: 3-4 weeks
- Week 1: Parlay service enhancement + disadvantage support
- Week 2: UI integration + testing
- Week 3: Pickpocket system
- Week 4: Polish + regression testing
