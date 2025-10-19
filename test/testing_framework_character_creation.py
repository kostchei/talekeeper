# test
"""
Character Creation Automation Framework
=======================================

TESTING FRAMEWORK - Exclude from ongoing work

Automated character creation testing for all classes with spell selection validation.
Tests the complete character creation pipeline including spell selection for spellcasters.

Usage:
    python testing_framework_character_creation.py --class wizard --name TestWizard
    python testing_framework_character_creation.py --test-all-classes
    python testing_framework_character_creation.py --validate-spells
"""

import sys
import os
import time
import sqlite3
import json
import argparse
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QLabel, QWidget, QListWidget, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from testing_framework_ui_automation import UIAutomationFramework, TestResult, TestRunner


class CharacterClass(Enum):
    """D&D Character Classes."""
    WIZARD = "wizard"
    CLERIC = "cleric"
    WARLOCK = "warlock"
    PALADIN = "paladin"
    FIGHTER = "fighter"
    BARBARIAN = "barbarian"
    ROGUE = "rogue"


@dataclass
class SpellSelectionRequirements:
    """Spell selection requirements for a class."""
    cantrips_required: int
    cantrips_known_level1: int
    spells_known_level1: int
    spells_prepared_level1: int
    uses_spellbook: bool  # Wizard
    prepares_from_list: bool  # Cleric, Paladin


