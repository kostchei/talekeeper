"""
Game Menu Widget - Top dropdown menu with game controls

PyQt6 widget that provides the main game menu functionality including:
- Dropdown toggle capability
- Save/Load game options
- Settings access
- Game controls

Designed to match ui_plan.md specifications:
- Fixed size: 648x200 (menu frame) + 648x300 (dropdown)
- Toggle visibility for dropdown options
- Dark theme styling
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class GameMenu(QWidget):
    """
    Main game menu widget with dropdown functionality.
    
    Signals:
        create_character_requested: Emitted when create character is clicked
        load_game_requested: Emitted when load game is clicked  
        save_and_exit_requested: Emitted when save & exit is clicked
        archive_character_requested: Emitted when archive character is clicked
        settings_requested: Emitted when settings is clicked
        campaign_frame_requested: Emitted when campaign frame is clicked
    """
    
    # Define signals for menu actions
    create_character_requested = pyqtSignal()
    load_game_requested = pyqtSignal()
    save_and_exit_requested = pyqtSignal()
    archive_character_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    campaign_frame_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.dropdown_visible = False
        self.setAutoFillBackground(True)  # Ensure background is filled
        self.setFixedSize(648, 140)  # Slightly taller for better button fit
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the menu UI components."""
        # Main layout - simple grid of buttons
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(10, 2, 10, 10)  # Reduced top margin from 10 to 2
        self.main_layout.setSpacing(1)  # Further reduced spacing to 1px
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align content to top, don't stretch
        
        # === 2 COLUMNS x 3 ROWS OF BUTTONS ===
        
        # Row 1
        self.create_character_btn = QPushButton("Create Character")
        self.create_character_btn.clicked.connect(self.create_character_requested.emit)
        self.create_character_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.create_character_btn, 0, 0)
        
        self.load_game_btn = QPushButton("Load Game")
        self.load_game_btn.clicked.connect(self.load_game_requested.emit)
        self.load_game_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.load_game_btn, 0, 1)
        
        # Row 2
        self.save_and_exit_btn = QPushButton("Save & Exit")
        self.save_and_exit_btn.clicked.connect(self.save_and_exit_requested.emit)
        self.save_and_exit_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.save_and_exit_btn, 1, 0)
        
        self.archive_character_btn = QPushButton("Archive Character")
        self.archive_character_btn.clicked.connect(self.archive_character_requested.emit)
        self.archive_character_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.archive_character_btn, 1, 1)
        
        # Row 3
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        self.settings_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.settings_btn, 2, 0)
        
        self.campaign_frame_btn = QPushButton("Campaign Frame")
        self.campaign_frame_btn.clicked.connect(self.campaign_frame_requested.emit)
        self.campaign_frame_btn.setObjectName("menuButton")
        self.main_layout.addWidget(self.campaign_frame_btn, 2, 1)
    
    def _apply_styles(self):
        """Apply dark theme styling to menu components."""
        style_sheet = """
        GameMenu {
            background-color: #2d2d2d;
        }
        
        QFrame#menuFrame {
            background-color: #2d2d2d;
        }
        
        QFrame#dropdownFrame {
            background-color: #3d3d3d;
        }
        
        QLabel#gameInfoLabel {
            color: #cccccc;
            font-size: 12px;
        }
        
        QPushButton#menuButton {
            background-color: #404040;
            color: #ffffff;
            font-weight: bold;
            text-align: left;
            font-size: 12px;
            padding: 2px 8px;
            margin: 1px;
        }
        
        QPushButton#menuButton:hover {
            background-color: #505050;
        }
        
        QPushButton#menuButton:pressed {
            background-color: #303030;
        }
        
        QPushButton#expandButton {
            background-color: #404040;
            color: #ffffff;
            font-weight: bold;
        }
        
        QPushButton#expandButton:hover {
            background-color: #505050;
        }
        
        QPushButton {
            background-color: #404040;
            color: #ffffff;
            font-weight: bold;
            text-align: left;
        }
        
        QPushButton:hover {
            background-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #303030;
        }
        
        QFrame#separator {
            color: #666666;
        }
        """
        self.setStyleSheet(style_sheet)
    
    
    def set_save_enabled(self, enabled: bool):
        """Enable/disable the save & exit button based on game state."""
        self.save_and_exit_btn.setEnabled(enabled)
    
    def set_character_loaded(self, loaded: bool):
        """Enable/disable character-dependent buttons based on whether a character is loaded."""
        self.save_and_exit_btn.setEnabled(loaded)
        self.archive_character_btn.setEnabled(loaded)
    
    def update_game_info(self, character_name: str, level: int):
        """Update the game information display with character name and level."""
        pass