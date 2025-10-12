"""
Monster Knowledge Label - Interactive label with hover tooltips for monster information

This widget displays monster information and allows the player to make knowledge checks
by hovering over the monster name. The tooltip shows information based on the player's
skill check result.
"""

from PyQt6.QtWidgets import (QLabel, QDialog, QVBoxLayout, QPushButton,
                             QHBoxLayout, QComboBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor, QEnterEvent
from typing import Dict, Optional
import random

from talekeeper.services.monster_knowledge import monster_knowledge_service, MonsterKnowledge


class MonsterKnowledgeDialog(QDialog):
    """Dialog for making a monster knowledge check."""

    def __init__(self, monster_data: Dict, character_data: Dict, parent=None):
        super().__init__(parent)
        self.monster_data = monster_data
        self.character_data = character_data
        self.knowledge_result: Optional[MonsterKnowledge] = None

        self.setWindowTitle("Monster Knowledge Check")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Monster info
        monster_type = self.monster_data.get('type', 'Unknown')
        monster_name = self.monster_data.get('name', 'Unknown Creature')
        cr = self.monster_data.get('challenge_rating', '0')

        info_group = QGroupBox(f"Identify: {monster_name}")
        info_layout = QVBoxLayout()

        # Get applicable skills
        applicable_skills = monster_knowledge_service.get_applicable_skills(monster_type)
        dc = monster_knowledge_service.calculate_dc(cr)

        if applicable_skills:
            skills_text = ', '.join([s.title() for s in applicable_skills])
            info_layout.addWidget(QLabel(f"Applicable Skills: {skills_text}"))
        else:
            info_layout.addWidget(QLabel(f"No applicable skills for {monster_type} type"))

        info_layout.addWidget(QLabel(f"DC: {dc} (CR {cr})"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Skill selection
        skill_group = QGroupBox("Make Knowledge Check")
        skill_layout = QVBoxLayout()

        skill_row = QHBoxLayout()
        skill_row.addWidget(QLabel("Skill:"))
        self.skill_combo = QComboBox()

        # Populate with applicable skills or all knowledge skills
        if applicable_skills:
            for skill in applicable_skills:
                self.skill_combo.addItem(skill.title(), skill)
        else:
            # Add all knowledge skills as fallback
            for skill in ['arcana', 'nature', 'religion', 'history', 'insight', 'investigation', 'survival']:
                self.skill_combo.addItem(skill.title(), skill)

        skill_row.addWidget(self.skill_combo)
        skill_layout.addLayout(skill_row)

        # Roll input
        roll_row = QHBoxLayout()
        roll_row.addWidget(QLabel("Roll Result:"))
        self.roll_spinbox = QSpinBox()
        self.roll_spinbox.setMinimum(1)
        self.roll_spinbox.setMaximum(30)
        self.roll_spinbox.setValue(10)
        roll_row.addWidget(self.roll_spinbox)

        # Auto-roll button
        auto_roll_btn = QPushButton("Roll d20")
        auto_roll_btn.clicked.connect(self.auto_roll)
        roll_row.addWidget(auto_roll_btn)

        skill_layout.addLayout(roll_row)
        skill_group.setLayout(skill_layout)
        layout.addWidget(skill_group)

        # Buttons
        button_layout = QHBoxLayout()

        check_btn = QPushButton("Check Knowledge")
        check_btn.clicked.connect(self.perform_check)
        button_layout.addWidget(check_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Result display
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        layout.addWidget(self.result_label)
        self.result_label.hide()

    def auto_roll(self):
        """Auto-roll a d20 and add character's skill modifier."""
        # Get selected skill
        skill = self.skill_combo.currentData()

        # Roll d20
        roll = random.randint(1, 20)

        # Get skill modifier from character
        # This is simplified - in a real implementation, you'd calculate from proficiencies
        modifier = self.get_skill_modifier(skill)

        total = roll + modifier
        self.roll_spinbox.setValue(total)

        # Show roll breakdown
        self.result_label.setText(f"Rolled: {roll} + {modifier} (modifier) = {total}")
        self.result_label.show()

    def get_skill_modifier(self, skill: str) -> int:
        """
        Calculate skill modifier for the character.
        This is simplified - a full implementation would check proficiency, expertise, etc.
        """
        # Map skills to abilities
        skill_abilities = {
            'arcana': 'intelligence',
            'nature': 'intelligence',
            'religion': 'intelligence',
            'history': 'intelligence',
            'insight': 'wisdom',
            'investigation': 'intelligence',
            'survival': 'wisdom'
        }

        ability = skill_abilities.get(skill, 'intelligence')
        ability_score = self.character_data.get(ability, 10)
        modifier = (ability_score - 10) // 2

        # Add proficiency bonus if proficient (simplified check)
        # In a real implementation, check character_proficiencies table
        level = self.character_data.get('level', 1)
        prof_bonus = 2 + ((level - 1) // 4)  # Standard proficiency progression

        # For now, assume proficiency in Int-based skills for wizards, Wis-based for clerics, etc.
        is_proficient = False
        class_id = self.character_data.get('class_id', '').lower()

        if class_id in ['wizard', 'warlock'] and ability == 'intelligence':
            is_proficient = True
        elif class_id == 'cleric' and skill in ['religion', 'insight']:
            is_proficient = True
        elif class_id == 'rogue' and ability == 'intelligence':
            is_proficient = True

        if is_proficient:
            modifier += prof_bonus

        return modifier

    def perform_check(self):
        """Perform the knowledge check and display results."""
        skill = self.skill_combo.currentData()
        roll_result = self.roll_spinbox.value()

        # Perform knowledge check
        self.knowledge_result = monster_knowledge_service.check_knowledge(
            self.monster_data,
            roll_result,
            skill
        )

        # Format and display results
        result_html = monster_knowledge_service.format_tooltip_html(
            self.knowledge_result,
            skill,
            roll_result
        )

        self.result_label.setText(result_html)
        self.result_label.setTextFormat(Qt.TextFormat.RichText)
        self.result_label.show()

        # Auto-close after showing results (optional)
        # QTimer.singleShot(5000, self.accept)


class MonsterKnowledgeLabel(QLabel):
    """
    A QLabel that shows monster knowledge tooltips on hover.

    Features:
    - Displays monster name
    - Shows knowledge check dialog on click
    - Can auto-generate tooltip from stored knowledge checks
    """

    knowledge_checked = pyqtSignal(MonsterKnowledge)

    def __init__(self, monster_data: Dict, character_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)

        self.monster_data = monster_data
        self.character_data = character_data or {}
        self.stored_knowledge: Optional[MonsterKnowledge] = None

        # Set initial text
        monster_name = monster_data.get('name', 'Unknown')
        self.setText(monster_name)

        # Style
        self.setStyleSheet("""
            QLabel {
                color: #4FC3F7;
                text-decoration: underline;
                padding: 2px;
            }
            QLabel:hover {
                color: #81D4FA;
                background-color: rgba(79, 195, 247, 0.1);
            }
        """)

        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Handle mouse click to open knowledge check dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_knowledge_dialog()
        super().mousePressEvent(event)

    def open_knowledge_dialog(self):
        """Open the knowledge check dialog."""
        dialog = MonsterKnowledgeDialog(
            self.monster_data,
            self.character_data,
            self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.knowledge_result:
                self.stored_knowledge = dialog.knowledge_result
                self.update_tooltip()
                self.knowledge_checked.emit(dialog.knowledge_result)

    def update_tooltip(self):
        """Update the tooltip with stored knowledge."""
        if self.stored_knowledge:
            # Get the applicable skill (just use first applicable skill for tooltip)
            monster_type = self.monster_data.get('type', 'Unknown')
            skills = monster_knowledge_service.get_applicable_skills(monster_type)
            skill = skills[0] if skills else 'knowledge'

            # Generate tooltip HTML
            tooltip_html = monster_knowledge_service.format_tooltip_html(
                self.stored_knowledge,
                skill,
                self.stored_knowledge.dc + self.stored_knowledge.margin
            )

            self.setToolTip(tooltip_html)

    def set_knowledge_result(self, knowledge: MonsterKnowledge):
        """Manually set a knowledge check result."""
        self.stored_knowledge = knowledge
        self.update_tooltip()

    def enterEvent(self, event: QEnterEvent):
        """Show tooltip when mouse enters."""
        if self.stored_knowledge:
            # Tooltip is already set via setToolTip
            pass
        else:
            # Show a hint that clicking will reveal information
            cr = self.monster_data.get('challenge_rating', '0')
            dc = monster_knowledge_service.calculate_dc(cr)
            monster_type = self.monster_data.get('type', 'Unknown')
            skills = monster_knowledge_service.get_applicable_skills(monster_type)

            if skills:
                skills_text = ', '.join([s.title() for s in skills])
                hint = f"<b>Click to identify</b><br/>DC {dc} {skills_text} check"
            else:
                hint = f"<b>Click to identify</b><br/>DC {dc} knowledge check"

            self.setToolTip(hint)

        super().enterEvent(event)
