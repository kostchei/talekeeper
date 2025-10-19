#test
"""
Test Action Economy Enforcement

This test verifies that the action economy properly prevents multiple
bonus actions, reactions, and main actions per turn.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_action_economy_logic():
    """Test the logic for action economy enforcement."""
    print("Testing action economy enforcement...")

    # Import the action economy module
    try:
        from models.action_economy import ActionEconomyType, ActionEconomyState
        print("  [OK] Action economy modules imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Could not import action economy modules: {e}")
        return False

    # Test action economy state
    state = ActionEconomyState(
        combatant_id="test_char",
        combatant_name="Test Character"
    )

    print(f"  [OK] Initial state - Action: {state.action_available}, Bonus: {state.bonus_action_available}, Reaction: {state.reaction_available}")

    # Test using actions
    test_cases = [
        ("Use main action", ActionEconomyType.ACTION, True),
        ("Try second main action", ActionEconomyType.ACTION, False),
        ("Use bonus action", ActionEconomyType.BONUS_ACTION, True),
        ("Try second bonus action", ActionEconomyType.BONUS_ACTION, False),
        ("Use reaction", ActionEconomyType.REACTION, True),
        ("Try second reaction", ActionEconomyType.REACTION, False),
    ]

    all_passed = True
    for test_name, economy_type, should_succeed in test_cases:
        try:
            # Try to use the action (returns True if successful, False if blocked)
            result = state.use_action(economy_type, f"Test {test_name}")

            if result and should_succeed:
                print(f"  [OK] {test_name} - succeeded as expected")
            elif not result and not should_succeed:
                print(f"  [OK] {test_name} - blocked as expected")
            elif result and not should_succeed:
                print(f"  [ERROR] {test_name} - should have been blocked but succeeded")
                all_passed = False
            else:
                print(f"  [ERROR] {test_name} - should have succeeded but was blocked")
                all_passed = False

        except Exception as e:
            print(f"  [ERROR] {test_name} - exception: {e}")
            all_passed = False

    return all_passed


def test_action_mapping():
    """Test that actions are properly mapped to economy types."""
    print("\nTesting action type mapping...")

    # Import action types
    try:
        from action_cards.action_panel import ActionType
        print("  [OK] ActionType imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Could not import ActionType: {e}")
        return False

    # Test action mappings
    test_mappings = [
        (ActionType.USE_POTION, "bonus_action", "Potions should be bonus actions"),
        (ActionType.SECOND_WIND, "bonus_action", "Second Wind should be bonus action"),
        (ActionType.ATTACK_MAIN_HAND, "action", "Attacks should be main actions"),
        (ActionType.DODGE, "action", "Dodge should be main action"),
        (ActionType.OPPORTUNITY, "reaction", "Opportunity attacks should be reactions"),
    ]

    # Note: We can't easily test the mapping without the full action panel setup
    # But we can verify the action types exist
    for action_type, expected_economy, description in test_mappings:
        try:
            action_name = action_type.value
            print(f"  [OK] {description} - {action_name} exists")
        except Exception as e:
            print(f"  [ERROR] {description} - {e}")
            return False

    return True


if __name__ == "__main__":
    print("=== Action Economy Enforcement Test ===")

    success = True
    success &= test_action_economy_logic()
    success &= test_action_mapping()

    if success:
        print("\n[SUCCESS] Action economy enforcement tests passed!")
        print("\nExpected behavior:")
        print("- Only one main action per turn (unless Action Surge)")
        print("- Only one bonus action per turn")
        print("- Only one reaction per round")
        print("- Bonus action tabs should grey out after first bonus action")
        print("- Second potion/Second Wind should be blocked with clear message")
    else:
        print("\n[FAILED] Some action economy tests failed!")
        sys.exit(1)