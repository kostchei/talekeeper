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
from .town_encounter import TownEncounterPanel
# Monster models no longer needed - using direct SQL queries and local dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime


@dataclass
class CombatSession:
    """Simple combat session for action economy tracking."""
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    
    # Combat state
    is_active: bool = True
    current_round: int = 1
    current_turn: int = 0
    
    # Action Economy
    action_economy: Optional[Any] = None  # CombatActionEconomy imported when needed
    
    # Metadata
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    
    def start_combat_with_action_economy(self, character_id: str):
        """Initialize combat session with action economy tracking."""
        from models.action_economy import CombatActionEconomy
        
        self.character_id = character_id
        self.current_round = 1
        self.current_turn = 0
        
        # Create action economy tracker
        self.action_economy = CombatActionEconomy(
            combat_session_id=self.id,
            current_round=1,
            current_turn=0,
            turn_order=[character_id]  # Simple single-player combat
        )
        
        # Add character to action economy
        # Check if character is a Fighter level 2+ for Action Surge
        has_action_surge = False
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine.current_character:
                    character = parent.game_engine.current_character
                    if (character.get('class_id', '').lower() == 'fighter' and 
                        character.get('level', 0) >= 2):
                        has_action_surge = True
                    break
                parent = parent.parent()
        except Exception:
            pass  # Fallback to False if character data unavailable
        
        self.action_economy.add_combatant(
            combatant_id=character_id,
            name="Player",
            combatant_type="character",
            movement_speed=30,
            has_action_surge=has_action_surge
        )
        
        self.is_active = True
    
    def can_take_action(self, combatant_id: str, action_type: str) -> bool:
        """Check if a combatant can take a specific type of action."""
        if not self.action_economy:
            return True  # No restrictions if action economy not initialized
        
        from models.action_economy import ActionEconomyType
        
        # Map action type strings to ActionEconomyType
        action_type_mapping = {
            "action": ActionEconomyType.ACTION,
            "bonus_action": ActionEconomyType.BONUS_ACTION,
            "reaction": ActionEconomyType.REACTION,
            "movement": ActionEconomyType.MOVEMENT,
            "free_action": ActionEconomyType.FREE_ACTION
        }
        
        economy_type = action_type_mapping.get(action_type.lower())
        if not economy_type:
            return True  # Unknown action types are allowed
        
        state = self.action_economy.get_combatant_state(combatant_id)
        return state.can_take_action(economy_type) if state else False
    
    def use_action(self, combatant_id: str, action_type: str, action_name: str, action_data: Dict = None) -> bool:
        """Attempt to use an action and record it."""
        if not self.action_economy:
            return True
        
        from models.action_economy import ActionEconomyType
        
        # Map action type strings to ActionEconomyType
        action_type_mapping = {
            "action": ActionEconomyType.ACTION,
            "bonus_action": ActionEconomyType.BONUS_ACTION,
            "reaction": ActionEconomyType.REACTION,
            "movement": ActionEconomyType.MOVEMENT,
            "free_action": ActionEconomyType.FREE_ACTION
        }
        
        economy_type = action_type_mapping.get(action_type.lower())
        if not economy_type:
            economy_type = ActionEconomyType.FREE_ACTION
        
        # Try to use the action
        return self.action_economy.use_action(combatant_id, economy_type, action_name, action_data or {})


@dataclass
class Encounter:
    """Simple dataclass to replace the IndexedDB Encounter model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    
    # Encounter metadata
    encounter_level: int = 1
    difficulty: str = "low"
    total_xp_budget: int = 0
    
    # Status tracking - REQUIRED for _save_encounter_to_db
    status: str = "active"  # active, completed, abandoned
    is_combat: bool = False
    rounds_elapsed: int = 0
    
    # Initiative tracking
    initiative_rolled: bool = False
    current_turn: int = 0
    player_initiative: Optional[int] = None
    
    # XP and rewards
    xp_awarded: int = 0
    xp_pending: int = 0
    monsters_defeated: int = 0
    monsters_total: int = 0
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if encounter is completed."""
        return self.status == "completed" or self.monsters_defeated >= self.monsters_total
    
    def complete_encounter(self):
        """Mark encounter as completed."""
        self.status = "completed"
        self.updated_at = datetime.now().isoformat()
    
    def add_defeated_monster(self, xp_value: int):
        """Add a defeated monster to the encounter."""
        self.monsters_defeated += 1
        self.xp_awarded += xp_value
        self.xp_pending -= xp_value
        
        # Check if encounter is complete
        if self.monsters_defeated >= self.monsters_total:
            self.complete_encounter()
    
    @classmethod
    def from_encounter_data(cls, encounter_data: Dict[str, Any], character_id: str):
        """Create an Encounter from encounter data."""
        total_xp = sum(m.get('xp', 0) for m in encounter_data.get('monsters', []))
        monster_count = len(encounter_data.get('monsters', []))
        
        return cls(
            character_id=character_id,
            encounter_level=encounter_data.get('level', 1),
            difficulty=encounter_data.get('difficulty', 'low'),
            total_xp_budget=encounter_data.get('total_xp', total_xp),
            status="active",
            is_combat=False,
            xp_awarded=0,
            xp_pending=total_xp,
            monsters_defeated=0,
            monsters_total=monster_count
        )
    
    def roll_initiative(self, player_dex_mod: int, monster_instances: list, monster_data: dict) -> int:
        """Roll initiative for player and all monsters with advantage/disadvantage support."""
        import random
        from services.advantage_system import advantage_system, RollType
        
        # Create context for player initiative roll
        initiative_context = {
            'dexterity_modifier': player_dex_mod,
            # TODO: Add character features that affect initiative (e.g., Feral Instinct for Barbarians)
            # 'feral_instinct': False  # Barbarian level 7 feature gives advantage on initiative
        }
        
        # Get advantage/disadvantage sources for initiative
        advantage_sources = advantage_system.get_common_advantage_sources(RollType.INITIATIVE, initiative_context)
        disadvantage_sources = advantage_system.get_common_disadvantage_sources(RollType.INITIATIVE, initiative_context)
        
        # Calculate advantage state and roll
        advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)
        self.player_initiative, roll_breakdown = advantage_system.roll_d20_with_advantage(advantage_state, player_dex_mod)
        
        # Store the roll breakdown for logging
        self._player_initiative_breakdown = roll_breakdown
        
        # Roll initiative for each monster
        self.monster_initiative_rolls = {}  # Store rolls for logging
        for instance in monster_instances:
            if instance.is_alive:
                # Get monster DEX modifier from monster data
                monster_name = instance.monster_name
                dex_modifier = 0  # Default
                
                if monster_name in monster_data:
                    dex_score = monster_data[monster_name].get('dexterity', 10)
                    dex_modifier = (dex_score - 10) // 2
                
                # Roll initiative for this monster
                monster_roll = random.randint(1, 20)
                instance.initiative = monster_roll + dex_modifier
                
                # Store the roll breakdown for logging
                self.monster_initiative_rolls[instance.id] = {
                    'name': monster_name,
                    'd20_roll': monster_roll,
                    'dex_modifier': dex_modifier,
                    'total': instance.initiative
                }
        
        # Mark initiative as rolled
        self.initiative_rolled = True
        
        return self.player_initiative
    
    def get_initiative_order(self, monster_instances: list) -> list:
        """Get initiative order for all participants."""
        initiative_order = []
        
        # Add player to order
        if self.player_initiative is not None:
            initiative_order.append({
                'name': 'Player',
                'initiative': self.player_initiative,
                'type': 'player'
            })
        
        # Add living monsters to order
        for instance in monster_instances:
            if instance.is_alive and instance.initiative is not None:
                initiative_order.append({
                    'name': instance.monster_name,
                    'initiative': instance.initiative,
                    'type': 'monster',
                    'instance': instance
                })
        
        # Sort by initiative (highest first)
        initiative_order.sort(key=lambda x: x['initiative'], reverse=True)
        
        return initiative_order
    
    def start_combat(self):
        """Start combat mode for this encounter."""
        self.is_combat = True
        self.current_turn = 0


