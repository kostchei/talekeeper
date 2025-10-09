import sqlite3
import json
from typing import Dict, List, Optional, Tuple, Any
from talekeeper.services.feature_registry import FeatureRegistry
from talekeeper.services.spellcasting_progression import SpellcastingProgressionService


class UnifiedLevelUpService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_registry = FeatureRegistry(db_path)
        self.spellcasting_progression = SpellcastingProgressionService(db_path)

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

            spell_result = self.spellcasting_progression.update_spellcasting_on_level_up(
                character_id, new_level, class_id
            )
            if spell_result.get('success'):
                results['spellcasting_updated'] = spell_result

                if spell_result.get('prepared_spell_count', 0) > 0:
                    results["choices_required"].append({
                        "type": "spell_preparation",
                        "class": class_id,
                        "max_prepared": spell_result['prepared_spell_count']
                    })

                if spell_result.get('cantrips_updated'):
                    results["choices_required"].append({
                        "type": "cantrip_selection",
                        "class": class_id,
                        "new_cantrips": spell_result['new_cantrips']
                    })

            if class_id == 'warlock':
                warlock_choices = self._handle_warlock_level_up(cursor, character_id, new_level)
                if warlock_choices:
                    results["choices_required"].extend(warlock_choices)

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

    def _handle_warlock_level_up(self, cursor, character_id: str, new_level: int) -> List[Dict[str, Any]]:
        """Handle Warlock-specific level-up choices (invocations and pact boon)"""
        choices = []

        cursor.execute("""
            SELECT formula_data FROM ability_scaling_formulas
            WHERE formula_name = 'invocations_by_level'
        """)
        row = cursor.fetchone()
        if row:
            invocations_formula = json.loads(row[0])
            old_invocations = invocations_formula.get(str(new_level - 1), 0)
            new_invocations = invocations_formula.get(str(new_level), 0)

            if new_invocations > old_invocations:
                invocations_to_learn = new_invocations - old_invocations
                choices.append({
                    "type": "eldritch_invocations",
                    "count": invocations_to_learn,
                    "total_known": new_invocations,
                    "level": new_level
                })

        if new_level == 3:
            choices.append({
                "type": "pact_boon",
                "options": ["blade", "chain", "tome"],
                "level": 3
            })

        return choices

    def apply_warlock_invocations(self, character_id: str, invocation_ids: List[str]) -> Dict[str, Any]:
        """Apply selected Eldritch Invocations to character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            level_row = cursor.fetchone()
            if not level_row:
                return {"success": False, "error": "Character not found"}

            level = level_row[0]

            for invocation_id in invocation_ids:
                cursor.execute("""
                    INSERT OR IGNORE INTO warlock_invocations (character_id, invocation_id, learned_at_level)
                    VALUES (?, ?, ?)
                """, (character_id, invocation_id, level))

                ability_id = f"invocation_{invocation_id}"
                cursor.execute("""
                    SELECT ability_id, uses_formula FROM class_abilities
                    WHERE ability_id = ? AND class_name = 'Warlock'
                """, (ability_id,))
                ability = cursor.fetchone()

                if ability:
                    max_uses = self._calculate_ability_max_uses(cursor, character_id, ability[1], level)
                    cursor.execute("""
                        INSERT OR REPLACE INTO character_ability_usage
                        (character_id, ability_id, current_uses, max_uses, is_active, turns_remaining)
                        VALUES (?, ?, ?, ?, 0, 0)
                    """, (character_id, ability_id, max_uses, max_uses))

            cursor.execute("""
                SELECT invocations_known FROM warlock_features WHERE character_id = ?
            """, (character_id,))
            current_row = cursor.fetchone()
            current = json.loads(current_row[0]) if current_row and current_row[0] else []

            for invocation_id in invocation_ids:
                if invocation_id not in current:
                    current.append(invocation_id)

            cursor.execute("""
                UPDATE warlock_features
                SET invocations_known = ?
                WHERE character_id = ?
            """, (json.dumps(current), character_id))

            conn.commit()

            return {
                "success": True,
                "invocations_learned": invocation_ids
            }

    def _calculate_ability_max_uses(self, cursor, character_id: str, uses_formula: Optional[str], level: int) -> int:
        """Calculate max uses for an ability based on formula"""
        if not uses_formula:
            return 0

        if uses_formula == 'proficiency_bonus':
            prof_bonus = 2 + ((level - 1) // 4)
            return prof_bonus
        elif 'level' in uses_formula:
            try:
                return eval(uses_formula.replace('level', str(level)))
            except:
                return 0
        elif uses_formula.isdigit():
            return int(uses_formula)
        else:
            return 0

    def apply_spell_selection(self, character_id: str, spell_ids: List[str], spellcasting_class: str = None) -> Dict[str, Any]:
        """Apply selected spells to character's known/prepared spells (works for Warlock, Sorcerer, Wizard, etc)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if not spellcasting_class:
                cursor.execute("""
                    SELECT class_id FROM characters WHERE id = ?
                """, (character_id,))
                row = cursor.fetchone()
                if row:
                    spellcasting_class = row[0]

            cursor.execute("""
                SELECT known_spells FROM character_spellcasting
                WHERE character_id = ? AND spellcasting_class = ?
            """, (character_id, spellcasting_class))

            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"{spellcasting_class} spellcasting not found"}

            known_spells = json.loads(row[0]) if row[0] else {}

            for spell_id in spell_ids:
                cursor.execute("SELECT level FROM spells WHERE id = ?", (spell_id,))
                spell_row = cursor.fetchone()
                if spell_row:
                    spell_level = str(spell_row[0])
                    if spell_level not in known_spells:
                        known_spells[spell_level] = []
                    if spell_id not in known_spells[spell_level]:
                        known_spells[spell_level].append(spell_id)

            cursor.execute("""
                UPDATE character_spellcasting
                SET known_spells = ?
                WHERE character_id = ? AND spellcasting_class = ?
            """, (json.dumps(known_spells), character_id, spellcasting_class))

            conn.commit()

            return {
                "success": True,
                "spells_learned": spell_ids
            }

    def apply_pact_boon(self, character_id: str, pact_boon: str) -> Dict[str, Any]:
        """Apply Pact Boon choice to Warlock"""
        valid_pacts = ['blade', 'chain', 'tome']
        if pact_boon.lower() not in valid_pacts:
            return {"success": False, "error": f"Invalid pact boon: {pact_boon}"}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE warlock_features
                SET pact_boon = ?
                WHERE character_id = ?
            """, (pact_boon.lower(), character_id))

            conn.commit()

            return {
                "success": True,
                "pact_boon": pact_boon.lower()
            }