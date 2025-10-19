import sqlite3
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .hex_coordinate_system import HexCoordinateSystem

class HexMapService:

    TERRAIN_TYPES = ['plains', 'forest', 'mountain', 'hills', 'swamp', 'desert']

    BIOMES = {
        'plains': {'move_cost': 1.0, 'encounter_rate': 0.3},
        'forest': {'move_cost': 1.2, 'encounter_rate': 0.5},
        'mountain': {'move_cost': 1.5, 'encounter_rate': 0.4},
        'hills': {'move_cost': 1.2, 'encounter_rate': 0.35},
        'swamp': {'move_cost': 1.5, 'encounter_rate': 0.6},
        'desert': {'move_cost': 1.3, 'encounter_rate': 0.2}
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.coord_system = HexCoordinateSystem()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_character_position(self, character_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT character_id FROM character_hex_position WHERE character_id = ?',
            (character_id,)
        )

        needs_init = not cursor.fetchone()

        if needs_init:
            cursor.execute(
                'INSERT INTO character_hex_position (character_id, current_q, current_r, facing_direction) VALUES (?, 0, 0, 0)',
                (character_id,)
            )
            conn.commit()

        conn.close()

        if needs_init:
            self._generate_hex(character_id, 0, 0)
            self._mark_hex_visited(character_id, 0, 0)

            for direction in range(6):
                neighbor_q, neighbor_r = self.coord_system.get_neighbor(0, 0, direction)
                self._generate_hex(character_id, neighbor_q, neighbor_r)
                self._reveal_hex(character_id, neighbor_q, neighbor_r)

    def get_character_position(self, character_id: str) -> Tuple[int, int]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT current_q, current_r FROM character_hex_position WHERE character_id = ?',
            (character_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return (row['current_q'], row['current_r'])
        return (0, 0)

    def _generate_hex(self, character_id: str, q: int, r: int) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM character_hex_map WHERE character_id = ? AND q = ? AND r = ?',
            (character_id, q, r)
        )

        existing = cursor.fetchone()
        if existing:
            conn.close()
            return dict(existing)

        distance = self.coord_system.get_distance(0, 0, q, r)
        seed = self._get_position_seed(q, r)
        random.seed(seed)

        terrain = random.choice(self.TERRAIN_TYPES)
        biome = terrain

        settlement_type = self._generate_settlement_type()

        cursor.execute('''
            INSERT INTO character_hex_map
            (character_id, q, r, terrain_type, biome, encounter_seed, revealed, visited, settlement_type)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
        ''', (character_id, q, r, terrain, biome, seed, settlement_type))

        conn.commit()

        cursor.execute(
            'SELECT * FROM character_hex_map WHERE character_id = ? AND q = ? AND r = ?',
            (character_id, q, r)
        )
        result = dict(cursor.fetchone())
        conn.close()

        return result

    def _generate_settlement_type(self) -> str:
        settlement_roll = random.randint(1, 100)

        if settlement_roll <= 6:
            return 'empty'
        elif settlement_roll <= 31:
            return 'hamlet'
        elif settlement_roll <= 99:
            return 'village'
        else:
            town_roll = random.randint(1, 6)
            if town_roll <= 3:
                return 'town_small'
            elif town_roll <= 5:
                return 'town_medium'
            else:
                return 'town_large'

    def _get_position_seed(self, q: int, r: int) -> int:
        return hash(f"{q},{r}") % (2**31)

    def _reveal_hex(self, character_id: str, q: int, r: int):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE character_hex_map
            SET revealed = 1
            WHERE character_id = ? AND q = ? AND r = ? AND revealed = 0
        ''', (character_id, q, r))

        conn.commit()
        conn.close()

    def _mark_hex_visited(self, character_id: str, q: int, r: int):
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            UPDATE character_hex_map
            SET visited = 1,
                last_visited_date = ?,
                visit_count = visit_count + 1,
                first_visited_date = COALESCE(first_visited_date, ?)
            WHERE character_id = ? AND q = ? AND r = ?
        ''', (now, now, character_id, q, r))

        conn.commit()
        conn.close()

    def get_hex(self, character_id: str, q: int, r: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM character_hex_map WHERE character_id = ? AND q = ? AND r = ?',
            (character_id, q, r)
        )

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_visible_hexes(self, character_id: str, center_q: int, center_r: int, radius: int = 3) -> List[Dict]:
        hexes = self.coord_system.get_hexes_in_radius(center_q, center_r, radius)
        results = []

        for q, r in hexes:
            hex_data = self.get_hex(character_id, q, r)
            if hex_data:
                results.append(hex_data)
            else:
                results.append({
                    'character_id': character_id,
                    'q': q,
                    'r': r,
                    'terrain_type': 'unknown',
                    'biome': 'unknown',
                    'revealed': 0,
                    'visited': 0
                })

        return results

    def travel_to_hex(self, character_id: str, target_q: int, target_r: int) -> Dict:
        current_q, current_r = self.get_character_position(character_id)

        if self.coord_system.get_distance(current_q, current_r, target_q, target_r) != 1:
            raise ValueError("Can only travel to adjacent hexes")

        hex_data = self._generate_hex(character_id, target_q, target_r)
        self._mark_hex_visited(character_id, target_q, target_r)

        conn = self._get_connection()
        cursor = conn.cursor()

        direction = self.coord_system.get_direction_index(current_q, current_r, target_q, target_r)
        cursor.execute('''
            UPDATE character_hex_position
            SET current_q = ?, current_r = ?, facing_direction = ?
            WHERE character_id = ?
        ''', (target_q, target_r, direction, character_id))

        conn.commit()
        conn.close()

        for neighbor_dir in range(6):
            neighbor_q, neighbor_r = self.coord_system.get_neighbor(target_q, target_r, neighbor_dir)
            self._generate_hex(character_id, neighbor_q, neighbor_r)
            self._reveal_hex(character_id, neighbor_q, neighbor_r)

        return hex_data

    def get_hex_settlement(self, character_id: str, q: int, r: int) -> Optional[str]:
        hex_data = self.get_hex(character_id, q, r)
        return hex_data.get('settlement_type') if hex_data else None

    def get_exploration_stats(self, character_id: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_hexes,
                SUM(visited) as visited_hexes,
                SUM(cleared) as cleared_hexes
            FROM character_hex_map
            WHERE character_id = ?
        ''', (character_id,))

        stats = dict(cursor.fetchone())

        cursor.execute('''
            SELECT COUNT(*) as total_events
            FROM hex_events
            WHERE character_id = ?
        ''', (character_id,))

        stats.update(dict(cursor.fetchone()))

        conn.close()
        return stats
