# core
# core
"""
Equipment database helper functions for TaleKeeper.
Provides database access methods for equipment data.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional


class EquipmentDatabase:
    """Helper class for accessing equipment data from the database."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
    def _infer_base_weapon_name(self, name: str) -> Optional[str]:
        """Infer the non-magical base weapon name from a variant."""
        if not name:
            return None
        base = name.strip()
        if ' +' in base:
            base = base.split(' +')[0].strip()
        elif '(' in base and base.endswith(')'):
            start = base.index('(') + 1
            end = base.rindex(')')
            inside = base[start:end].strip()
            if inside:
                base = inside
        return base if base and base != name else None

    def _fetch_base_weapon(self, conn: sqlite3.Connection, base_name: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name, weapon_category, damage_dice, damage_type,
                   weapon_properties, weapon_mastery, range_normal,
                   range_long, versatile_damage
            FROM equipment
            WHERE name = ?
            """,
            (base_name,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        item = dict(row)
        if item.get('weapon_properties'):
            try:
                item['weapon_properties'] = json.loads(item['weapon_properties'])
            except json.JSONDecodeError:
                item['weapon_properties'] = []
        return item

    def _hydrate_weapon_defaults(self, conn: sqlite3.Connection, item: Dict[str, Any]) -> Dict[str, Any]:
        if item.get('item_type') != 'weapon':
            return item
        missing_fields = [
            key for key in (
                'weapon_properties', 'weapon_category', 'damage_dice',
                'damage_type', 'weapon_mastery', 'range_normal',
                'range_long', 'versatile_damage'
            ) if not item.get(key)
        ]
        if not missing_fields:
            return item
        base_name = self._infer_base_weapon_name(item.get('name', ''))
        if not base_name:
            return item
        base_item = self._fetch_base_weapon(conn, base_name)
        if not base_item:
            return item
        for key in missing_fields:
            value = base_item.get(key)
            if value and not item.get(key):
                item[key] = value
        if not item.get('weapon_properties'):
            item['weapon_properties'] = []
        return item
    def get_all_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    name, description, item_type, rarity, cost_gp, weight_lb,
                    weapon_category, damage_dice, damage_type, weapon_properties,
                    weapon_mastery, range_normal, range_long, versatile_damage,
                    ammunition, armor_class, armor_type, dex_bonus_max,
                    strength_requirement, stealth_disadvantage, is_magical
                FROM equipment
                ORDER BY item_type, name
            """)
            
            equipment = []
            for row in cursor.fetchall():
                item = dict(row)
                
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except json.JSONDecodeError:
                        item['weapon_properties'] = []
                
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                item = self._hydrate_weapon_defaults(conn, item)
                item = {k: v for k, v in item.items() if v is not None}
                equipment.append(item)
            
            return equipment
            
        finally:
            conn.close()
    
    def get_equipment_by_rarity(self, rarities: List[str]) -> List[Dict[str, Any]]:
        """Get equipment filtered by rarity."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join(['?' for _ in rarities])
            cursor.execute(f"""
                SELECT 
                    name, description, item_type, rarity, cost_gp, weight_lb,
                    weapon_category, damage_dice, damage_type, weapon_properties,
                    weapon_mastery, range_normal, range_long, versatile_damage,
                    ammunition, armor_class, armor_type, dex_bonus_max,
                    strength_requirement, stealth_disadvantage, is_magical
                FROM equipment
                WHERE LOWER(rarity) IN ({placeholders})
                ORDER BY item_type, name
            """, [r.lower() for r in rarities])
            
            equipment = []
            for row in cursor.fetchall():
                item = dict(row)
                
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except json.JSONDecodeError:
                        item['weapon_properties'] = []
                
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                item = self._hydrate_weapon_defaults(conn, item)
                item = {k: v for k, v in item.items() if v is not None}
                equipment.append(item)
            
            return equipment
            
        finally:
            conn.close()
    
    def get_equipment_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific equipment item by name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    name, description, item_type, rarity, cost_gp, weight_lb,
                    weapon_category, damage_dice, damage_type, weapon_properties,
                    weapon_mastery, range_normal, range_long, versatile_damage,
                    ammunition, armor_class, armor_type, dex_bonus_max,
                    strength_requirement, stealth_disadvantage, is_magical
                FROM equipment
                WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            if row:
                item = dict(row)
                
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except json.JSONDecodeError:
                        item['weapon_properties'] = []
                
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                item = self._hydrate_weapon_defaults(conn, item)
                item = {k: v for k, v in item.items() if v is not None}
                return item
            
            return None
            
        finally:
            conn.close()
    
    def get_weapons(self) -> List[Dict[str, Any]]:
        """Get all weapons from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    name, description, item_type, rarity, cost_gp, weight_lb,
                    weapon_category, damage_dice, damage_type, weapon_properties,
                    weapon_mastery, range_normal, range_long, versatile_damage,
                    ammunition, is_magical
                FROM equipment
                WHERE item_type = 'weapon'
                ORDER BY weapon_category, name
            """)
            
            weapons = []
            for row in cursor.fetchall():
                item = dict(row)
                
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except json.JSONDecodeError:
                        item['weapon_properties'] = []
                
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                item = self._hydrate_weapon_defaults(conn, item)
                item = {k: v for k, v in item.items() if v is not None}
                weapons.append(item)
            
            return weapons
            
        finally:
            conn.close()
    
    def get_equipment_lookup(self) -> Dict[str, Dict[str, Any]]:
        """Get all equipment as a lookup dictionary by name."""
        equipment = self.get_all_equipment()
        return {item['name']: item for item in equipment}





