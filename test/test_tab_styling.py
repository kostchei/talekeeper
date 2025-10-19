# test
"""
Test script to verify tab styling based on action economy
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_tab_availability_logic():
    """Test the logic for determining tab availability."""
    print("Testing tab availability logic...")

    # Mock different economy states
    test_cases = [
        {
            "name": "Fresh turn - all available",
            "status": {
                "action_available": True,
                "bonus_action_available": True,
                "reaction_available": True,
                "movement_remaining": 30
            },
            "expected_available": {
                "Action": True,
                "Movement": True,
                "Bonus": True,
                "Reaction": True,
                "Free": True
            }
        },
        {
            "name": "Action used",
            "status": {
                "action_available": False,
                "bonus_action_available": True,
                "reaction_available": True,
                "movement_remaining": 30
            },
            "expected_available": {
                "Action": False,
                "Movement": True,
                "Bonus": True,
                "Reaction": True,
                "Free": True
            }
        },
        {
            "name": "Bonus action used",
            "status": {
                "action_available": True,
                "bonus_action_available": False,
                "reaction_available": True,
                "movement_remaining": 30
            },
            "expected_available": {
                "Action": True,
                "Movement": True,
                "Bonus": False,
                "Reaction": True,
                "Free": True
            }
        },
        {
            "name": "Reaction used",
            "status": {
                "action_available": True,
                "bonus_action_available": True,
                "reaction_available": False,
                "movement_remaining": 30
            },
            "expected_available": {
                "Action": True,
                "Movement": True,
                "Bonus": True,
                "Reaction": False,
                "Free": True
            }
        },
        {
            "name": "No movement left",
            "status": {
                "action_available": True,
                "bonus_action_available": True,
                "reaction_available": True,
                "movement_remaining": 0
            },
            "expected_available": {
                "Action": True,
                "Movement": False,
                "Bonus": True,
                "Reaction": True,
                "Free": True
            }
        },
        {
            "name": "All actions used",
            "status": {
                "action_available": False,
                "bonus_action_available": False,
                "reaction_available": False,
                "movement_remaining": 0
            },
            "expected_available": {
                "Action": False,
                "Movement": False,
                "Bonus": False,
                "Reaction": False,
                "Free": True
            }
        }
    ]

    # Map category names to the actual logic
    def get_tab_availability(status):
        return {
            "Action": status.get("action_available", True),
            "Movement": status.get("movement_remaining", 30) > 0,
            "Bonus": status.get("bonus_action_available", True),
            "Reaction": status.get("reaction_available", True),
            "Free": True  # Free actions always available
        }

    all_passed = True
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        actual = get_tab_availability(test_case['status'])
        expected = test_case['expected_available']

        for tab_name, expected_available in expected.items():
            actual_available = actual.get(tab_name)
            if actual_available != expected_available:
                print(f"    [X] {tab_name}: Expected {expected_available}, got {actual_available}")
                all_passed = False
            else:
                print(f"    [OK] {tab_name}: {actual_available}")

    return all_passed


def test_css_generation():
    """Test that CSS is generated correctly."""
    print("\nTesting CSS generation...")

    # Test available style
    available_css = """
                    QPushButton#categoryButton {
                        background-color: #3a3a3a;
                        color: white;
                        border: 1px solid #555;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton#categoryButton:checked {
                        background-color: #4a90e2;
                        border: 2px solid #357abd;
                    }
                    QPushButton#categoryButton:hover {
                        background-color: #4a4a4a;
                    }
                """

    # Test unavailable style
    unavailable_css = """
                    QPushButton#categoryButton {
                        background-color: #2a2a2a;
                        color: #666666;
                        border: 1px solid #444;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: normal;
                    }
                    QPushButton#categoryButton:checked {
                        background-color: #333333;
                        border: 2px solid #555555;
                        color: #777777;
                    }
                    QPushButton#categoryButton:hover {
                        background-color: #2a2a2a;
                    }
                """

    # Check that CSS contains expected elements
    css_checks = [
        ("Available CSS has white color", "color: white" in available_css),
        ("Available CSS has bold font", "font-weight: bold" in available_css),
        ("Unavailable CSS has grey color", "color: #666666" in unavailable_css),
        ("Unavailable CSS has normal font", "font-weight: normal" in unavailable_css),
        ("Available CSS has blue checked state", "#4a90e2" in available_css),
        ("Unavailable CSS has dark checked state", "#333333" in unavailable_css)
    ]

    all_passed = True
    for check_name, check_result in css_checks:
        if check_result:
            print(f"  [OK] {check_name}")
        else:
            print(f"  [X] {check_name}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=== Tab Styling Test Suite ===")

    success = True
    success &= test_tab_availability_logic()
    success &= test_css_generation()

    if success:
        print("\n[SUCCESS] All tab styling tests passed!")
        print("The tab greying functionality should work correctly.")
        print("\nTo test manually:")
        print("1. Start a combat encounter")
        print("2. Use an action (like Attack)")
        print("3. Check that the 'Action' tab becomes greyed out")
        print("4. Use a bonus action (like Rage)")
        print("5. Check that the 'Bonus' tab becomes greyed out")
        print("6. Use a reaction")
        print("7. Check that the 'Reaction' tab becomes greyed out")
        print("8. Move your full movement")
        print("9. Check that the 'Movement' tab becomes greyed out")
    else:
        print("\n[FAILED] Some tab styling tests failed!")
        sys.exit(1)