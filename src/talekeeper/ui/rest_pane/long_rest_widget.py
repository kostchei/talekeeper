# core
# category: core
from typing import Dict, Optional, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QButtonGroup, QFrame,
                             QScrollArea, QMessageBox, QSizePolicy)
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
        self.current_gold = 0.0
        self.current_hp = 0
        self.max_hp = 0

        if parent is None:
            self.setWindowTitle("Long Rest")
            self.setMinimumSize(820, 720)
            self.resize(960, 760)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Expanding)
            self.setMinimumSize(720, 520)

        self._setup_ui()
        self._refresh_character_snapshot()
        self._update_character_status()
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
        self.lifestyle_layout.setSpacing(12)
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

    def _refresh_character_snapshot(self):
        status = self.rest_service.get_character_rest_status(self.character_data['id'])
        self.current_hp = int(status.get('current_hp', 0))
        self.max_hp = int(status.get('max_hp', max(1, self.current_hp)))
        self.current_gold = float(self.rest_service.get_character_gold(self.character_data['id']))

        # Keep the upstream character dict reasonably current for any listeners.
        self.character_data['hit_points_current'] = self.current_hp
        self.character_data['hit_points_max'] = self.max_hp
        self.character_data['gold'] = self.current_gold

    def _load_settlement_data(self):
        settlement_data = self.name_service.get_or_create_settlement_names(
            self.character_data['id'], self.hex_q, self.hex_r
        )

        if not settlement_data:
            self._show_wilderness_rest()
            return

        settlement_type = settlement_data.get('settlement_type') or 'empty'
        settlement_name = settlement_data.get('settlement_name')
        population = settlement_data.get('population', 0)

        if settlement_type == 'empty':
            self._show_wilderness_rest()
            return

        settlement_type_display = self._format_settlement_type(settlement_type)
        population_display = population if population and population > 0 else 'None'

        if settlement_name:
            display_name = settlement_name
        else:
            display_name = (
                f"Unnamed {settlement_type_display}"
                if settlement_type_display != 'Unknown'
                else "Unnamed Settlement"
            )

        self.settlement_info_label.setText(
            f"{display_name}\n"
            f"{settlement_type_display} | Population: {population_display}"
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
        self.selected_lifestyle = None
        for i in reversed(range(self.lifestyle_layout.count())):
            widget = self.lifestyle_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self._on_lifestyle_selected)

        safe_selection_index: Optional[int] = None

        for idx, option in enumerate(self.lifestyle_options):
            radio_button = self._create_lifestyle_option(option, idx)
            self.lifestyle_layout.addWidget(radio_button)
            hazard = option.get('hazard_chance', 0.0)
            if safe_selection_index is None and (hazard is None or hazard <= 0.0):
                safe_selection_index = idx

        if self.lifestyle_options:
            self.lifestyle_layout.addStretch()

        if not self.lifestyle_options:
            self.rest_button.setEnabled(False)
            self.rest_button.setText("Take Long Rest")
            return

        default_index = safe_selection_index if safe_selection_index is not None else 0
        default_button = self.button_group.button(default_index)
        if default_button:
            default_button.setChecked(True)
            self._on_lifestyle_selected(default_button)

    def _create_lifestyle_option(self, option: Dict, index: int) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(6)

        radio = QRadioButton()
        self.button_group.addButton(radio, index)

        header_layout = QHBoxLayout()

        lifestyle_name = option['lifestyle'].capitalize()
        cost_text = f"{option['cost_gp']:.2f} gp" if option['cost_gp'] > 0 else "Free"

        title_label = QLabel(f"{lifestyle_name} \u2013 {cost_text}")
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
        desc_label.setStyleSheet("color: #d8d8d8; margin-left: 32px;")
        container_layout.addWidget(desc_label)

        location_label = QLabel(f"Location: {option.get('location', 'Unknown')}")
        location_label.setStyleSheet("color: #b5b5b5; font-style: italic; margin-left: 32px;")
        container_layout.addWidget(location_label)

        hazard_chance = option.get('hazard_chance', 0.0)
        if hazard_chance:
            risk_label = QLabel(f"Rest risk: {int(hazard_chance * 100)}% chance of trouble.")
            risk_label.setStyleSheet(
                "color: #d8b25c; "
                "margin-left: 32px; "
                "font-style: italic; "
                "font-size: 11px;"
            )
            container_layout.addWidget(risk_label)

        container.setLayout(container_layout)

        neutral_palette = {
            'wretched': ('#272727', '#4f4f4f'),
            'squalid': ('#282828', '#575757'),
            'poor': ('#2c3034', '#49616c'),
            'modest': ('#2d3339', '#567284'),
            'comfortable': ('#303741', '#6c879e'),
            'wealthy': ('#343b48', '#7f97b1')
        }

        bg_color, border_color = neutral_palette.get(option['lifestyle'], ('#2a2a2a', '#535353'))

        container.setStyleSheet(
            f"QWidget {{ "
            f"  background-color: {bg_color}; "
            f"  border: 1px solid {border_color}; "
            f"  border-radius: 8px; "
            f"}} "
            "QRadioButton { background-color: transparent; } "
            "QLabel { background-color: transparent; border: none; }"
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
        max_hp = self.max_hp if self.max_hp else max(1, self.current_hp)
        status_lines = [
            "Character Status:",
            f"HP: {self.current_hp} / {max_hp}   |   Gold: {self.current_gold:.2f} gp",
            ""
        ]

        if self.current_hp < max_hp:
            status_lines.append(f"Long rest will restore {max_hp - self.current_hp} HP")
        else:
            status_lines.append("You are already at full HP.")

        self.character_status_label.setText("\n".join(status_lines))

    def _on_lifestyle_selected(self, button):
        index = self.button_group.id(button)
        if 0 <= index < len(self.lifestyle_options):
            self.selected_lifestyle = self.lifestyle_options[index]
            self.rest_button.setEnabled(True)

            cost = self.selected_lifestyle['cost_gp']
            current_gold = self.current_gold

            if cost - current_gold > 1e-6:
                self.rest_button.setEnabled(False)
                self.rest_button.setText(f"Need {cost:.2f} gp (You have {current_gold:.2f} gp)")
            else:
                if cost > 0:
                    self.rest_button.setText(f"Take Long Rest ({cost:.2f} gp)")
                else:
                    self.rest_button.setText("Take Long Rest")

    def _on_rest_clicked(self):
        if not self.selected_lifestyle:
            return

        cost = self.selected_lifestyle['cost_gp']
        lifestyle = self.selected_lifestyle['lifestyle']

        current_gold = self.current_gold
        if cost - current_gold > 1e-6:
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

        self._refresh_character_snapshot()
        self._update_character_status()

        # Check for ration consumption (wretched/wilderness rests)
        ration_result = None
        if lifestyle == 'wretched':
            ration_result = self._handle_ration_requirement()
            if ration_result and ration_result.get('cancelled'):
                return  # User cancelled the rest

        triggered, event_type, event_data = self.rest_service.check_hazard_trigger(lifestyle)

        if triggered:
            self._handle_hazard_event(event_type, event_data, lifestyle, cost, ration_result)
        else:
            self._complete_rest_safely(lifestyle, cost, ration_result)

    def _handle_ration_requirement(self) -> Dict:
        """
        Handle ration consumption requirement for wretched rests.

        Returns:
            Dict with ration consumption and CON save results, or None
        """
        ration_check = self.rest_service.check_and_consume_ration(self.character_data['id'])

        if ration_check['has_ration']:
            QMessageBox.information(
                self,
                "Ration Consumed",
                "You consume 1 day's worth of rations to sustain yourself during your rest."
            )
            return {'consumed_ration': True, 'con_save_needed': False}

        # No rations - need to make a CON save
        save_result = self.rest_service.make_constitution_save(self.character_data['id'], dc=10)

        if save_result['success']:
            QMessageBox.information(
                self,
                "Survived Without Food",
                f"You have no rations!\n\n"
                f"Constitution Save: d20({save_result['roll']}) + {save_result['modifier']} = {save_result['total']}\n"
                f"DC: {save_result['dc']}\n\n"
                f"Despite your hunger, you manage to endure the night without food."
            )
            return {
                'consumed_ration': False,
                'con_save_needed': True,
                'con_save_success': True,
                'save_result': save_result
            }
        else:
            # Failed save - add exhaustion
            exhaustion_result = self.rest_service.add_exhaustion_level(self.character_data['id'], 1)

            QMessageBox.warning(
                self,
                "Exhaustion from Starvation",
                f"You have no rations!\n\n"
                f"Constitution Save: d20({save_result['roll']}) + {save_result['modifier']} = {save_result['total']}\n"
                f"DC: {save_result['dc']} - FAILED\n\n"
                f"The lack of food takes its toll.\n"
                f"You gain 1 level of Exhaustion (now level {exhaustion_result.get('new_level', 1)})."
            )
            return {
                'consumed_ration': False,
                'con_save_needed': True,
                'con_save_success': False,
                'save_result': save_result,
                'exhaustion_added': True,
                'exhaustion_level': exhaustion_result.get('new_level', 1)
            }

    def _handle_hazard_event(self, event_type: str, event_data: Dict, lifestyle: str, cost: float, ration_result: Dict = None):
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
                lambda result: self._on_hazard_resolved(result, lifestyle, cost, ration_result)
            )

            event_widget.exec()

    def _on_hazard_resolved(self, result: Dict, lifestyle: str, cost: float, ration_result: Dict = None):
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

        # Add ration info to message if applicable
        if ration_result:
            if ration_result.get('consumed_ration'):
                message += "\n\n1 ration consumed during rest."
            elif ration_result.get('exhaustion_added'):
                message += f"\n\nExhaustion gained from lack of food (Level {ration_result['exhaustion_level']})."

        QMessageBox.information(
            self,
            "Rest Complete",
            f"{message}\n\n"
            f"HP Restored: {rest_result['hp_restored']}\n"
            f"Hit Dice Restored: {rest_result['hit_dice_restored']}"
        )

        self._refresh_character_snapshot()

        self.rest_completed.emit({
            'lifestyle': lifestyle,
            'cost': cost,
            'hazard_triggered': True,
            'hazard_result': result,
            'rest_result': rest_result
        })

        self.close()

    def _complete_rest_safely(self, lifestyle: str, cost: float, ration_result: Dict = None):
        self.rest_service.record_rest(
            self.character_data['id'], self.hex_q, self.hex_r,
            lifestyle, cost, False, None, None
        )

        rest_result = self.rest_service.apply_long_rest_benefits(self.character_data['id'])

        # Build message with ration info if applicable
        message_parts = []
        if lifestyle == 'wretched':
            message_parts.append("You rest in the wilderness.")
        else:
            message_parts.append(f"You rest peacefully in {lifestyle.capitalize()} accommodations.")

        if ration_result:
            if ration_result.get('consumed_ration'):
                message_parts.append("\n1 ration consumed.")
            elif ration_result.get('exhaustion_added'):
                message_parts.append(f"\nExhaustion gained from lack of food (Level {ration_result['exhaustion_level']}).")

        message_parts.append(f"\nHP Restored: {rest_result['hp_restored']}")
        message_parts.append(f"Hit Dice Restored: {rest_result['hit_dice_restored']}")
        message_parts.append("\nYou wake ready for adventure.")

        QMessageBox.information(
            self,
            "Rest Complete",
            "\n".join(message_parts)
        )

        self._refresh_character_snapshot()

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
