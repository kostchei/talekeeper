from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class GameScreen(QWidget):
    """Main gameplay screen placeholder."""

    def __init__(self, on_start_combat: Callable[[], None]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Game Screen"))

        combat_btn = QPushButton("Start Combat")
        combat_btn.clicked.connect(on_start_combat)
        layout.addWidget(combat_btn)

        layout.addStretch()
