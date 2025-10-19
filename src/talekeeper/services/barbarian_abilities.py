# core
# category: core
"""
Barbarian Abilities Service for TaleKeeper

Handles all Barbarian-specific abilities and features:
- Rage
- Reckless Attack
- Unarmored Defense
- Brutal Strike
- Relentless Rage
- Berserker subclass features

Follows the same patterns as FighterAbilitiesService for consistency.
"""

import sqlite3
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class BarbarianAbilitiesService:
    """Service for managing Barbarian abilities and resources."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_barbarian_level(self, character_id: str) -> int:
        """Get the barbarian class level for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level, class_id FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if row and (row['class_id'] or '').lower() == 'barbarian':
                return row['level']
            return 0

    def update_barbarian_resources_for_level(self, character_id: str, level: int) -> None:
        """Update barbarian resource maximums based on level."""
        # Get character's class to determine resources
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT class_id FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return
            class_id = result['class_id'].lower()

        # Only update if this is a Barbarian
        if class_id != 'barbarian':
            return

        # Rage uses scaling: 2 → 3 → 4 → 5 → 6
        rage_uses_max = 2
        if level >= 17:
            rage_uses_max = 6
        elif level >= 12:
            rage_uses_max = 5
        elif level >= 6:
            rage_uses_max = 4
        elif level >= 3:
            rage_uses_max = 3

        # Rage damage bonus scaling: +2 → +3 → +4
        rage_damage_bonus = 2
        if level >= 16:
            rage_damage_bonus = 4
        elif level >= 9:
            rage_damage_bonus = 3

        # Brutal Strike uses (available when using Reckless Attack)
        brutal_strike_uses_max = 0
        if level >= 9:
            brutal_strike_uses_max = 1  # Can use once when using Reckless Attack

        # Relentless Rage uses (Level 11+)
        relentless_rage_uses_max = 0
        if level >= 11:
            relentless_rage_uses_max = 1  # Resets after rest

        # Weapon Mastery count - unlimited for Barbarian
        weapon_mastery_count = -1  # Unlimited

        # Extra attacks
        extra_attacks = 1 if level < 5 else 2

        # Intimidating Presence uses (Berserker Level 14+)
        intimidating_presence_uses_max = 0
        subclass = self.get_character_subclass(character_id)
        if subclass == 'berserker' and level >= 14:
            intimidating_presence_uses_max = 1

        # Brutal Strike effects available by level
        brutal_strike_effects = []
        if level >= 9:
            brutal_strike_effects.extend(['forceful', 'hamstring'])
        if level >= 13:
            brutal_strike_effects.extend(['staggering', 'sundering'])

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Update or insert barbarian_features
            cursor.execute("""
                INSERT INTO barbarian_features (
                    character_id, level, rage_uses_current, rage_uses_max, rage_damage_bonus,
                    brutal_strike_uses_current, brutal_strike_uses_max,
                    relentless_rage_uses_current, relentless_rage_uses_max,
                    intimidating_presence_uses_current, intimidating_presence_uses_max,
                    weapon_mastery_count, extra_attacks, brutal_strike_effects,
                    reckless_attack_available, danger_sense_active, fast_movement_active,
                    feral_instinct_active, instinctive_pounce_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(character_id) DO UPDATE SET
                    level = ?,
                    rage_uses_max = ?,
                    rage_damage_bonus = ?,
                    brutal_strike_uses_max = ?,
                    relentless_rage_uses_max = ?,
                    intimidating_presence_uses_max = ?,
                    weapon_mastery_count = ?,
                    extra_attacks = ?,
                    brutal_strike_effects = ?,
                    reckless_attack_available = ?,
                    danger_sense_active = ?,
                    fast_movement_active = ?,
                    feral_instinct_active = ?,
                    instinctive_pounce_available = ?
            """, (
                character_id, level, rage_uses_max, rage_uses_max, rage_damage_bonus,
                0, brutal_strike_uses_max, 0, relentless_rage_uses_max,
                0, intimidating_presence_uses_max, weapon_mastery_count, extra_attacks,
                json.dumps(brutal_strike_effects), level >= 2, level >= 2, level >= 5,
                level >= 7, level >= 7,
                # ON CONFLICT UPDATE values
                level, rage_uses_max, rage_damage_bonus, brutal_strike_uses_max,
                relentless_rage_uses_max, intimidating_presence_uses_max,
                weapon_mastery_count, extra_attacks, json.dumps(brutal_strike_effects),
                level >= 2, level >= 2, level >= 5, level >= 7, level >= 7
            ))

            conn.commit()

    def get_character_subclass(self, character_id: str) -> Optional[str]:
        """Get the barbarian subclass for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT subclass_id
                FROM character_subclasses
                WHERE character_id = ? AND LOWER(class_id) = 'barbarian'
                """,
                (character_id,)
            )
            row = cursor.fetchone()
            if row and row['subclass_id']:
                return row['subclass_id']

            cursor.execute(
                """
                SELECT class_id, subclass_id
                FROM characters
                WHERE id = ?
                """,
                (character_id,)
            )
            legacy = cursor.fetchone()
            if not legacy or not legacy['subclass_id']:
                return None

            if not legacy['class_id'] or legacy['class_id'].lower() == 'barbarian':
                return legacy['subclass_id']

            return None

    def use_rage(self, character_id: str) -> Dict[str, Any]:
        """Use Rage ability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get current rage state from barbarian_features (state tracking only)
            cursor.execute("""
                SELECT rage_damage_bonus, is_raging, level
                FROM barbarian_features WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row:
                return {'success': False, 'error': 'Barbarian features not found'}

            if row['is_raging']:
                return {'success': False, 'error': 'Already raging'}

            # Check rage uses from character_resources (resource tracking)
            cursor.execute("""
                SELECT current_uses, max_uses
                FROM character_resources
                WHERE character_id = ? AND resource_name = 'Rage'
            """, (character_id,))
            resource_row = cursor.fetchone()

            if not resource_row:
                return {'success': False, 'error': 'Rage resource not found'}

            if resource_row['current_uses'] <= 0:
                return {'success': False, 'error': 'No Rage uses remaining'}

            # Start rage
            rage_damage_bonus = row['rage_damage_bonus']
            rage_turns = 10  # Rage lasts 10 rounds (60 seconds)

            # Consume rage use from character_resources
            cursor.execute("""
                UPDATE character_resources SET
                    current_uses = current_uses - 1
                WHERE character_id = ? AND resource_name = 'Rage'
            """, (character_id,))

            # Update state in barbarian_features
            cursor.execute("""
                UPDATE barbarian_features SET
                    is_raging = TRUE,
                    rage_turns_remaining = ?
                WHERE character_id = ?
            """, (rage_turns, character_id))

            conn.commit()

            return {
                'success': True,
                'rage_damage_bonus': rage_damage_bonus,
                'rage_turns_remaining': rage_turns,
                'uses_remaining': resource_row['current_uses'] - 1,
                'effects': [
                    'Resistance to bludgeoning, piercing, slashing damage',
                    f'+{rage_damage_bonus} damage on Strength-based melee attacks',
                    'Advantage on Strength checks and saves',
                    'Cannot cast spells or maintain concentration'
                ]
            }

    def end_rage(self, character_id: str, reason: str = "duration") -> Dict[str, Any]:
        """End rage (duration, heavy armor, incapacitated, etc.)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE barbarian_features SET
                    is_raging = FALSE,
                    rage_turns_remaining = 0
                WHERE character_id = ?
            """, (character_id,))

            conn.commit()

            return {
                'success': True,
                'reason': reason,
                'message': f'Rage ended ({reason})'
            }

    def use_reckless_attack(self, character_id: str) -> Dict[str, Any]:
        """Toggle Reckless Attack for this turn."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if available
            cursor.execute("""
                SELECT reckless_attack_available, level
                FROM barbarian_features WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or not row['reckless_attack_available']:
                return {'success': False, 'error': 'Reckless Attack not available (requires level 2)'}

            # Update character combat state
            cursor.execute("""
                INSERT INTO character_combat_state (character_id, reckless_attack_active)
                VALUES (?, TRUE)
                ON CONFLICT(character_id) DO UPDATE SET
                    reckless_attack_active = NOT reckless_attack_active
            """, (character_id,))

            # Get new state
            cursor.execute("""
                SELECT reckless_attack_active FROM character_combat_state WHERE character_id = ?
            """, (character_id,))
            state_row = cursor.fetchone()
            is_active = state_row['reckless_attack_active'] if state_row else False

            conn.commit()

            return {
                'success': True,
                'reckless_active': is_active,
                'effect': 'Advantage on Strength attack rolls; enemies have advantage on attacks against you' if is_active else 'Reckless Attack deactivated'
            }

    def use_brutal_strike(self, character_id: str, strike_type: str, target_name: str = "") -> Dict[str, Any]:
        """Use Brutal Strike when making a Reckless Attack."""
        valid_strikes = ['forceful', 'hamstring', 'staggering', 'sundering']
        if strike_type not in valid_strikes:
            return {'success': False, 'error': f'Invalid strike type: {strike_type}'}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get brutal strike availability
            cursor.execute("""
                SELECT brutal_strike_uses_current, brutal_strike_uses_max, brutal_strike_effects, level
                FROM barbarian_features WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or row['level'] < 9:
                return {'success': False, 'error': 'Brutal Strike requires level 9'}

            if row['brutal_strike_uses_current'] <= 0:
                return {'success': False, 'error': 'No Brutal Strike uses remaining (requires Reckless Attack)'}

            # Check if this strike type is available at current level
            available_effects = json.loads(row['brutal_strike_effects'] or '[]')
            if strike_type not in available_effects:
                return {'success': False, 'error': f'{strike_type.title()} strike not available at this level'}

            # Use Brutal Strike
            cursor.execute("""
                UPDATE barbarian_features SET
                    brutal_strike_uses_current = brutal_strike_uses_current - 1
                WHERE character_id = ?
            """, (character_id,))

            conn.commit()

            # Determine damage and effect
            damage_dice = "2d10" if row['level'] >= 17 else "1d10"

            effects = {
                'forceful': f"Push {target_name or 'target'} 15 feet away and move toward them",
                'hamstring': f"Reduce {target_name or 'target'}'s speed by 15 feet until their next turn",
                'staggering': f"{target_name or 'Target'} has disadvantage on next save and can't make opportunity attacks",
                'sundering': f"Next attack roll against {target_name or 'target'} gains +5 bonus"
            }

            return {
                'success': True,
                'strike_type': strike_type,
                'damage_bonus': damage_dice,
                'effect': effects[strike_type],
                'uses_remaining': row['brutal_strike_uses_current'] - 1
            }

    def check_relentless_rage(self, character_id: str, damage_taken: int) -> Dict[str, Any]:
        """Check and potentially trigger Relentless Rage when dropping to 0 HP."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get character info
            cursor.execute("""
                SELECT bf.relentless_rage_uses_current, bf.level, bf.is_raging,
                       c.hit_points_current
                FROM barbarian_features bf
                JOIN characters c ON bf.character_id = c.id
                WHERE bf.character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or row['level'] < 11:
                return {'success': False, 'available': False}

            if not row['is_raging']:
                return {'success': False, 'available': False, 'reason': 'Not raging'}

            if row['relentless_rage_uses_current'] <= 0:
                return {'success': False, 'available': False, 'reason': 'No uses remaining'}

            # Calculate DC (starts at 10, increases by 5 each use)
            uses_made = 1 - row['relentless_rage_uses_current']  # Assuming max 1 for now
            dc = 10 + (uses_made * 5)

            # Roll Constitution save
            con_save_roll = random.randint(1, 20)
            # TODO: Add character's Constitution save bonus
            con_save_total = con_save_roll  # Simplified for now

            success = con_save_total >= dc

            if success:
                # Stay at HP = 2 × Barbarian level instead of 0
                new_hp = 2 * row['level']

                cursor.execute("""
                    UPDATE characters SET
                        hit_points_current = ?,
                        current_hit_points = ?
                    WHERE id = ?
                """, (new_hp, new_hp, character_id))

                cursor.execute("""
                    UPDATE barbarian_features SET
                        relentless_rage_uses_current = relentless_rage_uses_current - 1
                    WHERE character_id = ?
                """, (character_id,))

                conn.commit()

                return {
                    'success': True,
                    'triggered': True,
                    'save_roll': con_save_roll,
                    'save_total': con_save_total,
                    'dc': dc,
                    'new_hp': new_hp,
                    'uses_remaining': row['relentless_rage_uses_current'] - 1
                }
            else:
                return {
                    'success': True,
                    'triggered': False,
                    'save_roll': con_save_roll,
                    'save_total': con_save_total,
                    'dc': dc,
                    'result': 'Relentless Rage failed - character drops to 0 HP'
                }

    def rest_barbarian_resources(self, character_id: str, rest_type: str) -> None:
        """Reset barbarian resources on rest."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if rest_type == 'short':
                # Short rest: End rage, reset brutal strike uses
                cursor.execute("""
                    UPDATE barbarian_features SET
                        is_raging = FALSE,
                        rage_turns_remaining = 0,
                        brutal_strike_uses_current = brutal_strike_uses_max,
                        frenzy_active = FALSE
                    WHERE character_id = ?
                """, (character_id,))

                # Clear combat state
                cursor.execute("""
                    UPDATE character_combat_state SET
                        raging = FALSE,
                        rage_damage_bonus = 0,
                        reckless_attack_active = FALSE,
                        frenzy_active = FALSE
                    WHERE character_id = ?
                """, (character_id,))

            elif rest_type == 'long':
                # Long rest: Restore all resources
                cursor.execute("""
                    UPDATE barbarian_features SET
                        rage_uses_current = rage_uses_max,
                        is_raging = FALSE,
                        rage_turns_remaining = 0,
                        brutal_strike_uses_current = brutal_strike_uses_max,
                        relentless_rage_uses_current = relentless_rage_uses_max,
                        intimidating_presence_uses_current = intimidating_presence_uses_max,
                        persistent_rage_recharge_used = FALSE,
                        frenzy_active = FALSE
                    WHERE character_id = ?
                """, (character_id,))

                # Clear combat state
                cursor.execute("""
                    UPDATE character_combat_state SET
                        raging = FALSE,
                        rage_damage_bonus = 0,
                        reckless_attack_active = FALSE,
                        frenzy_active = FALSE
                    WHERE character_id = ?
                """, (character_id,))

            conn.commit()

    def process_berserker_turn_start(self, character_id: str) -> Dict[str, Any]:
        """Apply Berserker subclass start-of-turn effects."""
        result = {"success": True, "frenzy": None, "mindless_rage": None}

        subclass = self.get_character_subclass(character_id)
        if subclass != 'berserker':
            return result

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get character state
            cursor.execute("""
                SELECT bf.level, bf.is_raging, bf.frenzy_active, bf.mindless_rage_active,
                       cs.reckless_attack_active
                FROM barbarian_features bf
                LEFT JOIN character_combat_state cs ON bf.character_id = cs.character_id
                WHERE bf.character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row:
                return {"success": False, "error": "Character not found"}

            level = row['level']
            is_raging = row['is_raging']
            reckless_active = row['reckless_attack_active'] or False

            # Frenzy (Level 3+): When you Reckless Attack while Raging
            if level >= 3 and is_raging and reckless_active:
                if not row['frenzy_active']:
                    cursor.execute("""
                        UPDATE barbarian_features SET frenzy_active = TRUE
                        WHERE character_id = ?
                    """, (character_id,))

                    cursor.execute("""
                        UPDATE character_combat_state SET frenzy_active = TRUE
                        WHERE character_id = ?
                    """, (character_id,))

                    result["frenzy"] = {
                        "activated": True,
                        "effect": f"Add {row['rage_damage_bonus']}d6 to first hit this turn"
                    }

            # Mindless Rage (Level 6+): Immune to Charmed/Frightened while raging
            if level >= 6 and is_raging:
                if not row['mindless_rage_active']:
                    cursor.execute("""
                        UPDATE barbarian_features SET mindless_rage_active = TRUE
                        WHERE character_id = ?
                    """, (character_id,))

                    result["mindless_rage"] = {
                        "activated": True,
                        "effect": "Immune to Charmed and Frightened conditions"
                    }

            conn.commit()

        return result

    def use_berserker_retaliation(self, character_id: str, attacker_name: str = "") -> Dict[str, Any]:
        """Use Berserker Retaliation reaction (Level 10+)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level, retaliation_available
                FROM barbarian_features WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or row['level'] < 10:
                return {'success': False, 'error': 'Retaliation requires Berserker level 10'}

            if not row['retaliation_available']:
                return {'success': False, 'error': 'Retaliation not available'}

            # Check if subclass is berserker
            subclass = self.get_character_subclass(character_id)
            if subclass != 'berserker':
                return {'success': False, 'error': 'Retaliation requires Berserker subclass'}

            return {
                'success': True,
                'effect': f'Make one melee weapon or unarmed attack against {attacker_name or "the attacker"}',
                'action_type': 'reaction'
            }

    def use_intimidating_presence(self, character_id: str) -> Dict[str, Any]:
        """Use Intimidating Presence (Berserker Level 14+)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level, intimidating_presence_uses_current, intimidating_presence_uses_max
                FROM barbarian_features WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or row['level'] < 14:
                return {'success': False, 'error': 'Intimidating Presence requires Berserker level 14'}

            if row['intimidating_presence_uses_current'] <= 0:
                return {'success': False, 'error': 'No Intimidating Presence uses remaining'}

            # Check if subclass is berserker
            subclass = self.get_character_subclass(character_id)
            if subclass != 'berserker':
                return {'success': False, 'error': 'Intimidating Presence requires Berserker subclass'}

            # Get character stats for DC calculation
            cursor.execute("""
                SELECT strength, proficiency_bonus FROM characters WHERE id = ?
            """, (character_id,))
            char_row = cursor.fetchone()

            if not char_row:
                return {'success': False, 'error': 'Character not found'}

            str_mod = (char_row['strength'] - 10) // 2
            prof_bonus = char_row['proficiency_bonus'] or 2
            save_dc = 8 + str_mod + prof_bonus

            # Use the ability
            cursor.execute("""
                UPDATE barbarian_features SET
                    intimidating_presence_uses_current = intimidating_presence_uses_current - 1
                WHERE character_id = ?
            """, (character_id,))

            conn.commit()

            return {
                'success': True,
                'save_dc': save_dc,
                'effect': '30 ft emanation - Wisdom save or Frightened for 1 minute (repeat save each turn)',
                'uses_remaining': row['intimidating_presence_uses_current'] - 1
            }

    def has_danger_sense_advantage(self, character_id: str, save_ability: str, conditions: List[str] = None) -> bool:
        """Check if character gets Danger Sense advantage on a Dexterity saving throw."""
        if save_ability.lower() != 'dexterity':
            return False

        # Check for incapacitating conditions
        if conditions:
            incapacitating = {'blinded', 'deafened', 'incapacitated', 'unconscious', 'paralyzed', 'stunned'}
            if any(condition.lower() in incapacitating for condition in conditions):
                return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT danger_sense_active, level
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if row and row['danger_sense_active'] and row['level'] >= 2:
                return True

        return False

    def has_danger_sense_advantage_enhanced(self, character_id: str, save_ability: str = 'dexterity') -> bool:
        """
        Enhanced Danger Sense check using the formal condition system.
        This is the new implementation that integrates with our condition manager.
        """
        if save_ability.lower() != 'dexterity':
            return False

        # Check if character has Danger Sense feature (level 2+ barbarian)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT danger_sense_active, level
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not (row and row['danger_sense_active'] and row['level'] >= 2):
                return False

        # NEW: Use formal condition system to check for incapacitating conditions
        try:
            from talekeeper.services.condition_manager import ConditionManager
            # Create condition manager instance with same database path
            condition_manager = ConditionManager(self.db_path)

            has_incapacitating = condition_manager.has_incapacitating_condition(character_id)

            if has_incapacitating:
                return False
        except ImportError:
            # Fallback to original logic if condition system not available
            print("[BarbarianAbilities] Condition system not available, using fallback")
            return True
        except Exception as e:
            print(f"[BarbarianAbilities] Error checking conditions: {e}")
            return True

        return True

    def get_primal_knowledge_skills(self, character_id: str) -> List[str]:
        """Get available Primal Knowledge skills for barbarian."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT primal_knowledge_skills, level
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if row and row['level'] >= 3:
                skills_json = row['primal_knowledge_skills'] or '[]'
                return json.loads(skills_json)

            return []

    def add_primal_knowledge_skill(self, character_id: str, skill_name: str) -> Dict[str, Any]:
        """Add a skill to Primal Knowledge (Animal Handling, Athletics, Intimidation, Nature, Perception, Survival)."""
        valid_skills = ['Animal Handling', 'Athletics', 'Intimidation', 'Nature', 'Perception', 'Survival']
        if skill_name not in valid_skills:
            return {'success': False, 'error': f'Invalid skill: {skill_name}. Must be one of: {", ".join(valid_skills)}'}

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT primal_knowledge_skills, level
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row or row['level'] < 3:
                return {'success': False, 'error': 'Primal Knowledge requires barbarian level 3+'}

            current_skills = json.loads(row['primal_knowledge_skills'] or '[]')
            if skill_name in current_skills:
                return {'success': False, 'error': f'{skill_name} already known'}

            # Calculate max skills (2 at level 3, +1 every 4 levels: 6, 10, 14, 18)
            level = row['level']
            max_skills = 2 + ((level - 3) // 4)

            if len(current_skills) >= max_skills:
                return {'success': False, 'error': f'Maximum {max_skills} skills allowed at level {level}'}

            current_skills.append(skill_name)
            cursor.execute("""
                UPDATE barbarian_features
                SET primal_knowledge_skills = ?
                WHERE character_id = ?
            """, (json.dumps(current_skills), character_id))

            conn.commit()

            return {
                'success': True,
                'skill_added': skill_name,
                'total_skills': len(current_skills),
                'max_skills': max_skills
            }

    def has_feral_instinct(self, character_id: str) -> bool:
        """Check if character has Feral Instinct (advantage on initiative, can act if surprised)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feral_instinct_active, level
                FROM barbarian_features
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()

            return bool(row and row['feral_instinct_active'] and row['level'] >= 7)