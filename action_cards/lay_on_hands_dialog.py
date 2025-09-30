"""
Lay on Hands Dialog for Paladins

Allows Paladins to use their healing pool to restore HP or cure poison.
Per D&D 2024 rules: Bonus action, 5 points per paladin level pool, max 5 points per use.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QCheckBox, QGroupBox,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any


class LayOnHandsDialog(QDialog):
    """Dialog for using Lay on Hands healing ability."""

    # Signal emitted when healing is applied: (healing_points, cure_poison, target_id)
    healing_applied = pyqtSignal(int, bool, str)
    healing_cancelled = pyqtSignal()

    def __init__(self, parent=None, character_data: Dict[str, Any] = None,
                 current_pool: int = 0, max_pool: int = 0,
                 target_options: list = None):
        """
        Initialize Lay on Hands dialog.

        Args:
            parent: Parent widget
            character_data: Paladin character information
            current_pool: Current healing points available
            max_pool: Maximum healing pool
            target_options: List of possible healing targets [(id, name, current_hp, max_hp)]
        """
        super().__init__(parent)
        self.character_data = character_data or {}
        self.current_pool = current_pool
        self.max_pool = max_pool
        self.target_options = target_options or []
        self.selected_target = None
        self.healing_points = 1
        self.cure_poison = False

        self.setWindowTitle("Lay on Hands")
        self.setModal(True)
        self.setFixedWidth(450)

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Lay on Hands")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Channel divine energy to heal wounds or cure poison.\n"
            "Uses your healing pool (5 points per paladin level)."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Pool status
        pool_group = QGroupBox("Healing Pool")
        pool_layout = QVBoxLayout()

        self.pool_bar = QProgressBar()
        self.pool_bar.setMinimum(0)
        self.pool_bar.setMaximum(self.max_pool)
        self.pool_bar.setValue(self.current_pool)
        self.pool_bar.setFormat(f"{self.current_pool}/{self.max_pool} points")
        pool_layout.addWidget(self.pool_bar)

        pool_group.setLayout(pool_layout)
        layout.addWidget(pool_group)

        # Target selection
        if len(self.target_options) > 1:
            target_group = QGroupBox("Healing Target")
            target_layout = QVBoxLayout()

            for target_id, name, current_hp, max_hp in self.target_options:
                target_btn = QPushButton(f"{name} ({current_hp}/{max_hp} HP)")
                target_btn.setCheckable(True)
                target_btn.clicked.connect(lambda checked, tid=target_id: self.select_target(tid))
                target_layout.addWidget(target_btn)

            target_group.setLayout(target_layout)
            layout.addWidget(target_group)
        elif self.target_options:
            # Single target (self-healing)
            self.selected_target = self.target_options[0][0]
            target_info = self.target_options[0]
            target_label = QLabel(f"Healing: {target_info[1]} ({target_info[2]}/{target_info[3]} HP)")
            target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(target_label)

        # Healing options
        options_group = QGroupBox("Healing Options")
        options_layout = QVBoxLayout()

        # Healing points
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Healing Points:"))

        self.points_spin = QSpinBox()
        self.points_spin.setMinimum(1)
        self.points_spin.setMaximum(min(5, self.current_pool))  # Max 5 per use
        self.points_spin.setValue(1)
        self.points_spin.valueChanged.connect(self.update_healing_points)
        points_layout.addWidget(self.points_spin)

        points_layout.addWidget(QLabel("(Max 5 per use)"))
        points_layout.addStretch()
        options_layout.addLayout(points_layout)

        # Cure poison option
        self.poison_checkbox = QCheckBox("Cure Poison (5 points, no healing)")
        self.poison_checkbox.stateChanged.connect(self.update_poison_option)
        options_layout.addWidget(self.poison_checkbox)

        # Effect description
        self.effect_label = QLabel("Restores 1 Hit Point")
        self.effect_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        options_layout.addWidget(self.effect_label)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply Healing")
        self.apply_btn.clicked.connect(self.apply_healing)
        self.apply_btn.setDefault(True)
        button_layout.addWidget(self.apply_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_target(self, target_id: str):
        """Select a healing target."""
        self.selected_target = target_id

        # Update button states
        for i in range(self.layout().itemAt(3).widget().layout().count()):
            btn = self.layout().itemAt(3).widget().layout().itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(btn.property("target_id") == target_id)

    def update_healing_points(self, value: int):
        """Update healing points and effect description."""
        self.healing_points = value
        if not self.cure_poison:
            self.effect_label.setText(f"Restores {value} Hit Point{'s' if value > 1 else ''}")
        self.update_apply_button()

    def update_poison_option(self, state: int):
        """Update poison curing option."""
        self.cure_poison = state == Qt.CheckState.Checked.value

        if self.cure_poison:
            self.points_spin.setValue(5)
            self.points_spin.setEnabled(False)
            self.effect_label.setText("Removes Poisoned condition (no HP restored)")
            self.effect_label.setStyleSheet("font-weight: bold; color: #1976d2;")
        else:
            self.points_spin.setEnabled(True)
            self.points_spin.setMaximum(min(5, self.current_pool))
            self.effect_label.setText(f"Restores {self.healing_points} Hit Point{'s' if self.healing_points > 1 else ''}")
            self.effect_label.setStyleSheet("font-weight: bold; color: #2e7d32;")

        self.update_apply_button()

    def update_apply_button(self):
        """Update apply button availability."""
        points_needed = 5 if self.cure_poison else self.healing_points
        can_apply = (
            self.current_pool >= points_needed and
            (self.selected_target is not None or len(self.target_options) <= 1)
        )
        self.apply_btn.setEnabled(can_apply)

    def update_display(self):
        """Update the display with current values."""
        if hasattr(self, 'pool_bar'):
            self.pool_bar.setValue(self.current_pool)
            self.pool_bar.setFormat(f"{self.current_pool}/{self.max_pool} points")

        if hasattr(self, 'points_spin'):
            max_usable = min(5, self.current_pool)
            self.points_spin.setMaximum(max_usable)
            if self.points_spin.value() > max_usable:
                self.points_spin.setValue(max_usable)

        self.update_apply_button()

    def apply_healing(self):
        """Apply the healing and emit signal."""
        if not self.selected_target and self.target_options:
            self.selected_target = self.target_options[0][0]

        points_to_use = 5 if self.cure_poison else self.healing_points

        if self.current_pool >= points_to_use:
            self.healing_applied.emit(points_to_use, self.cure_poison, self.selected_target or "")
            self.accept()
        else:
            # This shouldn't happen due to button state, but safety check
            self.update_apply_button()

    def reject(self):
        """Handle dialog cancellation."""
        self.healing_cancelled.emit()
        super().reject()

    def get_healing_info(self) -> Dict[str, Any]:
        """Get the current healing configuration."""
        return {
            "target_id": self.selected_target,
            "healing_points": self.healing_points,
            "cure_poison": self.cure_poison,
            "points_cost": 5 if self.cure_poison else self.healing_points
        }