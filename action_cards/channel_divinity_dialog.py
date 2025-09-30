"""
Channel Divinity Dialog for Paladins

Allows Paladins to choose from available Channel Divinity options.
Per D&D 2024 rules: Action, 2 uses per short rest (3 at level 11+).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QGroupBox, QProgressBar, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any, List


class ChannelDivinityDialog(QDialog):
    """Dialog for choosing Channel Divinity options."""

    # Signal emitted when option is chosen: (option_name, option_data)
    channel_divinity_used = pyqtSignal(str, dict)
    channel_divinity_cancelled = pyqtSignal()

    def __init__(self, parent=None, character_data: Dict[str, Any] = None,
                 current_uses: int = 0, max_uses: int = 2,
                 available_options: List[Dict[str, Any]] = None):
        """
        Initialize Channel Divinity dialog.

        Args:
            parent: Parent widget
            character_data: Paladin character information
            current_uses: Current uses consumed
            max_uses: Maximum uses per rest
            available_options: List of available options with their data
        """
        super().__init__(parent)
        self.character_data = character_data or {}
        self.current_uses = current_uses
        self.max_uses = max_uses
        self.available_options = available_options or []
        self.selected_option = None

        self.setWindowTitle("Channel Divinity")
        self.setModal(True)
        self.setFixedWidth(500)

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Channel Divinity")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Channel divine energy from the Outer Planes to fuel magical effects.\n"
            "Choose one of your available Channel Divinity options."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Uses status
        uses_group = QGroupBox("Channel Divinity Uses")
        uses_layout = QVBoxLayout()

        remaining_uses = self.max_uses - self.current_uses
        self.uses_bar = QProgressBar()
        self.uses_bar.setMinimum(0)
        self.uses_bar.setMaximum(self.max_uses)
        self.uses_bar.setValue(remaining_uses)
        self.uses_bar.setFormat(f"{remaining_uses}/{self.max_uses} uses remaining")
        uses_layout.addWidget(self.uses_bar)

        uses_group.setLayout(uses_layout)
        layout.addWidget(uses_group)

        # Options selection
        if self.available_options:
            options_group = QGroupBox("Available Options")
            options_layout = QVBoxLayout()

            self.option_group = QButtonGroup()
            self.option_buttons = []

            for i, option in enumerate(self.available_options):
                option_frame = QFrame()
                option_frame.setFrameStyle(QFrame.Shape.Box)
                option_layout = QVBoxLayout()

                # Option radio button
                option_btn = QRadioButton(option.get('name', 'Unknown Option'))
                option_btn.setProperty('option_index', i)
                option_btn.toggled.connect(self.option_selected)
                self.option_group.addButton(option_btn)
                self.option_buttons.append(option_btn)
                option_layout.addWidget(option_btn)

                # Option description
                desc_text = QTextEdit()
                desc_text.setPlainText(option.get('description', 'No description available'))
                desc_text.setMaximumHeight(80)
                desc_text.setReadOnly(True)
                option_layout.addWidget(desc_text)

                # Option details
                details = []
                if option.get('action_cost'):
                    details.append(f"Cost: {option['action_cost'].title()}")
                if option.get('range'):
                    details.append(f"Range: {option['range']}")
                if option.get('duration'):
                    details.append(f"Duration: {option['duration']}")
                if option.get('save_type'):
                    details.append(f"Save: {option['save_type'].title()}")

                if details:
                    details_label = QLabel(" • ".join(details))
                    details_label.setStyleSheet("color: #666; font-style: italic;")
                    option_layout.addWidget(details_label)

                option_frame.setLayout(option_layout)
                options_layout.addWidget(option_frame)

            options_group.setLayout(options_layout)
            layout.addWidget(options_group)

        else:
            no_options_label = QLabel("No Channel Divinity options available at your level.")
            no_options_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_options_label.setStyleSheet("color: #999; font-style: italic;")
            layout.addWidget(no_options_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.use_btn = QPushButton("Use Channel Divinity")
        self.use_btn.clicked.connect(self.use_channel_divinity)
        self.use_btn.setDefault(True)
        button_layout.addWidget(self.use_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def option_selected(self, checked: bool):
        """Handle option selection."""
        if checked:
            sender = self.sender()
            option_index = sender.property('option_index')
            if 0 <= option_index < len(self.available_options):
                self.selected_option = self.available_options[option_index]
                self.update_use_button()

    def update_use_button(self):
        """Update use button availability."""
        remaining_uses = self.max_uses - self.current_uses
        can_use = (
            remaining_uses > 0 and
            self.selected_option is not None
        )
        self.use_btn.setEnabled(can_use)

    def update_display(self):
        """Update the display with current values."""
        if hasattr(self, 'uses_bar'):
            remaining_uses = self.max_uses - self.current_uses
            self.uses_bar.setValue(remaining_uses)
            self.uses_bar.setFormat(f"{remaining_uses}/{self.max_uses} uses remaining")

        self.update_use_button()

    def use_channel_divinity(self):
        """Use the selected Channel Divinity option."""
        if self.selected_option and (self.max_uses - self.current_uses) > 0:
            self.channel_divinity_used.emit(
                self.selected_option.get('name', ''),
                self.selected_option
            )
            self.accept()
        else:
            self.update_use_button()

    def reject(self):
        """Handle dialog cancellation."""
        self.channel_divinity_cancelled.emit()
        super().reject()

    def get_selected_option(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected option."""
        return self.selected_option