class CharacterCreationAutomator:
    """TESTING FRAMEWORK - Automates complete character creation process."""

    def __init__(self, framework: UIAutomationFramework):
        self.framework = framework
        self.main_window = framework.main_window

        # Spell requirements by class (D&D 2024)
        self.spell_requirements = {
            CharacterClass.WIZARD: SpellSelectionRequirements(
                cantrips_required=3, cantrips_known_level1=3,
                spells_known_level1=6, spells_prepared_level1=4,
                uses_spellbook=True, prepares_from_list=False
            ),
            CharacterClass.CLERIC: SpellSelectionRequirements(
                cantrips_required=3, cantrips_known_level1=3,
                spells_known_level1=0, spells_prepared_level1=4,
                uses_spellbook=False, prepares_from_list=True
            ),
            CharacterClass.WARLOCK: SpellSelectionRequirements(
                cantrips_required=2, cantrips_known_level1=2,
                spells_known_level1=2, spells_prepared_level1=2,
                uses_spellbook=False, prepares_from_list=False
            ),
            CharacterClass.PALADIN: SpellSelectionRequirements(
                cantrips_required=0, cantrips_known_level1=0,
                spells_known_level1=0, spells_prepared_level1=2,
                uses_spellbook=False, prepares_from_list=True
            )
        }

        # Recommended spells by class
        self.recommended_spells = {
            CharacterClass.WIZARD: {
                'cantrips': ['Fire Bolt', 'Prestidigitation', 'Light'],
                'level1': ['Magic Missile', 'Shield', 'Mage Armor', 'Detect Magic', 'Burning Hands', 'Feather Fall']
            },
            CharacterClass.CLERIC: {
                'cantrips': ['Sacred Flame', 'Guidance', 'Light'],
                'level1': ['Cure Wounds', 'Bless', 'Healing Word', 'Guiding Bolt']
            },
            CharacterClass.WARLOCK: {
                'cantrips': ['Eldritch Blast', 'Prestidigitation'],
                'level1': ['Hex', 'Armor of Agathys']
            },
            CharacterClass.PALADIN: {
                'cantrips': [],  # No cantrips at level 1
                'level1': ['Bless', 'Shield of Faith']
            }
        }

    def create_complete_character(self, char_class: CharacterClass, name: str) -> TestResult:
        """Create a complete character with all steps."""
        start_time = time.time()

        try:
            steps_completed = []

            # Step 1: Navigate to character creation
            if not self._navigate_to_character_creation():
                return TestResult("create_character", False, "Failed to start character creation", time.time())
            steps_completed.append("Started character creation")

            # Step 2: Select class
            if not self._select_class(char_class):
                return TestResult("create_character", False, f"Failed to select {char_class.value} class", time.time())
            steps_completed.append(f"Selected {char_class.value} class")

            # Step 3: Handle class features (fighting styles, invocations, etc.)
            if not self._handle_class_features(char_class):
                return TestResult("create_character", False, "Failed to handle class features", time.time())
            steps_completed.append("Handled class features")

            # Step 4: Handle spell selection (for spellcasters)
            if char_class in self.spell_requirements:
                if not self._handle_spell_selection(char_class):
                    return TestResult("create_character", False, "Failed spell selection", time.time())
                steps_completed.append("Completed spell selection")

            # Step 5: Select background and species
            if not self._select_background_and_species():
                return TestResult("create_character", False, "Failed background/species selection", time.time())
            steps_completed.append("Selected background and species")

            # Step 6: Set ability scores
            if not self._set_ability_scores(char_class):
                return TestResult("create_character", False, "Failed to set ability scores", time.time())
            steps_completed.append("Set ability scores")

            # Step 7: Handle equipment
            if not self._handle_equipment():
                return TestResult("create_character", False, "Failed equipment selection", time.time())
            steps_completed.append("Handled equipment")

            # Step 8: Set name and finalize
            if not self._finalize_character(name):
                return TestResult("create_character", False, "Failed to finalize character", time.time())
            steps_completed.append("Finalized character")

            # Verify character was created
            character_id = self._verify_character_created(name)
            if not character_id:
                return TestResult("create_character", False, "Character not found in database", time.time())

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot(f"character_created_{char_class.value}")

            return TestResult(
                "create_character", True,
                f"Successfully created {char_class.value} '{name}' - Steps: {', '.join(steps_completed)}",
                time.time(), screenshot, duration
            )

        except Exception as e:
            return TestResult("create_character", False, f"Exception: {e}", time.time())

    def _navigate_to_character_creation(self) -> bool:
        """Navigate to character creation interface."""
        # Look for character creation entry points
        creation_triggers = [
            "Create Character", "New Character", "Character Creation",
            "Create", "New", "Add Character"
        ]

        for trigger_text in creation_triggers:
            widget = self.framework.find_widget_by_text(trigger_text, QPushButton)
            if widget and widget.isVisible():
                if self.framework.click_widget(widget):
                    QTest.qWait(1000)  # Wait for UI to load
                    return True

        # Check if already in character creation
        class_label = self.framework.find_widget_by_text("Class", QLabel)
        return class_label is not None

    def _select_class(self, char_class: CharacterClass) -> bool:
        """Select character class."""
        class_name = char_class.value.title()

        # Try different selection methods
        methods = [
            self._select_class_from_list,
            self._select_class_from_buttons,
            self._select_class_from_combo
        ]

        for method in methods:
            if method(class_name):
                QTest.qWait(1000)  # Wait for class features to load
                return True

        return False

    def _select_class_from_list(self, class_name: str) -> bool:
        """Select class from QListWidget."""
        list_widgets = self.main_window.findChildren(QListWidget)

        for list_widget in list_widgets:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item and class_name.lower() in item.text().lower():
                    list_widget.setCurrentItem(item)
                    return True

        return False

    def _select_class_from_buttons(self, class_name: str) -> bool:
        """Select class from buttons."""
        buttons = self.main_window.findChildren(QPushButton)

        for button in buttons:
            if class_name.lower() in button.text().lower():
                return self.framework.click_widget(button)

        return False

    def _select_class_from_combo(self, class_name: str) -> bool:
        """Select class from combo box."""
        combos = self.main_window.findChildren(QComboBox)

        for combo in combos:
            if self.framework.set_combo_box_value(combo, class_name):
                return True

        return False

    def _handle_class_features(self, char_class: CharacterClass) -> bool:
        """Handle class-specific feature selection."""
        if char_class == CharacterClass.FIGHTER:
            return self._select_fighting_style()
        elif char_class == CharacterClass.WARLOCK:
            return self._select_warlock_invocation()
        elif char_class == CharacterClass.ROGUE:
            return self._handle_rogue_features()

        return True  # No special features for other classes at level 1

    def _select_fighting_style(self) -> bool:
        """Select fighting style for Fighter."""
        fighting_styles = ["Defense", "Dueling", "Archery", "Great Weapon Fighting"]

        # Look for fighting style selection
        combo = self.framework.find_widget_by_text("Fighting Style", QComboBox)
        if combo:
            return self.framework.set_combo_box_value(combo, fighting_styles[0])

        # Alternative: look for radio buttons or other selection methods
        for style in fighting_styles:
            button = self.framework.find_widget_by_text(style, QPushButton)
            if button:
                return self.framework.click_widget(button)

        return True  # May not be required at level 1

    def _select_warlock_invocation(self) -> bool:
        """Select invocation for Warlock."""
        # Level 1 Warlocks don't get invocations in D&D 2024
        return True

    def _handle_rogue_features(self) -> bool:
        """Handle Rogue-specific features."""
        # Select expertise skills if available
        checkboxes = self.main_window.findChildren(QCheckBox)
        expertise_selected = 0

        for checkbox in checkboxes:
            if expertise_selected >= 2:  # Rogues get 2 expertise at level 1
                break

            if "expertise" in checkbox.text().lower() and not checkbox.isChecked():
                self.framework.check_checkbox(checkbox, True)
                expertise_selected += 1

        return True

    def _handle_spell_selection(self, char_class: CharacterClass) -> bool:
        """Handle spell selection for spellcasting classes."""
        requirements = self.spell_requirements[char_class]
        recommended = self.recommended_spells[char_class]

        success = True

        # Select cantrips
        if requirements.cantrips_required > 0:
            if not self._select_cantrips(recommended['cantrips'], requirements.cantrips_required):
                success = False

        # Select spells
        if requirements.spells_known_level1 > 0:
            if not self._select_level1_spells(recommended['level1'], requirements.spells_known_level1):
                success = False

        QTest.qWait(500)
        return success

    def _select_cantrips(self, recommended_cantrips: List[str], required_count: int) -> bool:
        """Select cantrips from available options."""
        selected_count = 0

        # Method 1: Combo boxes for cantrip selection
        combos = self.main_window.findChildren(QComboBox)
        cantrip_combos = []

        for combo in combos:
            # Check if this combo is for cantrip selection
            parent = combo.parent()
            if parent:
                labels = parent.findChildren(QLabel)
                for label in labels:
                    if "cantrip" in label.text().lower():
                        cantrip_combos.append(combo)
                        break

        # Select cantrips in combo boxes
        for i, combo in enumerate(cantrip_combos[:required_count]):
            if i < len(recommended_cantrips):
                if self.framework.set_combo_box_value(combo, recommended_cantrips[i]):
                    selected_count += 1

        # Method 2: Checkboxes for cantrips
        if selected_count < required_count:
            checkboxes = self.main_window.findChildren(QCheckBox)

            for checkbox in checkboxes:
                if selected_count >= required_count:
                    break

                checkbox_text = checkbox.text()
                for cantrip in recommended_cantrips:
                    if cantrip.lower() in checkbox_text.lower() and not checkbox.isChecked():
                        if self.framework.check_checkbox(checkbox, True):
                            selected_count += 1
                            break

        return selected_count >= required_count

    def _select_level1_spells(self, recommended_spells: List[str], required_count: int) -> bool:
        """Select level 1 spells."""
        selected_count = 0
        checkboxes = self.main_window.findChildren(QCheckBox)

        for checkbox in checkboxes:
            if selected_count >= required_count:
                break

            checkbox_text = checkbox.text()
            for spell in recommended_spells:
                if spell.lower() in checkbox_text.lower() and not checkbox.isChecked():
                    if self.framework.check_checkbox(checkbox, True):
                        selected_count += 1
                        break

        return selected_count >= required_count

    def _select_background_and_species(self) -> bool:
        """Select background and species."""
        # Select a default background (Acolyte)
        bg_success = self._select_from_list_or_combo("Acolyte", ["background"])

        # Select a default species (Human)
        species_success = self._select_from_list_or_combo("Human", ["species", "race"])

        return bg_success and species_success

    def _select_from_list_or_combo(self, option_name: str, context_keywords: List[str]) -> bool:
        """Select an option from list widget or combo box based on context."""
        # Try list widgets first
        list_widgets = self.main_window.findChildren(QListWidget)

        for list_widget in list_widgets:
            # Check if this list is in the right context
            parent = list_widget.parent()
            if parent:
                labels = parent.findChildren(QLabel)
                parent_text = " ".join([label.text() for label in labels]).lower()

                if any(keyword in parent_text for keyword in context_keywords):
                    # Try to select the option
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if item and option_name.lower() in item.text().lower():
                            list_widget.setCurrentItem(item)
                            QTest.qWait(300)
                            return True

        # Try combo boxes
        combos = self.main_window.findChildren(QComboBox)

        for combo in combos:
            parent = combo.parent()
            if parent:
                labels = parent.findChildren(QLabel)
                parent_text = " ".join([label.text() for label in labels]).lower()

                if any(keyword in parent_text for keyword in context_keywords):
                    if self.framework.set_combo_box_value(combo, option_name):
                        return True

        return False

    def _set_ability_scores(self, char_class: CharacterClass) -> bool:
        """Set ability scores appropriate for the class."""
        # Recommended ability priorities by class
        class_priorities = {
            CharacterClass.WIZARD: {'intelligence': 15, 'dexterity': 14, 'constitution': 13},
            CharacterClass.CLERIC: {'wisdom': 15, 'strength': 14, 'constitution': 13},
            CharacterClass.WARLOCK: {'charisma': 15, 'dexterity': 14, 'constitution': 13},
            CharacterClass.PALADIN: {'strength': 15, 'charisma': 14, 'constitution': 13},
            CharacterClass.FIGHTER: {'strength': 15, 'constitution': 14, 'dexterity': 13},
            CharacterClass.BARBARIAN: {'strength': 15, 'constitution': 14, 'dexterity': 13},
            CharacterClass.ROGUE: {'dexterity': 15, 'intelligence': 14, 'constitution': 13}
        }

        priorities = class_priorities.get(char_class, {})
        spinboxes = self.main_window.findChildren(QSpinBox)

        # Try to set ability scores
        for spinbox in spinboxes:
            parent = spinbox.parent()
            if parent:
                labels = parent.findChildren(QLabel)
                for label in labels:
                    label_text = label.text().lower()
                    for ability, value in priorities.items():
                        if ability in label_text:
                            self.framework.set_spinbox_value(spinbox, value)
                            break

        return True

    def _handle_equipment(self) -> bool:
        """Handle equipment selection."""
        # Just select default equipment options
        buttons = self.main_window.findChildren(QPushButton)

        for button in buttons:
            if button.text() and any(keyword in button.text().lower()
                                   for keyword in ["leather armor", "chain mail", "equipment"]):
                if button.isCheckable() and not button.isChecked():
                    self.framework.click_widget(button)

        return True

    def _finalize_character(self, name: str) -> bool:
        """Set character name and complete creation."""
        # Set character name
        name_widgets = [
            self.framework.find_widget_by_object_name("characterNameInput"),
            self.framework.find_widget_by_text("Name", QComboBox)
        ]

        for widget in name_widgets:
            if widget:
                if isinstance(widget, QComboBox):
                    widget.setEditText(name)
                elif hasattr(widget, 'setText'):
                    widget.setText(name)

        # Find and click final creation button
        final_buttons = [
            "Create Character", "Finish", "Complete", "Done", "Create"
        ]

        for button_text in final_buttons:
            button = self.framework.find_widget_by_text(button_text, QPushButton)
            if button and button.isVisible():
                return self.framework.click_widget(button)

        return False

    def _verify_character_created(self, name: str) -> Optional[str]:
        """Verify character was created in database."""
        try:
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM characters WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else None

        except Exception as e:
            print(f"Error verifying character creation: {e}")
            return None


