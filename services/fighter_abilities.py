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
            
            if row and row['class_id'] == 'fighter':
                return row['level']
            return 0
    
    def update_fighter_resources_for_level(self, character_id: str, level: int) -> None:
        """Update fighter resource maximums based on level."""
        # Second Wind uses
        if level >= 1:
            second_wind_max = 2  # Base 2 uses
            if level >= 4:
                second_wind_max = 3
            if level >= 10:
                second_wind_max = 4
        else:
            second_wind_max = 0
            
        # Action Surge uses
        action_surge_max = 1 if level >= 2 else 0
        if level >= 17:
            action_surge_max = 2
            
        # Indomitable uses
        indomitable_max = 0
        if level >= 9:
            indomitable_max = 1
        if level >= 13:
            indomitable_max = 2
        if level >= 17:
            indomitable_max = 3
            
        # Weapon Mastery count
        weapon_mastery_count = 0
        if level >= 1:
            weapon_mastery_count = 3
        if level >= 4:
            weapon_mastery_count = 4
        if level >= 10:
            weapon_mastery_count = 5
        if level >= 16:
            weapon_mastery_count = 6
            
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
    def use_second_wind(self, character_id: str) -> Dict[str, Any]:
        """Use Second Wind ability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current uses and level
            cursor.execute("""
                SELECT second_wind_uses_current, level, hit_points_current, hit_points_max
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
            
            conn.commit()
            
            return {
                'success': True,
                'healing_roll': healing_roll,
                'level_bonus': row['level'],
                'total_healing': total_healing,
                'actual_healing': actual_healing,
                'new_hp': new_hp,
                'max_hp': max_hp,
                'uses_remaining': row['second_wind_uses_current'] - 1
            }
    
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
    
    def check_heroic_warrior(self, character_id: str) -> Dict[str, Any]:
        """Check and apply Heroic Warrior healing (Champion level 10)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get character info
            cursor.execute("""
                SELECT c.level, c.subclass_id, c.hit_points_current, c.hit_points_max, c.constitution
                FROM characters c
                WHERE c.id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'error': 'Character not found'}
            
            # Check if Champion level 10+
            if row['subclass_id'] != 'champion' or row['level'] < 10:
                return {'success': False, 'error': 'Not a Champion of sufficient level'}
            
            # Check if at or below half HP
            if row['hit_points_current'] > row['hit_points_max'] // 2:
                return {'success': False, 'error': 'Above half hit points'}
            
            if row['hit_points_current'] <= 0:
                return {'success': False, 'error': 'Cannot heal at 0 HP'}
            
            # Calculate healing
            con_mod = (row['constitution'] - 10) // 2
            healing = 5 + con_mod
            
            # Apply healing
            new_hp = min(row['hit_points_current'] + healing, row['hit_points_max'])
            actual_healing = new_hp - row['hit_points_current']
            
            cursor.execute("""
                UPDATE characters SET
                    hit_points_current = ?,
                    current_hit_points = ?
                WHERE id = ?
            """, (new_hp, new_hp, character_id))
            
            conn.commit()
            
            return {
                'success': True,
                'healing': healing,
                'actual_healing': actual_healing,
                'new_hp': new_hp
            }
    
    def check_survivor(self, character_id: str) -> Dict[str, Any]:
        """Check and apply Survivor healing (Champion level 18)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get character info
            cursor.execute("""
                SELECT c.level, c.subclass_id, c.hit_points_current, c.hit_points_max, c.constitution
                FROM characters c
                WHERE c.id = ?
            """, (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'error': 'Character not found'}
            
            # Check if Champion level 18+
            if row['subclass_id'] != 'champion' or row['level'] < 18:
                return {'success': False, 'error': 'Not a Champion of sufficient level'}
            
            # Check if at or below half HP
            if row['hit_points_current'] > row['hit_points_max'] // 2:
                return {'success': False, 'error': 'Above half hit points'}
            
            if row['hit_points_current'] <= 0:
                return {'success': False, 'error': 'Cannot heal at 0 HP'}
            
            # Calculate healing
            con_mod = (row['constitution'] - 10) // 2
            healing = 10 + con_mod
            
            # Apply healing
            new_hp = min(row['hit_points_current'] + healing, row['hit_points_max'])
            actual_healing = new_hp - row['hit_points_current']
            
            cursor.execute("""
                UPDATE characters SET
                    hit_points_current = ?,
                    current_hit_points = ?
                WHERE id = ?
            """, (new_hp, new_hp, character_id))
            
            conn.commit()
            
            return {
                'success': True,
                'healing': healing,
                'actual_healing': actual_healing,
                'new_hp': new_hp
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
