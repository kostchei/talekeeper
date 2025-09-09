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
                
                # Parse JSON fields
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except:
                        item['weapon_properties'] = []
                
                # Format range if applicable
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                # Clean up None values
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
                
                # Parse JSON fields
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except:
                        item['weapon_properties'] = []
                
                # Format range if applicable
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                # Clean up None values
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
                
                # Parse JSON fields
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except:
                        item['weapon_properties'] = []
                
                # Format range if applicable
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                # Clean up None values
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
                
                # Parse JSON fields
                if item.get('weapon_properties'):
                    try:
                        item['weapon_properties'] = json.loads(item['weapon_properties'])
                    except:
                        item['weapon_properties'] = []
                
                # Format range if applicable
                if item.get('range_normal') and item.get('range_long'):
                    item['range'] = f"{item['range_normal']}/{item['range_long']}"
                
                # Clean up None values
                item = {k: v for k, v in item.items() if v is not None}
                weapons.append(item)
            
            return weapons
            
        finally:
            conn.close()
    
    def get_equipment_lookup(self) -> Dict[str, Dict[str, Any]]:
        """Get all equipment as a lookup dictionary by name."""
        equipment = self.get_all_equipment()
        return {item['name']: item for item in equipment}