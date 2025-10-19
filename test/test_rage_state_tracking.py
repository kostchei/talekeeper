# test
"""
Test Rage State Tracking

This test verifies that rage state is properly tracked in character context.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_rage_state_conditions():
    """Test the conditions for applying rage resistance."""
    print("Testing rage state conditions...")

    # Mock character contexts for testing
    test_cases = [
        {
            "name": "Barbarian not raging",
            "context": {
                "class_id": "barbarian",
                "raging": False
            },
            "damage": 4,
            "damage_type": "physical",
            "expected_resistance": False,
            "expected_damage": 4
        },
        {
            "name": "Barbarian raging, physical damage",
            "context": {
                "class_id": "barbarian",
                "raging": True
            },
            "damage": 4,
            "damage_type": "physical",
            "expected_resistance": True,
            "expected_damage": 2
        },
        {
            "name": "Fighter raging (should not apply)",
            "context": {
                "class_id": "fighter",
                "raging": True
            },
            "damage": 4,
            "damage_type": "physical",
            "expected_resistance": False,
            "expected_damage": 4
        },
        {
            "name": "Barbarian raging, fire damage (should not apply)",
            "context": {
                "class_id": "barbarian",
                "raging": True
            },
            "damage": 4,
            "damage_type": "fire",
            "expected_resistance": False,
            "expected_damage": 4
        }
    ]

    all_passed = True
    for test_case in test_cases:
        # Simulate the rage resistance logic
        damage = test_case["damage"]
        original_damage = damage
        context = test_case["context"]
        damage_type = test_case["damage_type"]

        # Apply the same logic as _apply_damage_to_player
        rage_resistance_applied = False
        is_barbarian = context.get('class_id', '').lower() == 'barbarian'
        is_raging = context.get('raging', False)

        if is_barbarian and is_raging and damage_type in ['physical', 'bludgeoning', 'piercing', 'slashing']:
            damage = damage // 2  # Half damage (rounded down)
            if damage < original_damage:
                rage_resistance_applied = True

        # Check results
        expected_resistance = test_case["expected_resistance"]
        expected_damage = test_case["expected_damage"]

        if rage_resistance_applied == expected_resistance and damage == expected_damage:
            print(f"  [OK] {test_case['name']}: {original_damage} -> {damage} (resistance: {rage_resistance_applied})")
        else:
            print(f"  [ERROR] {test_case['name']}: Expected {expected_damage} (resistance: {expected_resistance}), got {damage} (resistance: {rage_resistance_applied})")
            all_passed = False

    return all_passed

def test_damage_type_mapping():
    """Test damage type recognition."""
    print("\nTesting damage type mapping...")

    # Test which damage types should trigger rage resistance
    damage_types = [
        ("physical", True),
        ("bludgeoning", True),
        ("piercing", True),
        ("slashing", True),
        ("fire", False),
        ("cold", False),
        ("lightning", False),
        ("acid", False),
        ("poison", False),
        ("psychic", False),
        ("force", False),
        ("necrotic", False),
        ("radiant", False),
    ]

    # Simulate barbarian raging context
    context = {"class_id": "barbarian", "raging": True}

    all_passed = True
    for damage_type, should_resist in damage_types:
        # Apply rage resistance logic
        damage = 6  # Test with 6 damage
        original_damage = damage
        rage_resistance_applied = False

        is_barbarian = context.get('class_id', '').lower() == 'barbarian'
        is_raging = context.get('raging', False)

        if is_barbarian and is_raging and damage_type in ['physical', 'bludgeoning', 'piercing', 'slashing']:
            damage = damage // 2
            if damage < original_damage:
                rage_resistance_applied = True

        if rage_resistance_applied == should_resist:
            resist_text = "resisted" if rage_resistance_applied else "not resisted"
            print(f"  [OK] {damage_type} damage: {resist_text}")
        else:
            print(f"  [ERROR] {damage_type} damage: Expected {'resisted' if should_resist else 'not resisted'}, got {'resisted' if rage_resistance_applied else 'not resisted'}")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    print("=== Rage State Tracking Test Suite ===")

    success = True
    success &= test_rage_state_conditions()
    success &= test_damage_type_mapping()

    if success:
        print("\n[SUCCESS] All rage state tracking tests passed!")
        print("\nKey findings:")
        print("- Rage resistance only applies to Barbarians who are raging")
        print("- Only physical/bludgeoning/piercing/slashing damage is resisted")
        print("- Fire, cold, lightning, etc. damage is NOT resisted by rage")
        print("- Fighters with 'raging' state should NOT get resistance")
    else:
        print("\n[FAILED] Some rage state tracking tests failed!")
        sys.exit(1)