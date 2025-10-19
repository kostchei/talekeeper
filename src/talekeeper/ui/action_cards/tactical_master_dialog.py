# core
# category: core
"""
Tactical Master Dialog for Fighter Level 9+

Allows Fighter to swap weapon mastery property to Push, Sap, or Slow on a per-attack basis.
D&D 2024 Fighter Level 9 feature.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QButtonGroup, QRadioButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class TacticalMasterDialog(QDialog):
    """
    Dialog for choosing Tactical Master mastery override.

    Signals:
        mastery_chosen: Emits chosen mastery type ('original', 'push', 'sap', 'slow')
    """

    mastery_chosen = pyqtSignal(str)

    def __init__(self, weapon_name: str, original_mastery: str, parent=None):
        super().__init__(parent)
        self.weapon_name = weapon_name
        self.original_mastery = original_mastery
        self.selected_mastery = original_mastery.lower()

        self.setWindowTitle("Tactical Master")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("Tactical Master")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        info_label = QLabel(
            f"<b>Weapon:</b> {self.weapon_name}<br>"
            f"<b>Original Mastery:</b> {self.original_mastery}<br><br>"
            "Choose mastery property for this attack:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self.button_group = QButtonGroup()

        original_radio = QRadioButton(f"{self.original_mastery} (Weapon's Normal Mastery)")
        original_radio.setChecked(True)
        original_radio.toggled.connect(lambda: self._on_selection_changed('original'))
        self.button_group.addButton(original_radio)
        layout.addWidget(original_radio)

        original_desc = self._get_mastery_description(self.original_mastery)
        original_desc_label = QLabel(f"   {original_desc}")
        original_desc_label.setWordWrap(True)
        original_desc_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(original_desc_label)

        layout.addSpacing(10)

        tactical_label = QLabel("<b>Tactical Master Options:</b>")
        layout.addWidget(tactical_label)

        for mastery_name in ['Push', 'Sap', 'Slow']:
            radio = QRadioButton(mastery_name)
            radio.toggled.connect(lambda checked, m=mastery_name.lower():
                                self._on_selection_changed(m) if checked else None)
            self.button_group.addButton(radio)
            layout.addWidget(radio)

            desc_label = QLabel(f"   {self._get_mastery_description(mastery_name)}")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray; font-size: 10pt;")
            layout.addWidget(desc_label)

        layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumWidth(100)
        confirm_btn.clicked.connect(self._on_confirm)
        button_layout.addWidget(confirm_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _get_mastery_description(self, mastery: str) -> str:
        """Get description for mastery type."""
        descriptions = {
            'Push': 'Push target up to 10 feet away (Large or smaller)',
            'Sap': 'Target has disadvantage on its next attack roll',
            'Slow': 'Reduce target\'s speed by 10 feet until start of your next turn',
            'Graze': 'Deal ability modifier damage on miss',
            'Cleave': 'Attack a second creature within 5 feet',
            'Nick': 'Light weapon extra attack as part of Attack action',
            'Topple': 'Target makes CON save or falls prone',
            'Vex': 'Gain advantage on next attack against this target'
        }
        return descriptions.get(mastery, f'{mastery} mastery property')

    def _on_selection_changed(self, mastery: str):
        """Handle radio button selection."""
        self.selected_mastery = mastery

    def _on_confirm(self):
        """Confirm selection and close dialog."""
        self.mastery_chosen.emit(self.selected_mastery)
        self.accept()

    def get_selected_mastery(self) -> str:
        """Get the selected mastery type."""
        return self.selected_mastery


def show_tactical_master_dialog(weapon_name: str, original_mastery: str, parent=None) -> str:
    """
    Show tactical master dialog and return selected mastery.

    Args:
        weapon_name: Name of weapon being used
        original_mastery: Weapon's normal mastery property
        parent: Parent widget

    Returns:
        Selected mastery type ('original', 'push', 'sap', 'slow') or original if cancelled
    """
    dialog = TacticalMasterDialog(weapon_name, original_mastery, parent)
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        return dialog.get_selected_mastery()
    else:
        return 'original'