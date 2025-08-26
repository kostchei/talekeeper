"""
Encounter Pane Widget - Central content area for encounters and exploration

PyQt6 widget that serves as the main content display area:
- Monster/NPC encounters
- Story text and descriptions
- Environmental details
- Combat interfaces
- Exploration content

Designed to match ui_plan.md specifications:
- Fixed size: 648x972 (center panel)
- Flexible content display
- Dark theme styling
- Integration ready for GameEngine encounter data
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTextEdit, QScrollArea,
                            QTabWidget, QListWidget, QListWidgetItem,
                            QSplitter, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any


class EncounterPanel(QWidget):
    """
    Central encounter display widget.
    
    Signals:
        encounter_action_requested: Emitted when encounter action is requested (str action)
        combat_initiated: Emitted when combat is started (dict encounter_data)
        exploration_action: Emitted when exploration action is taken (str action)
    """
    
    encounter_action_requested = pyqtSignal(str)
    combat_initiated = pyqtSignal(dict)
    exploration_action = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_encounter = None
        self.encounter_mode = "exploration"  # exploration, encounter, combat
        
        # Set fixed size (fits above action cards)
        self.setFixedSize(648, 672)  # 726 - 54 = 672px available space
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the encounter panel UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        self.title_label = QLabel("Exploration")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Mode indicator
        self.mode_label = QLabel("Exploring")
        self.mode_label.setObjectName("modeLabel")
        header_layout.addWidget(self.mode_label)
        
        # === CONTENT TABS ===
        self.content_tabs = QTabWidget()
        self.content_tabs.setObjectName("contentTabs")
        
        # --- MAIN CONTENT TAB ---
        self.main_content_tab = QWidget()
        self.content_tabs.addTab(self.main_content_tab, "Scene")
        
        main_content_layout = QVBoxLayout(self.main_content_tab)
        main_content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Scene description area
        self.scene_text = QTextEdit()
        self.scene_text.setObjectName("sceneText")
        self.scene_text.setReadOnly(True)
        self.scene_text.setPlainText("You find yourself in a dimly lit chamber. The air is thick with mystery and adventure awaits...")
        main_content_layout.addWidget(self.scene_text, 2)
        
        # Action buttons frame
        self.action_buttons_frame = QFrame()
        self.action_buttons_frame.setObjectName("actionButtonsFrame")
        action_buttons_layout = QHBoxLayout(self.action_buttons_frame)
        
        self.investigate_btn = QPushButton("Investigate")
        self.investigate_btn.clicked.connect(lambda: self.exploration_action.emit("investigate"))
        action_buttons_layout.addWidget(self.investigate_btn)
        
        self.rest_btn = QPushButton("Rest")
        self.rest_btn.clicked.connect(lambda: self.exploration_action.emit("rest"))
        action_buttons_layout.addWidget(self.rest_btn)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(lambda: self.exploration_action.emit("search"))
        action_buttons_layout.addWidget(self.search_btn)
        
        main_content_layout.addWidget(self.action_buttons_frame)
        
        # --- ENCOUNTERS TAB ---
        self.encounters_tab = QWidget()
        self.content_tabs.addTab(self.encounters_tab, "Encounters")
        
        encounters_layout = QVBoxLayout(self.encounters_tab)
        encounters_layout.setContentsMargins(5, 5, 5, 5)
        
        # Active encounters list
        self.encounters_label = QLabel("Active Encounters")
        self.encounters_label.setObjectName("sectionLabel")
        encounters_layout.addWidget(self.encounters_label)
        
        self.encounters_list = QListWidget()
        self.encounters_list.setObjectName("encountersList")
        encounters_layout.addWidget(self.encounters_list)
        
        # Combat controls
        self.combat_controls_frame = QFrame()
        self.combat_controls_frame.setObjectName("combatControlsFrame")
        combat_layout = QHBoxLayout(self.combat_controls_frame)
        
        self.initiative_btn = QPushButton("Roll Initiative")
        self.initiative_btn.clicked.connect(lambda: self.encounter_action_requested.emit("initiative"))
        combat_layout.addWidget(self.initiative_btn)
        
        self.start_combat_btn = QPushButton("Start Combat")
        self.start_combat_btn.clicked.connect(self._start_combat)
        combat_layout.addWidget(self.start_combat_btn)
        
        encounters_layout.addWidget(self.combat_controls_frame)
        
        # --- ENVIRONMENT TAB ---
        self.environment_tab = QWidget()
        self.content_tabs.addTab(self.environment_tab, "Environment")
        
        env_layout = QVBoxLayout(self.environment_tab)
        env_layout.setContentsMargins(5, 5, 5, 5)
        
        # Environment details
        self.environment_text = QTextEdit()
        self.environment_text.setObjectName("environmentText")
        self.environment_text.setReadOnly(True)
        self.environment_text.setPlainText("Environment details and hazards will be displayed here...")
        env_layout.addWidget(self.environment_text)
        
        # Environmental action buttons
        self.env_actions_frame = QFrame()
        env_actions_layout = QHBoxLayout(self.env_actions_frame)
        
        self.climb_btn = QPushButton("Climb")
        self.climb_btn.clicked.connect(lambda: self.exploration_action.emit("climb"))
        env_actions_layout.addWidget(self.climb_btn)
        
        self.swim_btn = QPushButton("Swim") 
        self.swim_btn.clicked.connect(lambda: self.exploration_action.emit("swim"))
        env_actions_layout.addWidget(self.swim_btn)
        
        self.hide_btn = QPushButton("Hide")
        self.hide_btn.clicked.connect(lambda: self.exploration_action.emit("hide"))
        env_actions_layout.addWidget(self.hide_btn)
        
        env_layout.addWidget(self.env_actions_frame)
        
        # === STATUS BAR ===
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusFrame")
        self.status_frame.setFixedHeight(40)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("Ready for adventure")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Difficulty indicator
        self.difficulty_label = QLabel("Normal")
        self.difficulty_label.setObjectName("difficultyLabel")
        status_layout.addWidget(self.difficulty_label)
        
        # Add components to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.content_tabs, 1)
        self.main_layout.addWidget(self.status_frame)
    
    def _apply_styles(self):
        """Apply dark theme styling to encounter panel components."""
        style_sheet = """
        EncounterPanel {
            background-color: #101010;
        }
        
        QFrame#headerFrame {
            background-color: #1a1a1a;
            border: 1px solid #444444;
            border-radius: 6px;
        }
        
        QFrame#actionButtonsFrame, QFrame#combatControlsFrame {
            background-color: #1e1e1e;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 5px;
        }
        
        QFrame#statusFrame {
            background-color: #1a1a1a;
            border: 1px solid #444444;
            border-radius: 6px;
        }
        
        QLabel#titleLabel {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
        }
        
        QLabel#modeLabel {
            color: #4a90e2;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 8px;
            border: 1px solid #4a90e2;
            border-radius: 3px;
        }
        
        QLabel#sectionLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        }
        
        QLabel#statusLabel {
            color: #cccccc;
            font-size: 12px;
        }
        
        QLabel#difficultyLabel {
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
            padding: 2px 6px;
            border: 1px solid #666666;
            border-radius: 3px;
            background-color: #2a2a2a;
        }
        
        QTabWidget#contentTabs {
            background-color: transparent;
        }
        
        QTabWidget#contentTabs::pane {
            border: 1px solid #444444;
            border-radius: 4px;
            background-color: #1a1a1a;
        }
        
        QTabWidget#contentTabs::tab-bar {
            alignment: left;
        }
        
        QTabBar::tab {
            background-color: #2a2a2a;
            color: #cccccc;
            border: 1px solid #444444;
            border-bottom: none;
            border-radius: 4px 4px 0px 0px;
            padding: 6px 12px;
            margin: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #1a1a1a;
            color: #ffffff;
            border-bottom: 1px solid #1a1a1a;
        }
        
        QTabBar::tab:hover {
            background-color: #3a3a3a;
        }
        
        QTextEdit#sceneText, QTextEdit#environmentText {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 8px;
            font-size: 13px;
            line-height: 1.4;
        }
        
        QListWidget#encountersList {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            alternate-background-color: #1a1a1a;
        }
        
        QListWidget#encountersList::item {
            padding: 8px;
            border-bottom: 1px solid #333333;
        }
        
        QListWidget#encountersList::item:selected {
            background-color: #4a90e2;
            color: #ffffff;
        }
        
        QListWidget#encountersList::item:hover {
            background-color: #2a2a2a;
        }
        
        QPushButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px 12px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #303030;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
        }
        """
        self.setStyleSheet(style_sheet)
    
    def set_exploration_mode(self):
        """Switch to exploration mode."""
        self.encounter_mode = "exploration"
        self.title_label.setText("Exploration")
        self.mode_label.setText("Exploring")
        self.mode_label.setStyleSheet("color: #4a90e2; border-color: #4a90e2;")
        self.content_tabs.setCurrentIndex(0)  # Scene tab
        self._update_action_buttons()
    
    def set_encounter_mode(self):
        """Switch to encounter mode."""
        self.encounter_mode = "encounter"
        self.title_label.setText("Encounter")
        self.mode_label.setText("Encounter")
        self.mode_label.setStyleSheet("color: #ff9500; border-color: #ff9500;")
        self.content_tabs.setCurrentIndex(1)  # Encounters tab
        self._update_action_buttons()
    
    def set_combat_mode(self):
        """Switch to combat mode."""
        self.encounter_mode = "combat"
        self.title_label.setText("Combat")
        self.mode_label.setText("In Combat")
        self.mode_label.setStyleSheet("color: #ff4444; border-color: #ff4444;")
        self.content_tabs.setCurrentIndex(1)  # Encounters tab
        self._update_action_buttons()
    
    def _update_action_buttons(self):
        """Update button states based on current mode."""
        exploration_mode = self.encounter_mode == "exploration"
        encounter_mode = self.encounter_mode == "encounter"
        combat_mode = self.encounter_mode == "combat"
        
        # Main content buttons
        self.investigate_btn.setEnabled(exploration_mode)
        self.rest_btn.setEnabled(not combat_mode)
        self.search_btn.setEnabled(exploration_mode)
        
        # Combat buttons
        self.initiative_btn.setEnabled(encounter_mode)
        self.start_combat_btn.setEnabled(encounter_mode)
        
        # Environment buttons
        self.climb_btn.setEnabled(not combat_mode)
        self.swim_btn.setEnabled(not combat_mode)
        self.hide_btn.setEnabled(not combat_mode)
    
    def update_scene_description(self, description: str):
        """Update the main scene description."""
        self.scene_text.setPlainText(description)
    
    def update_environment_details(self, details: str):
        """Update environmental information."""
        self.environment_text.setPlainText(details)
    
    def add_encounter(self, encounter_data: Dict[str, Any]):
        """Add an encounter to the list."""
        encounter_name = encounter_data.get('name', 'Unknown Encounter')
        difficulty = encounter_data.get('difficulty', 'Normal')
        
        item = QListWidgetItem(f"{encounter_name} ({difficulty})")
        item.setData(Qt.ItemDataRole.UserRole, encounter_data)
        self.encounters_list.addItem(item)
        
        # Switch to encounter mode if not in combat
        if self.encounter_mode != "combat":
            self.set_encounter_mode()
    
    def clear_encounters(self):
        """Clear all encounters from the list."""
        self.encounters_list.clear()
        if self.encounter_mode in ["encounter", "combat"]:
            self.set_exploration_mode()
    
    def _start_combat(self):
        """Start combat with selected encounter."""
        current_item = self.encounters_list.currentItem()
        if current_item:
            encounter_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.set_combat_mode()
            self.combat_initiated.emit(encounter_data)
        else:
            self.update_status("No encounter selected for combat")
    
    def update_status(self, status: str):
        """Update the status message."""
        self.status_label.setText(status)
    
    def set_difficulty(self, difficulty: str):
        """Set the difficulty indicator."""
        self.difficulty_label.setText(difficulty)
        
        # Color code difficulty
        color_map = {
            "Easy": "#4a9",
            "Normal": "#ffffff", 
            "Hard": "#ff9500",
            "Deadly": "#ff4444"
        }
        color = color_map.get(difficulty, "#ffffff")
        self.difficulty_label.setStyleSheet(
            f"color: {color}; border-color: {color}; background-color: #2a2a2a;"
        )
    
    def get_current_mode(self) -> str:
        """Get the current encounter mode."""
        return self.encounter_mode
    
    def get_selected_encounter(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected encounter data."""
        current_item = self.encounters_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None