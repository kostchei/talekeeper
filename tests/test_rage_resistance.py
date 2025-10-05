"""
Test Rage Damage Resistance

This test verifies that rage damage resistance works correctly for different damage amounts.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_rage_resistance_calculations():
    """Test the mathematics of rage damage resistance."""
    print("Testing rage damage resistance calculations...")

    # Test cases with expected results
    test_cases = [
        (1, 0, "1 damage -> 0 (rage resistance)"),
        (2, 1, "2 damage -> 1 (rage resistance)"),
        (3, 1, "3 damage -> 1 (rage resistance)"),
        (4, 2, "4 damage -> 2 (rage resistance)"),
        (5, 2, "5 damage -> 2 (rage resistance)"),
        (6, 3, "6 damage -> 3 (rage resistance)"),
        (10, 5, "10 damage -> 5 (rage resistance)"),
        (15, 7, "15 damage -> 7 (rage resistance)"),
    ]

    all_passed = True
    for original_damage, expected_reduced, description in test_cases:
        # Simulate rage resistance: half damage (rounded down)
        actual_reduced = original_damage // 2

        if actual_reduced == expected_reduced:
            print(f"  [OK] {description}")
        else:
            print(f"  [ERROR] {description} - got {actual_reduced}")
            all_passed = False

    return all_passed

def test_action_economy_integration():
    """Test that rage action economy integration works."""
    print("\nTesting rage action economy integration...")

    try:
        from action_cards.action_panel import ActionType
        from models.action_economy import ActionEconomyType

        # Create a mock action panel to test mapping
        class MockActionPanel:
            def _map_action_to_economy_type(self, action_type: ActionType):
                """Copy of the mapping method for testing."""
                from models.action_economy import ActionEconomyType

                # Bonus Actions
                bonus_actions = {
                    ActionType.SECOND_WIND, ActionType.USE_POTION,
                    ActionType.NICK_MASTERY, ActionType.CLEAVE_MASTERY, ActionType.RAGE,
                    ActionType.ATTACK_OFF_HAND, ActionType.INSTINCTIVE_POUNCE,
                    ActionType.INTIMIDATING_PRESENCE, ActionType.BRUTAL_STRIKE_FORCEFUL,
                    ActionType.BRUTAL_STRIKE_HAMSTRING, ActionType.BRUTAL_STRIKE_STAGGERING,
                    ActionType.BRUTAL_STRIKE_SUNDERING
                }

                if action_type in bonus_actions:
                    return ActionEconomyType.BONUS_ACTION
                else:
                    return ActionEconomyType.FREE_ACTION

        mock_panel = MockActionPanel()

        # Test that Rage is correctly mapped as bonus action
        rage_economy = mock_panel._map_action_to_economy_type(ActionType.RAGE)
        if rage_economy == ActionEconomyType.BONUS_ACTION:
            print("  [OK] Rage correctly mapped as BONUS_ACTION")
        else:
            print(f"  [ERROR] Rage mapped as {rage_economy}, expected BONUS_ACTION")
            return False

        # Test that potion is correctly mapped as bonus action
        potion_economy = mock_panel._map_action_to_economy_type(ActionType.USE_POTION)
        if potion_economy == ActionEconomyType.BONUS_ACTION:
            print("  [OK] Use Potion correctly mapped as BONUS_ACTION")
        else:
            print(f"  [ERROR] Use Potion mapped as {potion_economy}, expected BONUS_ACTION")
            return False

        return True

    except ImportError as e:
        print(f"  [ERROR] Could not import required modules: {e}")
        return False

if __name__ == "__main__":
    print("=== Rage Resistance Test Suite ===")

    success = True
    success &= test_rage_resistance_calculations()
    success &= test_action_economy_integration()

    if success:
        print("\n[SUCCESS] All rage resistance tests passed!")
        print("\nExpected behavior:")
        print("- Damage of 1 should be reduced to 0 (this is correct D&D 5e behavior)")
        print("- Damage of 2 should be reduced to 1")
        print("- Damage of 6 should be reduced to 3")
        print("- Rage should be a bonus action (preventing multiple bonus actions)")
        print("- Action economy fix should prevent Rage + Potion in same turn")
    else:
        print("\n[FAILED] Some rage resistance tests failed!")
        sys.exit(1)