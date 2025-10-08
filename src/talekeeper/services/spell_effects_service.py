import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging


class SpellEffectsService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def apply_healing(self, target_id: str, healing_amount: int, source_spell: str) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT current_hit_points, max_hit_points
                    FROM characters
                    WHERE id = ?
                """, (target_id,))

                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'reason': 'Character not found'}

                current_hp, max_hp = result
                new_hp = min(current_hp + healing_amount, max_hp)
                actual_healing = new_hp - current_hp

                cursor.execute("""
                    UPDATE characters
                    SET current_hit_points = ?
                    WHERE id = ?
                """, (new_hp, target_id))

                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] {source_spell} healed {target_id} for {actual_healing} HP")

                return {
                    'success': True,
                    'healing': actual_healing,
                    'new_hp': new_hp,
                    'max_hp': max_hp,
                    'target_id': target_id
                }

        except Exception as e:
            self.logger.error(f"Error applying healing: {e}")
            return {'success': False, 'reason': str(e)}

    def apply_damage(self, target_id: str, damage: int, damage_type: str, source_spell: str) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT current_hit_points, hit_points_temporary
                    FROM characters
                    WHERE id = ?
                """, (target_id,))

                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'reason': 'Character not found'}

                current_hp, temp_hp = result
                temp_hp = temp_hp or 0

                if temp_hp > 0:
                    if damage <= temp_hp:
                        new_temp_hp = temp_hp - damage
                        new_hp = current_hp
                        actual_damage = 0
                    else:
                        overflow = damage - temp_hp
                        new_temp_hp = 0
                        new_hp = max(0, current_hp - overflow)
                        actual_damage = overflow
                else:
                    new_temp_hp = 0
                    new_hp = max(0, current_hp - damage)
                    actual_damage = damage

                cursor.execute("""
                    UPDATE characters
                    SET current_hit_points = ?,
                        hit_points_temporary = ?
                    WHERE id = ?
                """, (new_hp, new_temp_hp, target_id))

                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] {source_spell} dealt {damage} {damage_type} damage to {target_id}")

                return {
                    'success': True,
                    'damage': damage,
                    'actual_damage': actual_damage,
                    'damage_type': damage_type,
                    'temp_hp_absorbed': temp_hp - new_temp_hp if temp_hp > 0 else 0,
                    'new_hp': new_hp,
                    'target_id': target_id
                }

        except Exception as e:
            self.logger.error(f"Error applying damage: {e}")
            return {'success': False, 'reason': str(e)}

    def apply_temp_hp(self, target_id: str, temp_hp: int, source_spell: str) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT hit_points_temporary
                    FROM characters
                    WHERE id = ?
                """, (target_id,))

                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'reason': 'Character not found'}

                current_temp_hp = result[0] or 0
                new_temp_hp = max(current_temp_hp, temp_hp)

                cursor.execute("""
                    UPDATE characters
                    SET hit_points_temporary = ?
                    WHERE id = ?
                """, (new_temp_hp, target_id))

                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] {source_spell} granted {temp_hp} temp HP to {target_id}")

                return {
                    'success': True,
                    'temp_hp_granted': temp_hp,
                    'temp_hp_total': new_temp_hp,
                    'replaced': new_temp_hp == temp_hp and current_temp_hp > 0,
                    'target_id': target_id
                }

        except Exception as e:
            self.logger.error(f"Error applying temp HP: {e}")
            return {'success': False, 'reason': str(e)}

    def set_temp_hp(self, character_id: str, amount: int, source: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT hit_points_temporary
                    FROM characters
                    WHERE id = ?
                """, (character_id,))

                result = cursor.fetchone()
                if not result:
                    return False

                current_temp_hp = result[0] or 0
                new_temp_hp = max(current_temp_hp, amount)

                cursor.execute("""
                    UPDATE characters
                    SET hit_points_temporary = ?
                    WHERE id = ?
                """, (new_temp_hp, character_id))

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error setting temp HP: {e}")
            return False

    def get_temp_hp(self, character_id: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT hit_points_temporary
                    FROM characters
                    WHERE id = ?
                """, (character_id,))

                result = cursor.fetchone()
                if result:
                    return result[0] or 0
                return 0

        except Exception as e:
            self.logger.error(f"Error getting temp HP: {e}")
            return 0

    def clear_temp_hp(self, character_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE characters
                    SET hit_points_temporary = 0
                    WHERE id = ?
                """, (character_id,))

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error clearing temp HP: {e}")
            return False

    def apply_buff(self, target_id: str, buff_data: Dict[str, Any], duration_rounds: int,
                   caster_id: Optional[str] = None, concentration: bool = False) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                spell_id = buff_data.get('source')
                spell_name = buff_data.get('spell_name', spell_id)
                spell_level = buff_data.get('spell_level', 1)
                effect_type = buff_data.get('type')
                effect_data_json = json.dumps(buff_data)

                cursor.execute("""
                    INSERT INTO active_spell_effects (
                        character_id, spell_id, spell_name, spell_level_cast,
                        effect_type, effect_data, duration_type, rounds_remaining,
                        concentration, caster_id, target_id
                    ) VALUES (?, ?, ?, ?, ?, ?, 'rounds', ?, ?, ?, ?)
                """, (target_id, spell_id, spell_name, spell_level, effect_type,
                      effect_data_json, duration_rounds, concentration,
                      caster_id or target_id, target_id))

                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] Applied buff {spell_name} to {target_id}")

                return {
                    'success': True,
                    'spell_id': spell_id,
                    'target_id': target_id,
                    'duration_rounds': duration_rounds
                }

        except Exception as e:
            self.logger.error(f"Error applying buff: {e}")
            return {'success': False, 'reason': str(e)}

    def remove_buff(self, character_id: str, spell_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM active_spell_effects
                    WHERE character_id = ? AND spell_id = ?
                """, (character_id, spell_id))

                rows_deleted = cursor.rowcount
                conn.commit()

                if rows_deleted > 0:
                    self.logger.info(f"[SPELL_EFFECTS] Removed buff {spell_id} from {character_id}")

                return rows_deleted > 0

        except Exception as e:
            self.logger.error(f"Error removing buff: {e}")
            return False

    def remove_all_buffs(self, character_id: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM active_spell_effects
                    WHERE character_id = ?
                """, (character_id,))

                rows_deleted = cursor.rowcount
                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] Removed {rows_deleted} buffs from {character_id}")

                return rows_deleted

        except Exception as e:
            self.logger.error(f"Error removing all buffs: {e}")
            return 0

    def get_active_buffs(self, character_id: str, buff_type: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if buff_type:
                    cursor.execute("""
                        SELECT id, spell_id, spell_name, spell_level_cast, effect_type,
                               effect_data, rounds_remaining, concentration, caster_id
                        FROM active_spell_effects
                        WHERE character_id = ? AND effect_type = ?
                    """, (character_id, buff_type))
                else:
                    cursor.execute("""
                        SELECT id, spell_id, spell_name, spell_level_cast, effect_type,
                               effect_data, rounds_remaining, concentration, caster_id
                        FROM active_spell_effects
                        WHERE character_id = ?
                    """, (character_id,))

                buffs = []
                for row in cursor.fetchall():
                    effect_data = json.loads(row[5]) if row[5] else {}
                    buffs.append({
                        'id': row[0],
                        'spell_id': row[1],
                        'spell_name': row[2],
                        'spell_level_cast': row[3],
                        'effect_type': row[4],
                        'effect_data': effect_data,
                        'rounds_remaining': row[6],
                        'concentration': row[7],
                        'caster_id': row[8]
                    })

                return buffs

        except Exception as e:
            self.logger.error(f"Error getting active buffs: {e}")
            return []

    def has_buff(self, character_id: str, spell_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM active_spell_effects
                    WHERE character_id = ? AND spell_id = ?
                """, (character_id, spell_id))

                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            self.logger.error(f"Error checking buff: {e}")
            return False

    def get_buff(self, character_id: str, spell_id: str) -> Optional[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, spell_name, spell_level_cast, effect_type,
                           effect_data, rounds_remaining, concentration, caster_id
                    FROM active_spell_effects
                    WHERE character_id = ? AND spell_id = ?
                    LIMIT 1
                """, (character_id, spell_id))

                row = cursor.fetchone()
                if not row:
                    return None

                effect_data = json.loads(row[4]) if row[4] else {}
                return {
                    'id': row[0],
                    'spell_id': spell_id,
                    'spell_name': row[1],
                    'spell_level_cast': row[2],
                    'effect_type': row[3],
                    'effect_data': effect_data,
                    'rounds_remaining': row[5],
                    'concentration': row[6],
                    'caster_id': row[7]
                }

        except Exception as e:
            self.logger.error(f"Error getting buff: {e}")
            return None

    def get_ac_modifier(self, character_id: str) -> int:
        buffs = self.get_active_buffs(character_id, 'ac_bonus')
        total_bonus = 0

        for buff in buffs:
            effect_data = buff.get('effect_data', {})
            bonus_value = effect_data.get('value', 0)
            total_bonus += bonus_value

        return total_bonus

    def get_attack_bonus(self, character_id: str) -> Dict[str, Any]:
        buffs = self.get_active_buffs(character_id)
        static_bonus = 0
        dice_bonuses = []

        for buff in buffs:
            effect_type = buff.get('effect_type')
            effect_data = buff.get('effect_data', {})

            if effect_type == 'attack_bonus':
                static_bonus += effect_data.get('value', 0)
            elif effect_type == 'attack_and_save_bonus':
                dice_bonus = effect_data.get('bonus_dice')
                if dice_bonus:
                    dice_bonuses.append({
                        'spell': buff.get('spell_name'),
                        'dice': dice_bonus
                    })

        return {
            'total': static_bonus,
            'static': static_bonus,
            'dice_bonuses': dice_bonuses
        }

    def get_damage_bonus(self, character_id: str) -> Dict[str, Any]:
        buffs = self.get_active_buffs(character_id)
        static_bonus = 0
        dice_bonuses = []
        next_hit_bonuses = []

        for buff in buffs:
            effect_type = buff.get('effect_type')
            effect_data = buff.get('effect_data', {})

            if effect_type == 'damage_bonus':
                static_bonus += effect_data.get('value', 0)
            elif effect_type == 'damage_bonus_per_hit':
                dice_bonuses.append({
                    'spell': buff.get('spell_name'),
                    'dice': effect_data.get('damage_dice'),
                    'damage_type': effect_data.get('damage_type')
                })
            elif effect_type == 'next_hit_bonus_damage':
                next_hit_bonuses.append({
                    'spell': buff.get('spell_name'),
                    'spell_id': buff.get('spell_id'),
                    'dice': effect_data.get('damage_dice'),
                    'die_type': effect_data.get('damage_die_type'),
                    'damage_type': effect_data.get('damage_type'),
                    'on_hit_apply_condition': effect_data.get('on_hit_apply_condition')
                })

        return {
            'total': static_bonus,
            'static': static_bonus,
            'dice_bonuses': dice_bonuses,
            'next_hit_bonuses': next_hit_bonuses
        }

    def get_condition_immunities(self, character_id: str) -> List[str]:
        buffs = self.get_active_buffs(character_id, 'condition_immunity')
        immunities = []

        for buff in buffs:
            effect_data = buff.get('effect_data', {})
            condition = effect_data.get('condition')
            if condition:
                immunities.append(condition)

        return immunities

    def get_resistances(self, character_id: str) -> List[str]:
        buffs = self.get_active_buffs(character_id)
        resistances = []

        for buff in buffs:
            effect_data = buff.get('effect_data', {})
            if 'resistance' in effect_data:
                resist_type = effect_data.get('resistance')
                if resist_type:
                    resistances.append(resist_type)

        return resistances

    def process_turn_start_effects(self, character_id: str) -> List[Dict[str, Any]]:
        effects_triggered = []

        try:
            buffs = self.get_active_buffs(character_id)

            for buff in buffs:
                effect_type = buff.get('effect_type')
                effect_data = buff.get('effect_data', {})

                if effect_type == 'temp_hp_per_turn':
                    temp_hp_amount = effect_data.get('temp_hp_per_turn', 0)
                    if temp_hp_amount > 0:
                        result = self.apply_temp_hp(character_id, temp_hp_amount, buff.get('spell_name'))
                        effects_triggered.append({
                            'type': 'temp_hp_granted',
                            'spell': buff.get('spell_name'),
                            'amount': temp_hp_amount,
                            'result': result
                        })

        except Exception as e:
            self.logger.error(f"Error processing turn start effects: {e}")

        return effects_triggered

    def process_turn_end_effects(self, character_id: str) -> List[Dict[str, Any]]:
        effects_triggered = []

        try:
            pass

        except Exception as e:
            self.logger.error(f"Error processing turn end effects: {e}")

        return effects_triggered

    def decrement_effect_durations(self, character_id: str) -> List[str]:
        expired_spell_ids = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE active_spell_effects
                    SET rounds_remaining = rounds_remaining - 1
                    WHERE character_id = ? AND rounds_remaining > 0
                """, (character_id,))

                cursor.execute("""
                    SELECT spell_id, spell_name
                    FROM active_spell_effects
                    WHERE character_id = ? AND rounds_remaining <= 0
                """, (character_id,))

                expired = cursor.fetchall()

                for spell_id, spell_name in expired:
                    expired_spell_ids.append(spell_id)
                    self.logger.info(f"[SPELL_EFFECTS] {spell_name} expired for {character_id}")

                cursor.execute("""
                    DELETE FROM active_spell_effects
                    WHERE character_id = ? AND rounds_remaining <= 0
                """, (character_id,))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error decrementing effect durations: {e}")

        return expired_spell_ids

    def cleanup_expired_effects(self) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM active_spell_effects
                    WHERE expires_at IS NOT NULL AND expires_at < datetime('now')
                """)

                rows_deleted = cursor.rowcount
                conn.commit()

                if rows_deleted > 0:
                    self.logger.info(f"[SPELL_EFFECTS] Cleaned up {rows_deleted} expired effects")

                return rows_deleted

        except Exception as e:
            self.logger.error(f"Error cleaning up expired effects: {e}")
            return 0

    def remove_condition(self, character_id: str, condition_name: str) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id FROM character_conditions
                    WHERE character_id = ? AND condition_name = ?
                """, (character_id, condition_name))

                if not cursor.fetchone():
                    return {
                        'success': False,
                        'reason': f'Character does not have {condition_name} condition'
                    }

                cursor.execute("""
                    DELETE FROM character_conditions
                    WHERE character_id = ? AND condition_name = ?
                """, (character_id, condition_name))

                conn.commit()

                self.logger.info(f"[SPELL_EFFECTS] Removed {condition_name} from {character_id}")

                return {
                    'success': True,
                    'condition': condition_name,
                    'target_id': character_id
                }

        except Exception as e:
            self.logger.error(f"Error removing condition: {e}")
            return {'success': False, 'reason': str(e)}
