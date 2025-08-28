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
                            QSpinBox, QCheckBox, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any
import json
import os
import random


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
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_encounter = None
        self.encounter_mode = "exploration"  # exploration, encounter, combat, character_creation
        self.character_creation_data = {}  # Store character creation progress
        self.creation_step = 0  # Track current creation step
        
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
        
        # --- CHARACTER CREATION TAB ---
        self.character_creation_tab = QWidget()
        self.content_tabs.addTab(self.character_creation_tab, "Create Character")
        self.content_tabs.setTabVisible(3, False)  # Hidden initially
        
        creation_layout = QVBoxLayout(self.character_creation_tab)
        creation_layout.setContentsMargins(5, 5, 5, 5)
        
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
        
        self.creation_step_label = QLabel("Step 1 of 5")
        creation_nav_layout.addWidget(self.creation_step_label)
        
        creation_nav_layout.addStretch()
        
        self.creation_next_btn = QPushButton("Next")
        self.creation_next_btn.clicked.connect(self._creation_next_step)
        creation_nav_layout.addWidget(self.creation_next_btn)
        
        creation_layout.addWidget(self.creation_nav_frame)
        
        self._setup_character_creation_steps()
        
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
    
    # === CHARACTER CREATION METHODS ===
    
    def set_character_creation_mode(self):
        """Switch to character creation mode."""
        self.encounter_mode = "character_creation"
        self.title_label.setText("Create Character")
        self.mode_label.setText("Character Creation")
        self.mode_label.setStyleSheet("color: #50c878; border-color: #50c878;")
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
        
        # Step 2: Background & Species
        self.bg_species_step = self._create_background_species_step()
        self.creation_stack.addWidget(self.bg_species_step)
        
        # Step 3: Ability Scores
        self.abilities_step = self._create_abilities_step()
        self.creation_stack.addWidget(self.abilities_step)
        
        # Step 4: Equipment
        self.equipment_step = self._create_equipment_step()
        self.creation_stack.addWidget(self.equipment_step)
        
        # Step 5: Final Review
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
        
        # Description area
        self.bg_species_description = QTextEdit()
        self.bg_species_description.setObjectName("bgSpeciesDescription")
        self.bg_species_description.setMaximumHeight(100)
        self.bg_species_description.setReadOnly(True)
        layout.addWidget(self.bg_species_description)
        
        # Load data
        self._load_background_species_data()
        
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
        abilities_layout.addWidget(QLabel("Racial"), 0, 2) 
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
            
            # Show racial bonus
            bonus_label = QLabel("+0")
            bonus_label.setObjectName("racialBonus")
            self.racial_bonus_labels[ability_lower] = bonus_label
            abilities_layout.addWidget(bonus_label, row, 2)
            
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
        
        # Equipment will be populated based on class/background choices
        self.equipment_list = QListWidget()
        self.equipment_list.setObjectName("equipmentList")
        layout.addWidget(self.equipment_list)
        
        return widget
    
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
    
    def _on_class_selected(self, current, previous):
        """Handle class selection change."""
        if current:
            class_data = current.data(Qt.ItemDataRole.UserRole)
            self.character_creation_data['class'] = class_data
            
            description = f"**{class_data['name']}**\n\n"
            description += f"{class_data['description']}\n\n"
            description += f"Hit Die: d{class_data['hit_die']}\n"
            description += f"Primary Ability: {class_data['primary_ability']}\n"
            description += f"Saving Throws: {', '.join(class_data['saving_throw_proficiencies'])}"
            
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
    
    def _update_racial_bonuses(self):
        """Update racial bonuses display in abilities step."""
        if 'species' not in self.character_creation_data:
            return
        
        bonuses = self.character_creation_data['species'].get('ability_score_increases', {})
        
        # Update bonus and final score labels
        for ability in self.ability_spinboxes:
            bonus = bonuses.get(ability, 0)
            base_score = self.ability_spinboxes[ability].value()
            final_score = base_score + bonus
            
            # Update displays
            bonus_text = f"+{bonus}" if bonus > 0 else f"{bonus}" if bonus < 0 else "+0"
            self.racial_bonus_labels[ability].setText(bonus_text)
            self.final_score_labels[ability].setText(str(final_score))
    
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
        """Update final ability scores using higher of point buy or rolled + racial bonuses."""
        if not hasattr(self, 'racial_bonus_labels'):
            return
            
        bonuses = {}
        if 'species' in self.character_creation_data:
            bonuses = self.character_creation_data['species'].get('ability_score_increases', {})
        
        rolled_scores = self.character_creation_data.get('rolled_scores', {})
        
        for ability in self.ability_spinboxes:
            racial_bonus = bonuses.get(ability, 0)
            point_buy_score = self.ability_spinboxes[ability].value()
            
            # Get rolled score if available
            rolled_score = 0
            if ability in rolled_scores:
                rolled_score = rolled_scores[ability]['total']
            
            # Take higher of point buy or rolled, then add racial bonus
            base_score = max(point_buy_score, rolled_score)
            final_score = base_score + racial_bonus
            
            self.final_score_labels[ability].setText(str(final_score))
    
    def _creation_next_step(self):
        """Move to next character creation step."""
        if self.creation_step < 4:  # 5 steps total (0-4)
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
        self.creation_step_label.setText(f"Step {self.creation_step + 1} of 5")
        
        # Update button states
        self.creation_back_btn.setEnabled(self.creation_step > 0)
        
        # Check if current step is valid for next button
        if self.creation_step == 4:  # Final step
            self.creation_next_btn.setText("Complete")
        else:
            self.creation_next_btn.setText("Next")
    
    def _finish_character_creation(self):
        """Complete character creation and emit the character data."""
        # Calculate final ability scores using "take higher" logic
        final_ability_scores = {}
        rolled_scores = self.character_creation_data.get('rolled_scores', {})
        
        for ability, spinbox in self.ability_spinboxes.items():
            point_buy_score = spinbox.value()
            rolled_score = rolled_scores.get(ability, {}).get('total', 0)
            # Take higher of the two
            final_ability_scores[ability] = max(point_buy_score, rolled_score)
        
        # Compile final character data
        final_character = {
            'name': self.character_name_input.currentText(),
            'class_data': self.character_creation_data.get('class'),
            'background_data': self.character_creation_data.get('background'),
            'species_data': self.character_creation_data.get('species'),
            'ability_scores': final_ability_scores,
            'point_buy_scores': {ability: spinbox.value() for ability, spinbox in self.ability_spinboxes.items()},
            'rolled_scores': rolled_scores,
            'level': 1,
            'experience_points': 0
        }
        
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