# test
"""
Test Action Validation Layer

Tests the validation system to ensure it provides warnings without blocking actions.
Stage 3.3: Safety layer testing.
"""

import sys
sys.path.append('..')

import tempfile
import sqlite3
import os
from models.action_economy import ActionEconomyState
from services.action_validation import ActionValidator, can_use_class_action, get_action_feedback


class TestActionValidation:
    """Test action validation system"""

    def setup_method(self):
        """Setup test database and validator"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize database schema
        self._setup_test_database()

        # Create validator
        self.validator = ActionValidator(self.db_path)

    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _setup_test_database(self):
        """Setup minimal database schema for testing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Characters table
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    level INTEGER DEFAULT 1
                )
            """)

            # Character subclasses table
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT,
                    class_id TEXT,
                    subclass_id TEXT,
                    PRIMARY KEY (character_id, class_id)
                )
            """)

            # Barbarian features table
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER,
                    rage_uses_current INTEGER DEFAULT 2,
                    rage_uses_max INTEGER DEFAULT 2,
                    brutal_strike_uses_current INTEGER DEFAULT 0,
                    brutal_strike_uses_max INTEGER DEFAULT 0,
                    intimidating_presence_uses_current INTEGER DEFAULT 0,
                    intimidating_presence_uses_max INTEGER DEFAULT 0,
                    is_raging BOOLEAN DEFAULT FALSE,
                    reckless_attack_available BOOLEAN DEFAULT FALSE
                )
            """)

            # Combat state table
            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    reckless_attack_active BOOLEAN DEFAULT FALSE,
                    raging BOOLEAN DEFAULT FALSE
                )
            """)

            conn.commit()

    def _create_test_character(self, character_id="test_char", class_name="barbarian",
                              level=1, subclass="berserker", rage_uses=2):
        """Create a test character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert character
            cursor.execute("""
                INSERT INTO characters (id, name, class_id, level)
                VALUES (?, ?, ?, ?)
            """, (character_id, f"Test {class_name.title()}", class_name, level))

            # Insert subclass if specified
            if subclass:
                cursor.execute("""
                    INSERT INTO character_subclasses (character_id, class_id, subclass_id)
                    VALUES (?, ?, ?)
                """, (character_id, class_name, subclass))

            # Insert class features
            if class_name == "barbarian":
                cursor.execute("""
                    INSERT INTO barbarian_features (
                        character_id, level, rage_uses_current, rage_uses_max,
                        brutal_strike_uses_current, brutal_strike_uses_max,
                        intimidating_presence_uses_current, intimidating_presence_uses_max,
                        reckless_attack_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id, level, rage_uses, rage_uses,  # rage
                    1 if level >= 9 else 0, 1 if level >= 9 else 0,  # brutal strike
                    1 if level >= 14 else 0, 1 if level >= 14 else 0,  # intimidating presence
                    level >= 2  # reckless attack
                ))

            conn.commit()

    def test_valid_action_validation(self):
        """Test validation of valid actions"""
        # Create level 1 barbarian
        self._create_test_character("valid_char", "barbarian", level=1)

        # Test rage (should be valid)
        result = self.validator.can_use_class_action("valid_char", "barbarian_rage")

        assert result.can_use, f"Rage should be usable: {result.reason}"
        assert result.action_id == "barbarian_rage"
        assert len(result.prerequisites_failed) == 0
        assert len(result.resources_insufficient) == 0

    def test_level_prerequisite_failure(self):
        """Test validation fails appropriately for level requirements"""
        # Create level 1 barbarian
        self._create_test_character("low_level", "barbarian", level=1)

        # Test reckless attack (requires level 2)
        result = self.validator.can_use_class_action("low_level", "barbarian_reckless_attack")

        assert not result.can_use, "Reckless attack should not be usable at level 1"
        assert len(result.prerequisites_failed) > 0

        # Check specific failure
        level_failure = next((f for f in result.prerequisites_failed if f["type"] == "level"), None)
        assert level_failure is not None
        assert level_failure["expected"] == 2
        assert level_failure["actual"] == 1

    def test_resource_shortage_detection(self):
        """Test validation detects resource shortages"""
        # Create character with no rage uses
        self._create_test_character("depleted_char", "barbarian", level=5, rage_uses=0)

        # Test rage (should fail due to no uses)
        result = self.validator.can_use_class_action("depleted_char", "barbarian_rage")

        assert not result.can_use, "Rage should not be usable with no uses"
        assert len(result.resources_insufficient) > 0

        # Check specific shortage
        rage_shortage = next((r for r in result.resources_insufficient if r["resource"] == "rage_uses"), None)
        assert rage_shortage is not None
        assert rage_shortage["needed"] == 1
        assert rage_shortage["available"] == 0

    def test_action_economy_blocking(self):
        """Test validation respects action economy"""
        # Create character
        self._create_test_character("economy_test", "barbarian", level=5)

        # Create combat state with action already used
        combat_state = ActionEconomyState(
            combatant_id="economy_test",
            combatant_name="Test",
            action_available=False,  # Action already used
            bonus_action_available=True
        )

        # Test an action that requires an Action
        # Note: Rage uses bonus action, so this should still work
        result = self.validator.can_use_class_action("economy_test", "barbarian_rage", combat_state)
        assert result.can_use, "Rage should work as it uses bonus action"

        # Test with bonus action also used
        combat_state.bonus_action_available = False
        result = self.validator.can_use_class_action("economy_test", "barbarian_rage", combat_state)
        assert not result.can_use, "Rage should not work with bonus action used"
        assert len(result.economy_blocked) > 0

    def test_action_availability_calculator(self):
        """Test getting availability for all character actions"""
        # Create high-level berserker
        self._create_test_character("full_berserker", "barbarian", level=20, subclass="berserker")

        # Get all action availability
        availability = self.validator.get_action_availability("full_berserker")

        # Should have multiple actions
        assert len(availability) > 0, "Should have multiple actions available"

        # Check specific actions
        assert "barbarian_rage" in availability
        assert "barbarian_reckless_attack" in availability
        assert "berserker_intimidating_presence" in availability

        # Most should be available for a level 20 character
        available_count = sum(1 for result in availability.values() if result.can_use)
        assert available_count > 0, "Should have some available actions"

    def test_detailed_feedback_system(self):
        """Test the feedback system provides user-friendly messages"""
        # Create low-level character
        self._create_test_character("feedback_test", "barbarian", level=1, rage_uses=0)

        # Test feedback for unavailable action
        can_use, reason, warnings = self.validator.validate_action_with_feedback(
            "feedback_test", "barbarian_reckless_attack"
        )

        assert not can_use
        assert "level" in reason.lower() or "requires" in reason.lower()
        assert len(warnings) > 0

        # Check warning format
        level_warning = next((w for w in warnings if "level" in w.lower()), None)
        assert level_warning is not None

    def test_warning_logs_without_blocking(self):
        """Test that warnings are logged but actions aren't blocked"""
        # Create character with some limitations
        self._create_test_character("warning_test", "barbarian", level=1)

        # Get availability (should generate warnings but not crash)
        availability = self.validator.get_action_availability("warning_test")

        # Should still return results even with warnings
        assert len(availability) > 0

        # Some actions should be unavailable due to level
        unavailable_actions = [aid for aid, result in availability.items() if not result.can_use]
        assert len(unavailable_actions) > 0, "Should have some unavailable actions"

    def test_user_friendly_messages(self):
        """Test that error messages are user-friendly"""
        # Create character with various limitations
        self._create_test_character("message_test", "barbarian", level=1, rage_uses=0)

        # Test level requirement
        result = self.validator.can_use_class_action("message_test", "barbarian_reckless_attack")
        message = result.get_user_friendly_message()
        assert "level" in message.lower()
        assert "2" in message  # Should mention level 2

        # Test resource shortage
        result = self.validator.can_use_class_action("message_test", "barbarian_rage")
        message = result.get_user_friendly_message()
        assert "rage" in message.lower() or "remaining" in message.lower()


def test_action_validation():
    """Main test function as specified in roadmap"""

    # Test basic validation
    from services.action_validation import ActionValidator
    validator = ActionValidator(":memory:")

    # Create mock combat state
    combat_state = ActionEconomyState(
        combatant_id="test",
        combatant_name="Test Character",
        action_available=True,
        bonus_action_available=False  # Bonus action used
    )

    # Test global functions
    result = can_use_class_action("nonexistent", "barbarian_rage", combat_state)
    assert not result.can_use, "Should fail for nonexistent character"

    can_use, reason, warnings = get_action_feedback("nonexistent", "barbarian_rage", combat_state)
    assert not can_use, "Should provide feedback for nonexistent character"
    assert len(reason) > 0, "Should provide reason"

    print("Action validation layer test passed!")


if __name__ == "__main__":
    test_action_validation()