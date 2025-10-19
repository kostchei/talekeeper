# core
# category: core
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class HexEventLogger:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def log_travel_event(self, character_id: str, q: int, r: int, hex_data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        narrative = f"Entered {hex_data['biome']} terrain at coordinates ({q}, {r})"

        cursor.execute('''
            INSERT INTO hex_events
            (character_id, hex_q, hex_r, event_type, event_date, character_level, narrative, outcome)
            VALUES (?, ?, ?, 'travel', ?, ?, ?, 'entered')
        ''', (character_id, q, r, datetime.now().isoformat(), self._get_character_level(character_id), narrative))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def log_combat_event(self, character_id: str, q: int, r: int, combat_result: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        narrative = self._generate_combat_narrative(combat_result)
        outcome = 'victory' if combat_result.get('won') else 'defeat'

        cursor.execute('''
            INSERT INTO hex_events
            (character_id, hex_q, hex_r, event_type, event_date, character_level, narrative, outcome)
            VALUES (?, ?, ?, 'combat', ?, ?, ?, ?)
        ''', (character_id, q, r, datetime.now().isoformat(), combat_result.get('character_level', 1), narrative, outcome))

        event_id = cursor.lastrowid

        for enemy in combat_result.get('enemies', []):
            cursor.execute('''
                INSERT INTO hex_combat_log
                (hex_event_id, monster_name, monster_cr, quantity, killed, fled, combat_rounds, damage_dealt, damage_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                enemy.get('name'),
                enemy.get('cr', 0),
                enemy.get('quantity', 1),
                enemy.get('killed', 0),
                enemy.get('fled', 0),
                combat_result.get('rounds', 0),
                combat_result.get('damage_dealt', 0),
                combat_result.get('damage_taken', 0)
            ))

        for item in combat_result.get('loot', []):
            cursor.execute('''
                INSERT INTO hex_loot_log
                (hex_event_id, item_name, item_type, quantity, value_gp, equipped, sold)
                VALUES (?, ?, ?, ?, ?, 0, 0)
            ''', (
                event_id,
                item.get('name'),
                item.get('type', 'misc'),
                item.get('quantity', 1),
                item.get('value', 0)
            ))

        conn.commit()
        conn.close()

        return event_id

    def log_resource_event(self, character_id: str, q: int, r: int, resource_data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        narrative = f"Discovered {resource_data['name']}"
        if resource_data.get('value'):
            narrative += f" worth {resource_data['value']} gp"

        cursor.execute('''
            INSERT INTO hex_events
            (character_id, hex_q, hex_r, event_type, event_date, character_level, narrative, outcome)
            VALUES (?, ?, ?, 'resource', ?, ?, ?, 'success')
        ''', (character_id, q, r, datetime.now().isoformat(), self._get_character_level(character_id), narrative))

        event_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO hex_loot_log
            (hex_event_id, item_name, item_type, quantity, value_gp, equipped, sold)
            VALUES (?, ?, ?, ?, ?, 0, 0)
        ''', (
            event_id,
            resource_data.get('name'),
            resource_data.get('type', 'resource'),
            resource_data.get('quantity', 1),
            resource_data.get('value', 0)
        ))

        conn.commit()
        conn.close()

        return event_id

    def log_landmark_event(self, character_id: str, q: int, r: int, landmark_data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        narrative = f"Discovered: {landmark_data['name']}"
        if landmark_data.get('description'):
            narrative += f"\n{landmark_data['description']}"

        cursor.execute('''
            INSERT INTO hex_events
            (character_id, hex_q, hex_r, event_type, event_date, character_level, narrative, outcome)
            VALUES (?, ?, ?, 'landmark', ?, ?, ?, 'discovered')
        ''', (character_id, q, r, datetime.now().isoformat(), self._get_character_level(character_id), narrative))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def get_hex_events(self, character_id: str, q: int, r: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM hex_events
            WHERE character_id = ? AND hex_q = ? AND hex_r = ?
            ORDER BY event_date DESC
        ''', (character_id, q, r))

        events = [dict(row) for row in cursor.fetchall()]

        for event in events:
            if event['event_type'] == 'combat':
                cursor.execute('''
                    SELECT * FROM hex_combat_log WHERE hex_event_id = ?
                ''', (event['id'],))
                event['combat_log'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute('''
                SELECT * FROM hex_loot_log WHERE hex_event_id = ?
            ''', (event['id'],))
            event['loot_log'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return events

    def get_all_character_events(self, character_id: str) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM hex_events
            WHERE character_id = ?
            ORDER BY event_date DESC
        ''', (character_id,))

        events = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return events

    def _generate_combat_narrative(self, combat_result: Dict) -> str:
        parts = []

        enemies = combat_result.get('enemies', [])
        if enemies:
            enemy_desc = self._format_enemy_list(enemies)
            parts.append(f"Encountered {enemy_desc}")

        rounds = combat_result.get('rounds', 0)
        if rounds:
            parts.append(f"Combat lasted {rounds} rounds")

        if combat_result.get('won'):
            killed = [e for e in enemies if e.get('killed')]
            if killed:
                parts.append(f"Defeated: {self._format_enemy_list(killed)}")

            loot = combat_result.get('loot', [])
            if loot:
                parts.append(f"Looted: {len(loot)} items")
        else:
            parts.append("Retreated from combat")

        damage_dealt = combat_result.get('damage_dealt', 0)
        damage_taken = combat_result.get('damage_taken', 0)
        parts.append(f"Damage dealt: {damage_dealt}")
        parts.append(f"Damage taken: {damage_taken}")

        return "\n".join(parts)

    def _format_enemy_list(self, enemies: List[Dict]) -> str:
        if not enemies:
            return "Unknown enemies"

        parts = []
        for enemy in enemies:
            quantity = enemy.get('quantity', 1)
            name = enemy.get('name', 'Unknown')
            cr = enemy.get('cr', 0)
            if quantity > 1:
                parts.append(f"{quantity}x {name} (CR {cr})")
            else:
                parts.append(f"{name} (CR {cr})")

        return ", ".join(parts)

    def _get_character_level(self, character_id: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT level FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()
        conn.close()

        return row['level'] if row else 1