def create_channel_divinity_options(character_level: int, sacred_oath: str) -> List[Dict[str, Any]]:
    """Create Channel Divinity options based on character level and oath."""
    options = []

    # All paladins get Divine Sense at level 3
    if character_level >= 3:
        options.append({
            'name': 'Divine Sense',
            'description': 'Open your awareness to detect Celestials, Fiends, and Undead within 60 feet for 10 minutes. You also detect consecrated or desecrated places and objects.',
            'action_cost': 'bonus action',
            'range': '60 feet',
            'duration': '10 minutes',
            'effect_type': 'detection',
            'source': 'paladin'
        })

    # Oath-specific options at level 3
    if character_level >= 3:
        if sacred_oath.lower() == 'devotion':
            options.extend([
                {
                    'name': 'Sacred Weapon',
                    'description': 'Imbue one melee weapon with positive energy. For 10 minutes, add your Charisma modifier to attack rolls (minimum +1), choose radiant or normal damage, and the weapon emits bright light.',
                    'action_cost': 'action',
                    'range': 'Self',
                    'duration': '10 minutes',
                    'effect_type': 'enhancement',
                    'source': 'oath_devotion'
                },
                {
                    'name': 'Turn the Unholy',
                    'description': 'Present your holy symbol to turn fiends and undead within 30 feet. Each must make a Wisdom saving throw or be turned for 1 minute.',
                    'action_cost': 'action',
                    'range': '30 feet',
                    'duration': '1 minute',
                    'save_type': 'wisdom',
                    'effect_type': 'control',
                    'source': 'oath_devotion'
                }
            ])

        elif sacred_oath.lower() == 'ancients':
            options.extend([
                {
                    'name': 'Nature\'s Wrath',
                    'description': 'Cause spectral vines to erupt from the ground in a 10-foot radius. Creatures must make a Strength or Dexterity saving throw or be restrained.',
                    'action_cost': 'action',
                    'range': '30 feet',
                    'duration': '1 minute',
                    'save_type': 'strength or dexterity',
                    'effect_type': 'control',
                    'source': 'oath_ancients'
                },
                {
                    'name': 'Turn the Faithless',
                    'description': 'Turn fey and fiends within 30 feet. Each must make a Wisdom saving throw or be turned for 1 minute.',
                    'action_cost': 'action',
                    'range': '30 feet',
                    'duration': '1 minute',
                    'save_type': 'wisdom',
                    'effect_type': 'control',
                    'source': 'oath_ancients'
                }
            ])

        elif sacred_oath.lower() == 'vengeance':
            options.extend([
                {
                    'name': 'Abjure Enemy',
                    'description': 'Choose one creature within 60 feet. It must make a Wisdom saving throw or be frightened and have its speed reduced to 0.',
                    'action_cost': 'action',
                    'range': '60 feet',
                    'duration': '1 minute',
                    'save_type': 'wisdom',
                    'effect_type': 'control',
                    'source': 'oath_vengeance'
                },
                {
                    'name': 'Vow of Enmity',
                    'description': 'Choose one creature within 10 feet and gain advantage on attack rolls against it for 1 minute.',
                    'action_cost': 'bonus action',
                    'range': '10 feet',
                    'duration': '1 minute',
                    'effect_type': 'enhancement',
                    'source': 'oath_vengeance'
                }
            ])

        elif sacred_oath.lower() in ['oath_of_the_unbroken', 'the_unbroken', 'unbroken']:
            options.extend([
                {
                    'name': 'Mind\'s Razor',
                    'description': 'When you hit with a weapon attack, use Channel Divinity to bypass physical defenses. The damage ignores the target\'s resistances and immunities.',
                    'action_cost': 'reaction',
                    'range': 'Self',
                    'duration': 'Instant',
                    'effect_type': 'enhancement',
                    'source': 'oath_unbroken'
                },
                {
                    'name': 'Unbroken Resolve',
                    'description': 'Touch a creature (including yourself) to steel their will. Target gains 1d10 + your Paladin level temporary HP and advantage on Wisdom saving throws for 1 minute.',
                    'action_cost': 'bonus action',
                    'range': 'Touch',
                    'duration': '1 minute',
                    'effect_type': 'support',
                    'source': 'oath_unbroken'
                }
            ])

    # Level 9: Abjure Foes (all paladins)
    if character_level >= 9:
        options.append({
            'name': 'Abjure Foes',
            'description': 'Target a number of creatures equal to your Charisma modifier within 60 feet. Each must make a Wisdom saving throw or be frightened and limited to one action type per turn.',
            'action_cost': 'magic action',
            'range': '60 feet',
            'duration': '1 minute',
            'save_type': 'wisdom',
            'effect_type': 'control',
            'source': 'paladin'
        })

    return options