#test
"""
Validate ActionType References

This script checks that all ActionType references in the code actually exist.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def validate_action_types():
    """Validate that all ActionType references exist in the enum."""
    print("Validating ActionType references...")

    # Import the ActionType enum
    try:
        from action_cards.action_panel import ActionType
        print("  [OK] ActionType imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Could not import ActionType: {e}")
        return False

    # Get all ActionType values
    valid_action_types = set(action_type.name for action_type in ActionType)
    print(f"  [OK] Found {len(valid_action_types)} valid ActionTypes")

    # List ActionTypes referenced in the action economy mapping
    referenced_types = [
        # Main actions
        'ATTACK_MAIN_HAND', 'CAST_SPELL', 'DASH', 'DODGE', 'HIDE', 'SEARCH', 'USE_ITEM', 'SIGNATURE_MOVE',
        # Bonus actions
        'SECOND_WIND', 'USE_POTION', 'NICK_MASTERY', 'CLEAVE_MASTERY', 'RAGE', 'ATTACK_OFF_HAND',
        'INSTINCTIVE_POUNCE', 'INTIMIDATING_PRESENCE', 'BRUTAL_STRIKE_FORCEFUL', 'BRUTAL_STRIKE_HAMSTRING',
        'BRUTAL_STRIKE_STAGGERING', 'BRUTAL_STRIKE_SUNDERING',
        # Reactions
        'OPPORTUNITY', 'RETALIATION'
    ]

    all_valid = True
    for action_type_name in referenced_types:
        if action_type_name in valid_action_types:
            print(f"  [OK] {action_type_name} exists")
        else:
            print(f"  [ERROR] {action_type_name} does not exist in ActionType enum")
            all_valid = False

    # Show available ActionTypes for reference
    print(f"\n  Available ActionTypes: {sorted(valid_action_types)}")

    return all_valid


def test_action_economy_mapping():
    """Test that action economy mapping works without errors."""
    print("\nTesting action economy mapping...")

    try:
        from action_cards.action_panel import ActionPanel, ActionType
        from models.action_economy import ActionEconomyType

        # Create a mock action panel to test the mapping
        class MockActionPanel:
            def _map_action_to_economy_type(self, action_type: ActionType):
                """Copy of the mapping method for testing."""
                from models.action_economy import ActionEconomyType

                main_actions = {
                    ActionType.ATTACK_MAIN_HAND,
                    ActionType.CAST_SPELL, ActionType.DASH, ActionType.DODGE,
                    ActionType.HIDE, ActionType.SEARCH, ActionType.USE_ITEM,
                    ActionType.SIGNATURE_MOVE
                }

                bonus_actions = {
                    ActionType.SECOND_WIND, ActionType.USE_POTION,
                    ActionType.NICK_MASTERY, ActionType.CLEAVE_MASTERY, ActionType.RAGE,
                    ActionType.ATTACK_OFF_HAND, ActionType.INSTINCTIVE_POUNCE,
                    ActionType.INTIMIDATING_PRESENCE, ActionType.BRUTAL_STRIKE_FORCEFUL,
                    ActionType.BRUTAL_STRIKE_HAMSTRING, ActionType.BRUTAL_STRIKE_STAGGERING,
                    ActionType.BRUTAL_STRIKE_SUNDERING
                }

                reactions = {
                    ActionType.OPPORTUNITY, ActionType.RETALIATION
                }

                if action_type in main_actions:
                    return ActionEconomyType.ACTION
                elif action_type in bonus_actions:
                    return ActionEconomyType.BONUS_ACTION
                elif action_type in reactions:
                    return ActionEconomyType.REACTION
                else:
                    return ActionEconomyType.FREE_ACTION

        mock_panel = MockActionPanel()

        # Test mapping some key actions
        test_cases = [
            (ActionType.ATTACK_MAIN_HAND, ActionEconomyType.ACTION),
            (ActionType.RAGE, ActionEconomyType.BONUS_ACTION),
            (ActionType.OPPORTUNITY, ActionEconomyType.REACTION),
            (ActionType.INTERACT, ActionEconomyType.FREE_ACTION),  # Should default to free
        ]

        all_passed = True
        for action_type, expected_economy in test_cases:
            try:
                result = mock_panel._map_action_to_economy_type(action_type)
                if result == expected_economy:
                    print(f"  [OK] {action_type.name} -> {result.name}")
                else:
                    print(f"  [ERROR] {action_type.name} -> {result.name} (expected {expected_economy.name})")
                    all_passed = False
            except Exception as e:
                print(f"  [ERROR] {action_type.name} -> Exception: {e}")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"  [ERROR] Could not test action economy mapping: {e}")
        return False


if __name__ == "__main__":
    print("=== ActionType Validation ===")

    success = True
    success &= validate_action_types()
    success &= test_action_economy_mapping()

    if success:
        print("\n[SUCCESS] All ActionType references are valid!")
        print("The action economy system should work without AttributeError crashes.")
    else:
        print("\n[FAILED] Some ActionType validation failed!")
        sys.exit(1)