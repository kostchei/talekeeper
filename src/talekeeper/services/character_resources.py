"""
Universal Character Resource Management System

Handles all class-based resources (Fighter, Barbarian, Wizard, etc.) 
with unified short rest/long rest restoration.

Replaces class-specific resource columns with scalable table-based approach.
"""

import sqlite3
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CharacterResource:
    """Represents a single character resource (e.g., Second Wind, Rage, Spell Slot)."""
    resource_name: str
    current_uses: int
    max_uses: int
    rest_type: str  # "short_rest", "long_rest", "none"
    source_class: str
    source_level: int


class CharacterResourceService:
    """Universal service for managing character resources across all classes."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def add_resource(self, character_id: str, resource_name: str, max_uses: int, 
                    rest_type: str, source_class: str, source_level: int) -> bool:
        """Add a new resource to a character (or update existing)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO character_resources 
                (character_id, resource_name, current_uses, max_uses, rest_type, source_class, source_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (character_id, resource_name, max_uses, max_uses, rest_type, source_class, source_level))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding resource {resource_name}: {e}")
            return False
    
    def get_character_resources(self, character_id: str) -> List[CharacterResource]:
        """Get all resources for a character."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT resource_name, current_uses, max_uses, rest_type, source_class, source_level
                FROM character_resources 
                WHERE character_id = ?
                ORDER BY source_class, source_level, resource_name
            """, (character_id,))
            
            resources = []
            for row in cursor.fetchall():
                resources.append(CharacterResource(*row))
            
            conn.close()
            return resources
            
        except Exception as e:
            print(f"Error getting resources for {character_id}: {e}")
            return []
    
    def get_resource(self, character_id: str, resource_name: str) -> Optional[CharacterResource]:
        """Get a specific resource for a character."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT resource_name, current_uses, max_uses, rest_type, source_class, source_level
                FROM character_resources 
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, resource_name))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return CharacterResource(*row)
            return None
            
        except Exception as e:
            print(f"Error getting resource {resource_name}: {e}")
            return None
    
    def use_resource(self, character_id: str, resource_name: str, uses: int = 1) -> Dict[str, Any]:
        """Use a resource (consume uses)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current resource
            cursor.execute("""
                SELECT current_uses, max_uses FROM character_resources 
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, resource_name))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return {'success': False, 'error': f'Resource {resource_name} not found'}
            
            current_uses, max_uses = row
            
            if current_uses < uses:
                conn.close()
                return {
                    'success': False, 
                    'error': f'Not enough {resource_name} uses remaining ({current_uses} < {uses})',
                    'current_uses': current_uses,
                    'max_uses': max_uses
                }
            
            # Consume uses
            new_current = current_uses - uses
            cursor.execute("""
                UPDATE character_resources 
                SET current_uses = ?
                WHERE character_id = ? AND resource_name = ?
            """, (new_current, character_id, resource_name))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'resource_name': resource_name,
                'uses_consumed': uses,
                'current_uses': new_current,
                'max_uses': max_uses
            }
            
        except Exception as e:
            print(f"Error using resource {resource_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _grant_human_long_rest_inspiration(self, cursor, character_id: str) -> Optional[Dict[str, Any]]:
        """Ensure humans regain Heroic Inspiration on long rest."""
        try:
            cursor.execute(
                """
                SELECT race_id, 
                       COALESCE(inspiration_uses_current, 0),
                       COALESCE(inspiration_uses_max, 0)
                FROM characters
                WHERE id = ?
                """,
                (character_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            race_id, current_uses, max_uses = row
            if not race_id or "human" not in str(race_id).lower():
                return None

            desired_max = max(max_uses, 1)
            desired_current = max(current_uses, desired_max)
            desired_max = max(desired_max, desired_current)

            if desired_current == current_uses and desired_max == max_uses:
                return None

            cursor.execute(
                """
                UPDATE characters
                SET inspiration_uses_current = ?, inspiration_uses_max = ?
                WHERE id = ?
                """,
                (desired_current, desired_max, character_id),
            )

            gained = max(0, desired_current - current_uses)
            return {
                "resource_name": "Heroic Inspiration",
                "old_uses": current_uses,
                "new_uses": desired_current,
                "gained": gained,
                "max_uses": desired_max,
            }
        except Exception as exc:
            print(f"[CharacterResources] Failed to grant human inspiration: {exc}")
            return None

    def restore_resources_by_rest_type(self, character_id: str, rest_type: str) -> Dict[str, Any]:
        """Restore all resources of a specific rest type (short_rest or long_rest)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get resources that need restoration
            cursor.execute("""
                SELECT resource_name, current_uses, max_uses 
                FROM character_resources 
                WHERE character_id = ? AND rest_type = ? AND current_uses < max_uses
            """, (character_id, rest_type))
            
            resources_to_restore = cursor.fetchall()
            restored_resources = []
            
            # Restore each resource to maximum
            for resource_name, current_uses, max_uses in resources_to_restore:
                cursor.execute("""
                    UPDATE character_resources 
                    SET current_uses = max_uses 
                    WHERE character_id = ? AND resource_name = ?
                """, (character_id, resource_name))
                
                restored_resources.append({
                    'resource_name': resource_name,
                    'old_uses': current_uses,
                    'new_uses': max_uses,
                    'gained': max_uses - current_uses
                })
            
            if rest_type == 'long_rest':
                bonus = self._grant_human_long_rest_inspiration(cursor, character_id)
                if bonus:
                    restored_resources.append(bonus)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'rest_type': rest_type,
                'restored_count': len(restored_resources),
                'restored_resources': restored_resources
            }
            
        except Exception as e:
            print(f"Error restoring {rest_type} resources: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_resource_max_uses(self, character_id: str, resource_name: str, new_max: int) -> bool:
        """Update max uses for a resource (for level progression)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update max uses and set current to max (full refresh)
            cursor.execute("""
                UPDATE character_resources 
                SET max_uses = ?, current_uses = ?
                WHERE character_id = ? AND resource_name = ?
            """, (new_max, new_max, character_id, resource_name))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating max uses for {resource_name}: {e}")
            return False
    
    def initialize_fighter_resources(self, character_id: str, level: int) -> Dict[str, Any]:
        """Initialize/update Fighter resources based on level."""
        resources_updated = []
        
        # Second Wind (level 1+)
        # D&D 2024: 2 uses at L1, 3 at L4, 4 at L10
        if level >= 1:
            if level >= 10:
                second_wind_uses = 4
            elif level >= 4:
                second_wind_uses = 3
            else:
                second_wind_uses = 2
            
            success = self.add_resource(
                character_id, "Second Wind", second_wind_uses, "short_rest", "fighter", 1
            )
            if success:
                resources_updated.append(f"Second Wind ({second_wind_uses} uses)")
        
        # Action Surge (level 2+)
        if level >= 2:
            action_surge_uses = 2 if level >= 17 else 1
            success = self.add_resource(
                character_id, "Action Surge", action_surge_uses, "short_rest", "fighter", 2
            )
            if success:
                resources_updated.append(f"Action Surge ({action_surge_uses} uses)")
        
        # Indomitable (level 9+)
        if level >= 9:
            indomitable_uses = 3 if level >= 17 else (2 if level >= 13 else 1)
            success = self.add_resource(
                character_id, "Indomitable", indomitable_uses, "long_rest", "fighter", 9
            )
            if success:
                resources_updated.append(f"Indomitable ({indomitable_uses} uses)")
        
        return {
            'success': True,
            'character_id': character_id,
            'level': level,
            'resources_added': resources_updated  # Keep same key for compatibility
        }
    
    def initialize_barbarian_resources(self, character_id: str, level: int) -> Dict[str, Any]:
        """Initialize Barbarian resources based on level."""
        resources_added = []
        
        # Rage uses (level 1+)
        # 2 at 1st, 3 at 3rd, 4 at 6th, 5 at 12th, 6 at 17th, unlimited at 20th
        if level >= 20:
            rage_uses = 999  # Effectively unlimited
        elif level >= 17:
            rage_uses = 6
        elif level >= 12:
            rage_uses = 5
        elif level >= 6:
            rage_uses = 4
        elif level >= 3:
            rage_uses = 3
        else:
            rage_uses = 2
        
        success = self.add_resource(
            character_id, "Rage", rage_uses, "long_rest", "barbarian", 1
        )
        if success:
            resources_added.append("Rage")
        
        # Note: Reckless Attack doesn't consume resources (at-will ability)
        # Note: Danger Sense is passive
        # Note: Brutal Critical is passive
        
        return {
            'success': True,
            'character_id': character_id,
            'level': level,
            'resources_added': resources_added
        }
    
    def get_resources_summary(self, character_id: str) -> Dict[str, Any]:
        """Get a summary of all character resources for UI display."""
        resources = self.get_character_resources(character_id)
        
        summary = {
            'total_resources': len(resources),
            'short_rest_resources': [],
            'long_rest_resources': [],
            'permanent_resources': []
        }
        
        for resource in resources:
            resource_info = {
                'name': resource.resource_name,
                'current': resource.current_uses,
                'max': resource.max_uses,
                'available': resource.current_uses > 0,
                'source': f"{resource.source_class} {resource.source_level}"
            }
            
            if resource.rest_type == "short_rest":
                summary['short_rest_resources'].append(resource_info)
            elif resource.rest_type == "long_rest":
                summary['long_rest_resources'].append(resource_info)
            else:
                summary['permanent_resources'].append(resource_info)
        
        return summary
