# core
# category: utility
import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any


class FeatureRegistry:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_class_features_for_level(self, class_id: str, level: int) -> List[Dict[str, Any]]:
        """Get all class features available at a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, feature_name, feature_type, description, mechanics, prerequisites
                FROM class_features_progression
                WHERE class_id = ? AND level = ?
                ORDER BY feature_name
            """, (class_id, level))

            features = []
            for row in cursor.fetchall():
                feature = {
                    'id': row[0],
                    'feature_name': row[1],
                    'feature_type': row[2],
                    'description': row[3],
                    'mechanics': json.loads(row[4]) if row[4] else {},
                    'prerequisites': json.loads(row[5]) if row[5] else {}
                }
                features.append(feature)

            return features

    def get_subclass_features_for_level(self, subclass_id: str, level: int) -> List[Dict[str, Any]]:
        """Get all subclass features available at a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, feature_name, feature_type, description, mechanics, prerequisites
                FROM subclass_features_progression
                WHERE subclass_id = ? AND level = ?
                ORDER BY feature_name
            """, (subclass_id, level))

            features = []
            for row in cursor.fetchall():
                feature = {
                    'id': row[0],
                    'feature_name': row[1],
                    'feature_type': row[2],
                    'description': row[3],
                    'mechanics': json.loads(row[4]) if row[4] else {},
                    'prerequisites': json.loads(row[5]) if row[5] else {}
                }
                features.append(feature)

            return features

    def get_all_class_features(self, class_id: str, max_level: int = 20) -> Dict[int, List[Dict[str, Any]]]:
        """Get all class features up to max_level, organized by level"""
        features_by_level = {}

        for level in range(1, max_level + 1):
            features = self.get_class_features_for_level(class_id, level)
            if features:
                features_by_level[level] = features

        return features_by_level

    def get_character_features(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all active features for a character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, feature_source, feature_id, feature_name, level_gained,
                       current_uses, max_uses, recharge_type, configuration, active
                FROM character_feature_instances
                WHERE character_id = ? AND active = 1
                ORDER BY level_gained, feature_name
            """, (character_id,))

            features = []
            for row in cursor.fetchall():
                feature = {
                    'id': row[0],
                    'feature_source': row[1],
                    'feature_id': row[2],
                    'feature_name': row[3],
                    'level_gained': row[4],
                    'current_uses': row[5],
                    'max_uses': row[6],
                    'recharge_type': row[7],
                    'configuration': json.loads(row[8]) if row[8] else {},
                    'active': bool(row[9])
                }
                features.append(feature)

            return features

    def grant_feature_to_character(self, character_id: str, feature_source: str,
                                 feature_id: int, feature_name: str, level_gained: int,
                                 max_uses: int = 0, recharge_type: str = 'permanent',
                                 configuration: Dict[str, Any] = None) -> int:
        """Grant a feature to a character"""
        if configuration is None:
            configuration = {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO character_feature_instances
                (character_id, feature_source, feature_id, feature_name, level_gained,
                 current_uses, max_uses, recharge_type, configuration, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (character_id, feature_source, feature_id, feature_name, level_gained,
                  max_uses, max_uses, recharge_type, json.dumps(configuration)))

            return cursor.lastrowid

    def get_features_by_type(self, character_id: str, feature_type: str) -> List[Dict[str, Any]]:
        """Get character features filtered by type (action, bonus_action, reaction, etc.)"""
        character_features = self.get_character_features(character_id)

        matching_features = []
        for char_feature in character_features:
            feature_id = char_feature['feature_id']
            feature_source = char_feature['feature_source']

            if feature_source == 'class':
                feature_details = self._get_class_feature_details(feature_id)
            elif feature_source == 'subclass':
                feature_details = self._get_subclass_feature_details(feature_id)
            else:
                continue

            if feature_details and feature_details.get('feature_type') == feature_type:
                char_feature.update(feature_details)
                matching_features.append(char_feature)

        return matching_features

    def _get_class_feature_details(self, feature_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a class feature"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_type, description, mechanics, prerequisites
                FROM class_features_progression
                WHERE id = ?
            """, (feature_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'feature_type': row[0],
                    'description': row[1],
                    'mechanics': json.loads(row[2]) if row[2] else {},
                    'prerequisites': json.loads(row[3]) if row[3] else {}
                }
        return None

    def _get_subclass_feature_details(self, feature_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a subclass feature"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_type, description, mechanics, prerequisites
                FROM subclass_features_progression
                WHERE id = ?
            """, (feature_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'feature_type': row[0],
                    'description': row[1],
                    'mechanics': json.loads(row[2]) if row[2] else {},
                    'prerequisites': json.loads(row[3]) if row[3] else {}
                }
        return None

    def update_feature_uses(self, character_id: str, feature_name: str, uses_spent: int):
        """Update the current uses of a feature"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_feature_instances
                SET current_uses = CASE
                    WHEN current_uses - ? < 0 THEN 0
                    ELSE current_uses - ?
                END
                WHERE character_id = ? AND feature_name = ? AND active = 1
            """, (uses_spent, uses_spent, character_id, feature_name))
            conn.commit()

    def recharge_features(self, character_id: str, recharge_type: str):
        """Recharge features based on rest type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_feature_instances
                SET current_uses = max_uses
                WHERE character_id = ? AND recharge_type = ? AND active = 1
            """, (character_id, recharge_type))
            conn.commit()

    def get_subclass_selection_level(self, class_id: str) -> Optional[int]:
        """Get the level at which a class selects its subclass"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level FROM class_features_progression
                WHERE class_id = ? AND JSON_EXTRACT(mechanics, '$.subclass_selection') = 1
                ORDER BY level LIMIT 1
            """, (class_id,))

            row = cursor.fetchone()
            return row[0] if row else None

    def get_available_subclasses(self, class_id: str) -> List[Dict[str, str]]:
        """Get available subclasses for a class"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name FROM subclasses
                WHERE class_id = ?
                ORDER BY name
            """, (class_id,))

            subclasses = []
            for row in cursor.fetchall():
                subclasses.append({
                    'id': row[0],
                    'name': row[1]
                })

            return subclasses