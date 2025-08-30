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
                            QSplitter, QGroupBox, QGridLayout, QComboBox,
                            QSpinBox, QCheckBox, QStackedWidget, QRadioButton,
                            QButtonGroup, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any
import json
import os
import random
from uuid import uuid4
from .encounter_generator import EncounterGenerator, CampaignFrame, roll_monster_hp
from models.monsters_indexeddb import EncounterInstance, Encounter


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
    character_created = pyqtSignal(dict)  # Emitted when character creation is complete
    monster_selected = pyqtSignal(str)  # Emitted when monster card is selected (instance_id)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_encounter = None
        self.encounter_mode = "exploration"  # exploration, encounter, combat, character_creation
        self.character_creation_data = {}  # Store character creation progress
        self.creation_step = 0  # Track current creation step
        
        # Initialize encounter generator
        self.encounter_generator = None
        self._load_campaign_frame()
        
        # Track current encounter instances
        self.current_encounter_id = None
        self.encounter_instances = {}  # instance_id -> EncounterInstance
        self.selected_monster_id = None  # Currently selected monster for targeting
        self.current_encounter = None  # Current Encounter object for database tracking
        
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
        
        # === CONTENT TABS ===
        self.content_tabs = QTabWidget()
        self.content_tabs.setObjectName("contentTabs")
        
        # --- MAIN CONTENT TAB ---
        self.main_content_tab = QWidget()
        self.content_tabs.addTab(self.main_content_tab, "Scene")
        
        main_content_layout = QVBoxLayout(self.main_content_tab)
        main_content_layout.setContentsMargins(1, 1, 1, 1)
        
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
        encounters_layout.setContentsMargins(1, 1, 1, 1)
        
        
        # Generate encounter button
        self.generate_encounter_btn = QPushButton("Generate Random Encounter")
        self.generate_encounter_btn.clicked.connect(self._generate_encounter)
        encounters_layout.addWidget(self.generate_encounter_btn)
        
        # Monster cards container (grid layout for multiple rows)
        self.monsters_frame = QFrame()
        self.monsters_frame.setObjectName("monstersFrame")
        from PyQt6.QtWidgets import QGridLayout
        self.monsters_layout = QGridLayout(self.monsters_frame)
        self.monsters_layout.setContentsMargins(1, 1, 1, 1)
        self.monsters_layout.setSpacing(5)
        self.monsters_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        encounters_layout.addWidget(self.monsters_frame)
        
        
        # --- ENVIRONMENT TAB ---
        self.environment_tab = QWidget()
        self.content_tabs.addTab(self.environment_tab, "Environment")
        
        env_layout = QVBoxLayout(self.environment_tab)
        env_layout.setContentsMargins(1, 1, 1, 1)
        
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
        
        # --- CHARACTER CREATION TAB ---
        self.character_creation_tab = QWidget()
        self.content_tabs.addTab(self.character_creation_tab, "Create Character")
        self.content_tabs.setTabVisible(3, False)  # Hidden initially
        
        creation_layout = QVBoxLayout(self.character_creation_tab)
        creation_layout.setContentsMargins(1, 1, 1, 1)
        
        # Character creation stacked widget for different steps
        self.creation_stack = QStackedWidget()
        creation_layout.addWidget(self.creation_stack, 1)
        
        # Navigation buttons
        self.creation_nav_frame = QFrame()
        creation_nav_layout = QHBoxLayout(self.creation_nav_frame)
        
        self.creation_back_btn = QPushButton("Back")
        self.creation_back_btn.clicked.connect(self._creation_previous_step)
        creation_nav_layout.addWidget(self.creation_back_btn)
        
        creation_nav_layout.addStretch()
        
        self.creation_step_label = QLabel("Step 1 of 6")
        creation_nav_layout.addWidget(self.creation_step_label)
        
        creation_nav_layout.addStretch()
        
        self.creation_next_btn = QPushButton("Next")
        self.creation_next_btn.clicked.connect(self._creation_next_step)
        creation_nav_layout.addWidget(self.creation_next_btn)
        
        creation_layout.addWidget(self.creation_nav_frame)
        
        self._setup_character_creation_steps()
        
        # Add components to main layout
        self.main_layout.addWidget(self.content_tabs, 1)
    
    def _apply_styles(self):
        """Apply dark theme styling to encounter panel components."""
        style_sheet = """
        EncounterPanel {
            background-color: #101010;
        }
        
        QFrame#actionButtonsFrame, QFrame#combatControlsFrame {
            background-color: #1e1e1e;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 5px;
        }
        
        QLabel#sectionLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
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
        
        /* Character Creation Styles */
        QLabel#creationStepTitle {
            color: #50c878;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 0px;
        }
        
        QListWidget#classSelectionList, QListWidget#backgroundList, QListWidget#speciesList, QListWidget#equipmentList {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            alternate-background-color: #1a1a1a;
        }
        
        QListWidget#classSelectionList::item, QListWidget#backgroundList::item, QListWidget#speciesList::item {
            padding: 8px;
            border-bottom: 1px solid #333333;
        }
        
        QListWidget#classSelectionList::item:selected, QListWidget#backgroundList::item:selected, QListWidget#speciesList::item:selected {
            background-color: #50c878;
            color: #ffffff;
        }
        
        QTextEdit#classDescription, QTextEdit#bgSpeciesDescription, QTextEdit#reviewSummary {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 8px;
            font-size: 12px;
        }
        
        QLabel#racialBonus {
            color: #50c878;
            font-weight: bold;
        }
        
        QLabel#finalScore {
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
        }
        
        QLabel#pointsRemaining {
            color: #ff9500;
            font-weight: bold;
            padding: 10px 0px;
        }
        
        QLabel#classStatsInfo {
            color: #4a90e2;
            font-weight: bold;
            padding: 5px 0px;
            background-color: #1e1e1e;
            border: 1px solid #4a90e2;
            border-radius: 4px;
            padding: 8px;
        }
        
        QLabel#rolledScore {
            color: #ff9500;
            font-weight: bold;
            font-size: 12px;
        }
        
        QLabel#abilityAbbrev {
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
            padding: 4px;
        }
        
        QPushButton#createCharacterBtn {
            background-color: #50c878;
            color: #ffffff;
            border: 1px solid #50c878;
            border-radius: 6px;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        QPushButton#createCharacterBtn:hover {
            background-color: #45b567;
        }
        
        QPushButton#createCharacterBtn:pressed {
            background-color: #3a9954;
        }
        
        /* Monster Card Styles - Matching Action Card Aesthetic */
        QFrame#monsterCard {
            background-color: #2d2d2d;
            border: 2px solid #555555;
            border-radius: 8px;
        }
        
        QFrame#monsterCard:hover {
            border-color: #4a90e2;
        }
        
        QFrame#monsterCard[selected="true"] {
            border-color: #4a90e2;
            border-width: 3px;
            background-color: #3d3d4d;
        }
        
        QFrame#monstersFrame {
            background-color: transparent;
            border: none;
        }
        
        QLabel#monsterName {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
        }
        
        QLabel#monsterCR {
            color: #cccccc;
            font-size: 9px;
        }
        
        QLabel#monsterType {
            color: #cccccc;
            font-size: 9px;
        }
        
        QLabel#monsterImage {
            background-color: #1a1a1a;
            border: 1px solid #444444;
            border-radius: 4px;
            color: #666666;
            font-size: 9px;
        }
        """
        self.setStyleSheet(style_sheet)
    
    def update_theme(self, theme_name: str):
        """Update styling based on theme."""
        from ui.themes import get_theme_palette
        palette = get_theme_palette(theme_name)
        
        style_sheet = f"""
        EncounterPanel {{
            background-color: {palette['background']};
            border: 2px solid {palette['border']};
            border-radius: 8px;
        }}
        
        QFrame#contentFrame {{
            background-color: {palette['background']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {palette['border']};
            background-color: {palette['surface']};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {palette['surface']};
            color: {palette['text']};
            padding: 6px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            border: 1px solid {palette['border']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {palette['accent_primary']};
            border-bottom-color: {palette['accent_primary']};
        }}
        
        QTextEdit {{
            background-color: {palette['background']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            font-size: 12px;
            selection-background-color: {palette['selection']};
            alternate-background-color: {palette['highlight']};
        }}
        
        QListWidget {{
            background-color: {palette['background']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            alternate-background-color: {palette['highlight']};
            selection-background-color: {palette['selection']};
            selection-color: {palette['text']};
        }}
        
        QListWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {palette['border']};
        }}
        
        QPushButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {palette['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {palette['button_pressed']};
        }}
        
        QPushButton#rollButton {{
            background-color: {palette['accent_tertiary']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        QPushButton#rollButton:hover {{
            background-color: {palette['accent_secondary']};
        }}
        
        QPushButton#rollButton:pressed {{
            background-color: {palette['accent_primary']};
        }}
        """
        self.setStyleSheet(style_sheet)
    
    def set_exploration_mode(self):
        """Switch to exploration mode."""
        self.encounter_mode = "exploration"
        # self.title_label.setText("Exploration")
        # self.mode_label.setText("Exploring")
        # self.mode_label.setStyleSheet("color: #4a90e2; border-color: #4a90e2;")
        self.content_tabs.setCurrentIndex(0)  # Scene tab
        self._update_action_buttons()
    
    def set_encounter_mode(self):
        """Switch to encounter mode."""
        self.encounter_mode = "encounter"
        # self.title_label.setText("Encounter")
        # self.mode_label.setText("Encounter")
        # self.mode_label.setStyleSheet("color: #ff9500; border-color: #ff9500;")
        self.content_tabs.setCurrentIndex(1)  # Encounters tab
        self._update_action_buttons()
    
    def set_combat_mode(self):
        """Switch to combat mode."""
        self.encounter_mode = "combat"
        # self.title_label.setText("Combat")
        # self.mode_label.setText("In Combat")
        # self.mode_label.setStyleSheet("color: #ff4444; border-color: #ff4444;")
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
        
        # Combat buttons (removed - combat now starts automatically)
        
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
        """Clear all encounters."""
        self._clear_monster_cards()
        self.encounter_instances = {}
        self.current_encounter_id = None
        self.current_encounter = None  # Clear encounter tracking
        self.selected_monster_id = None  # Clear selection
        if self.encounter_mode in ["encounter", "combat"]:
            self.set_exploration_mode()
    
    def _start_combat(self):
        """Start combat with current encounter."""
        if self.encounter_instances and self.current_encounter_id:
            # Create encounter data from current instances
            encounter_data = {
                'encounter_id': self.current_encounter_id,
                'monsters': [instance.to_dict() for instance in self.encounter_instances.values()],
                'living_count': len(self.get_living_monsters())
            }
            self.set_combat_mode()
            self.combat_initiated.emit(encounter_data)
        else:
            self.update_status("No active encounter to start combat with")
    
    def update_status(self, status: str):
        """Update the status message."""
        # self.status_label.setText(status)
        pass
    
    def set_difficulty(self, difficulty: str):
        """Set the difficulty indicator."""
        # self.difficulty_label.setText(difficulty)
        # 
        # # Color code difficulty
        # color_map = {
        #     "Easy": "#4a9",
        #     "Normal": "#ffffff", 
        #     "Hard": "#ff9500",
        #     "Deadly": "#ff4444"
        # }
        # color = color_map.get(difficulty, "#ffffff")
        # self.difficulty_label.setStyleSheet(
        #     f"color: {color}; border-color: {color}; background-color: #2a2a2a;"
        # )
        pass
    
    def get_current_mode(self) -> str:
        """Get the current encounter mode."""
        return self.encounter_mode
    
    def get_selected_encounter(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected encounter data."""
        current_item = self.encounters_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    # === CHARACTER CREATION METHODS ===
    
    def set_character_creation_mode(self):
        """Switch to character creation mode."""
        self.encounter_mode = "character_creation"
        # self.title_label.setText("Create Character")
        # self.mode_label.setText("Character Creation")
        # self.mode_label.setStyleSheet("color: #50c878; border-color: #50c878;")
        self.content_tabs.setTabVisible(3, True)  # Show character creation tab
        self.content_tabs.setCurrentIndex(3)  # Switch to character creation tab
        self.creation_step = 0
        self.character_creation_data = {}
        # Reset 4d6 rolling for new character
        if hasattr(self, 'has_rolled_4d6'):
            self.has_rolled_4d6 = False
        if hasattr(self, 'roll_4d6_btn'):
            self.roll_4d6_btn.setEnabled(True)
            self.roll_4d6_btn.setText("Roll 4d6 Drop Lowest (One Time Only)")
        self._update_creation_step()
    
    def exit_character_creation(self):
        """Exit character creation and return to exploration."""
        self.content_tabs.setTabVisible(3, False)  # Hide character creation tab
        self.set_exploration_mode()
        self.creation_step = 0
        self.character_creation_data = {}
    
    def _setup_character_creation_steps(self):
        """Setup the character creation step widgets."""
        # Step 1: Class Selection
        self.class_step = self._create_class_selection_step()
        self.creation_stack.addWidget(self.class_step)
        
        # Step 2: Class Features (Fighter-specific features)
        self.class_features_step = self._create_class_features_step()
        self.creation_stack.addWidget(self.class_features_step)
        
        # Step 3: Background & Species
        self.bg_species_step = self._create_background_species_step()
        self.creation_stack.addWidget(self.bg_species_step)
        
        # Step 4: Ability Scores
        self.abilities_step = self._create_abilities_step()
        self.creation_stack.addWidget(self.abilities_step)
        
        # Step 5: Equipment
        self.equipment_step = self._create_equipment_step()
        self.creation_stack.addWidget(self.equipment_step)
        
        # Step 6: Final Review
        self.review_step = self._create_review_step()
        self.creation_stack.addWidget(self.review_step)
    
    def _create_class_selection_step(self) -> QWidget:
        """Create the class selection step widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Choose Your Class")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Class selection list
        self.class_list = QListWidget()
        self.class_list.setObjectName("classSelectionList")
        
        # Load class data and populate list
        self._load_class_data()
        
        layout.addWidget(self.class_list)
        
        # Class description
        self.class_description = QTextEdit()
        self.class_description.setObjectName("classDescription")
        self.class_description.setMaximumHeight(120)
        self.class_description.setReadOnly(True)
        layout.addWidget(self.class_description)
        
        # Connect selection change
        self.class_list.currentItemChanged.connect(self._on_class_selected)
        
        return widget
    
    def _create_class_features_step(self) -> QWidget:
        """Create the class features selection step."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Class Features")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Info text
        info_label = QLabel("Configure your class-specific features.")
        info_label.setObjectName("stepDescription")
        layout.addWidget(info_label)
        
        # Class features container (will be populated based on selected class)
        self.class_features_container = QWidget()
        self.class_features_layout = QVBoxLayout(self.class_features_container)
        layout.addWidget(self.class_features_container)
        
        # Spacer
        layout.addStretch()
        
        return widget
    
    def _create_background_species_step(self) -> QWidget:
        """Create background and species selection step."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Choose Background & Species")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Horizontal split for background and species
        content_layout = QHBoxLayout()
        
        # Background section
        bg_frame = QFrame()
        bg_layout = QVBoxLayout(bg_frame)
        
        bg_label = QLabel("Background")
        bg_label.setObjectName("sectionLabel")
        bg_layout.addWidget(bg_label)
        
        self.background_list = QListWidget()
        self.background_list.setObjectName("backgroundList")
        bg_layout.addWidget(self.background_list)
        
        # Species section
        species_frame = QFrame()
        species_layout = QVBoxLayout(species_frame)
        
        species_label = QLabel("Species (Race)")
        species_label.setObjectName("sectionLabel")
        species_layout.addWidget(species_label)
        
        self.species_list = QListWidget()
        self.species_list.setObjectName("speciesList")
        species_layout.addWidget(self.species_list)
        
        content_layout.addWidget(bg_frame)
        content_layout.addWidget(species_frame)
        layout.addLayout(content_layout)
        
        # Feat selection section
        feat_frame = QFrame()
        feat_layout = QVBoxLayout(feat_frame)
        
        # Background origin feat
        bg_feat_label = QLabel("Background Origin Feat")
        bg_feat_label.setObjectName("sectionLabel")
        feat_layout.addWidget(bg_feat_label)
        
        self.background_feat_combo = QComboBox()
        self.background_feat_combo.setObjectName("backgroundFeatCombo")
        feat_layout.addWidget(self.background_feat_combo)
        
        # Species bonus feat (shown only for humans)
        self.species_feat_label = QLabel("Species Bonus Feat")
        self.species_feat_label.setObjectName("sectionLabel")
        self.species_feat_label.hide()  # Initially hidden
        feat_layout.addWidget(self.species_feat_label)
        
        self.species_feat_combo = QComboBox()
        self.species_feat_combo.setObjectName("speciesFeatCombo")
        self.species_feat_combo.hide()  # Initially hidden
        feat_layout.addWidget(self.species_feat_combo)
        
        # Feat description area
        self.feat_description = QTextEdit()
        self.feat_description.setObjectName("featDescription")
        self.feat_description.setMaximumHeight(120)
        self.feat_description.setReadOnly(True)
        self.feat_description.setPlaceholderText("Select a feat to see its description...")
        feat_layout.addWidget(self.feat_description)
        
        content_layout.addWidget(feat_frame)
        
        # Description area (for background/species)
        self.bg_species_description = QTextEdit()
        self.bg_species_description.setObjectName("bgSpeciesDescription")
        self.bg_species_description.setMaximumHeight(100)
        self.bg_species_description.setReadOnly(True)
        layout.addWidget(self.bg_species_description)
        
        # Load data
        self._load_background_species_data()
        self._populate_feat_lists()
        
        # Connect signals
        self.background_list.currentItemChanged.connect(self._on_background_selected)
        self.species_list.currentItemChanged.connect(self._on_species_selected)
        
        return widget
    
    def _create_abilities_step(self) -> QWidget:
        """Create ability score assignment step."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Assign Ability Scores")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Instructions
        info_label = QLabel("Point buy system with class-based starting values")
        layout.addWidget(info_label)
        
        # Class info label
        self.class_stats_info = QLabel("Select a class first to see starting ability scores")
        self.class_stats_info.setObjectName("classStatsInfo")
        layout.addWidget(self.class_stats_info)
        
        # Ability score controls
        abilities_layout = QGridLayout()
        
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        ability_abbrevs = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        self.ability_spinboxes = {}
        self.racial_bonus_labels = {}
        self.final_score_labels = {}
        self.rolled_score_labels = {}  # For 4d6 results
        
        # Add column headers
        abilities_layout.addWidget(QLabel("Stat"), 0, 0)
        abilities_layout.addWidget(QLabel("Point Buy"), 0, 1)
        abilities_layout.addWidget(QLabel("Background"), 0, 2) 
        abilities_layout.addWidget(QLabel("Rolled"), 0, 3)
        abilities_layout.addWidget(QLabel("Final"), 0, 4)
        
        for i, ability in enumerate(abilities):
            row = i + 1  # Account for header row
            ability_lower = ability.lower()
            
            # Use abbreviation instead of full name
            label = QLabel(ability_abbrevs[i])
            label.setObjectName("abilityAbbrev")
            abilities_layout.addWidget(label, row, 0)
            
            spinbox = QSpinBox()
            spinbox.setMinimum(3)  # Allow down to 3 for dump stats
            spinbox.setMaximum(15)
            spinbox.setValue(8)
            spinbox.valueChanged.connect(self._on_ability_value_changed)
            self.ability_spinboxes[ability_lower] = spinbox
            abilities_layout.addWidget(spinbox, row, 1)
            
            # Show background bonus (D&D 2024)
            bonus_spinbox = QSpinBox()
            bonus_spinbox.setMinimum(0)
            bonus_spinbox.setMaximum(2)
            bonus_spinbox.setValue(0)
            bonus_spinbox.setObjectName("backgroundBonus")
            bonus_spinbox.valueChanged.connect(self._update_background_bonuses)
            self.racial_bonus_labels[ability_lower] = bonus_spinbox
            abilities_layout.addWidget(bonus_spinbox, row, 2)
            
            # Show rolled score (4d6 drop lowest)
            rolled_label = QLabel("-")
            rolled_label.setObjectName("rolledScore")
            self.rolled_score_labels[ability_lower] = rolled_label
            abilities_layout.addWidget(rolled_label, row, 3)
            
            # Final score (higher of point buy or rolled + racial)
            final_label = QLabel("8")
            final_label.setObjectName("finalScore")
            self.final_score_labels[ability_lower] = final_label
            abilities_layout.addWidget(final_label, row, 4)
        
        layout.addLayout(abilities_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Set class defaults button
        self.set_class_defaults_btn = QPushButton("Apply Class Defaults")
        self.set_class_defaults_btn.clicked.connect(self._apply_class_defaults)
        self.set_class_defaults_btn.setEnabled(False)
        controls_layout.addWidget(self.set_class_defaults_btn)
        
        controls_layout.addStretch()
        
        # Roll 4d6 button
        self.roll_4d6_btn = QPushButton("Roll 4d6 Drop Lowest (One Time Only)")
        self.roll_4d6_btn.clicked.connect(self._roll_4d6_overlay)
        self.has_rolled_4d6 = False  # Track if 4d6 has been used
        controls_layout.addWidget(self.roll_4d6_btn)
        
        layout.addLayout(controls_layout)
        
        # Points remaining
        self.points_remaining_label = QLabel("Points available: Calculate after setting defaults")
        self.points_remaining_label.setObjectName("pointsRemaining")
        layout.addWidget(self.points_remaining_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_equipment_step(self) -> QWidget:
        """Create equipment selection step."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Starting Equipment")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Equipment choices will be populated when class is selected
        self.equipment_choices_widget = QWidget()
        self.equipment_choices_layout = QVBoxLayout(self.equipment_choices_widget)
        layout.addWidget(self.equipment_choices_widget)
        
        # Add some default content
        self._populate_equipment_choices()
        
        layout.addStretch()
        return widget
    
    def _populate_equipment_choices(self):
        """Populate equipment choices based on selected class."""
        # Clear existing choices
        for i in reversed(range(self.equipment_choices_layout.count())):
            child = self.equipment_choices_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Check if class is selected
        selected_class_data = self.character_creation_data.get('class')
        if not selected_class_data:
            info_label = QLabel("Please select a class first.")
            info_label.setStyleSheet("color: #ff6b6b;")
            self.equipment_choices_layout.addWidget(info_label)
            return
        
        # Get class name
        selected_class_name = selected_class_data.get('name', '') if isinstance(selected_class_data, dict) else str(selected_class_data)
        
        # Test data for Fighter (you can expand this)
        equipment_choices = []
        if selected_class_name == "Fighter":
            equipment_choices = [
                {
                    "name": "Martial Weapon",
                    "options": ["Longsword (1d8 slashing)", "Greatsword (2d6 slashing)", "Rapier (1d8 piercing)"]
                },
                {
                    "name": "Armor",  
                    "options": ["Studded Leather (AC 12)", "Breastplate (AC 14)", "Chain Mail (AC 16)"]
                }
            ]
        
        if not equipment_choices:
            info_label = QLabel(f"No equipment choices available for {selected_class_name}.")
            self.equipment_choices_layout.addWidget(info_label)
            return
        
        # Create equipment choice widgets
        self.equipment_button_groups = {}  # Store button groups for each choice
        
        for choice in equipment_choices:
            # Choice group
            choice_group = QGroupBox(choice["name"])
            choice_layout = QVBoxLayout(choice_group)
            
            # Create button group to ensure only one selection per choice
            button_group = QButtonGroup(self)
            self.equipment_button_groups[choice["name"]] = button_group
            
            # Radio buttons for options
            for i, option in enumerate(choice["options"]):
                radio = QRadioButton(option)
                choice_layout.addWidget(radio)
                button_group.addButton(radio, i)
                
                # Select first option by default
                if i == 0:
                    radio.setChecked(True)
            
            self.equipment_choices_layout.addWidget(choice_group)
    
    def _populate_class_features(self):
        """Populate class-specific features based on selected class."""
        # Clear existing class features
        for i in reversed(range(self.class_features_layout.count())):
            child = self.class_features_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Check if class is selected
        selected_class_data = self.character_creation_data.get('class')
        if not selected_class_data:
            info_label = QLabel("Please select a class first.")
            info_label.setStyleSheet("color: #ff6b6b;")
            self.class_features_layout.addWidget(info_label)
            return
        
        # Get class name
        selected_class_name = selected_class_data.get('name', '') if isinstance(selected_class_data, dict) else str(selected_class_data)
        
        # Handle Fighter-specific features
        if selected_class_name == "Fighter":
            self._setup_fighter_features()
        else:
            # For non-Fighter classes, show placeholder text
            info_label = QLabel(f"{selected_class_name} class features will be implemented soon.")
            info_label.setStyleSheet("color: #888;")
            self.class_features_layout.addWidget(info_label)
    
    def _setup_fighter_features(self):
        """Setup Fighter Level 1 class features."""
        # Fighting Style selection
        fighting_style_group = QGroupBox("Fighting Style (Level 1)")
        fs_layout = QVBoxLayout(fighting_style_group)
        
        fs_description = QLabel("Choose a Fighting Style feat. This represents your martial training specialty.")
        fs_description.setWordWrap(True)
        fs_description.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        fs_layout.addWidget(fs_description)
        
        self.fighting_style_combo = QComboBox()
        self.fighting_style_combo.addItem("Select a Fighting Style...", None)
        
        # Load Fighting Style feats from feats_srd.json  
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            feats_file = os.path.join(project_root, "data", "feats_srd.json")
            
            with open(feats_file, 'r') as f:
                feats_data = json.load(f)
            
            feats = feats_data.get('feat', [])
            
            # Filter for Fighting Style feats (those that require "Fighting Style" feature)
            fighting_style_feats = []
            for feat in feats:
                prereqs = feat.get('prerequisite', [])
                for prereq in prereqs:
                    if isinstance(prereq, dict) and 'feature' in prereq:
                        if 'Fighting Style' in prereq['feature']:
                            fighting_style_feats.append(feat)
                            break
            
            # Add Fighting Style feats to combo box
            for feat in fighting_style_feats:
                feat_name = feat.get('name', 'Unknown Feat')
                self.fighting_style_combo.addItem(feat_name, feat)
                
        except Exception as e:
            print(f"Error loading Fighting Style feats: {e}")
            # Add fallback options
            fallback_styles = ["Archery", "Defense", "Dueling", "Great Weapon Fighting", "Protection", "Two-Weapon Fighting"]
            for style in fallback_styles:
                self.fighting_style_combo.addItem(style, {"name": style})
        
        fs_layout.addWidget(self.fighting_style_combo)
        
        # Fighting Style description
        self.fighting_style_description = QTextEdit()
        self.fighting_style_description.setMaximumHeight(100)
        self.fighting_style_description.setReadOnly(True)
        self.fighting_style_description.setHtml("<i>Select a Fighting Style to see its description.</i>")
        fs_layout.addWidget(self.fighting_style_description)
        
        # Connect selection handler
        self.fighting_style_combo.currentIndexChanged.connect(self._on_fighting_style_selected)
        
        self.class_features_layout.addWidget(fighting_style_group)
        
        
        # Weapon Mastery selection
        weapon_mastery_group = QGroupBox("Weapon Mastery")
        wm_layout = QVBoxLayout(weapon_mastery_group)
        wm_layout.setContentsMargins(1, 1, 1, 1)
        wm_layout.setSpacing(3)
        
        wm_description = QLabel("Choose 3:")
        wm_description.setWordWrap(True)
        wm_description.setStyleSheet("color: #666; font-size: 11px; margin: 1px;")
        wm_layout.addWidget(wm_description)
        
        # Create checkboxes for weapon masteries
        self.weapon_mastery_checkboxes = {}
        mastery_weapons = [
            ("Dagger", "Nick"), ("Handaxe", "Vex"), ("Javelin", "Slow"),
            ("Light Hammer", "Nick"), ("Scimitar", "Nick"), ("Shortsword", "Vex"),
            ("Battleaxe", "Topple"), ("Flail", "Sap"), ("Glaive", "Graze"),
            ("Greataxe", "Cleave"), ("Greatsword", "Graze"), ("Halberd", "Cleave"),
            ("Lance", "Topple"), ("Longsword", "Sap"), ("Maul", "Topple"),
            ("Morningstar", "Sap"), ("Pike", "Push"), ("Rapier", "Vex"),
            ("Scimitar", "Nick"), ("Shortsword", "Vex"), ("Trident", "Topple"),
            ("War Pick", "Sap"), ("Warhammer", "Push"), ("Whip", "Slow")
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_weapons = []
        for weapon, mastery in mastery_weapons:
            if weapon not in seen:
                unique_weapons.append((weapon, mastery))
                seen.add(weapon)
        
        # Create grid layout for checkboxes
        checkbox_widget = QWidget()
        checkbox_layout = QGridLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(1, 1, 1, 1)
        checkbox_layout.setSpacing(2)
        
        for i, (weapon, mastery) in enumerate(unique_weapons):
            checkbox = QCheckBox(f"{weapon} ({mastery})")
            checkbox.weapon_name = weapon
            checkbox.mastery = mastery
            checkbox.toggled.connect(self._on_weapon_mastery_changed)
            checkbox.setStyleSheet("font-size: 10px; margin: 1px;")
            
            # Add to layout (3 columns)
            row = i // 3
            col = i % 3
            checkbox_layout.addWidget(checkbox, row, col)
            
            self.weapon_mastery_checkboxes[weapon] = checkbox
        
        wm_layout.addWidget(checkbox_widget)
        
        # Add selection counter
        self.mastery_counter_label = QLabel("Selected: 0/3")
        self.mastery_counter_label.setStyleSheet("color: #888; font-weight: bold; font-size: 10px; margin: 1px;")
        wm_layout.addWidget(self.mastery_counter_label)
        
        self.class_features_layout.addWidget(weapon_mastery_group)
    
    def _on_fighting_style_selected(self):
        """Handle Fighting Style selection change."""
        fighting_style_data = self.fighting_style_combo.currentData()
        if fighting_style_data:
            # Update description
            entries = fighting_style_data.get('entries', [])
            if entries:
                description = f"<b>{fighting_style_data.get('name', 'Fighting Style')}</b><br><br>"
                description += "<br>".join(entries)
                self.fighting_style_description.setHtml(description)
            else:
                self.fighting_style_description.setHtml(f"<b>{fighting_style_data.get('name', 'Fighting Style')}</b><br><br>Description not available.")
        else:
            self.fighting_style_description.setHtml("<i>Select a Fighting Style to see its description.</i>")
    
    def _on_weapon_mastery_changed(self):
        """Handle weapon mastery checkbox selection changes."""
        if not hasattr(self, 'weapon_mastery_checkboxes'):
            return
            
        # Count selected masteries
        selected_count = sum(1 for checkbox in self.weapon_mastery_checkboxes.values() if checkbox.isChecked())
        
        # Update counter label
        self.mastery_counter_label.setText(f"Selected: {selected_count}/3")
        
        # Update label color based on selection
        if selected_count > 3:
            self.mastery_counter_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        elif selected_count == 3:
            self.mastery_counter_label.setStyleSheet("color: #44aa44; font-weight: bold;")
        else:
            self.mastery_counter_label.setStyleSheet("color: #888; font-weight: bold;")
        
        # Disable unchecked boxes if 3 are already selected
        if selected_count >= 3:
            for checkbox in self.weapon_mastery_checkboxes.values():
                if not checkbox.isChecked():
                    checkbox.setEnabled(False)
        else:
            # Re-enable all checkboxes
            for checkbox in self.weapon_mastery_checkboxes.values():
                checkbox.setEnabled(True)
    
    def _create_review_step(self) -> QWidget:
        """Create final review and confirmation step."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Review Character")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)
        
        # Character name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Character Name:"))
        self.character_name_input = QComboBox()
        self.character_name_input.setEditable(True)
        self.character_name_input.setCurrentText("Adventurer")
        name_layout.addWidget(self.character_name_input)
        layout.addLayout(name_layout)
        
        # Review summary
        self.review_summary = QTextEdit()
        self.review_summary.setObjectName("reviewSummary")
        self.review_summary.setReadOnly(True)
        layout.addWidget(self.review_summary)
        
        # Create character button
        self.create_character_btn = QPushButton("Create Character")
        self.create_character_btn.clicked.connect(self._finish_character_creation)
        self.create_character_btn.setObjectName("createCharacterBtn")
        layout.addWidget(self.create_character_btn)
        
        return widget
    
    def _load_class_data(self):
        """Load class data from JSON file."""
        try:
            # Get the absolute path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            classes_file = os.path.join(project_root, "data", "classes.json")
            
            with open(classes_file, 'r') as f:
                classes_data = json.load(f)
            
            for class_data in classes_data:
                item = QListWidgetItem(class_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, class_data)
                self.class_list.addItem(item)
        except Exception as e:
            print(f"Error loading class data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_background_species_data(self):
        """Load background and species data from JSON files."""
        try:
            # Get the absolute path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # Load backgrounds
            bg_file = os.path.join(project_root, "data", "backgrounds.json")
            with open(bg_file, 'r') as f:
                backgrounds_data = json.load(f)
            
            for bg_data in backgrounds_data:
                item = QListWidgetItem(bg_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, bg_data)
                self.background_list.addItem(item)
            
            # Load species/races
            races_file = os.path.join(project_root, "data", "races.json")
            with open(races_file, 'r') as f:
                races_data = json.load(f)
            
            for race_data in races_data:
                item = QListWidgetItem(race_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, race_data)
                self.species_list.addItem(item)
                
        except Exception as e:
            print(f"Error loading background/species data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_feats_data(self):
        """Load available feats from feats_srd.json."""
        try:
            # Get the absolute path to the scripts directory 
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            feats_file = os.path.join(project_root, "scripts", "feats_srd.json")
            
            with open(feats_file, 'r', encoding='utf-8') as f:
                feats_data = json.load(f)
            
            if 'feat' in feats_data:
                return feats_data['feat']
            else:
                print("No 'feat' key found in feats_srd.json")
                return []
                
        except Exception as e:
            print(f"Error loading feats data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _populate_feat_lists(self):
        """Populate the feat selection dropdowns with available feats."""
        try:
            feats = self._load_feats_data()
            if not feats:
                return
            
            # Clear existing items
            self.background_feat_combo.clear()
            self.species_feat_combo.clear()
            
            # Add placeholder option
            self.background_feat_combo.addItem("Select an origin feat...", None)
            self.species_feat_combo.addItem("Select a bonus feat...", None)
            
            # Filter and add origin-appropriate feats using category field
            for feat in feats:
                feat_name = feat.get('name', 'Unknown Feat')
                feat_category = feat.get('category', '')
                
                # Include only Origin feats (O) - Fighting Styles are class features, not origin feats
                if feat_category == 'O':
                    self.background_feat_combo.addItem(feat_name, feat)
                    self.species_feat_combo.addItem(feat_name, feat)
                elif not feat_category:  # Handle feats with no category
                    # Check if they have level prerequisites
                    prereqs = feat.get('prerequisite', [])
                    has_level_req = any('level' in req for req in prereqs if isinstance(req, dict))
                    if not has_level_req:
                        self.background_feat_combo.addItem(feat_name, feat)
                        self.species_feat_combo.addItem(feat_name, feat)
            
            # Connect selection handlers
            self.background_feat_combo.currentIndexChanged.connect(self._on_feat_selected)
            self.species_feat_combo.currentIndexChanged.connect(self._on_feat_selected)
            
        except Exception as e:
            print(f"Error populating feat lists: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_feat_selected(self):
        """Handle feat selection and update description."""
        sender = self.sender()
        if not sender:
            return
            
        feat_data = sender.currentData()
        if not feat_data:
            self.feat_description.clear()
            return
        
        # Format feat description
        feat_name = feat_data.get('name', 'Unknown Feat')
        feat_source = feat_data.get('source', 'Unknown')
        feat_category = feat_data.get('category', '')
        feat_entries = feat_data.get('entries', [])
        
        description = f"<h3>{feat_name}</h3>"
        description += f"<p><i>Source: {feat_source}</i></p>"
        
        # Show mechanical effects preview
        if feat_name == 'Tough':
            description += f"<p><b>Effect:</b> +2 hit points per character level</p>"
        elif feat_name == 'Linguist':
            description += f"<p><b>Effect:</b> +1 Intelligence, +3 languages</p>"
        elif feat_category == 'FS':
            description += f"<p><b>Effect:</b> Fighting style for combat</p>"
        elif feat_category == 'O':
            description += f"<p><b>Effect:</b> Origin feat with special abilities</p>"
        
        # Add feat description
        for entry in feat_entries:
            if isinstance(entry, str):
                description += f"<p>{entry}</p>"
            elif isinstance(entry, dict) and entry.get('type') == 'list':
                items = entry.get('items', [])
                if items:
                    description += "<ul>"
                    for item in items:
                        description += f"<li>{item}</li>"
                    description += "</ul>"
        
        self.feat_description.setHtml(description)
    
    def _on_class_selected(self, current, previous):
        """Handle class selection change."""
        if current:
            class_data = current.data(Qt.ItemDataRole.UserRole)
            self.character_creation_data['class'] = class_data  # Store the full class data
            
            description = f"**{class_data['name']}**\n\n"
            description += f"{class_data['description']}\n\n"
            description += f"Hit Die: d{class_data['hit_die']}\n"
            description += f"Primary Ability: {class_data['primary_ability']}\n"
            description += f"Saving Throws: {', '.join(class_data['saving_throw_proficiencies'])}"
            
            # Update equipment choices
            self._populate_equipment_choices()
            
            # Update class features
            self._populate_class_features()
            
            self.class_description.setPlainText(description)
            
            # Automatically apply class defaults when class is selected
            self._apply_class_defaults_auto()
            
            # Enable class defaults button if we have ability controls
            if hasattr(self, 'set_class_defaults_btn'):
                self.set_class_defaults_btn.setEnabled(True)
                
                # Update class info
                class_name = class_data['name'].lower()
                dump_stats = self._get_class_dump_stats(class_name)
                info_text = f"{class_data['name']} dump stat: {dump_stats['dump_stat'].title()} = 3 (auto-applied)"
                self.class_stats_info.setText(info_text)
    
    def _on_background_selected(self, current, previous):
        """Handle background selection change."""
        if current:
            bg_data = current.data(Qt.ItemDataRole.UserRole)
            self.character_creation_data['background'] = bg_data
            self._update_bg_species_description()
    
    def _on_species_selected(self, current, previous):
        """Handle species selection change."""
        if current:
            species_data = current.data(Qt.ItemDataRole.UserRole)
            self.character_creation_data['species'] = species_data
            self._update_bg_species_description()
            self._update_racial_bonuses()
            
            # Show/hide species bonus feat for humans
            species_name = species_data.get('name', '').lower()
            is_human = 'human' in species_name
            
            self.species_feat_label.setVisible(is_human)
            self.species_feat_combo.setVisible(is_human)
            
            # Reset species feat selection when changing species
            if not is_human:
                self.species_feat_combo.setCurrentIndex(0)
    
    def _update_bg_species_description(self):
        """Update the combined background/species description."""
        description = ""
        
        if 'background' in self.character_creation_data:
            bg = self.character_creation_data['background']
            description += f"**Background: {bg['name']}**\n{bg.get('description', '')}\n\n"
        
        if 'species' in self.character_creation_data:
            species = self.character_creation_data['species']
            description += f"**Species: {species['name']}**\n{species.get('description', '')}"
        
        self.bg_species_description.setPlainText(description)
    
    def _update_background_bonuses(self):
        """D&D 2024: Background provides up to 3 points distributed as +1/+1/+1 or +2/+1."""
        # Calculate total points used
        total_points = 0
        for ability in self.ability_spinboxes:
            bonus_spinbox = self.racial_bonus_labels[ability]
            total_points += bonus_spinbox.value()
        
        # Disable spinboxes if we've used all 3 points
        for ability in self.ability_spinboxes:
            bonus_spinbox = self.racial_bonus_labels[ability]
            current_value = bonus_spinbox.value()
            
            # If at max points (3), disable increasing any more
            if total_points >= 3 and current_value == 0:
                bonus_spinbox.setEnabled(False)
            else:
                bonus_spinbox.setEnabled(True)
        
        # Update final scores
        self._update_final_scores()
    
    def _update_racial_bonuses(self):
        """Legacy method - now calls background bonuses."""
        self._update_background_bonuses()
    
    def _update_point_buy(self):
        """Update point buy calculations."""
        total_points = 0
        # Extended point costs to handle low values
        point_costs = {
            8: 0,   # Standard starting point
            9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9,
            16: 12, 17: 15, 18: 17  # Handle high rolled values
        }
        
        # Special handling for dump stat (3) - it costs 0 points
        # This ensures 27 points total regardless of dump stat
        
        for ability, spinbox in self.ability_spinboxes.items():
            value = spinbox.value()
            if value == 3:  # Dump stat
                cost = 0  # Dump stat costs nothing
            else:
                cost = point_costs.get(value, 0)
            total_points += cost
        
        # Standard D&D 5e point buy: 27 points
        base_points = 27
        remaining = base_points - total_points
        
        if remaining >= 0:
            self.points_remaining_label.setText(f"Points remaining: {remaining}")
        else:
            self.points_remaining_label.setText(f"Points over budget: {abs(remaining)} (reduce some stats)")
        
        # Enable/disable next button based on valid point allocation
        if hasattr(self, 'creation_next_btn'):
            self.creation_next_btn.setEnabled(remaining >= 0)
        
        # Update final scores with current racial bonuses
        self._update_final_scores()
    
    def _update_final_scores(self):
        """Update final ability scores with point buy/rolled + background bonuses (D&D 2024)."""
        if not hasattr(self, 'racial_bonus_labels'):
            return
            
        rolled_scores = self.character_creation_data.get('rolled_scores', {})
        
        for ability in self.ability_spinboxes:
            point_buy_score = self.ability_spinboxes[ability].value()
            
            # Get rolled score if available
            rolled_score = 0
            if ability in rolled_scores:
                rolled_score = rolled_scores[ability]['total']
            
            # Get background bonus
            background_bonus = self.racial_bonus_labels[ability].value()
            
            # D&D 2024: Take higher of point buy or rolled, then add background bonus
            base_score = max(point_buy_score, rolled_score)
            final_score = base_score + background_bonus
            
            self.final_score_labels[ability].setText(str(final_score))
    
    def _creation_next_step(self):
        """Move to next character creation step."""
        if self.creation_step < 5:  # 6 steps total (0-5)
            self.creation_step += 1
            self._update_creation_step()
    
    def _creation_previous_step(self):
        """Move to previous character creation step."""
        if self.creation_step > 0:
            self.creation_step -= 1
            self._update_creation_step()
    
    def _update_creation_step(self):
        """Update the current creation step display and navigation."""
        self.creation_stack.setCurrentIndex(self.creation_step)
        self.creation_step_label.setText(f"Step {self.creation_step + 1} of 6")
        
        # Update button states
        self.creation_back_btn.setEnabled(self.creation_step > 0)
        
        # Check if current step is valid for next button
        if self.creation_step == 5:  # Final step
            self.creation_next_btn.setText("Complete")
        else:
            self.creation_next_btn.setText("Next")
    
    def _finish_character_creation(self):
        """Complete character creation and emit the character data."""
        # Calculate final ability scores with background bonuses (D&D 2024)
        final_ability_scores = {}
        rolled_scores = self.character_creation_data.get('rolled_scores', {})
        
        for ability, spinbox in self.ability_spinboxes.items():
            point_buy_score = spinbox.value()
            rolled_score = rolled_scores.get(ability, {}).get('total', 0)
            background_bonus = self.racial_bonus_labels[ability].value()
            
            # Take higher of point buy or rolled, then add background bonus
            base_score = max(point_buy_score, rolled_score)
            final_ability_scores[ability] = base_score + background_bonus
        
        # Collect selected feats
        selected_feats = []
        
        # Background origin feat (required)
        bg_feat_data = self.background_feat_combo.currentData()
        if bg_feat_data:
            selected_feats.append(bg_feat_data.get('name', ''))
        
        # Species bonus feat (only for humans)
        if self.species_feat_combo.isVisible():
            species_feat_data = self.species_feat_combo.currentData()
            if species_feat_data:
                selected_feats.append(species_feat_data.get('name', ''))
        
        # Class-specific feats (Fighter Fighting Style)
        class_data = self.character_creation_data.get('class')
        if class_data and class_data.get('name') == 'Fighter':
            if hasattr(self, 'fighting_style_combo'):
                fighting_style_data = self.fighting_style_combo.currentData()
                if fighting_style_data:
                    feat_name = fighting_style_data.get('name', '')
                    selected_feats.append(feat_name)
        
        # Collect class features
        class_features = {}
        selected_weapon_masteries = []
        
        if class_data and class_data.get('name') == 'Fighter':
            class_features['Second Wind'] = {
                'type': 'bonus_action',
                'usage': 'short_rest',
                'recharge': 2,  # 2 uses per short rest
                'description': 'Regain 1d10 + Fighter level hit points',
                'level_acquired': 1
            }
            
            # Collect selected weapon masteries
            if hasattr(self, 'weapon_mastery_checkboxes'):
                selected_weapon_masteries = [
                    checkbox.weapon_name for checkbox in self.weapon_mastery_checkboxes.values() 
                    if checkbox.isChecked()
                ]
            
            class_features['Weapon Mastery'] = {
                'type': 'passive',
                'usage': 'permanent',
                'count': 3,  # 3 weapon masteries
                'selected_weapons': selected_weapon_masteries,
                'description': f'Use mastery properties of {len(selected_weapon_masteries)} weapons: {", ".join(selected_weapon_masteries)}',
                'level_acquired': 1
            }
        
        # Compile final character data
        final_character = {
            'name': self.character_name_input.currentText(),
            'class_data': self.character_creation_data.get('class'),
            'background_data': self.character_creation_data.get('background'),
            'species_data': self.character_creation_data.get('species'),
            'ability_scores': final_ability_scores,
            'point_buy_scores': {ability: spinbox.value() for ability, spinbox in self.ability_spinboxes.items()},
            'rolled_scores': rolled_scores,
            'selected_feats': selected_feats,
            'class_features': class_features,
            'weapon_masteries': selected_weapon_masteries,  # Add weapon masteries for action panel
            'level': 1,
            'experience_points': 0,
            'equipment_choices': {}
        }

        # Record selected equipment options
        if hasattr(self, 'equipment_button_groups'):
            for choice_name, button_group in self.equipment_button_groups.items():
                checked = button_group.checkedButton()
                if checked:
                    item_name = checked.text().split(' (', 1)[0]
                    final_character['equipment_choices'][choice_name] = item_name

        # Emit the completed character
        self.character_created.emit(final_character)
        
        # Return to exploration mode
        self.exit_character_creation()
    
    def _get_class_dump_stats(self, class_name: str) -> Dict[str, str]:
        """Get dump stat for a class."""
        dump_stats = {
            'fighter': 'intelligence',
            'rogue': 'wisdom',
            # Add more classes as needed
        }
        
        # Default to intelligence for unknown classes
        dump_stat = dump_stats.get(class_name, 'intelligence')
        
        return {
            'dump_stat': dump_stat
        }
    
    def _apply_class_defaults(self):
        """Apply class-specific default ability scores."""
        if 'class' not in self.character_creation_data:
            return
        
        class_name = self.character_creation_data['class']['name'].lower()
        dump_stats = self._get_class_dump_stats(class_name)
        
        # Reset all stats to 8 first
        for ability in self.ability_spinboxes:
            self.ability_spinboxes[ability].setValue(8)
        
        # Set dump stat to 3
        self.ability_spinboxes[dump_stats['dump_stat']].setValue(3)
        
        # No longer setting a random stat to 6
        
        # Update display
        self._update_point_buy()
        
        # Update info text
        class_data = self.character_creation_data['class']
        info_text = f"{class_data['name']} defaults applied: {dump_stats['dump_stat'].title()} = 3"
        self.class_stats_info.setText(info_text)
    
    def _apply_class_defaults_auto(self):
        """Automatically apply class defaults when class is selected."""
        if 'class' not in self.character_creation_data or not hasattr(self, 'ability_spinboxes'):
            return
        
        class_name = self.character_creation_data['class']['name'].lower()
        dump_stats = self._get_class_dump_stats(class_name)
        
        # Only apply if ability scores are still at default (8)
        all_at_default = all(spinbox.value() == 8 for spinbox in self.ability_spinboxes.values())
        
        if all_at_default:
            # Set dump stat to 3
            self.ability_spinboxes[dump_stats['dump_stat']].setValue(3)
            
            # Update display
            self._update_point_buy()
    
    def _on_ability_value_changed(self, value):
        """Handle ability score changes with budget enforcement."""
        sender = self.sender()
        
        # Check if this change would exceed budget
        if self._would_exceed_budget(sender, value):
            # Find the maximum value we can afford
            max_affordable = self._get_max_affordable_value(sender)
            sender.blockSignals(True)  # Prevent recursion
            sender.setValue(max_affordable)
            sender.blockSignals(False)
        
        self._update_point_buy()
    
    def _would_exceed_budget(self, changed_spinbox, new_value) -> bool:
        """Check if changing a spinbox to new_value would exceed 27 points."""
        point_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        
        total_points = 0
        for ability, spinbox in self.ability_spinboxes.items():
            if spinbox == changed_spinbox:
                # Use the proposed new value
                value = new_value
            else:
                # Use current value
                value = spinbox.value()
            
            if value == 3:  # Dump stat
                cost = 0
            else:
                cost = point_costs.get(value, 0)
            total_points += cost
        
        return total_points > 27
    
    def _get_max_affordable_value(self, changed_spinbox) -> int:
        """Find the highest value we can set without exceeding budget."""
        for test_value in range(15, 2, -1):  # Test from 15 down to 3
            if not self._would_exceed_budget(changed_spinbox, test_value):
                return test_value
        return 3  # Minimum value
    
    def _roll_4d6_overlay(self):
        """Roll 4d6 drop lowest for each ability score and auto-apply higher values."""
        # Check if already rolled
        if self.has_rolled_4d6:
            return
        
        # Mark as used
        self.has_rolled_4d6 = True
        self.roll_4d6_btn.setEnabled(False)
        self.roll_4d6_btn.setText("4d6 Already Rolled")
        
        rolled_scores = {}
        
        for ability in self.ability_spinboxes:
            # Roll 4d6, drop lowest
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)  # Sort descending
            total = sum(rolls[:3])  # Take highest 3
            
            rolled_scores[ability] = {
                'total': total,
                'rolls': rolls
            }
            
            # Update the rolled score display - show if it beats point buy
            point_buy_value = self.ability_spinboxes[ability].value()
            if total > point_buy_value:
                roll_text = f"{total}* (4d6: {','.join(map(str, rolls))} → {','.join(map(str, rolls[:3]))})"  # * indicates it's being used
                self.rolled_score_labels[ability].setStyleSheet("color: #50c878; font-weight: bold;")  # Green for winning
            else:
                roll_text = f"{total} (4d6: {','.join(map(str, rolls))} → {','.join(map(str, rolls[:3]))})"
                self.rolled_score_labels[ability].setStyleSheet("color: #ff9500; font-weight: bold;")  # Orange for not used
            
            self.rolled_score_labels[ability].setText(roll_text)
        
        # Store rolled scores
        self.character_creation_data['rolled_scores'] = rolled_scores
        
        # Auto-update final scores to use higher values
        self._update_final_scores()
        
        # Update info text
        self.class_stats_info.setText("4d6 rolled! Point buy is your minimum - 4d6 only improves if higher (* = rolled used)")
        
        # Log the rolls - try to find log panel in parent hierarchy
        log_panel = None
        parent = self.parent()
        while parent and not log_panel:
            if hasattr(parent, 'log_panel'):
                log_panel = parent.log_panel
                break
            parent = parent.parent()
        
        if log_panel:
            for ability, data in rolled_scores.items():
                point_buy = self.ability_spinboxes[ability].value()
                used = "USED" if data['total'] > point_buy else "not used"
                log_panel.log_dice(f"{ability.title()}: 4d6 drop lowest = {data['total']} {data['rolls']} ({used})")
    
    # === ENCOUNTER GENERATION METHODS ===
    
    def _load_campaign_frame(self):
        """Load campaign frame from conan.json and initialize encounter generator."""
        try:
            campaign_path = os.path.join(os.path.dirname(__file__), 'campaign', 'conan.json')
            with open(campaign_path, 'r', encoding='utf-8') as f:
                frame_data = json.load(f)
            
            campaign_frame = CampaignFrame(frame_data)
            self.encounter_generator = EncounterGenerator(campaign_frame)
            
        except Exception as e:
            print(f"Error loading campaign frame: {e}")
            # Fallback to default frame
            default_frame_data = {
                'monster_type_weights': {'humanoid': 0.7, 'fiend': 0.2, 'aberration': 0.1},
                'difficulty_distribution': {'low': 0.5, 'moderate': 0.4, 'high': 0.1}
            }
            campaign_frame = CampaignFrame(default_frame_data)
            self.encounter_generator = EncounterGenerator(campaign_frame)
    
    def _generate_encounter(self):
        """Generate a random encounter based on active character level."""
        if not self.encounter_generator:
            self._load_campaign_frame()
        
        # Get character level - need to access through parent main window
        character_level = self._get_character_level()
        if character_level is None:
            self.update_scene_description("No active character found. Please create or load a character first.")
            return
        
        try:
            # Generate encounter
            encounter_data = self.encounter_generator.generate_encounter(character_level)
            
            # Clear existing encounters and instances
            self._clear_monster_cards()
            
            # Process pending widget deletions to prevent memory leaks
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            self.encounter_instances = {}
            self.selected_monster_id = None  # Clear selection
            
            # Create new encounter ID
            self.current_encounter_id = str(uuid4())
            
            # Get current character ID for encounter tracking
            character_id = self._get_current_character_id()
            
            # Create encounter tracking object
            self.current_encounter = Encounter.from_encounter_data(encounter_data, character_id)
            self.current_encounter.id = self.current_encounter_id  # Use the same ID
            
            # Save encounter to database
            self._save_encounter_to_db()
            
            # Create encounter instances with rolled HP and add monster cards
            for i, monster in enumerate(encounter_data['monsters']):
                try:
                    # Roll HP for this instance
                    rolled_hp = roll_monster_hp(monster['hp_formula'])
                    
                    # Create encounter instance
                    instance = EncounterInstance.from_monster_data(
                        monster_data=monster,
                        encounter_id=self.current_encounter_id,
                        rolled_hp=rolled_hp
                    )
                    
                    # Store instance
                    self.encounter_instances[instance.id] = instance
                    
                    # Create monster card widget and add to grid layout (3 cards per row)
                    monster_widget = self._create_monster_card(instance)
                    row = i // 3  # Integer division to get row
                    col = i % 3   # Modulo to get column
                    self.monsters_layout.addWidget(monster_widget, row, col)
                    
                except Exception as e:
                    print(f"Error creating monster card for {monster.get('name', 'Unknown')}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Update scene description
            difficulty_desc = encounter_data['difficulty'].capitalize()
            monster_names = [m['name'] for m in encounter_data['monsters']]
            if len(monster_names) == 1:
                desc = f"A {difficulty_desc.lower()} encounter appears: {monster_names[0]}!"
            else:
                desc = f"A {difficulty_desc.lower()} encounter appears: {', '.join(monster_names)}!"
            
            self.update_scene_description(desc)
            
            # Switch to encounter mode
            self.set_encounter_mode()
            
        except Exception as e:
            print(f"Error generating encounter: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_character_level(self) -> Optional[int]:
        """Get the level of the current active character."""
        try:
            # Access main window through parent hierarchy
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and hasattr(parent.game_engine, 'current_character'):
                    character = parent.game_engine.current_character
                    if character:
                        return character.level
                    break
                parent = parent.parent()
            
            return None
        except Exception as e:
            print(f"Error getting character level: {e}")
            return None
    
    def _get_current_character_id(self) -> str:
        """Get the ID of the current active character."""
        try:
            # Access main window through parent hierarchy
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and hasattr(parent.game_engine, 'current_character'):
                    character = parent.game_engine.current_character
                    if character:
                        return character.id
                    break
                parent = parent.parent()
            
            return "unknown-character"  # Fallback
        except Exception as e:
            print(f"Error getting character ID: {e}")
            return "unknown-character"
    
    def _create_monster_card(self, instance: EncounterInstance) -> QWidget:
        """Create a compact monster card using action card styling."""
        card = QFrame()
        card.setObjectName("monsterCard")
        card.setFixedSize(120, 140)  # Compact size to fit 4-5 cards (648px / 5 = ~130px each)
        card.setProperty("selected", False)  # Track selection state
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Monster image
        image_label = QLabel()
        image_label.setObjectName("monsterImage")
        image_label.setFixedSize(80, 60)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            QLabel#monsterImage {
                background-color: #1a1a1a;
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """)
        
        # Try to load monster image from data/images directory
        image_path = self._get_monster_image_path(instance.monster_name)
        if image_path and os.path.exists(image_path):
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale pixmap to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(80, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
        else:
            # Show placeholder text if no image found
            image_label.setText("No Image")
            image_label.setStyleSheet("""
                QLabel#monsterImage {
                    background-color: #1a1a1a;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    color: #666666;
                    font-size: 9px;
                }
            """)
        
        layout.addWidget(image_label)
        
        # Monster name (truncated if too long)
        name = instance.monster_name
        if len(name) > 12:
            name = name[:10] + "..."
        
        name_label = QLabel(name)
        name_label.setObjectName("monsterName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # CR and Type
        cr_label = QLabel(f"CR {instance.monster_cr}")
        cr_label.setObjectName("monsterCR")
        cr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cr_label)
        
        type_label = QLabel(instance.monster_type.capitalize())
        type_label.setObjectName("monsterType")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(type_label)
        
        # HP progress bar only (no text display)
        hp_bar = QProgressBar()
        hp_bar.setRange(0, 100)
        hp_bar.setValue(int(instance.hp_percentage))
        hp_bar.setTextVisible(False)
        hp_bar.setFixedHeight(8)
        
        # Color-code HP bar based on health status
        if instance.hp_percentage <= 25:
            bar_color = "#ff6b6b"  # Red for critical (matching action card cooldown)
        elif instance.hp_percentage <= 50:
            bar_color = "#ff9500"  # Orange for bloodied
        else:
            bar_color = "#4CAF50"  # Green for healthy
        
        hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444444;
                border-radius: 2px;
                background-color: #1a1a1a;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 1px;
            }}
        """)
        
        layout.addWidget(hp_bar)
        layout.addStretch()
        
        # Store instance reference in the card for updates
        card.instance_id = instance.id
        card.hp_bar = hp_bar
        card.image_label = image_label
        
        # Add click handler for selection (use default argument to capture instance.id)
        card.mousePressEvent = lambda event, iid=instance.id: self._select_monster_card(iid)
        
        return card
    
    def _get_monster_image_path(self, monster_name: str) -> Optional[str]:
        """Get the path to a monster's image file."""
        try:
            # Get the absolute path to the data/images directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            images_dir = os.path.join(project_root, "data", "images")
            
            # Try common image extensions
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                # Replace spaces and special characters with underscores for filename
                safe_name = monster_name.lower().replace(' ', '_').replace('-', '_')
                # Remove any other special characters
                import re
                safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)
                
                image_path = os.path.join(images_dir, f"{safe_name}{ext}")
                if os.path.exists(image_path):
                    return image_path
            
            return None
        except Exception as e:
            print(f"Error getting monster image path for {monster_name}: {e}")
            return None
    
    def _select_monster_card(self, instance_id: str):
        """Select a monster card for targeting."""
        # Clear previous selection
        if self.selected_monster_id:
            self._update_card_selection_display(self.selected_monster_id, False)
        
        # Set new selection
        self.selected_monster_id = instance_id
        self._update_card_selection_display(instance_id, True)
        
        # Emit selection signal
        self.monster_selected.emit(instance_id)
        
        # Log the selection
        if instance_id in self.encounter_instances:
            monster_name = self.encounter_instances[instance_id].monster_name
            self._log_monster_action(f"Targeting {monster_name}")
    
    def _update_card_selection_display(self, instance_id: str, selected: bool):
        """Update the visual display of a monster card's selection state."""
        # Find the monster card widget in the grid layout
        for i in range(self.monsters_layout.count()):
            item = self.monsters_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                
                if hasattr(widget, 'instance_id') and widget.instance_id == instance_id:
                    widget.setProperty("selected", selected)
                    # Force style refresh
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    widget.update()
                    break
    
    def get_selected_monster(self) -> Optional[EncounterInstance]:
        """Get the currently selected monster instance."""
        if self.selected_monster_id and self.selected_monster_id in self.encounter_instances:
            return self.encounter_instances[self.selected_monster_id]
        return None
    
    def _clear_monster_cards(self):
        """Clear all monster cards from the grid layout."""
        try:
            # Remove all widgets from the monsters layout
            widgets_to_delete = []
            while self.monsters_layout.count():
                child = self.monsters_layout.takeAt(0)
                if child and child.widget():
                    widgets_to_delete.append(child.widget())
            
            # Delete widgets after removing from layout
            for widget in widgets_to_delete:
                widget.deleteLater()
                
        except Exception as e:
            print(f"Error clearing monster cards: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_damage_to_monster(self, instance_id: str, damage: int):
        """Apply damage to a specific monster instance and update UI."""
        if instance_id not in self.encounter_instances:
            return
        
        instance = self.encounter_instances[instance_id]
        actual_damage = instance.take_damage(damage)
        
        # Update the monster card UI
        self._update_monster_card_display(instance_id)
        
        # Log the damage (if log panel is available)
        self._log_monster_action(f"{instance.monster_name} takes {actual_damage} damage! " +
                                f"({instance.current_hit_points}/{instance.max_hit_points} HP)")
        
        # Check if monster died
        if not instance.is_alive:
            self._log_monster_action(f"{instance.monster_name} has been defeated!")
            
            # Award XP for defeated monster
            self._award_xp_for_defeated_monster(instance)
    
    def _heal_monster(self, instance_id: str, healing: int):
        """Heal a specific monster instance and update UI."""
        if instance_id not in self.encounter_instances:
            return
        
        instance = self.encounter_instances[instance_id]
        actual_healing = instance.heal(healing)
        
        if actual_healing > 0:
            # Update the monster card UI
            self._update_monster_card_display(instance_id)
            
            # Log the healing
            self._log_monster_action(f"{instance.monster_name} heals {actual_healing} HP! " +
                                   f"({instance.current_hit_points}/{instance.max_hit_points} HP)")
    
    def _update_monster_card_display(self, instance_id: str):
        """Update the visual display of a monster card after HP changes."""
        if instance_id not in self.encounter_instances:
            return
        
        instance = self.encounter_instances[instance_id]
        
        # Find the monster card widget in the horizontal layout
        for i in range(self.monsters_layout.count()):
            item = self.monsters_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                
                if hasattr(widget, 'instance_id') and widget.instance_id == instance_id:
                    # Update HP bar value and color
                    widget.hp_bar.setValue(int(instance.hp_percentage))
                    
                    # Update HP bar color based on health status
                    if instance.hp_percentage <= 25:
                        bar_color = "#ff6b6b"  # Red for critical
                    elif instance.hp_percentage <= 50:
                        bar_color = "#ff9500"  # Orange for bloodied  
                    else:
                        bar_color = "#4CAF50"  # Green for healthy
                    
                    widget.hp_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: 1px solid #444444;
                            border-radius: 2px;
                            background-color: #1a1a1a;
                        }}
                        QProgressBar::chunk {{
                            background-color: {bar_color};
                            border-radius: 1px;
                        }}
                    """)
                    
                    # Add visual indicator for dead monsters
                    if not instance.is_alive:
                        # Use action card styling for dead state
                        widget.setStyleSheet("""
                            QFrame#monsterCard {
                                background-color: #1a1a1a;
                                border: 2px solid #444444;
                                border-radius: 8px;
                                opacity: 0.6;
                            }
                        """)
                    
                    break
    
    def _log_monster_action(self, message: str):
        """Log monster-related actions to the log panel if available."""
        try:
            # Try to find log panel in parent hierarchy
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(message)
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log message: {e}")
            print(f"Message was: {message}")
    
    def _award_xp_for_defeated_monster(self, instance: EncounterInstance):
        """Award XP to character for defeating a monster."""
        try:
            xp_value = instance.monster_xp
            
            # Update encounter tracking
            if self.current_encounter:
                self.current_encounter.add_defeated_monster(xp_value)
                self._save_encounter_to_db()
            
            # Award XP to character
            self._add_xp_to_character(xp_value)
            
            # Update character sheet XP display
            self._update_character_sheet_xp(instance.monster_name, xp_value)
            
            # Log XP gain
            self._log_xp_gain(instance.monster_name, xp_value)
            
            # Check if encounter is complete
            if self.current_encounter and self.current_encounter.is_complete:
                self._log_monster_action(f"Encounter completed! Total XP gained: {self.current_encounter.xp_awarded}")
                
        except Exception as e:
            print(f"Error awarding XP: {e}")
    
    def _add_xp_to_character(self, xp_value: int):
        """Add XP to the current character."""
        try:
            # Get game engine from parent for character update
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    
                    if character:
                        # Add XP to character
                        old_xp = character.experience_points
                        character.experience_points += xp_value
                        
                        # TODO: Check for level up
                        # level_up_xp = [300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 
                        #                100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
                        
                        # Save character to database
                        # TODO: Add character save method to game engine
                        print(f"Character XP updated: {old_xp} -> {character.experience_points} (+{xp_value})")
                        
                        return
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error adding XP to character: {e}")
    
    def _log_xp_gain(self, monster_name: str, xp_value: int):
        """Log XP gain to the combat log."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"💰 Gained {xp_value} XP for defeating {monster_name}")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log XP gain: {e}")
    
    def _update_character_sheet_xp(self, monster_name: str, xp_value: int):
        """Update the character sheet XP display."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_sheet'):
                    parent.character_sheet.add_xp_gain(f"Defeated {monster_name}", xp_value)
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not update character sheet XP: {e}")
    
    # === DATABASE PERSISTENCE METHODS ===
    
    def _save_encounter_to_db(self):
        """Save the current encounter to the database."""
        try:
            if not self.current_encounter:
                return
                
            # Get game engine from parent for database access
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    # For now, just print what we would save
                    # TODO: Add encounter persistence to game engine
                    print(f"Would save encounter {self.current_encounter.id} to database")
                    print(f"Status: {self.current_encounter.status}, XP awarded: {self.current_encounter.xp_awarded}")
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error saving encounter: {e}")
    
    def _save_encounter_instances_to_db(self):
        """Save current encounter instances to the database."""
        try:
            # Get game engine from parent for database access
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    
                    # Save each instance to the database
                    # (This would require adding methods to the game engine)
                    # For now, we'll just store in memory
                    print(f"Would save {len(self.encounter_instances)} encounter instances to DB")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error saving encounter instances: {e}")
    
    def get_encounter_instance(self, instance_id: str) -> Optional[EncounterInstance]:
        """Get an encounter instance by ID."""
        return self.encounter_instances.get(instance_id)
    
    def get_all_encounter_instances(self) -> List[EncounterInstance]:
        """Get all current encounter instances."""
        return list(self.encounter_instances.values())
    
    def get_living_monsters(self) -> List[EncounterInstance]:
        """Get all living monsters in the current encounter."""
        return [instance for instance in self.encounter_instances.values() if instance.is_alive]
    
    def is_encounter_complete(self) -> bool:
        """Check if all monsters in the encounter are defeated."""
        return len(self.get_living_monsters()) == 0