"""
Spell Action Card Testing Framework - Specialized Tests
======================================================

TESTING FRAMEWORK - Exclude from ongoing work

Specialized testing utilities for spell action card functionality.
Tests spell selection, action card generation, casting mechanics, and concentration.

Usage:
    python testing_framework_spell_actions.py --character Nathlas
    python testing_framework_spell_actions.py --test-all
    python testing_framework_spell_actions.py --create-test-wizard
"""

import sys
import os
import sqlite3
import json
import time
import argparse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from testing_framework_ui_automation import UIAutomationFramework, TestResult, TestRunner
# Removed TaleKeeperApp import - not needed


@dataclass
class SpellTestCase:
    """Represents a spell test case."""
    spell_id: str
    spell_name: str
    spell_level: int
    expected_action_type: str
    should_consume_slot: bool
    should_trigger_concentration: bool


class SpellActionCardValidator:
    """TESTING FRAMEWORK - Validates spell action card behavior."""

    def __init__(self, framework: UIAutomationFramework):
        self.framework = framework
        self.main_window = framework.main_window

    def test_spell_card_generation(self, character_id: str) -> TestResult:
        """Test that spell cards are generated correctly for a character."""
        start_time = time.time()

        try:
            # Get character's spells from database
            character_spells = self._get_character_spells(character_id)
            if not character_spells:
                return TestResult(
                    "spell_card_generation", False,
                    f"Character {character_id} has no spells in database",
                    time.time()
                )

            # Load character in UI
            if not self._navigate_to_character(character_id):
                return TestResult(
                    "spell_card_generation", False,
                    "Failed to load character in UI",
                    time.time()
                )

            # Start encounter to see action cards
            if not self._enter_encounter_mode():
                return TestResult(
                    "spell_card_generation", False,
                    "Failed to enter encounter mode",
                    time.time()
                )

            # Find action cards
            action_cards = self._find_all_action_cards()
            spell_cards = [card for card in action_cards if self._is_spell_card(card)]

            # Validate spell cards match database
            validation_results = []
            for spell in character_spells:
                card_found = self._find_card_for_spell(spell, spell_cards)
                validation_results.append({
                    'spell': spell,
                    'card_found': card_found is not None,
                    'card': card_found
                })

            # Generate result
            passed_validations = sum(1 for v in validation_results if v['card_found'])
            total_spells = len(character_spells)

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("spell_card_validation")

            if passed_validations == total_spells:
                return TestResult(
                    "spell_card_generation", True,
                    f"All {total_spells} spells have corresponding action cards",
                    time.time(), screenshot, duration
                )
            else:
                missing_spells = [v['spell']['name'] for v in validation_results if not v['card_found']]
                return TestResult(
                    "spell_card_generation", False,
                    f"Missing cards for spells: {', '.join(missing_spells)}",
                    time.time(), screenshot, duration
                )

        except Exception as e:
            return TestResult("spell_card_generation", False, f"Exception: {e}", time.time())

    def test_spell_slot_consumption(self, character_id: str) -> TestResult:
        """Test that casting spells consumes spell slots correctly."""
        start_time = time.time()

        try:
            # Get initial spell slot counts
            initial_slots = self._get_character_spell_slots(character_id)

            # Load character and enter encounter
            if not self._navigate_to_character(character_id):
                return TestResult("spell_slot_consumption", False, "Failed to load character", time.time())

            if not self._enter_encounter_mode():
                return TestResult("spell_slot_consumption", False, "Failed to enter encounter", time.time())

            # Find a level 1 spell card (not cantrip)
            spell_cards = self._find_spell_cards_by_level(1)
            if not spell_cards:
                return TestResult("spell_slot_consumption", False, "No level 1 spell cards found", time.time())

            # Cast the spell
            first_spell_card = spell_cards[0]
            if not self.framework.click_widget(first_spell_card):
                return TestResult("spell_slot_consumption", False, "Failed to click spell card", time.time())

            QTest.qWait(1000)  # Wait for spell casting

            # Check spell slot consumption
            final_slots = self._get_character_spell_slots(character_id)

            # Validate level 1 slot was consumed
            initial_level1 = initial_slots.get('1', {}).get('current', 0)
            final_level1 = final_slots.get('1', {}).get('current', 0)

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("spell_slot_test")

            if final_level1 == initial_level1 - 1:
                return TestResult(
                    "spell_slot_consumption", True,
                    f"Level 1 spell slot consumed correctly ({initial_level1} -> {final_level1})",
                    time.time(), screenshot, duration
                )
            else:
                return TestResult(
                    "spell_slot_consumption", False,
                    f"Spell slot not consumed properly ({initial_level1} -> {final_level1})",
                    time.time(), screenshot, duration
                )

        except Exception as e:
            return TestResult("spell_slot_consumption", False, f"Exception: {e}", time.time())

    def test_cantrip_unlimited_casting(self, character_id: str) -> TestResult:
        """Test that cantrips can be cast unlimited times."""
        start_time = time.time()

        try:
            # Load character and enter encounter
            if not self._navigate_to_character(character_id):
                return TestResult("cantrip_unlimited", False, "Failed to load character", time.time())

            if not self._enter_encounter_mode():
                return TestResult("cantrip_unlimited", False, "Failed to enter encounter", time.time())

            # Find cantrip cards (level 0)
            cantrip_cards = self._find_spell_cards_by_level(0)
            if not cantrip_cards:
                return TestResult("cantrip_unlimited", False, "No cantrip cards found", time.time())

            # Cast the same cantrip multiple times
            cantrip_card = cantrip_cards[0]
            cast_count = 0

            for i in range(5):  # Try casting 5 times
                if self.framework.click_widget(cantrip_card):
                    cast_count += 1
                    QTest.qWait(500)
                else:
                    break

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot("cantrip_unlimited_test")

            if cast_count >= 5:
                return TestResult(
                    "cantrip_unlimited", True,
                    f"Cantrip cast {cast_count} times successfully",
                    time.time(), screenshot, duration
                )
            else:
                return TestResult(
                    "cantrip_unlimited", False,
                    f"Cantrip only cast {cast_count}/5 times",
                    time.time(), screenshot, duration
                )

        except Exception as e:
            return TestResult("cantrip_unlimited", False, f"Exception: {e}", time.time())

    def _get_character_spells(self, character_id: str) -> List[Dict]:
        """Get character's spells from database."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT cs.spell_id, cs.spell_level, cs.is_prepared, cs.always_prepared,
                       s.name, s.school, s.casting_time, s.concentration
                FROM character_spells cs
                JOIN spells s ON cs.spell_id = s.id
                WHERE cs.character_id = ?
                ORDER BY cs.spell_level, s.name
            """, (character_id,))

            spells = []
            for row in cursor.fetchall():
                spells.append({
                    'spell_id': row[0],
                    'spell_level': row[1],
                    'is_prepared': row[2],
                    'always_prepared': row[3],
                    'name': row[4],
                    'school': row[5],
                    'casting_time': row[6],
                    'concentration': row[7]
                })

            conn.close()
            return spells

        except Exception as e:
            print(f"Error getting character spells: {e}")
            return []

    def _get_character_spell_slots(self, character_id: str) -> Dict:
        """Get character's current spell slots."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            # Check if character has wizard_features table
            cursor.execute("""
                SELECT spell_slots_1_current, spell_slots_1_max,
                       spell_slots_2_current, spell_slots_2_max,
                       spell_slots_3_current, spell_slots_3_max
                FROM wizard_features
                WHERE character_id = ?
            """, (character_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    '1': {'current': row[0], 'max': row[1]},
                    '2': {'current': row[2], 'max': row[3]},
                    '3': {'current': row[4], 'max': row[5]}
                }

        except Exception:
            pass

        return {}

    def _navigate_to_character(self, character_id: str) -> bool:
        """Navigate to and load a specific character."""
        # This would need to interact with character selection UI
        # For now, assume character is already loaded
        return True

    def _enter_encounter_mode(self) -> bool:
        """Enter encounter mode to see action cards."""
        # Look for encounter-related buttons
        encounter_btns = [
            "Start Encounter", "Begin Combat", "Enter Encounter",
            "Combat", "Encounter", "Battle"
        ]

        for btn_text in encounter_btns:
            btn = self.framework.find_widget_by_text(btn_text, QPushButton)
            if btn and btn.isVisible():
                return self.framework.click_widget(btn)

        # Check if already in encounter mode
        action_panel = self.framework.find_widget_by_text("Action", QWidget)
        return action_panel is not None

    def _find_all_action_cards(self) -> List[QWidget]:
        """Find all action cards in the action panel."""
        action_cards = []

        # Look for widgets that look like action cards
        buttons = self.main_window.findChildren(QPushButton)

        for button in buttons:
            # Check if this looks like an action card
            if self._looks_like_action_card(button):
                action_cards.append(button)

        return action_cards

    def _looks_like_action_card(self, widget: QWidget) -> bool:
        """Check if a widget looks like an action card."""
        if not isinstance(widget, QPushButton):
            return False

        # Check parent containers
        parent = widget.parent()
        while parent:
            if hasattr(parent, 'objectName'):
                parent_name = parent.objectName().lower()
                if 'action' in parent_name or 'card' in parent_name:
                    return True
            parent = parent.parent()

        return False

    def _is_spell_card(self, card: QWidget) -> bool:
        """Check if an action card is a spell card."""
        if hasattr(card, 'text'):
            text = card.text().lower()
            spell_indicators = ['spell', 'cantrip', '✨', '⭐', 'cast', 'level']
            return any(indicator in text for indicator in spell_indicators)
        return False

    def _find_card_for_spell(self, spell: Dict, cards: List[QWidget]) -> Optional[QWidget]:
        """Find the action card for a specific spell."""
        spell_name = spell['name'].lower()

        for card in cards:
            if hasattr(card, 'text'):
                card_text = card.text().lower()
                if spell_name in card_text:
                    return card

        return None

    def _find_spell_cards_by_level(self, level: int) -> List[QWidget]:
        """Find spell cards for a specific spell level."""
        all_cards = self._find_all_action_cards()
        level_cards = []

        for card in all_cards:
            if hasattr(card, 'text'):
                text = card.text()
                if level == 0 and '✨' in text:  # Cantrip indicator
                    level_cards.append(card)
                elif level > 0 and f'{level}⭐' in text:  # Level indicator
                    level_cards.append(card)

        return level_cards


class TestDataCreator:
    """TESTING FRAMEWORK - Creates test data for spell testing."""

    def __init__(self):
        self.db_path = 'talekeeper.db'

    def create_test_wizard_with_spells(self, name: str = "TestWizardSpells") -> str:
        """Create a test wizard character with known spells."""
        try:
            # Generate unique character ID
            import uuid
            character_id = str(uuid.uuid4())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create basic character
            cursor.execute("""
                INSERT INTO characters (
                    id, name, class_id, level, strength, dexterity, constitution,
                    intelligence, wisdom, charisma, hit_points_max, hit_points_current
                ) VALUES (?, ?, 'wizard', 1, 10, 14, 12, 16, 13, 8, 8, 8)
            """, (character_id, name))

            # Add wizard features
            cursor.execute("""
                INSERT INTO wizard_features (
                    character_id, level, spell_slots_1_max, spell_slots_1_current,
                    spell_slots_2_max, spell_slots_2_current, spellbook_spells_known
                ) VALUES (?, 1, 2, 2, 0, 0, 6)
            """, (character_id,))

            # Add test spells
            test_spells = [
                ('fire_bolt', 0, True, True),  # Cantrip, always prepared
                ('prestidigitation', 0, True, True),  # Cantrip, always prepared
                ('light', 0, True, True),  # Cantrip, always prepared
                ('magic_missile', 1, True, False),  # Level 1, prepared
                ('shield', 1, True, False),  # Level 1, prepared
                ('mage_armor', 1, False, False),  # Level 1, not prepared
            ]

            for spell_id, level, prepared, always_prepared in test_spells:
                cursor.execute("""
                    INSERT INTO character_spells (
                        character_id, spell_id, spell_level, is_prepared,
                        source, always_prepared
                    ) VALUES (?, ?, ?, ?, 'class', ?)
                """, (character_id, spell_id, level, prepared, always_prepared))

            conn.commit()
            conn.close()

            print(f"Created test wizard character: {name} ({character_id})")
            return character_id

        except Exception as e:
            print(f"Error creating test wizard: {e}")
            return ""

    def cleanup_test_characters(self):
        """Remove test characters from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Find test characters
            cursor.execute("SELECT id FROM characters WHERE name LIKE 'Test%' OR name LIKE 'Auto%'")
            test_chars = cursor.fetchall()

            for char_id in test_chars:
                # Remove from all related tables
                tables = [
                    'character_spells', 'wizard_features', 'character_spellcasting',
                    'wizard_spellbook', 'characters'
                ]

                for table in tables:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE character_id = ?", (char_id[0],))
                    except:
                        pass

            conn.commit()
            conn.close()

            print(f"Cleaned up {len(test_chars)} test characters")

        except Exception as e:
            print(f"Error cleaning up test characters: {e}")


