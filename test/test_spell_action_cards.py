#!/usr/bin/env python3
"""
Test Spell Action Cards Implementation

Verifies that spell action cards are created and work correctly.
"""

import sys
import os
import sqlite3
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from action_cards.action_panel import ActionPanel, ActionType
from services.spellcasting_service import SpellcastingService

def test_spell_action_cards_creation():
    """Test that spell action cards are created for spellcasting characters."""
    print("Testing spell action cards creation...")

    # Create a mock character with spells
    mock_character = {
        'id': 'test-wizard-123',
        'name': 'Test Wizard',
        'class_id': 'wizard',
        'level': 1
    }

    # Create action panel
    action_panel = ActionPanel()
    action_panel.character_context = mock_character

    # Mock the database to return some test spells
    test_spells = [
        {
            'spell_id': 'fire_bolt',
            'spell_level': 0,
            'is_prepared': 1,
            'always_prepared': 1,
            'name': 'Fire Bolt',
            'school': 'evocation',
            'casting_time': '1 action',
            'range_value': '120 feet',
            'components': 'V, S',
            'duration': 'Instantaneous',
            'concentration': 0,
            'description': 'You hurl a mote of fire at a creature or object within range.'
        },
        {
            'spell_id': 'magic_missile',
            'spell_level': 1,
            'is_prepared': 1,
            'always_prepared': 0,
            'name': 'Magic Missile',
            'school': 'evocation',
            'casting_time': '1 action',
            'range_value': '120 feet',
            'components': 'V, S',
            'duration': 'Instantaneous',
            'concentration': 0,
            'description': 'You create three glowing darts of magical force.'
        }
    ]

    # Mock the spell service to return available slots
    with patch.object(action_panel, '_get_character_castable_spells', return_value=test_spells):
        with patch.object(action_panel, '_get_spellcasting_service') as mock_service:
            mock_spellcasting_service = Mock()
            mock_spellcasting_service.can_cast_spell.return_value = (True, "")
            mock_service.return_value = mock_spellcasting_service

            # Create spell action cards
            action_panel._create_spell_action_cards()

    # Verify spell cards were created
    spell_cards = [key for key in action_panel.action_cards.keys() if isinstance(key, str) and key.startswith('spell_')]

    assert len(spell_cards) == 2, f"Expected 2 spell cards, got {len(spell_cards)}"

    # Verify card details
    fire_bolt_card = action_panel.action_cards.get('spell_fire_bolt')
    magic_missile_card = action_panel.action_cards.get('spell_magic_missile')

    assert fire_bolt_card is not None, "Fire Bolt card should be created"
    assert magic_missile_card is not None, "Magic Missile card should be created"

    # Check spell data is attached
    assert hasattr(fire_bolt_card, 'spell_data'), "Fire Bolt card should have spell data"
    assert hasattr(magic_missile_card, 'spell_data'), "Magic Missile card should have spell data"

    # Check action types
    assert fire_bolt_card.action_type in [ActionType.SPELL_ATTACK, ActionType.SPELL_UTILITY], "Fire Bolt should have spell action type"
    assert magic_missile_card.action_type in [ActionType.SPELL_ATTACK, ActionType.SPELL_UTILITY], "Magic Missile should have spell action type"

    print("✅ Spell action cards creation test passed")

def test_spell_casting_context():
    """Test that spell data is passed correctly in action context."""
    print("Testing spell casting context...")

    # Create a test spell card
    mock_character = {
        'id': 'test-wizard-123',
        'name': 'Test Wizard',
        'class_id': 'wizard',
        'level': 1
    }

    action_panel = ActionPanel()
    action_panel.character_context = mock_character

    # Mock spell data
    test_spell = {
        'spell_id': 'fire_bolt',
        'spell_level': 0,
        'name': 'Fire Bolt',
        'school': 'evocation',
        'casting_time': '1 action',
        'range_value': '120 feet',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'concentration': 0,
        'description': 'You hurl a mote of fire at a creature or object within range.'
    }

    # Test the cast spell method directly
    context = {'spell_data': test_spell}

    with patch.object(action_panel, '_get_spellcasting_service') as mock_service:
        mock_spellcasting_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.concentration_started = False
        mock_result.concentration_ended = None
        mock_spellcasting_service.cast_spell.return_value = mock_result
        mock_service.return_value = mock_spellcasting_service

        with patch.object(action_panel, '_log_to_combat_panel') as mock_log:
            with patch.object(action_panel, '_refresh_spell_action_cards'):
                # Test spell casting
                action_panel._cast_spell(ActionType.SPELL_ATTACK, context)

                # Verify spellcasting service was called
                mock_spellcasting_service.cast_spell.assert_called_once_with('test-wizard-123', 'fire_bolt')

                # Verify log was called
                mock_log.assert_called()

    print("✅ Spell casting context test passed")

def test_spell_icon_generation():
    """Test that spell icons are generated correctly."""
    print("Testing spell icon generation...")

    action_panel = ActionPanel()

    # Test different schools and levels
    test_cases = [
        ({'school': 'evocation', 'spell_level': 0}, "🔥"),
        ({'school': 'evocation', 'spell_level': 1}, "💥"),
        ({'school': 'abjuration', 'spell_level': 0}, "🛡"),
        ({'school': 'abjuration', 'spell_level': 1}, "🛡️"),
        ({'school': 'unknown', 'spell_level': 0}, "✨"),
        ({'school': 'unknown', 'spell_level': 1}, "🔮"),
    ]

    for spell_data, expected_icon in test_cases:
        result = action_panel._get_spell_icon(spell_data)
        assert result == expected_icon, f"Expected {expected_icon} for {spell_data}, got {result}"

    print("✅ Spell icon generation test passed")

def main():
    """Run all tests."""
    print("Running spell action cards tests...\n")

    try:
        test_spell_action_cards_creation()
        test_spell_casting_context()
        test_spell_icon_generation()

        print("\n🎉 All spell action cards tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)