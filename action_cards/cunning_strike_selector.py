# core
# core
"""
Cunning Strike Selector UI Widget

Provides UI for selecting Cunning Strike effects with:
- Visual cost display
- Damage calculation preview
- Multi-selection support (level 11+)
- Context-sensitive enabling/disabling
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QCheckBox, QScrollArea, QWidget,
                             QFrame, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any, Optional

from services.cunning_strike_manager import CunningStrikeManager, CunningStrikeEffect


class CunningStrikeOptionWidget(QFrame):
    """Widget for a single Cunning Strike option"""

    toggled = pyqtSignal(str, bool)

    def __init__(self, option_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.option_data = option_data
        self.effect_id = option_data['effect']
        self.is_selected = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        self.checkbox = QCheckBox()
        self.checkbox.setEnabled(self.option_data['available'])
        self.checkbox.toggled.connect(self._on_toggled)
        layout.addWidget(self.checkbox)

        info_layout = QVBoxLayout()

        name_cost_layout = QHBoxLayout()

        name_label = QLabel(self.option_data['name'])
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_cost_layout.addWidget(name_label)

        name_cost_layout.addStretch()

        cost_label = QLabel(f"Cost: {self.option_data['dice_cost']}d6")
        cost_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        name_cost_layout.addWidget(cost_label)

        info_layout.addLayout(name_cost_layout)

        desc_label = QLabel(self.option_data['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(desc_label)

        if self.option_data['save_type'] != 'none':
            save_label = QLabel(f"Save: {self.option_data['save_type'].title()}")
            save_label.setStyleSheet("color: #6b9eff; font-size: 10px;")
            info_layout.addWidget(save_label)

        if not self.option_data['available']:
            unavailable_label = QLabel(f"⚠ {self.option_data['unavailable_reason']}")
            unavailable_label.setStyleSheet("color: #ff4444; font-size: 10px; font-weight: bold;")
            info_layout.addWidget(unavailable_label)

        layout.addLayout(info_layout)

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self._update_style()

    def _update_style(self):
        if not self.option_data['available']:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border: 2px solid #555;
                    border-radius: 5px;
                    opacity: 0.5;
                }
            """)
        elif self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a3a1a;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a1a1a;
                    border: 2px solid #444;
                    border-radius: 5px;
                }
                QFrame:hover {
                    border: 2px solid #666;
                }
            """)

    def _on_toggled(self, checked: bool):
        self.is_selected = checked
        self._update_style()
        self.toggled.emit(self.effect_id, checked)

    def set_enabled(self, enabled: bool):
        self.checkbox.setEnabled(enabled and self.option_data['available'])
        if not enabled:
            self.checkbox.setChecked(False)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        if self.option_data['available']:
            self.checkbox.setChecked(checked)


class CunningStrikeSelectorDialog(QDialog):
    """Dialog for selecting Cunning Strike effects"""

    effects_selected = pyqtSignal(list)

    def __init__(self, character_id: str, db_path: str = "talekeeper.db",
                 sneak_attack_eligible: bool = True, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.db_path = db_path
        self.sneak_attack_eligible = sneak_attack_eligible
        self.manager = CunningStrikeManager(db_path)

        self.option_widgets: Dict[str, CunningStrikeOptionWidget] = {}
        self.selected_effects: List[str] = []
        self.max_selections = 2 if self.manager.can_use_multiple_effects(character_id) else 1

        self._setup_ui()
        self._load_options()
        self._update_preview()

    def _setup_ui(self):
        self.setWindowTitle("Cunning Strike")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        if not self.sneak_attack_eligible:
            warning_label = QLabel("⚠ Sneak Attack not eligible this turn!")
            warning_label.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 14px; padding: 10px;")
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(warning_label)

            info_label = QLabel("Need advantage or an ally within 5ft of target")
            info_label.setStyleSheet("color: #888; font-size: 12px; padding-bottom: 10px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)

        title_label = QLabel("Select Cunning Strike Effects")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        selection_info = QLabel(
            f"Select up to {self.max_selections} effect(s). Each costs Sneak Attack dice."
        )
        selection_info.setStyleSheet("color: #888; padding: 5px 10px;")
        layout.addWidget(selection_info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        options_widget = QWidget()
        self.options_layout = QVBoxLayout(options_widget)
        self.options_layout.setSpacing(10)

        scroll.setWidget(options_widget)
        layout.addWidget(scroll)

        preview_group = QGroupBox("Damage Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("font-family: monospace; padding: 10px;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)

        self.effects_preview_label = QLabel()
        self.effects_preview_label.setStyleSheet("color: #888; padding: 5px 10px; font-size: 11px;")
        self.effects_preview_label.setWordWrap(True)
        preview_layout.addWidget(self.effects_preview_label)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self._clear_selection)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self.confirm_btn.clicked.connect(self._confirm_selection)
        self.confirm_btn.setEnabled(False)
        button_layout.addWidget(self.confirm_btn)

        layout.addLayout(button_layout)

    def _load_options(self):
        available_options = self.manager.get_available_cunning_strikes(self.character_id)

        for option_data in available_options:
            widget = CunningStrikeOptionWidget(option_data)
            widget.toggled.connect(self._on_option_toggled)
            widget.set_enabled(self.sneak_attack_eligible)
            self.options_layout.addWidget(widget)
            self.option_widgets[option_data['effect']] = widget

        self.options_layout.addStretch()

    def _on_option_toggled(self, effect_id: str, checked: bool):
        if checked:
            if len(self.selected_effects) >= self.max_selections:
                self.option_widgets[effect_id].set_checked(False)
                return
            self.selected_effects.append(effect_id)
        else:
            if effect_id in self.selected_effects:
                self.selected_effects.remove(effect_id)

        if len(self.selected_effects) >= self.max_selections:
            for effect, widget in self.option_widgets.items():
                if effect not in self.selected_effects:
                    widget.set_enabled(False)
        else:
            for widget in self.option_widgets.values():
                widget.set_enabled(self.sneak_attack_eligible)

        self._update_preview()

    def _update_preview(self):
        if not self.selected_effects:
            damage_calc = self.manager.calculate_sneak_attack_with_cost(
                self.character_id, []
            )
            self.preview_label.setText(
                f"Base Sneak Attack: {damage_calc['base_damage_string']}\n"
                f"No effects selected"
            )
            self.effects_preview_label.setText("")
            self.confirm_btn.setEnabled(False)
            return

        effects = [CunningStrikeEffect(eid) for eid in self.selected_effects]
        preview = self.manager.get_cunning_strike_preview(self.character_id, effects)

        preview_text = (
            f"Base Sneak Attack: {preview['base_sneak_attack']}\n"
            f"Dice Cost: {preview['dice_cost']}d6\n"
            f"Remaining Damage: {preview['remaining_damage']}\n"
            f"Save DC: {preview['save_dc']}"
        )
        self.preview_label.setText(preview_text)

        effects_text = "\n".join([
            f"• {eff['name']} ({eff['cost']}): {eff['condition'].title() if eff['condition'] else 'Movement'} "
            f"[{eff['save']} save, {eff['duration']}]"
            for eff in preview['effects']
        ])
        self.effects_preview_label.setText(effects_text)

        self.confirm_btn.setEnabled(True)

    def _clear_selection(self):
        self.selected_effects.clear()
        for widget in self.option_widgets.values():
            widget.set_checked(False)
            widget.set_enabled(self.sneak_attack_eligible)
        self._update_preview()

    def _confirm_selection(self):
        effects = [CunningStrikeEffect(eid) for eid in self.selected_effects]
        self.effects_selected.emit(effects)
        self.accept()

    def get_selected_effects(self) -> List[CunningStrikeEffect]:
        return [CunningStrikeEffect(eid) for eid in self.selected_effects]


class CunningStrikePreviewLabel(QLabel):
    """Compact label showing Cunning Strike cost on action cards"""

    def __init__(self, dice_cost: int, parent=None):
        super().__init__(parent)
        self.dice_cost = dice_cost
        self._update_text()

    def _update_text(self):
        self.setText(f"Cost: {self.dice_cost}d6")
        self.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-weight: bold;
                font-size: 10px;
                padding: 2px 5px;
                background-color: rgba(255, 107, 107, 0.2);
                border-radius: 3px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
