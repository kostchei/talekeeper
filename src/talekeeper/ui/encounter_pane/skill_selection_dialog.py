from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
import sqlite3
from typing import List, Set


class SkillSelectionDialog(QDialog):
    def __init__(self, character_id: str, num_skills: int = 3, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.num_skills = num_skills
        self.selected_skills = []

        self.setWindowTitle("Skilled Feat - Select Skills")
        self.setModal(True)
        self.setMinimumSize(400, 500)

        self._setup_ui()
        self._load_available_skills()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"Select {self.num_skills} Skills")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        instructions = QLabel(
            f"Choose {self.num_skills} skills you don't already have proficiency in.\n"
            "Skills you're already proficient in are not shown."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 5px; padding: 10px; background: #f0f0f0; border-radius: 4px;")
        layout.addWidget(instructions)

        self.skill_list = QListWidget()
        self.skill_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.skill_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.skill_list)

        self.selection_label = QLabel(f"Selected: 0 / {self.num_skills}")
        self.selection_label.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(self.selection_label)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self._confirm_selection)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setStyleSheet("padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.confirm_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("padding: 8px;")
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _load_available_skills(self):
        all_skills = [
            'Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception',
            'History', 'Insight', 'Intimidation', 'Investigation', 'Medicine',
            'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion',
            'Sleight of Hand', 'Stealth', 'Survival'
        ]

        existing_proficiencies = self._get_character_skill_proficiencies()

        for skill in all_skills:
            if skill not in existing_proficiencies:
                self.skill_list.addItem(skill)

    def _get_character_skill_proficiencies(self) -> Set[str]:
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT proficiency_name
                FROM character_proficiencies
                WHERE character_id = ? AND proficiency_type = 'skill'
            """, (self.character_id,))

            proficiencies = {row[0] for row in cursor.fetchall()}
            conn.close()

            return proficiencies
        except Exception as e:
            print(f"Error getting character skill proficiencies: {e}")
            return set()

    def _on_selection_changed(self):
        selected_items = self.skill_list.selectedItems()
        num_selected = len(selected_items)

        if num_selected > self.num_skills:
            for item in selected_items[self.num_skills:]:
                item.setSelected(False)
            num_selected = self.num_skills

        self.selection_label.setText(f"Selected: {num_selected} / {self.num_skills}")
        self.confirm_button.setEnabled(num_selected == self.num_skills)

    def _confirm_selection(self):
        selected_items = self.skill_list.selectedItems()
        if len(selected_items) != self.num_skills:
            QMessageBox.warning(
                self,
                "Invalid Selection",
                f"Please select exactly {self.num_skills} skills."
            )
            return

        self.selected_skills = [item.text() for item in selected_items]
        self.accept()

    def get_selected_skills(self) -> List[str]:
        return self.selected_skills