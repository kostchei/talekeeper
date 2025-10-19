#test
"""
TESTING FRAMEWORK - Qt6 test to verify spell action cards appear
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
import time


def test_spell_action_cards():
    """Test that spell action cards appear for Nathlas."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    QTest.qWait(2000)

    print("\n=== SPELL ACTION CARD TEST ===")

    action_panel = window.action_panel
    print(f"Action panel found: {action_panel is not None}")

    if action_panel:
        print(f"Action panel has character_context: {hasattr(action_panel, 'character_context')}")

        if hasattr(action_panel, 'character_context') and action_panel.character_context:
            char_id = action_panel.character_context.get('id')
            char_class = action_panel.character_context.get('class_id')
            print(f"Character ID: {char_id}")
            print(f"Character class: {char_class}")

        print(f"\nAction cards dictionary: {hasattr(action_panel, 'action_cards')}")
        if hasattr(action_panel, 'action_cards'):
            print(f"Number of action cards: {len(action_panel.action_cards)}")
            print(f"Action card types: {list(action_panel.action_cards.keys())}")

            spell_cards = [k for k in action_panel.action_cards.keys() if isinstance(k, str) and k.startswith('spell_')]
            print(f"\nSpell action cards in dictionary: {spell_cards}")
            for spell_key in spell_cards:
                card = action_panel.action_cards[spell_key]
                print(f"  {spell_key}: visible={card.isVisible()}, parent={card.parent()}, type={type(card).__name__}")

                card_buttons = card.findChildren(QPushButton)
                print(f"    Buttons inside this card: {len(card_buttons)}")
                for btn in card_buttons:
                    print(f"      - '{btn.text()}' (visible={btn.isVisible()})")

        if hasattr(action_panel, 'current_category'):
            print(f"\nCurrent category: {action_panel.current_category}")

        all_buttons = action_panel.findChildren(QPushButton)
        print(f"\nTotal QPushButtons in action panel: {len(all_buttons)}")
        print(f"All button texts:")
        for btn in all_buttons:
            print(f"  - '{btn.text()}' (visible={btn.isVisible()})")

        spell_buttons = []
        for btn in all_buttons:
            text = btn.text().lower()
            if any(keyword in text for keyword in ['fire bolt', 'magic missile', 'spell', 'cantrip', 'level 0', 'level 1']):
                spell_buttons.append(btn)
                print(f"  Found spell button: '{btn.text()}'")

        print(f"\nSpell-related buttons found: {len(spell_buttons)}")

        spell_card_count = len([k for k in action_panel.action_cards.keys() if isinstance(k, str) and k.startswith('spell_')])

        if spell_card_count > 0:
            print(f"\nSUCCESS: {spell_card_count} spell action card(s) present!")
            print("Note: Button text shows 'Use' instead of spell name")
            return True
        else:
            print("\nFAILURE: No spell action cards found!")
            return False

    return False


if __name__ == "__main__":
    success = test_spell_action_cards()
    sys.exit(0 if success else 1)