from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QMenu,
)

from core.game_engine import GameEngine
from .character_creator_qt import CharacterCreator
from .game_screen_qt import GameScreen
from .combat_screen_qt import CombatScreen


class MainWindow(QMainWindow):
    """Qt-based main window managing application screens."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

        self.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        self.resize(1920, 1080)
        self.setMinimumSize(1280, 720)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._screens: Dict[str, QWidget] = {}
        self._current: Optional[str] = None

        self._create_status_bar()
        self._create_menu()
        self.show_start_screen()

    # ------------------------------------------------------------------
    def _create_status_bar(self) -> None:
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)
        self.status = status

    # ------------------------------------------------------------------
    def _create_menu(self) -> None:
        menubar = self.menuBar()
        game_menu = menubar.addMenu("Game")
        new_action = game_menu.addAction("New Character")
        new_action.triggered.connect(self.open_character_creator)
        save_action = game_menu.addAction("Save Game")
        save_action.triggered.connect(self.save_game)
        game_menu.addSeparator()
        exit_action = game_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

    # ------------------------------------------------------------------
    def _switch_screen(self, name: str, widget: QWidget) -> None:
        if self._current:
            old = self._screens.pop(self._current, None)
            if old:
                self._stack.removeWidget(old)
                old.deleteLater()
        self._screens[name] = widget
        self._stack.addWidget(widget)
        self._stack.setCurrentWidget(widget)
        self._current = name

    # ------------------------------------------------------------------
    def show_start_screen(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        title = QLabel("TaleKeeper")
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)
        new_btn = QPushButton("New Character")
        new_btn.clicked.connect(self.open_character_creator)
        layout.addWidget(new_btn)
        layout.addStretch()
        self._switch_screen("start", widget)

    # ------------------------------------------------------------------
    def open_character_creator(self) -> None:
        creator = CharacterCreator(
            self.engine, self._character_created, self.show_start_screen
        )
        self._switch_screen("creator", creator)

    # ------------------------------------------------------------------
    def _character_created(self, data: Dict) -> None:
        self.status.showMessage(f"Character created: {data.get('name')}")
        self.open_game_screen()

    # ------------------------------------------------------------------
    def open_game_screen(self) -> None:
        game = GameScreen(self.start_combat)
        self._switch_screen("game", game)

    # ------------------------------------------------------------------
    def start_combat(self) -> None:
        combat = CombatScreen(self.end_combat)
        self._switch_screen("combat", combat)

    # ------------------------------------------------------------------
    def end_combat(self) -> None:
        self.open_game_screen()

    # ------------------------------------------------------------------
    def save_game(self) -> None:
        if self.engine.current_character:
            self.engine.save_game()
            self.status.showMessage("Game saved", 3000)
