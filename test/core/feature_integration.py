"""
Feature System Integration with Game Engine

This module integrates the new feature system with the existing game engine,
providing backward compatibility while enabling the new scalable architecture.
"""

import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from core.class_features import FeatureManager, ResourceRecharge
from core.feature_definitions import ClassFeatures, FeatureDefinition


class FeatureSystemIntegration:
    """Integrates the feature system with the existing SQLite database."""
    
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.feature_manager = FeatureManager(db_path)
        self._ensure_feature_tables()
    
    def _ensure_feature_tables(self):
        """Ensure all required feature tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create unified feature state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_states (
                character_id TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                feature_type TEXT NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                uses_current INTEGER,
                uses_max INTEGER,
                configuration TEXT,  -- JSON for feature-specific config
                last_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                PRIMARY KEY (character_id, feature_name),
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        # Create feature progression tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_progression (
                character_id TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subclass TEXT,
                level INTEGER NOT NULL,
                features_gained TEXT,  -- JSON list of feature names
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def initialize_character_features(self, character_id: str) -> bool:
        """Initialize features for a character based on class and level."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get character info
            cursor.execute("""
                SELECT id, class_id, subclass_id, level
                FROM characters
                WHERE id = ?
            """, (character_id,))
            
            char_row = cursor.fetchone()
            if not char_row:
                return False
            
            class_name = char_row['class_id']
            subclass = char_row['subclass_id']
            level = char_row['level']
            
            # Clear existing features for this character (fresh start)
            cursor.execute("DELETE FROM feature_states WHERE character_id = ?", (character_id,))
            
            # Get all features for this class/level combo
            features = ClassFeatures.get_features_by_level(class_name, level, subclass)
            
            # Initialize each feature in the database
            for feature_def in features:
                self._initialize_feature(cursor, character_id, feature_def, level)
            
            # Initialize class-specific feature tables (create fresh)
            self._initialize_class_features(cursor, character_id, class_name, level)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error initializing features: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _initialize_feature(self, cursor: sqlite3.Cursor, character_id: str, 
                          feature: FeatureDefinition, character_level: int):
        """Initialize a single feature in the database."""
        # Calculate uses if it's a resource feature
        uses_max = None
        if feature.scaling and feature.feature_type == "resource":
            # Find the appropriate scaling tier
            for lvl in sorted(feature.scaling.keys(), reverse=True):
                if character_level >= lvl:
                    scaling_data = feature.scaling[lvl]
                    uses_max = scaling_data.get("uses", uses_max)
                    break
        
        # Create configuration JSON
        config = {
            "description": feature.description,
            "mechanics": feature.mechanics,
            "usage": feature.usage,
            "recharge": feature.recharge,
            "level_acquired": feature.level_acquired
        }
        
        # Insert or update feature state
        cursor.execute("""
            INSERT OR REPLACE INTO feature_states
            (character_id, feature_name, feature_type, uses_current, uses_max, configuration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (character_id, feature.name, feature.feature_type, 
              uses_max, uses_max, json.dumps(config)))
    
    def _initialize_class_features(self, cursor: sqlite3.Cursor, character_id: str, 
                                   class_name: str, level: int):
        """Initialize class-specific feature tables with fresh data."""
        if class_name == "Fighter":
            # Clear existing and create fresh
            cursor.execute("DELETE FROM fighter_features WHERE character_id = ?", (character_id,))
            
            # Initialize fighter features  
            fighting_style = self._get_fighting_style(cursor, character_id)
            
            # Calculate feature values based on level
            action_surge_max = 1 if level >= 2 else 0
            if level >= 17:
                action_surge_max = 2
            
            second_wind_uses = 2
            if level >= 4:
                second_wind_uses = 3
            if level >= 10:
                second_wind_uses = 4
            
            weapon_masteries = 3
            if level >= 4:
                weapon_masteries = 4
            if level >= 10:
                weapon_masteries = 5
            if level >= 16:
                weapon_masteries = 6
            
            extra_attacks = 1
            if level >= 5:
                extra_attacks = 2
            if level >= 11:
                extra_attacks = 3
            if level >= 20:
                extra_attacks = 4
            
            indomitable_max = 0
            if level >= 9:
                indomitable_max = 1
            if level >= 13:
                indomitable_max = 2
            if level >= 17:
                indomitable_max = 3
            
            cursor.execute("""
                INSERT INTO fighter_features 
                (character_id, level, fighting_style, action_surge_uses_max, 
                 action_surge_uses_current, second_wind_used, 
                 indomitable_uses_max, indomitable_uses_current, 
                 extra_attacks, weapon_masteries_known)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (character_id, level, fighting_style, action_surge_max,
                  action_surge_max, False, indomitable_max, indomitable_max,
                  extra_attacks, weapon_masteries))
        
        elif class_name == "Barbarian":
            # Clear existing and create fresh
            cursor.execute("DELETE FROM barbarian_features WHERE character_id = ?", (character_id,))
            
            # Calculate barbarian feature values
            rage_uses = 2
            rage_damage = 2
            
            if level >= 3:
                rage_uses = 3
            if level >= 6:
                rage_uses = 4
            if level >= 9:
                rage_damage = 3
            if level >= 12:
                rage_uses = 5
            if level >= 16:
                rage_damage = 4
            if level >= 17:
                rage_uses = 6
            
            cursor.execute("""
                INSERT INTO barbarian_features
                (character_id, level, rage_uses_max, rage_uses_current, 
                 rage_damage_bonus, unarmored_defense_active,
                 reckless_attack_available, danger_sense_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (character_id, level, rage_uses, rage_uses, rage_damage,
                  True, level >= 2, level >= 2))
        
        elif class_name == "Rogue":
            # Clear existing and create fresh
            cursor.execute("DELETE FROM rogue_features WHERE character_id = ?", (character_id,))
            
            # Calculate sneak attack dice
            sneak_dice = (level + 1) // 2
            
            cursor.execute("""
                INSERT INTO rogue_features
                (character_id, level, sneak_attack_dice, expertise_skills,
                 cunning_action_available, uncanny_dodge_available,
                 evasion_available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (character_id, level, sneak_dice, "[]",
                  level >= 2, level >= 5, level >= 7))
    
    def _get_fighting_style(self, cursor: sqlite3.Cursor, character_id: str) -> Optional[str]:
        """Get fighting style from character feats."""
        cursor.execute("""
            SELECT feat_name 
            FROM character_feats 
            WHERE character_id = ? 
            AND feat_name IN ('archery', 'defense', 'dueling', 
                            'great_weapon_fighting', 'protection', 
                            'two_weapon_fighting')
        """, (character_id,))
        
        row = cursor.fetchone()
        return row[0] if row else None
    
    def use_feature(self, character_id: str, feature_name: str, 
                    context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use a character feature and update database state."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get character data
            cursor.execute("""
                SELECT * FROM characters WHERE id = ?
            """, (character_id,))
            
            char_row = cursor.fetchone()
            if not char_row:
                return {"success": False, "reason": "Character not found"}
            
            # Convert row to dict
            character = dict(char_row)
            
            # Load features for this character
            self.feature_manager.load_character_features(character_id)
            
            # Use the feature
            result = self.feature_manager.use_feature(feature_name, character, context)
            
            if result.get("success"):
                # Update database state
                cursor.execute("""
                    UPDATE feature_states
                    SET uses_current = uses_current - 1,
                        last_used = ?,
                        updated_at = ?
                    WHERE character_id = ? AND feature_name = ?
                    AND uses_current > 0
                """, (datetime.now().isoformat(), datetime.now().isoformat(),
                      character_id, feature_name))
                
                # Update legacy tables if needed
                self._update_legacy_tables(cursor, character_id, feature_name, result)
                
                conn.commit()
            
            return result
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "reason": str(e)}
        finally:
            conn.close()
    
    def _update_legacy_tables(self, cursor: sqlite3.Cursor, character_id: str, 
                             feature_name: str, result: Dict):
        """Update legacy feature tables for backward compatibility."""
        if feature_name == "second_wind":
            cursor.execute("""
                UPDATE fighter_features
                SET second_wind_used = TRUE
                WHERE character_id = ?
            """, (character_id,))
        
        elif feature_name == "action_surge":
            cursor.execute("""
                UPDATE fighter_features
                SET action_surge_uses_current = action_surge_uses_current - 1
                WHERE character_id = ? AND action_surge_uses_current > 0
            """, (character_id,))
        
        elif feature_name == "rage":
            cursor.execute("""
                UPDATE barbarian_features
                SET rage_uses_current = rage_uses_current - 1,
                    is_raging = TRUE,
                    rage_turns_remaining = 10
                WHERE character_id = ? AND rage_uses_current > 0
            """, (character_id,))
    
    def process_rest(self, character_id: str, rest_type: str) -> Dict[str, Any]:
        """Process a rest and restore features."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Load features
            self.feature_manager.load_character_features(character_id)
            self.feature_manager.process_rest(rest_type)
            
            # Update database
            if rest_type == "long":
                # Restore all features
                cursor.execute("""
                    UPDATE feature_states
                    SET uses_current = uses_max
                    WHERE character_id = ? AND uses_max IS NOT NULL
                """, (character_id,))
                
                # Update legacy tables
                cursor.execute("""
                    UPDATE fighter_features
                    SET action_surge_uses_current = action_surge_uses_max,
                        second_wind_used = FALSE,
                        indomitable_uses_current = indomitable_uses_max
                    WHERE character_id = ?
                """, (character_id,))
                
                cursor.execute("""
                    UPDATE barbarian_features
                    SET rage_uses_current = rage_uses_max,
                        is_raging = FALSE,
                        rage_turns_remaining = 0
                    WHERE character_id = ?
                """, (character_id,))
                
            elif rest_type == "short":
                # Restore short rest features
                cursor.execute("""
                    UPDATE feature_states
                    SET uses_current = uses_max
                    WHERE character_id = ? 
                    AND configuration LIKE '%"recharge": "short_rest"%'
                """, (character_id,))
                
                # Update legacy tables
                cursor.execute("""
                    UPDATE fighter_features
                    SET action_surge_uses_current = action_surge_uses_max,
                        second_wind_used = FALSE
                    WHERE character_id = ?
                """, (character_id,))
            
            conn.commit()
            
            return {"success": True, "rest_type": rest_type, "features_restored": True}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "reason": str(e)}
        finally:
            conn.close()
    
    def get_available_features(self, character_id: str, 
                              context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get all features available to a character."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get character data
            cursor.execute("""
                SELECT * FROM characters WHERE id = ?
            """, (character_id,))
            
            char_row = cursor.fetchone()
            if not char_row:
                return []
            
            character = dict(char_row)
            
            # Get feature details directly from database (simplified approach)
            cursor.execute("""
                SELECT feature_name, feature_type, uses_current, uses_max, configuration
                FROM feature_states
                WHERE character_id = ? AND (uses_current > 0 OR uses_current IS NULL)
            """, (character_id,))
            
            features = []
            for row in cursor.fetchall():
                config = json.loads(row['configuration']) if row['configuration'] else {}
                features.append({
                    "name": row['feature_name'],
                    "type": row['feature_type'],
                    "uses_remaining": row['uses_current'],
                    "uses_max": row['uses_max'],
                    "usage": config.get("usage"),
                    "description": config.get("description")
                })
            
            return features
            
        finally:
            conn.close()
    
    def apply_passive_features(self, character_id: str) -> Dict[str, Any]:
        """Apply all passive feature modifiers to a character."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get character data
            cursor.execute("""
                SELECT * FROM characters WHERE id = ?
            """, (character_id,))
            
            char_row = cursor.fetchone()
            if not char_row:
                return {}
            
            character = dict(char_row)
            
            # Load features
            self.feature_manager.load_character_features(character_id)
            
            # Apply passive features
            modifiers = self.feature_manager.apply_passive_features(character)
            
            return modifiers
            
        finally:
            conn.close()


# Singleton instance for easy access
_integration = None

def get_feature_integration(db_path: str = "talekeeper.db") -> FeatureSystemIntegration:
    """Get the singleton feature integration instance."""
    global _integration
    if _integration is None:
        _integration = FeatureSystemIntegration(db_path)
    return _integration