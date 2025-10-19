# core
# category: core
from typing import Dict, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import random

from talekeeper.services.long_rest_service import LongRestService


class EventResolutionWidget(QDialog):

    event_resolved = pyqtSignal(dict)

    def __init__(self, event_type: str, event_data: Dict, character_data: Dict,
                 rest_service: LongRestService, parent=None):
        super().__init__(parent)
        self.event_type = event_type
        self.event_data = event_data
        self.character_data = character_data
        self.rest_service = rest_service

        self.save_rolled = False
        self.save_result = None

        self.setWindowTitle("Event!")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setMaximumSize(700, 600)

        self._setup_ui()
        self._display_event()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(self.title_label)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider1)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(11)
        self.description_label.setFont(desc_font)
        self.description_label.setStyleSheet(
            "background-color: #2a2a2a; "
            "border: 1px solid #555; "
            "border-radius: 4px; "
            "padding: 15px; "
            "color: #e0e0e0;"
        )
        layout.addWidget(self.description_label)

        self.save_info_label = QLabel()
        self.save_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_info_label.setWordWrap(True)
        save_font = QFont()
        save_font.setPointSize(10)
        save_font.setBold(True)
        self.save_info_label.setFont(save_font)
        self.save_info_label.setStyleSheet(
            "background-color: #1a1a2a; "
            "border: 2px solid #4a90e2; "
            "border-radius: 4px; "
            "padding: 10px; "
            "color: #4a90e2;"
        )
        layout.addWidget(self.save_info_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        self.result_text.setStyleSheet(
            "background-color: #1a1a1a; "
            "border: 1px solid #444; "
            "border-radius: 4px; "
            "padding: 10px; "
            "color: #e0e0e0; "
            "font-size: 11px;"
        )
        self.result_text.setVisible(False)
        layout.addWidget(self.result_text)

        layout.addStretch()

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider2)

        button_layout = QHBoxLayout()

        self.action_button = QPushButton("Roll Save")
        self.action_button.setMinimumHeight(40)
        self.action_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #ff6b6b; "
            "  color: white; "
            "  border: none; "
            "  border-radius: 4px; "
            "  padding: 10px; "
            "  font-size: 14px; "
            "  font-weight: bold; "
            "} "
            "QPushButton:hover { background-color: #ff5252; }"
        )
        self.action_button.clicked.connect(self._on_action_clicked)
        button_layout.addWidget(self.action_button)

        self.continue_button = QPushButton("Continue to Rest")
        self.continue_button.setMinimumHeight(40)
        self.continue_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #4a90e2; "
            "  color: white; "
            "  border: none; "
            "  border-radius: 4px; "
            "  padding: 10px; "
            "  font-size: 14px; "
            "  font-weight: bold; "
            "} "
            "QPushButton:hover { background-color: #357abd; }"
        )
        self.continue_button.clicked.connect(self._on_continue_clicked)
        self.continue_button.setVisible(False)
        button_layout.addWidget(self.continue_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _display_event(self):
        if self.event_type == 'hazard':
            self._display_hazard()
        else:
            self._display_encounter()

    def _display_hazard(self):
        hazard_name = self.event_data.get('name', 'Unknown Hazard')
        description = self.event_data.get('description', 'Something dangerous happens!')
        save_ability = self.event_data.get('save_ability', 'dexterity')
        dc = self.event_data.get('dc', 12)

        self.title_label.setText(f"HAZARD: {hazard_name}")
        self.description_label.setText(description)

        ability_name = save_ability.capitalize()
        modifier = self._get_ability_modifier(save_ability)
        modifier_text = f"+{modifier}" if modifier >= 0 else str(modifier)

        self.save_info_label.setText(
            f"Make a DC {dc} {ability_name} saving throw\n"
            f"Your modifier: {modifier_text}"
        )

    def _display_encounter(self):
        encounter_name = self.event_data.get('name', 'Unknown Encounter')
        description = self.event_data.get('description', 'Something approaches!')

        self.title_label.setText(f"ENCOUNTER: {encounter_name}")
        self.description_label.setText(description)
        self.save_info_label.setText("This encounter requires resolution before you can rest.")

        self.action_button.setText("Resolve Encounter")

    def _get_ability_modifier(self, ability: str) -> int:
        ability_score_map = {
            'strength': 'strength',
            'dexterity': 'dexterity',
            'constitution': 'constitution',
            'intelligence': 'intelligence',
            'wisdom': 'wisdom',
            'charisma': 'charisma'
        }

        score_key = ability_score_map.get(ability.lower(), 'dexterity')
        score = self.character_data.get(score_key, 10)
        modifier = (score - 10) // 2

        return modifier

    def _on_action_clicked(self):
        if self.event_type == 'hazard':
            self._roll_saving_throw()
        else:
            self._resolve_encounter()

    def _roll_saving_throw(self):
        save_ability = self.event_data.get('save_ability', 'dexterity')
        dc = self.event_data.get('dc', 12)
        modifier = self._get_ability_modifier(save_ability)

        roll = random.randint(1, 20)
        total = roll + modifier

        success = total >= dc

        result_text = f"D20 Roll: {roll}\n"
        result_text += f"Modifier: {'+' if modifier >= 0 else ''}{modifier}\n"
        result_text += f"Total: {total} vs DC {dc}\n\n"

        if success:
            result_text += "SUCCESS! You avoid the worst of it.\n"
            result_text += "No damage or effects suffered."
            self.save_result = {
                'event_name': self.event_data.get('name'),
                'save_success': True,
                'roll': roll,
                'total': total,
                'dc': dc,
                'effects': {}
            }
        else:
            result_text += "FAILURE! You suffer the hazard's effects.\n\n"
            effects = self._apply_hazard_effects()
            result_text += self._format_effects(effects)
            self.save_result = {
                'event_name': self.event_data.get('name'),
                'save_success': False,
                'roll': roll,
                'total': total,
                'dc': dc,
                'effects': effects
            }

        self.result_text.setPlainText(result_text)
        self.result_text.setVisible(True)

        self.action_button.setVisible(False)
        self.continue_button.setVisible(True)

        self.save_rolled = True

    def _apply_hazard_effects(self) -> Dict:
        effects = {}
        on_fail = self.event_data.get('on_fail', '')

        if 'damage' in on_fail:
            damage_formula = self.event_data.get('damage_formula', '1d6')
            damage_type = self.event_data.get('damage_type', 'untyped')
            damage = self.rest_service.roll_damage(damage_formula)

            damage_result = self.rest_service.apply_damage(
                self.character_data['id'], damage, damage_type
            )

            effects['damage'] = damage
            effects['damage_type'] = damage_type
            effects['new_hp'] = damage_result.get('new_hp', 0)

        if 'condition' in on_fail:
            condition = self.event_data.get('condition', 'unknown')
            duration_hours = 8

            if 'duration_hours' in self.event_data:
                duration_hours = self.event_data['duration_hours']
            elif 'duration_days' in self.event_data:
                days_formula = self.event_data['duration_days']
                days = self.rest_service.roll_damage(days_formula)
                duration_hours = days * 24

            effects['condition'] = condition
            effects['duration_hours'] = duration_hours

        if 'exhaustion' in on_fail or 'exhaustion_levels' in self.event_data:
            exhaustion_levels = self.event_data.get('exhaustion_levels', 1)
            effects['exhaustion'] = exhaustion_levels

        if 'lose_gold' in on_fail or 'gold_formula' in self.event_data:
            gold_formula = self.event_data.get('gold_formula', '1d10')
            gold_result = self.rest_service.apply_gold_loss(
                self.character_data['id'], gold_formula
            )
            effects['gold_lost'] = gold_result.get('gold_lost', 0)

        if 'items' in on_fail or 'items_lost' in self.event_data:
            items_lost_formula = self.event_data.get('items_lost', '1')
            if 'd' in str(items_lost_formula):
                items_count = self.rest_service.roll_damage(items_lost_formula)
            else:
                items_count = int(items_lost_formula)
            effects['items_lost'] = items_count

        return effects

    def _format_effects(self, effects: Dict) -> str:
        lines = []

        if 'damage' in effects:
            lines.append(f"Damage: {effects['damage']} {effects.get('damage_type', '')} damage")
            lines.append(f"New HP: {effects.get('new_hp', 0)}")

        if 'gold_lost' in effects:
            lines.append(f"Gold Lost: {effects['gold_lost']} gp")

        if 'condition' in effects:
            lines.append(f"Condition: {effects['condition']} ({effects.get('duration_hours', 0)} hours)")

        if 'exhaustion' in effects:
            lines.append(f"Exhaustion: {effects['exhaustion']} level(s) gained")

        if 'items_lost' in effects:
            lines.append(f"Items Lost: {effects['items_lost']} random items")

        return "\n".join(lines) if lines else "No effects"

    def _resolve_encounter(self):
        pass

    def _on_continue_clicked(self):
        if self.save_result:
            self.event_resolved.emit(self.save_result)
        self.accept()
