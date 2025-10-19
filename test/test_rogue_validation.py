# test
"""
Simple validation test for Rogue implementation

This test verifies that the Rogue implementation is working correctly
without complex database setup.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_rogue_service_import():
    """Test that the RogueAbilitiesService can be imported."""
    try:
        from services.rogue_abilities import RogueAbilitiesService
        print("PASS: RogueAbilitiesService imported successfully")
        return True
    except ImportError as e:
        print(f"FAIL: Failed to import RogueAbilitiesService: {e}")
        return False

def test_sneak_attack_dice_calculation():
    """Test Sneak Attack dice calculation logic."""
    try:
        from services.rogue_abilities import RogueAbilitiesService
        service = RogueAbilitiesService()

        # Test some key levels
        test_cases = [
            (1, 1), (3, 2), (5, 3), (9, 5), (11, 6), (20, 10)
        ]

        all_correct = True
        for level, expected in test_cases:
            actual = service._calculate_sneak_attack_dice(level)
            if actual == expected:
                print(f"PASS: Level {level}: {actual}d6 Sneak Attack (correct)")
            else:
                print(f"FAIL: Level {level}: Expected {expected}d6, got {actual}d6")
                all_correct = False

        return all_correct
    except Exception as e:
        print(f"FAIL: Error testing Sneak Attack dice: {e}")
        return False

def test_weapon_eligibility():
    """Test weapon eligibility for Sneak Attack."""
    try:
        from services.rogue_abilities import RogueAbilitiesService
        service = RogueAbilitiesService()

        # Test finesse weapon
        finesse_weapon = {'weapon_properties': 'finesse, light'}
        if service._is_sneak_attack_weapon(finesse_weapon):
            print("PASS: Finesse weapon eligible for Sneak Attack")
        else:
            print("FAIL: Finesse weapon should be eligible for Sneak Attack")
            return False

        # Test ranged weapon
        ranged_weapon = {'weapon_type': 'ranged', 'name': 'shortbow'}
        if service._is_sneak_attack_weapon(ranged_weapon):
            print("PASS: Ranged weapon eligible for Sneak Attack")
        else:
            print("FAIL: Ranged weapon should be eligible for Sneak Attack")
            return False

        # Test non-eligible weapon
        heavy_weapon = {'weapon_properties': 'heavy, two-handed', 'weapon_type': 'melee'}
        if not service._is_sneak_attack_weapon(heavy_weapon):
            print("PASS: Heavy weapon correctly not eligible for Sneak Attack")
        else:
            print("FAIL: Heavy weapon should not be eligible for Sneak Attack")
            return False

        return True
    except Exception as e:
        print(f"FAIL: Error testing weapon eligibility: {e}")
        return False

def test_weapon_attack_service_integration():
    """Test that WeaponAttackService includes Sneak Attack integration."""
    try:
        from services.weapon_attack_service import WeaponAttackService
        service = WeaponAttackService("test.db")

        # Check if the method exists
        if hasattr(service, '_apply_sneak_attack_if_eligible'):
            print("PASS: WeaponAttackService has Sneak Attack integration")
            return True
        else:
            print("FAIL: WeaponAttackService missing Sneak Attack integration")
            return False
    except Exception as e:
        print(f"FAIL: Error testing WeaponAttackService: {e}")
        return False

def test_action_types_defined():
    """Test that Rogue action types are defined."""
    try:
        from action_cards.action_panel import ActionType

        rogue_actions = [
            'CUNNING_DASH', 'CUNNING_DISENGAGE', 'CUNNING_HIDE',
            'STEADY_AIM', 'UNCANNY_DODGE', 'STROKE_OF_LUCK',
            'CUNNING_STRIKE_POISON', 'CUNNING_STRIKE_TRIP', 'CUNNING_STRIKE_WITHDRAW'
        ]

        all_defined = True
        for action in rogue_actions:
            if hasattr(ActionType, action):
                print(f"PASS: {action} action type defined")
            else:
                print(f"FAIL: {action} action type missing")
                all_defined = False

        return all_defined
    except Exception as e:
        print(f"FAIL: Error testing action types: {e}")
        return False

def test_feature_definitions():
    """Test that Rogue feature definitions are complete."""
    try:
        from core.feature_definitions import ClassFeatures

        expected_levels = list(range(1, 21))  # Levels 1-20
        defined_levels = list(ClassFeatures.ROGUE_FEATURES.keys())

        missing_levels = set(expected_levels) - set(defined_levels)
        if not missing_levels:
            print("PASS: All Rogue levels (1-20) have feature definitions")
            return True
        else:
            print(f"FAIL: Missing feature definitions for levels: {missing_levels}")
            return False
    except Exception as e:
        print(f"FAIL: Error testing feature definitions: {e}")
        return False

def main():
    """Run all validation tests."""
    print("Running Rogue Implementation Validation Tests")
    print("=" * 50)

    tests = [
        test_rogue_service_import,
        test_sneak_attack_dice_calculation,
        test_weapon_eligibility,
        test_weapon_attack_service_integration,
        test_action_types_defined,
        test_feature_definitions
    ]

    passed = 0
    total = len(tests)

    for i, test in enumerate(tests, 1):
        print(f"\n[{i}/{total}] {test.__name__}")
        if test():
            passed += 1
        else:
            print("   Test failed!")

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! Rogue implementation is ready.")
        return True
    else:
        print("Some tests failed. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)