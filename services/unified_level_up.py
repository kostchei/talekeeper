# core
# core
import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from services.feature_registry import FeatureRegistry


class UnifiedLevelUpService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_registry = FeatureRegistry(db_path)

    def level_up_character(self, character_id: str) -> Dict[str, Any]:
        """Level up a character using the unified feature system"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            character = self._get_character_data(cursor, character_id)
            if not character:
                return {"success": False, "error": "Character not found"}

            current_level = character['level']
            new_level = current_level + 1
            class_id = character['class_id']
            subclass_id = character.get('subclass_id')

            if new_level > 20:
                return {"success": False, "error": "Maximum level reached"}

            results = {
                "success": True,
                "old_level": current_level,
                "new_level": new_level,
                "features_gained": [],
                "choices_required": [],
                "hp_gained": 0
            }

            cursor.execute("UPDATE characters SET level = ? WHERE id = ?", (new_level, character_id))

            class_features = self.feature_registry.get_class_features_for_level(class_id, new_level)
            for feature in class_features:
                self._grant_class_feature(cursor, character_id, feature, new_level, results)

            if subclass_id:
                subclass_features = self.feature_registry.get_subclass_features_for_level(subclass_id, new_level)
                for feature in subclass_features:
                    self._grant_subclass_feature(cursor, character_id, feature, new_level, results)

            hp_gain = self._calculate_hp_gain(class_id, character['constitution'])
            if hp_gain > 0:
                new_hp = character['max_hp'] + hp_gain
                cursor.execute("UPDATE characters SET max_hp = ?, current_hp = ? WHERE id = ?",
                             (new_hp, new_hp, character_id))
                results["hp_gained"] = hp_gain

            subclass_selection_level = self.feature_registry.get_subclass_selection_level(class_id)
            if new_level == subclass_selection_level and not subclass_id:
                available_subclasses = self.feature_registry.get_available_subclasses(class_id)
                results["choices_required"].append({
                    "type": "subclass_selection",
                    "options": available_subclasses
                })

            if new_level == 19 and not self._has_epic_boon(cursor, character_id):
                results["choices_required"].append({
                    "type": "epic_boon",
                    "level": 19
                })

            conn.commit()
            return results

    def _get_character_data(self, cursor, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character data from database"""
        cursor.execute("""
            SELECT level, class_id, subclass_id, max_hp, constitution
            FROM characters WHERE id = ?
        """, (character_id,))

        row = cursor.fetchone()
        if row:
            return {
                'level': row[0],
                'class_id': row[1],
                'subclass_id': row[2],
                'max_hp': row[3],
                'constitution': row[4]
            }
        return None

    def _grant_class_feature(self, cursor, character_id: str, feature: Dict[str, Any],
                           level: int, results: Dict[str, Any]):
        """Grant a class feature to the character"""
        mechanics = feature['mechanics']
        max_uses = 0
        recharge_type = 'permanent'

        if 'uses_per_short_rest' in mechanics:
            max_uses = mechanics['uses_per_short_rest']
            recharge_type = 'short_rest'
        elif 'uses_per_long_rest' in mechanics:
            max_uses = mechanics['uses_per_long_rest']
            recharge_type = 'long_rest'

        feature_instance_id = self.feature_registry.grant_feature_to_character(
            character_id=character_id,
            feature_source='class',
            feature_id=feature['id'],
            feature_name=feature['feature_name'],
            level_gained=level,
            max_uses=max_uses,
            recharge_type=recharge_type
        )

        results["features_gained"].append({
            "name": feature['feature_name'],
            "type": feature['feature_type'],
            "description": feature['description'],
            "source": "class"
        })

        if 'choice' in mechanics:
            results["choices_required"].append({
                "type": "feature_choice",
                "feature_name": feature['feature_name'],
                "feature_instance_id": feature_instance_id,
                "options": mechanics['choice']
            })

        if 'asi_or_feat' in mechanics and mechanics['asi_or_feat']:
            results["choices_required"].append({
                "type": "asi_or_feat",
                "level": level
            })

    def _grant_subclass_feature(self, cursor, character_id: str, feature: Dict[str, Any],
                              level: int, results: Dict[str, Any]):
        """Grant a subclass feature to the character"""
        mechanics = feature['mechanics']
        max_uses = 0
        recharge_type = 'permanent'

        if 'uses_per_short_rest' in mechanics:
            max_uses = mechanics['uses_per_short_rest']
            recharge_type = 'short_rest'
        elif 'uses_per_long_rest' in mechanics:
            max_uses = mechanics['uses_per_long_rest']
            recharge_type = 'long_rest'

        feature_instance_id = self.feature_registry.grant_feature_to_character(
            character_id=character_id,
            feature_source='subclass',
            feature_id=feature['id'],
            feature_name=feature['feature_name'],
            level_gained=level,
            max_uses=max_uses,
            recharge_type=recharge_type
        )

        results["features_gained"].append({
            "name": feature['feature_name'],
            "type": feature['feature_type'],
            "description": feature['description'],
            "source": "subclass"
        })

    def _calculate_hp_gain(self, class_id: str, constitution: int) -> int:
        """Calculate HP gain for level up"""
        hit_dice = {
            'barbarian': 12,
            'fighter': 10,
            'paladin': 10,
            'ranger': 10,
            'bard': 8,
            'cleric': 8,
            'druid': 8,
            'rogue': 8,
            'warlock': 8,
            'sorcerer': 6,
            'wizard': 6
        }

        base_hp = hit_dice.get(class_id, 8)
        con_modifier = (constitution - 10) // 2

        return max(1, base_hp // 2 + 1 + con_modifier)

    def apply_subclass_choice(self, character_id: str, subclass_id: str) -> Dict[str, Any]:
        """Apply a subclass choice to a character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("UPDATE characters SET subclass_id = ? WHERE id = ?",
                         (subclass_id, character_id))

            character = self._get_character_data(cursor, character_id)
            current_level = character['level']

            subclass_features_gained = []
            for level in range(1, current_level + 1):
                subclass_features = self.feature_registry.get_subclass_features_for_level(subclass_id, level)
                for feature in subclass_features:
                    mechanics = feature['mechanics']
                    max_uses = 0
                    recharge_type = 'permanent'

                    if 'uses_per_short_rest' in mechanics:
                        max_uses = mechanics['uses_per_short_rest']
                        recharge_type = 'short_rest'
                    elif 'uses_per_long_rest' in mechanics:
                        max_uses = mechanics['uses_per_long_rest']
                        recharge_type = 'long_rest'

                    self.feature_registry.grant_feature_to_character(
                        character_id=character_id,
                        feature_source='subclass',
                        feature_id=feature['id'],
                        feature_name=feature['feature_name'],
                        level_gained=level,
                        max_uses=max_uses,
                        recharge_type=recharge_type
                    )

                    subclass_features_gained.append(feature['feature_name'])

            conn.commit()

            return {
                "success": True,
                "subclass_id": subclass_id,
                "features_gained": subclass_features_gained
            }

    def apply_feature_choice(self, character_id: str, feature_instance_id: int,
                           choice: str) -> Dict[str, Any]:
        """Apply a choice for a feature (like fighting style, expertise skills)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT configuration FROM character_feature_instances
                WHERE id = ? AND character_id = ?
            """, (feature_instance_id, character_id))

            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Feature instance not found"}

            current_config = json.loads(row[0]) if row[0] else {}
            current_config['choice'] = choice

            cursor.execute("""
                UPDATE character_feature_instances
                SET configuration = ?
                WHERE id = ? AND character_id = ?
            """, (json.dumps(current_config), feature_instance_id, character_id))

            conn.commit()

            return {
                "success": True,
                "choice_applied": choice
            }

    def _has_epic_boon(self, cursor, character_id: str) -> bool:
        """Check if character already has an Epic Boon feat"""
        cursor.execute("""
            SELECT COUNT(*) FROM character_feats
            WHERE character_id = ? AND feat_name LIKE 'Boon of%'
        """, (character_id,))
        return cursor.fetchone()[0] > 0

    def get_available_epic_boons(self) -> List[Dict[str, Any]]:
        """Get all available Epic Boon feats"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, description, prerequisites
                FROM feats
                WHERE name LIKE 'Boon of%'
                ORDER BY name
            """)

            boons = []
            for row in cursor.fetchall():
                boons.append({
                    "name": row[0],
                    "description": row[1],
                    "prerequisites": row[2]
                })
            return boons

    def apply_epic_boon(self, character_id: str, boon_name: str) -> Dict[str, Any]:
        """Apply an Epic Boon feat to the character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if self._has_epic_boon(cursor, character_id):
                return {"success": False, "error": "Character already has an Epic Boon"}

            cursor.execute("""
                INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
                VALUES (?, ?, 'level_19_epic_boon', 19)
            """, (character_id, boon_name))

            conn.commit()

            return {
                "success": True,
                "boon_granted": boon_name
            }