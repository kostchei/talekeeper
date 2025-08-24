from __future__ import annotations

from typing import Callable, Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)

from core.game_engine import GameEngine


class CharacterCreator(QWidget):
    """Simple character creation screen.

    This widget is intentionally minimal and serves as a placeholder for a
    full character creation workflow. When the user finishes, a callback is
    invoked with basic character data so the main window can transition to
    the game screen.
    """

    def __init__(
        self,
        engine: GameEngine,
        on_finished: Callable[[Dict], None],
        on_cancel: Callable[[], None],
    ):
        super().__init__()
        self.engine = engine
        self._on_finished = on_finished
        self._on_cancel = on_cancel

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Character Creator"))
        layout.addStretch()

        button_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        finish_btn = QPushButton("Finish")
        button_row.addWidget(cancel_btn)
        button_row.addStretch()
        button_row.addWidget(finish_btn)
        layout.addLayout(button_row)

        cancel_btn.clicked.connect(self._on_cancel)
        finish_btn.clicked.connect(self._finish)

    def _finish(self) -> None:
        # Placeholder character data; a full implementation would collect
        # selections from the user.
        character = {"name": "Hero"}
        self._on_finished(character)
