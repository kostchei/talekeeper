# core
# category: core
import sqlite3
import random
from typing import Dict, List, Any, Optional
from datetime import datetime


class DowntimeActivityService:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS downtime_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    result_text TEXT NOT NULL,
                    gold_spent INTEGER DEFAULT 0,
                    gold_gained INTEGER DEFAULT 0,
                    inspiration_gained INTEGER DEFAULT 0,
                    days_spent INTEGER DEFAULT 1,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating downtime_activities table: {e}")

    def carousing(self, character_id: str, character_level: int) -> Dict[str, Any]:
        character_data = self._get_character_data(character_id)
        if not character_data:
            return {'success': False, 'error': 'Character not found'}

        lifestyle_cost = self._calculate_lifestyle_cost('wealthy', character_level)

        if character_data['gold'] < lifestyle_cost:
            return {
                'success': False,
                'error': f'Not enough gold. Need {lifestyle_cost} gp for carousing (wealthy lifestyle).'
            }

        roll = random.randint(1, 100) + character_level
        result = self._resolve_carousing_result(roll, lifestyle_cost)

        gold_change_total = -lifestyle_cost + result['gold_change']
        new_gold = character_data['gold'] + gold_change_total
        inspiration_gained = result.get('inspiration_gained', 0)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_inventory
            SET quantity = quantity + ?
            WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
        """, (gold_change_total, character_id))

        cursor.execute("""
            UPDATE characters
            SET inspiration_uses_current = MIN(inspiration_uses_max, inspiration_uses_current + ?)
            WHERE id = ?
        """, (inspiration_gained, character_id))

        cursor.execute("""
            INSERT INTO downtime_activities
            (character_id, activity_type, result_text, gold_spent, gold_gained, inspiration_gained, days_spent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id,
            'carousing',
            result['description'],
            lifestyle_cost,
            result['gold_change'] if result['gold_change'] > 0 else 0,
            inspiration_gained,
            1,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return {
            'success': True,
            'activity': 'Carousing',
            'roll': roll - character_level,
            'modified_roll': roll,
            'description': result['description'],
            'gold_spent': lifestyle_cost,
            'gold_change': result['gold_change'],
            'new_gold': new_gold,
            'inspiration_gained': inspiration_gained,
            'special_effect': result.get('special_effect', '')
        }

    def _resolve_carousing_result(self, roll: int, lifestyle_cost: int) -> Dict[str, Any]:
        if roll <= 10:
            return {
                'description': 'You are jailed for 1d4 days on charges of disorderly conduct and disturbing the peace. You can pay a fine of 10 gp to avoid jail time.',
                'gold_change': -10,
                'special_effect': 'jailed_1d4_days'
            }
        elif roll <= 20:
            gold_lost = random.randint(3, 18) * 5
            return {
                'description': f'You regain consciousness in a strange place with no memory of how you got there. You have been robbed of {gold_lost} gp.',
                'gold_change': -gold_lost,
                'special_effect': 'robbed'
            }
        elif roll <= 30:
            return {
                'description': 'You make an enemy. This person, business, or organization is now hostile to you.',
                'gold_change': 0,
                'special_effect': 'enemy_made'
            }
        elif roll <= 40:
            romance_roll = random.randint(1, 20)
            if romance_roll <= 5:
                desc = 'You are caught up in a whirlwind romance, but it ends badly.'
            elif romance_roll <= 10:
                desc = 'You are caught up in a whirlwind romance that ends amicably.'
            else:
                desc = 'You are caught up in a whirlwind romance that is still ongoing.'
            return {
                'description': desc,
                'gold_change': 0,
                'inspiration_gained': 1,
                'special_effect': 'romance'
            }
        elif roll <= 80:
            return {
                'description': 'You earn modest winnings from gambling and recuperate your lifestyle expenses.',
                'gold_change': lifestyle_cost,
                'special_effect': 'broke_even'
            }
        elif roll <= 90:
            winnings = random.randint(1, 20) * 4
            return {
                'description': f'You earn modest winnings from gambling. You recuperate your lifestyle expenses and gain {winnings} gp.',
                'gold_change': lifestyle_cost + winnings,
                'special_effect': 'modest_winnings'
            }
        else:
            winnings = random.randint(4, 24) * 10
            return {
                'description': f'You make a small fortune gambling! You recuperate your lifestyle expenses and gain {winnings} gp. Your carousing becomes the stuff of local legend.',
                'gold_change': lifestyle_cost + winnings,
                'inspiration_gained': 0,
                'special_effect': 'legendary_win'
            }

    def prayer(self, character_id: str, character_level: int) -> Dict[str, Any]:
        character_data = self._get_character_data(character_id)
        if not character_data:
            return {'success': False, 'error': 'Character not found'}

        prayer_cost = 5 * character_level
        lifestyle_cost = self._calculate_lifestyle_cost('modest', character_level) * 2
        total_cost = prayer_cost + lifestyle_cost

        if character_data['gold'] < total_cost:
            return {
                'success': False,
                'error': f'Not enough gold. Need {total_cost} gp ({prayer_cost} gp donation + {lifestyle_cost} gp modest lifestyle for 2 days).'
            }

        new_gold = character_data['gold'] - total_cost
        inspiration_gained = 1

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_inventory
            SET quantity = quantity - ?
            WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
        """, (total_cost, character_id))

        cursor.execute("""
            UPDATE characters
            SET inspiration_uses_current = MIN(inspiration_uses_max, inspiration_uses_current + ?)
            WHERE id = ?
        """, (inspiration_gained, character_id))

        cursor.execute("""
            INSERT INTO downtime_activities
            (character_id, activity_type, result_text, gold_spent, gold_gained, inspiration_gained, days_spent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id,
            'prayer',
            'You spend time in prayer and contemplation, gaining divine favor.',
            total_cost,
            0,
            inspiration_gained,
            2,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return {
            'success': True,
            'activity': 'Prayer',
            'description': 'You spend 2 days in prayer and contemplation, making a donation to your deity. You gain divine inspiration.',
            'gold_spent': total_cost,
            'breakdown': {
                'donation': prayer_cost,
                'lifestyle': lifestyle_cost
            },
            'new_gold': new_gold,
            'inspiration_gained': inspiration_gained
        }

    def _calculate_lifestyle_cost(self, lifestyle: str, character_level: int) -> int:
        base_costs = {
            'wretched': 0,
            'squalid': 1,
            'poor': 2,
            'modest': 10,
            'comfortable': 20,
            'wealthy': 40,
            'aristocratic': 100
        }
        return base_costs.get(lifestyle, 10)

    def _get_character_data(self, character_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level, inspiration_uses_current, inspiration_uses_max
                FROM characters
                WHERE id = ?
            """, (character_id,))
            char_row = cursor.fetchone()

            if not char_row:
                conn.close()
                return None

            cursor.execute("""
                SELECT quantity FROM character_inventory
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
            """, (character_id,))
            gold_row = cursor.fetchone()

            conn.close()

            return {
                'gold': gold_row[0] if gold_row else 0,
                'level': char_row[0],
                'inspiration_current': char_row[1] if char_row[1] is not None else 0,
                'inspiration_max': char_row[2] if char_row[2] is not None else 1
            }
        except Exception as e:
            print(f"Error getting character data: {e}")
            return None

    def get_activity_history(self, character_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT activity_type, result_text, gold_spent, gold_gained,
                       inspiration_gained, days_spent, timestamp
                FROM downtime_activities
                WHERE character_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (character_id, limit))

            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'type': row[0],
                    'description': row[1],
                    'gold_spent': row[2],
                    'gold_gained': row[3],
                    'inspiration_gained': row[4],
                    'days_spent': row[5],
                    'timestamp': row[6]
                })

            conn.close()
            return activities
        except Exception as e:
            print(f"Error getting activity history: {e}")
            return []
