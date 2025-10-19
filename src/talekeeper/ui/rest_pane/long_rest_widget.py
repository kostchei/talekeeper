from typing import Dict, Optional, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QButtonGroup, QFrame,
                             QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from talekeeper.services.long_rest_service import LongRestService
from talekeeper.services.settlement_name_service import SettlementNameService


class LongRestWidget(QWidget):

    rest_completed = pyqtSignal(dict)
    rest_cancelled = pyqtSignal()
    encounter_triggered = pyqtSignal(dict)

    def __init__(self, db_path: str, character_data: Dict, hex_q: int, hex_r: int, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.character_data = character_data
        self.hex_q = hex_q
        self.hex_r = hex_r

        self.rest_service = LongRestService(db_path)
        self.name_service = SettlementNameService(db_path)

        self.selected_lifestyle = None
        self.lifestyle_options = []

        self.setWindowTitle("Long Rest")
        self.setMinimumSize(600, 700)
        self.setMaximumSize(800, 900)

        self._setup_ui()
        self._load_settlement_data()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.header_label = QLabel("LONG REST")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        layout.addWidget(self.header_label)

        self.settlement_info_label = QLabel()
        self.settlement_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settlement_info_label.setStyleSheet(
            "background-color: #2a2a2a; "
            "color: #e0e0e0; "
            "border: 1px solid #555; "
            "border-radius: 4px; "
            "padding: 10px; "
            "margin: 5px 0px;"
        )
        layout.addWidget(self.settlement_info_label)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider1)

        lifestyle_label = QLabel("Available Accommodations:")
        lifestyle_font = QFont()
        lifestyle_font.setPointSize(12)
        lifestyle_font.setBold(True)
        lifestyle_label.setFont(lifestyle_font)
        layout.addWidget(lifestyle_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.lifestyle_container = QWidget()
        self.lifestyle_layout = QVBoxLayout()
        self.lifestyle_layout.setSpacing(10)
        self.lifestyle_container.setLayout(self.lifestyle_layout)
        scroll_area.setWidget(self.lifestyle_container)

        layout.addWidget(scroll_area, 1)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider2)

        self.character_status_label = QLabel()
        self.character_status_label.setStyleSheet(
            "background-color: #1a1a1a; "
            "border: 1px solid #444; "
            "border-radius: 4px; "
            "padding: 8px; "
            "color: #e0e0e0;"
        )
        layout.addWidget(self.character_status_label)
        self._update_character_status()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.rest_button = QPushButton("Take Long Rest")
        self.rest_button.setMinimumHeight(40)
        self.rest_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #4a90e2; "
            "  color: white; "
            "  border: none; "
            "  border-radius: 4px; "
            "  padding: 10px; "
            "  font-size: 14px; "
            "  font-weight: bold; "
            "} "
            "QPushButton:hover { background-color: #357abd; } "
            "QPushButton:disabled { background-color: #555; color: #999; }"
        )
        self.rest_button.clicked.connect(self._on_rest_clicked)
        self.rest_button.setEnabled(False)
        button_layout.addWidget(self.rest_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(40)
        cancel_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #666; "
            "  color: white; "
            "  border: none; "
            "  border-radius: 4px; "
            "  padding: 10px; "
            "  font-size: 14px; "
            "} "
            "QPushButton:hover { background-color: #555; }"
        )
        cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_settlement_data(self):
        settlement_data = self.name_service.get_or_create_settlement_names(
            self.character_data['id'], self.hex_q, self.hex_r
        )

        if not settlement_data:
            self._show_wilderness_rest()
            return

        settlement_type = settlement_data.get('settlement_type', 'empty')
        settlement_name = settlement_data.get('settlement_name', 'The Wilderness')
        population = settlement_data.get('population', 0)

        if settlement_type == 'empty' or not settlement_name:
            settlement_name = "The Wilderness"
            population = 0

        self.settlement_info_label.setText(
            f"{settlement_name}\n"
            f"{self._format_settlement_type(settlement_type)} | "
            f"Population: {population if population > 0 else 'None'}"
        )

        self.lifestyle_options = self.rest_service.get_available_lifestyles(
            self.character_data['id'], self.hex_q, self.hex_r
        )

        self._populate_lifestyle_options()

    def _show_wilderness_rest(self):
        self.settlement_info_label.setText("The Wilderness\nNo Settlement | Population: None")
        self.lifestyle_options = [{
            'lifestyle': 'wretched',
            'cost_gp': 0.0,
            'description': 'Camp in the wilderness, exposed to the elements.',
            'hazard_chance': 0.5,
            'warning': 'DANGER: 50% chance of encounter or hazard',
            'location': 'Sleeping rough under the stars'
        }]
        self._populate_lifestyle_options()

    def _populate_lifestyle_options(self):
        for i in reversed(range(self.lifestyle_layout.count())):
            widget = self.lifestyle_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self._on_lifestyle_selected)

        for idx, option in enumerate(self.lifestyle_options):
            radio_button = self._create_lifestyle_option(option, idx)
            self.lifestyle_layout.addWidget(radio_button)

        if self.lifestyle_options:
            self.lifestyle_layout.addStretch()

    def _create_lifestyle_option(self, option: Dict, index: int) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(5)

        radio = QRadioButton()
        self.button_group.addButton(radio, index)

        header_layout = QHBoxLayout()

        lifestyle_name = option['lifestyle'].capitalize()
        cost_text = f"{option['cost_gp']:.2f} gp" if option['cost_gp'] > 0 else "Free"

        title_label = QLabel(f"{lifestyle_name} - {cost_text}")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)

        header_layout.addWidget(radio)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        container_layout.addLayout(header_layout)

        desc_label = QLabel(option['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #cccccc; margin-left: 25px;")
        container_layout.addWidget(desc_label)

        location_label = QLabel(f"Location: {option.get('location', 'Unknown')}")
        location_label.setStyleSheet("color: #aaaaaa; font-style: italic; margin-left: 25px;")
        container_layout.addWidget(location_label)

        if option.get('warning'):
            warning_label = QLabel(f"⚠ {option['warning']}")
            warning_label.setStyleSheet(
                "color: #ff6b6b; "
                "background-color: #3a1a1a; "
                "border: 1px solid #ff6b6b; "
                "border-radius: 3px; "
                "padding: 5px; "
                "margin-left: 25px; "
                "margin-top: 5px; "
                "font-weight: bold;"
            )
            container_layout.addWidget(warning_label)

        container.setLayout(container_layout)

        if option['lifestyle'] in ['wretched', 'squalid']:
            bg_color = "#2a1a1a"
            border_color = "#ff6b6b"
        elif option['lifestyle'] in ['poor', 'modest']:
            bg_color = "#1a2a1a"
            border_color = "#6bff6b"
        else:
            bg_color = "#1a1a2a"
            border_color = "#6b6bff"

        container.setStyleSheet(
            f"QWidget {{ "
            f"  background-color: {bg_color}; "
            f"  border: 2px solid {border_color}; "
            f"  border-radius: 6px; "
            f"}} "
            f"QRadioButton {{ background-color: transparent; }} "
            f"QLabel {{ background-color: transparent; border: none; }}"
        )

        return container

    def _format_settlement_type(self, settlement_type: str) -> str:
        type_map = {
            'empty': 'Wilderness',
            'hamlet': 'Hamlet',
            'village': 'Village',
            'town_small': 'Small Town',
            'town_medium': 'Medium Town',
            'town_large': 'Large Town'
        }
        return type_map.get(settlement_type, 'Unknown')

    def _update_character_status(self):
        character = self.character_data
        current_hp = character.get('current_hp', 0)
        max_hp = character.get('max_hp', 1)
        gold = character.get('gold', 0)

        status_text = (
            f"Character Status:\n"
            f"HP: {current_hp} / {max_hp}   |   "
            f"Gold: {gold:.2f} gp"
        )

        if current_hp < max_hp:
            hp_restored = max_hp - current_hp
            status_text += f"\n\nLong rest will restore {hp_restored} HP"

        self.character_status_label.setText(status_text)

    def _on_lifestyle_selected(self, button):
        index = self.button_group.id(button)
        if 0 <= index < len(self.lifestyle_options):
            self.selected_lifestyle = self.lifestyle_options[index]
            self.rest_button.setEnabled(True)

            cost = self.selected_lifestyle['cost_gp']
            current_gold = self.character_data.get('gold', 0)

            if cost > current_gold:
                self.rest_button.setEnabled(False)
                self.rest_button.setText(f"Cannot Afford ({cost:.2f} gp needed)")
            else:
                self.rest_button.setText("Take Long Rest")

    def _on_rest_clicked(self):
        if not self.selected_lifestyle:
            return

        cost = self.selected_lifestyle['cost_gp']
        lifestyle = self.selected_lifestyle['lifestyle']

        current_gold = self.character_data.get('gold', 0)
        if cost > current_gold:
            QMessageBox.warning(
                self,
                "Insufficient Gold",
                f"You need {cost:.2f} gp but only have {current_gold:.2f} gp."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Rest",
            f"Take a long rest with {lifestyle.capitalize()} accommodations?\n\n"
            f"Cost: {cost:.2f} gp\n"
            f"Your gold after: {current_gold - cost:.2f} gp",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        success = self.rest_service.deduct_lifestyle_cost(self.character_data['id'], cost)

        if not success:
            QMessageBox.critical(
                self,
                "Payment Failed",
                "Failed to deduct gold. Please check your funds."
            )
            return

        self.character_data['gold'] = current_gold - cost

        triggered, event_type, event_data = self.rest_service.check_hazard_trigger(lifestyle)

        if triggered:
            self._handle_hazard_event(event_type, event_data, lifestyle, cost)
        else:
            self._complete_rest_safely(lifestyle, cost)

    def _handle_hazard_event(self, event_type: str, event_data: Dict, lifestyle: str, cost: float):
        if event_type == 'encounter':
            QMessageBox.information(
                self,
                "Trouble!",
                f"As you settle in to rest, trouble finds you!\n\n"
                f"{event_data['description']}\n\n"
                f"Your rest has been interrupted. You must resolve this encounter first."
            )

            self.rest_service.record_rest(
                self.character_data['id'], self.hex_q, self.hex_r,
                lifestyle, cost, True, event_type, event_data['name']
            )

            self.encounter_triggered.emit({
                'event_type': 'encounter',
                'event_data': event_data,
                'character_data': self.character_data,
                'hex_q': self.hex_q,
                'hex_r': self.hex_r
            })

            self.close()

        else:
            from talekeeper.ui.rest_pane.event_resolution_widget import EventResolutionWidget

            event_widget = EventResolutionWidget(
                event_type='hazard',
                event_data=event_data,
                character_data=self.character_data,
                rest_service=self.rest_service,
                parent=self
            )

            event_widget.event_resolved.connect(
                lambda result: self._on_hazard_resolved(result, lifestyle, cost)
            )

            event_widget.exec()

    def _on_hazard_resolved(self, result: Dict, lifestyle: str, cost: float):
        hazard_name = result.get('event_name', 'Unknown')
        save_success = result.get('save_success', False)

        if save_success:
            message = f"You successfully avoided the hazard!\n\nDespite the danger, you manage to complete your rest."
        else:
            effects = result.get('effects', {})
            effect_text = self._format_hazard_effects(effects)
            message = f"You suffered from the hazard.\n\n{effect_text}\n\nDespite the hardship, you manage to complete your rest."

        self.rest_service.record_rest(
            self.character_data['id'], self.hex_q, self.hex_r,
            lifestyle, cost, True, 'hazard', hazard_name
        )

        rest_result = self.rest_service.apply_long_rest_benefits(self.character_data['id'])

        QMessageBox.information(
            self,
            "Rest Complete",
            f"{message}\n\n"
            f"HP Restored: {rest_result['hp_restored']}\n"
            f"Hit Dice Restored: {rest_result['hit_dice_restored']}"
        )

        self.rest_completed.emit({
            'lifestyle': lifestyle,
            'cost': cost,
            'hazard_triggered': True,
            'hazard_result': result,
            'rest_result': rest_result
        })

        self.close()

    def _complete_rest_safely(self, lifestyle: str, cost: float):
        self.rest_service.record_rest(
            self.character_data['id'], self.hex_q, self.hex_r,
            lifestyle, cost, False, None, None
        )

        rest_result = self.rest_service.apply_long_rest_benefits(self.character_data['id'])

        QMessageBox.information(
            self,
            "Rest Complete",
            f"You rest peacefully in {lifestyle.capitalize()} accommodations.\n\n"
            f"HP Restored: {rest_result['hp_restored']}\n"
            f"Hit Dice Restored: {rest_result['hit_dice_restored']}\n\n"
            f"You wake refreshed and ready for adventure."
        )

        self.rest_completed.emit({
            'lifestyle': lifestyle,
            'cost': cost,
            'hazard_triggered': False,
            'rest_result': rest_result
        })

        self.close()

    def _format_hazard_effects(self, effects: Dict) -> str:
        lines = []

        if effects.get('damage'):
            lines.append(f"Damage: {effects['damage']} {effects.get('damage_type', '')} damage")

        if effects.get('gold_lost'):
            lines.append(f"Gold Lost: {effects['gold_lost']} gp")

        if effects.get('condition'):
            lines.append(f"Condition: {effects['condition']} for {effects.get('duration_hours', 0)} hours")

        if effects.get('exhaustion'):
            lines.append(f"Exhaustion: {effects['exhaustion']} level(s)")

        return "\n".join(lines) if lines else "No lasting effects"

    def _on_cancel_clicked(self):
        self.rest_cancelled.emit()
        self.close()
