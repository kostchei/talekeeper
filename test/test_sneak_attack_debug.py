#!/usr/bin/env python3
"""
Debug test for Sneak Attack issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from action_cards.action_panel import ActionPanel
from services.advantage_system import AdvantageState

def test_sneak_attack_debug():
    """Debug sneak attack with various advantage states."""

    print("=== Sneak Attack Debug Test ===")

    # Create QApplication if one doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create action panel with rogue character context
    action_panel = ActionPanel()
    action_panel.character_context = {
        'character_id': 'test-rogue',
        'class_id': 'rogue',
        'level': 2,
        'dexterity': 16,
        'proficiency_bonus': 2
    }

    # Mock the class feature check
    def mock_has_class_feature(feature_name):
        return feature_name == 'Sneak Attack'

    action_panel._has_class_feature = mock_has_class_feature

    # Mock weapon properties
    def mock_get_context_weapon_properties(context):
        return ['finesse', 'light']

    action_panel._get_context_weapon_properties = mock_get_context_weapon_properties

    print("\n=== Test 1: String advantage state ===")
    context1 = {
        'weapon': {'name': 'Shortsword', 'weapon_properties': ['finesse', 'light']},
        'has_advantage': False,
        'advantage_state': 'advantage',
        'has_disadvantage': False,
        'ally_within_5ft': False
    }

    result1 = action_panel._can_sneak_attack(context1)
    print(f"Result with string 'advantage': {result1}")

    print("\n=== Test 2: Enum advantage state ===")
    context2 = {
        'weapon': {'name': 'Shortsword', 'weapon_properties': ['finesse', 'light']},
        'has_advantage': False,
        'advantage_state': AdvantageState.ADVANTAGE,
        'has_disadvantage': False,
        'ally_within_5ft': False
    }

    result2 = action_panel._can_sneak_attack(context2)
    print(f"Result with enum AdvantageState.ADVANTAGE: {result2}")

    print("\n=== Test 3: No advantage ===")
    context3 = {
        'weapon': {'name': 'Shortsword', 'weapon_properties': ['finesse', 'light']},
        'has_advantage': False,
        'advantage_state': AdvantageState.NORMAL,
        'has_disadvantage': False,
        'ally_within_5ft': False
    }

    result3 = action_panel._can_sneak_attack(context3)
    print(f"Result with no advantage: {result3}")

    print("\n=== Test 4: Non-finesse weapon ===")
    context4 = {
        'weapon': {'name': 'Longsword', 'weapon_properties': ['versatile']},
        'has_advantage': False,
        'advantage_state': AdvantageState.ADVANTAGE,
        'has_disadvantage': False,
        'ally_within_5ft': False
    }

    # Override weapon properties for this test
    action_panel._get_context_weapon_properties = lambda ctx: ['versatile']

    result4 = action_panel._can_sneak_attack(context4)
    print(f"Result with non-finesse weapon: {result4}")

    print("\n=== Summary ===")
    print(f"String advantage: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Enum advantage: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"No advantage: {'✅ PASS' if not result3 else '❌ FAIL'}")
    print(f"Non-finesse: {'✅ PASS' if not result4 else '❌ FAIL'}")

    if result1 and result2:
        print("\n🎯 Sneak attack logic is working correctly!")
    else:
        print("\n💥 Sneak attack logic has issues!")

    return result1 and result2

if __name__ == "__main__":
    test_sneak_attack_debug()