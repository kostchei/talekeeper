# core
# category: utility
import sqlite3
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class FeatureInstance:
    id: Optional[int]
    character_id: str
    feature_source: str
    feature_id: Optional[int]
    feature_name: str
    level_gained: int
    current_uses: int
    max_uses: int
    recharge_type: Optional[str]
    configuration: Dict[str, Any]
    active: bool

class DynamicFeatureManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def grant_class_features_for_level(self, character_id: str, class_id: str, level: int) -> List[FeatureInstance]:
        """Grant all class features for a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get features for this class and level
            cursor.execute("""
                SELECT id, feature_name, feature_type, description, mechanics, prerequisites
                FROM class_features_progression
                WHERE class_id = ? AND level = ?
                ORDER BY feature_name
            """, (class_id, level))

            features = cursor.fetchall()
            granted_features = []

            for feature_data in features:
                feature_id, name, feature_type, description, mechanics_json, prerequisites_json = feature_data

                # Parse mechanics and prerequisites
                mechanics = json.loads(mechanics_json) if mechanics_json else {}
                prerequisites = json.loads(prerequisites_json) if prerequisites_json else {}

                # Check prerequisites
                if not self._check_prerequisites(cursor, character_id, prerequisites):
                    continue

                # Check if feature already exists
                if self._character_has_feature(cursor, character_id, name, 'class'):
                    continue

                # Calculate uses based on mechanics
                max_uses, recharge_type = self._calculate_feature_uses(mechanics, level)

                # Create feature instance
                feature_instance = FeatureInstance(
                    id=None,
                    character_id=character_id,
                    feature_source='class',
                    feature_id=feature_id,
                    feature_name=name,
                    level_gained=level,
                    current_uses=max_uses,
                    max_uses=max_uses,
                    recharge_type=recharge_type,
                    configuration={},
                    active=True
                )

                # Handle special feature configurations
                if name == 'Fighting Style' or mechanics.get('choice'):
                    feature_instance.configuration = {'requires_choice': True, 'choices': mechanics.get('choice', [])}
                elif name == 'Ability Score Improvement':
                    feature_instance.configuration = {'asi_or_feat': True}
                elif name == 'Expertise':
                    expertise_count = mechanics.get('expertise_count', 2)
                    feature_instance.configuration = {'expertise_count': expertise_count, 'skills_chosen': []}

                # Insert into database
                self._insert_character_feature(cursor, feature_instance)
                granted_features.append(feature_instance)

            conn.commit()
            return granted_features

    def grant_subclass_features_for_level(self, character_id: str, subclass_id: str, level: int) -> List[FeatureInstance]:
        """Grant all subclass features for a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, feature_name, feature_type, description, mechanics, prerequisites
                FROM subclass_features_progression
                WHERE subclass_id = ? AND level = ?
                ORDER BY feature_name
            """, (subclass_id, level))

            features = cursor.fetchall()
            granted_features = []

            for feature_data in features:
                feature_id, name, feature_type, description, mechanics_json, prerequisites_json = feature_data

                mechanics = json.loads(mechanics_json) if mechanics_json else {}
                prerequisites = json.loads(prerequisites_json) if prerequisites_json else {}

                if not self._check_prerequisites(cursor, character_id, prerequisites):
                    continue

                if self._character_has_feature(cursor, character_id, name, 'subclass'):
                    continue

                max_uses, recharge_type = self._calculate_feature_uses(mechanics, level)

                feature_instance = FeatureInstance(
                    id=None,
                    character_id=character_id,
                    feature_source='subclass',
                    feature_id=feature_id,
                    feature_name=name,
                    level_gained=level,
                    current_uses=max_uses,
                    max_uses=max_uses,
                    recharge_type=recharge_type,
                    configuration=mechanics,
                    active=True
                )

                self._insert_character_feature(cursor, feature_instance)
                granted_features.append(feature_instance)

            conn.commit()
            return granted_features

    def get_character_features(self, character_id: str, active_only: bool = True) -> List[FeatureInstance]:
        """Get all features for a character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT id, character_id, feature_source, feature_id, feature_name,
                       level_gained, current_uses, max_uses, recharge_type,
                       configuration, active
                FROM character_feature_instances
                WHERE character_id = ?
            """
            params = [character_id]

            if active_only:
                query += " AND active = 1"

            query += " ORDER BY level_gained, feature_name"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            features = []
            for row in rows:
                config = json.loads(row[9]) if row[9] else {}
                feature = FeatureInstance(
                    id=row[0],
                    character_id=row[1],
                    feature_source=row[2],
                    feature_id=row[3],
                    feature_name=row[4],
                    level_gained=row[5],
                    current_uses=row[6],
                    max_uses=row[7],
                    recharge_type=row[8],
                    configuration=config,
                    active=bool(row[10])
                )
                features.append(feature)

            return features

    def update_feature_uses(self, character_id: str, feature_name: str, current_uses: int):
        """Update the current uses of a feature"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_feature_instances
                SET current_uses = ?
                WHERE character_id = ? AND feature_name = ?
            """, (current_uses, character_id, feature_name))
            conn.commit()

    def recharge_features(self, character_id: str, recharge_type: str):
        """Recharge features that use the specified recharge type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_feature_instances
                SET current_uses = max_uses
                WHERE character_id = ? AND recharge_type = ?
            """, (character_id, recharge_type))
            conn.commit()

    def configure_feature(self, character_id: str, feature_name: str, configuration: Dict[str, Any]):
        """Update feature configuration (e.g., chosen fighting style, expertise skills)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_feature_instances
                SET configuration = ?
                WHERE character_id = ? AND feature_name = ?
            """, (json.dumps(configuration), character_id, feature_name))
            conn.commit()

    def _check_prerequisites(self, cursor, character_id: str, prerequisites: Dict[str, Any]) -> bool:
        """Check if character meets prerequisites for a feature"""
        if not prerequisites:
            return True

        # Add prerequisite checking logic here
        # For now, assume all prerequisites are met
        return True

    def _character_has_feature(self, cursor, character_id: str, feature_name: str, source: str) -> bool:
        """Check if character already has this feature"""
        cursor.execute("""
            SELECT 1 FROM character_feature_instances
            WHERE character_id = ? AND feature_name = ? AND feature_source = ?
        """, (character_id, feature_name, source))
        return cursor.fetchone() is not None

    def _calculate_feature_uses(self, mechanics: Dict[str, Any], level: int) -> tuple[int, Optional[str]]:
        """Calculate max uses and recharge type based on feature mechanics"""
        if 'uses_per_long_rest' in mechanics:
            uses = mechanics['uses_per_long_rest']
            if isinstance(uses, str):
                if uses == 'charisma_modifier':
                    return 3, 'long_rest'  # Default to 3 for now
                elif uses == 'wisdom_modifier':
                    return 3, 'long_rest'
                elif uses.endswith('_plus_cha_mod'):
                    return 4, 'long_rest'  # 1 + 3 default
                else:
                    return int(uses) if uses.isdigit() else 1, 'long_rest'
            return uses, 'long_rest'

        if 'uses_per_short_rest' in mechanics:
            uses = mechanics['uses_per_short_rest']
            return uses if isinstance(uses, int) else 1, 'short_rest'

        # No limited uses
        return 0, None

    def _insert_character_feature(self, cursor, feature: FeatureInstance):
        """Insert a character feature into the database"""
        cursor.execute("""
            INSERT INTO character_feature_instances
            (character_id, feature_source, feature_id, feature_name, level_gained,
             current_uses, max_uses, recharge_type, configuration, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feature.character_id,
            feature.feature_source,
            feature.feature_id,
            feature.feature_name,
            feature.level_gained,
            feature.current_uses,
            feature.max_uses,
            feature.recharge_type,
            json.dumps(feature.configuration),
            feature.active
        ))

    def get_feature_progression_summary(self, class_id: str, subclass_id: Optional[str] = None) -> Dict[int, List[str]]:
        """Get a summary of features by level for a class/subclass"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get class features
            cursor.execute("""
                SELECT level, feature_name FROM class_features_progression
                WHERE class_id = ? ORDER BY level, feature_name
            """, (class_id,))

            features_by_level = {}
            for level, name in cursor.fetchall():
                if level not in features_by_level:
                    features_by_level[level] = []
                features_by_level[level].append(f"{name} (Class)")

            # Get subclass features if specified
            if subclass_id:
                cursor.execute("""
                    SELECT level, feature_name FROM subclass_features_progression
                    WHERE subclass_id = ? ORDER BY level, feature_name
                """, (subclass_id,))

                for level, name in cursor.fetchall():
                    if level not in features_by_level:
                        features_by_level[level] = []
                    features_by_level[level].append(f"{name} (Subclass)")

            return features_by_level