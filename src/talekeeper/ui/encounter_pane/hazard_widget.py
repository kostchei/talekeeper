# core
# category: core
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QTextEdit, QScrollArea,
                            QGroupBox, QGridLayout, QListWidget, QListWidgetItem,
                            QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, List
import random

from talekeeper.services.hazard_service import HazardService


class HazardWidget(QWidget):
    hazard_completed = pyqtSignal(bool, int, int, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hazard_service = HazardService()
        self.current_hazard: Optional[Dict] = None
        self.character_data: Optional[Dict] = None
        self.selected_gear: List[str] = []

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.title_label = QLabel("No Active Hazard")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(150)
        self.description_text.setReadOnly(True)
        layout.addWidget(self.description_text)

        self.mechanics_text = QTextEdit()
        self.mechanics_text.setMaximumHeight(100)
        self.mechanics_text.setReadOnly(True)
        self.mechanics_text.setPlaceholderText("Hazard mechanics...")
        layout.addWidget(self.mechanics_text)

        gear_group = QGroupBox("Nominate Gear (Optional)")
        gear_layout = QVBoxLayout()

        self.gear_list = QListWidget()
        self.gear_list.setMaximumHeight(120)
        self.gear_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        gear_layout.addWidget(self.gear_list)

        gear_help = QLabel("Select equipment that might help with this hazard")
        gear_help.setStyleSheet("color: #888;")
        gear_layout.addWidget(gear_help)

        gear_group.setLayout(gear_layout)
        layout.addWidget(gear_group)

        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.attempt_button = QPushButton("Face Hazard")
        self.attempt_button.clicked.connect(self.attempt_hazard)
        self.attempt_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.attempt_button)
        buttons_layout.addStretch()

        layout.addWidget(buttons_frame)

        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(120)
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")
        layout.addWidget(self.results_text)

        self.setLayout(layout)

    def set_character_data(self, character_data: Dict):
        self.character_data = character_data
        self._populate_gear_list()

    def start_hazard(self, hazard: Dict):
        if not self.character_data:
            QMessageBox.warning(self, "Error", "No character selected")
            return

        self.current_hazard = hazard
        self.selected_gear = []
        self.results_text.clear()

        self.title_label.setText(hazard.get('name', 'Unknown Hazard'))

        description = hazard.get('description', 'A dangerous environmental hazard.')
        self.description_text.setPlainText(description)

        mechanics_lines = []
        if hazard.get('dc'):
            save_type = hazard.get('save_type', 'Save')
            mechanics_lines.append(f"DC {hazard['dc']} {save_type}")

        if hazard.get('damage_dice'):
            damage_type = hazard.get('damage_type', '')
            mechanics_lines.append(f"Damage: {hazard['damage_dice']} ({hazard.get('damage_avg', 0)}) {damage_type}")

        mechanics_lines.append(f"Failure: {hazard.get('failure_effect', 'Unknown')}")

        if hazard.get('success_effect'):
            mechanics_lines.append(f"Success: {hazard['success_effect']}")

        if hazard.get('mechanics'):
            mechanics_lines.append(f"\n{hazard['mechanics']}")

        mechanics_lines.append(f"\nXP Reward: {hazard.get('xp', 0)}")

        self.mechanics_text.setPlainText('\n'.join(mechanics_lines))

    def _populate_gear_list(self):
        self.gear_list.clear()

        if not self.character_data:
            return

        import sqlite3
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()

        character_id = self.character_data.get('id')
        cursor.execute("""
            SELECT item_name, equipped
            FROM character_inventory
            WHERE character_id = ?
            AND item_type IN ('gear', 'armor', 'shield', 'cloak', 'ring')
            ORDER BY equipped DESC, item_name
        """, (character_id,))

        items = cursor.fetchall()
        conn.close()

        for item_name, equipped in items:
            display_name = f"{item_name} {'(equipped)' if equipped else ''}"
            self.gear_list.addItem(display_name.strip())

    def attempt_hazard(self):
        if not self.current_hazard or not self.character_data:
            return

        self.selected_gear = [item.text().replace(' (equipped)', '') for item in self.gear_list.selectedItems()]

        bonuses = self.hazard_service.apply_gear_bonus(self.current_hazard, self.selected_gear)

        save_type = self.current_hazard.get('save_type', 'Dexterity').lower()
        ability_map = {
            'strength': 'strength',
            'dexterity': 'dexterity',
            'constitution': 'constitution',
            'intelligence': 'intelligence',
            'wisdom': 'wisdom',
            'charisma': 'charisma'
        }

        ability_key = None
        for key in ability_map:
            if key in save_type:
                ability_key = ability_map[key]
                break

        if not ability_key:
            ability_key = 'dexterity'

        ability_score = self.character_data.get(ability_key, 10)
        ability_mod = (ability_score - 10) // 2

        from talekeeper.services.proficiency_bonus import get_proficiency_bonus
        proficiency = get_proficiency_bonus(self.character_data.get('level', 1))

        roll = random.randint(1, 20)
        has_advantage = bonuses.get('advantage', False)
        if has_advantage:
            roll2 = random.randint(1, 20)
            roll = max(roll, roll2)

        total = roll + ability_mod + proficiency

        dc = self.current_hazard.get('dc', 15) - bonuses.get('dc_reduction', 0)

        success = total >= dc

        results = []
        results.append(f"{'Advantage ' if has_advantage else ''}Roll: {roll}")
        results.append(f"Modifier: +{ability_mod} ({ability_key.capitalize()}) +{proficiency} (Prof)")
        if bonuses.get('dc_reduction'):
            results.append(f"DC Reduced: -{bonuses['dc_reduction']} (gear)")
        results.append(f"Total: {total} vs DC {dc}")
        results.append("")

        damage_taken = 0
        exhaustion_gained = 0
        xp_gained = self.current_hazard.get('xp', 0)

        if success:
            results.append("SUCCESS!")
            success_effect = self.current_hazard.get('success_effect') or 'No effect'
            results.append(success_effect)
        else:
            results.append("FAILURE!")
            failure_effect = self.current_hazard.get('failure_effect') or 'Unknown effect'
            results.append(failure_effect)

            if 'exhaustion' in failure_effect.lower():
                import re
                exhaustion_match = re.search(r'(\d+)\s+exhaustion', failure_effect.lower())
                if exhaustion_match:
                    exhaustion_gained = int(exhaustion_match.group(1))
                else:
                    exhaustion_gained = 1

                # Apply exhaustion via ConditionManager
                character_id = self.character_data.get('id')
                if character_id:
                    try:
                        from src.talekeeper.services.condition_manager import ConditionManager
                        condition_manager = ConditionManager()

                        condition_manager._add_exhaustion_level(character_id, exhaustion_gained, f"Hazard: {self.current_hazard.get('name')}")
                        current_level = condition_manager.get_exhaustion_level(character_id)

                        results.append(f"Exhaustion Gained: {exhaustion_gained} level(s) (now level {current_level})")
                    except Exception as e:
                        print(f"[HazardWidget] Error applying exhaustion: {e}")
                        results.append(f"Exhaustion Gained: {exhaustion_gained} level(s)")
                else:
                    results.append(f"Exhaustion Gained: {exhaustion_gained} level(s)")

            if self.current_hazard.get('damage_avg'):
                damage = self.current_hazard['damage_avg']
                damage_reduction = bonuses.get('damage_reduction', 0)
                damage_taken = max(0, damage - damage_reduction)

                if bonuses.get('damage_cap_2d6'):
                    capped_damage = min(damage_taken, 12)
                    if capped_damage < damage_taken:
                        results.append(f"Damage Capped: {damage_taken} -> {capped_damage} (Climber's Kit limits to 2d6)")
                        damage_taken = capped_damage
                    else:
                        results.append(f"Damage (already below cap): {damage_taken}")
                elif damage_reduction > 0:
                    results.append(f"Damage Reduced: {damage} - {damage_reduction} (gear) = {damage_taken}")
                else:
                    results.append(f"Damage Taken: {damage_taken}")

        if self.selected_gear:
            gear_names = [str(g) for g in self.selected_gear if g]
            results.append(f"\nGear Used: {', '.join(gear_names)}")

        results.append(f"\nXP Gained: {xp_gained}")

        results_text = '\n'.join(str(r) for r in results if r is not None)
        self.results_text.setPlainText(results_text)

        roll_details = []
        roll_details.append(f"{'[Advantage] ' if has_advantage else ''}Rolled {roll} + {ability_mod + proficiency} = {total} vs DC {dc}")
        if success:
            roll_details.append("Success - No damage")
        else:
            effect_parts = []
            if damage_taken > 0:
                effect_parts.append(f"{damage_taken} damage")
            if exhaustion_gained > 0:
                effect_parts.append(f"{exhaustion_gained} exhaustion")
            if effect_parts:
                roll_details.append(f"Failed - {', '.join(effect_parts)}")
            else:
                roll_details.append("Failed - No immediate effect")
        if self.selected_gear:
            gear_names = [str(g) for g in self.selected_gear if g]
            roll_details.append(f"Gear: {', '.join(gear_names)}")

        roll_summary = ' | '.join(roll_details)
        self.hazard_completed.emit(success, xp_gained, damage_taken, exhaustion_gained, roll_summary)