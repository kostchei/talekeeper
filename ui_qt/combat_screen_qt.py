from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class CombatScreen(QWidget):
    """Combat encounter screen placeholder."""

    def __init__(self, on_end_combat: Callable[[], None]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Combat Screen"))

        end_btn = QPushButton("End Combat")
        end_btn.clicked.connect(on_end_combat)
        layout.addWidget(end_btn)

        layout.addStretch()
