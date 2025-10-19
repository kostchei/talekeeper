# core
# category: core
import sqlite3
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

class MoraleManager:
    """
    Manages enemy morale system for D&D combat.

    Morale Rules:
    - Enemies flee when reduced below 50% of their number (groups) or 50% HP (solo)
    - DC 15 Wisdom save to avoid fleeing
    - For groups, use highest surviving enemy's WIS modifier
    - On failure: enemies flee, players get full XP, loot, and one final attack
    """

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._ensure_morale_table()

    def _ensure_morale_table(self):
        """Ensure combat_morale_status table exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combat_morale_status (
                    encounter_id TEXT NOT NULL,
                    monster_id TEXT NOT NULL,
                    monster_name TEXT NOT NULL,
                    initial_count INTEGER NOT NULL,
                    initial_hp INTEGER NOT NULL,
                    current_count INTEGER NOT NULL,
                    morale_broken BOOLEAN DEFAULT 0,
                    morale_check_passed BOOLEAN DEFAULT NULL,
                    morale_roll INTEGER,
                    morale_modifier INTEGER,
                    check_timestamp DATETIME,
                    PRIMARY KEY (encounter_id, monster_id)
                )
            """)
            conn.commit()
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    def track_combat_start(self, encounter_id: str, monster_id: str, monster_name: str,
                          initial_count: int, initial_hp: int):
        """Record initial monster state for morale tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO combat_morale_status
                (encounter_id, monster_id, monster_name, initial_count, initial_hp, current_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (encounter_id, monster_id, monster_name, initial_count, initial_hp, initial_count))

            conn.commit()
        except Exception as e:
            print(f"[MORALE] Error tracking combat start: {e}")
        finally:
            if conn:
                conn.close()

    def update_monster_count(self, encounter_id: str, monster_id: str, current_count: int):
        """Update current monster count for morale tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE combat_morale_status
                SET current_count = ?
                WHERE encounter_id = ? AND monster_id = ?
            """, (current_count, encounter_id, monster_id))

            conn.commit()
        except Exception as e:
            print(f"[MORALE] Error updating count: {e}")
        finally:
            if conn:
                conn.close()

    def check_morale_trigger(self, encounter_id: str, monster_id: str,
                           current_hp: int, is_solo: bool = False) -> bool:
        """
        Check if morale threshold has been crossed.

        Args:
            encounter_id: Combat encounter ID
            monster_id: Monster ID
            current_hp: Current HP of the monster (for solo check)
            is_solo: True if single monster, False if group

        Returns:
            True if morale check should be triggered
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT initial_count, initial_hp, current_count, morale_broken, morale_check_passed
                FROM combat_morale_status
                WHERE encounter_id = ? AND monster_id = ?
            """, (encounter_id, monster_id))

            row = cursor.fetchone()
            if not row:
                return False

            initial_count, initial_hp, current_count, morale_broken, morale_check_passed = row

            if morale_broken or morale_check_passed is not None:
                return False

            if is_solo:
                threshold_hp = initial_hp * 0.5
                return current_hp < threshold_hp
            else:
                threshold_count = initial_count * 0.5
                return current_count < threshold_count

        except Exception as e:
            print(f"[MORALE] Error checking trigger: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_wisdom_modifier(self, monster_id: str) -> int:
        """Get Wisdom modifier for a monster"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT wisdom FROM monsters WHERE id = ?", (monster_id,))
            row = cursor.fetchone()

            if row:
                wisdom = row[0] or 10
                return (wisdom - 10) // 2

            return 0

        except Exception:
            return 0
        finally:
            if conn:
                conn.close()

    def get_highest_wisdom_modifier(self, monster_ids: List[str]) -> int:
        """Get highest Wisdom modifier from a group of monsters"""
        if not monster_ids:
            return 0

        modifiers = [self.get_wisdom_modifier(mid) for mid in monster_ids]
        return max(modifiers) if modifiers else 0

    def roll_morale_check(self, encounter_id: str, monster_id: str,
                         group_monster_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Roll a morale check (DC 15 Wisdom save).

        Args:
            encounter_id: Combat encounter ID
            monster_id: Primary monster ID
            group_monster_ids: List of all monster IDs in the group (for highest WIS)

        Returns:
            Dict with 'passed', 'roll', 'modifier', 'total', 'dc'
        """
        dc = 15
        d20_roll = random.randint(1, 20)

        if group_monster_ids and len(group_monster_ids) > 1:
            modifier = self.get_highest_wisdom_modifier(group_monster_ids)
        else:
            modifier = self.get_wisdom_modifier(monster_id)

        total = d20_roll + modifier
        passed = total >= dc

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE combat_morale_status
                SET morale_check_passed = ?,
                    morale_broken = ?,
                    morale_roll = ?,
                    morale_modifier = ?,
                    check_timestamp = ?
                WHERE encounter_id = ? AND monster_id = ?
            """, (passed, not passed, d20_roll, modifier, datetime.now(), encounter_id, monster_id))

            conn.commit()
        except Exception as e:
            print(f"[MORALE] Error saving morale check: {e}")
        finally:
            if conn:
                conn.close()

        return {
            'passed': passed,
            'roll': d20_roll,
            'modifier': modifier,
            'total': total,
            'dc': dc
        }

    def get_morale_status(self, encounter_id: str, monster_id: str) -> Optional[Dict[str, Any]]:
        """Get current morale status for a monster"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT monster_name, initial_count, initial_hp, current_count,
                       morale_broken, morale_check_passed, morale_roll, morale_modifier
                FROM combat_morale_status
                WHERE encounter_id = ? AND monster_id = ?
            """, (encounter_id, monster_id))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'monster_name': row[0],
                'initial_count': row[1],
                'initial_hp': row[2],
                'current_count': row[3],
                'morale_broken': bool(row[4]),
                'morale_check_passed': bool(row[5]) if row[5] is not None else None,
                'morale_roll': row[6],
                'morale_modifier': row[7]
            }

        except Exception as e:
            print(f"[MORALE] Error getting status: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def clear_encounter_morale(self, encounter_id: str):
        """Clear morale tracking for an encounter (called when combat ends)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM combat_morale_status WHERE encounter_id = ?",
                         (encounter_id,))
            conn.commit()
        except Exception as e:
            print(f"[MORALE] Error clearing morale: {e}")
        finally:
            if conn:
                conn.close()
