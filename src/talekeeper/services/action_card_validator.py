"""
Action Card Validation System

Ensures that every class feature with an action economy (action, bonus action,
reaction, free action) has a corresponding action card created in the UI.

This validation runs during character creation and raises identifiable errors
if any action cards are missing.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ActionCardValidationError(Exception):
    """Raised when action card validation fails during character creation"""
    pass


class FeatureActivationType(Enum):
    """Types of feature activation"""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE_ACTION = "free_action"
    PASSIVE = "passive"
    AUTOMATIC = "automatic"


@dataclass
class FeatureActionMapping:
    """Maps a class feature to its required action card"""
    feature_name: str
    action_card_id: str
    activation_type: FeatureActivationType
    class_name: str
    subclass_name: Optional[str] = None
    min_level: int = 1
    requires_uses: bool = True  # Does it consume uses?


class ActionCardValidator:
    """Validates that all features with activation types have action cards"""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self._feature_mappings: Dict[str, FeatureActionMapping] = {}
        self._initialize_mappings()

    def _initialize_mappings(self):
        """Initialize the feature -> action card mappings"""

        # === BARBARIAN FEATURES ===

        self.register_mapping(FeatureActionMapping(
            feature_name="Rage",
            action_card_id="barbarian_rage",
            activation_type=FeatureActivationType.BONUS_ACTION,
            class_name="barbarian",
            min_level=1,
            requires_uses=True
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Reckless Attack",
            action_card_id="barbarian_reckless_attack",
            activation_type=FeatureActivationType.FREE_ACTION,
            class_name="barbarian",
            min_level=2,
            requires_uses=False
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Brutal Strike",
            action_card_id="barbarian_brutal_strike",
            activation_type=FeatureActivationType.FREE_ACTION,
            class_name="barbarian",
            min_level=9,
            requires_uses=True
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Frenzy",
            action_card_id="berserker_frenzy",
            activation_type=FeatureActivationType.FREE_ACTION,
            class_name="barbarian",
            subclass_name="berserker",
            min_level=3,
            requires_uses=False
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Retaliation",
            action_card_id="berserker_retaliation",
            activation_type=FeatureActivationType.REACTION,
            class_name="barbarian",
            subclass_name="berserker",
            min_level=10,
            requires_uses=False
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Intimidating Presence",
            action_card_id="berserker_intimidating_presence",
            activation_type=FeatureActivationType.BONUS_ACTION,
            class_name="barbarian",
            subclass_name="berserker",
            min_level=14,
            requires_uses=True
        ))

        # === FIGHTER FEATURES ===

        self.register_mapping(FeatureActionMapping(
            feature_name="Second Wind",
            action_card_id="fighter_second_wind",
            activation_type=FeatureActivationType.BONUS_ACTION,
            class_name="fighter",
            min_level=1,
            requires_uses=True
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Action Surge",
            action_card_id="fighter_action_surge",
            activation_type=FeatureActivationType.FREE_ACTION,
            class_name="fighter",
            min_level=2,
            requires_uses=True
        ))

        self.register_mapping(FeatureActionMapping(
            feature_name="Indomitable",
            action_card_id="fighter_indomitable",
            activation_type=FeatureActivationType.REACTION,
            class_name="fighter",
            min_level=9,
            requires_uses=True
        ))

        # Add more classes as needed...

    def register_mapping(self, mapping: FeatureActionMapping):
        """Register a feature -> action card mapping"""
        key = self._get_mapping_key(
            mapping.feature_name,
            mapping.class_name,
            mapping.subclass_name
        )
        self._feature_mappings[key] = mapping

    def _get_mapping_key(self, feature_name: str, class_name: str, subclass_name: Optional[str] = None) -> str:
        """Generate unique key for feature mapping"""
        if subclass_name:
            return f"{class_name}:{subclass_name}:{feature_name}".lower()
        return f"{class_name}:{feature_name}".lower()

    def validate_character_actions(
        self,
        character_id: str,
        raise_on_error: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all features with action economy have action cards.

        Args:
            character_id: Character to validate
            raise_on_error: If True, raise ActionCardValidationError on failure

        Returns:
            Tuple of (success, list_of_errors)

        Raises:
            ActionCardValidationError: If validation fails and raise_on_error=True
        """
        errors = []

        # Get character data
        character_data = self._get_character_data(character_id)
        if not character_data:
            error = f"Character {character_id} not found in database"
            if raise_on_error:
                raise ActionCardValidationError(error)
            return False, [error]

        class_name = character_data['class_id']
        level = character_data['level']
        subclass_name = character_data.get('subclass_id')

        print(f"\n[ACTION CARD VALIDATOR] Validating {character_data['name']}")
        print(f"  Class: {class_name}, Level: {level}, Subclass: {subclass_name or 'None'}")

        # Get expected features for this character
        expected_features = self._get_expected_features(class_name, level, subclass_name)

        if not expected_features:
            print(f"  [OK] No action card features required for this class/level")
            return True, []

        print(f"  Expected {len(expected_features)} action card features:")

        # Check each expected feature
        for mapping in expected_features:
            print(f"    - {mapping.feature_name} ({mapping.activation_type.value})")

            # Check if feature exists in database
            feature_exists = self._feature_exists_in_db(character_id, mapping)

            if not feature_exists:
                error = (
                    f"[MISSING FEATURE] {mapping.feature_name} not found for "
                    f"{character_data['name']} ({class_name} {level})"
                )
                errors.append(error)
                print(f"      [FAIL] Feature not in database!")
                continue

            # Check if resource exists (if required)
            if mapping.requires_uses:
                resource_exists = self._resource_exists_in_db(character_id, mapping)
                if not resource_exists:
                    error = (
                        f"[MISSING RESOURCE] {mapping.feature_name} has no resource entry in "
                        f"character_resources for {character_data['name']}"
                    )
                    errors.append(error)
                    print(f"      [FAIL] Resource not in character_resources!")
                    continue
                print(f"      [OK] Resource exists in character_resources")
            else:
                print(f"      [OK] No resource tracking required")

        # Report results
        if errors:
            error_msg = "\n".join(errors)
            print(f"\n[ACTION CARD VALIDATOR] VALIDATION FAILED!")
            print(f"{len(errors)} error(s) found:\n{error_msg}")

            if raise_on_error:
                raise ActionCardValidationError(
                    f"Action card validation failed for {character_data['name']}:\n{error_msg}"
                )
            return False, errors

        print(f"[ACTION CARD VALIDATOR] VALIDATION PASSED - All action cards validated!")
        return True, []

    def _get_expected_features(
        self,
        class_name: str,
        level: int,
        subclass_name: Optional[str] = None
    ) -> List[FeatureActionMapping]:
        """Get all features expected for this class/level/subclass"""
        expected = []

        for mapping in self._feature_mappings.values():
            # Check class match
            if mapping.class_name.lower() != class_name.lower():
                continue

            # Check level requirement
            if level < mapping.min_level:
                continue

            # Check subclass match (if applicable)
            if mapping.subclass_name:
                if not subclass_name or mapping.subclass_name.lower() != subclass_name.lower():
                    continue

            expected.append(mapping)

        return expected

    def _feature_exists_in_db(self, character_id: str, mapping: FeatureActionMapping) -> bool:
        """Check if feature exists in character_features table"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as count
                FROM character_features
                WHERE character_id = ? AND feature_name = ?
            """, (character_id, mapping.feature_name))

            row = cursor.fetchone()
            conn.close()

            return row and row['count'] > 0

        except sqlite3.Error as e:
            print(f"[ACTION CARD VALIDATOR] Database error checking feature: {e}")
            return False

    def _resource_exists_in_db(self, character_id: str, mapping: FeatureActionMapping) -> bool:
        """Check if resource exists in character_resources table"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Map feature name to resource name
            resource_name = mapping.feature_name

            cursor.execute("""
                SELECT COUNT(*) as count, current_uses, max_uses
                FROM character_resources
                WHERE character_id = ? AND resource_name = ?
            """, (character_id, resource_name))

            row = cursor.fetchone()
            conn.close()

            if row and row['count'] > 0:
                print(f"        Resource: {resource_name} {row['current_uses']}/{row['max_uses']}")
                return True

            return False

        except sqlite3.Error as e:
            print(f"[ACTION CARD VALIDATOR] Database error checking resource: {e}")
            return False

    def _get_character_data(self, character_id: str) -> Optional[Dict]:
        """Get character data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, c.name, c.class_id, c.subclass_id, c.level
                FROM characters c
                WHERE c.id = ?
            """, (character_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)

        except sqlite3.Error as e:
            print(f"[ACTION CARD VALIDATOR] Database error: {e}")

        return None

    def get_missing_features_report(self, character_id: str) -> str:
        """Generate a detailed report of missing features"""
        success, errors = self.validate_character_actions(character_id, raise_on_error=False)

        if success:
            return "All action cards validated successfully!"

        report = "=== MISSING ACTION CARDS REPORT ===\n\n"
        report += f"Found {len(errors)} missing feature(s):\n\n"

        for i, error in enumerate(errors, 1):
            report += f"{i}. {error}\n"

        report += "\nThese features require action cards but are not properly configured."
        report += "\nPlease check character creation code and resource initialization."

        return report


def validate_character_on_creation(character_id: str):
    """
    Convenience function to validate character immediately after creation.
    Raises ActionCardValidationError if validation fails.
    """
    validator = ActionCardValidator()
    validator.validate_character_actions(character_id, raise_on_error=True)