@dataclass
class EncounterInstance:
    """Simple dataclass to replace the IndexedDB model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    encounter_id: str = ""
    
    # Monster reference and current state
    monster_name: str = ""
    monster_cr: str = ""
    monster_type: str = ""
    monster_xp: int = 0
    
    # HP tracking
    max_hit_points: int = 0
    current_hit_points: int = 0
    temporary_hit_points: int = 0
    
    # Combat state
    is_alive: bool = True
    conditions: List[str] = field(default_factory=list)
    initiative: Optional[int] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    @property
    def hp_percentage(self) -> float:
        """Calculate HP percentage for health bar displays."""
        if self.max_hit_points <= 0:
            return 0
        return (self.current_hit_points / self.max_hit_points) * 100
    
    @classmethod
    def from_monster_data(cls, monster_data: Dict[str, Any], encounter_id: str, rolled_hp: Optional[int] = None):
        """Create encounter instance from monster generator data."""
        # Calculate HP from SRD data or use provided rolled HP
        if rolled_hp is not None:
            max_hp = rolled_hp
        else:
            # Use average HP from SRD data
            max_hp = monster_data.get('average_hp', 8)  # Default fallback
        
        return cls(
            encounter_id=encounter_id,
            monster_name=monster_data['name'],
            monster_cr=monster_data['cr_str'],
            monster_type=monster_data['type'],
            monster_xp=monster_data['xp'],
            max_hit_points=max_hp,
            current_hit_points=max_hp,
            temporary_hit_points=0,
            is_alive=True,
            conditions=[],
            initiative=None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'monster_name': self.monster_name,
            'monster_type': self.monster_type,
            'monster_cr': self.monster_cr,
            'current_hit_points': self.current_hit_points,
            'max_hit_points': self.max_hit_points,
            'hp_percentage': self.hp_percentage,
            'is_alive': self.is_alive
        }
    
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage dealt."""
        # Damage applies to temp HP first
        if self.temporary_hit_points > 0:
            if damage <= self.temporary_hit_points:
                self.temporary_hit_points -= damage
                return damage
            else:
                damage -= self.temporary_hit_points
                self.temporary_hit_points = 0
        
        # Then regular HP
        actual_damage = min(damage, self.current_hit_points)
        self.current_hit_points -= actual_damage
        
        # Check if defeated
        if self.current_hit_points <= 0:
            self.current_hit_points = 0
            self.is_alive = False
        
        self.updated_at = datetime.now().isoformat()
        return actual_damage
    
    def heal(self, healing: int) -> int:
        """Apply healing and return actual healing done."""
        if not self.is_alive:
            return 0  # Can't heal dead monsters
            
        actual_healing = min(healing, self.max_hit_points - self.current_hit_points)
        self.current_hit_points += actual_healing
        self.updated_at = datetime.now().isoformat()
        return actual_healing


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
        
        # Encounters list widget (was missing)
        # Encounter details area (for XP budget info) - AT THE TOP
        self.encounter_details_text = QTextEdit()
        self.encounter_details_text.setObjectName("encounterDetailsText")
        self.encounter_details_text.setReadOnly(True)
        self.encounter_details_text.setMaximumHeight(80)
        self.encounter_details_text.setPlainText("Click 'Generate Random Encounter' to see encounter details...")
        self.encounter_details_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        encounters_layout.addWidget(self.encounter_details_text)
        
        # Encounters list widget  
        self.encounters_list = QListWidget()
        self.encounters_list.setObjectName("encountersList")
        self.encounters_list.setMaximumHeight(150)  # Keep it compact
        encounters_layout.addWidget(self.encounters_list)
        
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
        
        # Long Rest button - NEW
        self.long_rest_btn = QPushButton("Long Rest")
        self.long_rest_btn.clicked.connect(self._perform_long_rest)
        self.long_rest_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a4a2a;
                border: 2px solid #4a6a4a;
                border-radius: 4px;
                color: #88ff88;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #3a5a3a;
                border-color: #5a7a5a;
            }
            QPushButton:pressed {
                background-color: #1a3a1a;
            }
        """)
        env_actions_layout.addWidget(self.long_rest_btn)
        
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
        
        # --- TOWN ENCOUNTER TAB ---
        self.town_tab = None  # Will be created when needed
        self.town_tab_index = -1  # Track town tab index
        
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
        
        QTextEdit#sceneText, QTextEdit#environmentText {{
            background-color: {palette['surface']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 8px;
            font-size: 13px;
            line-height: 1.4;
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
        
        # Initialize combat session for action economy
        self._init_combat_session()
        
        self._update_action_buttons()
    
    def _init_combat_session(self):
        """Initialize combat session and notify action panel."""
        try:
            # Get character ID
            character_id = self._get_current_character_id()
            if not character_id:
                print("No character ID found for combat session")
                return
            
            # Create combat session
            combat_session = CombatSession()
            combat_session.start_combat_with_action_economy(character_id)
            
            # Notify action panel about combat session
            parent = self.parent()
            while parent:
                if hasattr(parent, 'action_panel'):
                    parent.action_panel.set_combat_session(combat_session, character_id)
                    print(f"Combat session initialized for character {character_id}")
                    break
                parent = parent.parent()
            else:
                print("Could not find action panel to set combat session")
                
        except Exception as e:
            print(f"Error initializing combat session: {e}")
    
    def _end_combat_session(self):
        """End combat session and notify action panel."""
        try:
            # Notify action panel to end combat session
            parent = self.parent()
            while parent:
                if hasattr(parent, 'action_panel'):
                    parent.action_panel.end_combat_session()
                    print("Combat session ended")
                    break
                parent = parent.parent()
            else:
                print("Could not find action panel to end combat session")
                
        except Exception as e:
            print(f"Error ending combat session: {e}")
    
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
        print(f"[SCENE] Setting: {description[:50]}...")
        self.scene_text.setPlainText(description)
        
        # Use very visible styling
        self.scene_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.5;
            }
        """)
        
        # Ensure visibility
        self.scene_text.raise_()
        self.scene_text.show()
    
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
        
        # Clear encounters list
        if hasattr(self, 'encounters_list'):
            self.encounters_list.clear()
        
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
    
    def show_town_encounter(self):
        """Show the town encounter tab if level up is available"""
        # Check if character can level up
        if not self._can_character_level_up():
            return
        
        # Create town tab if it doesn't exist
        if self.town_tab is None:
            character_data = self._get_current_character_data()
            if character_data:
                # Character data is already a dictionary
                char_dict = character_data
                self.town_tab = TownEncounterPanel(char_dict, self)
                self.town_tab_index = self.content_tabs.addTab(self.town_tab, "🏘️ Town")
        
        # Show and switch to town tab
        if self.town_tab_index >= 0:
            self.content_tabs.setTabVisible(self.town_tab_index, True)
            self.content_tabs.setCurrentIndex(self.town_tab_index)
    
    def hide_town_encounter(self):
        """Hide the town encounter tab"""
        if self.town_tab_index >= 0:
            self.content_tabs.setTabVisible(self.town_tab_index, False)
    
    def remove_town_encounter(self):
        """Remove the town encounter tab completely"""
        if self.town_tab_index >= 0:
            self.content_tabs.removeTab(self.town_tab_index)
            self.town_tab = None
            self.town_tab_index = -1
    
    def _can_character_level_up(self) -> bool:
        """Check if current character can level up"""
        character_data = self._get_current_character_data()
        if not character_data:
            return False
        
        # Character data is always a dictionary now
        current_level = character_data.get('level', 1)
        current_xp = character_data.get('experience_points', 0)
        
        # XP thresholds for each level
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
            100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        if current_level >= 20:
            return False  # Max level reached
        
        next_level_xp = xp_thresholds[current_level] if current_level < len(xp_thresholds) else xp_thresholds[-1]
        return current_xp >= next_level_xp
    
    def _get_current_character_data(self) -> Optional[Dict[str, Any]]:
        """Get current character data from game engine"""
        try:
            # Get game engine from parent
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine:
                    game_engine = parent.game_engine
                    if hasattr(game_engine, 'current_character') and game_engine.current_character:
                        return game_engine.current_character
                    break
                parent = parent.parent()
            return None
        except Exception as e:
            print(f"Error getting current character data: {e}")
            return None
    
    def refresh_character_data(self):
        """Refresh character data and check if town tab should be shown/hidden"""
        can_level = self._can_character_level_up()
        
        if can_level and self.town_tab is None:
            # Character can now level up - show town tab
            self.show_town_encounter()
        elif not can_level and self.town_tab is not None:
            # Character can no longer level up - remove town tab
            self.remove_town_encounter()
    
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
        
        # Species skill selection area (initially hidden)
        self.species_skill_frame = QFrame()
        species_skill_layout = QVBoxLayout(self.species_skill_frame)
        
        self.species_skill_label = QLabel("Species Skill Choice")
        self.species_skill_label.setObjectName("sectionLabel")
        species_skill_layout.addWidget(self.species_skill_label)
        
        # Container for species skill selection widgets
        self.species_skill_container = QWidget()
        self.species_skill_layout = QVBoxLayout(self.species_skill_container)
        species_skill_layout.addWidget(self.species_skill_container)
        
        # Initially hide the species skill selection
        self.species_skill_frame.hide()
        layout.addWidget(self.species_skill_frame)
        
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
        
        # Get class name/ID
        selected_class_name = selected_class_data.get('name', '') if isinstance(selected_class_data, dict) else str(selected_class_data)
        
        # Load equipment choices from database via game engine
        equipment_choices = []
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    db_choices = parent.game_engine.get_class_equipment_choices_sync(selected_class_name)
                    # Format for display
                    for choice in db_choices:
                        formatted_choice = {
                            "name": choice['name'],
                            "group": choice['group'],
                            "options": []
                        }
                        for option in choice['options']:
                            # Handle both string and dictionary option formats
                            if isinstance(option, str):
                                # Option is already a formatted string
                                display = option
                            elif isinstance(option, dict):
                                # Build display string from option data
                                if 'damage' in option:
                                    display = f"{option['name']} ({option['damage']})"
                                elif 'ac' in option:
                                    display = f"{option['name']} (AC {option['ac']})"
                                elif 'contents' in option:
                                    display = f"{option['name']}"
                                else:
                                    display = option.get('name', str(option))
                            else:
                                # Fallback for unexpected formats
                                display = str(option)
                            formatted_choice['options'].append(display)
                        equipment_choices.append(formatted_choice)
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error loading equipment choices: {e}")
        
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
            # Store the group identifier for saving later
            button_group.choice_group = choice.get("group", choice["name"])
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
        
        # Add skill selection for all classes
        self._setup_class_skill_selection(selected_class_name.lower())
        
        # Handle class-specific features
        if selected_class_name == "Fighter":
            self._setup_fighter_features()
        else:
            # For non-Fighter classes, show placeholder text
            info_label = QLabel(f"{selected_class_name} other class features will be implemented soon.")
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
        
        # Load Fighting Style feats from database
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            # Get all Fighting Style feats by category
            cursor.execute("SELECT * FROM feats WHERE category = 'fighting_style' ORDER BY name")
            feats_rows = cursor.fetchall()
            
            # Add Fighting Style feats to combo box
            for feat_row in feats_rows:
                feat_data = {
                    'name': feat_row[1],
                    'description': feat_row[2],
                    'prerequisites': json.loads(feat_row[3]),
                    'ability_score_increases': json.loads(feat_row[4]),
                    'benefits': json.loads(feat_row[5]),
                    'category': feat_row[7] if len(feat_row) > 7 else 'fighting_style',
                    'entries': [feat_row[2]] if feat_row[2] else []
                }
                feat_name = feat_data.get('name', 'Unknown Feat')
                self.fighting_style_combo.addItem(feat_name, feat_data)
            
            conn.close()
                
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
    
    def _setup_class_skill_selection(self, class_id: str):
        """Setup skill selection interface for the selected class."""
        # Query database for class skill choices
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Get skill choices for this class
            cursor.execute("""
                SELECT skill_count, available_skills 
                FROM class_skill_choices 
                WHERE class_id = ?
            """, (class_id,))
            
            skill_choice_data = cursor.fetchone()
            conn.close()
            
            if not skill_choice_data:
                # No skill choices defined for this class
                return
            
            skill_count, available_skills_json = skill_choice_data
            available_skills = json.loads(available_skills_json)
            
        except Exception as e:
            print(f"Error loading class skill choices: {e}")
            return
        
        # Create skill selection group
        skill_group = QGroupBox(f"Class Skills - Choose {skill_count}")
        skill_layout = QVBoxLayout(skill_group)
        
        skill_description = QLabel(f"Choose {skill_count} skill{'s' if skill_count != 1 else ''} from your class list:")
        skill_description.setWordWrap(True)
        skill_description.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        skill_layout.addWidget(skill_description)
        
        # Create checkboxes for available skills
        self.class_skill_checkboxes = {}
        skill_grid_layout = QGridLayout()
        
        for i, skill in enumerate(available_skills):
            checkbox = QCheckBox(skill)
            checkbox.setObjectName("skillCheckbox")
            
            # Connect to limit selection
            checkbox.stateChanged.connect(lambda state, s=skill: self._on_class_skill_toggled(s, state, skill_count))
            
            self.class_skill_checkboxes[skill] = checkbox
            
            # Arrange in 2 columns
            row = i // 2
            col = i % 2
            skill_grid_layout.addWidget(checkbox, row, col)
        
        skill_layout.addLayout(skill_grid_layout)
        
        # Add selected skills count display
        self.selected_skills_count_label = QLabel(f"Selected: 0 / {skill_count}")
        self.selected_skills_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        skill_layout.addWidget(self.selected_skills_count_label)
        
        self.class_features_layout.addWidget(skill_group)
    
    def _on_class_skill_toggled(self, skill_name: str, state: int, max_skills: int):
        """Handle class skill checkbox toggle with selection limit."""
        # Count currently selected skills
        selected_count = sum(1 for cb in self.class_skill_checkboxes.values() if cb.isChecked())
        
        # If trying to select more than allowed, prevent it
        if state == 2 and selected_count > max_skills:  # 2 = Qt.CheckState.Checked
            # Uncheck this box
            self.class_skill_checkboxes[skill_name].setChecked(False)
            return
        
        # Update count display
        actual_selected = sum(1 for cb in self.class_skill_checkboxes.values() if cb.isChecked())
        self.selected_skills_count_label.setText(f"Selected: {actual_selected} / {max_skills}")
        
        # Update selection color
        if actual_selected == max_skills:
            self.selected_skills_count_label.setStyleSheet("font-weight: bold; color: #50c878;")  # Green when complete
        elif actual_selected > max_skills:
            self.selected_skills_count_label.setStyleSheet("font-weight: bold; color: #ff6b6b;")  # Red when over
        else:
            self.selected_skills_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")  # Blue when incomplete
        
        # Store selected skills in character creation data
        selected_skills = [skill for skill, cb in self.class_skill_checkboxes.items() if cb.isChecked()]
        self.character_creation_data['selected_class_skills'] = selected_skills
    
    def _setup_species_skill_selection(self, species_id: str):
        """Setup skill selection interface for the selected species."""
        # Clear existing species skill widgets
        for i in reversed(range(self.species_skill_layout.count())):
            child = self.species_skill_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Query database for species skill choices
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Get skill choices for this species
            cursor.execute("""
                SELECT proficiency_type, proficiency_name, choice_count, available_options 
                FROM species_proficiencies 
                WHERE species_id = ? AND proficiency_type = 'skill'
            """, (species_id,))
            
            species_proficiencies = cursor.fetchall()
            conn.close()
            
            # Check if there are any skill choices to make
            skill_choices = [row for row in species_proficiencies if row[2] > 0]  # choice_count > 0
            
            if not skill_choices:
                # Hide species skill selection frame
                self.species_skill_frame.hide()
                return
            
            # Show species skill selection frame
            self.species_skill_frame.show()
            
            for choice_data in skill_choices:
                proficiency_type, proficiency_name, choice_count, available_options_json = choice_data
                
                if available_options_json:
                    available_options = json.loads(available_options_json)
                else:
                    continue
                
                # Handle special case for "any" skill choice
                if available_options == ["any"]:
                    # Get all skills from a standard skill list
                    all_skills = [
                        "Acrobatics", "Animal Handling", "Arcana", "Athletics", 
                        "Deception", "History", "Insight", "Intimidation", 
                        "Investigation", "Medicine", "Nature", "Perception", 
                        "Performance", "Persuasion", "Religion", "Sleight of Hand", 
                        "Stealth", "Survival"
                    ]
                    available_options = all_skills
                
                # Create skill selection widget
                skill_choice_widget = QWidget()
                skill_choice_layout = QVBoxLayout(skill_choice_widget)
                
                choice_label = QLabel(f"Choose {choice_count} skill{'s' if choice_count != 1 else ''}:")
                choice_label.setStyleSheet("color: #666; font-style: italic;")
                skill_choice_layout.addWidget(choice_label)
                
                # Create skill selection method based on count
                if choice_count == 1:
                    # Use combo box for single selection
                    skill_combo = QComboBox()
                    skill_combo.addItem("Select a skill...", None)
                    
                    for skill in available_options:
                        skill_combo.addItem(skill, skill)
                    
                    skill_combo.currentIndexChanged.connect(
                        lambda idx, combo=skill_combo: self._on_species_skill_selected(combo)
                    )
                    
                    skill_choice_layout.addWidget(skill_combo)
                    
                    # Store reference for later use
                    if not hasattr(self, 'species_skill_widgets'):
                        self.species_skill_widgets = []
                    self.species_skill_widgets.append(skill_combo)
                    
                else:
                    # Use checkboxes for multiple selection
                    self.species_skill_checkboxes = {}
                    skill_grid = QGridLayout()
                    
                    for i, skill in enumerate(available_options):
                        checkbox = QCheckBox(skill)
                        checkbox.stateChanged.connect(
                            lambda state, s=skill: self._on_species_skill_toggled(s, state, choice_count)
                        )
                        self.species_skill_checkboxes[skill] = checkbox
                        
                        row = i // 2
                        col = i % 2
                        skill_grid.addWidget(checkbox, row, col)
                    
                    skill_choice_layout.addLayout(skill_grid)
                    
                    # Add selection count label
                    self.species_skills_count_label = QLabel(f"Selected: 0 / {choice_count}")
                    self.species_skills_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
                    skill_choice_layout.addWidget(self.species_skills_count_label)
                
                self.species_skill_layout.addWidget(skill_choice_widget)
                
        except Exception as e:
            print(f"Error loading species skill choices: {e}")
            # Hide the frame on error
            self.species_skill_frame.hide()
    
    def _on_species_skill_selected(self, combo_widget):
        """Handle single species skill selection from combo box."""
        selected_skill = combo_widget.currentData()
        if selected_skill:
            # Store in character creation data
            if 'selected_species_skills' not in self.character_creation_data:
                self.character_creation_data['selected_species_skills'] = []
            self.character_creation_data['selected_species_skills'] = [selected_skill]
    
    def _on_species_skill_toggled(self, skill_name: str, state: int, max_skills: int):
        """Handle species skill checkbox toggle with selection limit."""
        # Count currently selected skills
        selected_count = sum(1 for cb in self.species_skill_checkboxes.values() if cb.isChecked())
        
        # If trying to select more than allowed, prevent it
        if state == 2 and selected_count > max_skills:  # 2 = Qt.CheckState.Checked
            self.species_skill_checkboxes[skill_name].setChecked(False)
            return
        
        # Update count display
        actual_selected = sum(1 for cb in self.species_skill_checkboxes.values() if cb.isChecked())
        self.species_skills_count_label.setText(f"Selected: {actual_selected} / {max_skills}")
        
        # Update selection color
        if actual_selected == max_skills:
            self.species_skills_count_label.setStyleSheet("font-weight: bold; color: #50c878;")
        elif actual_selected > max_skills:
            self.species_skills_count_label.setStyleSheet("font-weight: bold; color: #ff6b6b;")
        else:
            self.species_skills_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        
        # Store selected skills in character creation data
        selected_skills = [skill for skill, cb in self.species_skill_checkboxes.items() if cb.isChecked()]
        self.character_creation_data['selected_species_skills'] = selected_skills
        
    
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
        """Load class data from database."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get classes in display order
            cursor.execute("SELECT * FROM classes ORDER BY display_order, name")
            classes_data = cursor.fetchall()
            
            for class_row in classes_data:
                class_id = class_row['id']
                
                # Get saving throw proficiencies
                cursor.execute("SELECT ability FROM class_saving_throws WHERE class_id = ?", (class_id,))
                saving_throws = [row[0] for row in cursor.fetchall()]
                
                # Get armor proficiencies
                cursor.execute("SELECT armor_type FROM class_armor_proficiencies WHERE class_id = ?", (class_id,))
                armor_profs = [row[0] for row in cursor.fetchall()]
                
                # Get weapon proficiencies
                cursor.execute("SELECT weapon_type FROM class_weapon_proficiencies WHERE class_id = ?", (class_id,))
                weapon_profs = [row[0] for row in cursor.fetchall()]
                
                # Get skill proficiencies
                cursor.execute("SELECT skill FROM class_skill_proficiencies WHERE class_id = ?", (class_id,))
                skill_profs = [row[0] for row in cursor.fetchall()]
                
                class_data = {
                    'id': class_row['id'],
                    'name': class_row['name'],
                    'description': class_row['description'],
                    'hit_die': class_row['hit_die'],
                    'primary_ability': class_row['primary_ability'],
                    'skill_choices': class_row['skill_choices'],
                    'saving_throw_proficiencies': saving_throws,
                    'armor_proficiencies': armor_profs,
                    'weapon_proficiencies': weapon_profs,
                    'skill_proficiencies': skill_profs
                }
                
                item = QListWidgetItem(class_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, class_data)
                self.class_list.addItem(item)
            
            conn.close()
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
            
            # Load backgrounds from database
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backgrounds ORDER BY name")
            backgrounds_data = cursor.fetchall()
            conn.close()
            
            for bg_row in backgrounds_data:
                bg_data = {
                    'name': bg_row['name'],
                    'description': bg_row['description'],
                    'feat': bg_row['feat']
                }
                item = QListWidgetItem(bg_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, bg_data)
                self.background_list.addItem(item)
            
            # Load species/races from database
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM races ORDER BY display_order, name")
            races_rows = cursor.fetchall()
            
            for race_row in races_rows:
                race_data = {
                    'id': race_row[0],
                    'name': race_row[1], 
                    'description': race_row[2],
                    'size': race_row[3],
                    'speed': race_row[4],
                    'ability_score_increases': json.loads(race_row[5]),
                    'traits': json.loads(race_row[6]),
                    'languages': json.loads(race_row[7]),
                    'subraces': json.loads(race_row[8])
                }
                item = QListWidgetItem(race_data['name'])
                item.setData(Qt.ItemDataRole.UserRole, race_data)
                self.species_list.addItem(item)
            
            conn.close()
                
        except Exception as e:
            print(f"Error loading background/species data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_feats_data(self):
        """Load available feats from database."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feats ORDER BY name")
            feats_rows = cursor.fetchall()
            
            # Create feats_data structure to match existing code
            feats_data = {"feat": []}
            for feat_row in feats_rows:
                feat_data = {
                    'name': feat_row[1],
                    'description': feat_row[2],
                    'prerequisites': json.loads(feat_row[3]),
                    'ability_score_increases': json.loads(feat_row[4]),
                    'benefits': json.loads(feat_row[5]),
                    'category': feat_row[7] if len(feat_row) > 7 else 'general'
                }
                feats_data["feat"].append(feat_data)
            
            conn.close()
            
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
                
                # Include only Origin feats (category = 'O') - no fallbacks
                if feat_category == 'O':
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
        
        # Add feat description from database
        feat_description = feat_data.get('description', '')
        if feat_description:
            description += f"<p>{feat_description}</p>"
        
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
            self._auto_select_background_feat(bg_data)
    
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
            
            # Setup species skill selection
            self._setup_species_skill_selection(species_data.get('id', species_name))
    
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
    
    def _auto_select_background_feat(self, bg_data):
        """Auto-select the default feat for the chosen background."""
        # Map backgrounds to their default feats from 2024 SRD
        default_feats = {
            "Acolyte": "Magic Initiate; Cleric",
            "Criminal": "Alert", 
            "Sage": "Magic Initiate; Wizard",
            "Soldier": "Savage Attacker",
            "Farmer": "Tough"
        }
        
        bg_name = bg_data.get('name', '')
        default_feat = default_feats.get(bg_name)
        
        if default_feat:
            # Find and select the default feat in the combo box
            for i in range(self.background_feat_combo.count()):
                if self.background_feat_combo.itemText(i) == default_feat:
                    self.background_feat_combo.setCurrentIndex(i)
                    break
    
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
        
        # Species bonus feat (only for humans) - use currentText() as fallback
        # Check if human based on species data, not visibility (combo might be on different wizard step)
        species_data = self.character_creation_data.get('species', {})
        is_human = 'human' in species_data.get('name', '').lower()
        if is_human and self.species_feat_combo.currentIndex() > 0:
            species_feat_data = self.species_feat_combo.currentData()
            if species_feat_data:
                selected_feats.append(species_feat_data.get('name', ''))
            else:
                # Fallback to currentText if currentData fails
                species_feat_text = self.species_feat_combo.currentText()
                if species_feat_text and not species_feat_text.startswith("Select"):
                    selected_feats.append(species_feat_text)
        
        # Class-specific feats (Fighter Fighting Style)
        class_data = self.character_creation_data.get('class')
        if class_data and class_data.get('name') == 'Fighter':
            if hasattr(self, 'fighting_style_combo'):
                fighting_style_data = self.fighting_style_combo.currentData()
                if fighting_style_data:
                    selected_feats.append(fighting_style_data.get('name', ''))
        
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
            
            # Add Action Surge for level 2+ Fighters
            level = self.character_creation_data.get('level', 1)
            if level >= 2:
                class_features['Action Surge'] = {
                    'type': 'free_action',
                    'usage': 'short_rest', 
                    'recharge': 1,  # 1 use per short rest
                    'description': 'Take an additional action on your turn',
                    'level_acquired': 2
                }
        
        elif class_data and class_data.get('name') == 'Barbarian':
            # Rage - Barbarian's signature ability
            class_features['Rage'] = {
                'type': 'bonus_action',
                'usage': 'long_rest',
                'recharge': 2,  # 2 rages per long rest at level 1
                'description': '+2 damage on Str-based melee attacks, resistance to bludgeoning/piercing/slashing damage, advantage on Str checks/saves. Lasts for entire combat.',
                'level_acquired': 1,
                'mechanics': {
                    'damage_bonus': 2,
                    'damage_resistance': ['bludgeoning', 'piercing', 'slashing'],
                    'advantage_on': ['strength_checks', 'strength_saves'],
                    'duration': 'combat'
                }
            }
            
            # Unarmored Defense - Passive AC calculation
            class_features['Unarmored Defense'] = {
                'type': 'passive',
                'usage': 'permanent',
                'description': 'While not wearing armor, your AC equals 10 + Dex modifier + Con modifier',
                'level_acquired': 1,
                'mechanics': {
                    'ac_calculation': '10 + dex_mod + con_mod',
                    'requires_no_armor': True
                }
            }
            
            # Add level 2+ Barbarian features
            level = self.character_creation_data.get('level', 1)
            if level >= 2:
                class_features['Reckless Attack'] = {
                    'type': 'free_action',
                    'usage': 'unlimited',
                    'description': 'When making first attack on turn with Str, gain advantage but attacks against you have advantage until next turn',
                    'level_acquired': 2,
                    'mechanics': {
                        'grants_advantage': True,
                        'grants_enemies_advantage': True,
                        'requires_strength_attack': True
                    }
                }
                
                class_features['Danger Sense'] = {
                    'type': 'passive',
                    'usage': 'permanent',
                    'description': 'Advantage on Dex saving throws against effects you can see (traps, spells, etc.) while not blinded, deafened, or incapacitated',
                    'level_acquired': 2,
                    'mechanics': {
                        'advantage_on': ['dexterity_saves'],
                        'requires_sight': True,
                        'excludes_conditions': ['blinded', 'deafened', 'incapacitated']
                    }
                }
            
        
        # Calculate saving throw proficiencies
        saving_throw_profs = {
            'str_save_proficient': 0,
            'dex_save_proficient': 0,
            'con_save_proficient': 0,
            'int_save_proficient': 0,
            'wis_save_proficient': 0,
            'cha_save_proficient': 0
        }
        
        # Add class saving throw proficiencies
        class_data = self.character_creation_data.get('class')
        if class_data and 'saving_throw_proficiencies' in class_data:
            for ability in class_data['saving_throw_proficiencies']:
                if ability == 'strength':
                    saving_throw_profs['str_save_proficient'] = 1
                elif ability == 'dexterity':
                    saving_throw_profs['dex_save_proficient'] = 1
                elif ability == 'constitution':
                    saving_throw_profs['con_save_proficient'] = 1
                elif ability == 'intelligence':
                    saving_throw_profs['int_save_proficient'] = 1
                elif ability == 'wisdom':
                    saving_throw_profs['wis_save_proficient'] = 1
                elif ability == 'charisma':
                    saving_throw_profs['cha_save_proficient'] = 1
        
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
            'equipment_choices': {},
            'saving_throw_proficiencies': saving_throw_profs,
            'selected_class_skills': self.character_creation_data.get('selected_class_skills', []),
            'selected_species_skills': self.character_creation_data.get('selected_species_skills', [])
        }

        # Record selected equipment options - break down combination strings
        if hasattr(self, 'equipment_button_groups'):
            for choice_key, button_group in self.equipment_button_groups.items():
                checked = button_group.checkedButton()
                if checked:
                    # Extract just the item name (before parentheses)
                    selected_text = checked.text().split(' (', 1)[0]
                    
                    # Break down combination strings (e.g., "Longsword + Shield")
                    individual_items = [item.strip() for item in selected_text.split(' + ')]
                    
                    # Use the group name from our stored data
                    group_name = button_group.choice_group if hasattr(button_group, 'choice_group') else choice_key
                    
                    # If single item, store directly; if multiple items, store as list
                    if len(individual_items) == 1:
                        final_character['equipment_choices'][group_name] = individual_items[0]
                    else:
                        # For multiple items, store each with a suffix
                        for i, item in enumerate(individual_items):
                            final_character['equipment_choices'][f"{group_name}_item_{i+1}"] = item

        # Emit the completed character
        self.character_created.emit(final_character)
        
        # Return to exploration mode
        self.exit_character_creation()
    
    def _get_class_dump_stats(self, class_name: str) -> Dict[str, str]:
        """Get dump stat for a class."""
        dump_stats = {
            'fighter': 'intelligence',
            'rogue': 'wisdom',
            'cleric': 'dexterity',
            'wizard': 'strength',
            'warlock': 'strength',
            'paladin': 'intelligence',
            'barbarian': 'charisma'
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
                roll_text = f"{total}* (4d6: {','.join(map(str, rolls))} -> {','.join(map(str, rolls[:3]))})"  # * indicates it's being used
                self.rolled_score_labels[ability].setStyleSheet("color: #50c878; font-weight: bold;")  # Green for winning
            else:
                roll_text = f"{total} (4d6: {','.join(map(str, rolls))} -> {','.join(map(str, rolls[:3]))})"
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
                'difficulty_distribution': {'low': 0.5, 'moderate': 0.4, 'high': 0.1},
                'rest_rules': {'short_rest_duration': 1, 'long_rest_duration': 8},
                'style': 'standard'
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
            self.defeated_monsters = []  # Clear defeated monsters list for treasure tracking
            
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
            
            # Update scene description with encounter budget details
            difficulty_desc = encounter_data['difficulty'].capitalize()
            total_xp = encounter_data.get('total_xp', 0)
            level = encounter_data.get('level', character_level)
            
            # Build monster list with individual XP
            monster_details = []
            for monster in encounter_data['monsters']:
                monster_xp = monster.get('xp', 0)
                cr = monster.get('cr', '?')
                
                # Format CR display (handle fractions)
                if isinstance(cr, (int, float)):
                    if cr < 1:
                        # Convert decimal to fraction for display
                        if cr == 0.125:
                            cr_display = "1/8"
                        elif cr == 0.25:
                            cr_display = "1/4"  
                        elif cr == 0.5:
                            cr_display = "1/2"
                        else:
                            cr_display = str(cr)
                    else:
                        cr_display = str(int(cr))
                else:
                    cr_display = str(cr)
                    
                monster_details.append(f"{monster['name']} (CR {cr_display}, {monster_xp} XP)")
            
            # Create detailed encounter description
            if len(monster_details) == 1:
                monsters_text = monster_details[0]
            else:
                monsters_text = '\n'.join([f"• {detail}" for detail in monster_details])
            
            # Get the XP budget for this difficulty level
            try:
                from encounter_pane.encounter_generator import XP_BUDGETS
                budget_entry = next((entry for entry in XP_BUDGETS if entry["Level"] == level), None)
                if budget_entry:
                    max_budget = budget_entry.get(difficulty_desc, "Unknown")
                    budget_info = f"XP Budget: {total_xp} / {max_budget} ({difficulty_desc})"
                else:
                    budget_info = f"XP Budget: {total_xp} ({difficulty_desc})"
            except:
                budget_info = f"XP Budget: {total_xp} ({difficulty_desc})"
            
            desc = f"""== {difficulty_desc} Encounter (Level {level}) ==

{monsters_text}

{budget_info}
Character Level: {character_level}"""
            
            self.update_scene_description(desc)
            
            # Also update the encounter details in the Encounters tab
            if hasattr(self, 'encounter_details_text'):
                self.encounter_details_text.setPlainText(desc)
                print(f"[ENCOUNTER] Updated encounter details: {desc[:50]}...")
            
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
                        return character['level']
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
                        return character['id']
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
            
            # Track defeated monsters for treasure calculation
            if not hasattr(self, 'defeated_monsters'):
                self.defeated_monsters = []
            
            # Get monster CR for treasure calculation
            monster_cr = getattr(instance, 'monster_cr', 0)  # Default to CR 0 if not found
            self.defeated_monsters.append((instance.monster_name, monster_cr))
            
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
                # Replace defeated monster cards with post-combat action cards
                self._show_post_combat_actions()
                
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
                        old_xp = character['experience_points']
                        new_xp = old_xp + xp_value
                        
                        # Save XP to database immediately
                        success = game_engine.update_character_xp_sync(character['id'], new_xp)
                        if success:
                            print(f"Character XP saved to database: {old_xp} -> {new_xp} (+{xp_value})")
                            character['experience_points'] = new_xp
                        else:
                            print(f"Failed to save XP to database, keeping in memory only")
                            # Still update in memory as fallback
                            character['experience_points'] = new_xp
                        
                        # Check if town tab should be shown (character can now level up)
                        self.refresh_character_data()
                        
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
    
    def _show_post_combat_actions(self):
        """Add Loot and Short Rest action cards after the monster cards."""
        try:
            # End combat session - combat is over
            self._end_combat_session()
            
            # Find the next available row (after existing monster cards)
            next_row = self.monsters_layout.rowCount()
            
            # Create action cards
            loot_card = self._create_loot_action_card()
            rest_card = self._create_short_rest_action_card()
            
            # Add cards to the next row
            self.monsters_layout.addWidget(loot_card, next_row, 0)
            self.monsters_layout.addWidget(rest_card, next_row, 1)
            
        except Exception as e:
            print(f"Error showing post-combat actions: {e}")
    
    def _create_loot_action_card(self) -> QWidget:
        """Create the Loot action card for post-combat."""
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QPushButton
        from PyQt6.QtCore import Qt
        
        card = QWidget()
        card.setFixedSize(200, 120)
        card.setStyleSheet("""
            QWidget {
                background-color: #2a4a2a;
                border: 2px solid #4a6a4a;
                border-radius: 8px;
                margin: 1px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Title
        title = QLabel("💰 Loot")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #ffdd44; font-size: 14px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Search defeated\nenemies for treasure")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(desc)
        
        # Action button
        action_btn = QPushButton("Search for Loot")
        action_btn.clicked.connect(self._handle_loot_action)
        layout.addWidget(action_btn)
        
        return card
    
    def _create_short_rest_action_card(self) -> QWidget:
        """Create the Short Rest action card for post-combat."""
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QPushButton
        from PyQt6.QtCore import Qt
        
        card = QWidget()
        card.setFixedSize(200, 120)
        card.setStyleSheet("""
            QWidget {
                background-color: #4a4a2a;
                border: 2px solid #6a6a4a;
                border-radius: 8px;
                margin: 1px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Title
        title = QLabel("[SHIELD] Short Rest")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #44ddff; font-size: 14px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Rest and recover\nabilities & hit dice")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(desc)
        
        # Action button
        action_btn = QPushButton("Take Short Rest")
        action_btn.clicked.connect(self._handle_short_rest_action)
        layout.addWidget(action_btn)
        
        return card
    
    def _handle_loot_action(self):
        """Handle clicking the Loot action card."""
        self._log_monster_action("[SEARCH] Searching for loot...")
        
        if not hasattr(self, 'defeated_monsters') or not self.defeated_monsters:
            self._log_monster_action("No defeated monsters to loot.")
            return
            
        # Calculate individual treasure from each defeated monster
        total_individual_gp = 0
        treasure_details = []
        all_item_drops = []
        
        for monster_name, monster_cr in self.defeated_monsters:
            individual_gp = self._roll_individual_treasure(monster_cr)
            item_drops = self._roll_equipment_drops(monster_name, monster_cr)
            
            if individual_gp > 0:
                total_individual_gp += individual_gp
                treasure_details.append(f"{monster_name}: {individual_gp} GP")
            
            if item_drops:
                all_item_drops.extend(item_drops)
                item_names = [item['name'] for item in item_drops]
                treasure_details.append(f"{monster_name}: {', '.join(item_names)}")
        
        # Log individual treasure
        if total_individual_gp > 0:
            self._log_monster_action(f"💰 Individual Treasure: {total_individual_gp} GP total")
            for detail in treasure_details:
                self._log_monster_action(f"  └─ {detail}")
        
        # Check for encounter hoard based on difficulty
        hoard_gp = 0
        if hasattr(self, 'current_encounter') and self.current_encounter:
            hoard_treasure = self._check_for_hoard(self.current_encounter.difficulty if hasattr(self.current_encounter, 'difficulty') else 'moderate')
            if hoard_treasure:
                self._log_monster_action(f"🏆 {hoard_treasure}")
                # Extract GP amount from hoard string (e.g., "A Hoard with 200 GP and 0 magical items")
                import re
                gp_match = re.search(r'(\d+) GP', hoard_treasure)
                if gp_match:
                    hoard_gp = int(gp_match.group(1))
        
        # Add treasure to character's inventory/gold
        total_treasure = total_individual_gp + hoard_gp
        if total_treasure > 0:
            self._add_gold_to_character(total_treasure)
        
        # Add item drops to character's inventory
        if all_item_drops:
            self._add_items_to_character(all_item_drops)
            item_summary = ', '.join([f"{item['name']}" for item in all_item_drops])
            self._log_monster_action(f"🎒 Items Found: {item_summary}")
    
    def _roll_individual_treasure(self, monster_cr) -> int:
        """Roll individual treasure based on monster CR."""
        import random
        
        # Convert CR to numeric value if it's a string
        if isinstance(monster_cr, str):
            try:
                # Handle fractional CRs like "1/2", "1/4", etc.
                if '/' in monster_cr:
                    numerator, denominator = monster_cr.split('/')
                    cr_numeric = float(numerator) / float(denominator)
                else:
                    cr_numeric = float(monster_cr)
            except (ValueError, TypeError):
                cr_numeric = 0
        else:
            cr_numeric = float(monster_cr) if monster_cr else 0
        
        if cr_numeric <= 4:
            # CR 0-4: 3d6 GP
            return sum(random.randint(1, 6) for _ in range(3))
        elif cr_numeric <= 10:
            # CR 5-10: 2d8 × 10 GP
            return sum(random.randint(1, 8) for _ in range(2)) * 10
        elif cr_numeric <= 16:
            # CR 11-16: 2d10 × 100 GP
            return sum(random.randint(1, 10) for _ in range(2)) * 100
        else:
            # CR 17+: 2d8 × 1000 GP
            return sum(random.randint(1, 8) for _ in range(2)) * 1000
    
    def _roll_equipment_drops(self, monster_name: str, monster_cr) -> list:
        """Roll for equipment drops based on monster CR and type."""
        import random
        import json
        
        # Convert CR to numeric value
        if isinstance(monster_cr, str):
            try:
                if '/' in monster_cr:
                    numerator, denominator = monster_cr.split('/')
                    cr_numeric = float(numerator) / float(denominator)
                else:
                    cr_numeric = float(monster_cr)
            except (ValueError, TypeError):
                cr_numeric = 0
        else:
            cr_numeric = float(monster_cr) if monster_cr else 0
        
        # Base drop chance based on CR
        drop_chance = min(0.3 + (cr_numeric * 0.05), 0.85)  # 30% + 5% per CR, max 85%
        
        if random.random() > drop_chance:
            return []
        
        try:
            # Load equipment data
            with open('data/equipment.json', 'r') as f:
                equipment_data = json.load(f)
            
            # Filter equipment based on monster type and CR
            possible_drops = []
            
            # Determine monster category from name (basic categorization)
            monster_type = self._categorize_monster(monster_name.lower())
            
            for item in equipment_data:
                item_cr = self._get_item_cr_appropriateness(item, monster_type)
                if item_cr <= cr_numeric + 2 and item.get('rarity', 'common').lower() in ['common', 'uncommon']:
                    # Weight items by appropriateness
                    weight = max(1, int(4 - abs(item_cr - cr_numeric)))
                    for _ in range(weight):
                        possible_drops.append(item)
            
            if not possible_drops:
                return []
            
            # Roll number of items to drop (usually 1, occasionally 2)
            num_items = 1 if random.random() < 0.8 else 2
            
            drops = []
            for _ in range(min(num_items, len(possible_drops))):
                if possible_drops:
                    item = random.choice(possible_drops)
                    drops.append(item.copy())
                    # Remove to prevent duplicates
                    possible_drops = [i for i in possible_drops if i['name'] != item['name']]
            
            return drops
            
        except Exception as e:
            print(f"Error rolling equipment drops: {e}")
            return []
    
    def _categorize_monster(self, monster_name: str) -> str:
        """Categorize monster type for loot table purposes."""
        name = monster_name.lower()
        
        if any(word in name for word in ['goblin', 'orc', 'hobgoblin', 'bandit', 'thug', 'guard', 'soldier']):
            return 'humanoid_warrior'
        elif any(word in name for word in ['skeleton', 'zombie', 'ghost', 'wraith', 'vampire']):
            return 'undead'
        elif any(word in name for word in ['dragon', 'wyrm', 'drake']):
            return 'dragon'
        elif any(word in name for word in ['wolf', 'bear', 'boar', 'deer', 'eagle']):
            return 'beast'
        elif any(word in name for word in ['wizard', 'mage', 'cultist', 'priest', 'acolyte']):
            return 'spellcaster'
        else:
            return 'generic'
    
    def _get_item_cr_appropriateness(self, item: dict, monster_type: str) -> float:
        """Get the CR level this item is appropriate for based on monster type."""
        item_type = item.get('item_type', '').lower()
        
        # Base CR by item rarity
        base_cr = {'common': 0, 'uncommon': 3, 'rare': 8, 'very rare': 13, 'legendary': 17}.get(
            item.get('rarity', 'common').lower(), 0)
        
        # Adjust based on monster type preferences
        if monster_type == 'humanoid_warrior':
            if item_type in ['weapon', 'armor']:
                base_cr -= 1  # Warriors more likely to have combat gear
        elif monster_type == 'spellcaster':
            if 'staff' in item.get('name', '').lower() or item_type in ['tool']:
                base_cr -= 1  # Spellcasters more likely to have magical implements
        elif monster_type == 'beast':
            base_cr += 2  # Beasts less likely to have manufactured equipment
        elif monster_type == 'undead':
            if item_type in ['weapon', 'armor']:
                base_cr += 0.5  # Undead might have deteriorated equipment
        
        return max(0, base_cr)
    
    def _add_items_to_character(self, items: list):
        """Add dropped items to character inventory."""
        try:
            # Get game engine from parent for character update
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    
                    if character:
                        character_id = character['id']
                        
                        import sqlite3
                        conn = sqlite3.connect("talekeeper.db")
                        cursor = conn.cursor()
                        
                        for item in items:
                            # Check if item already exists in inventory
                            cursor.execute("""
                                SELECT quantity FROM character_inventory 
                                WHERE character_id = ? AND item_name = ? AND item_type = ?
                            """, (character_id, item['name'], item['item_type']))
                            
                            existing = cursor.fetchone()
                            
                            if existing:
                                # Update existing quantity
                                new_quantity = existing[0] + 1
                                cursor.execute("""
                                    UPDATE character_inventory 
                                    SET quantity = ?
                                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                                """, (new_quantity, character_id, item['name'], item['item_type']))
                            else:
                                # Add new item
                                cursor.execute("""
                                    INSERT INTO character_inventory 
                                    (character_id, item_name, item_type, quantity, equipped) 
                                    VALUES (?, ?, ?, 1, 0)
                                """, (character_id, item['name'], item['item_type']))
                        
                        conn.commit()
                        conn.close()
                        
                        # Force refresh inventory display
                        if hasattr(parent, '_force_reload_character'):
                            parent._force_reload_character()
                    
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error adding items to character: {e}")
    
    def _check_for_hoard(self, difficulty: str) -> str:
        """Check for hoard treasure based on encounter difficulty."""
        import random
        
        # Determine hoard chance based on difficulty
        hoard_chances = {
            'low': 0.05,      # 5%
            'moderate': 0.20, # 20%
            'hard': 0.95,     # 95%
            'high': 0.95      # Treat 'high' same as 'hard'
        }
        
        chance = hoard_chances.get(difficulty.lower(), 0.20)  # Default to moderate
        
        if random.random() <= chance:
            # Roll hoard treasure: 2d4 × 100 GP and 1d4-1 magical items
            hoard_gp_dice = sum(random.randint(1, 4) for _ in range(2))
            hoard_gp = hoard_gp_dice * 100
            
            magic_items_roll = random.randint(1, 4) - 1
            magic_items = max(0, magic_items_roll)  # Minimum 0 items
            
            magic_text = f" and {magic_items} magical item{'s' if magic_items != 1 else ''}" if magic_items > 0 else " and no magical items"
            
            return f"A Hoard with {hoard_gp} GP{magic_text}"
        
        return None
    
    def _add_gold_to_character(self, gold_amount: int):
        """Add gold to the current character."""
        try:
            # Get game engine from parent for character update
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    
                    if character:
                        # Add gold to character inventory
                        try:
                            # Update gold in inventory database
                            success = game_engine.add_gold_to_character_sync(character['id'], gold_amount)
                            if success:
                                self._log_monster_action(f"💰 Gained {gold_amount} gold pieces!")
                                print(f"[TREASURE] Successfully added {gold_amount} GP to character {character['id']}")
                                
                                # Refresh the equipment panel to show updated gold
                                self._refresh_equipment_panel(game_engine, character['id'])
                            else:
                                self._log_monster_action(f"💰 Found {gold_amount} gold pieces, but couldn't add to inventory!")
                                print(f"[TREASURE] Failed to add {gold_amount} GP to character inventory")
                        except Exception as e:
                            self._log_monster_action(f"💰 Found {gold_amount} gold pieces, but couldn't add to inventory!")
                            print(f"[TREASURE] Error adding gold: {e}")
                        return
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error adding gold to character: {e}")
    
    def _handle_short_rest_action(self):
        """Handle clicking the Short Rest action card."""
        self._log_monster_action("💤 Taking a short rest...")
        self._perform_short_rest()
    
    def _perform_short_rest(self):
        """Perform short rest - instant ability recovery and optional hit dice spending."""
        from datetime import datetime
        
        try:
            # Get current character
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    break
                parent = parent.parent()
            
            if not character:
                self._log_monster_action("[FAIL] No character found for short rest!")
                return
            
            # Update rest timestamp
            character['last_short_rest'] = datetime.now().isoformat()
            
            # End rage if active (rage ends on any rest)
            self._end_rage_on_rest()
            
            # Recover short rest abilities (instant)
            recovered_abilities = []
            
            # Universal resource restoration system
            try:
                from services.character_resources import CharacterResourceService
                resource_service = CharacterResourceService('talekeeper.db')
                
                # Restore all short rest resources
                result = resource_service.restore_resources_by_rest_type(character['id'], 'short_rest')
                if result.get('success', False):
                    for resource in result.get('restored_resources', []):
                        recovered_abilities.append(resource['resource_name'])
                
                # Refresh the character object with updated resource values
                character = game_engine.get_character_by_id_sync(character['id'])
                game_engine.current_character = character
                        
            except Exception as e:
                print(f"Error restoring short rest resources: {e}")
            
            # Generic ability restoration (fallback)
            if "Second Wind" in character.get('ability_uses', {}):
                character['ability_uses']["Second Wind"] = character.get('ability_uses_max', {}).get("Second Wind", 1)
                if 'Second Wind' not in recovered_abilities:
                    recovered_abilities.append("Second Wind")
            
            if "Action Surge" in character.get('ability_uses', {}):
                character['ability_uses']["Action Surge"] = character.get('ability_uses_max', {}).get("Action Surge", 1) 
                if 'Action Surge' not in recovered_abilities:
                    recovered_abilities.append("Action Surge")
            
            # Log recovery
            if recovered_abilities:
                self._log_monster_action(f"✨ Abilities recovered: {', '.join(recovered_abilities)}")
            
            # Open hit dice spending dialog (optional)
            self._show_hit_dice_dialog(game_engine, character)
            
            # Save character (save the whole game state)
            game_engine.save_game_sync()
            
            self._log_monster_action("[OK] Short rest completed!")
            
        except Exception as e:
            print(f"Error performing short rest: {e}")
            self._log_monster_action(f"[FAIL] Short rest failed: {e}")
    
    def _end_rage_on_rest(self):
        """End rage when character takes any rest."""
        try:
            # Find action panel in main window
            parent = self.parent()
            while parent:
                if hasattr(parent, 'action_panel'):
                    action_panel = parent.action_panel
                    if action_panel.character_context.get('raging', False):
                        action_panel.character_context['raging'] = False
                        action_panel.character_context['rage_turns_remaining'] = 0
                        self._log_monster_action("💨 RAGE ends due to rest")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error ending rage on rest: {e}")
    
    def _show_hit_dice_dialog(self, game_engine, character):
        """Show dialog for optional hit dice spending."""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QSpinBox, QDialogButtonBox, QGroupBox)
        from PyQt6.QtCore import Qt
        
        # Get current HP - prioritize fresh data from game engine
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine:
                    # Get fresh character data from database
                    fresh_character = parent.game_engine.get_character_by_id_sync(character['id'])
                    if fresh_character:
                        current_hp = fresh_character['hit_points_current']
                        max_hp = fresh_character['hit_points_max']
                        break
                parent = parent.parent()
            else:
                # Fallback to character object values
                current_hp = character['hit_points_current']
                max_hp = character['hit_points_max']
        except Exception as e:
            print(f"ERROR: Could not get HP: {e}")
            current_hp = character['hit_points_current']
            max_hp = character['hit_points_max']
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Hit Dice Recovery")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Status info
        status_label = QLabel(f"Current HP: {current_hp}/{max_hp}")
        status_label.setStyleSheet("font-weight: bold; color: #ff6b6b; font-size: 14px;")
        layout.addWidget(status_label)
        
        missing_hp = max_hp - current_hp
        if missing_hp > 0:
            info_label = QLabel(f"Missing {missing_hp} HP - You can spend hit dice to recover")
            layout.addWidget(info_label)
        
        # Hit dice info
        hit_dice_available = character['hit_dice_current']
        if hit_dice_available <= 0:
            no_dice_label = QLabel("[FAIL] No hit dice available!")
            no_dice_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            layout.addWidget(no_dice_label)
        else:
            # Determine hit die type based on class - check both class_id and resolved class name
            class_id = character.get('class_id', '') if isinstance(character, dict) else getattr(character, 'class_id', '')
            
            # Try to get the actual class name from database
            class_name = class_id
            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'game_engine'):
                        class_name = parent.game_engine._get_class_name_from_db(class_id)
                        break
                    parent = parent.parent()
            except:
                pass
            
            # Hit die mapping - check both normalized names and IDs
            hit_die_map = {
                # Class names
                'Fighter': 10, 'Paladin': 10, 'Ranger': 10, 'Barbarian': 12,
                'Rogue': 8, 'Monk': 8, 'Bard': 8, 'Cleric': 8, 'Druid': 8, 'Warlock': 8,
                'Artificer': 8, 'Sorcerer': 6, 'Wizard': 6,
                # Class IDs (lowercase versions)
                'fighter': 10, 'paladin': 10, 'ranger': 10, 'barbarian': 12,
                'rogue': 8, 'monk': 8, 'bard': 8, 'cleric': 8, 'druid': 8, 'warlock': 8,
                'artificer': 8, 'sorcerer': 6, 'wizard': 6
            }
            
            # Try class name first, then class_id, then class_id lowercase
            hit_die = hit_die_map.get(class_name, hit_die_map.get(class_id, hit_die_map.get(class_id.lower())))
            
            if hit_die is None:
                self._log_monster_action(f"[TARGET] ERROR: Unknown class '{class_id}'/'{class_name}' - cannot determine hit die")
                return
            
            self._log_monster_action(f"[TARGET] DEBUG: class_id='{class_id}', class_name='{class_name}', hit_die=d{hit_die}")
            con_mod = character['constitution_modifier']
            
            dice_group = QGroupBox(f"Available Hit Dice: {hit_dice_available} × d{hit_die}")
            dice_layout = QVBoxLayout(dice_group)
            
            # Spending controls
            spend_layout = QHBoxLayout()
            spend_layout.addWidget(QLabel("Spend:"))
            
            dice_spinner = QSpinBox()
            dice_spinner.setMinimum(0)
            dice_spinner.setMaximum(min(hit_dice_available, 10))  # Max 10 at once
            dice_spinner.setValue(1 if hit_dice_available > 0 else 0)
            spend_layout.addWidget(dice_spinner)
            
            spend_layout.addWidget(QLabel(f"d{hit_die} (+ {con_mod} CON each)"))
            dice_layout.addLayout(spend_layout)
            
            # Roll button
            roll_btn = QPushButton("[DICE] Roll Hit Dice")
            roll_btn.clicked.connect(lambda: self._roll_hit_dice(dialog, game_engine, character, 
                                                               dice_spinner.value(), hit_die, status_label))
            dice_layout.addWidget(roll_btn)
            
            layout.addWidget(dice_group)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.accept)  # Close button acts like OK
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def _roll_hit_dice(self, dialog, game_engine, character, num_dice, hit_die, status_label):
        """Roll hit dice and apply healing."""
        if num_dice <= 0:
            return
            
        if character['hit_dice_current'] < num_dice:
            self._log_monster_action("[FAIL] Not enough hit dice available!")
            return
        
        from services.dice import DiceRoller
        dice_roller = DiceRoller()
        
        total_healing = 0
        rolls = []
        
        for i in range(num_dice):
            # Roll the hit die
            roll = dice_roller.roll(f"1d{hit_die}")
            healing = roll + character['constitution_modifier']
            healing = max(1, healing)  # Minimum 1 HP per die
            total_healing += healing
            rolls.append(f"d{hit_die}({roll})+{character['constitution_modifier']}={healing}")
        
        # Apply healing (cannot exceed max HP) - use combat system fields
        old_hp = character.get('current_hit_points', character['hit_points_current'])
        max_hp = character.get('max_hit_points', character['hit_points_max'])
        new_hp = min(max_hp, old_hp + total_healing)
        actual_healing = new_hp - old_hp
        
        # Update both HP field sets to keep them in sync
        if 'current_hit_points' in character:
            character['current_hit_points'] = new_hp
        character['hit_points_current'] = new_hp
        
        # Spend the hit dice
        character['hit_dice_current'] -= num_dice
        
        # Log the results
        roll_details = " + ".join(rolls)
        if actual_healing < total_healing:
            self._log_monster_action(f"[DICE] Hit Dice: {roll_details} = {total_healing} healing")
            self._log_monster_action(f"💚 HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {actual_healing}, max HP reached)")
        else:
            self._log_monster_action(f"[DICE] Hit Dice: {roll_details} = {total_healing} healing")
            self._log_monster_action(f"💚 HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {actual_healing})")
        
        # Update status label
        status_label.setText(f"Current HP: {new_hp}/{max_hp}")
        
        # Save changes to database FIRST (source of truth)
        game_engine.update_character_hp_sync(new_hp, max_hp)
        
        # Update character sheet display to reflect database state
        self._update_character_sheet_hp(new_hp, max_hp)
        
        # Close dialog if at full health
        if new_hp >= max_hp:
            self._log_monster_action("💚 Fully healed!")
            dialog.accept()
    
    def _update_character_sheet_hp(self, current_hp: int, max_hp: int):
        """Update the character sheet HP display."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_sheet'):
                    parent.character_sheet.update_hp(current_hp, max_hp)
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"ERROR: Could not update character sheet HP: {e}")
    
    def _perform_long_rest(self):
        """Perform long rest - restore all resources according to D&D 5e rules."""
        from datetime import datetime
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            # Get current character
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    break
                parent = parent.parent()
            
            if not character:
                self._log_monster_action("[FAIL] No character found for long rest!")
                return
            
            # Confirm long rest (since it's a significant action)
            reply = QMessageBox.question(
                self, 
                "Long Rest", 
                f"Take a Long Rest?\n\n{character['name']} will:\n• Restore all hit points\n• Restore all spell slots\n• Restore all long rest abilities\n• Restore half of spent hit dice\n\nThis represents 8 hours of rest in a safe location.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            self._log_monster_action("[MOON] Beginning long rest...")
            
            # === D&D 5e LONG REST BENEFITS ===
            
            # 1. Restore all hit points to maximum
            old_hp = character['hit_points_current']
            max_hp = character['hit_points_max']
            character['hit_points_current'] = max_hp
            character['current_hit_points'] = max_hp  # Alternative field
            self._log_monster_action(f"💚 HP fully restored: {old_hp}/{max_hp} -> {max_hp}/{max_hp}")
            
            # 2. Restore all spent hit dice (up to half maximum, minimum 1)
            character_level = character['level']
            max_hit_dice = character_level
            current_hit_dice = character['hit_dice_current']
            hit_dice_to_restore = max(1, max_hit_dice // 2)
            new_hit_dice = min(max_hit_dice, current_hit_dice + hit_dice_to_restore)
            
            if new_hit_dice > current_hit_dice:
                character['hit_dice_current'] = new_hit_dice
                self._log_monster_action(f"[DICE] Hit Dice restored: {current_hit_dice} -> {new_hit_dice} (gained {new_hit_dice - current_hit_dice})")
            
            # 3. Restore all spell slots
            if 'spell_slots_current' in character and character['spell_slots_current']:
                spell_slots_restored = []
                for level, current_slots in character['spell_slots_current'].items():
                    max_slots = character.get('spell_slots_max', {}).get(level, 0)
                    if current_slots < max_slots:
                        character['spell_slots_current'][level] = max_slots
                        spell_slots_restored.append(f"Level {level}: {current_slots} -> {max_slots}")
                
                if spell_slots_restored:
                    self._log_monster_action(f"✨ Spell slots restored: {', '.join(spell_slots_restored)}")
            
            # 4. Restore all long rest abilities
            abilities_restored = []
            
            # Universal resource restoration system
            try:
                from services.character_resources import CharacterResourceService
                resource_service = CharacterResourceService('talekeeper.db')
                
                # Restore all short rest resources (long rest includes short rest benefits)
                short_result = resource_service.restore_resources_by_rest_type(character['id'], 'short_rest')
                if short_result.get('success', False):
                    for resource in short_result.get('restored_resources', []):
                        abilities_restored.append(resource['resource_name'])
                
                # Restore all long rest resources
                long_result = resource_service.restore_resources_by_rest_type(character['id'], 'long_rest')
                if long_result.get('success', False):
                    for resource in long_result.get('restored_resources', []):
                        abilities_restored.append(resource['resource_name'])
                
                # Refresh the character object with updated resource values
                character = game_engine.get_character_by_id_sync(character['id'])
                game_engine.current_character = character
                        
            except Exception as e:
                print(f"Error restoring long rest resources: {e}")
            
            # Generic ability restoration (fallback for other systems)
            for ability in ["Healing Potion"]:  # Non-class specific abilities
                if ability in character.get('ability_uses', {}):
                    max_uses = character.get('ability_uses_max', {}).get(ability, 1)
                    if character['ability_uses'][ability] < max_uses:
                        character['ability_uses'][ability] = max_uses
                        if ability not in abilities_restored:
                            abilities_restored.append(ability)
            
            if abilities_restored:
                self._log_monster_action(f"[LIGHTNING] Abilities restored: {', '.join(abilities_restored)}")
            
            # 5. Reset action economy for new day (if in combat)
            if hasattr(self, 'current_combat_session') and self.current_combat_session:
                # Reset action surge usage
                if 'action_surge_used' in character:
                    character['action_surge_used'] = False
            
            # 6. Update rest timestamp
            character['last_long_rest'] = datetime.now().isoformat()
            character['updated_at'] = datetime.now().isoformat()
            
            # Save character to database (following DB-first pattern)
            game_engine.update_character_hp_sync(max_hp, max_hp)  # This also saves the character
            
            # Character changes are saved via SQLite game engine above
            
            # Update character sheet display
            self._update_character_sheet_hp(max_hp, max_hp)
            
            self._log_monster_action("🌅 Long rest completed! All resources restored.")
            
            # Log to parent log panel
            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_info(f"[MOON] {character['name']} completed a long rest - all resources restored")
                        break
                    parent = parent.parent()
            except:
                pass
            
        except Exception as e:
            print(f"Error performing long rest: {e}")
    
    def _refresh_equipment_panel(self, game_engine, character_id):
        """Refresh the equipment panel to show updated inventory."""
        try:
            # Navigate up the parent hierarchy to find the main window
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_panel') and hasattr(parent.character_panel, 'equipment_panel'):
                    equipment_panel = parent.character_panel.equipment_panel
                    if hasattr(equipment_panel, 'load_equipment_data'):
                        # Get full character data for proper equipment loading
                        character = game_engine.get_character_sync(character_id)
                        if character:
                            equipped_items = game_engine.get_character_equipment_sync(character_id)
                            character_inventory = game_engine.get_character_inventory_sync(character_id)
                            equipment_panel.load_equipment_data(
                                equipped_items, character_inventory, 
                                character['strength'], character['dexterity'], 
                                character.get('class_id', ''), character['constitution']
                            )
                        print(f"[UI] Refreshed equipment panel for character {character_id}")
                        return
                parent = parent.parent()
            print(f"[UI] Could not find equipment panel to refresh")
        except Exception as e:
            print(f"[UI] Error refreshing equipment panel: {e}")
            self._log_monster_action(f"[FAIL] Long rest failed: {e}")