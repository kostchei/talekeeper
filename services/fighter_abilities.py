# core
# core
"""
Fighter Abilities Service for TaleKeeper

Handles all Fighter-specific abilities and features:
- Second Wind
- Action Surge
- Indomitable
- Tactical Mind
- Tactical Shift
- Champion subclass features
"""

import sqlite3
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class FighterAbilitiesService:
    """Service for managing Fighter abilities and resources."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_fighter_level(self, character_id: str) -> int:
        """Get the fighter class level for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level, class_id FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if row and (row['class_id'] or '').lower() == 'fighter':
                return row['level']
            return 0
    
    def update_fighter_resources_for_level(self, character_id: str, level: int) -> None:
        """Update fighter resource maximums based on level."""
        # Get character's class to determine resources
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT class_id FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                return
            class_id = result['class_id'].lower()

        # Second Wind uses (Fighter only)
        if class_id == 'fighter' and level >= 1:
            second_wind_max = 2  # Base 2 uses
            if level >= 4:
                second_wind_max = 3
            if level >= 10:
                second_wind_max = 4
        else:
            second_wind_max = 0

        # Action Surge uses (Fighter only)
        action_surge_max = 0
        if class_id == 'fighter':
            action_surge_max = 1 if level >= 2 else 0
            if level >= 17:
                action_surge_max = 2

        # Indomitable uses (Fighter only)
        indomitable_max = 0
        if class_id == 'fighter':
            if level >= 9:
                indomitable_max = 1
            if level >= 13:
                indomitable_max = 2
            if level >= 17:
                indomitable_max = 3

        # Weapon Mastery count - unlimited for Fighter, Barbarian, Rogue, Paladin
        unlimited_mastery_classes = ['fighter', 'barbarian', 'rogue', 'paladin']
        weapon_mastery_count = -1 if class_id in unlimited_mastery_classes else 0
        
        # Update critical range based on Champion features
        critical_range_min = 20  # Default
        subclass = self.get_character_subclass(character_id)
        if subclass == 'champion':
            if level >= 15:
                critical_range_min = 18  # Superior Critical
            elif level >= 3:
                critical_range_min = 19  # Improved Critical
                
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Update character resources
            cursor.execute("""
                UPDATE characters SET
                    second_wind_uses_max = ?,
                    second_wind_uses_current = CASE 
                        WHEN second_wind_uses_current > ? THEN ?
                        ELSE second_wind_uses_current
                    END,
                    action_surge_uses_max = ?,
                    action_surge_uses_current = CASE
                        WHEN action_surge_uses_current > ? THEN ?
                        ELSE action_surge_uses_current
                    END,
                    indomitable_uses_max = ?,
                    indomitable_uses_current = CASE
                        WHEN indomitable_uses_current > ? THEN ?
                        ELSE indomitable_uses_current
                    END,
                    weapon_mastery_count = ?
                WHERE id = ?
            """, (second_wind_max, second_wind_max, second_wind_max,
                  action_surge_max, action_surge_max, action_surge_max,
                  indomitable_max, indomitable_max, indomitable_max,
                  weapon_mastery_count, character_id))
            
            # Update or insert combat state
            cursor.execute("""
                INSERT INTO character_combat_state (character_id, critical_range_min)
                VALUES (?, ?)
                ON CONFLICT(character_id) DO UPDATE SET
                    critical_range_min = ?
            """, (character_id, critical_range_min, critical_range_min))
            
            conn.commit()
    
    def get_character_subclass(self, character_id: str) -> Optional[str]:
        """Get the fighter subclass for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT subclass_id
                FROM character_subclasses
                WHERE character_id = ? AND LOWER(class_id) = 'fighter'
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

            if not legacy['class_id'] or legacy['class_id'].lower() == 'fighter':
                return legacy['subclass_id']

            return None

    def has_remarkable_athlete(self, character_id: str) -> bool:
        """Return True if the character qualifies for Remarkable Athlete."""
        level = self.get_fighter_level(character_id)
        if level < 3:
            return False
        subclass = self.get_character_subclass(character_id)
        return bool(subclass and subclass.lower() == 'champion')

    def get_remarkable_athlete_jump_bonus(self, character_id: str) -> int:
        """Get jump distance bonus from Remarkable Athlete."""
        if not self.has_remarkable_athlete(character_id):
            return 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT strength FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()

            if not row:
                return 0

            strength = row['strength'] or 10
            str_modifier = (strength - 10) // 2
            return str_modifier

    def roll_skill_check(
        self,
        character_id: str,
        skill_name: str,
        ability_modifier: int,
        proficiency_bonus: int = 0,
        proficient: bool = False,
        expertise: bool = False,
        base_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Roll a skill check with automatic Remarkable Athlete integration."""
        from services.advantage_system import advantage_system, RollType

        context = dict(base_context or {})
        advantage_sources = list(context.pop('advantage_sources', []))
        disadvantage_sources = list(context.pop('disadvantage_sources', []))
        context['skill_name'] = skill_name

        normalized_skill = (skill_name or '').strip().lower()
        remarkable_athlete_applied = False
        if normalized_skill == 'athletics' and self.has_remarkable_athlete(character_id):
            context['remarkable_athlete'] = True
            remarkable_athlete_applied = True

        advantage_sources.extend(advantage_system.get_common_advantage_sources(RollType.SKILL_CHECK, context))
        disadvantage_sources.extend(advantage_system.get_common_disadvantage_sources(RollType.SKILL_CHECK, context))

        def _dedupe(items):
            seen = set()
            ordered = []
            for entry in items:
                if entry not in seen:
                    seen.add(entry)
                    ordered.append(entry)
            return ordered

        advantage_sources = _dedupe(advantage_sources)
        disadvantage_sources = _dedupe(disadvantage_sources)

        advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)

        total_modifier = ability_modifier
        if proficient:
            total_modifier += proficiency_bonus * (2 if expertise else 1)

        total, breakdown = advantage_system.roll_d20_with_advantage(advantage_state, total_modifier)

        return {
            'total': total,
            'breakdown': breakdown,
            'advantage_state': advantage_state.value,
            'advantage_sources': advantage_sources,
            'disadvantage_sources': disadvantage_sources,
            'remarkable_athlete_applied': remarkable_athlete_applied,
            'modifier': total_modifier
        }

    def _ensure_combat_state(self, cursor: sqlite3.Cursor, character_id: str) -> None:
        """Ensure a combat state row exists for the character."""
        # Try full insert, fall back to minimal insert for test databases
        try:
            cursor.execute(
                """
                INSERT INTO character_combat_state (character_id, studied_target_id, last_miss_turn, heroic_warrior_active, survivor_active, last_attack_missed, critical_range_min)
                VALUES (?, NULL, 0, 0, 0, 0, 20)
                ON CONFLICT(character_id) DO NOTHING
                """,
                (character_id,)
            )
        except sqlite3.OperationalError:
            # Fallback for minimal schema (test databases)
            cursor.execute(
                """
                INSERT INTO character_combat_state (character_id)
                VALUES (?)
                ON CONFLICT(character_id) DO NOTHING
                """,
                (character_id,)
            )

    def use_second_wind(self, character_id: str) -> Dict[str, Any]:
        """Use Second Wind ability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get current uses and level
            cursor.execute("""
                SELECT second_wind_uses_current, level, hit_points_current, hit_points_max, class_id
                FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()

            if not row:
                return {'success': False, 'error': 'Character not found'}

            if row['second_wind_uses_current'] <= 0:
                return {'success': False, 'error': 'No Second Wind uses remaining'}

            # Roll healing: 1d10 + fighter level
            healing_roll = random.randint(1, 10)
            total_healing = healing_roll + row['level']

            # Calculate new HP (can't exceed max)
            current_hp = row['hit_points_current']
            max_hp = row['hit_points_max']
            new_hp = min(current_hp + total_healing, max_hp)
            actual_healing = new_hp - current_hp

            # Update uses and HP
            cursor.execute("""
                UPDATE characters SET
                    second_wind_uses_current = second_wind_uses_current - 1,
                    hit_points_current = ?,
                    current_hit_points = ?
                WHERE id = ?
            """, (new_hp, new_hp, character_id))

            # Check for Tactical Shift (Level 5+)
            tactical_shift_movement = 0
            if row['class_id'].lower() == 'fighter' and row['level'] >= 5:
                # Default speed is 30 feet for most characters
                speed = 30
                tactical_shift_movement = speed // 2  # Half speed = 15 feet

                # Store tactical shift movement allowance in combat state
                self._ensure_combat_state(cursor, character_id)
                cursor.execute("""
                    UPDATE character_combat_state
                    SET tactical_shift_movement = ?
                    WHERE character_id = ?
                """, (tactical_shift_movement, character_id))

            conn.commit()

            result = {
                'success': True,
                'healing_roll': healing_roll,
                'level_bonus': row['level'],
                'total_healing': total_healing,
                'actual_healing': actual_healing,
                'new_hp': new_hp,
                'max_hp': max_hp,
                'uses_remaining': row['second_wind_uses_current'] - 1
            }

            if tactical_shift_movement > 0:
                result['tactical_shift_movement'] = tactical_shift_movement
                result['tactical_shift_active'] = True

            return result
    
    def use_action_surge(self, character_id: str) -> Dict[str, Any]:
        """Use Action Surge ability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current uses
            cursor.execute("""
                SELECT action_surge_uses_current FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'error': 'Character not found'}
            
            if row['action_surge_uses_current'] <= 0:
                return {'success': False, 'error': 'No Action Surge uses remaining'}
            
            # Update uses
            cursor.execute("""
                UPDATE characters SET action_surge_uses_current = action_surge_uses_current - 1
                WHERE id = ?
            """, (character_id,))
            
            conn.commit()
            
            return {
                'success': True,
                'uses_remaining': row['action_surge_uses_current'] - 1,
                'effect': 'Gain one additional action this turn (except Magic action)'
            }
    
    def use_tactical_mind(self, character_id: str, check_result: int, dc: int) -> Dict[str, Any]:
        """Use Tactical Mind to boost an ability check."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current Second Wind uses
            cursor.execute("""
                SELECT second_wind_uses_current, level FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'error': 'Character not found'}
            
            if row['level'] < 2:
                return {'success': False, 'error': 'Tactical Mind requires Fighter level 2'}
            
            if row['second_wind_uses_current'] <= 0:
                return {'success': False, 'error': 'No Second Wind uses remaining for Tactical Mind'}
            
            # Roll 1d10 boost
            boost_roll = random.randint(1, 10)
            new_total = check_result + boost_roll
            
            # Check if it succeeds now
            succeeds = new_total >= dc
            
            # Only consume Second Wind if it still fails
            if not succeeds:
                # Don't consume the use
                return {
                    'success': True,
                    'boost_roll': boost_roll,
                    'new_total': new_total,
                    'check_succeeds': False,
                    'second_wind_consumed': False,
                    'uses_remaining': row['second_wind_uses_current']
                }
            else:
                # Consume Second Wind use
                cursor.execute("""
                    UPDATE characters SET second_wind_uses_current = second_wind_uses_current - 1
                    WHERE id = ?
                """, (character_id,))
                conn.commit()
                
                return {
                    'success': True,
                    'boost_roll': boost_roll,
                    'new_total': new_total,
                    'check_succeeds': True,
                    'second_wind_consumed': True,
                    'uses_remaining': row['second_wind_uses_current'] - 1
                }
    
    def use_indomitable(self, character_id: str, save_roll: int, save_bonus: int) -> Dict[str, Any]:
        """Use Indomitable to reroll a failed save."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current uses and level
            cursor.execute("""
                SELECT indomitable_uses_current, level FROM characters WHERE id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'error': 'Character not found'}
            
            if row['level'] < 9:
                return {'success': False, 'error': 'Indomitable requires Fighter level 9'}
            
            if row['indomitable_uses_current'] <= 0:
                return {'success': False, 'error': 'No Indomitable uses remaining'}
            
            # Reroll with bonus equal to fighter level
            new_roll = random.randint(1, 20)
            level_bonus = row['level']
            new_total = new_roll + save_bonus + level_bonus
            
            # Update uses
            cursor.execute("""
                UPDATE characters SET indomitable_uses_current = indomitable_uses_current - 1
                WHERE id = ?
            """, (character_id,))
            
            conn.commit()
            
            return {
                'success': True,
                'new_roll': new_roll,
                'save_bonus': save_bonus,
                'level_bonus': level_bonus,
                'new_total': new_total,
                'uses_remaining': row['indomitable_uses_current'] - 1
            }
    
    def rest_fighter_resources(self, character_id: str, rest_type: str) -> None:
        """Reset fighter resources on rest."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if rest_type == 'short':
                # Restore 1 Second Wind use on short rest
                cursor.execute("""
                    UPDATE characters SET
                        second_wind_uses_current = MIN(second_wind_uses_current + 1, second_wind_uses_max),
                        action_surge_uses_current = action_surge_uses_max
                    WHERE id = ?
                """, (character_id,))
            elif rest_type == 'long':
                # Restore all uses on long rest
                cursor.execute("""
                    UPDATE characters SET
                        second_wind_uses_current = second_wind_uses_max,
                        action_surge_uses_current = action_surge_uses_max,
                        indomitable_uses_current = indomitable_uses_max
                    WHERE id = ?
                """, (character_id,))
                
                # Reset combat state
                cursor.execute("""
                    UPDATE character_combat_state SET
                        studied_target_id = NULL,
                        last_miss_turn = 0,
                        last_attack_missed = 0
                    WHERE character_id = ?
                """, (character_id,))
            
            conn.commit()
    
    def _apply_heroic_warrior(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int) -> Dict[str, Any]:
        """Internal helper to handle Heroic Warrior start-of-turn logic."""
        info = {
            "available": level >= 10,
            "triggered": False,
            "current": (character.get("inspiration_uses_current") or 0),
            "max": (character.get("inspiration_uses_max") or 0)
        }

        self._ensure_combat_state(cursor, character_id)

        if level < 10:
            cursor.execute(
                "UPDATE character_combat_state SET heroic_warrior_active = 0 WHERE character_id = ?",
                (character_id,)
            )
            return info

        current = info["current"]
        max_uses = info["max"]

        new_max = max(max_uses, 1)
        new_current = min(current, new_max)

        if new_current < 1:
            new_current = 1
            info["triggered"] = True

        if new_current != current or new_max != max_uses:
            cursor.execute(
                """
                UPDATE characters
                SET inspiration_uses_current = ?, inspiration_uses_max = ?
                WHERE id = ?
                """,
                (new_current, new_max, character_id)
            )
            character["inspiration_uses_current"] = new_current
            character["inspiration_uses_max"] = new_max

        cursor.execute(
            """
            UPDATE character_combat_state
            SET heroic_warrior_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE character_id = ?
            """,
            (1 if info["triggered"] else 0, character_id)
        )

        info["current"] = new_current
        info["max"] = new_max
        return info

    def _apply_survivor(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int) -> Dict[str, Any]:
        """Internal helper to handle Survivor start-of-turn logic."""
        info = {
            "available": level >= 18,
            "healing": 0,
            "healing_triggered": False,
            "defy_death_active": False,
            "new_hp": character.get("hit_points_current"),
            "max_hp": character.get("hit_points_max")
        }

        self._ensure_combat_state(cursor, character_id)

        if level < 18:
            cursor.execute(
                "UPDATE character_combat_state SET survivor_active = 0 WHERE character_id = ?",
                (character_id,)
            )
            return info

        info["defy_death_active"] = True

        current_hp = character.get("hit_points_current") or 0
        max_hp = character.get("hit_points_max") or 0
        con_score = character.get("constitution") or 10
        con_mod = (con_score - 10) // 2
        heal_amount = max(0, 5 + con_mod)

        if max_hp > 0 and current_hp > 0 and current_hp <= max_hp // 2 and heal_amount > 0:
            new_hp = min(current_hp + heal_amount, max_hp)
            actual_healing = new_hp - current_hp
            if actual_healing > 0:
                cursor.execute(
                    """
                    UPDATE characters
                    SET hit_points_current = ?, current_hit_points = ?
                    WHERE id = ?
                    """,
                    (new_hp, new_hp, character_id)
                )
                character["hit_points_current"] = new_hp
                info["healing"] = actual_healing
                info["healing_triggered"] = True
                info["new_hp"] = new_hp

        cursor.execute(
            """
            UPDATE character_combat_state
            SET survivor_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE character_id = ?
            """,
            (character_id,)
        )

        info["max_hp"] = character.get("hit_points_max")
        if info["new_hp"] is None:
            info["new_hp"] = character.get("hit_points_current")
        return info

    def process_champion_turn_start(self, character_id: str) -> Dict[str, Any]:
        """Apply Champion subclass start-of-turn effects and return outcome details."""
        result = {"success": True, "heroic_warrior": None, "survivor": None}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Try to get character data with inspiration columns, fall back if missing
            try:
                cursor.execute(
                    """
                    SELECT level, hit_points_current, hit_points_max, constitution,
                           inspiration_uses_current, inspiration_uses_max,
                           class_id, subclass_id
                    FROM characters
                    WHERE id = ?
                    """,
                    (character_id,)
                )
                row = cursor.fetchone()
            except sqlite3.OperationalError as e:
                if "no such column: inspiration_uses_current" in str(e):
                    # Fall back to query without inspiration columns
                    cursor.execute(
                        """
                        SELECT level, hit_points_current, hit_points_max, constitution,
                               class_id, subclass_id
                        FROM characters
                        WHERE id = ?
                        """,
                        (character_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        character = dict(row)
                        # Add default inspiration values
                        character['inspiration_uses_current'] = 0
                        character['inspiration_uses_max'] = 0
                    else:
                        return {"success": False, "error": "Character not found"}
                else:
                    raise e
            else:
                if not row:
                    return {"success": False, "error": "Character not found"}
                character = dict(row)
            level = character.get("level", 0) or 0

            subclass = (character.get("subclass_id") or "").lower()
            if not subclass and (character.get("class_id") or "").lower() == "fighter":
                cursor.execute(
                    """
                    SELECT subclass_id
                    FROM character_subclasses
                    WHERE character_id = ? AND LOWER(class_id) = 'fighter'
                    """,
                    (character_id,)
                )
                subclass_row = cursor.fetchone()
                if subclass_row and subclass_row["subclass_id"]:
                    subclass = (subclass_row["subclass_id"] or "").lower()

            if subclass != "champion":
                self._ensure_combat_state(cursor, character_id)
                cursor.execute(
                    """
                    UPDATE character_combat_state
                    SET heroic_warrior_active = 0,
                        survivor_active = CASE WHEN survivor_active IS NULL THEN 0 ELSE survivor_active END
                    WHERE character_id = ?
                    """,
                    (character_id,)
                )
                conn.commit()
                return result

            hero_info = self._apply_heroic_warrior(cursor, character_id, character, level)
            survivor_info = self._apply_survivor(cursor, character_id, character, level)

            conn.commit()

        result["heroic_warrior"] = hero_info
        result["survivor"] = survivor_info
        return result

    def check_heroic_warrior(self, character_id: str) -> Dict[str, Any]:
        """Public wrapper to process Heroic Warrior start-of-turn effect."""
        result = self.process_champion_turn_start(character_id)
        hero_info = result.get("heroic_warrior") or {}
        hero_info["success"] = result.get("success", True)
        return hero_info

    def check_survivor(self, character_id: str) -> Dict[str, Any]:
        """Public wrapper to process Survivor start-of-turn effect."""
        result = self.process_champion_turn_start(character_id)
        survivor_info = result.get("survivor") or {}
        survivor_info["success"] = result.get("success", True)
        return survivor_info

    def has_defy_death(self, character_id: str) -> bool:
        """Check if character has Defy Death (Champion 18)."""
        level = self.get_fighter_level(character_id)
        if level < 18:
            return False
        subclass = self.get_character_subclass(character_id)
        return bool(subclass and subclass.lower() == 'champion')

    def roll_death_save(self, character_id: str) -> Dict[str, Any]:
        """Roll a death saving throw with Defy Death if available."""
        has_defy = self.has_defy_death(character_id)

        # Roll with advantage if Defy Death
        if has_defy:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll = max(roll1, roll2)
            advantage_used = True
        else:
            roll = random.randint(1, 20)
            advantage_used = False

        # Defy Death: 18-20 counts as nat 20
        if has_defy and roll >= 18:
            roll = 20

        success = roll >= 10
        critical_success = roll == 20
        critical_failure = roll == 1

        return {
            'roll': roll,
            'success': success,
            'critical_success': critical_success,
            'critical_failure': critical_failure,
            'advantage_used': advantage_used,
            'defy_death_active': has_defy
        }
    
    def update_studied_attacks(self, character_id: str, target_id: str, hit: bool) -> None:
        """Update Studied Attacks state after an attack."""
        level = self.get_fighter_level(character_id)
        if level < 13:
            return
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if hit:
                # Clear studied target on hit
                cursor.execute("""
                    UPDATE character_combat_state SET
                        studied_target_id = NULL,
                        last_attack_missed = 0
                    WHERE character_id = ?
                """, (character_id,))
            else:
                # Set studied target on miss
                cursor.execute("""
                    INSERT INTO character_combat_state (character_id, studied_target_id, last_attack_missed)
                    VALUES (?, ?, 1)
                    ON CONFLICT(character_id) DO UPDATE SET
                        studied_target_id = ?,
                        last_attack_missed = 1
                """, (character_id, target_id, target_id))
            
            conn.commit()
    
    def has_studied_attacks_advantage(self, character_id: str, target_id: str) -> bool:
        """Check if character has advantage from Studied Attacks."""
        level = self.get_fighter_level(character_id)
        if level < 13:
            return False
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studied_target_id, last_attack_missed
                FROM character_combat_state
                WHERE character_id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
                
            return (row['studied_target_id'] == target_id and 
                    row['last_attack_missed'] == 1)