class SpellSelectionValidator:
    """TESTING FRAMEWORK - Validates spell selection during character creation."""

    def __init__(self, framework: UIAutomationFramework):
        self.framework = framework

    def validate_spell_selection_ui(self, char_class: CharacterClass) -> TestResult:
        """Validate that spell selection UI appears for spellcasting classes."""
        start_time = time.time()

        try:
            automator = CharacterCreationAutomator(self.framework)

            # Start character creation
            if not automator._navigate_to_character_creation():
                return TestResult("spell_ui_validation", False, "Failed to start creation", time.time())

            # Select spellcasting class
            if not automator._select_class(char_class):
                return TestResult("spell_ui_validation", False, f"Failed to select {char_class.value}", time.time())

            QTest.qWait(1000)  # Wait for spell UI to load

            # Look for spell selection elements
            spell_ui_found = self._find_spell_selection_ui()

            duration = int((time.time() - start_time) * 1000)
            screenshot = self.framework.take_screenshot(f"spell_ui_{char_class.value}")

            if spell_ui_found:
                return TestResult(
                    "spell_ui_validation", True,
                    f"Spell selection UI found for {char_class.value}",
                    time.time(), screenshot, duration
                )
            else:
                return TestResult(
                    "spell_ui_validation", False,
                    f"No spell selection UI found for {char_class.value}",
                    time.time(), screenshot, duration
                )

        except Exception as e:
            return TestResult("spell_ui_validation", False, f"Exception: {e}", time.time())

    def _find_spell_selection_ui(self) -> bool:
        """Check if spell selection UI elements are present."""
        spell_indicators = [
            "cantrip", "spell", "known", "prepared", "spellbook",
            "Fire Bolt", "Magic Missile", "Sacred Flame", "Eldritch Blast"
        ]

        # Check for combo boxes (cantrip selection)
        combos = self.framework.main_window.findChildren(QComboBox)
        for combo in combos:
            for i in range(combo.count()):
                item_text = combo.itemText(i).lower()
                if any(indicator in item_text for indicator in spell_indicators):
                    return True

        # Check for checkboxes (spell selection)
        checkboxes = self.framework.main_window.findChildren(QCheckBox)
        for checkbox in checkboxes:
            checkbox_text = checkbox.text().lower()
            if any(indicator in checkbox_text for indicator in spell_indicators):
                return True

        # Check for labels
        labels = self.framework.main_window.findChildren(QLabel)
        for label in labels:
            label_text = label.text().lower()
            if any(indicator in label_text for indicator in spell_indicators):
                return True

        return False


