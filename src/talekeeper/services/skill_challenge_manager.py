# core
# category: core
import sqlite3
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from uuid import uuid4
from datetime import datetime


@dataclass
class SkillChallengeTemplate:
    id: str
    name: str
    description: str
    base_dc: int
    skills: List[str] = field(default_factory=list)
    success_options: List[str] = field(default_factory=list)
    failure_options: List[str] = field(default_factory=list)
    refuse_options: List[str] = field(default_factory=list)


@dataclass
class SkillAttemptResult:
    skill_name: str
    dc: int
    roll_result: int
    ability_modifier: int
    proficiency_bonus: int
    total_result: int
    success: bool
    session_complete: bool = False
    final_outcome: Optional[str] = None
    roll_breakdown: Optional[str] = None


@dataclass
class SkillChallengeSession:
    id: str
    character_id: str
    template: SkillChallengeTemplate
    challenge_name: str
    base_dc: int
    successes: int = 0
    failures: int = 0
    skill_usage: Dict[str, int] = field(default_factory=dict)
    success_revealed: bool = True
    failure_revealed: bool = True
    is_active: bool = True
    selected_success: Optional[str] = None
    selected_failure: Optional[str] = None
    selected_refuse: Optional[str] = None


class SkillChallengeManager:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def get_all_templates(self) -> List[SkillChallengeTemplate]:
        """Load all skill challenge templates from talekeeper.database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT id, name, description, base_dc FROM skill_challenge_templates ORDER BY name')
            template_rows = cursor.fetchall()

            templates = []
            for template_row in template_rows:
                template_id, name, description, base_dc = template_row

                # Load skills
                cursor.execute('''
                    SELECT skill_name FROM skill_challenge_template_skills
                    WHERE template_id = ? ORDER BY skill_order
                ''', (template_id,))
                skills = [row[0] for row in cursor.fetchall()]

                # Load success options
                cursor.execute('''
                    SELECT success_option FROM skill_challenge_template_success
                    WHERE template_id = ?
                ''', (template_id,))
                success_options = [row[0] for row in cursor.fetchall()]

                # Load failure options
                cursor.execute('''
                    SELECT failure_option FROM skill_challenge_template_failure
                    WHERE template_id = ?
                ''', (template_id,))
                failure_options = [row[0] for row in cursor.fetchall()]

                # Load refuse options
                cursor.execute('''
                    SELECT refuse_option FROM skill_challenge_template_refuse
                    WHERE template_id = ?
                ''', (template_id,))
                refuse_options = [row[0] for row in cursor.fetchall()]

                template = SkillChallengeTemplate(
                    id=template_id,
                    name=name,
                    description=description or f"A skill challenge involving {', '.join(skills)}",
                    base_dc=base_dc,
                    skills=skills,
                    success_options=success_options,
                    failure_options=failure_options,
                    refuse_options=refuse_options
                )
                templates.append(template)

            return templates

        except Exception as e:
            print(f"Error loading skill challenge templates: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_template_by_id(self, template_id: str) -> Optional[SkillChallengeTemplate]:
        """Get a specific template by ID."""
        templates = self.get_all_templates()
        for template in templates:
            if template.id == template_id:
                return template
        return None

    def create_session(self, character_id: str, template: SkillChallengeTemplate) -> SkillChallengeSession:
        """Create a new skill challenge session."""
        session_id = str(uuid4())

        # Determine what information is revealed (based on requirements)
        success_revealed = random.random() < 0.75  # 75% chance success is revealed
        failure_revealed = random.random() < 0.50  # 50% chance failure is revealed

        # Pre-select the outcomes that will be used
        selected_success = random.choice(template.success_options) if template.success_options else None
        selected_failure = random.choice(template.failure_options) if template.failure_options else None
        selected_refuse = random.choice(template.refuse_options) if template.refuse_options else None

        session = SkillChallengeSession(
            id=session_id,
            character_id=character_id,
            template=template,
            challenge_name=template.name,
            base_dc=template.base_dc,
            success_revealed=success_revealed,
            failure_revealed=failure_revealed,
            selected_success=selected_success,
            selected_failure=selected_failure,
            selected_refuse=selected_refuse
        )

        # Save to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO skill_challenge_sessions
                (id, character_id, template_id, challenge_name, base_dc, current_successes,
                 current_failures, skill_usage_json, success_revealed, failure_revealed,
                 is_active, selected_success, selected_failure, selected_refuse)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id, session.character_id, template.id, session.challenge_name,
                session.base_dc, session.successes, session.failures,
                json.dumps(session.skill_usage), session.success_revealed,
                session.failure_revealed, session.is_active, session.selected_success,
                session.selected_failure, session.selected_refuse
            ))

            conn.commit()
            return session

        except Exception as e:
            print(f"Error creating skill challenge session: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_active_session(self, character_id: str) -> Optional[SkillChallengeSession]:
        """Get the active skill challenge session for a character."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, character_id, template_id, challenge_name, base_dc,
                       current_successes, current_failures, skill_usage_json,
                       success_revealed, failure_revealed, is_active,
                       selected_success, selected_failure, selected_refuse
                FROM skill_challenge_sessions
                WHERE character_id = ? AND is_active = 1
                ORDER BY started_at DESC LIMIT 1
            ''', (character_id,))

            row = cursor.fetchone()
            if not row:
                return None

            (session_id, char_id, template_id, challenge_name, base_dc,
             successes, failures, skill_usage_json, success_revealed,
             failure_revealed, is_active, selected_success, selected_failure,
             selected_refuse) = row

            # Load template
            template = self.get_template_by_id(template_id)
            if not template:
                return None

            skill_usage = json.loads(skill_usage_json) if skill_usage_json else {}

            session = SkillChallengeSession(
                id=session_id,
                character_id=char_id,
                template=template,
                challenge_name=challenge_name,
                base_dc=base_dc,
                successes=successes,
                failures=failures,
                skill_usage=skill_usage,
                success_revealed=bool(success_revealed),
                failure_revealed=bool(failure_revealed),
                is_active=bool(is_active),
                selected_success=selected_success,
                selected_failure=selected_failure,
                selected_refuse=selected_refuse
            )

            return session

        except Exception as e:
            print(f"Error getting active session: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_skill_dc(self, session: SkillChallengeSession, skill_name: str) -> int:
        """Calculate the DC for a skill based on usage count."""
        usage_count = session.skill_usage.get(skill_name, 0)
        return session.base_dc + usage_count

    def attempt_skill(self, session_id: str, skill_name: str, character_data: dict) -> SkillAttemptResult:
        """Attempt a skill check in the challenge."""
        from talekeeper.services.advantage_system import AdvantageSystem, AdvantageState

        session = self._get_session_by_id(session_id)
        if not session or not session.is_active:
            raise ValueError("Invalid or inactive session")

        if skill_name not in session.template.skills:
            raise ValueError(f"Skill {skill_name} not available for this challenge")

        dc = self.get_skill_dc(session, skill_name)

        ability_modifier, proficiency_bonus = self._get_skill_modifiers(skill_name, character_data)

        disadvantage_mode = self._get_session_disadvantage_mode(session.template.id)

        advantage_state = AdvantageState.NORMAL
        roll_breakdown = None

        if disadvantage_mode == 'first' and session.successes == 0 and session.failures == 0:
            advantage_state = AdvantageState.DISADVANTAGE
        elif disadvantage_mode == 'all':
            advantage_state = AdvantageState.DISADVANTAGE

        advantage_system = AdvantageSystem()
        roll_result, breakdown = advantage_system.roll_d20_with_advantage(advantage_state)

        if advantage_state != AdvantageState.NORMAL:
            roll_breakdown = breakdown

        total_result = roll_result + ability_modifier + proficiency_bonus
        success = total_result >= dc

        session.skill_usage[skill_name] = session.skill_usage.get(skill_name, 0) + 1

        if success:
            session.successes += 1
        else:
            session.failures += 1

        session_complete = False
        final_outcome = None

        if session.successes >= 3:
            session_complete = True
            final_outcome = 'success'
            session.is_active = False
        elif session.failures >= 3:
            session_complete = True
            final_outcome = 'failure'
            session.is_active = False

        self._save_attempt(session_id, skill_name, ability_modifier, proficiency_bonus,
                          dc, roll_result, total_result, success)

        self._update_session(session, final_outcome)

        return SkillAttemptResult(
            skill_name=skill_name,
            dc=dc,
            roll_result=roll_result,
            ability_modifier=ability_modifier,
            proficiency_bonus=proficiency_bonus,
            total_result=total_result,
            success=success,
            session_complete=session_complete,
            final_outcome=final_outcome,
            roll_breakdown=roll_breakdown
        )

    def refuse_challenge(self, session_id: str) -> str:
        """Refuse the challenge and return the refuse outcome."""
        session = self._get_session_by_id(session_id)
        if not session or not session.is_active:
            raise ValueError("Invalid or inactive session")

        session.is_active = False
        self._update_session(session, 'refused')

        return session.selected_refuse or "No consequences"

    def _get_session_by_id(self, session_id: str) -> Optional[SkillChallengeSession]:
        """Get session by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT character_id, template_id, challenge_name, base_dc,
                       current_successes, current_failures, skill_usage_json,
                       success_revealed, failure_revealed, is_active,
                       selected_success, selected_failure, selected_refuse
                FROM skill_challenge_sessions WHERE id = ?
            ''', (session_id,))

            row = cursor.fetchone()
            if not row:
                return None

            (char_id, template_id, challenge_name, base_dc, successes, failures,
             skill_usage_json, success_revealed, failure_revealed, is_active,
             selected_success, selected_failure, selected_refuse) = row

            template = self.get_template_by_id(template_id)
            if not template:
                return None

            skill_usage = json.loads(skill_usage_json) if skill_usage_json else {}

            return SkillChallengeSession(
                id=session_id,
                character_id=char_id,
                template=template,
                challenge_name=challenge_name,
                base_dc=base_dc,
                successes=successes,
                failures=failures,
                skill_usage=skill_usage,
                success_revealed=bool(success_revealed),
                failure_revealed=bool(failure_revealed),
                is_active=bool(is_active),
                selected_success=selected_success,
                selected_failure=selected_failure,
                selected_refuse=selected_refuse
            )

        except Exception as e:
            print(f"Error getting session by ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _get_skill_modifiers(self, skill_name: str, character_data: dict) -> Tuple[int, int]:
        """Get ability modifier and proficiency bonus for a skill."""
        from talekeeper.services.proficiency_bonus import get_proficiency_bonus

        # Map skills to abilities
        skill_ability_map = {
            'Athletics': 'strength',
            'Acrobatics': 'dexterity',
            'Sleight of Hand': 'dexterity',
            'Stealth': 'dexterity',
            'Arcana': 'intelligence',
            'History': 'intelligence',
            'Investigation': 'intelligence',
            'Nature': 'intelligence',
            'Religion': 'intelligence',
            'Animal Handling': 'wisdom',
            'Insight': 'wisdom',
            'Medicine': 'wisdom',
            'Perception': 'wisdom',
            'Survival': 'wisdom',
            'Deception': 'charisma',
            'Intimidation': 'charisma',
            'Performance': 'charisma',
            'Persuasion': 'charisma'
        }

        # Handle tool proficiencies
        if 'Tools' in skill_name or 'Kit' in skill_name:
            # Most tools use Intelligence or Dexterity
            if 'Thieves' in skill_name:
                ability = 'dexterity'
            else:
                ability = 'intelligence'
        else:
            ability = skill_ability_map.get(skill_name, 'intelligence')

        # Get ability modifier
        ability_score = character_data.get(ability, 10)
        ability_modifier = (ability_score - 10) // 2

        # Get proficiency bonus
        level = character_data.get('level', 1)
        proficiency_bonus = get_proficiency_bonus(level)

        # Get item bonuses from equipped items (like luckstone)
        try:
            from talekeeper.services.item_effects import ItemEffectsService
            item_effects = ItemEffectsService(self.db_path)
            character_id = character_data.get('id')
            if character_id:
                bonuses = item_effects.get_character_bonuses(character_id)
                ability_check_bonus = bonuses.get('ability_check_bonus', 0)
                ability_modifier += ability_check_bonus
        except Exception as e:
            print(f"Error getting item bonuses for skill check: {e}")

        # Check if character is proficient in this skill
        # For now, assume proficiency for simplicity - could be enhanced
        # to check character's actual skill proficiencies

        return ability_modifier, proficiency_bonus

    def _get_session_disadvantage_mode(self, template_id: str) -> str:
        """
        Get disadvantage mode from skill_challenge_metadata.

        Returns:
            'none', 'first', or 'all'
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

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

    def _save_attempt(self, session_id: str, skill_name: str, ability_modifier: int,
                     proficiency_bonus: int, dc: int, roll_result: int,
                     total_result: int, success: bool):
        """Save skill attempt to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get attempt order
            cursor.execute('''
                SELECT COUNT(*) FROM skill_challenge_attempts WHERE session_id = ?
            ''', (session_id,))
            attempt_order = cursor.fetchone()[0] + 1

            cursor.execute('''
                INSERT INTO skill_challenge_attempts
                (id, session_id, skill_name, ability_modifier, proficiency_bonus,
                 dc, roll_result, total_result, success, attempt_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid4()), session_id, skill_name, ability_modifier, proficiency_bonus,
                dc, roll_result, total_result, success, attempt_order
            ))

            conn.commit()

        except Exception as e:
            print(f"Error saving skill attempt: {e}")
        finally:
            if conn:
                conn.close()

    def _update_session(self, session: SkillChallengeSession, outcome: Optional[str] = None):
        """Update session in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE skill_challenge_sessions
                SET current_successes = ?, current_failures = ?,
                    skill_usage_json = ?, is_active = ?, outcome = ?,
                    completed_at = CASE WHEN ? IS NOT NULL THEN datetime('now') ELSE completed_at END
                WHERE id = ?
            ''', (
                session.successes, session.failures, json.dumps(session.skill_usage),
                session.is_active, outcome, outcome, session.id
            ))

            conn.commit()

        except Exception as e:
            print(f"Error updating session: {e}")
        finally:
            if conn:
                conn.close()

    def get_challenge_info_text(self, session: SkillChallengeSession) -> str:
        """Generate challenge information text for display."""
        lines = [
            f"**{session.challenge_name}**",
            "",
            session.template.description,
            "",
            f"**Available Skills:** {', '.join(session.template.skills)}",
            f"**Base DC:** {session.base_dc} (increases with repeated skill use)",
            "",
            f"**Progress:** {session.successes}/3 successes, {session.failures}/3 failures",
            ""
        ]

        # Success information
        if session.success_revealed and session.selected_success:
            lines.append(f"**Success:** {session.selected_success}")
        elif not session.success_revealed:
            lines.append("**Success:** Hidden reward")
        else:
            lines.append("**Success:** Unknown")

        # Failure information
        if session.failure_revealed and session.selected_failure:
            lines.append(f"**Failure:** {session.selected_failure}")
        elif not session.failure_revealed:
            lines.append("**Failure:** Hidden consequence")
        else:
            lines.append("**Failure:** Unknown")

        # Refuse information
        if session.selected_refuse:
            lines.append(f"**Refuse:** {session.selected_refuse}")
        else:
            lines.append("**Refuse:** No consequences")

        return "\n".join(lines)