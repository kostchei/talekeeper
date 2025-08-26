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

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
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
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the menu UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # === MENU FRAME ===
        self.menu_frame = QFrame()
        self.menu_frame.setFixedSize(648, 200)
        self.menu_frame.setObjectName("menuFrame")
        
        # Menu frame layout
        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title and toggle button container
        title_container = QHBoxLayout()
        
        # Menu title
        self.menu_title = QLabel("Game Menu")
        self.menu_title.setObjectName("menuTitle")
        self.menu_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_container.addWidget(self.menu_title)
        
        # Toggle button
        self.toggle_btn = QPushButton("☰ Menu")
        self.toggle_btn.setObjectName("toggleButton")
        self.toggle_btn.clicked.connect(self._toggle_dropdown)
        title_container.addWidget(self.toggle_btn)
        
        menu_layout.addLayout(title_container)
        
        # Current game info area (placeholder)
        self.game_info_label = QLabel("No game loaded")
        self.game_info_label.setObjectName("gameInfoLabel")
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.game_info_label)
        
        # === DROPDOWN MENU ===
        self.dropdown_frame = QFrame()
        self.dropdown_frame.setFixedSize(648, 300)
        self.dropdown_frame.setObjectName("dropdownFrame")
        self.dropdown_frame.hide()  # Hidden by default
        
        # Dropdown layout
        dropdown_layout = QVBoxLayout(self.dropdown_frame)
        dropdown_layout.setContentsMargins(15, 15, 15, 15)
        dropdown_layout.setSpacing(10)
        
        # Menu buttons
        self.create_character_btn = QPushButton("Create Character")
        self.create_character_btn.clicked.connect(self.create_character_requested.emit)
        dropdown_layout.addWidget(self.create_character_btn)
        
        self.load_game_btn = QPushButton("Load Game")
        self.load_game_btn.clicked.connect(self.load_game_requested.emit)
        dropdown_layout.addWidget(self.load_game_btn)
        
        self.save_and_exit_btn = QPushButton("Save & Exit")
        self.save_and_exit_btn.clicked.connect(self.save_and_exit_requested.emit)
        dropdown_layout.addWidget(self.save_and_exit_btn)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        dropdown_layout.addWidget(separator)
        
        self.archive_character_btn = QPushButton("Archive Character")
        self.archive_character_btn.clicked.connect(self.archive_character_requested.emit)
        dropdown_layout.addWidget(self.archive_character_btn)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        dropdown_layout.addWidget(self.settings_btn)
        
        self.campaign_frame_btn = QPushButton("Campaign Frame")
        self.campaign_frame_btn.clicked.connect(self.campaign_frame_requested.emit)
        dropdown_layout.addWidget(self.campaign_frame_btn)
        
        # Add frames to main layout
        self.main_layout.addWidget(self.menu_frame)
        self.main_layout.addWidget(self.dropdown_frame)
    
    def _apply_styles(self):
        """Apply dark theme styling to menu components."""
        style_sheet = """
        QFrame#menuFrame {
            background-color: #2d2d2d;
            border: 2px solid #666666;
            border-radius: 8px;
        }
        
        QFrame#dropdownFrame {
            background-color: #3d3d3d;
            border: 2px solid #666666;
            border-radius: 8px;
            border-top: none;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
        }
        
        QLabel#menuTitle {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 5px;
        }
        
        QLabel#gameInfoLabel {
            color: #cccccc;
            font-size: 12px;
            padding: 10px;
        }
        
        QPushButton#toggleButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            max-width: 100px;
        }
        
        QPushButton#toggleButton:hover {
            background-color: #505050;
        }
        
        QPushButton#toggleButton:pressed {
            background-color: #303030;
        }
        
        QPushButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 10px;
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
    
    def _toggle_dropdown(self):
        """Toggle the dropdown menu visibility."""
        self.dropdown_visible = not self.dropdown_visible
        self.dropdown_frame.setVisible(self.dropdown_visible)
        
        # Update toggle button text
        if self.dropdown_visible:
            self.toggle_btn.setText("✕ Close")
        else:
            self.toggle_btn.setText("☰ Menu")
    
    def update_game_info(self, character_name: Optional[str] = None, 
                        save_slot: Optional[int] = None):
        """Update the game info display."""
        if character_name and save_slot:
            self.game_info_label.setText(f"Playing: {character_name} (Slot {save_slot})")
        elif character_name:
            self.game_info_label.setText(f"Playing: {character_name}")
        else:
            self.game_info_label.setText("No game loaded")
    
    def set_save_enabled(self, enabled: bool):
        """Enable/disable the save & exit button based on game state."""
        self.save_and_exit_btn.setEnabled(enabled)
    
    def set_character_loaded(self, loaded: bool):
        """Enable/disable character-dependent buttons based on whether a character is loaded."""
        self.save_and_exit_btn.setEnabled(loaded)
        self.archive_character_btn.setEnabled(loaded)
    
    def close_dropdown(self):
        """Close the dropdown menu."""
        if self.dropdown_visible:
            self._toggle_dropdown()