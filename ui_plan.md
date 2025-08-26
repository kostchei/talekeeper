"""
Game Layout UI - PyQt6 (Animated)

Assumptions & Overview:
-----------------------
- Minimum window size: 1920x1080
- 5% margins → usable central space: 1728 x 972
- Layout divided into major components:
    1. Top Menu (static + dropdown)
    2. Character Sheet (expandable left panel)
    3. Log Pane (top-right)
    4. Equipment Layout (slides open/closed)
    5. Monster Pane (center main view)
    6. Action Cards (bottom panel)

- Sliding panels:
    * Character Sheet: expands from 648px → 1296px width.
    * Equipment Panel: expands from 432px → 1080px width.
- Uses QPropertyAnimation for smooth transitions.
- QSplitter manages flexible space, but animations are explicit.

"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QFrame, QLabel, QPushButton, QTextEdit, QSplitter, QHBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect


class GamePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D&D Game Layout")
        self.setMinimumSize(1920, 1080)

        # === CENTRAL WIDGET ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # === TOP MENU ===
        self.menu_frame = QFrame()
        self.menu_frame.setFixedSize(648, 200)
        self.menu_frame.setStyleSheet("background-color: #2d2d2d; border: 2px solid #666;")
        menu_label = QLabel("Menu", self.menu_frame)
        menu_label.setStyleSheet("color: white; font-weight: bold; padding: 8px;")

        # Dropdown (hidden by default)
        self.menu_dropdown = QFrame()
        self.menu_dropdown.setFixedSize(648, 600)
        self.menu_dropdown.setStyleSheet("background-color: #3d3d3d; border: 2px solid #666;")
        self.menu_dropdown.hide()

        # Toggle dropdown
        toggle_menu_btn = QPushButton("Toggle Menu")
        toggle_menu_btn.clicked.connect(self.toggle_menu_dropdown)

        # === MAIN SPLITTER ===
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- CHARACTER SHEET ---
        self.character_frame = QFrame()
        self.character_frame.setFixedSize(648, 1228)
        self.character_frame.setStyleSheet("background-color: #202020; border: 2px solid #444;")
        char_layout = QVBoxLayout(self.character_frame)
        char_layout.addWidget(QLabel("Character Sheet", self.character_frame))
        char_layout.itemAt(0).widget().setStyleSheet("color: white; padding: 8px;")

        # Toggle button for character sheet size
        self.char_expanded = False
        self.char_toggle_btn = QPushButton("Expand Character Sheet")
        self.char_toggle_btn.clicked.connect(self.toggle_character_sheet)
        char_layout.addWidget(self.char_toggle_btn)

        # --- MONSTER PANE ---
        self.monster_frame = QFrame()
        self.monster_frame.setFixedSize(648, 1428)
        self.monster_frame.setStyleSheet("background-color: #101010; border: 2px solid #333;")
        monster_layout = QVBoxLayout(self.monster_frame)
        monster_label = QLabel("Monster Pane", self.monster_frame)
        monster_label.setStyleSheet("color: white; padding: 8px;")
        monster_layout.addWidget(monster_label)

        # --- RIGHT COLUMN: LOG + EQUIPMENT ---
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Log window
        self.log_frame = QFrame()
        self.log_frame.setFixedSize(432, 486)
        self.log_frame.setStyleSheet("background-color: #181818; border: 2px solid #555;")
        log_text = QTextEdit("Log Window")
        log_text.setStyleSheet("color: white; background-color: #181818;")
        log_text.setReadOnly(True)
        log_layout = QVBoxLayout(self.log_frame)
        log_layout.addWidget(log_text)

        # Equipment panel (slides open)
        self.equipment_frame = QFrame()
        self.equipment_frame.setFixedSize(432, 486)
        self.equipment_frame.setStyleSheet("background-color: #222; border: 2px solid #555;")
        eq_layout = QVBoxLayout(self.equipment_frame)
        eq_layout.addWidget(QLabel("Equipment Layout", self.equipment_frame))
        eq_layout.itemAt(0).widget().setStyleSheet("color: white; padding: 8px;")

        self.eq_expanded = False
        self.eq_toggle_btn = QPushButton("Expand Equipment")
        self.eq_toggle_btn.clicked.connect(self.toggle_equipment)
        eq_layout.addWidget(self.eq_toggle_btn)

        self.right_splitter.addWidget(self.log_frame)
        self.right_splitter.addWidget(self.equipment_frame)
        self.right_splitter.setSizes([486, 486])

        # Add to main splitter
        self.main_splitter.addWidget(self.character_frame)
        self.main_splitter.addWidget(self.monster_frame)
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setSizes([648, 648, 432])

        # === ACTION CARDS ===
        self.action_cards_frame = QFrame()
        self.action_cards_frame.setFixedSize(1296, 300)
        self.action_cards_frame.setStyleSheet("background-color: #2a2a2a; border: 2px solid #444;")
        action_label = QLabel("Action Cards Area", self.action_cards_frame)
        action_label.setStyleSheet("color: white; padding: 8px;")

        # === STACK LAYOUT ===
        self.main_layout.addWidget(self.menu_frame)
        self.main_layout.addWidget(toggle_menu_btn)
        self.main_layout.addWidget(self.main_splitter)
        self.main_layout.addWidget(self.action_cards_frame)

    # --- DROPDOWN MENU ---
    def toggle_menu_dropdown(self):
        self.menu_dropdown.setVisible(not self.menu_dropdown.isVisible())

    # --- CHARACTER SHEET SLIDE ---
    def toggle_character_sheet(self):
        start_width = self.character_frame.width()
        end_width = 1296 if not self.char_expanded else 648

        anim = QPropertyAnimation(self.character_frame, b"geometry")
        anim.setDuration(400)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(QRect(
            self.character_frame.x(), self.character_frame.y(),
            start_width, self.character_frame.height()
        ))
        anim.setEndValue(QRect(
            self.character_frame.x(), self.character_frame.y(),
            end_width, self.character_frame.height()
        ))
        anim.start()
        self.char_expanded = not self.char_expanded
        self.char_toggle_btn.setText(
            "Collapse Character Sheet" if self.char_expanded else "Expand Character Sheet"
        )

    # --- EQUIPMENT SLIDE ---
    def toggle_equipment(self):
        start_width = self.equipment_frame.width()
        end_width = 1080 if not self.eq_expanded else 432

        anim = QPropertyAnimation(self.equipment_frame, b"geometry")
        anim.setDuration(400)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(QRect(
            self.equipment_frame.x(), self.equipment_frame.y(),
            start_width, self.equipment_frame.height()
        ))
        anim.setEndValue(QRect(
            self.equipment_frame.x(), self.equipment_frame.y(),
            end_width, self.equipment_frame.height()
        ))
        anim.start()
        self.eq_expanded = not self.eq_expanded
        self.eq_toggle_btn.setText(
            "Collapse Equipment" if self.eq_expanded else "Expand Equipment"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_page = GamePage()
    game_page.show()
    sys.exit(app.exec())
