# core
# core
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any


class EpicBoonDialog(QDialog):
    boon_chosen = pyqtSignal(str)

    def __init__(self, available_boons: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.available_boons = available_boons
        self.selected_boon = None

        self.setWindowTitle("Epic Boon Selection - Level 19")
        self.setModal(True)
        self.setMinimumSize(700, 600)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("Epic Boon Selection")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        info_label = QLabel(
            "At level 19, you gain an Epic Boon - a powerful feat that enhances your capabilities.<br>"
            "Select one boon from the list below:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        content_layout = QHBoxLayout()

        self.boon_list = QListWidget()
        self.boon_list.setMinimumWidth(250)
        for boon in self.available_boons:
            item = QListWidgetItem(boon['name'].replace('Boon of ', ''))
            item.setData(Qt.ItemDataRole.UserRole, boon['name'])
            self.boon_list.addItem(item)
        self.boon_list.currentItemChanged.connect(self._on_selection_changed)
        content_layout.addWidget(self.boon_list)

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumWidth(400)
        content_layout.addWidget(self.description_text)

        layout.addLayout(content_layout)

        layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumWidth(100)
        confirm_btn.clicked.connect(self._on_confirm)
        confirm_btn.setEnabled(False)
        self.confirm_btn = confirm_btn
        button_layout.addWidget(confirm_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        if self.available_boons:
            self.boon_list.setCurrentRow(0)

    def _on_selection_changed(self, current, previous):
        if current:
            boon_name = current.data(Qt.ItemDataRole.UserRole)
            boon_data = next((b for b in self.available_boons if b['name'] == boon_name), None)

            if boon_data:
                self.selected_boon = boon_name

                description_html = f"<h3>{boon_data['name']}</h3>"
                description_html += f"<p><b>Type:</b> Epic Boon (Level 19)</p>"

                if boon_data.get('prerequisites'):
                    description_html += f"<p><b>Prerequisites:</b> {boon_data['prerequisites']}</p>"

                description_html += f"<p>{boon_data['description']}</p>"

                self.description_text.setHtml(description_html)
                self.confirm_btn.setEnabled(True)

    def _on_confirm(self):
        if self.selected_boon:
            self.boon_chosen.emit(self.selected_boon)
            self.accept()

    def get_selected_boon(self) -> str:
        return self.selected_boon


def show_epic_boon_dialog(available_boons: List[Dict[str, Any]], parent=None) -> str:
    dialog = EpicBoonDialog(available_boons, parent)
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        return dialog.get_selected_boon()
    else:
        return None