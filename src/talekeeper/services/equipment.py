# core
# category: core
"""
Equipment Service - Database-backed equipment data and properties.
Queries the equipment table for all item data and AC calculations.
"""

from typing import Dict, Any, Optional
import sqlite3
import json

class EquipmentService:
    """Service for managing equipment data from talekeeper.database."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
    def get_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get equipment item data by name from talekeeper.database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            # Case-insensitive search
            cursor.execute("SELECT * FROM equipment WHERE LOWER(name) = LOWER(?)", (item_name,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Convert to dict and parse JSON fields
                item_dict = dict(row)
                
                # Parse JSON fields
                if item_dict.get('weapon_properties'):
                    item_dict['weapon_properties'] = json.loads(item_dict['weapon_properties'])
                
                return item_dict
            
            return None
            
        except Exception as e:
            print(f"Error getting equipment item '{item_name}': {e}")
            return None
    
    def get_armor_ac(self, armor_name: str, dex_modifier: int) -> int:
        """Calculate AC for armor based on database properties and character's dex."""
        armor_data = self.get_item(armor_name)
        if not armor_data or armor_data['item_type'] != 'armor':
            return 10 + dex_modifier  # No armor - base AC + dex
        
        ac_base = armor_data['armor_class']
        armor_type = armor_data['armor_type']
        dex_max = armor_data['dex_bonus_max']
        
        if armor_type == 'light':
            # Light armor - full dex bonus
            return ac_base + dex_modifier
        elif armor_type == 'heavy':
            # Heavy armor - no dex bonus
            return ac_base
        else:  # Medium armor
            # Medium armor - limited dex bonus (usually max +2)
            dex_bonus = min(dex_modifier, dex_max) if dex_max is not None else dex_modifier
            return ac_base + dex_bonus
    
    def get_shield_ac_bonus(self, shield_name: str) -> int:
        """Get AC bonus from shield. Shields typically give +2 AC."""
        shield_data = self.get_item(shield_name)
        if not shield_data or shield_data['item_type'] != 'shield':
            return 0
        
        # For now, all shields give +2 AC (D&D standard)
        # Could be extended to read from a shield_ac_bonus column if needed
        return 2
    
    def is_weapon(self, item_name: str) -> bool:
        """Check if item is a weapon."""
        item_data = self.get_item(item_name)
        return item_data and item_data['item_type'] == 'weapon'
    
    def is_armor(self, item_name: str) -> bool:
        """Check if item is armor."""
        item_data = self.get_item(item_name)
        return item_data and item_data['item_type'] == 'armor'
    
    def is_shield(self, item_name: str) -> bool:
        """Check if item is a shield."""
        item_data = self.get_item(item_name)
        return item_data and item_data['item_type'] == 'shield'
    
    def get_weapon_properties(self, weapon_name: str) -> Dict[str, Any]:
        """Get weapon properties for damage calculations."""
        weapon_data = self.get_item(weapon_name)
        if not weapon_data or weapon_data['item_type'] != 'weapon':
            return {}
        
        properties = {
            'damage_dice': weapon_data['damage_dice'],
            'damage_type': weapon_data['damage_type'],
            'weapon_properties': json.loads(weapon_data['weapon_properties']) if weapon_data['weapon_properties'] else [],
            'weapon_mastery': weapon_data['weapon_mastery'],
            'versatile_damage': weapon_data['versatile_damage']
        }
        
        # Add range for ranged weapons
        if weapon_data['range_normal']:
            properties['range'] = f"{weapon_data['range_normal']}/{weapon_data['range_long']}"
        
        return properties
    
    def get_items_by_type(self, item_type: str) -> list:
        """Get all items of a specific type (weapon, armor, etc.)."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM equipment WHERE item_type = ? ORDER BY name", (item_type,))
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dict and parse JSON fields
            items = []
            for row in rows:
                item_dict = dict(row)
                if item_dict.get('weapon_properties'):
                    item_dict['weapon_properties'] = json.loads(item_dict['weapon_properties'])
                items.append(item_dict)
            
            return items
            
        except Exception as e:
            print(f"Error getting items of type '{item_type}': {e}")
            return []

# Global equipment service instance
equipment_service = EquipmentService()