# core
# category: core
import sqlite3
import json
from typing import Dict, List, Optional, Any


class SubclassFeatureManager:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def get_subclass_features_for_level(self, subclass_id: str, level: int) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, subclass_id, level, feature_name, description,
                       mechanics, action_type, uses_per_rest, rest_type
                FROM subclass_features
                WHERE subclass_id = ? AND level = ?
                ORDER BY feature_name
            """, (subclass_id, level))

            features = []
            for row in cursor.fetchall():
                mechanics = json.loads(row[5]) if row[5] else {}
                features.append({
                    'id': row[0],
                    'subclass_id': row[1],
                    'level': row[2],
                    'feature_name': row[3],
                    'description': row[4],
                    'mechanics': mechanics,
                    'action_type': row[6],
                    'uses_per_rest': row[7],
                    'rest_type': row[8]
                })
            return features

    def get_all_subclass_features(self, subclass_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, subclass_id, level, feature_name, description,
                       mechanics, action_type, uses_per_rest, rest_type
                FROM subclass_features
                WHERE subclass_id = ?
                ORDER BY level, feature_name
            """, (subclass_id,))

            features = []
            for row in cursor.fetchall():
                mechanics = json.loads(row[5]) if row[5] else {}
                features.append({
                    'id': row[0],
                    'subclass_id': row[1],
                    'level': row[2],
                    'feature_name': row[3],
                    'description': row[4],
                    'mechanics': mechanics,
                    'action_type': row[6],
                    'uses_per_rest': row[7],
                    'rest_type': row[8]
                })
            return features

    def grant_subclass_feature(self, character_id: str, feature_id: int, level_gained: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT feature_name, uses_per_rest, rest_type, mechanics, action_type, description
                FROM subclass_features
                WHERE id = ?
            """, (feature_id,))

            row = cursor.fetchone()
            if not row:
                print(f"[SubclassFeatureManager] Feature {feature_id} not found")
                return False

            feature_name = row[0]
            max_uses = row[1] if row[1] else 0
            rest_type = row[2] if row[2] else 'permanent'
            mechanics = row[3]
            action_type = row[4] if row[4] else 'passive'
            description = row[5] if row[5] else ''

            try:
                cursor.execute("""
                    INSERT INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (character_id, feature_name, action_type, rest_type, level_gained, description, mechanics))

                if max_uses > 0:
                    cursor.execute("""
                        INSERT OR REPLACE INTO feature_states
                        (character_id, feature_name, feature_type, is_active, uses_current, uses_max, configuration)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (character_id, feature_name, action_type, False, max_uses, max_uses, mechanics))

                conn.commit()
                print(f"[SubclassFeatureManager] Granted {feature_name} to character {character_id}")
                return True

            except sqlite3.IntegrityError as e:
                print(f"[SubclassFeatureManager] Feature already granted or error: {e}")
                return False

    def get_character_subclass_features(self, character_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cf.id, cf.feature_name, cf.level_gained,
                       cf.feature_type, cf.usage_type, cf.description, cf.mechanics,
                       fs.uses_current, fs.uses_max
                FROM character_features cf
                LEFT JOIN feature_states fs
                    ON cf.character_id = fs.character_id
                    AND cf.feature_name = fs.feature_name
                WHERE cf.character_id = ?
                ORDER BY cf.level_gained, cf.feature_name
            """, (character_id,))

            features = []
            for row in cursor.fetchall():
                mechanics = json.loads(row[6]) if row[6] else {}
                features.append({
                    'id': row[0],
                    'feature_name': row[1],
                    'level_gained': row[2],
                    'action_type': row[3],
                    'usage_type': row[4],
                    'description': row[5],
                    'mechanics': mechanics,
                    'current_uses': row[7] if row[7] is not None else 0,
                    'max_uses': row[8] if row[8] is not None else 0
                })
            return features

    def use_feature(self, character_id: str, feature_instance_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT current_uses FROM character_feature_instances
                WHERE id = ? AND character_id = ?
            """, (feature_instance_id, character_id))

            row = cursor.fetchone()
            if not row:
                return False

            current_uses = row[0]
            if current_uses <= 0:
                return False

            cursor.execute("""
                UPDATE character_feature_instances
                SET current_uses = current_uses - 1
                WHERE id = ? AND character_id = ?
            """, (feature_instance_id, character_id))

            conn.commit()
            return True

    def recharge_features(self, character_id: str, rest_type: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if rest_type == 'short':
                cursor.execute("""
                    UPDATE character_feature_instances
                    SET current_uses = max_uses
                    WHERE character_id = ?
                    AND feature_source = 'subclass'
                    AND recharge_type IN ('short', 'none')
                """, (character_id,))
            elif rest_type == 'long':
                cursor.execute("""
                    UPDATE character_feature_instances
                    SET current_uses = max_uses
                    WHERE character_id = ?
                    AND feature_source = 'subclass'
                """, (character_id,))

            affected = cursor.rowcount
            conn.commit()
            return affected

    def get_oath_spells(self, subclass_id: str, paladin_level: int) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT spell_name
                FROM subclass_spells
                WHERE subclass_id = ? AND paladin_level <= ?
                ORDER BY paladin_level, spell_name
            """, (subclass_id, paladin_level))

            return [row[0] for row in cursor.fetchall()]

    def grant_oath_spells_for_level(self, character_id: str, subclass_id: str, paladin_level: int) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT spell_name
                FROM subclass_spells
                WHERE subclass_id = ? AND paladin_level = ?
            """, (subclass_id, paladin_level))

            new_spells = [row[0] for row in cursor.fetchall()]

            for spell_name in new_spells:
                try:
                    cursor.execute("""
                        INSERT INTO character_spells (character_id, spell_name, source, always_prepared)
                        VALUES (?, ?, 'oath', 1)
                    """, (character_id, spell_name))
                    print(f"[SubclassFeatureManager] Granted oath spell {spell_name} to {character_id}")
                except sqlite3.IntegrityError:
                    print(f"[SubclassFeatureManager] Spell {spell_name} already known by {character_id}")

            conn.commit()
            return new_spells