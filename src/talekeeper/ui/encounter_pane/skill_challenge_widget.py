from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QTextEdit, QScrollArea,
                            QGroupBox, QGridLayout, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from typing import Optional, Dict, List
import random

from talekeeper.services.skill_challenge_manager import (
    SkillChallengeManager, SkillChallengeSession, SkillChallengeTemplate, SkillAttemptResult
)


class SkillButton(QPushButton):
    """Custom button for skill attempts with DC display."""

    def __init__(self, skill_name: str, current_dc: int, parent=None):
        super().__init__(parent)
        self.skill_name = skill_name
        self.current_dc = current_dc
        self.setMinimumHeight(60)
        self.setMaximumWidth(180)
        self.update_text()

    def update_text(self):
        self.setText(f"{self.skill_name}\nDC {self.current_dc}")

    def update_dc(self, new_dc: int):
        self.current_dc = new_dc
        self.update_text()


class SkillChallengeWidget(QWidget):
    """Widget for displaying and interacting with skill challenges."""

    challenge_completed = pyqtSignal(str, str)  # outcome, reward_text
    challenge_refused = pyqtSignal(str)  # refuse_cost

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = SkillChallengeManager()
        self.current_session: Optional[SkillChallengeSession] = None
        self.character_data: Optional[Dict] = None
        self.skill_buttons: Dict[str, SkillButton] = {}

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Challenge title and description
        self.title_label = QLabel("No Active Challenge")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Challenge description area
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(120)
        self.description_text.setReadOnly(True)
        layout.addWidget(self.description_text)

        # Progress tracking
        progress_frame = QFrame()
        progress_layout = QHBoxLayout(progress_frame)

        self.success_label = QLabel("Successes: 0/3")
        self.failure_label = QLabel("Failures: 0/3")

        self.success_progress = QProgressBar()
        self.success_progress.setMaximum(3)
        self.success_progress.setValue(0)
        self.success_progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")

        self.failure_progress = QProgressBar()
        self.failure_progress.setMaximum(3)
        self.failure_progress.setValue(0)
        self.failure_progress.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")

        progress_layout.addWidget(self.success_label)
        progress_layout.addWidget(self.success_progress)
        progress_layout.addStretch()
        progress_layout.addWidget(self.failure_label)
        progress_layout.addWidget(self.failure_progress)

        layout.addWidget(progress_frame)

        # Skills section
        skills_group = QGroupBox("Available Skills")
        self.skills_layout = QGridLayout(skills_group)
        layout.addWidget(skills_group)

        # Action buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.refuse_button = QPushButton("Refuse Challenge")
        self.refuse_button.clicked.connect(self.refuse_challenge)
        self.refuse_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")

        self.new_challenge_button = QPushButton("Start New Challenge")
        self.new_challenge_button.clicked.connect(self.request_new_challenge)

        buttons_layout.addWidget(self.refuse_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.new_challenge_button)

        layout.addWidget(buttons_frame)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(100)
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Skill attempt results will appear here...")
        layout.addWidget(self.results_text)

        self.setLayout(layout)
        self.update_ui_state()

    def set_character_data(self, character_data: Dict):
        """Set the current character data."""
        self.character_data = character_data

    def start_challenge(self, template: SkillChallengeTemplate):
        """Start a new skill challenge."""
        if not self.character_data:
            QMessageBox.warning(self, "Error", "No character selected")
            return

        character_id = self.character_data.get('id')
        if not character_id:
            QMessageBox.warning(self, "Error", "Invalid character data")
            return

        try:
            self.current_session = self.manager.create_session(character_id, template)
            self.update_ui_state()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start challenge: {e}")

    def load_active_session(self, character_id: str):
        """Load an existing active session for the character."""
        self.current_session = self.manager.get_active_session(character_id)
        self.update_ui_state()

    def update_ui_state(self):
        """Update the UI based on current session state."""
        if not self.current_session:
            self.title_label.setText("No Active Challenge")
            self.description_text.clear()
            self.clear_skill_buttons()
            self.success_progress.setValue(0)
            self.failure_progress.setValue(0)
            self.success_label.setText("Successes: 0/3")
            self.failure_label.setText("Failures: 0/3")
            self.refuse_button.setEnabled(False)
            self.new_challenge_button.setEnabled(True)
            return

        # Update title and description
        self.title_label.setText(self.current_session.challenge_name)
        info_text = self.manager.get_challenge_info_text(self.current_session)
        self.description_text.setPlainText(info_text)

        # Update progress
        self.success_progress.setValue(self.current_session.successes)
        self.failure_progress.setValue(self.current_session.failures)
        self.success_label.setText(f"Successes: {self.current_session.successes}/3")
        self.failure_label.setText(f"Failures: {self.current_session.failures}/3")

        # Update skill buttons
        self.update_skill_buttons()

        # Update button states
        self.refuse_button.setEnabled(self.current_session.is_active)
        self.new_challenge_button.setEnabled(not self.current_session.is_active)

    def update_skill_buttons(self):
        """Update the skill buttons based on current session."""
        if not self.current_session:
            self.clear_skill_buttons()
            return

        # Clear existing buttons
        self.clear_skill_buttons()

        # Create new buttons
        skills = self.current_session.template.skills
        cols = 3

        for i, skill in enumerate(skills):
            row = i // cols
            col = i % cols

            current_dc = self.manager.get_skill_dc(self.current_session, skill)
            button = SkillButton(skill, current_dc)
            button.clicked.connect(lambda checked, s=skill: self.attempt_skill(s))
            button.setEnabled(self.current_session.is_active)

            self.skill_buttons[skill] = button
            self.skills_layout.addWidget(button, row, col)

    def clear_skill_buttons(self):
        """Remove all skill buttons."""
        for button in self.skill_buttons.values():
            button.deleteLater()
        self.skill_buttons.clear()

        # Clear layout
        for i in reversed(range(self.skills_layout.count())):
            self.skills_layout.itemAt(i).widget().setParent(None)

    def attempt_skill(self, skill_name: str):
        """Attempt a skill check."""
        if not self.current_session or not self.current_session.is_active:
            return

        if not self.character_data:
            QMessageBox.warning(self, "Error", "No character data available")
            return

        try:
            result = self.manager.attempt_skill(
                self.current_session.id,
                skill_name,
                self.character_data
            )

            self.display_attempt_result(result)

            # Update session data
            self.current_session = self.manager._get_session_by_id(self.current_session.id)
            self.update_ui_state()

            if result.session_complete:
                self.handle_challenge_completion(result.final_outcome)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Skill attempt failed: {e}")

    def display_attempt_result(self, result: SkillAttemptResult):
        """Display the result of a skill attempt."""
        outcome = "SUCCESS" if result.success else "FAILURE"
        color = "#4CAF50" if result.success else "#f44336"

        result_text = (
            f"<div style='color: {color}; font-weight: bold;'>"
            f"{result.skill_name} (DC {result.dc}): {outcome}</div>"
            f"Roll: {result.roll_result} + {result.ability_modifier} (ability) + "
            f"{result.proficiency_bonus} (proficiency) = {result.total_result}"
        )

        self.results_text.append(result_text)

        # Auto-scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)

    def handle_challenge_completion(self, outcome: str):
        """Handle when a challenge is completed."""
        if not self.current_session:
            return

        if outcome == 'success':
            reward = self.current_session.selected_success or "Unknown reward"
            self.challenge_completed.emit('success', reward)
            QMessageBox.information(
                self,
                "Challenge Completed!",
                f"Success! You earned: {reward}"
            )
        elif outcome == 'failure':
            penalty = self.current_session.selected_failure or "Unknown consequence"
            self.challenge_completed.emit('failure', penalty)
            QMessageBox.warning(
                self,
                "Challenge Failed",
                f"Failure! Consequence: {penalty}"
            )

    def refuse_challenge(self):
        """Refuse the current challenge."""
        if not self.current_session or not self.current_session.is_active:
            return

        refuse_cost = self.current_session.selected_refuse or "No consequences"

        reply = QMessageBox.question(
            self,
            "Refuse Challenge",
            f"Are you sure you want to refuse this challenge?\n\nCost: {refuse_cost}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                actual_cost = self.manager.refuse_challenge(self.current_session.id)
                self.challenge_refused.emit(actual_cost)

                # Update UI
                self.current_session.is_active = False
                self.update_ui_state()

                QMessageBox.information(
                    self,
                    "Challenge Refused",
                    f"Challenge refused. Cost: {actual_cost}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to refuse challenge: {e}")

    def request_new_challenge(self):
        """Request a new challenge (should be handled by parent)."""
        # This will be connected to the encounter panel's challenge selection
        pass

    def get_random_challenge_template(self) -> Optional[SkillChallengeTemplate]:
        """Get a random challenge template for testing."""
        templates = self.manager.get_all_templates()
        return random.choice(templates) if templates else None

    def update_theme(self, is_dark: bool):
        """Update widget theme."""
        if is_dark:
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #555;
                    border-radius: 5px;
                    margin-top: 10px;
                    background-color: #2b2b2b;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 10px 0 10px;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    border: 1px solid #555;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    color: #ffffff;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QPushButton:disabled {
                    background-color: #1a1a1a;
                    color: #666;
                }
            """)
        else:
            self.setStyleSheet("")