def main():
    """Main entry point for spell action testing."""
    parser = argparse.ArgumentParser(description='Spell Action Card Testing Framework')
    parser.add_argument('--character', help='Character ID to test')
    parser.add_argument('--create-test-wizard', action='store_true',
                       help='Create a test wizard character')
    parser.add_argument('--test-all', action='store_true',
                       help='Run all spell tests')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up test characters')

    args = parser.parse_args()

    creator = TestDataCreator()

    if args.cleanup:
        creator.cleanup_test_characters()
        return 0

    if args.create_test_wizard:
        character_id = creator.create_test_wizard_with_spells()
        print(f"Created test wizard: {character_id}")
        return 0

    # Run UI tests
    app = QApplication(sys.argv)
    runner = TestRunner()

    try:
        if not runner.setup():
            print("Failed to setup testing environment")
            return 1

        validator = SpellActionCardValidator(runner.framework)

        if args.character:
            character_id = args.character
        else:
            # Create a test character
            character_id = creator.create_test_wizard_with_spells("AutoTestWizardSpells")

        print(f"Testing spell actions for character: {character_id}")

        # Run tests
        tests = [
            validator.test_spell_card_generation,
            validator.test_spell_slot_consumption,
            validator.test_cantrip_unlimited_casting
        ]

        for test_func in tests:
            result = test_func(character_id)
            runner.results.append(result)
            print(f"  {result.test_name}: {'PASS' if result.success else 'FAIL'} - {result.message}")

        runner.generate_report()

        passed = sum(1 for r in runner.results if r.success)
        total = len(runner.results)
        print(f"\nSpell testing completed: {passed}/{total} tests passed")

        return 0 if passed == total else 1

    except Exception as e:
        print(f"Testing failed: {e}")
        return 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())