def main():
    """Main entry point for character creation testing."""
    parser = argparse.ArgumentParser(description='Character Creation Testing Framework')
    parser.add_argument('--class', dest='char_class',
                       choices=[c.value for c in CharacterClass],
                       help='Character class to create')
    parser.add_argument('--name', default='TestCharacter', help='Character name')
    parser.add_argument('--test-all-classes', action='store_true',
                       help='Test character creation for all classes')
    parser.add_argument('--validate-spells', action='store_true',
                       help='Validate spell selection UI for spellcasters')

    args = parser.parse_args()

    app = QApplication(sys.argv)
    runner = TestRunner()

    try:
        if not runner.setup():
            print("Failed to setup testing environment")
            return 1

        automator = CharacterCreationAutomator(runner.framework)
        validator = SpellSelectionValidator(runner.framework)

        if args.validate_spells:
            # Test spell UI for all spellcasting classes
            spellcasters = [CharacterClass.WIZARD, CharacterClass.CLERIC,
                           CharacterClass.WARLOCK, CharacterClass.PALADIN]

            for char_class in spellcasters:
                result = validator.validate_spell_selection_ui(char_class)
                runner.results.append(result)
                print(f"  Spell UI {char_class.value}: {'PASS' if result.success else 'FAIL'} - {result.message}")

        elif args.test_all_classes:
            # Test creation for all classes
            for char_class in CharacterClass:
                char_name = f"Test{char_class.value.title()}"
                result = automator.create_complete_character(char_class, char_name)
                runner.results.append(result)
                print(f"  Create {char_class.value}: {'PASS' if result.success else 'FAIL'} - {result.message}")

        elif args.char_class:
            # Test specific class
            char_class = CharacterClass(args.char_class)
            result = automator.create_complete_character(char_class, args.name)
            runner.results.append(result)
            print(f"  Create {char_class.value}: {'PASS' if result.success else 'FAIL'} - {result.message}")

        else:
            print("Please specify --class, --test-all-classes, or --validate-spells")
            return 1

        runner.generate_report()

        passed = sum(1 for r in runner.results if r.success)
        total = len(runner.results)
        print(f"\nCharacter creation testing completed: {passed}/{total} tests passed")

        return 0 if passed == total else 1

    except Exception as e:
        print(f"Testing failed: {e}")
        return 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())