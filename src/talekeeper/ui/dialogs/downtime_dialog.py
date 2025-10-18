from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from typing import Dict, Any
from talekeeper.services.downtime_activities import DowntimeActivityService


class DowntimeDialog(QDialog):

    def __init__(self, character_data: Dict[str, Any], db_path: str = "talekeeper.db", parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.db_path = db_path
        self.service = DowntimeActivityService(db_path)

        self.setWindowTitle("Downtime Activities")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("DOWNTIME ACTIVITIES")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a90e2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        character_id = self.character_data.get('id', '')
        character_gold = self._get_character_gold(character_id)
        character_level = self.character_data.get('level', 1)

        info_label = QLabel(f"Character: {self.character_data.get('name')} (Level {character_level})\nGold: {character_gold:,} gp")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(info_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(10)

        carousing_frame = self._create_activity_frame(
            "Carousing",
            "Spend time in revelry and socializing. Roll on the carousing table to see what happens!",
            self._calculate_carousing_cost(character_level),
            character_gold,
            self._start_carousing
        )
        scroll_layout.addWidget(carousing_frame)

        prayer_frame = self._create_activity_frame(
            "Prayer and Contemplation",
            "Spend 2 days in prayer and meditation. Requires a donation and modest lifestyle costs.",
            self._calculate_prayer_cost(character_level),
            character_gold,
            self._start_prayer
        )
        scroll_layout.addWidget(prayer_frame)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        history_label = QLabel("Recent Activities:")
        history_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(history_label)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(120)
        self._load_activity_history()
        layout.addWidget(self.history_text)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def _create_activity_frame(self, title: str, description: str, cost: int, character_gold: int, callback) -> QFrame:
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; margin-bottom: 5px;")
        layout.addWidget(desc_label)

        cost_label = QLabel(f"Cost: {cost} gp")
        cost_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout.addWidget(cost_label)

        button = QPushButton("Start Activity")
        button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)

        if character_gold < cost:
            button.setEnabled(False)
            button.setText("Insufficient Gold")

        button.clicked.connect(callback)
        layout.addWidget(button)

        return frame

    def _calculate_carousing_cost(self, level: int) -> int:
        return 40

    def _calculate_prayer_cost(self, level: int) -> int:
        donation = 5 * level
        lifestyle = 10 * 2
        return donation + lifestyle

    def _start_carousing(self):
        character_id = self.character_data.get('id', '')
        character_level = self.character_data.get('level', 1)

        result = self.service.carousing(character_id, character_level)

        if result['success']:
            details = f"Carousing Results:\n\n"
            details += f"Roll: {result['roll']} + {character_level} (level) = {result['modified_roll']}\n\n"
            details += f"{result['description']}\n\n"
            details += f"Gold spent: {result['gold_spent']} gp\n"

            if result['gold_change'] != 0:
                if result['gold_change'] > 0:
                    details += f"Gold gained: {result['gold_change']} gp\n"
                else:
                    details += f"Gold lost: {abs(result['gold_change'])} gp\n"

            if result.get('inspiration_gained', 0) > 0:
                details += f"\nYou gained {result['inspiration_gained']} Heroic Inspiration!"

            details += f"\n\nNew gold total: {result['new_gold']} gp"

            QMessageBox.information(self, "Carousing Complete", details)
            self._load_activity_history()
            self.accept()
        else:
            QMessageBox.warning(self, "Carousing Failed", result.get('error', 'Unknown error'))

    def _start_prayer(self):
        character_id = self.character_data.get('id', '')
        character_level = self.character_data.get('level', 1)

        result = self.service.prayer(character_id, character_level)

        if result['success']:
            details = f"Prayer and Contemplation:\n\n"
            details += f"{result['description']}\n\n"
            details += f"Donation: {result['breakdown']['donation']} gp\n"
            details += f"Lifestyle (2 days): {result['breakdown']['lifestyle']} gp\n"
            details += f"Total spent: {result['gold_spent']} gp\n\n"
            details += f"You gained {result['inspiration_gained']} Heroic Inspiration!\n\n"
            details += f"New gold total: {result['new_gold']} gp"

            QMessageBox.information(self, "Prayer Complete", details)
            self._load_activity_history()
            self.accept()
        else:
            QMessageBox.warning(self, "Prayer Failed", result.get('error', 'Unknown error'))

    def _load_activity_history(self):
        character_id = self.character_data.get('id', '')
        activities = self.service.get_activity_history(character_id, limit=5)

        if not activities:
            self.history_text.setPlainText("No downtime activities recorded yet.")
            return

        history_text = ""
        for activity in activities:
            history_text += f"[{activity['type'].upper()}] {activity['description']}\n"
            if activity['gold_spent'] > 0:
                history_text += f"  Spent: {activity['gold_spent']} gp\n"
            if activity['gold_gained'] > 0:
                history_text += f"  Gained: {activity['gold_gained']} gp\n"
            if activity['inspiration_gained'] > 0:
                history_text += f"  Inspiration: +{activity['inspiration_gained']}\n"
            history_text += "\n"

        self.history_text.setPlainText(history_text)

    def _get_character_gold(self, character_id: str) -> int:
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quantity FROM character_inventory
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
            """, (character_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting character gold: {e}")
            return 0
