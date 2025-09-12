"""
Subclass Manager Service for TaleKeeper

Handles all subclass-related operations:
- Subclass selection during level-up
- Feature progression
- Mechanical effects of subclass features
- Integration with action cards and combat
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SubclassLevel(Enum):
    """Standard subclass progression levels."""
    SELECTION = 3
    FIRST_UPGRADE = 7
    SECOND_UPGRADE = 10
    THIRD_UPGRADE = 15
    FINAL_UPGRADE = 18


@dataclass
class SubclassFeature:
    """Represents a subclass feature."""
    name: str
    description: str
    level: int
    mechanics: Dict[str, Any]
    action_type: Optional[str] = None
    uses_per_rest: Optional[int] = None
    rest_type: Optional[str] = None


class SubclassManager:
    """Manages subclass selection, features, and mechanics."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._run_migration()
    
    def _run_migration(self):
        """Ensure subclass tables exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                with open('database/migrations/004_add_subclass_system.sql', 'r') as f:
                    conn.executescript(f.read())
                conn.commit()
        except Exception as e:
            print(f"[SubclassManager] Migration note: {e}")
    
    def get_available_subclasses(self, class_id: str) -> List[Dict[str, Any]]:
        """Get all available subclasses for a class."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, flavor_text, selection_level
                FROM subclasses
                WHERE LOWER(class_id) = LOWER(?)
                ORDER BY name
            """, (class_id,))
            
            subclasses = []
            for row in cursor:
                subclasses.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'flavor_text': row['flavor_text'],
                    'selection_level': row['selection_level']
                })
            
            return subclasses
    
    def select_subclass(self, character_id: str, subclass_id: str) -> bool:
        """Assign a subclass to a character."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verify character doesn't already have a subclass
                cursor.execute("""
                    SELECT subclass_id FROM characters WHERE id = ?
                """, (character_id,))
                
                current = cursor.fetchone()
                if current and current[0]:
                    print(f"[SubclassManager] Character already has subclass: {current[0]}")
                    return False
                
                # Update character with subclass
                cursor.execute("""
                    UPDATE characters
                    SET subclass_id = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (subclass_id, character_id))
                
                # Grant initial subclass features
                self._grant_subclass_features(cursor, character_id, subclass_id, 3)
                
                conn.commit()
                print(f"[SubclassManager] Assigned subclass {subclass_id} to character {character_id}")
                return True
                
        except Exception as e:
            print(f"[SubclassManager] Error selecting subclass: {e}")
            return False
    
    def _grant_subclass_features(self, cursor, character_id: str, subclass_id: str, up_to_level: int):
        """Grant subclass features up to specified level."""
        cursor.execute("""
            SELECT level, feature_name, description, mechanics, action_type
            FROM subclass_features
            WHERE subclass_id = ? AND level <= ?
            ORDER BY level
        """, (subclass_id, up_to_level))
        
        for row in cursor:
            # Add to character_features table
            cursor.execute("""
                INSERT OR IGNORE INTO character_features 
                (character_id, feature_name, feature_type, description, level_gained)
                VALUES (?, ?, ?, ?, ?)
            """, (character_id, row[1], row[4] or 'passive', row[2], row[0]))
            
            # Apply immediate mechanical effects
            self._apply_feature_mechanics(cursor, character_id, row[1], row[3])
    
    def _apply_feature_mechanics(self, cursor, character_id: str, feature_name: str, mechanics_json: str):
        """Apply mechanical effects of a feature."""
        if not mechanics_json:
            return
        
        try:
            mechanics = json.loads(mechanics_json)
            
            # Handle critical range modifications (Champion)
            if 'critical_range_min' in mechanics:
                cursor.execute("""
                    INSERT INTO character_combat_state (character_id, critical_range_min)
                    VALUES (?, ?)
                    ON CONFLICT(character_id) DO UPDATE SET
                        critical_range_min = ?
                """, (character_id, mechanics['critical_range_min'], mechanics['critical_range_min']))
            
            # Handle skill proficiencies (Gladiator, Assassin)
            if 'skills' in mechanics:
                for skill in mechanics['skills']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_skills (character_id, skill_name, proficient)
                        VALUES (?, ?, 1)
                    """, (character_id, skill))
            
            # Handle tool proficiencies (Assassin)
            if 'tool_proficiencies' in mechanics:
                for tool in mechanics['tool_proficiencies']:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies (character_id, proficiency_type, proficiency_name)
                        VALUES (?, 'tool', ?)
                    """, (character_id, tool))
                    
        except json.JSONDecodeError as e:
            print(f"[SubclassManager] Error parsing mechanics for {feature_name}: {e}")
    
    def get_subclass_features(self, subclass_id: str, level: int) -> List[SubclassFeature]:
        """Get all features for a subclass up to specified level."""
        features = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT feature_name, description, level, mechanics, 
                       action_type, uses_per_rest, rest_type
                FROM subclass_features
                WHERE subclass_id = ? AND level <= ?
                ORDER BY level
            """, (subclass_id, level))
            
            for row in cursor:
                mechanics = {}
                if row['mechanics']:
                    try:
                        mechanics = json.loads(row['mechanics'])
                    except:
                        pass
                
                features.append(SubclassFeature(
                    name=row['feature_name'],
                    description=row['description'],
                    level=row['level'],
                    mechanics=mechanics,
                    action_type=row['action_type'],
                    uses_per_rest=row['uses_per_rest'],
                    rest_type=row['rest_type']
                ))
        
        return features
    
    def check_subclass_requirement(self, character_id: str) -> Tuple[bool, str]:
        """Check if character needs to select a subclass."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT level, class_id, subclass_id
                FROM characters
                WHERE id = ?
            """, (character_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, ""
            
            level, class_id, subclass_id = row
            
            # Check if approaching subclass selection level without a subclass
            if level >= 2 and not subclass_id:
                # Next level would be 3 (subclass selection)
                return True, class_id
            
            return False, ""
    
    def update_features_for_level(self, character_id: str, new_level: int):
        """Update subclass features when character levels up."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get character's subclass
            cursor.execute("""
                SELECT subclass_id FROM characters WHERE id = ?
            """, (character_id,))
            
            row = cursor.fetchone()
            if not row or not row[0]:
                return
            
            subclass_id = row[0]
            
            # Get new features at this level
            cursor.execute("""
                SELECT feature_name, description, mechanics, action_type
                FROM subclass_features
                WHERE subclass_id = ? AND level = ?
            """, (subclass_id, new_level))
            
            for feature in cursor:
                # Add feature to character
                cursor.execute("""
                    INSERT OR IGNORE INTO character_features 
                    (character_id, feature_name, feature_type, description, level_gained)
                    VALUES (?, ?, ?, ?, ?)
                """, (character_id, feature[0], feature[3] or 'passive', feature[1], new_level))
                
                # Apply mechanics
                self._apply_feature_mechanics(cursor, character_id, feature[0], feature[2])
            
            conn.commit()
    
    def has_feature(self, character_id: str, feature_name: str) -> bool:
        """Check if character has a specific subclass feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM character_features
                WHERE character_id = ? AND feature_name = ?
            """, (character_id, feature_name))
            
            return cursor.fetchone() is not None
    
    def get_feature_uses(self, character_id: str, feature_name: str) -> Tuple[int, int]:
        """Get current and max uses for a resource-based feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check character_resources table for tracking
            cursor.execute("""
                SELECT current_uses, max_uses
                FROM character_resources
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, feature_name))
            
            row = cursor.fetchone()
            if row:
                return row[0], row[1]
            
            return 0, 0
    
    def use_feature(self, character_id: str, feature_name: str) -> bool:
        """Use a resource-based subclass feature."""
        current, max_uses = self.get_feature_uses(character_id, feature_name)
        
        if current <= 0:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE character_resources
                SET current_uses = current_uses - 1
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, feature_name))
            
            conn.commit()
            return True
    
    def apply_combat_modifiers(self, character_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply subclass-specific combat modifiers."""
        modifiers = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get character's subclass
            cursor.execute("""
                SELECT c.subclass_id, c.level, c.hit_points_current, c.hit_points_max
                FROM characters c
                WHERE c.id = ?
            """, (character_id,))
            
            row = cursor.fetchone()
            if not row or not row[0]:
                return modifiers
            
            subclass_id, level, current_hp, max_hp = row
            
            # Champion critical range
            if subclass_id == 'champion':
                if level >= 15:
                    modifiers['critical_range_min'] = 18
                elif level >= 3:
                    modifiers['critical_range_min'] = 19
            
            # Gladiator crowd favorite resistance
            elif subclass_id == 'gladiator' and level >= 15:
                if current_hp <= max_hp // 2:
                    modifiers['damage_resistance'] = ['all_except_psychic']
            
            # Assassin assassinate
            elif subclass_id == 'assassin' and level >= 3:
                if context.get('target_has_not_acted'):
                    modifiers['advantage'] = True
                if context.get('target_surprised'):
                    modifiers['auto_crit'] = True
            
            # Thief fast hands
            elif subclass_id == 'thief' and level >= 3:
                modifiers['bonus_action_use_object'] = True
        
        return modifiers


# Singleton instance
subclass_manager = SubclassManager()