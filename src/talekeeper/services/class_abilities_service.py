# core
# category: core
import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class ClassAbilitiesService:

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ability_cache = {}
        self._scaling_cache = {}

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_character_abilities(self, character_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level, class_id FROM characters WHERE id = ?
            """, (character_id,))
            char = cursor.fetchone()
            if not char:
                return []

            level = char['level']
            class_name = (char['class_id'] or '').title()

            cursor.execute("""
                SELECT
                    ca.ability_id,
                    ca.ability_name,
                    ca.description,
                    ca.level_gained,
                    ca.feature_type,
                    ca.usage_type,
                    ca.uses_formula,
                    ca.scaling_type,
                    ca.mechanics,
                    COALESCE(cau.current_uses, 0) as current_uses,
                    COALESCE(cau.max_uses, 0) as max_uses,
                    COALESCE(cau.is_active, 0) as is_active,
                    COALESCE(cau.turns_remaining, 0) as turns_remaining
                FROM class_abilities ca
                LEFT JOIN character_ability_usage cau
                    ON ca.ability_id = cau.ability_id AND cau.character_id = ?
                WHERE ca.class_name = ? AND ca.level_gained <= ?
                ORDER BY ca.level_gained, ca.ability_name
            """, (character_id, class_name, level))

            abilities = []
            for row in cursor.fetchall():
                abilities.append({
                    'ability_id': row['ability_id'],
                    'ability_name': row['ability_name'],
                    'description': row['description'],
                    'level_gained': row['level_gained'],
                    'feature_type': row['feature_type'],
                    'usage_type': row['usage_type'],
                    'current_uses': row['current_uses'],
                    'max_uses': row['max_uses'],
                    'is_active': bool(row['is_active']),
                    'turns_remaining': row['turns_remaining'],
                    'mechanics': json.loads(row['mechanics']) if row['mechanics'] else {}
                })

            return abilities

    def use_ability(self, character_id: str, ability_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        if context is None:
            context = {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM class_abilities WHERE ability_id = ?
            """, (ability_id,))
            ability = cursor.fetchone()
            if not ability:
                return {"success": False, "reason": "Ability not found"}

            cursor.execute("""
                SELECT * FROM character_ability_usage
                WHERE character_id = ? AND ability_id = ?
            """, (character_id, ability_id))
            usage = cursor.fetchone()

            if not usage:
                return {"success": False, "reason": "Character does not have this ability"}

            if ability['usage_type'] not in ['unlimited', 'permanent']:
                if usage['current_uses'] >= usage['max_uses']:
                    return {"success": False, "reason": "No uses remaining"}

            mechanics = json.loads(ability['mechanics']) if ability['mechanics'] else {}

            result = self._execute_ability_mechanics(
                character_id, ability_id, ability, mechanics, context, cursor
            )

            if result.get('success'):
                if ability['usage_type'] not in ['unlimited', 'permanent']:
                    cursor.execute("""
                        UPDATE character_ability_usage
                        SET current_uses = current_uses + 1,
                            last_used = ?
                        WHERE character_id = ? AND ability_id = ?
                    """, (datetime.now().isoformat(), character_id, ability_id))

            conn.commit()
            return result

    def _execute_ability_mechanics(
        self,
        character_id: str,
        ability_id: str,
        ability: sqlite3.Row,
        mechanics: Dict[str, Any],
        context: Dict[str, Any],
        cursor: sqlite3.Cursor
    ) -> Dict[str, Any]:

        if ability_id == 'second_wind':
            return self._execute_second_wind(character_id, mechanics, cursor)
        elif ability_id == 'rage':
            return self._execute_rage(character_id, mechanics, cursor)
        elif ability_id == 'action_surge':
            return self._execute_action_surge(character_id, mechanics, cursor)
        elif ability_id == 'sneak_attack':
            return self._execute_sneak_attack(character_id, mechanics, context, cursor)
        else:
            return {
                "success": True,
                "ability": ability['ability_name'],
                "message": f"{ability['ability_name']} activated",
                "mechanics": mechanics
            }

    def _execute_second_wind(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
        level = cursor.fetchone()['level']

        import random
        heal_roll = random.randint(1, 10)
        total_healing = heal_roll + level

        return {
            "success": True,
            "ability": "Second Wind",
            "healing": total_healing,
            "roll": f"1d10({heal_roll}) + {level}",
            "message": f"Healed {total_healing} HP"
        }

    def _execute_rage(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
        level = cursor.fetchone()['level']

        rage_damage = self._get_scaling_value('rage_damage', level)

        cursor.execute("""
            UPDATE character_ability_usage
            SET is_active = 1, turns_remaining = ?
            WHERE character_id = ? AND ability_id = 'rage'
        """, (mechanics.get('duration_turns', 10), character_id))

        return {
            "success": True,
            "ability": "Rage",
            "damage_bonus": rage_damage,
            "duration": mechanics.get('duration_turns', 10),
            "resistances": mechanics.get('resistance_types', []),
            "message": f"Rage activated! +{rage_damage} damage, resistance to physical damage"
        }

    def _execute_action_surge(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        return {
            "success": True,
            "ability": "Action Surge",
            "extra_actions": mechanics.get('action_count', 1),
            "message": "Gained extra action this turn!"
        }

    def _execute_sneak_attack(
        self,
        character_id: str,
        mechanics: Dict,
        context: Dict,
        cursor: sqlite3.Cursor
    ) -> Dict[str, Any]:
        cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
        level = cursor.fetchone()['level']

        dice_count = self._calculate_sneak_attack_dice(level)

        return {
            "success": True,
            "ability": "Sneak Attack",
            "damage_dice": f"{dice_count}d6",
            "dice_count": dice_count,
            "message": f"Add {dice_count}d6 sneak attack damage"
        }

    def restore_abilities(self, character_id: str, rest_type: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if rest_type == 'short':
                cursor.execute("""
                    UPDATE character_ability_usage
                    SET current_uses = 0, last_reset = ?
                    WHERE character_id = ? AND ability_id IN (
                        SELECT ability_id FROM class_abilities
                        WHERE usage_type IN ('short_rest', 'unlimited')
                    )
                """, (datetime.now().isoformat(), character_id))
            elif rest_type == 'long':
                cursor.execute("""
                    UPDATE character_ability_usage
                    SET current_uses = 0, is_active = 0, turns_remaining = 0, last_reset = ?
                    WHERE character_id = ?
                """, (datetime.now().isoformat(), character_id))

            conn.commit()

    def calculate_max_uses(self, ability_id: str, level: int, character_stats: Dict = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uses_formula, scaling_type FROM class_abilities WHERE ability_id = ?
            """, (ability_id,))
            ability = cursor.fetchone()
            if not ability or not ability['uses_formula']:
                return 0

            formula = ability['uses_formula']

            if ability['scaling_type'] == 'level_based':
                if formula in self._scaling_cache:
                    scaling_data = self._scaling_cache[formula]
                else:
                    cursor.execute("""
                        SELECT formula_data FROM ability_scaling_formulas WHERE formula_name = ?
                    """, (formula,))
                    row = cursor.fetchone()
                    if row:
                        scaling_data = json.loads(row['formula_data'])
                        self._scaling_cache[formula] = scaling_data
                    else:
                        return self._evaluate_formula(formula, level)

                return scaling_data.get(str(level), 0)

            elif ability['scaling_type'] == 'proficiency_based':
                return self._get_proficiency_bonus(level)

            elif ability['scaling_type'] == 'fixed':
                return int(formula) if formula.isdigit() else 1

            else:
                return self._evaluate_formula(formula, level)

    def _evaluate_formula(self, formula: str, level: int) -> int:
        try:
            formula = formula.replace('level', str(level))
            return int(eval(formula))
        except:
            return 0

    def _get_scaling_value(self, formula_name: str, level: int) -> int:
        if formula_name in self._scaling_cache:
            return self._scaling_cache[formula_name].get(str(level), 0)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT formula_data FROM ability_scaling_formulas WHERE formula_name = ?
            """, (formula_name,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row['formula_data'])
                self._scaling_cache[formula_name] = data
                return data.get(str(level), 0)
        return 0

    def _get_proficiency_bonus(self, level: int) -> int:
        return self._get_scaling_value('proficiency_bonus', level)

    def _calculate_sneak_attack_dice(self, level: int) -> int:
        return 1 + ((level - 1) // 2)

    def update_ability_resources_for_level(self, character_id: str, new_level: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.class_id, cau.ability_id
                FROM characters c
                JOIN character_ability_usage cau ON c.id = cau.character_id
                WHERE c.id = ?
            """, (character_id,))

            for row in cursor.fetchall():
                max_uses = self.calculate_max_uses(row['ability_id'], new_level)
                cursor.execute("""
                    UPDATE character_ability_usage
                    SET max_uses = ?
                    WHERE character_id = ? AND ability_id = ?
                """, (max_uses, character_id, row['ability_id']))

            cursor.execute("""
                SELECT c.class_id FROM characters WHERE id = ?
            """, (character_id,))
            char = cursor.fetchone()
            class_name = (char['class_id'] or '').title()

            cursor.execute("""
                SELECT ability_id, uses_formula, scaling_type
                FROM class_abilities
                WHERE class_name = ? AND level_gained = ?
            """, (class_name, new_level))

            for ability in cursor.fetchall():
                max_uses = self.calculate_max_uses(ability['ability_id'], new_level)
                cursor.execute("""
                    INSERT OR IGNORE INTO character_ability_usage
                    (character_id, ability_id, current_uses, max_uses, is_active, turns_remaining)
                    VALUES (?, ?, 0, ?, 0, 0)
                """, (character_id, ability['ability_id'], max_uses))

            conn.commit()
