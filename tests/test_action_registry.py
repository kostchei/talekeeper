#test
"""
Test Action Registry System

Tests the action registry in isolation without modifying combat flow.
"""

import pytest
import sqlite3
import os
import tempfile
from services.action_registry import (
    ActionRegistry, ClassActionDefinition, ActionEconomyType,
    ActionTrigger, ActionPrerequisite, ActionResource, PrerequisiteType
)


class TestActionRegistry:
    """Test the action registry system"""

    def setup_method(self):
        """Setup test database and registry"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize database schema
        self._setup_test_database()

        # Create registry
        self.registry = ActionRegistry(self.db_path)

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
                              level=1, subclass="berserker"):
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
                    character_id, level, 2, 2,  # rage
                    1 if level >= 9 else 0, 1 if level >= 9 else 0,  # brutal strike
                    1 if level >= 14 else 0, 1 if level >= 14 else 0,  # intimidating presence
                    level >= 2  # reckless attack
                ))

            conn.commit()

    def test_action_registration(self):
        """Test registering and retrieving actions"""
        # Test basic action registration
        test_action = ClassActionDefinition(
            id="test_action",
            name="Test Action",
            description="A test action",
            class_name="barbarian",
            economy_type=ActionEconomyType.ACTION
        )

        self.registry.register_action(test_action)
        retrieved = self.registry.get_action("test_action")

        assert retrieved is not None
        assert retrieved.id == "test_action"
        assert retrieved.name == "Test Action"
        assert retrieved.class_name == "barbarian"

    def test_barbarian_actions_registered(self):
        """Test that all barbarian actions are registered"""
        expected_actions = [
            "barbarian_rage",
            "barbarian_reckless_attack",
            "barbarian_brutal_strike",
            "berserker_frenzy",
            "berserker_mindless_rage",
            "berserker_retaliation",
            "berserker_intimidating_presence"
        ]

        for action_id in expected_actions:
            action = self.registry.get_action(action_id)
            assert action is not None, f"Action {action_id} not registered"
            assert action.class_name == "barbarian"

    def test_class_actions_by_level(self):
        """Test getting class actions filtered by level"""
        barbarian_actions = self.registry.get_class_actions("barbarian", level=1)

        # Should include rage but not level 2+ actions
        action_names = [action.name for action in barbarian_actions]
        assert "Rage" in action_names
        assert "Reckless Attack" not in action_names

        # Test level 2
        barbarian_actions_l2 = self.registry.get_class_actions("barbarian", level=2)
        action_names_l2 = [action.name for action in barbarian_actions_l2]
        assert "Rage" in action_names_l2
        assert "Reckless Attack" in action_names_l2

    def test_subclass_actions(self):
        """Test getting subclass-specific actions"""
        berserker_actions = self.registry.get_subclass_actions("barbarian", "berserker", level=20)

        action_names = [action.name for action in berserker_actions]
        expected_berserker = ["Frenzy", "Mindless Rage", "Retaliation", "Intimidating Presence"]

        for expected in expected_berserker:
            assert expected in action_names, f"{expected} not found in berserker actions"

    def test_character_actions(self):
        """Test getting actions for a specific character"""
        # Create test character
        self._create_test_character("test_barbarian", "barbarian", level=5, subclass="berserker")

        # Get character actions
        actions = self.registry.get_character_actions("test_barbarian")
        action_names = [action.name for action in actions]

        # Should include appropriate level actions
        assert "Rage" in action_names
        assert "Reckless Attack" in action_names
        assert "Frenzy" in action_names
        assert "Brutal Strike" not in action_names  # Level 9+
        assert "Intimidating Presence" not in action_names  # Level 14+

    def test_prerequisite_validation(self):
        """Test prerequisite validation system"""
        # Create level 1 character
        self._create_test_character("low_level", "barbarian", level=1)

        # Test level prerequisite
        rage_action = self.registry.get_action("barbarian_rage")
        assert self.registry.validate_prerequisites(rage_action, "low_level")

        reckless_action = self.registry.get_action("barbarian_reckless_attack")
        assert not self.registry.validate_prerequisites(reckless_action, "low_level")

        # Create level 2 character
        self._create_test_character("mid_level", "barbarian", level=2)
        assert self.registry.validate_prerequisites(reckless_action, "mid_level")

    def test_resource_checking(self):
        """Test resource availability checking"""
        # Create character with resources
        self._create_test_character("resource_test", "barbarian", level=5)

        # Test rage availability
        rage_action = self.registry.get_action("barbarian_rage")
        can_use = self.registry.can_use_action("barbarian_rage", "resource_test")
        assert can_use["can_use"]

        # Deplete rage uses
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE barbarian_features
                SET rage_uses_current = 0
                WHERE character_id = ?
            """, ("resource_test",))
            conn.commit()

        can_use_depleted = self.registry.can_use_action("barbarian_rage", "resource_test")
        assert not can_use_depleted["can_use"]
        assert "rage_uses" in can_use_depleted["reason"]

    def test_combat_state_prerequisites(self):
        """Test combat state prerequisite checking"""
        # Create high-level berserker
        self._create_test_character("combat_test", "barbarian", level=10, subclass="berserker")

        # Test mindless rage (requires raging)
        mindless_rage = self.registry.get_action("berserker_mindless_rage")

        # Should fail when not raging
        assert not self.registry.validate_prerequisites(mindless_rage, "combat_test")

        # Set raging state
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE barbarian_features
                SET is_raging = TRUE
                WHERE character_id = ?
            """, ("combat_test",))
            conn.commit()

        # Should pass when raging
        assert self.registry.validate_prerequisites(mindless_rage, "combat_test")

    def test_action_definition_completeness(self):
        """Test that action definitions have required fields"""
        rage_action = self.registry.get_action("barbarian_rage")

        # Test required fields
        assert rage_action.id
        assert rage_action.name
        assert rage_action.description
        assert rage_action.economy_type
        assert rage_action.handler_function
        assert rage_action.handler_module

        # Test prerequisites
        assert len(rage_action.prerequisites) > 0
        level_prereq = next((p for p in rage_action.prerequisites
                           if p.type == PrerequisiteType.LEVEL), None)
        assert level_prereq is not None
        assert level_prereq.value == 1

        # Test resources
        assert len(rage_action.resources_consumed) > 0
        rage_resource = rage_action.resources_consumed[0]
        assert rage_resource.name == "rage_uses"
        assert rage_resource.amount == 1

    def test_economy_type_mapping(self):
        """Test that actions have correct economy types"""
        economy_tests = [
            ("barbarian_rage", ActionEconomyType.BONUS_ACTION),
            ("barbarian_reckless_attack", ActionEconomyType.FREE_ACTION),
            ("berserker_retaliation", ActionEconomyType.REACTION),
            ("berserker_intimidating_presence", ActionEconomyType.BONUS_ACTION)
        ]

        for action_id, expected_economy in economy_tests:
            action = self.registry.get_action(action_id)
            assert action.economy_type == expected_economy, \
                f"{action_id} has wrong economy type: {action.economy_type} vs {expected_economy}"

    def test_trigger_types(self):
        """Test that automatic triggers are properly set"""
        # Frenzy should be automatic
        frenzy = self.registry.get_action("berserker_frenzy")
        assert frenzy.trigger == ActionTrigger.AUTOMATIC

        # Mindless Rage should be automatic
        mindless_rage = self.registry.get_action("berserker_mindless_rage")
        assert mindless_rage.trigger == ActionTrigger.AUTOMATIC

        # Retaliation should be reaction
        retaliation = self.registry.get_action("berserker_retaliation")
        assert retaliation.trigger == ActionTrigger.REACTION

        # Rage should be manual
        rage = self.registry.get_action("barbarian_rage")
        assert rage.trigger == ActionTrigger.MANUAL


def test_action_registry():
    """Test registry in isolation as specified in roadmap"""
    # This is the specific test mentioned in the implementation roadmap
    registry = ActionRegistry(":memory:")  # Use in-memory database

    # Register Barbarian actions - already done in __init__
    barbarian_actions = registry.get_class_actions("barbarian", level=20)
    assert len(barbarian_actions) > 0

    # Validate action definitions
    for action in barbarian_actions:
        assert action.id
        assert action.name
        assert action.description
        assert action.class_name == "barbarian"

    # Test prerequisite checking
    rage_action = registry.get_action("barbarian_rage")
    assert rage_action is not None
    assert len(rage_action.prerequisites) > 0

    print("✅ Action registry test passed!")


if __name__ == "__main__":
    test_action_registry()