# core
# category: core
import sqlite3
import random
from typing import Optional, List, Dict, Any

XP_BY_LEVEL_LOW = {
    1: 50, 2: 100, 3: 150, 4: 250, 5: 500,
    6: 600, 7: 750, 8: 900, 9: 1100, 10: 1300,
    11: 1600, 12: 1900, 13: 2200, 14: 2600, 15: 3000,
    16: 3500, 17: 4000, 18: 4700, 19: 5400, 20: 6300
}

class HazardService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def get_hazards_for_level(self, character_level: int) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM hazards
            WHERE level_min <= ? AND level_max >= ?
            ORDER BY name
        """, (character_level, character_level))

        rows = cursor.fetchall()
        conn.close()

        hazards = []
        for row in rows:
            hazard = dict(row)
            hazard['xp'] = XP_BY_LEVEL_LOW.get(character_level, 50)
            hazards.append(hazard)

        return hazards

    def get_random_hazard(self, character_level: int) -> Optional[Dict[str, Any]]:
        hazards = self.get_hazards_for_level(character_level)
        if not hazards:
            return None
        return random.choice(hazards)

    def get_hazard_by_id(self, hazard_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM hazards WHERE id = ?", (hazard_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def apply_gear_bonus(self, hazard: Dict[str, Any], gear_items: List[str]) -> Dict[str, int]:
        bonuses = {
            'dc_reduction': 0,
            'damage_reduction': 0,
            'advantage': False
        }

        hazard_name = hazard.get('name', '').lower()
        save_type = hazard.get('save_type', '').lower()

        for item in gear_items:
            item_lower = item.lower()

            if 'rope' in item_lower and 'quicksand' in hazard_name:
                bonuses['advantage'] = True

            if 'armor' in item_lower or 'shield' in item_lower:
                if 'rockslide' in hazard_name or 'collapsing' in hazard_name:
                    bonuses['damage_reduction'] = 5

            if 'cloak' in item_lower or 'mantle' in item_lower:
                if 'fire' in hazard_name.lower() or 'inferno' in hazard_name:
                    bonuses['damage_reduction'] = 3

            if 'boots' in item_lower and 'dexterity' in save_type:
                bonuses['dc_reduction'] = 1

            if 'mask' in item_lower or 'respirator' in item_lower:
                if 'gas' in hazard_name or 'fumes' in hazard_name or 'mold' in hazard_name:
                    bonuses['advantage'] = True

            if 'gloves' in item_lower and 'slime' in hazard_name:
                bonuses['dc_reduction'] = 2

            if "climber" in item_lower and 'kit' in item_lower:
                if 'collapsing' in hazard_name or 'rockslide' in hazard_name or 'falling' in hazard_name:
                    bonuses['damage_cap_2d6'] = True

            if 'cold weather' in item_lower or 'bedroll' in item_lower or 'blanket' in item_lower:
                if 'cold' in hazard_name or 'frigid' in hazard_name:
                    bonuses['advantage'] = True

        return bonuses