# core
# category: core
import sqlite3
import json
import time
from typing import Dict, List, Optional, Tuple, Any, Callable


class UnifiedLevelUpService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        from talekeeper.services.feature_registry import FeatureRegistry
        self.feature_registry = FeatureRegistry(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get optimized database connection.

        Uses WAL mode-compatible settings for concurrent access.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.row_factory = sqlite3.Row
        return conn

    def _retry_on_lock(self, operation: Callable, max_retries: int = 3, operation_name: str = "operation") -> Any:
        """
        Retry an operation with exponential backoff if it encounters a database lock.

        Args:
            operation: Callable that performs the database operation
            max_retries: Maximum number of retry attempts
            operation_name: Name of operation for logging

        Returns:
            Result from the operation

        Raises:
            sqlite3.OperationalError: If all retries are exhausted
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return operation()
            except sqlite3.OperationalError as e:
                last_error = e
                if "locked" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = 0.1 * (2 ** attempt)  # Exponential backoff: 0.1s, 0.2s, 0.4s
                        print(f"[UnifiedLevelUp] Database locked during {operation_name}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"[UnifiedLevelUp] Failed after {max_retries} attempts: {e}")
                        raise
                else:
                    raise  # Re-raise non-lock errors immediately

        raise last_error

    def get_available_classes(self) -> List[str]:
        """Get list of available classes for leveling."""
        return ['Barbarian', 'Cleric', 'Paladin', 'Rogue', 'Warlock', 'Wizard', 'Fighter']

    def get_character_class_levels(self, character_id: str) -> Dict[str, int]:
        """Get current class levels for a character."""
        conn = self._get_connection()
        cursor = conn.cursor()
        result = {}

        try:
            cursor.execute("""
                SELECT class_name, level
                FROM character_class_levels
                WHERE character_id = ?
            """, (character_id,))

            result = {class_name.lower(): level for class_name, level in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting character class levels: {e}")
            result = {}
        finally:
            conn.close()

        return result

    def is_asi_level(self, character_id: str, class_choice: str) -> bool:
        """Check if next level grants ASI for the selected class."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT level FROM character_class_levels
                WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
            """, (character_id, class_choice))

            result = cursor.fetchone()
            if result:
                current_class_level = result[0]
            else:
                cursor.execute("""
                    SELECT level, class_id FROM characters
                    WHERE id = ?
                """, (character_id,))
                char_result = cursor.fetchone()
                if char_result and char_result[1] and char_result[1].lower() == class_choice.lower():
                    current_class_level = char_result[0]
                else:
                    current_class_level = 0

            next_class_level = current_class_level + 1

            asi_levels = {
                'fighter': [4, 6, 8, 12, 14, 16],
                'rogue': [4, 8, 10, 12, 16],
                'barbarian': [4, 8, 12, 16],
                'bard': [4, 8, 12, 16],
                'cleric': [4, 8, 12, 16],
                'druid': [4, 8, 12, 16],
                'monk': [4, 8, 12, 16],
                'paladin': [4, 8, 12, 16],
                'ranger': [4, 8, 12, 16],
                'sorcerer': [4, 8, 12, 16],
                'warlock': [4, 8, 12, 16],
                'wizard': [4, 8, 12, 16]
            }

            class_name = class_choice.lower()
            if class_name in asi_levels:
                is_asi = next_class_level in asi_levels[class_name]
            else:
                is_asi = next_class_level in [4, 8, 12, 16, 19]

            conn.close()
            return is_asi

        except Exception as e:
            print(f"Error checking ASI level: {e}")
            return False

    def level_up_character(self, character_id: str) -> Dict[str, Any]:
        """Level up a character using the unified feature system"""
        with self._get_connection() as conn:
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

            cursor.execute("""
                UPDATE character_class_levels
                SET level = ?
                WHERE character_id = ? AND LOWER(class_name) = LOWER(?)
            """, (new_level, character_id, class_id))

            expected_hp = self._calculate_total_hp_for_level(cursor, character_id, class_id, new_level, character['constitution'])
            current_hp_max = character['max_hp']

            if expected_hp != current_hp_max:
                hp_gain = expected_hp - current_hp_max
                current_hp_current = character.get('hit_points_current', current_hp_max)
                new_current_hp = min(current_hp_current + hp_gain, expected_hp)

                cursor.execute("UPDATE characters SET hit_points_max = ?, hit_points_current = ? WHERE id = ?",
                             (expected_hp, new_current_hp, character_id))
                results["hp_gained"] = hp_gain

            # Update spellcasting for all spellcasting classes
            spellcasting_classes = ['wizard', 'cleric', 'druid', 'bard', 'sorcerer', 'ranger']
            if class_id in spellcasting_classes:
                try:
                    from talekeeper.services.spellcasting_progression import SpellcastingProgressionService
                    progression_service = SpellcastingProgressionService(self.db_path)
                    progression_service.update_spellcasting_on_level_up(character_id, new_level, class_id)
                    print(f"[UnifiedLevelUp] Updated {class_id} spell slots for level {new_level}")
                except Exception as e:
                    print(f"[UnifiedLevelUp] Error updating {class_id} spell slots: {e}")

            if class_id == 'warlock':
                warlock_choices = self._handle_warlock_level_up(cursor, character_id, new_level)
                if warlock_choices:
                    results["choices_required"].extend(warlock_choices)

            if class_id == 'fighter':
                self._handle_fighter_level_up(cursor, character_id, new_level)

            if class_id == 'rogue':
                self._handle_rogue_level_up(cursor, character_id, new_level)

            if class_id == 'paladin':
                self._handle_paladin_level_up(cursor, character_id, new_level, subclass_id)

            conn.commit()

        # Handle barbarian resources AFTER main transaction to avoid lock
        if class_id == 'barbarian':
            try:
                from talekeeper.services.character_resources import CharacterResourceService
                resource_service = CharacterResourceService(self.db_path)
                result = resource_service.initialize_barbarian_resources(character_id, new_level)
                print(f"[UnifiedLevelUp] Updated Barbarian resources: {result.get('resources_added', [])}")
            except Exception as e:
                print(f"[UnifiedLevelUp] Error in Barbarian resource initialization: {e}")

        try:
            from talekeeper.services.class_abilities_service import ClassAbilitiesService
            abilities_service = ClassAbilitiesService(self.db_path)
            abilities_service.update_ability_resources_for_level(character_id, new_level)
            print(f"[UnifiedLevelUp] Updated class abilities for {class_id} level {new_level}")
        except Exception as e:
            print(f"[UnifiedLevelUp] Warning: Class abilities update failed: {e}")

        try:
            from talekeeper.core.feature_integration import FeatureSystemIntegration
            feature_system = FeatureSystemIntegration(self.db_path)
            feature_system.initialize_character_features(character_id)
            print(f"[UnifiedLevelUp] Updated feature system for {class_id} level {new_level}")
        except Exception as e:
            print(f"Error initializing features: {e}")

        return results

    def _get_character_data(self, cursor, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character data from database"""
        cursor.execute("""
            SELECT level, class_id, subclass_id, hit_points_max, constitution
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

    def _calculate_total_hp_for_level(self, cursor, character_id: str, class_id: str, level: int, constitution: int) -> int:
        """Calculate expected total HP for a given level"""
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

        hp_at_level_1 = base_hp + con_modifier
        hp_per_additional_level = max(1, base_hp // 2 + 1 + con_modifier)

        bonus_hp_per_level = 0

        cursor.execute("SELECT feat_name, feat_id FROM character_feats WHERE character_id = ?", (character_id,))
        feat_rows = cursor.fetchall()
        feat_names = [(row[0] or '').lower() for row in feat_rows]
        feat_ids = [(row[1] or '').lower() for row in feat_rows]
        if 'tough' in feat_names or 'toughness' in feat_names or 'tough' in feat_ids or 'toughness' in feat_ids:
            bonus_hp_per_level += 2

        cursor.execute("SELECT race_id FROM characters WHERE id = ?", (character_id,))
        race_row = cursor.fetchone()
        if race_row and race_row[0] in ['hill_dwarf', 'dwarf_hill']:
            bonus_hp_per_level += 1

        total_bonus_hp = bonus_hp_per_level * level

        if level == 1:
            return max(1, hp_at_level_1 + total_bonus_hp)
        else:
            return max(level, hp_at_level_1 + (level - 1) * hp_per_additional_level + total_bonus_hp)

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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("UPDATE characters SET subclass_id = ? WHERE id = ?",
                         (subclass_id, character_id))

            character = self._get_character_data(cursor, character_id)
            current_level = character['level']
            conn.commit()

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

        return {
            "success": True,
            "subclass_id": subclass_id,
            "features_gained": subclass_features_gained
        }

    def apply_feature_choice(self, character_id: str, feature_instance_id: int,
                           choice: str) -> Dict[str, Any]:
        """Apply a choice for a feature (like fighting style, expertise skills)"""
        with self._get_connection() as conn:
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
        with self._get_connection() as conn:
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
        with self._get_connection() as conn:
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

        # Update pact magic slots
        try:
            from talekeeper.services.spellcasting_progression import SpellcastingProgressionService
            progression_service = SpellcastingProgressionService(self.db_path)
            progression_service.update_spellcasting_on_level_up(character_id, new_level, 'warlock')
            print(f"[UnifiedLevelUp] Updated Warlock pact magic slots for level {new_level}")
        except Exception as e:
            print(f"[UnifiedLevelUp] Error updating Warlock pact slots: {e}")

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
        with self._get_connection() as conn:
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
        """Apply selected spells to character's known/prepared spells"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if not spellcasting_class:
                cursor.execute("SELECT class_id FROM characters WHERE id = ?", (character_id,))
                row = cursor.fetchone()
                if row:
                    spellcasting_class = row[0]

            cursor.execute("SELECT 1 FROM character_spellcasting WHERE character_id = ? AND spellcasting_class = ?",
                         (character_id, spellcasting_class))
            if not cursor.fetchone():
                return {"success": False, "error": f"{spellcasting_class} spellcasting not found"}

            cursor.execute("SELECT level FROM characters WHERE id = ?", (character_id,))
            level_row = cursor.fetchone()
            char_level = level_row[0] if level_row else 1

            for spell_id in spell_ids:
                cursor.execute("SELECT level FROM spells WHERE id = ?", (spell_id,))
                spell_row = cursor.fetchone()
                if spell_row:
                    spell_level_num = spell_row[0]
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_spells
                        (character_id, spell_id, spell_level, is_prepared, source, source_level, always_prepared)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (character_id, spell_id, spell_level_num, True, 'class', char_level, False))

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

        with self._get_connection() as conn:
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

    def _handle_fighter_level_up(self, cursor, character_id: str, level: int):
        """Handle Fighter-specific level-up updates"""
        try:
            from talekeeper.services.character_resources import CharacterResourceService
            resource_service = CharacterResourceService(self.db_path)
            result = resource_service.initialize_fighter_resources(character_id, level)
            print(f"[UnifiedLevelUp] Updated Fighter resources: {result.get('resources_added', [])}")

            cursor.execute("UPDATE fighter_features SET level = ? WHERE character_id = ?", (level, character_id))

            if level == 2:
                cursor.execute("""
                    UPDATE fighter_features
                    SET action_surge_uses_max = 1, action_surge_uses_current = 1
                    WHERE character_id = ?
                """, (character_id,))
                cursor.execute("""
                    UPDATE characters
                    SET action_surge_uses_max = 1, action_surge_uses_current = 1
                    WHERE id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Action Surge to Fighter")

            elif level == 5:
                cursor.execute("""
                    UPDATE fighter_features
                    SET extra_attacks = 2
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Extra Attack to Fighter (2 attacks)")

            elif level == 11:
                cursor.execute("""
                    UPDATE fighter_features
                    SET extra_attacks = 3
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Two Extra Attacks to Fighter (3 attacks)")

            elif level == 9:
                cursor.execute("""
                    UPDATE fighter_features
                    SET indomitable_uses_max = 1, indomitable_uses_current = 1
                    WHERE character_id = ?
                """, (character_id,))
                cursor.execute("""
                    UPDATE characters
                    SET indomitable_uses_max = 1, indomitable_uses_current = 1
                    WHERE id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Indomitable to Fighter (1 use)")

            elif level == 13:
                cursor.execute("""
                    UPDATE fighter_features
                    SET indomitable_uses_max = 2, indomitable_uses_current = 2
                    WHERE character_id = ?
                """, (character_id,))
                cursor.execute("""
                    UPDATE characters
                    SET indomitable_uses_max = 2, indomitable_uses_current = 2
                    WHERE id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Improved Indomitable for Fighter (2 uses)")

            elif level == 17:
                cursor.execute("""
                    UPDATE fighter_features
                    SET action_surge_uses_max = 2, action_surge_uses_current = 2,
                        indomitable_uses_max = 3, indomitable_uses_current = 3
                    WHERE character_id = ?
                """, (character_id,))
                cursor.execute("""
                    UPDATE characters
                    SET action_surge_uses_max = 2, action_surge_uses_current = 2,
                        indomitable_uses_max = 3, indomitable_uses_current = 3
                    WHERE id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Improved Action Surge (2 uses) and Indomitable (3 uses) for Fighter")

            elif level == 20:
                cursor.execute("""
                    UPDATE fighter_features
                    SET extra_attacks = 4
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Three Extra Attacks to Fighter (4 attacks)")

        except Exception as e:
            print(f"[UnifiedLevelUp] Error in Fighter level-up: {e}")

    def _handle_rogue_level_up(self, cursor, character_id: str, level: int):
        """Handle Rogue-specific level-up updates"""
        try:
            sneak_attack_dice = (level + 1) // 2

            cursor.execute("SELECT character_id FROM rogue_features WHERE character_id = ?", (character_id,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute("""
                    INSERT INTO rogue_features
                    (character_id, level, sneak_attack_dice, cunning_action_available,
                     expertise_count, uncanny_dodge_available, evasion_available,
                     cunning_strike_available, reliable_talent_active, improved_cunning_strike,
                     slippery_mind_active, elusive_active, stroke_of_luck_uses_current, stroke_of_luck_uses_max)
                    VALUES (?, ?, ?, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                """, (character_id, level, sneak_attack_dice))
            else:
                cursor.execute("""
                    UPDATE rogue_features
                    SET level = ?, sneak_attack_dice = ?
                    WHERE character_id = ?
                """, (level, sneak_attack_dice, character_id))

            if level == 2:
                cursor.execute("""
                    UPDATE rogue_features
                    SET cunning_action_available = 1
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Cunning Action to Rogue")

            elif level == 5:
                cursor.execute("""
                    UPDATE rogue_features
                    SET uncanny_dodge_available = 1, cunning_strike_available = 1
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Uncanny Dodge and Cunning Strike to Rogue")

            elif level == 6:
                cursor.execute("""
                    UPDATE rogue_features
                    SET expertise_count = 4
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Improved Expertise to 4 skills")

            elif level == 7:
                cursor.execute("""
                    UPDATE rogue_features
                    SET evasion_available = 1
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Evasion to Rogue")

            elif level == 11:
                cursor.execute("""
                    UPDATE rogue_features
                    SET reliable_talent_active = 1, reliable_talent_minimum = 10
                    WHERE character_id = ?
                """, (character_id,))
                print(f"[UnifiedLevelUp] Granted Reliable Talent to Rogue")

        except Exception as e:
            print(f"[UnifiedLevelUp] Error in Rogue level-up: {e}")


    def _handle_paladin_level_up(self, cursor, character_id: str, level: int, subclass_id: Optional[str]):
        """Handle Paladin-specific level-up updates"""
        try:
            from talekeeper.services.paladin_abilities import get_paladin_service
            paladin_service = get_paladin_service(self.db_path)

            # Update spell slots
            try:
                from talekeeper.services.spellcasting_progression import SpellcastingProgressionService
                progression_service = SpellcastingProgressionService(self.db_path)
                progression_service.update_spellcasting_on_level_up(character_id, level, 'paladin')
                print(f"[UnifiedLevelUp] Updated Paladin spell slots for level {level}")
            except Exception as e:
                print(f"[UnifiedLevelUp] Error updating Paladin spell slots: {e}")

            prepared_spells_by_level = {
                1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9,
                11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15
            }
            max_prepared = prepared_spells_by_level.get(level, 2)

            cursor.execute("""
                UPDATE paladin_features
                SET level = ?, max_spells_prepared = ?, lay_on_hands_pool_max = ?,
                    channel_divinity_uses_max = CASE
                        WHEN ? >= 15 THEN 3
                        WHEN ? >= 7 THEN 2
                        WHEN ? >= 3 THEN 1
                        ELSE 0
                    END
                WHERE character_id = ?
            """, (level, max_prepared, level * 5, level, level, level, character_id))

            print(f"[UnifiedLevelUp] Updated Paladin features: level={level}, max_prepared={max_prepared}")

            if subclass_id:
                from talekeeper.services.subclass_feature_manager import SubclassFeatureManager
                subclass_feature_mgr = SubclassFeatureManager(self.db_path)

                features = subclass_feature_mgr.get_subclass_features_for_level(subclass_id, level)
                for feature in features:
                    subclass_feature_mgr.grant_subclass_feature(character_id, feature['id'], level)

                new_spells = subclass_feature_mgr.grant_oath_spells_for_level(character_id, subclass_id, level)
                if new_spells:
                    print(f"[UnifiedLevelUp] Granted oath spells: {', '.join(new_spells)}")

                print(f"[UnifiedLevelUp] Granted {len(features)} subclass features for {subclass_id}")

        except Exception as e:
            print(f"[UnifiedLevelUp] Error in Paladin level-up: {e}")