# core
# category: core
"""
Divine Smite Dialog for Paladins

Allows Paladins to choose whether to use Divine Smite after hitting
but before damage is rolled, per D&D 2024 rules.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any, List, Tuple


class DivineSmiteDialog(QDialog):
    """Dialog for choosing Divine Smite options after a successful hit."""

    # Signal emitted when choice is made: (spell_slot_level, is_undead_or_fiend, use_free_smite)
    smite_chosen = pyqtSignal(int, bool, bool)
    smite_declined = pyqtSignal()

    def __init__(self, parent=None, is_critical: bool = False,
                 available_spell_slots: Dict[int, int] = None,
                 target_info: Dict[str, Any] = None,
                 has_free_smite: bool = False):
        """
        Initialize Divine Smite dialog.

        Args:
            parent: Parent widget
            is_critical: Whether the attack was a critical hit
            available_spell_slots: Dict of spell slot level -> available count
            target_info: Information about the target (name, type, current_hp if known)
            has_free_smite: Whether the paladin has their free Paladin's Smite available
        """
        super().__init__(parent)
        self.is_critical = is_critical
        self.available_spell_slots = available_spell_slots or {}
        self.target_info = target_info or {}
        self.has_free_smite = has_free_smite
        self.selected_slot_level = 0

        self.setWindowTitle("Divine Smite")
        self.setModal(True)
        self.setFixedWidth(400)

        # Auto-close timer (15 seconds)
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self._on_timeout)
        self.auto_close_timer.start(15000)  # 15 seconds

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title with critical hit indicator
        title_layout = QHBoxLayout()
        title_label = QLabel("Divine Smite Opportunity!")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        if self.is_critical:
            crit_label = QLabel("CRITICAL HIT!")
            crit_label.setStyleSheet("color: #FFD700; font-weight: bold;")
            title_layout.addWidget(crit_label)

        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Target information
        if self.target_info:
            target_frame = QFrame()
            target_frame.setFrameStyle(QFrame.Shape.Box)
            target_layout = QVBoxLayout(target_frame)

            target_name = self.target_info.get('name', 'Target')
            target_type = self.target_info.get('type', 'Unknown')

            target_label = QLabel(f"Target: {target_name}")
            target_layout.addWidget(target_label)

            # Show if target is undead/fiend (bonus damage)
            if target_type.lower() in ['undead', 'fiend']:
                bonus_label = QLabel(f"Type: {target_type} (+1d8 radiant damage)")
                bonus_label.setStyleSheet("color: #FFD700;")
                target_layout.addWidget(bonus_label)

            # Show target HP and damage preview if known (for tactical decisions)
            if 'current_hp' in self.target_info and self.target_info['current_hp'] > 0:
                current_hp = self.target_info['current_hp']
                base_damage = self.target_info.get('base_damage', 0)
                remaining_hp = current_hp - base_damage

                hp_label = QLabel(f"Current HP: {current_hp}")
                target_layout.addWidget(hp_label)

                if base_damage > 0:
                    damage_preview = QLabel(f"Base Attack Damage: {base_damage}")
                    damage_preview.setStyleSheet("color: #FF6B6B;")
                    target_layout.addWidget(damage_preview)

                    remaining_label = QLabel(f"HP After Base Attack: {remaining_hp}")
                    remaining_label.setStyleSheet("color: #95E1D3;" if remaining_hp > 0 else "color: #FF6B6B;")
                    target_layout.addWidget(remaining_label)

            layout.addWidget(target_frame)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Instructions
        instruction_label = QLabel(
            "Choose a spell slot to use for Divine Smite,\n"
            "or skip to save your spell slots."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # Spell slot options
        slots_group = QGroupBox("Available Spell Slots")
        slots_layout = QVBoxLayout()

        self.slot_buttons = QButtonGroup()
        self.slot_buttons.setExclusive(True)

        # Add free Paladin's Smite option if available (level 1 slot equivalent)
        if self.has_free_smite:
            damage_dice = self._calculate_damage_dice(
                1,
                self.target_info.get('type', '').lower() in ['undead', 'fiend']
            )
            display_dice = damage_dice
            if self.is_critical:
                display_dice *= 2

            free_smite_text = f"Paladin's Smite (FREE, 1/long rest) - {display_dice}d8 radiant"
            if self.is_critical and damage_dice != display_dice:
                free_smite_text += f" (crit doubled from {damage_dice}d8)"

            free_radio = QRadioButton(free_smite_text)
            free_radio.setProperty('slot_level', -1)  # Use -1 to indicate free smite
            free_radio.setStyleSheet("color: #FFD700; font-weight: bold;")
            self.slot_buttons.addButton(free_radio)
            slots_layout.addWidget(free_radio)

        # Sort spell slots by level
        sorted_slots = sorted(self.available_spell_slots.items())

        for slot_level, slot_count in sorted_slots:
            if slot_count > 0:
                # Calculate damage for this slot level
                damage_dice = self._calculate_damage_dice(
                    slot_level,
                    self.target_info.get('type', '').lower() in ['undead', 'fiend']
                )

                # Double dice on critical
                display_dice = damage_dice
                if self.is_critical:
                    display_dice *= 2

                # Create radio button with damage preview
                slot_text = f"Level {slot_level} ({slot_count} available) - {display_dice}d8 radiant"
                if self.is_critical and damage_dice != display_dice:
                    slot_text += f" (crit doubled from {damage_dice}d8)"

                radio = QRadioButton(slot_text)
                radio.setProperty('slot_level', slot_level)
                self.slot_buttons.addButton(radio)
                slots_layout.addWidget(radio)

        # No smite option
        no_smite_radio = QRadioButton("Don't use Divine Smite")
        no_smite_radio.setProperty('slot_level', 0)
        no_smite_radio.setChecked(True)  # Default to not using smite
        self.slot_buttons.addButton(no_smite_radio)
        slots_layout.addWidget(no_smite_radio)

        slots_group.setLayout(slots_layout)
        layout.addWidget(slots_group)

        # Auto-dismiss countdown
        self.countdown_label = QLabel("Auto-closing in 15 seconds...")
        self.countdown_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.countdown_label)

        # Update countdown every second
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)
        self.countdown_remaining = 15

        # Buttons
        button_layout = QHBoxLayout()

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self._on_confirm)
        confirm_button.setDefault(True)

        cancel_button = QPushButton("Cancel (No Smite)")
        cancel_button.clicked.connect(self._on_cancel)

        button_layout.addStretch()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _calculate_damage_dice(self, slot_level: int, is_undead_or_fiend: bool) -> int:
        """Calculate base damage dice for Divine Smite."""
        # Base: 2d8 + 1d8 per spell level above 1st
        damage_dice = 2 + (slot_level - 1)

        # +1d8 vs undead/fiends
        if is_undead_or_fiend:
            damage_dice += 1

        # Cap at 5d8
        return min(damage_dice, 5)

    def _update_countdown(self):
        """Update the countdown display."""
        self.countdown_remaining -= 1
        if self.countdown_remaining > 0:
            self.countdown_label.setText(f"Auto-closing in {self.countdown_remaining} seconds...")
        else:
            self.countdown_timer.stop()

    def _on_timeout(self):
        """Handle timeout - don't use smite."""
        self.auto_close_timer.stop()
        self.countdown_timer.stop()
        self.smite_declined.emit()
        self.reject()

    def _on_confirm(self):
        """Handle confirm button."""
        self.auto_close_timer.stop()
        self.countdown_timer.stop()

        # Get selected slot level
        checked_button = self.slot_buttons.checkedButton()
        if checked_button:
            slot_level = checked_button.property('slot_level')
            if slot_level and slot_level != 0:
                is_undead_or_fiend = self.target_info.get('type', '').lower() in ['undead', 'fiend']
                use_free_smite = (slot_level == -1)
                actual_slot_level = 1 if use_free_smite else slot_level
                self.smite_chosen.emit(actual_slot_level, is_undead_or_fiend, use_free_smite)
            else:
                self.smite_declined.emit()
        else:
            self.smite_declined.emit()

        self.accept()

    def _on_cancel(self):
        """Handle cancel button."""
        self.auto_close_timer.stop()
        self.countdown_timer.stop()
        self.smite_declined.emit()
        self.reject()

    def get_smite_damage_dice(self, slot_level: int) -> str:
        """
        Get the damage dice string for a given spell slot level.

        Args:
            slot_level: Spell slot level to use

        Returns:
            Damage dice string (e.g., "3d8")
        """
        is_undead_or_fiend = self.target_info.get('type', '').lower() in ['undead', 'fiend']
        dice_count = self._calculate_damage_dice(slot_level, is_undead_or_fiend)

        # Double on critical
        if self.is_critical:
            dice_count *= 2

        return f"{dice_count}d8"