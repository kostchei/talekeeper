"""
Level Up Service - Handle character leveling and multi-classing
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
import json


class LevelUpService:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
    
    def get_available_classes(self) -> List[str]:
        """Get list of available classes for leveling."""
        return ['Barbarian', 'Cleric', 'Paladin', 'Rogue', 'Warlock', 'Wizard', 'Fighter']
    
    def get_character_class_levels(self, character_id: str) -> Dict[str, int]:
        """Get current class levels for a character."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT class_name, level 
            FROM character_class_levels 
            WHERE character_id = ?
        """, (character_id,))
        
        result = {class_name: level for class_name, level in cursor.fetchall()}
        conn.close()
        
        # If no multi-class data exists, get from main character table
        if not result:
            cursor = conn.cursor()
            cursor.execute("SELECT class_id, level FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                result[row[0]] = row[1]
        
        return result
    
    def level_up_character(self, character_id: str, class_choice: str) -> bool:
        """Level up character in chosen class."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current total level
            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            current_total_level = cursor.fetchone()[0]
            new_total_level = current_total_level + 1
            
            # Check if character already has levels in this class
            cursor.execute("""
                SELECT level FROM character_class_levels 
                WHERE character_id = ? AND class_name = ?
            """, (character_id, class_choice))
            
            existing_class_level = cursor.fetchone()
            
            if existing_class_level:
                # Level up existing class
                new_class_level = existing_class_level[0] + 1
                cursor.execute("""
                    UPDATE character_class_levels 
                    SET level = ? 
                    WHERE character_id = ? AND class_name = ?
                """, (new_class_level, character_id, class_choice))
            else:
                # Add new class at level 1
                cursor.execute("""
                    INSERT INTO character_class_levels (character_id, class_name, level, hit_die_type)
                    VALUES (?, ?, 1, ?)
                """, (character_id, class_choice, self._get_hit_die_for_class(class_choice)))
                new_class_level = 1
            
            # Update main character table
            cursor.execute("""
                UPDATE characters 
                SET level = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_total_level, character_id))
            
            # Grant new class features (old system)
            self._grant_class_features(cursor, character_id, class_choice, new_class_level)
            
            # Update features using new feature system
            try:
                from core.feature_integration import FeatureSystemIntegration
                feature_system = FeatureSystemIntegration(self.db_path)
                
                # Refresh character features for new level
                feature_system.initialize_character_features(character_id)
                print(f"[LevelUp] Updated feature system for {class_choice} level {new_class_level} (total level {new_total_level})")
            except Exception as e:
                print(f"[LevelUp] Warning: Failed to update new feature system: {e}")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error leveling up character: {e}")
            return False
        finally:
            conn.close()
    
    def _get_hit_die_for_class(self, class_name: str) -> int:
        """Get hit die size for class."""
        hit_dice = {
            'Barbarian': 12,
            'Fighter': 10,
            'Paladin': 10,
            'Cleric': 8,
            'Rogue': 8,
            'Warlock': 8,
            'Wizard': 6
        }
        return hit_dice.get(class_name, 8)
    
    def _grant_class_features(self, cursor, character_id: str, class_name: str, class_level: int):
        """Grant class features for the new level."""
        # Get features for this class and level
        cursor.execute("""
            SELECT feature_name, feature_type, usage_type, combat_effect, 
                   conditions_granted, resource_pool, spell_slots
            FROM class_features_detailed 
            WHERE class_name = ? AND level_required = ?
        """, (class_name, class_level))
        
        features = cursor.fetchall()
        
        for feature in features:
            feature_name, feature_type, usage_type, combat_effect, conditions_granted, resource_pool, spell_slots = feature
            
            # Add to character_features table
            cursor.execute("""
                INSERT OR REPLACE INTO character_features 
                (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (character_id, feature_name, feature_type, usage_type, class_level, combat_effect, conditions_granted))
            
            # Handle special features
            if resource_pool:
                # Features like Lay on Hands
                cursor.execute("""
                    INSERT OR REPLACE INTO character_resources 
                    (character_id, resource_type, resource_name, current_value, max_value)
                    VALUES (?, 'class_feature', ?, ?, ?)
                """, (character_id, feature_name.lower().replace(' ', '_'), resource_pool, resource_pool))
            
            if spell_slots:
                # Add spell slots
                slots = json.loads(spell_slots)
                for slot_level, slot_count in slots.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO character_resources 
                        (character_id, resource_type, resource_name, current_value, max_value)
                        VALUES (?, 'spell_slot', ?, ?, ?)
                    """, (character_id, f'level_{slot_level}', slot_count, slot_count))
    
    def get_next_level_features(self, character_id: str, class_choice: str) -> List[Dict]:
        """Get features that would be gained at next level in chosen class."""
        class_levels = self.get_character_class_levels(character_id)
        current_class_level = class_levels.get(class_choice, 0)
        next_level = current_class_level + 1
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT feature_name, combat_effect 
            FROM class_features_detailed 
            WHERE class_name = ? AND level_required = ?
        """, (class_choice, next_level))
        
        features = []
        for row in cursor.fetchall():
            features.append({
                'name': row[0],
                'description': row[1]
            })
        
        conn.close()
        return features


level_up_service = LevelUpService()