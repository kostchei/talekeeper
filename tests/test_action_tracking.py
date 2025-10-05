"""
Test Action Tracking Enhancement

Verifies that the enhanced action economy tracking works alongside existing combat
without breaking the original combat flow.
"""

import pytest
import tempfile
import os
import sys
sys.path.append('..')

from models.action_economy import ActionEconomyState, CombatActionEconomy, ActionEconomyType


class TestActionTracking:
    """Test enhanced action economy tracking"""

    def setup_method(self):
        """Setup test action economy"""
        self.combat = CombatActionEconomy(combat_session_id="test_combat")

        # Add test combatants
        self.combat.add_combatant(
            "player1", "Test Barbarian", "character",
            movement_speed=30, has_action_surge=False
        )
        self.combat.add_combatant(
            "monster1", "Test Orc", "monster",
            movement_speed=30, has_action_surge=False
        )

    def test_class_action_tracking(self):
        """Test tracking of class-specific actions"""
        # Start combat
        self.combat.start_combat(["player1", "monster1"])

        # Track a Rage action
        success = self.combat.track_class_action(
            "player1",
            "barbarian_rage",
            "Rage",
            resource_cost={"rage_uses": 1},
            effect_duration={"type": "rounds", "value": 10, "data": {"damage_bonus": 2}}
        )

        assert success, "Should track rage action successfully"

        # Check resource usage
        rage_usage = self.combat.get_combatant_resource_usage("player1", "rage_uses")
        assert rage_usage == 1, f"Expected 1 rage use, got {rage_usage}"

        # Check action count
        rage_count = self.combat.get_combatant_action_count("player1", "barbarian_rage")
        assert rage_count == 1, f"Expected 1 rage use count, got {rage_count}"

        # Check active effects
        effects = self.combat.get_combatant_active_effects("player1")
        assert len(effects) == 1, f"Expected 1 active effect, got {len(effects)}"

        rage_effect = list(effects.values())[0]
        assert rage_effect["action_id"] == "barbarian_rage"
        assert rage_effect["duration_type"] == "rounds"
        assert rage_effect["duration_value"] == 10

    def test_resource_consumption_tracking(self):
        """Test resource consumption tracking across multiple actions"""
        self.combat.start_combat(["player1", "monster1"])

        # Use multiple rage actions (if somehow possible)
        self.combat.track_class_action("player1", "barbarian_rage", "Rage", {"rage_uses": 1})
        self.combat.track_class_action("player1", "barbarian_rage", "Rage", {"rage_uses": 1})

        # Use another resource
        self.combat.track_class_action(
            "player1", "barbarian_brutal_strike", "Brutal Strike",
            {"brutal_strike_uses": 1}
        )

        # Check cumulative resource usage
        rage_usage = self.combat.get_combatant_resource_usage("player1", "rage_uses")
        brutal_usage = self.combat.get_combatant_resource_usage("player1", "brutal_strike_uses")

        assert rage_usage == 2, f"Expected 2 rage uses, got {rage_usage}"
        assert brutal_usage == 1, f"Expected 1 brutal strike use, got {brutal_usage}"

    def test_duration_management(self):
        """Test effect duration tracking and expiration"""
        self.combat.start_combat(["player1", "monster1"])

        # Add effect that lasts 2 rounds
        self.combat.track_class_action(
            "player1", "test_effect", "Test Effect",
            effect_duration={"type": "rounds", "value": 2}
        )

        # Should have 1 active effect
        effects = self.combat.get_combatant_active_effects("player1")
        assert len(effects) == 1

        # Advance 1 round - effect should still be active
        self.combat.next_turn()  # monster turn
        self.combat.next_turn()  # back to player, round 2

        effects = self.combat.get_combatant_active_effects("player1")
        assert len(effects) == 1, "Effect should still be active after 1 round"

        # Advance another round - effect should expire
        self.combat.next_turn()  # monster turn
        self.combat.next_turn()  # back to player, round 3

        effects = self.combat.get_combatant_active_effects("player1")
        assert len(effects) == 0, "Effect should have expired after 2 rounds"

    def test_action_logging(self):
        """Test that actions are properly logged"""
        self.combat.start_combat(["player1", "monster1"])

        # Get initial state
        state = self.combat.get_combatant_state("player1")
        initial_action_count = len(state.actions_taken_this_turn)

        # Track a class action
        self.combat.track_class_action("player1", "barbarian_rage", "Rage")

        # Check that action was logged
        state = self.combat.get_combatant_state("player1")
        new_action_count = len(state.actions_taken_this_turn)

        assert new_action_count == initial_action_count + 1, "Action should be logged"

        # Check the logged action details
        last_action = state.actions_taken_this_turn[-1]
        assert last_action["type"] == "class_action"
        assert last_action["action_id"] == "barbarian_rage"
        assert last_action["name"] == "Rage"

    def test_existing_economy_still_works(self):
        """Test that existing action economy functionality is preserved"""
        self.combat.start_combat(["player1", "monster1"])

        # Test basic action economy still works
        state = self.combat.get_combatant_state("player1")
        assert state.action_available, "Action should be available at start of turn"
        assert state.bonus_action_available, "Bonus action should be available"
        assert state.reaction_available, "Reaction should be available"

        # Use basic action
        success = self.combat.use_action("player1", ActionEconomyType.ACTION, "Attack")
        assert success, "Should be able to use basic action"

        state = self.combat.get_combatant_state("player1")
        assert not state.action_available, "Action should be consumed"

        # Try to use another action - should fail
        success = self.combat.use_action("player1", ActionEconomyType.ACTION, "Attack")
        assert not success, "Should not be able to use second action"

    def test_parallel_tracking(self):
        """Test that class action tracking works alongside basic action economy"""
        self.combat.start_combat(["player1", "monster1"])

        # Use basic action
        self.combat.use_action("player1", ActionEconomyType.ACTION, "Attack")

        # Track class action - should not interfere
        success = self.combat.track_class_action("player1", "barbarian_rage", "Rage")
        assert success, "Class action tracking should work alongside basic actions"

        # Use bonus action
        success = self.combat.use_action("player1", ActionEconomyType.BONUS_ACTION, "Rage")
        assert success, "Should still be able to use bonus action"

        # Check that both tracking systems recorded actions
        state = self.combat.get_combatant_state("player1")
        assert len(state.actions_taken_this_turn) >= 2, "Should have multiple actions logged"
        assert state.get_action_usage_count("barbarian_rage") == 1, "Class action should be tracked"


def test_action_tracking():
    """Main test function as specified in roadmap"""

    # Test basic action economy enhancement
    state = ActionEconomyState(combatant_id="test", combatant_name="Test")

    # Test class action tracking
    success = state.track_class_action(
        "barbarian_rage", "Rage",
        resource_cost={"rage_uses": 1},
        effect_duration={"type": "rounds", "value": 10}
    )
    assert success, "Class action tracking should work"

    # Test resource tracking
    usage = state.get_resource_usage("rage_uses")
    assert usage == 1, f"Expected 1 rage use, got {usage}"

    # Test effect tracking
    effects = state.get_active_effects()
    assert len(effects) == 1, f"Expected 1 active effect, got {len(effects)}"

    print("✅ Action tracking enhancement test passed!")


if __name__ == "__main__":
    test_action_tracking()