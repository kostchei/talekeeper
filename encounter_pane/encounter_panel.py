"""
Encounter Pane Widget - Central content area for encounters and exploration

PyQt6 widget that serves as the main content display area:
- Monster/NPC encounters
- Story text and descriptions
- Environmental details
- Combat interfaces
- Exploration content

- Designed to match ui_plan.md specifications:
- Layout dimensions follow the active profile for center panel sizing
- Flexible content display
- Dark theme styling
- Integration ready for GameEngine encounter data
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QTextEdit, QScrollArea,
                            QTabWidget, QListWidget, QListWidgetItem,
                            QSplitter, QGroupBox, QGridLayout, QComboBox,
                            QSpinBox, QCheckBox, QStackedWidget, QRadioButton,
                            QButtonGroup, QProgressBar, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any
import json
import os
import random
from uuid import uuid4
from .encounter_generator import EncounterGenerator, roll_monster_hp
from .campaign_frame import CampaignFrame
from services.equipment_database import EquipmentDatabase
from services.proficiency_bonus import get_proficiency_bonus
from .town_encounter import TownEncounterPanel, ShopInterface
from .alt_encounters import generate_trap, generate_hazard, generate_skill_challenge
from .skill_challenge_widget import SkillChallengeWidget
from .hazard_widget import HazardWidget
from .spell_selection_widget import SpellSelectionWidget
from services.skill_challenge_manager import SkillChallengeManager
from services.skill_challenge_rewards import SkillChallengeRewards
from services.stealth_mechanics import StealthMechanicsService
# Monster models no longer needed - using direct SQL queries and local dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime

from ui.layout_profiles import BASELINE_PROFILE, LayoutProfile

def sync_hit_dice_with_level(character):
    """Ensure hit dice maximum matches level and add only new dice."""
    level = character.get('level', 1)
    prev_max = character.get('hit_dice_max', 0)
    hit_dice_max = max(prev_max, level)
    if hit_dice_max != prev_max:
        diff = hit_dice_max - prev_max
        character['hit_dice_max'] = hit_dice_max
        character['hit_dice_current'] = min(
            hit_dice_max,
            character.get('hit_dice_current', 0) + diff
        )
    return character.get('hit_dice_current', 0), hit_dice_max


def restore_hit_dice_on_long_rest(character):
    """Restore hit dice per long rest rules and sync with level."""
    current_before, hit_dice_max = sync_hit_dice_with_level(character)
    hit_dice_to_restore = max(1, hit_dice_max // 2)
    new_hit_dice = min(hit_dice_max, current_before + hit_dice_to_restore)
    restored = new_hit_dice - current_before
    character['hit_dice_current'] = new_hit_dice
    return new_hit_dice, restored


@dataclass
class CombatSession:
    """Simple combat session for action economy tracking."""
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    
    # Combat state
    is_active: bool = True
    current_round: int = 1
    current_turn: int = 0

    # Stealth state
    player_hidden: bool = False
    stealth_dc: int = 0
    surprise_round: bool = False
    
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

        try:
            self.action_economy.start_combat([character_id])
        except Exception as e:
            print(f"Error starting action economy combat: {e}")

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
    
    def roll_initiative(self, player_dex_mod: int, monster_instances: list, monster_data: dict, character_context: dict = None, character_features: dict = None) -> int:
        """Roll initiative for player and all monsters with advantage/disadvantage support."""
        import random
        from services.advantage_system import advantage_system, RollType

        # Create context for player initiative roll
        feats = character_context.get('feats', []) if character_context else []
        prof_bonus = character_context.get('proficiency_bonus', 2) if character_context else 2

        # Calculate proficiency bonus from level if not in character_context
        if character_context and 'proficiency_bonus' not in character_context:
            level = character_context.get('level', 1)
            prof_bonus = 2 + ((level - 1) // 4)  # Standard D&D progression

        initiative_context = {
            'dexterity_modifier': player_dex_mod,
            'feats': feats,
            'proficiency_bonus': prof_bonus,
            'character_features': character_features or {}
        }
        
        if character_context:
            feature_flags = character_context.get('feature_flags')
            if isinstance(feature_flags, dict):
                initiative_context['feature_flags'] = feature_flags

        # Get advantage/disadvantage sources for initiative
        advantage_sources = advantage_system.get_common_advantage_sources(RollType.INITIATIVE, initiative_context)
        disadvantage_sources = advantage_system.get_common_disadvantage_sources(RollType.INITIATIVE, initiative_context)
        
        feature_map = character_features or {}
        if isinstance(feature_map, list):
            feature_map = {
                feature.get('name'): feature
                for feature in feature_map
                if isinstance(feature, dict) and feature.get('name')
            }

        if 'Remarkable Athlete' in feature_map:
            initiative_context['remarkable_athlete'] = True

        # Calculate total initiative modifier (DEX + proficiency for Alertness feat)
        total_initiative_mod = player_dex_mod
        has_alert = ('Alert' in initiative_context.get('feats', []) or
                     'Alert' in initiative_context.get('character_features', {}))

        if has_alert:
            prof_bonus = initiative_context.get('proficiency_bonus', 2)
            total_initiative_mod += prof_bonus

        # Calculate advantage state and roll
        advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)
        self.player_initiative, roll_breakdown = advantage_system.roll_d20_with_advantage(advantage_state, total_initiative_mod)
        
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
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout_profile: Optional[LayoutProfile] = None,
    ):
        super().__init__(parent)
        self.layout_profile = layout_profile or BASELINE_PROFILE
        self.panel_width = self.layout_profile.encounter_panel_width
        self.panel_height = self.layout_profile.encounter_panel_height
        self.current_encounter = None
        self.encounter_mode = "exploration"  # exploration, encounter, combat, character_creation
        self.character_creation_data = {}  # Store character creation progress
        self.creation_step = 0  # Track current creation step
        
        # Initialize encounter generator and campaign frame
        self.encounter_generator = None
        self.campaign_frame = None
        self._load_campaign_frame()
        
        # Track current encounter instances
        self.current_encounter_id = None
        self.encounter_instances = {}  # instance_id -> EncounterInstance
        self.selected_monster_id = None  # Currently selected monster for targeting
        self.current_encounter = None  # Current Encounter object for database tracking
        self.vendor_widget = None  # Active vendor/shop interface

        # Skill challenge system
        self.skill_challenge_manager = SkillChallengeManager()
        self.skill_challenge_rewards = SkillChallengeRewards()
        self.skill_challenge_widget = None  # Active skill challenge interface

        # Hazard system
        self.hazard_widget = None  # Active hazard interface

        # Initialize stealth mechanics
        try:
            self.stealth_service = StealthMechanicsService()
        except Exception as e:
            print(f"Warning: Could not initialize stealth service: {e}")
            self.stealth_service = None
        self.player_hidden = False
        self.stealth_dc = 0
        
        # Set fixed size (fits above action cards)
        self.setFixedSize(self.panel_width, self.panel_height)
        self._setup_ui()
        self._apply_styles()
        self._show_initial_random_encounter()
    
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
        self.content_tabs.addTab(self.main_content_tab, "Description")

        main_content_layout = QVBoxLayout(self.main_content_tab)
        main_content_layout.setContentsMargins(1, 1, 1, 1)
        main_content_layout.setSpacing(1)

        # Hidden status indicator (initially hidden)
        self.hidden_status_frame = QFrame()
        self.hidden_status_frame.setObjectName("hiddenStatusFrame")
        self.hidden_status_frame.setStyleSheet("""
            QFrame#hiddenStatusFrame {
                background-color: #1a3a2a;
                border: 2px solid #4a8a6a;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        hidden_layout = QHBoxLayout(self.hidden_status_frame)
        hidden_layout.setContentsMargins(6, 3, 6, 3)

        self.hidden_status_label = QLabel("[HIDDEN] You are undetected (Stealth DC: 0)")
        self.hidden_status_label.setStyleSheet("""
            QLabel {
                color: #88ff88;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        hidden_layout.addWidget(self.hidden_status_label)
        hidden_layout.addStretch()

        self.hidden_status_frame.hide()  # Initially hidden
        main_content_layout.addWidget(self.hidden_status_frame)

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
        action_buttons_layout.setContentsMargins(1, 1, 1, 1)
        action_buttons_layout.setSpacing(1)

        self.travel_btn = QPushButton("Travel")
        self.travel_btn.clicked.connect(lambda: self.exploration_action.emit("travel"))
        action_buttons_layout.addWidget(self.travel_btn)

        self.downtime_btn = QPushButton("Downtime")
        self.downtime_btn.clicked.connect(lambda: self.exploration_action.emit("downtime"))
        action_buttons_layout.addWidget(self.downtime_btn)

        self.long_rest_btn = QPushButton("Long Rest")
        self.long_rest_btn.clicked.connect(self._perform_long_rest)
        action_buttons_layout.addWidget(self.long_rest_btn)
        
        main_content_layout.addWidget(self.action_buttons_frame)
        
        # --- ENCOUNTERS TAB ---
        self.encounters_tab = QWidget()
        self.content_tabs.addTab(self.encounters_tab, "Encounters")
        
        self.encounters_layout = QVBoxLayout(self.encounters_tab)
        encounters_layout = self.encounters_layout
        encounters_layout.setContentsMargins(1, 1, 1, 1)
        encounters_layout.setSpacing(1)
        
        # Encounters list widget (was missing)
        # Encounter details area (for XP budget info) - AT THE TOP
        self.encounter_details_text = QTextEdit()
        self.encounter_details_text.setObjectName("encounterDetailsText")
        self.encounter_details_text.setReadOnly(True)
        self.encounter_details_text.setMinimumHeight(220)
        self.encounter_details_text.setMaximumHeight(240)
        self.encounter_details_text.setPlainText("Click 'Generate Random Encounter' to see encounter details...")
        self.encounter_details_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 2px;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        encounters_layout.addWidget(self.encounter_details_text)
        
        # Encounters list widget
        self.encounters_list = QListWidget()
        self.encounters_list.setObjectName("encountersList")
        self.encounters_list.setMaximumHeight(150)
        self.encounters_list.setVisible(False)
        encounters_layout.addWidget(self.encounters_list)

        # Encounter type selector
        self.encounter_type_combo = QComboBox()
        self._random_encounter_topics = [
            "Monsters",
            "Traps",
            "Hazards",
            "Skill Challenge",
            "Vendors",
        ]
        self.encounter_type_combo.addItems(["Random"] + self._random_encounter_topics)
        self.encounter_type_combo.setCurrentText("Random")
        encounters_layout.addWidget(self.encounter_type_combo)

        # Generate encounter button
        self.generate_encounter_btn = QPushButton("Generate Encounter")
        self.generate_encounter_btn.clicked.connect(self._generate_selected_encounter)
        encounters_layout.addWidget(self.generate_encounter_btn)

        self.encounter_actions_frame = QFrame()
        self.encounter_actions_frame.setObjectName("actionButtonsFrame")
        encounter_actions_layout = QHBoxLayout(self.encounter_actions_frame)
        encounter_actions_layout.setContentsMargins(1, 1, 1, 1)
        encounter_actions_layout.setSpacing(1)

        self.influence_btn = QPushButton("Influence")
        self.influence_btn.clicked.connect(lambda: self.exploration_action.emit("influence"))
        encounter_actions_layout.addWidget(self.influence_btn)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(lambda: self.exploration_action.emit("search"))
        encounter_actions_layout.addWidget(self.search_btn)

        self.study_btn = QPushButton("Study")
        self.study_btn.clicked.connect(lambda: self.exploration_action.emit("study"))
        encounter_actions_layout.addWidget(self.study_btn)

        self.hide_btn = QPushButton("Hide")
        self.hide_btn.clicked.connect(lambda: self.exploration_action.emit("hide"))
        encounter_actions_layout.addWidget(self.hide_btn)

        encounters_layout.addWidget(self.encounter_actions_frame)

        # Monster cards container (grid layout for multiple rows)
        self.monsters_frame = QFrame()
        self.monsters_frame.setObjectName("monstersFrame")
        from PyQt6.QtWidgets import QGridLayout
        self.monsters_layout = QGridLayout(self.monsters_frame)
        self.monsters_layout.setContentsMargins(1, 1, 1, 1)
        self.monsters_layout.setSpacing(1)
        self.monsters_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.monsters_frame.setVisible(False)
        encounters_layout.addWidget(self.monsters_frame)
        
        
        # Trap card container
        self.trap_card_frame = QFrame()
        self.trap_card_frame.setObjectName("trapCardFrame")
        self.trap_card_layout = QVBoxLayout(self.trap_card_frame)
        self.trap_card_layout.setContentsMargins(1, 1, 1, 1)
        self.trap_card_layout.setSpacing(4)
        self.trap_card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.trap_card_frame.setMaximumWidth(160)
        self.trap_card_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.trap_card_frame.setVisible(False)
        encounters_layout.addWidget(self.trap_card_frame, alignment=Qt.AlignmentFlag.AlignLeft)
        # --- CHARACTER CREATION TAB ---
        self.character_creation_tab = QWidget()
        # Store the index so we can reliably show/hide this tab later even if
        # additional tabs are added or removed. Previously the code assumed the
        # character creation tab would always be at index 3, but the encounter
        # panel update reduced the number of tabs which broke the 'Create
        # Character' button. By capturing the index returned from addTab we
        # can reference it dynamically.
        self.character_creation_tab_index = self.content_tabs.addTab(
            self.character_creation_tab, "Create Character"
        )
        self.content_tabs.setTabVisible(self.character_creation_tab_index, False)
        
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
    
    def _show_initial_random_encounter(self):
        """Display a randomly selected encounter on startup."""
        self.encounter_type_combo.setCurrentText("Random")
        self._generate_selected_encounter()

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
            padding: 1px;
        }

        QLabel#sectionLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            padding: 1px;
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
            padding: 2px;
            margin: 1px;
        }
        
        QTabBar::tab:selected {
            background-color: #1a1a1a;
            color: #ffffff;
            border-bottom: 1px solid #1a1a1a;
        }
        
        QTabBar::tab:hover {
            background-color: #3a3a3a;
        }
        
        QTextEdit#sceneText {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 2px;
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
            padding: 2px;
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
            padding: 2px;
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
            padding: 2px;
        }
        
        QListWidget#classSelectionList, QListWidget#backgroundList, QListWidget#speciesList, QListWidget#equipmentList {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            alternate-background-color: #1a1a1a;
        }

        QListWidget#classSelectionList::item, QListWidget#backgroundList::item, QListWidget#speciesList::item {
            padding: 2px;
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
            padding: 2px;
            font-size: 13px;
        }
        
        QLabel#racialBonus {
            color: #50c878;
            font-weight: bold;
        }
        
        QLabel#finalScore {
            color: #2b211c;
            font-weight: bold;
            font-size: 14px;
        }
        
        QLabel#pointsRemaining {
            color: #ff9500;
            font-weight: bold;
            padding: 2px;
        }
        
        QLabel#classStatsInfo {
            color: #4a90e2;
            font-weight: bold;
            padding: 2px;
            background-color: #1e1e1e;
            border: 1px solid #4a90e2;
            border-radius: 4px;
        }
        
        QLabel#rolledScore {
            color: #ff9500;
            font-weight: bold;
            font-size: 12px;
        }
        
        QLabel#abilityAbbrev {
            color: #2b211c;
            font-weight: bold;
            font-size: 14px;
            padding: 2px;
        }
        
        QPushButton#createCharacterBtn {
            background-color: #50c878;
            color: #ffffff;
            border: 1px solid #50c878;
            border-radius: 6px;
            padding: 2px;
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
            border-width: 2px;
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
            padding: 2px;
            margin-right: 1px;
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
            padding: 2px;
            border-bottom: 1px solid {palette['border']};
        }}
        
        QPushButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 2px;
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
            padding: 2px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        QPushButton#rollButton:hover {{
            background-color: {palette['accent_secondary']};
        }}
        
        QPushButton#rollButton:pressed {{
            background-color: {palette['accent_primary']};
        }}
        
        QTextEdit#sceneText {{
            background-color: {palette['surface']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 2px;
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

        # Mark current encounter as combat
        if self.current_encounter:
            self.current_encounter.start_combat()

        # Initialize combat session for action economy
        self._init_combat_session()

        # Update town tab state since we're now in combat
        if hasattr(self, 'town_tab') and self.town_tab is not None:
            self._update_town_tab_state()

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
            # Clear hidden state
            self.player_hidden = False
            self.stealth_dc = 0
            if hasattr(self, 'hidden_status_frame'):
                self.hidden_status_frame.hide()

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

            # Update town tab state since combat has ended
            if hasattr(self, 'town_tab') and self.town_tab is not None:
                self._update_town_tab_state()

        except Exception as e:
            print(f"Error ending combat session: {e}")
    
    def _update_action_buttons(self):
        """Update button states based on current mode."""
        exploration_mode = self.encounter_mode == "exploration"
        encounter_mode = self.encounter_mode == "encounter"
        combat_mode = self.encounter_mode == "combat"

        # Description buttons
        self.travel_btn.setEnabled(exploration_mode)
        self.downtime_btn.setEnabled(not combat_mode)
        self.long_rest_btn.setEnabled(not combat_mode)

        # Encounter buttons
        self.influence_btn.setEnabled(not combat_mode)
        self.search_btn.setEnabled(not combat_mode)
        self.study_btn.setEnabled(not combat_mode)
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
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 2px;
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.5;
            }
        """)
        
        # Ensure visibility
        self.scene_text.raise_()
        self.scene_text.show()
    
    def update_environment_details(self, details: str):
        """Update environmental information (environment tab removed)."""
        pass
    
    def add_encounter(self, encounter_data: Dict[str, Any]):
        """Add an encounter to the list."""
        encounter_name = encounter_data.get('name', 'Unknown Encounter')
        difficulty = encounter_data.get('difficulty', 'Normal')
        
        item = QListWidgetItem(f"{encounter_name} ({difficulty})")
        item.setData(Qt.ItemDataRole.UserRole, encounter_data)
        self.encounters_list.addItem(item)
        self.encounters_list.setVisible(True)
        
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

        # Clear hidden state
        self.player_hidden = False
        self.stealth_dc = 0
        if hasattr(self, 'hidden_status_frame'):
            self.hidden_status_frame.hide()
        
        # Clear encounters list
        if hasattr(self, 'encounters_list'):
            self.encounters_list.clear()
            self.encounters_list.setVisible(False)

        if hasattr(self, 'monsters_frame'):
            self.monsters_frame.setVisible(False)
        
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
        # Use the stored tab index instead of a hardcoded value. This prevents
        # index errors when the number of tabs changes.
        self.content_tabs.setTabVisible(self.character_creation_tab_index, True)
        self.content_tabs.setCurrentIndex(self.character_creation_tab_index)
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
        # Hide the character creation tab using the stored index
        self.content_tabs.setTabVisible(self.character_creation_tab_index, False)
        self.set_exploration_mode()
        self.creation_step = 0
        self.character_creation_data = {}
    
    def _is_in_combat(self) -> bool:
        """Check if currently in combat"""
        return (self.current_encounter is not None and
                hasattr(self.current_encounter, 'is_combat') and
                self.current_encounter.is_combat and
                len(self.get_living_monsters()) > 0)

    def _update_town_tab_state(self):
        """Update town tab tooltip and enabled state based on combat status"""
        if self.town_tab_index < 0:
            return

        if self._is_in_combat():
            # Disable interaction during combat
            tooltip = "Can't go to town to train yet, still in combat"
            self.content_tabs.setTabEnabled(self.town_tab_index, False)
        else:
            # Enable interaction outside combat
            tooltip = "Go here to level up"
            self.content_tabs.setTabEnabled(self.town_tab_index, True)

        self.content_tabs.setTabToolTip(self.town_tab_index, tooltip)

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

        # Show town tab but don't automatically switch if in combat
        if self.town_tab_index >= 0:
            self.content_tabs.setTabVisible(self.town_tab_index, True)
            self._update_town_tab_state()

            # Only switch to town tab if not in combat
            if not self._is_in_combat():
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
    

    def _get_game_engine(self):
        """Fetch the active game engine reference from the widget hierarchy."""
        parent = self.parent()
        while parent:
            if hasattr(parent, "game_engine"):
                return parent.game_engine
            parent = parent.parent()
        return None

    def refresh_character_data(self):
        """Refresh character data and check if town tab should be shown/hidden"""
        can_level = self._can_character_level_up()

        if can_level and self.town_tab is None:
            # Character can now level up - show town tab
            self.show_town_encounter()
        elif can_level and self.town_tab is not None:
            # Character can level up and tab exists - update its state
            self._update_town_tab_state()
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # Title
        title = QLabel("Class Features")
        title.setObjectName("creationStepTitle")
        layout.addWidget(title)

        # Class features container (will be populated based on selected class)
        self.class_features_container = QWidget()
        self.class_features_layout = QVBoxLayout(self.class_features_container)
        self.class_features_layout.setContentsMargins(0, 0, 0, 0)
        self.class_features_layout.setSpacing(1)
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

        # Add spell selection for spellcasting classes
        self._setup_spell_selection(selected_class_name)

        # Handle class-specific features
        if selected_class_name == "Fighter":
            self._setup_fighter_features()
        elif selected_class_name == "Rogue":
            self._setup_rogue_features()
        elif selected_class_name == "Warlock":
            self._setup_warlock_features()
    
    def _setup_fighter_features(self):
        """Setup Fighter Level 1 class features."""
        # Fighting Style selection
        fighting_style_group = QGroupBox("Fighting Style")
        fs_layout = QVBoxLayout(fighting_style_group)
        fs_layout.setContentsMargins(5, 5, 5, 5)
        fs_layout.setSpacing(1)

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

    def _setup_rogue_features(self):
        """Setup Rogue Level 1 class features."""

        # Expertise selection
        expertise_group = QGroupBox("Expertise - Choose 2")
        expertise_layout = QVBoxLayout(expertise_group)
        expertise_layout.setContentsMargins(5, 5, 5, 5)
        expertise_layout.setSpacing(1)

        # Get skills the character is proficient in
        proficient_skills = self._get_character_proficient_skills()

        if not proficient_skills:
            no_skills_label = QLabel("Select your class skills above, then expertise choices will appear here.")
            no_skills_label.setStyleSheet("color: #ffa500; font-style: italic;")
            expertise_layout.addWidget(no_skills_label)

            # Store a reference to this label so we can update it later
            self.expertise_placeholder_label = no_skills_label

        else:
            # Create checkboxes for expertise selection
            expertise_skills_frame = QFrame()
            expertise_skills_layout = QGridLayout(expertise_skills_frame)

            self.expertise_checkboxes = {}
            row, col = 0, 0
            for skill in proficient_skills:
                checkbox = QCheckBox(skill)
                checkbox.toggled.connect(
                    lambda state, s=skill: self._on_expertise_skill_toggled(s, state)
                )
                self.expertise_checkboxes[skill] = checkbox
                expertise_skills_layout.addWidget(checkbox, row, col)

                col += 1
                if col > 2:  # 3 columns
                    col = 0
                    row += 1

            expertise_layout.addWidget(expertise_skills_frame)

            # Add selection count label
            self.expertise_count_label = QLabel("Selected: 0 / 2")
            self.expertise_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
            expertise_layout.addWidget(self.expertise_count_label)

        self.class_features_layout.addWidget(expertise_group)

        # Thieves' Tools note
        tools_group = QGroupBox("Proficiencies")
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setContentsMargins(5, 5, 5, 5)
        tools_layout.setSpacing(1)

        tools_note = QLabel("Proficiency: Thieves' Tools (auto-granted)")
        tools_note.setStyleSheet("color: #4a9eff;")
        tools_layout.addWidget(tools_note)

        self.class_features_layout.addWidget(tools_group)

    def _setup_warlock_features(self):
        """Setup Warlock Level 1 class features."""

        invocation_group = QGroupBox("Eldritch Invocation")
        invocation_layout = QVBoxLayout(invocation_group)
        invocation_layout.setContentsMargins(5, 5, 5, 5)
        invocation_layout.setSpacing(1)

        self.invocation_combo = QComboBox()
        self.invocation_combo.addItem("Select an Invocation...", None)

        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description, prerequisites
                FROM invocations
                ORDER BY name
            """)

            invocations = cursor.fetchall()
            conn.close()

            for inv_id, name, description, prereqs_json in invocations:
                import json
                prereqs = json.loads(prereqs_json) if prereqs_json else {}

                if not prereqs or prereqs == {}:
                    self.invocation_combo.addItem(f"{name}", {
                        'id': inv_id,
                        'name': name,
                        'description': description
                    })

        except Exception as e:
            print(f"Error loading invocations: {e}")

        self.invocation_combo.currentIndexChanged.connect(self._on_invocation_selected)
        invocation_layout.addWidget(self.invocation_combo)

        self.invocation_description = QTextEdit()
        self.invocation_description.setReadOnly(True)
        self.invocation_description.setMaximumHeight(80)
        self.invocation_description.setPlaceholderText("Select an invocation to see its description...")
        invocation_layout.addWidget(self.invocation_description)

        self.class_features_layout.addWidget(invocation_group)

    def _on_invocation_selected(self):
        """Handle Eldritch Invocation selection change."""
        invocation_data = self.invocation_combo.currentData()
        if invocation_data:
            self.invocation_description.setText(invocation_data.get('description', ''))
            self.character_creation_data['warlock_invocation'] = invocation_data
        else:
            self.invocation_description.clear()
            if 'warlock_invocation' in self.character_creation_data:
                del self.character_creation_data['warlock_invocation']

    def _get_character_proficient_skills(self):
        """Get list of skills the character is proficient in from their selections."""
        proficient_skills = []

        # Get selected class skills
        if hasattr(self, 'class_skill_checkboxes'):
            class_skills = []
            for skill, checkbox in self.class_skill_checkboxes.items():
                if checkbox.isChecked():
                    class_skills.append(skill)
                    proficient_skills.append(skill)

        # Get background skills (from character creation data)
        background_data = self.character_creation_data.get('background')
        if background_data and isinstance(background_data, dict):
            bg_skills = background_data.get('skill_proficiencies', [])
            if isinstance(bg_skills, list):
                proficient_skills.extend(bg_skills)
            elif isinstance(bg_skills, str):
                try:
                    import json
                    bg_skills_list = json.loads(bg_skills)
                    proficient_skills.extend(bg_skills_list)
                except:
                    pass

        # Get species skills
        species_data = self.character_creation_data.get('species')
        if species_data and isinstance(species_data, dict):
            species_skills = species_data.get('skill_proficiencies', [])
            if isinstance(species_skills, list):
                proficient_skills.extend(species_skills)

        # Remove duplicates and return
        final_skills = list(set(proficient_skills))
        return final_skills

    def _on_expertise_skill_toggled(self, skill_name: str, checked: bool):
        """Handle expertise skill checkbox toggle with selection limit."""
        # Count currently selected expertise skills
        selected_count = sum(1 for cb in self.expertise_checkboxes.values() if cb.isChecked())

        # Update count label
        if hasattr(self, 'expertise_count_label'):
            self.expertise_count_label.setText(f"Selected: {selected_count} / 2")

            # Change color based on selection status
            if selected_count == 2:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #28a745;")  # green
            elif selected_count > 2:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #dc3545;")  # red
            else:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")  # blue

        # Enforce selection limit
        if selected_count > 2:
            # Find and uncheck the checkbox that was just checked
            if checked:  # This was the checkbox that put us over the limit
                checkbox = self.expertise_checkboxes[skill_name]
                checkbox.setChecked(False)
                selected_count = 2  # Reset count
                if hasattr(self, 'expertise_count_label'):
                    self.expertise_count_label.setText(f"Selected: {selected_count} / 2")
                    self.expertise_count_label.setStyleSheet("font-weight: bold; color: #28a745;")

        # Store expertise selections in character creation data
        if not hasattr(self, 'character_creation_data'):
            self.character_creation_data = {}
        if 'rogue_features' not in self.character_creation_data:
            self.character_creation_data['rogue_features'] = {}

        expertise_skills = [skill for skill, cb in self.expertise_checkboxes.items() if cb.isChecked()]
        self.character_creation_data['rogue_features']['expertise_skills'] = expertise_skills

    def _refresh_expertise_options(self):
        """Refresh the expertise selection options when skills change."""
        # Get updated list of proficient skills
        proficient_skills = self._get_character_proficient_skills()

        # Find the expertise group box
        expertise_group = None
        for i in range(self.class_features_layout.count()):
            widget = self.class_features_layout.itemAt(i).widget()
            if widget and isinstance(widget, QGroupBox) and "Expertise" in widget.title():
                expertise_group = widget
                break

        if not expertise_group:
            return

        expertise_layout = expertise_group.layout()
        if not expertise_layout:
            return

        # Clear existing content after the description
        # Keep the description (index 0), remove everything else
        for i in reversed(range(1, expertise_layout.count())):
            child = expertise_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Clear any existing checkboxes
        if hasattr(self, 'expertise_checkboxes'):
            self.expertise_checkboxes.clear()
        else:
            self.expertise_checkboxes = {}

        # If no proficient skills, show placeholder message
        if not proficient_skills:
            no_skills_label = QLabel("Select your class skills above, then expertise choices will appear here.")
            no_skills_label.setStyleSheet("color: #ffa500; font-style: italic;")
            expertise_layout.addWidget(no_skills_label)
            return

        # Create skill selection interface
        expertise_skills_frame = QFrame()
        expertise_skills_layout = QGridLayout(expertise_skills_frame)

        row, col = 0, 0
        for skill in proficient_skills:
            checkbox = QCheckBox(skill)
            checkbox.toggled.connect(
                lambda state, s=skill: self._on_expertise_skill_toggled(s, state)
            )
            self.expertise_checkboxes[skill] = checkbox
            expertise_skills_layout.addWidget(checkbox, row, col)

            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1

        expertise_layout.addWidget(expertise_skills_frame)

        # Add selection count label
        self.expertise_count_label = QLabel("Selected: 0 / 2")
        self.expertise_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        expertise_layout.addWidget(self.expertise_count_label)


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
        skill_layout.setContentsMargins(5, 5, 5, 5)
        skill_layout.setSpacing(1)

        # Create checkboxes for available skills
        self.class_skill_checkboxes = {}
        skill_grid_layout = QGridLayout()
        skill_grid_layout.setSpacing(1)
        
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

        # Refresh expertise options for Rogue if applicable
        selected_class_data = self.character_creation_data.get('class')
        if selected_class_data:
            class_name = selected_class_data.get('name', '') if isinstance(selected_class_data, dict) else str(selected_class_data)
            if class_name == "Rogue":
                self._refresh_expertise_options()

    def _setup_spell_selection(self, class_name: str):
        spellcasting_classes = ['Wizard', 'Cleric', 'Warlock', 'Paladin']

        if class_name not in spellcasting_classes:
            return

        spell_widget = SpellSelectionWidget()
        spell_widget.setup_for_class(class_name)
        spell_widget.spells_changed.connect(self._on_spells_changed)

        self.spell_selection_widget = spell_widget
        self.class_features_layout.addWidget(spell_widget)

    def _on_spells_changed(self):
        if hasattr(self, 'spell_selection_widget'):
            self.character_creation_data['selected_cantrips'] = self.spell_selection_widget.get_selected_cantrips()
            self.character_creation_data['selected_spells'] = self.spell_selection_widget.get_selected_spells()

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

            allowed = None
            if getattr(self, 'campaign_frame', None):
                allowed = {c.lower() for c in self.campaign_frame.available_classes}

            for class_row in classes_data:
                name = class_row['name']
                if allowed and name.lower() not in allowed:
                    continue
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

            # Parse skills from the database format
            import json
            skill_proficiencies = []
            tool_proficiencies = []
            language_proficiencies = []

            # Try to get skill proficiencies from database
            try:
                import sqlite3
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()

                # Get unique skills (using DISTINCT to avoid duplicates)
                cursor.execute("""SELECT DISTINCT proficiency_name FROM background_proficiencies
                                WHERE background_id = ? AND proficiency_type = 'skill'
                                ORDER BY proficiency_name""", (bg['name'].lower(),))
                skills = cursor.fetchall()
                skill_proficiencies = [skill[0] for skill in skills]

                # Get unique tools (using DISTINCT to avoid duplicates)
                cursor.execute("""SELECT DISTINCT proficiency_name FROM background_proficiencies
                                WHERE background_id = ? AND proficiency_type = 'tool'
                                ORDER BY proficiency_name""", (bg['name'].lower(),))
                tools = cursor.fetchall()
                tool_proficiencies = [tool[0].replace('_', ' ').title() for tool in tools]

                # Get languages if any
                cursor.execute("""SELECT DISTINCT proficiency_name FROM background_proficiencies
                                WHERE background_id = ? AND proficiency_type = 'language'
                                ORDER BY proficiency_name""", (bg['name'].lower(),))
                languages = cursor.fetchall()
                for lang in languages:
                    if 'choice' in lang[0].lower():
                        # Handle language choices
                        num = lang[0].split('_')[-1] if '_' in lang[0] else '1'
                        language_proficiencies.append(f"Any {num} language(s)")
                    else:
                        language_proficiencies.append(lang[0])

                conn.close()
            except Exception as e:
                print(f"Error loading background proficiencies: {e}")
                # Fallback to parsing from the stored JSON if database query fails
                try:
                    if bg.get('skill_proficiencies'):
                        skill_proficiencies = json.loads(bg['skill_proficiencies']) if isinstance(bg['skill_proficiencies'], str) else bg['skill_proficiencies']
                    if bg.get('tool_proficiencies'):
                        tool_proficiencies = json.loads(bg['tool_proficiencies']) if isinstance(bg['tool_proficiencies'], str) else bg['tool_proficiencies']
                except:
                    pass

            # Build the description with HTML formatting
            description += f"<u><b>Background: {bg['name']}</b></u><br>"

            if skill_proficiencies:
                description += f"<b>Skill Proficiencies:</b> {', '.join(skill_proficiencies)}<br>"

            if tool_proficiencies:
                description += f"<b>Tool Proficiencies:</b> {', '.join(tool_proficiencies)}<br>"

            if language_proficiencies:
                description += f"<b>Languages:</b> {', '.join(language_proficiencies)}<br>"

            if bg.get('feat'):
                description += f"<b>Origin Feat:</b> {bg['feat']}<br>"

            description += "<br>"

        if 'species' in self.character_creation_data:
            species = self.character_creation_data['species']
            description += f"<u><b>Species: {species['name']}</b></u><br>"

            # Add size and speed
            if species.get('size'):
                description += f"<b>Size:</b> {species['size']}<br>"
            if species.get('speed'):
                description += f"<b>Speed:</b> {species['speed']} feet<br>"

            # Add languages
            if species.get('languages'):
                languages = species['languages']
                if isinstance(languages, str):
                    import json
                    try:
                        languages = json.loads(languages)
                    except:
                        languages = [languages]
                if languages:
                    description += f"<b>Languages:</b> {', '.join(languages)}<br>"

            # Add traits
            if species.get('traits'):
                traits = species['traits']
                if isinstance(traits, str):
                    import json
                    try:
                        traits = json.loads(traits)
                    except:
                        traits = {}

                if traits:
                    description += "<b>Traits:</b><br>"
                    for trait_name, trait_desc in traits.items():
                        # Format trait names (convert from snake_case to Title Case)
                        formatted_name = trait_name.replace('_', ' ').title()
                        description += f"• <b>{formatted_name}:</b> {trait_desc}<br>"

        self.bg_species_description.setHtml(description)
    
    def _auto_select_background_feat(self, bg_data):
        """Auto-select the default feat for the chosen background."""
        # Map backgrounds to their default feats from 2024 SRD
        default_feats = {
            "Acolyte": "Magic Initiate; Cleric",
            "Criminal": "Alert",
            "Sage": "Magic Initiate; Wizard",
            "Soldier": "Savage Attacker",
            "Farmer": "Tough",
            "Scribe": "Skilled",
            "Entertainer": "Musician"
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
            'selected_species_skills': self.character_creation_data.get('selected_species_skills', []),
            'rogue_features': self.character_creation_data.get('rogue_features', {}),
            'warlock_invocation': self.character_creation_data.get('warlock_invocation'),
            'selected_cantrips': self.character_creation_data.get('selected_cantrips', []),
            'selected_spells': self.character_creation_data.get('selected_spells', [])
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
    
    def _set_campaign_file(self, filename: str):
        """Set the campaign file to load."""
        self.campaign_file = filename

    def _load_campaign_frame(self):
        """Load campaign frame from specified file and initialize encounter generator."""
        try:
            # Use specified campaign file or default to golden
            campaign_name = getattr(self, 'campaign_file', 'golden.json').replace('.json', '')
            campaign_path = os.path.join(os.path.dirname(__file__), 'campaign', getattr(self, 'campaign_file', 'golden.json'))
            print(f"[DEBUG] Looking for campaign at: {campaign_path}")
            print(f"[DEBUG] __file__ is: {__file__}")
            print(f"[DEBUG] dirname(__file__) is: {os.path.dirname(__file__)}")

            # Fall back to conan if golden doesn't exist
            if not os.path.exists(campaign_path):
                print(f"[DEBUG] Golden campaign not found, falling back to conan")
                campaign_path = os.path.join(os.path.dirname(__file__), 'campaign', 'conan.json')

            print(f"[DEBUG] Loading campaign from: {campaign_path}")
            with open(campaign_path, 'r', encoding='utf-8') as f:
                frame_data = json.load(f)

            print(f"[DEBUG] Frame data loaded: {frame_data}")
            print(f"[DEBUG] Frame data name: {frame_data.get('name')}")
            print(f"[DEBUG] Frame data guaranteed_hoards: {frame_data.get('guaranteed_hoards')}")

            campaign_frame = CampaignFrame(frame_data)
            print(f"[DEBUG] CampaignFrame created successfully")
            self.campaign_frame = campaign_frame

            print(f"[DEBUG] Creating EncounterGenerator...")
            self.encounter_generator = EncounterGenerator(campaign_frame)
            print(f"[DEBUG] EncounterGenerator created successfully")

            print(f"[DEBUG] Loaded campaign: {getattr(campaign_frame, 'name', 'Unknown')}")
            print(f"[DEBUG] Guaranteed hoards: {getattr(campaign_frame, 'guaranteed_hoards', 'Not set')}")
            
        except Exception as e:
            print(f"Error loading campaign frame: {e}")
            # Fallback to Golden Age settings (since something is preventing golden.json from loading)
            default_frame_data = {
                'name': 'Golden Age (Fallback)',
                'monster_type_weights': {
                    'humanoid': 0.25, 'beast': 0.20, 'monstrosity': 0.15,
                    'fiend': 0.15, 'undead': 0.10, 'dragon': 0.08,
                    'aberration': 0.05, 'celestial': 0.02
                },
                'difficulty_distribution': {'low': 0.4, 'moderate': 0.5, 'high': 0.1},
                'rest_rules': {'short_rest_duration': 1, 'long_rest_duration': 8},
                'style': 'golden',
                'available_classes': ["Barbarian", "Fighter", "Rogue", "Paladin", "Cleric", "Warlock", "Wizard"],
                'guaranteed_hoards': True
            }
            campaign_frame = CampaignFrame(default_frame_data)
            self.campaign_frame = campaign_frame
            self.encounter_generator = EncounterGenerator(campaign_frame)
    
    def _generate_selected_encounter(self):
        """Generate encounter based on selected type."""
        # Remove any existing vendor widget
        if self.vendor_widget:
            self.vendor_widget.setParent(None)
            self.vendor_widget.deleteLater()
            self.vendor_widget = None

        if hasattr(self, 'trap_card_frame'):
            self._clear_trap_cards()
            self.trap_card_frame.setVisible(False)

        encounter_type = self.encounter_type_combo.currentText()
        random_selection = None
        if encounter_type == "Random":
            random_selection = random.choice(self._random_encounter_topics)
            encounter_type = random_selection

        if encounter_type == "Monsters":
            self._generate_monster_encounter()
        elif encounter_type == "Traps":
            self._generate_trap_encounter()
        elif encounter_type == "Hazards":
            self._generate_hazard_encounter()
        elif encounter_type == "Skill Challenge":
            self._generate_skill_challenge()
        elif encounter_type == "Vendors":
            self._generate_vendor_encounter()

        if random_selection:
            current_text = self.encounter_details_text.toPlainText().strip()
            prefix = f"Random selection: {random_selection}"
            if current_text:
                self.encounter_details_text.setPlainText(f"{prefix}\n\n{current_text}")
            else:
                self.encounter_details_text.setPlainText(prefix)

    def _generate_trap_encounter(self):
        """Generate a trap encounter with automated resolution."""
        level = self._get_character_level() or 1
        trap = generate_trap(level)

        self._active_trap_state = {
            'type': trap['type'],
            'xp_awarded': False,
            'resolved': False,
            'level': level,
            'trap': trap,
        }
        self._trap_context = self._build_trap_context()

        self.encounter_details_text.clear()
        self.encounters_list.setVisible(False)
        self.monsters_frame.setVisible(False)
        self._clear_trap_cards()
        self.trap_card_frame.setVisible(True)

        if trap['type'] == 'Setback':
            card, summary = self._create_setback_trap_card(trap, level)
        else:
            card, summary = self._create_dangerous_trap_card(trap, level)
        self.trap_card_layout.addWidget(card)
        self.encounter_details_text.setPlainText(summary)


    def _clear_trap_cards(self):
        """Clear any trap cards from the layout."""
        if not hasattr(self, 'trap_card_layout'):
            return
        while self.trap_card_layout.count():
            item = self.trap_card_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        if hasattr(self, 'trap_card_frame'):
            self.trap_card_frame.setVisible(False)
        self._trap_context = {}
        self._active_trap_state = {}

    def _build_trap_context(self) -> Dict[str, Any]:
        """Build context data used when resolving traps."""
        context = {
            'character': None,
            'game_engine': None,
            'proficiency_system': None,
            'proficiencies': {},
            'inventory': [],
            'proficiency_bonus': 2,
        }

        character = self._get_current_character_data()
        game_engine = self._get_game_engine()

        if character:
            context['character'] = character
            try:
                context['proficiency_bonus'] = get_proficiency_bonus(character.get('level', 1))
            except Exception:
                context['proficiency_bonus'] = 2
        if game_engine:
            context['game_engine'] = game_engine
            proficiency_system = getattr(game_engine, 'proficiency_system', None)
            if proficiency_system and character:
                try:
                    context['proficiency_system'] = proficiency_system
                    context['proficiencies'] = proficiency_system.get_character_proficiencies(character['id'])
                except Exception:
                    context['proficiencies'] = {}
            if character:
                try:
                    context['inventory'] = game_engine.get_character_inventory_sync(character['id'])
                except Exception:
                    context['inventory'] = []
        return context

    def _ensure_trap_context(self) -> Dict[str, Any]:
        """Ensure trap context includes current game engine and character data."""
        ctx = getattr(self, '_trap_context', {})
        if not ctx or not ctx.get('character') or not ctx.get('game_engine'):
            ctx = self._build_trap_context()
            self._trap_context = ctx
        return ctx


    def _format_trap_summary(self, trap: dict, extra: Optional[str] = None) -> str:
        lines = [
            f"Trap Type: {trap['type']}",
            f"Description: {trap['description']}",
            f"DC {trap['dc']} / Attack Bonus +{trap['toHit']}",
            f"Damage: {trap['damage']}",
            f"Effects: {trap['effects']}",
            f"XP: {trap['xp']}",
        ]
        if extra:
            lines.append('')
            lines.append(extra)
        return '\n'.join(lines)

    def _create_setback_trap_card(self, trap: dict, level: int):
        from PyQt6.QtWidgets import QVBoxLayout

        card = QFrame()
        card.setObjectName("trapCard")
        card.setFixedSize(120, 140)
        card.setStyleSheet("""
            QFrame#trapCard {
                background-color: #2a2a2a;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel(f"{trap['type']} Trap")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #ffcc66;")
        layout.addWidget(title)

        description = QLabel("This setback springs without warning if unnoticed.")
        description.setWordWrap(True)
        layout.addWidget(description)

        outcome_label = QLabel()
        outcome_label.setWordWrap(True)
        layout.addWidget(outcome_label)

        result = self._resolve_setback_trap(trap, level)
        outcome_label.setText(result['result'])

        summary = self._format_trap_summary(trap, result['summary_append'])
        return card, summary

    def _resolve_setback_trap(self, trap: dict, level: int) -> Dict[str, str]:
        ctx = self._ensure_trap_context()
        skill_name, skill_bonus, has_advantage = self._determine_detection_check(ctx)

        if not skill_name:
            message = "No active character found to resolve the setback automatically."
            self._log_monster_action("[TRAP] Setback encountered but no active character loaded.")
            self._award_trap_xp(trap['xp'], trap['type'])
            treasure_note = self._maybe_award_trap_treasure('Setback', level)
            self._active_trap_state['resolved'] = True
            combined = self._combine_trap_text(message, treasure_note)
            self._log_monster_action(combined)
            return {'result': combined, 'summary_append': combined}

        roll_total, detail = self._roll_d20(skill_bonus, advantage=has_advantage)
        advantage_text = " with advantage" if has_advantage else ""
        self._log_monster_action(
            f"[TRAP] Setback detection check ({skill_name}{advantage_text}) vs DC {trap['dc']}: {detail}"
        )

        if roll_total >= trap['dc']:
            self._log_monster_action("[TRAP] You see the setback in time and avoid it.")
            treasure_note = self._maybe_award_trap_treasure('Setback', level)
            self._award_trap_xp(trap['xp'], trap['type'])
            self._active_trap_state['resolved'] = True
            outcome = "You see the setback and avoid it."
            combined = self._combine_trap_text(outcome, treasure_note)
            self._log_monster_action(combined)
            return {'result': combined, 'summary_append': combined}

        self._log_monster_action("[TRAP] The setback is triggered!")
        outcome = self._trigger_trap_effect(trap, ctx)
        treasure_note = self._maybe_award_trap_treasure('Setback', level)
        self._award_trap_xp(trap['xp'], trap['type'])
        self._active_trap_state['resolved'] = True
        combined = self._combine_trap_text(outcome, treasure_note)
        self._log_monster_action(combined)
        return {'result': combined, 'summary_append': combined}

    def _create_dangerous_trap_card(self, trap: dict, level: int):
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

        card = QFrame()
        card.setObjectName("trapCard")
        card.setFixedSize(120, 140)
        card.setStyleSheet("""
            QFrame#trapCard {
                background-color: #352a1e;
                border: 2px solid #8a5a1f;
                border-radius: 8px;
                padding: 6px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Dangerous Trap")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #ff9955;")
        layout.addWidget(title)

        warning = QLabel("You see a dangerous area - surely treasure is nearby.")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        outcome_label = QLabel("Choose whether to avoid it or take the risk.")
        outcome_label.setWordWrap(True)
        layout.addWidget(outcome_label)

        button_row = QHBoxLayout()
        avoid_btn = QPushButton("Avoid")
        risk_btn = QPushButton("Take Risk")
        button_row.addWidget(avoid_btn)
        button_row.addWidget(risk_btn)
        layout.addLayout(button_row)

        avoid_btn.clicked.connect(
            lambda: self._resolve_dangerous_trap_avoid(trap, outcome_label, (avoid_btn, risk_btn))
        )
        risk_btn.clicked.connect(
            lambda: self._resolve_dangerous_trap_take_risk(trap, level, outcome_label, (avoid_btn, risk_btn))
        )

        summary = self._format_trap_summary(trap, "Choose to avoid the trap or take the risk for rewards.")
        return card, summary

    def _resolve_dangerous_trap_avoid(self, trap: dict, output_label: QLabel, buttons: tuple):
        if getattr(self, '_active_trap_state', {}).get('resolved'):
            return
        for btn in buttons:
            btn.setEnabled(False)
        self._active_trap_state['resolved'] = True
        message = "You decide it's too risky and walk away with no reward."
        output_label.setText(message)
        self._log_monster_action("[TRAP] Dangerous trap avoided - no XP or treasure gained.")
        self.encounter_details_text.setPlainText(self._format_trap_summary(trap, message))

    def _resolve_dangerous_trap_take_risk(self, trap: dict, level: int, output_label: QLabel, buttons: tuple):
        if getattr(self, '_active_trap_state', {}).get('resolved'):
            return
        for btn in buttons:
            btn.setEnabled(False)

        ctx = self._ensure_trap_context()
        skill_name, skill_bonus, has_advantage = self._determine_detection_check(ctx)
        if not skill_name:
            message = "No active character found to resolve the trap."
            output_label.setText(message)
            self._log_monster_action("[TRAP] Dangerous trap encountered but no character loaded.")
            treasure_note = self._maybe_award_trap_treasure('Dangerous', level)
            self._award_trap_xp(trap['xp'], trap['type'])
            self._active_trap_state['resolved'] = True
            combined = self._combine_trap_text(message, treasure_note)
            self.encounter_details_text.setPlainText(self._format_trap_summary(trap, combined))
            self._log_monster_action(combined)
            return

        roll_total, detail = self._roll_d20(skill_bonus, advantage=has_advantage)
        advantage_text = " with advantage" if has_advantage else ""
        self._log_monster_action(
            f"[TRAP] Dangerous trap survey ({skill_name}{advantage_text}) vs DC {trap['dc']}: {detail}"
        )

        outcome_parts = []
        if roll_total >= trap['dc']:
            self._log_monster_action("[TRAP] You identify the trap's mechanism and attempt to disarm it.")
            disarm_result = self._attempt_dangerous_trap_disarm(trap, ctx)
            outcome_parts.append(disarm_result['result'])
            if disarm_result['triggered']:
                outcome_parts.append(self._trigger_trap_effect(trap, ctx))
        else:
            self._log_monster_action("[TRAP] You blunder into the mechanism while studying it!")
            outcome_parts.append(self._trigger_trap_effect(trap, ctx))

        treasure_note = self._maybe_award_trap_treasure('Dangerous', level)
        outcome_parts.append(treasure_note)
        self._award_trap_xp(trap['xp'], trap['type'])
        self._active_trap_state['resolved'] = True

        combined = self._combine_trap_text(*outcome_parts)
        output_label.setText(combined)
        self.encounter_details_text.setPlainText(self._format_trap_summary(trap, combined))
        self._log_monster_action(combined)

    def _attempt_dangerous_trap_disarm(self, trap: dict, ctx: Dict[str, Any]) -> Dict[str, Any]:
        character = ctx.get('character')
        if not character:
            return {
                'result': 'No character available to disarm the trap.',
                'triggered': True,
            }

        profs = ctx.get('proficiencies', {})
        skill_profs = [p.lower() for p in profs.get('skill', [])]
        tool_profs = [p.lower().replace("'", "").replace(' ', '_') for p in profs.get('tool', [])]
        tool_bonus = character.get('dexterity_modifier', 0)
        if 'thieves_tools' in tool_profs:
            tool_bonus += ctx.get('proficiency_bonus', 2)
        investigation_bonus = self._get_skill_bonus(ctx, 'Investigation')
        perception_bonus = self._get_skill_bonus(ctx, 'Perception')

        has_tools_equipped = self._has_thieves_tools_equipped(ctx)
        has_investigation_prof = 'investigation' in skill_profs
        has_sleight_of_hand_prof = 'sleight of hand' in skill_profs or 'sleight_of_hand' in skill_profs
        tool_proficient = 'thieves_tools' in tool_profs

        # Advantage if tools equipped AND proficient in either Investigation or Sleight of Hand
        advantage = has_tools_equipped and tool_proficient and (has_investigation_prof or has_sleight_of_hand_prof)

        options = [
            ("Thieves' Tools", tool_bonus, advantage),
            ('Investigation', investigation_bonus, False),
            ('Perception', perception_bonus, False),
        ]

        best_option = options[0]
        for option in options[1:]:
            if option[1] > best_option[1]:
                best_option = option

        roll_total, detail = self._roll_d20(best_option[1], advantage=best_option[2])
        self._log_monster_action(
            f"[TRAP] Disarm attempt with {best_option[0]} vs DC {trap['dc']}: {detail}"
        )

        if roll_total >= trap['dc']:
            self._log_monster_action("[TRAP] You disable the trap and expose its cache.")
            return {
                'result': 'You carefully disarm the trap and keep the treasure safe.',
                'triggered': False,
            }

        self._log_monster_action("[TRAP] The disarm attempt fails!")
        return {
            'result': 'The mechanism slips while you work!',
            'triggered': True,
        }

    def _determine_detection_check(self, ctx: Dict[str, Any]) -> tuple:
        """Determine the best skill check for trap detection, with potential advantage."""
        options = []

        # Check for equipped thieves tools and proficiencies
        has_tools_equipped = self._has_thieves_tools_equipped(ctx)
        profs = ctx.get('proficiencies', {})
        skill_profs = [p.lower() for p in profs.get('skill', [])]
        has_investigation_prof = 'investigation' in skill_profs
        has_sleight_of_hand_prof = 'sleight of hand' in skill_profs or 'sleight_of_hand' in skill_profs

        # Check each detection skill
        for skill in ('Investigation', 'Perception'):
            bonus = self._get_skill_bonus(ctx, skill)

            # Check if this skill gets advantage from equipped thieves tools
            has_advantage = False
            if skill.lower() == 'investigation' and has_tools_equipped and has_investigation_prof:
                has_advantage = True

            options.append((skill, bonus, has_advantage))

        if not options:
            return None, 0, False

        # Choose best option (prioritize advantage, then highest bonus)
        best = options[0]
        for option in options[1:]:
            # Prefer option with advantage
            if option[2] and not best[2]:
                best = option
            # Or higher bonus if neither/both have advantage
            elif option[2] == best[2] and option[1] > best[1]:
                best = option

        return best[0], best[1], best[2]

    def _trigger_trap_effect(self, trap: dict, ctx: Dict[str, Any]) -> str:
        character = ctx.get('character')
        mode = random.choice(['attack', 'save'])
        if not character:
            self._log_monster_action('[TRAP] Trap triggered but no active character data available.')
            return 'The trap triggers, but character data is unavailable.'

        if mode == 'attack':
            roll_total, detail = self._roll_d20(trap['toHit'])
            armor_class = character.get('armor_class', 10)
            self._log_monster_action(
                f"[TRAP] Attack roll {detail} against AC {armor_class}"
            )
            if roll_total >= armor_class:
                damage, damage_detail = self._roll_damage_formula(trap['damage'])
                self._log_monster_action(
                    f"[TRAP] Damage {trap['damage']} -> {damage_detail} = {damage}"
                )
                self._deal_trap_damage(damage, trap['description'])
                return f'The trap strikes for {damage} damage.'
            self._log_monster_action("[TRAP] The trap misses its target.")
            return 'The trap lashes out but misses.'

        save_bonus = self._get_saving_throw_bonus_for_trap(ctx, 'dexterity')

        # Check for Danger Sense advantage
        has_advantage = self._check_danger_sense_advantage(ctx, 'dexterity')

        if has_advantage:
            # Roll with advantage (2d20, take higher)
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            d20_result = max(roll1, roll2)
            roll_total = d20_result + save_bonus
            detail = f"({roll1}, {roll2}) + {save_bonus} = {roll_total} (Danger Sense advantage)"
            self._log_monster_action("[TRAP] Rolling Dexterity save with Danger Sense advantage")
        else:
            roll_total, detail = self._roll_d20(save_bonus)

        self._log_monster_action(
            f"[TRAP] Dexterity save {detail} vs DC {trap['dc']}"
        )
        if roll_total < trap['dc']:
            damage, damage_detail = self._roll_damage_formula(trap['damage'])
            self._log_monster_action(
                f"[TRAP] Damage {trap['damage']} -> {damage_detail} = {damage}"
            )
            self._deal_trap_damage(damage, trap['description'])
            return f'You fail the save and take {damage} damage.'
        self._log_monster_action("[TRAP] You succeed on the save and dodge the worst of it.")
        return 'You twist away from the trap at the last moment.'

    def _maybe_award_trap_treasure(self, trap_type: str, level: int) -> str:
        loot_notes = []
        if trap_type == 'Setback':
            if random.random() < 0.5:
                gp_amount = self._roll_individual_treasure(level)
                if gp_amount > 0:
                    loot_notes.append(f'Individual treasure worth {gp_amount} GP.')
                    self._add_gold_to_character(gp_amount)
                    self._log_monster_action(f"[LOOT] Individual treasure worth {gp_amount} GP found at the trap.")
        elif trap_type == 'Dangerous':
            gp_amount = self._roll_individual_treasure(level)
            if gp_amount > 0:
                loot_notes.append(f'Individual treasure worth {gp_amount} GP.')
                self._add_gold_to_character(gp_amount)
                self._log_monster_action(f"[LOOT] Individual treasure worth {gp_amount} GP recovered from the trap.")
            if random.random() < 0.5:
                hoard_gp = self._roll_individual_treasure(max(1, level)) * 5
                if hoard_gp > 0:
                    loot_notes.append(f'Hoard cache worth {hoard_gp} GP.')
                    self._add_gold_to_character(hoard_gp)
                    self._log_monster_action(f"[LOOT] Hoard cache worth {hoard_gp} GP stashed in the trap's recesses.")
        return '\n'.join(loot_notes)

    def _get_skill_bonus(self, ctx: Dict[str, Any], skill_name: str) -> int:
        character = ctx.get('character')
        if not character:
            return 0
        ability_map = {
            'investigation': 'intelligence_modifier',
            'perception': 'wisdom_modifier',
        }
        ability_key = ability_map.get(skill_name.lower())
        ability_mod = character.get(ability_key, 0) if ability_key else 0
        proficiency_system = ctx.get('proficiency_system')
        if proficiency_system:
            try:
                return proficiency_system.calculate_skill_bonus(character['id'], skill_name, ability_mod)
            except Exception:
                return ability_mod
        return ability_mod

    def _get_saving_throw_bonus_for_trap(self, ctx: Dict[str, Any], ability: str) -> int:
        character = ctx.get('character')
        proficiency_system = ctx.get('proficiency_system')
        if character and proficiency_system:
            try:
                return proficiency_system.get_saving_throw_bonus(character['id'], ability)
            except Exception:
                pass
        if character:
            ability_key = f"{ability.lower()}_modifier"
            return character.get(ability_key, 0)
        return 0

    def _check_danger_sense_advantage(self, ctx: Dict[str, Any], ability: str) -> bool:
        """Check if character gets Danger Sense advantage on saving throw."""
        character = ctx.get('character')
        if not character or ability.lower() != 'dexterity':
            return False

        # Check if character is a barbarian
        if character.get('class_id', '').lower() != 'barbarian':
            return False

        try:
            from services.barbarian_abilities import BarbarianAbilitiesService
            barbarian_service = BarbarianAbilitiesService()

            # Get current conditions (simplified - could be expanded)
            conditions = []  # In future, get from character status effects

            return barbarian_service.has_danger_sense_advantage(character['id'], ability, conditions)
        except Exception:
            return False

    def _has_thieves_tools_equipped(self, ctx: Dict[str, Any]) -> bool:
        """Check if thieves tools are equipped in the belt slot."""
        character = ctx.get('character')
        if not character:
            return False

        # Check if Thieves Tools are equipped in belt slot
        belt_item = character.get('equipment_belt', '')
        if belt_item and 'thieves tools' in belt_item.lower():
            return True

        # Fallback: check inventory for backwards compatibility
        for item in ctx.get('inventory', []):
            name = item.get('name', '').lower()
            if 'thieves' in name and 'tool' in name:
                return True
        return False

    def _roll_d20(self, bonus: int, advantage: bool = False) -> tuple:
        rolls = [random.randint(1, 20)]
        if advantage:
            rolls.append(random.randint(1, 20))
            chosen = max(rolls)
        else:
            chosen = rolls[0]
        total = chosen + bonus
        detail = f"{' / '.join(str(r) for r in rolls)} + {bonus} = {total}"
        return total, detail

    def _roll_damage_formula(self, formula: str) -> tuple:
        import re
        match = re.match(r"(\d+)d(\d+)([+-]\d+)?", formula.strip())
        if not match:
            return 0, formula
        count = int(match.group(1))
        die = int(match.group(2))
        modifier = int(match.group(3) or 0)
        rolls = [random.randint(1, die) for _ in range(count)]
        total = sum(rolls) + modifier
        detail = "+".join(str(r) for r in rolls)
        if modifier:
            detail = f"{detail}{modifier:+d}"
        return max(total, 0), detail

    def _deal_trap_damage(self, amount: int, source: str):
        ctx = getattr(self, '_trap_context', {})
        character = ctx.get('character')
        game_engine = ctx.get('game_engine')
        if not character or not game_engine:
            self._log_monster_action(f"[TRAP] {source} deals {amount} damage (adjust manually).")
            return
        current_hp = character.get('hit_points_current', character.get('current_hit_points', 0))
        max_hp = character.get('hit_points_max', max(current_hp, character.get('hit_points_max', 0)))
        new_hp = max(0, current_hp - amount)
        try:
            game_engine.update_character_hp_sync(new_hp)
        except Exception as exc:
            print(f"Error updating character HP after trap damage: {exc}")
        character['hit_points_current'] = new_hp
        if 'current_hit_points' in character:
            character['current_hit_points'] = new_hp
        self._update_character_sheet_hp(new_hp, max_hp)
        self._log_monster_action(
            f"[TRAP] {character.get('name', 'Adventurer')} now has {new_hp}/{max_hp} HP."
        )

    def _award_trap_xp(self, xp_amount: int, trap_label: str):
        state = getattr(self, '_active_trap_state', {})
        if not xp_amount or state.get('xp_awarded'):
            return
        self._add_xp_to_character(xp_amount)
        self._log_monster_action(
            f"[XP] Gained {xp_amount} XP for overcoming the {trap_label.lower()} trap."
        )
        state['xp_awarded'] = True
        self._active_trap_state = state

    def _combine_trap_text(self, *parts: str) -> str:
        return '\n'.join([part for part in parts if part])
    def _generate_hazard_encounter(self):
        character_data = self._get_current_character_data()
        if not character_data:
            self.encounter_details_text.setPlainText("No active character found.")
            return

        self._cleanup_active_widgets()

        character_level = character_data.get('level', 1)
        hazard = generate_hazard(character_level)

        if not hazard:
            self.encounter_details_text.setPlainText("No hazards available for this level.")
            return

        self.hazard_widget = HazardWidget()
        self.hazard_widget.set_character_data(character_data)

        self.hazard_widget.hazard_completed.connect(self._on_hazard_completed)

        self.hazard_widget.start_hazard(hazard)

        self.encounters_list.setVisible(False)
        self.monsters_frame.setVisible(False)
        self.encounter_details_text.setVisible(False)

        self.encounters_layout.addWidget(self.hazard_widget)

    def _generate_skill_challenge(self):
        """Generate an interactive skill challenge."""
        character_data = self._get_current_character_data()
        if not character_data:
            self.encounter_details_text.setPlainText("No active character found.")
            return

        # Clean up any existing widgets
        self._cleanup_active_widgets()

        # Get available challenge templates
        templates = self.skill_challenge_manager.get_all_templates()
        if not templates:
            self.encounter_details_text.setPlainText("No skill challenges available.")
            return

        # Select a random challenge template
        template = random.choice(templates)

        # Create skill challenge widget
        self.skill_challenge_widget = SkillChallengeWidget()
        self.skill_challenge_widget.set_character_data(character_data)

        # Connect signals
        self.skill_challenge_widget.challenge_completed.connect(self._on_skill_challenge_completed)
        self.skill_challenge_widget.challenge_refused.connect(self._on_skill_challenge_refused)

        # Start the challenge
        self.skill_challenge_widget.start_challenge(template)

        # Hide other UI elements and show skill challenge
        self.encounters_list.setVisible(False)
        self.monsters_frame.setVisible(False)
        self.encounter_details_text.setVisible(False)

        # Add skill challenge widget to layout
        self.encounters_layout.addWidget(self.skill_challenge_widget)

    def _generate_vendor_encounter(self):
        character_data = self._get_current_character_data()
        if not character_data:
            self.encounter_details_text.setPlainText("No active character found.")
            return
        self.encounter_details_text.setPlainText("A travelling vendor offers goods.")
        self.encounters_list.setVisible(False)
        self.monsters_frame.setVisible(False)
        self.vendor_widget = ShopInterface(character_data, self)
        self.encounters_layout.addWidget(self.vendor_widget)

    def _generate_monster_encounter(self):
        """Generate a random monster encounter based on active character level."""
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
            self._loot_already_collected = False  # Reset loot collection flag
            
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
            self.monsters_frame.setVisible(True)
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
            
            # Check for stealth before switching to encounter mode
            self._check_encounter_stealth(encounter_data['monsters'])

            # Switch to encounter mode
            self.set_encounter_mode()
            
        except Exception as e:
            print(f"Error generating encounter: {e}")
            import traceback
            traceback.print_exc()

    def _check_encounter_stealth(self, monsters: List[Dict[str, Any]]) -> None:
        """Check if player can start encounter hidden."""
        try:
            # Check if stealth service is available
            if not self.stealth_service:
                self.player_hidden = False
                return
            # Get current character data
            character_data = self._get_current_character_data()
            if not character_data:
                self.player_hidden = False
                return

            character_id = character_data.get('id')
            if not character_id:
                self.player_hidden = False
                return

            # Perform stealth check
            stealth_result = self.stealth_service.check_encounter_stealth(
                character_id, character_data, monsters
            )

            # Store hidden state
            self.player_hidden = stealth_result['hidden']
            if self.player_hidden:
                self.stealth_dc = stealth_result['stealth_result']['dc_to_spot']
                # Log detailed stealth success
                stealth_info = stealth_result['stealth_result']
                breakdown = stealth_info['breakdown']
                self._log_monster_action(f"[STEALTH] Stealth Check: d20({breakdown['base_roll']}) +{breakdown['dex_modifier']} DEX +{breakdown['proficiency_bonus']} Prof = {stealth_info['total']} vs DC 15")
                self._log_monster_action(f"[STEALTH] SUCCESS! You are hidden (Stealth DC: {self.stealth_dc})")
                if breakdown['sources']:
                    sources_text = ', '.join(breakdown['sources'])
                    self._log_monster_action(f"[STEALTH] Modifiers: {sources_text}")

                # Update scene description
                current_desc = self.scene_text.toPlainText()
                stealth_text = f"\n\n[HIDDEN] You remain undetected. You can make a surprise attack or flee."
                self.scene_text.setPlainText(current_desc + stealth_text)

                # Show special action buttons for hidden state
                self._show_hidden_action_buttons()

                # Show hidden status indicator
                self._update_hidden_status_ui()
            else:
                # Log why stealth failed with details
                reason = stealth_result.get('reason', 'unknown')
                if reason == 'no_proficiency':
                    self._log_monster_action("[STEALTH] You lack Stealth proficiency - encounter begins normally.")
                elif reason == 'failed_stealth':
                    stealth_info = stealth_result.get('stealth_result', {})
                    breakdown = stealth_info.get('breakdown', {})
                    total = stealth_info.get('total', 0)
                    self._log_monster_action(f"[STEALTH] Stealth Check: d20({breakdown.get('base_roll', '?')}) +{breakdown.get('dex_modifier', 0)} DEX +{breakdown.get('proficiency_bonus', 0)} Prof = {total} vs DC 15")
                    self._log_monster_action(f"[STEALTH] FAILED! Not hidden (needed 15+)")
                elif reason == 'spotted_by_monster':
                    # First log the successful stealth roll
                    stealth_info = stealth_result.get('stealth_result', {})
                    breakdown = stealth_info.get('breakdown', {})
                    total = stealth_info.get('total', 0)
                    self._log_monster_action(f"[STEALTH] Stealth Check: d20({breakdown.get('base_roll', '?')}) +{breakdown.get('dex_modifier', 0)} DEX +{breakdown.get('proficiency_bonus', 0)} Prof = {total} vs DC 15")
                    self._log_monster_action(f"[STEALTH] Stealth successful, but spotted by monsters...")

                    # Then log monster perception results
                    for result in stealth_result.get('monster_results', []):
                        monster_name = result['monster']
                        perception_check = result['perception_check']
                        perception_total = perception_check['total']
                        spotted = perception_check['spotted']
                        self._log_monster_action(
                            f"[STEALTH] {monster_name} Perception: d20({perception_check['roll']}) +{perception_check['perception_bonus']} = {perception_total} vs DC {self.stealth_dc} - {'SPOTTED!' if spotted else 'missed'}"
                        )
                        if spotted:
                            self._log_monster_action(f"[STEALTH] DETECTED by {monster_name}! Encounter begins normally.")
                            break

        except Exception as e:
            print(f"[STEALTH] Error checking encounter stealth: {e}")
            import traceback
            traceback.print_exc()
            self.player_hidden = False

    def _show_hidden_action_buttons(self) -> None:
        """Show special action buttons when player is hidden."""
        try:
            # Add special hidden state buttons
            if hasattr(self, 'action_buttons_layout'):
                # Clear existing buttons
                while self.action_buttons_layout.count():
                    item = self.action_buttons_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # Add hidden state actions
                surprise_btn = QPushButton("Surprise Attack")
                surprise_btn.clicked.connect(self._initiate_surprise_attack)
                surprise_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4a3030;
                        color: #ff9999;
                        border: 2px solid #ff6666;
                        padding: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #5a3535;
                    }
                """)

                flee_btn = QPushButton("Flee Undetected")
                flee_btn.clicked.connect(self._flee_encounter)
                flee_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #303a4a;
                        color: #99ccff;
                        border: 2px solid #6699ff;
                        padding: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #354555;
                    }
                """)

                self.action_buttons_layout.addWidget(surprise_btn)
                self.action_buttons_layout.addWidget(flee_btn)

        except Exception as e:
            print(f"Error showing hidden action buttons: {e}")

    def _initiate_surprise_attack(self) -> None:
        """Handle surprise attack from hidden state."""
        try:
            # Mark that combat is starting with player hidden
            if hasattr(self, 'current_encounter') and self.current_encounter:
                self.current_encounter.player_hidden = True
                self.current_encounter.surprise_round = True
                self.current_encounter.stealth_dc = self.stealth_dc

            self._log_monster_action("[COMBAT] You attack from hiding! You have advantage and trigger sneak attack.")

            # Start combat with player going first
            self._init_combat_session()

            # Player automatically wins initiative when attacking from hidden
            if self.current_encounter:
                self.current_encounter.player_initiative = 99  # Guaranteed to go first

            # Emit signal that player is attacking from hidden
            self.combat_initiated.emit({
                'encounter_id': self.current_encounter_id,
                'player_hidden': True,
                'surprise_round': True
            })

        except Exception as e:
            print(f"Error initiating surprise attack: {e}")

    def _flee_encounter(self) -> None:
        """Handle fleeing from encounter while hidden."""
        try:
            self._log_monster_action("[ENCOUNTER] You slip away unnoticed, avoiding the encounter entirely.")

            # Clear encounter
            self._clear_monster_cards()
            self.encounter_instances = {}
            self.selected_monster_id = None
            self.current_encounter = None
            self.player_hidden = False
            self.stealth_dc = 0

            # Return to exploration mode
            self.set_exploration_mode()
            self.update_scene_description("You successfully evaded the encounter and continue exploring.")

            # Hide the hidden status indicator
            if hasattr(self, 'hidden_status_frame'):
                self.hidden_status_frame.hide()

        except Exception as e:
            print(f"Error fleeing encounter: {e}")

    def _get_current_character_data(self) -> Optional[Dict[str, Any]]:
        """Get full character data for current character."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and hasattr(parent.game_engine, 'current_character'):
                    return parent.game_engine.current_character
                parent = parent.parent()
            return None
        except Exception as e:
            print(f"Error getting character data: {e}")
            return None

    def _update_hidden_status_ui(self) -> None:
        """Update the UI to show hidden status."""
        if hasattr(self, 'hidden_status_frame') and hasattr(self, 'hidden_status_label'):
            if self.player_hidden:
                self.hidden_status_label.setText(f"[HIDDEN] You are undetected (Stealth DC: {self.stealth_dc})")
                self.hidden_status_frame.show()
            else:
                self.hidden_status_frame.hide()
    
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
        
        # Enable mouse tracking for hover events
        card.setMouseTracking(True)
        
        # Add defensive halo for Lucky/Inspiration usage
        from ui.advantage_halo import AdvantageHalo, AdvantageResourceManager
        defensive_halo = AdvantageHalo(card)
        defensive_halo.hide()
        defensive_halo.resource_used.connect(
            lambda resource_type, monster_id=instance.id: self._use_defensive_resource(resource_type, monster_id)
        )
        card.defensive_halo = defensive_halo
        
        # Add click handler for selection (use default argument to capture instance.id)
        card.mousePressEvent = lambda event, iid=instance.id: self._select_monster_card(iid)
        
        # Add hover handlers for defensive halo
        original_enter_event = card.enterEvent
        original_leave_event = card.leaveEvent
        
        def monster_enter_event(event):
            self._show_defensive_halo(card)
            if original_enter_event:
                original_enter_event(event)
        
        def monster_leave_event(event):
            if hasattr(card, 'defensive_halo'):
                card.defensive_halo.hide()
            if original_leave_event:
                original_leave_event(event)
        
        card.enterEvent = monster_enter_event
        card.leaveEvent = monster_leave_event
        
        return card
    
    def _show_defensive_halo(self, monster_card):
        """Show defensive halo when hovering over monster card."""
        if not hasattr(monster_card, 'defensive_halo'):
            return
            
        # Get character resources from action panel if available
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'action_panel') and hasattr(parent.action_panel, 'resource_manager'):
                    resource_manager = parent.action_panel.resource_manager
                    if resource_manager and resource_manager.has_resources():
                        counts = resource_manager.get_resource_counts()
                        monster_card.defensive_halo.update_resources(
                            counts['lucky_current'],
                            counts['lucky_max'],
                            counts['inspiration_current'], 
                            counts['inspiration_max']
                        )
                        # Position halo in top-right of monster card
                        halo_x = monster_card.width() - 30
                        halo_y = -10
                        monster_card.defensive_halo.move(halo_x, halo_y)
                        monster_card.defensive_halo.raise_()
                        monster_card.defensive_halo.show_with_timeout(3000)  # Auto-hide after 3 seconds
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"[DEBUG] Error showing defensive halo: {e}")
    
    def _use_defensive_resource(self, resource_type: str, monster_id: str):
        """Handle defensive resource usage (imposing disadvantage on monster attacks)."""
        try:
            # Get resource manager from action panel
            parent = self.parent()
            while parent:
                if hasattr(parent, 'action_panel') and hasattr(parent.action_panel, 'resource_manager'):
                    resource_manager = parent.action_panel.resource_manager
                    if resource_manager and resource_manager.consume_resource(resource_type):
                        # Set defensive flag in action panel
                        if resource_type == 'inspiration':
                            parent.action_panel.inspiration_defensive_active = True
                            resource_name = "Inspiration"
                        elif resource_type == 'lucky':
                            parent.action_panel.lucky_defensive_active = True
                            resource_name = "Lucky"
                        
                        # Log the defensive action
                        if hasattr(parent, 'log_panel'):
                            monster_name = "Unknown"
                            if monster_id in self.encounter_instances:
                                monster_name = self.encounter_instances[monster_id].monster_name
                            parent.log_panel.log_combat(f"🛡️ Used {resource_name} defensively: Next attack from {monster_name} has disadvantage")
                        
                        # Hide all defensive halos after use and update resource display
                        for card_widget in self.findChildren(QFrame):
                            if hasattr(card_widget, 'defensive_halo'):
                                card_widget.defensive_halo.hide()
                        
                        # Update all action card halos to reflect resource consumption
                        if hasattr(parent, 'action_panel'):
                            for card in parent.action_panel.action_cards.values():
                                if hasattr(card, '_update_advantage_halo'):
                                    card._update_advantage_halo()
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"[DEBUG] Error using defensive resource: {e}")
    
    
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

            self.monsters_frame.setVisible(False)
                
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
            
            # Check if encounter is complete (all monsters actually defeated, not just by count)
            # Use actual living monsters check instead of counter to avoid premature loot drops
            if self.current_encounter and len(self.get_living_monsters()) == 0:
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
                    parent.log_panel.log_combat(f"[XP] Gained {xp_value} XP for defeating {monster_name}")
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

    def _calculate_skill_challenge_xp(self, character_level: int, success: bool = True) -> int:
        """Calculate XP reward for skill challenge based on character level."""
        # Base XP values for low difficulty encounters by level tier
        if character_level <= 4:
            base_xp = 50   # Levels 1-4
        elif character_level <= 10:
            base_xp = 100  # Levels 5-10
        elif character_level <= 16:
            base_xp = 150  # Levels 11-16
        else:
            base_xp = 200  # Levels 17-20

        # Full XP for success, half XP for failure
        return base_xp if success else base_xp // 2

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
    
    def _set_action_card_click_handler(self, card: QWidget, handler) -> None:
        """Make the entire action card clickable by wiring a mouse release handler."""
        from PyQt6.QtCore import Qt

        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        def _on_mouse_release(event):
            if event.button() == Qt.MouseButton.LeftButton:
                handler()
            event.accept()

        card.mouseReleaseEvent = _on_mouse_release  # type: ignore[attr-defined]

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
        title = QLabel("Loot")
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
        print(f"[DEBUG] _handle_loot_action called")

        # Prevent multiple loot calls
        if hasattr(self, '_loot_already_collected') and self._loot_already_collected:
            self._log_monster_action("Loot has already been collected for this encounter.")
            return

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
            self._log_monster_action(f"[LOOT] Individual Treasure: {total_individual_gp} GP total")
            for detail in treasure_details:
                self._log_monster_action(f"  └─ {detail}")
        
        # Check for encounter hoard based on difficulty
        hoard_gp = 0
        if hasattr(self, 'current_encounter') and self.current_encounter:
            difficulty = self.current_encounter.difficulty if hasattr(self.current_encounter, 'difficulty') else 'moderate'
            print(f"[DEBUG] Checking for hoard with difficulty: {difficulty}")
            print(f"[DEBUG] Campaign guaranteed hoards: {getattr(self.campaign_frame, 'guaranteed_hoards', False) if hasattr(self, 'campaign_frame') else 'No campaign frame'}")
            hoard_treasure = self._check_for_hoard(difficulty)
            print(f"[DEBUG] Hoard result: {hoard_treasure}")
            if hoard_treasure:
                self._log_monster_action(f"🏆 HOARD FOUND! {hoard_treasure}")
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
            print(f"[LOOT] Adding {len(all_item_drops)} items to inventory")
            self._add_items_to_character(all_item_drops)
            item_summary = ', '.join([f"{item['name']}" for item in all_item_drops])
            self._log_monster_action(f"🎒 Items Found: {item_summary}")
            print(f"[LOOT] Logged items to combat log: {item_summary}")

        # Mark loot as collected
        self._loot_already_collected = True
    
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
        """Roll for equipment drops based on monster CR using BiS system."""
        import random
        from services.loot_drop_service import LootDropService

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
        drop_chance = min(0.3 + (cr_numeric * 0.05), 0.85)

        if random.random() > drop_chance:
            return []

        try:
            character_id = self._get_current_character_id()
            if not character_id:
                return []

            character_data = self._get_current_character_data()
            if not character_data:
                return []

            loot_service = LootDropService('talekeeper.db')

            rarity = loot_service.cr_to_rarity(cr_numeric)
            print(f"[LOOT] BiS System: CR {cr_numeric} -> {rarity} rarity")

            num_items = 1 if random.random() < 0.8 else 2

            drops = []
            dropped_item_names = set()

            for _ in range(num_items):
                item = loot_service.drop_loot(character_id, character_data, rarity)

                if item and item['name'] not in dropped_item_names:
                    drops.append(item.copy())
                    dropped_item_names.add(item['name'])
                    print(f"[LOOT] BiS dropped: {item['name']} ({rarity})")
                elif not item:
                    print(f"[LOOT] BiS: No valid items available for {rarity}")
                    break

            return drops

        except Exception as e:
            print(f"[LOOT] Error in BiS equipment drops: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_current_character_id(self) -> str:
        """Get the current character's ID."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    character = parent.game_engine.current_character
                    if character:
                        return character.get('id', '')
                parent = parent.parent()
        except Exception as e:
            print(f"Error getting current character ID: {e}")
        return ''

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
        print(f"[LOOT] _add_items_to_character called with {len(items)} items")
        try:
            # Get game engine from parent for character update
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    print(f"[LOOT] Found character: {character['id'] if character else 'None'}")

                    if character:
                        character_id = character['id']

                        import sqlite3
                        conn = sqlite3.connect("talekeeper.db")
                        cursor = conn.cursor()

                        for item in items:
                            print(f"[LOOT] Processing item: {item['name']} ({item['item_type']})")
                            # Check if item already exists in inventory
                            cursor.execute("""
                                SELECT quantity FROM character_inventory
                                WHERE character_id = ? AND item_name = ? AND item_type = ?
                            """, (character_id, item['name'], item['item_type']))

                            existing = cursor.fetchone()
                            print(f"[LOOT] Existing check result: {existing}")

                            if existing:
                                # Update existing quantity
                                new_quantity = existing[0] + 1
                                cursor.execute("""
                                    UPDATE character_inventory
                                    SET quantity = ?
                                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                                """, (new_quantity, character_id, item['name'], item['item_type']))
                                print(f"[LOOT] Updated {item['name']} quantity to {new_quantity}")
                            else:
                                # Add new item
                                cursor.execute("""
                                    INSERT INTO character_inventory
                                    (character_id, item_name, item_type, quantity, equipped)
                                    VALUES (?, ?, ?, 1, 0)
                                """, (character_id, item['name'], item['item_type']))
                                print(f"[LOOT] Inserted new item: {item['name']}")

                        conn.commit()
                        print(f"[LOOT] Database commit completed for {len(items)} items")
                        conn.close()

                        # Force refresh inventory display
                        if hasattr(parent, '_force_reload_character'):
                            print("[LOOT] Calling _force_reload_character()")
                            parent._force_reload_character()
                        else:
                            print("[LOOT] No _force_reload_character method found")

                    else:
                        print("[LOOT] No current character found")
                    break
                else:
                    print(f"[LOOT] Parent {parent} has no game_engine")
                parent = parent.parent()

        except Exception as e:
            print(f"[LOOT] Error adding items to character: {e}")
            import traceback
            traceback.print_exc()
    
    def _check_for_hoard(self, difficulty: str) -> str:
        """Check for hoard treasure based on encounter difficulty."""
        import random

        # Check if campaign guarantees hoards
        if hasattr(self, 'campaign_frame') and hasattr(self.campaign_frame, 'guaranteed_hoards'):
            if getattr(self.campaign_frame, 'guaranteed_hoards', False):
                chance = 1.0  # 100% chance for golden campaign
            else:
                # Determine hoard chance based on difficulty
                hoard_chances = {
                    'low': 0.05,      # 5%
                    'moderate': 0.20, # 20%
                    'hard': 0.95,     # 95%
                    'high': 0.95      # Treat 'high' same as 'hard'
                }
                chance = hoard_chances.get(difficulty.lower(), 0.20)  # Default to moderate
        else:
            # Fallback for campaigns without guaranteed_hoards setting
            hoard_chances = {
                'low': 0.05,      # 5%
                'moderate': 0.20, # 20%
                'hard': 0.95,     # 95%
                'high': 0.95      # Treat 'high' same as 'hard'
            }
            chance = hoard_chances.get(difficulty.lower(), 0.20)  # Default to moderate
        
        if random.random() <= chance:
            # Get highest monster CR from current encounter to determine hoard table
            max_cr = 0
            if hasattr(self, 'current_encounter') and self.current_encounter:
                if hasattr(self.current_encounter, 'monster_instances'):
                    for instance in self.current_encounter.monster_instances:
                        try:
                            if hasattr(instance, 'monster_cr'):
                                cr_str = instance.monster_cr
                                if '/' in cr_str:
                                    numerator, denominator = cr_str.split('/')
                                    cr_numeric = float(numerator) / float(denominator)
                                else:
                                    cr_numeric = float(cr_str)
                                max_cr = max(max_cr, cr_numeric)
                        except (ValueError, TypeError, AttributeError):
                            continue
            
            # Use D&D 2024 hoard table based on CR
            print(f"[DEBUG] Max CR in encounter: {max_cr}")
            if max_cr <= 4:
                # CR 0-4: 2d4 × 100 GP and 1d4-1 magical items
                hoard_gp_dice = sum(random.randint(1, 4) for _ in range(2))
                hoard_gp = hoard_gp_dice * 100
                magic_items_roll = random.randint(1, 4) - 1

                # Golden Age campaign: guarantee at least 1 magical item for guaranteed hoards
                if hasattr(self, 'campaign_frame') and getattr(self.campaign_frame, 'guaranteed_hoards', False):
                    magic_items_roll = max(1, magic_items_roll)
                    print(f"[DEBUG] Golden Age: Ensured at least 1 magical item")
            elif max_cr <= 10:
                # CR 5-10: 8d10 × 100 GP and 1d3 magical items
                hoard_gp_dice = sum(random.randint(1, 10) for _ in range(8))
                hoard_gp = hoard_gp_dice * 100
                magic_items_roll = random.randint(1, 3)
            elif max_cr <= 16:
                # CR 11-16: 8d8 × 1,000 GP and 1d4 magical items
                hoard_gp_dice = sum(random.randint(1, 8) for _ in range(8))
                hoard_gp = hoard_gp_dice * 1000
                magic_items_roll = random.randint(1, 4)
            else:
                # CR 17+: 6d10 × 10,000 GP and 1d6 magical items
                hoard_gp_dice = sum(random.randint(1, 10) for _ in range(6))
                hoard_gp = hoard_gp_dice * 10000
                magic_items_roll = random.randint(1, 6)
            
            magic_items = max(0, magic_items_roll)  # Minimum 0 items for CR 0-4 only
            print(f"[DEBUG] Magic items to generate: {magic_items}")

            # Generate actual magical items based on rarity
            generated_items = []
            if magic_items > 0:
                print(f"[DEBUG] Generating {magic_items} magic items for CR {max_cr}")
                generated_items = self._generate_hoard_magic_items(magic_items, max_cr)
                print(f"[DEBUG] Generated items: {[item.get('name', 'Unknown') for item in generated_items]}")
            
            if generated_items:
                item_names_with_rarity = [f"{item['name']} ({item.get('rarity', 'Unknown')})" for item in generated_items]
                magic_text = f" and {len(generated_items)} magical item{'s' if len(generated_items) != 1 else ''}: {', '.join(item_names_with_rarity)}"
                
                # Add items to character inventory
                self._add_magic_items_to_character(generated_items)
            else:
                magic_text = " and no magical items"
            
            return f"A Hoard with {hoard_gp} GP{magic_text}"
        
        return None
    
    def _generate_hoard_magic_items(self, count: int, monster_cr: float) -> list:
        """Generate magical items for hoard treasure based on CR and loot plan."""
        from services.treasure_rarity import TreasureRaritySystem
        import random
        
        # Convert CR to character level equivalent for rarity system
        # CR 0-4 maps to levels 1-4, CR 5-10 to levels 5-10, etc.
        if monster_cr <= 4:
            char_level = min(4, max(1, int(monster_cr) + 1))
        elif monster_cr <= 10:
            char_level = min(10, max(5, int(monster_cr)))
        elif monster_cr <= 16:
            char_level = min(16, max(11, int(monster_cr)))
        else:
            char_level = min(20, max(17, int(monster_cr)))
        
        rarity_system = TreasureRaritySystem()
        generated_items = []
        generated_item_names = set()

        character_equipment = self._get_character_equipment()
        character_id = character_equipment.get('character_id', '')

        for _ in range(count):
            rarity = rarity_system.get_rarity_for_level(char_level)
            item = None

            priority_item = self._get_priority_item(rarity, character_equipment)

            if priority_item:
                candidate_name = priority_item['name']

                if candidate_name not in generated_item_names:
                    if not character_id:
                        item = priority_item
                    else:
                        character_has_item = self._character_has_item(candidate_name, character_id)
                        allows_duplicates = self._item_allows_duplicates(priority_item)

                        if not character_has_item or allows_duplicates:
                            item = priority_item

            if not item:
                max_attempts = 20

                for attempt in range(max_attempts):
                    fallback_item = self._get_random_item(rarity)

                    if not fallback_item:
                        break

                    candidate_name = fallback_item['name']

                    if candidate_name in generated_item_names:
                        continue

                    if not character_id:
                        item = fallback_item
                        break

                    character_has_item = self._character_has_item(candidate_name, character_id)
                    allows_duplicates = self._item_allows_duplicates(fallback_item)

                    if not character_has_item or allows_duplicates:
                        item = fallback_item
                        break

            if item:
                generated_items.append(item)
                generated_item_names.add(item['name'])

        return generated_items
    
    def _get_character_equipment(self) -> dict:
        """Get current character's equipped items and class info."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    character = parent.game_engine.current_character
                    if character:
                        # Get equipped items and class info
                        equipped_items = {}
                        
                        # Get main hand weapon
                        if character.get('main_hand_weapon'):
                            equipped_items['main_hand'] = character['main_hand_weapon']
                        
                        # Get armor
                        if character.get('armor'):
                            equipped_items['armor'] = character['armor']
                        
                        # Get shield
                        if character.get('shield'):
                            equipped_items['shield'] = character['shield']
                        
                        # Get class for proficiency checking
                        equipped_items['class'] = character.get('class', '')
                        equipped_items['character_id'] = character.get('id')
                        
                        return equipped_items
                parent = parent.parent()
        except Exception as e:
            print(f"Error getting character equipment: {e}")
        
        return {}
    
    def _check_weapon_proficiency(self, weapon_name: str, character_class: str) -> bool:
        """Check if character class is proficient with weapon type."""
        import sqlite3
        
        try:
            # Get weapon proficiencies from database
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT weapon_proficiencies
                FROM classes 
                WHERE name = ?
            """, (character_class,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return False
            
            proficiencies = [p.strip().lower() for p in result[0].split(',')]
            weapon_name_lower = weapon_name.lower()
            
            # Check specific proficiencies
            if 'all weapons' in proficiencies or 'simple weapons,martial weapons' in ','.join(proficiencies):
                return True
            
            if 'martial weapons' in proficiencies:
                martial_weapons = ['longsword', 'greatsword', 'greataxe', 'rapier', 'scimitar']
                if any(weapon in weapon_name_lower for weapon in martial_weapons):
                    return True
            
            if 'simple weapons' in proficiencies:
                simple_weapons = ['staff', 'quarterstaff', 'spear', 'dagger']
                if any(weapon in weapon_name_lower for weapon in simple_weapons):
                    return True
            
            # Check specific weapon proficiencies
            for prof in proficiencies:
                if prof in weapon_name_lower or weapon_name_lower in prof:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking weapon proficiency: {e}")
            return False
    
    def _check_item_proficiency(self, item_name: str, character_class: str) -> bool:
        """Check if character can use this magic item."""
        import sqlite3
        
        try:
            # Get item type from database
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT item_type, weapon_category
                FROM equipment 
                WHERE name = ?
            """, (item_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return True  # Default allow if item not found
            
            item_type, weapon_category = result
            
            # Check proficiency based on item type
            if item_type in ['wand', 'rod', 'holy symbol', 'focus']:
                return self._check_item_type_proficiency(item_type, character_class)
            elif item_type == 'weapon':
                return self._check_weapon_proficiency(item_name, character_class)
            else:
                # Most other items (armor, consumables, etc.) can be used by anyone
                return True
                
        except Exception as e:
            print(f"Error checking item proficiency: {e}")
            return True  # Default to allowing if error occurs
    
    def _check_item_type_proficiency(self, item_type: str, character_class: str) -> bool:
        """Check if character class is proficient with this item type."""
        import sqlite3
        
        try:
            # Get item proficiencies from database
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT item_proficiencies
                FROM classes 
                WHERE name = ?
            """, (character_class,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return False
            
            proficiencies = [p.strip().lower() for p in result[0].split(',')]
            item_type_lower = item_type.lower()
            
            return item_type_lower in proficiencies
            
        except Exception as e:
            print(f"Error checking item type proficiency: {e}")
            return False
    
    def _check_attunement_requirement(self, item_name: str, character_class: str) -> bool:
        """Check if character meets attunement requirements for magic item."""
        import sqlite3
        
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT attunement_requirement 
                FROM equipment 
                WHERE name = ? AND is_magical = 1
            """, (item_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return True  # No attunement requirement
            
            requirement = result[0].lower()
            class_lower = character_class.lower()
            
            # Check specific requirements
            if requirement == 'any':
                return True
            elif requirement == 'spellcaster':
                spellcasters = ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard']
                return class_lower in spellcasters
            elif ',' in requirement:
                # Multiple classes (e.g., "cleric,paladin")
                allowed_classes = [c.strip() for c in requirement.split(',')]
                return class_lower in allowed_classes
            else:
                # Single class requirement
                return class_lower == requirement
                
        except Exception as e:
            print(f"Error checking attunement requirement: {e}")
            return True  # Default to allowing if error occurs
    
    def _get_priority_item(self, rarity: str, character_equipment: dict) -> dict:
        """Get priority item based on current equipment and proficiency."""
        import random
        
        character_class = character_equipment.get('class', '')
        main_hand = character_equipment.get('main_hand', '')
        
        # Priority slots by rarity
        priority_slots = {
            'uncommon': {
                'weapon_upgrade': self._get_weapon_upgrade(main_hand, character_class, '+1'),
                'protection': self._get_protection_item(character_equipment, 'uncommon'),
                'armor': self._get_armor_upgrade(character_equipment, 'uncommon')
            },
            'rare': {
                'weapon_upgrade': self._get_weapon_upgrade(main_hand, character_class, '+2'),
                'protection': self._get_protection_item(character_equipment, 'rare'),
                'armor': self._get_armor_upgrade(character_equipment, 'rare')
            },
            'very rare': {
                'weapon_upgrade': self._get_weapon_upgrade(main_hand, character_class, '+3'),
                'protection': self._get_protection_item(character_equipment, 'very rare'),
                'armor': self._get_armor_upgrade(character_equipment, 'very rare')
            }
        }
        
        slots = priority_slots.get(rarity, {})
        if slots:
            # Check each priority slot
            for slot_name, item in slots.items():
                if item and not self._character_has_item(item['name'], character_equipment.get('character_id')):
                    return item
        
        return None
    
    def _get_weapon_upgrade(self, current_weapon: str, character_class: str, bonus: str) -> dict:
        """Get weapon upgrade based on current weapon."""
        if not current_weapon:
            return None
        
        weapon_name = current_weapon.lower()
        
        # Map current weapon to upgrade
        upgrade_map = {
            'longsword': f'Longsword {bonus}',
            'rapier': f'Rapier {bonus}',
            'greatsword': f'Greatsword {bonus}',
            'greataxe': f'Greataxe {bonus}',
            'scimitar': f'Scimitar {bonus}',
            'spear': f'Spear {bonus}',
            'staff': f'Staff {bonus}',
            'quarterstaff': f'Staff {bonus}'
        }
        
        for weapon, upgrade in upgrade_map.items():
            if weapon in weapon_name:
                if self._check_item_proficiency(upgrade, character_class):
                    return {'name': upgrade, 'rarity': self._get_rarity_for_bonus(bonus), 'item_type': 'weapon'}
        
        return None
    
    def _get_protection_item(self, character_equipment: dict, rarity: str) -> dict:
        """Get protection item based on character needs."""
        character_class = character_equipment.get('class', '').lower()
        
        protection_items = {
            'uncommon': ['Cloak of Protection', 'Shield +1'],
            'rare': ['Ring of Protection', 'Shield +2'],
            'very rare': ['Shield +3']
        }
        
        items = protection_items.get(rarity, [])
        if items and self._check_item_proficiency(items[0], character_class):
            return {'name': items[0], 'rarity': rarity, 'item_type': 'protection'}
        
        return None
    
    def _get_armor_upgrade(self, character_equipment: dict, rarity: str) -> dict:
        """Get armor upgrade based on current armor."""
        current_armor = character_equipment.get('armor', '')
        if not current_armor:
            return None
        
        armor_name = current_armor.lower()
        
        upgrade_map = {
            'uncommon': {
                'studded leather': 'Studded Leather +1',
                'chain mail': 'Chain Mail +1',
                'plate': 'Plate Armor +1'
            },
            'rare': {
                'studded leather': 'Studded Leather +1',
                'plate': 'Plate Armor +1'
            },
            'very rare': {
                'studded leather': 'Studded Leather +2',
                'plate': 'Plate Armor +2'
            }
        }
        
        upgrades = upgrade_map.get(rarity, {})
        for armor_type, upgrade in upgrades.items():
            if armor_type in armor_name:
                return {'name': upgrade, 'rarity': rarity, 'item_type': 'armor'}
        
        return None
    
    def _get_random_item(self, rarity: str) -> dict:
        """Get random item from remaining pool."""
        import random
        
        fallback_items = {
            'common': ['Potion of Healing', '1st Level Spell Scroll'],
            'uncommon': ['Potion of Greater Healing', '2nd Level Spell Scroll', 'Bag of Holding'],
            'rare': ['Potion of Superior Healing', '4th Level Spell Scroll', 'Ring of Spell Storing'],
            'very rare': ['Potion of Supreme Healing', '6th Level Spell Scroll'],
            'legendary': ['8th Level Spell Scroll', 'Deck of Many Things']
        }
        
        items = fallback_items.get(rarity, fallback_items['common'])
        if items:
            item_name = random.choice(items)
            return {'name': item_name, 'rarity': rarity, 'item_type': 'consumable'}
        
        return None
    
    def _get_rarity_for_bonus(self, bonus: str) -> str:
        """Get rarity based on bonus."""
        bonus_map = {'+1': 'uncommon', '+2': 'rare', '+3': 'very rare'}
        return bonus_map.get(bonus, 'common')
    
    def _character_has_item(self, item_name: str, character_id: str) -> bool:
        """Check if character already has this item."""
        import sqlite3

        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM character_inventory
                WHERE character_id = ? AND item_name = ?
            """, (character_id, item_name))

            count = cursor.fetchone()[0]
            conn.close()

            return count > 0

        except Exception as e:
            print(f"Error checking if character has item: {e}")
            return False

    def _item_allows_duplicates(self, item: dict) -> bool:
        """Check if item can drop multiple times (potions and one-handed weapons)."""
        import sqlite3
        import json

        item_name = item.get('name', '')

        if 'potion' in item_name.lower():
            return True

        item_type = item.get('item_type', '')
        if item_type != 'weapon':
            return False

        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT weapon_properties
                FROM equipment
                WHERE name = ?
            """, (item_name,))

            result = cursor.fetchone()
            conn.close()

            if not result or not result[0]:
                return False

            properties = json.loads(result[0])

            return 'two-handed' not in properties and 'Two-Handed' not in properties

        except Exception as e:
            print(f"Error checking if item allows duplicates: {e}")
            return False

    def _determine_item_type(self, item_name: str) -> str:
        """Determine the item type based on the item name."""
        name_lower = item_name.lower()
        
        # Check for specific item patterns
        if 'ring' in name_lower:
            return 'ring'
        elif 'cloak' in name_lower or 'cape' in name_lower or 'mantle' in name_lower:
            return 'cloak'
        elif 'shield' in name_lower:
            return 'shield'
        elif 'armor' in name_lower or 'mail' in name_lower or 'plate' in name_lower:
            return 'armor'
        elif 'sword' in name_lower or 'blade' in name_lower or 'dagger' in name_lower:
            return 'weapon'
        elif 'axe' in name_lower or 'hammer' in name_lower or 'mace' in name_lower:
            return 'weapon'
        elif 'bow' in name_lower or 'crossbow' in name_lower:
            return 'weapon'
        elif 'staff' in name_lower or 'wand' in name_lower or 'rod' in name_lower:
            return 'tool'
        elif 'amulet' in name_lower or 'necklace' in name_lower or 'pendant' in name_lower:
            return 'accessory'
        elif 'belt' in name_lower or 'girdle' in name_lower:
            return 'accessory'
        elif 'boots' in name_lower or 'shoes' in name_lower or 'slippers' in name_lower:
            return 'footwear'
        elif 'gloves' in name_lower or 'gauntlets' in name_lower or 'bracers' in name_lower:
            return 'gloves'
        elif 'helm' in name_lower or 'helmet' in name_lower or 'hat' in name_lower:
            return 'helmet'
        elif 'potion' in name_lower:
            return 'consumable'
        elif 'scroll' in name_lower:
            return 'consumable'
        else:
            return 'misc'
    
    def _add_magic_items_to_character(self, magic_items: list):
        """Add magical items to character inventory."""
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
                        
                        for item in magic_items:
                            # Log the item acquisition
                            print(f"[DEBUG] Adding magic item to inventory: {item}")
                            self._log_monster_action(f"[MAGIC] Found {item['name']} ({item['rarity']})")
                            
                            # Determine item type from the item name
                            item_type = self._determine_item_type(item['name'])
                            
                            # Check if item already exists in inventory
                            cursor.execute("""
                                SELECT quantity FROM character_inventory 
                                WHERE character_id = ? AND item_name = ? AND item_type = ?
                            """, (character_id, item['name'], item_type))
                            
                            existing = cursor.fetchone()
                            
                            if existing:
                                # Update existing quantity
                                new_quantity = existing[0] + 1
                                cursor.execute("""
                                    UPDATE character_inventory 
                                    SET quantity = ?
                                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                                """, (new_quantity, character_id, item['name'], item_type))
                            else:
                                # Add new item
                                cursor.execute("""
                                    INSERT INTO character_inventory 
                                    (character_id, item_name, item_type, quantity, equipped) 
                                    VALUES (?, ?, ?, 1, 0)
                                """, (character_id, item['name'], item_type))
                        
                        conn.commit()
                        conn.close()
                        
                        # Force refresh inventory display
                        if hasattr(parent, '_force_reload_character'):
                            parent._force_reload_character()
                        break
                        
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error adding magic items to character: {e}")
    
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
                                self._log_monster_action(f"[GOLD] Gained {gold_amount} gold pieces!")
                                print(f"[TREASURE] Successfully added {gold_amount} GP to character {character['id']}")
                                
                                # Refresh the equipment panel to show updated gold
                                self._refresh_equipment_panel(game_engine, character['id'])
                            else:
                                self._log_monster_action(f"[GOLD] Found {gold_amount} gold pieces, but couldn't add to inventory!")
                                print(f"[TREASURE] Failed to add {gold_amount} GP to character inventory")
                        except Exception as e:
                            self._log_monster_action(f"[GOLD] Found {gold_amount} gold pieces, but couldn't add to inventory!")
                            print(f"[TREASURE] Error adding gold: {e}")
                        return
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error adding gold to character: {e}")
    
    def _handle_short_rest_action(self):
        """Handle clicking the Short Rest action card."""
        self._log_monster_action("[REST] Taking a short rest...")
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
            
            # Restore pact magic spell slots (Warlock short rest benefit)
            try:
                from services.spellcasting_service import SpellcastingService
                spellcasting_service = SpellcastingService()
                restored_slots = spellcasting_service.restore_spell_slots(character['id'], 'short')

                if restored_slots:
                    slots_restored_desc = [f"Level {level}: {slots} pact slots" for level, slots in restored_slots.items()]
                    self._log_monster_action(f"🔮 Pact magic restored: {', '.join(slots_restored_desc)}")

                    # Refresh spell action cards to show available pact slots
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'action_panel') and hasattr(parent.action_panel, '_refresh_spell_action_cards'):
                            parent.action_panel._refresh_spell_action_cards()
                            break
                        parent = parent.parent()

            except Exception as e:
                print(f"Error restoring pact magic slots: {e}")

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
                        current_hp = fresh_character.get('current_hit_points',
                                                        fresh_character['hit_points_current'])
                        max_hp = fresh_character.get('max_hit_points',
                                                     fresh_character['hit_points_max'])
                        break
                parent = parent.parent()
            else:
                # Fallback to character object values
                current_hp = character.get('current_hit_points',
                                           character['hit_points_current'])
                max_hp = character.get('max_hit_points',
                                       character['hit_points_max'])
        except Exception as e:
            print(f"ERROR: Could not get HP: {e}")
            current_hp = character.get('current_hit_points',
                                       character['hit_points_current'])
            max_hp = character.get('max_hit_points',
                                   character['hit_points_max'])
        
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
        # Ensure hit dice track character level without auto-refilling
        sync_hit_dice_with_level(character)
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
            self._log_monster_action(f"[HEAL] HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {actual_healing}, max HP reached)")
        else:
            self._log_monster_action(f"[DICE] Hit Dice: {roll_details} = {total_healing} healing")
            self._log_monster_action(f"[HEAL] HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {actual_healing})")
        
        # Update status label
        status_label.setText(f"Current HP: {new_hp}/{max_hp}")
        
        # Save changes to database FIRST (source of truth)
        game_engine.update_character_hp_sync(new_hp, max_hp)
        
        # Update character sheet display to reflect database state
        self._update_character_sheet_hp(new_hp, max_hp)
        
        # Close dialog if at full health
        if new_hp >= max_hp:
            self._log_monster_action("[HEAL] Fully healed!")
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
            self._log_monster_action(f"[HEAL] HP fully restored: {old_hp}/{max_hp} -> {max_hp}/{max_hp}")
            
            # 2. Restore spent hit dice (up to half maximum, minimum 1)
            old_hit_dice = character.get('hit_dice_current', 0)
            new_hit_dice, restored = restore_hit_dice_on_long_rest(character)
            if restored > 0:
                self._log_monster_action(
                    f"[DICE] Hit Dice restored: {old_hit_dice} -> {new_hit_dice} (gained {restored})"
                )
            
            # 3. Restore all spell slots using SpellcastingService
            try:
                from services.spellcasting_service import SpellcastingService
                spellcasting_service = SpellcastingService()
                restored_slots = spellcasting_service.restore_spell_slots(character['id'], 'long')

                if restored_slots:
                    slots_restored_desc = [f"Level {level}: {slots} slots" for level, slots in restored_slots.items()]
                    self._log_monster_action(f"✨ Spell slots restored: {', '.join(slots_restored_desc)}")

                    # Refresh spell action cards to show available slots
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'action_panel') and hasattr(parent.action_panel, '_refresh_spell_action_cards'):
                            parent.action_panel._refresh_spell_action_cards()
                            break
                        parent = parent.parent()

            except Exception as e:
                print(f"Error restoring spell slots: {e}")
            
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

    def _cleanup_active_widgets(self):
        """Clean up any active encounter widgets (vendor, skill challenge, hazard, etc.)."""
        if self.vendor_widget:
            self.vendor_widget.setParent(None)
            self.vendor_widget = None

        if self.skill_challenge_widget:
            self.skill_challenge_widget.setParent(None)
            self.skill_challenge_widget = None

        if self.hazard_widget:
            self.hazard_widget.setParent(None)
            self.hazard_widget = None

        # Show standard UI elements
        self.encounter_details_text.setVisible(True)

    def _on_skill_challenge_completed(self, outcome: str, reward_text: str):
        """Handle skill challenge completion."""
        character_data = self._get_current_character_data()
        if not character_data:
            return

        try:
            # Calculate XP based on outcome
            character_level = character_data.get('level', 1)
            if outcome == 'success':
                # Success: low challenge XP
                xp_gained = self._calculate_skill_challenge_xp(character_level, success=True)
                updated_character, log_messages = self.skill_challenge_rewards.apply_reward(
                    character_data, reward_text
                )
                self._log_monster_action(f"[SUCCESS] Skill challenge completed! Reward: {reward_text}")
            else:
                # Failure: half of low challenge XP
                xp_gained = self._calculate_skill_challenge_xp(character_level, success=False)
                updated_character, log_messages = self.skill_challenge_rewards.apply_penalty(
                    character_data, reward_text
                )
                self._log_monster_action(f"[FAILURE] Skill challenge failed! Penalty: {reward_text}")

            # Award XP for participation
            if xp_gained > 0:
                self._add_xp_to_character(xp_gained)
                self._log_monster_action(f"[XP] Gained {xp_gained} XP from skill challenge")

            # Log individual effects
            for message in log_messages:
                self._log_monster_action(f"[EFFECT] {message}")

            # Save character changes
            self.skill_challenge_rewards.save_character_data(updated_character)

            # Log to rewards tracking
            self.skill_challenge_rewards.log_reward_application(
                character_data.get('id', ''), outcome, reward_text, "; ".join(log_messages)
            )

            # Clean up the skill challenge widget
            self._cleanup_active_widgets()

            # Refresh character data in other panels
            self._force_reload_character()

        except Exception as e:
            self._log_monster_action(f"[ERROR] Failed to apply skill challenge outcome: {e}")

    def _on_skill_challenge_refused(self, refuse_cost: str):
        """Handle skill challenge refusal."""
        character_data = self._get_current_character_data()
        if not character_data:
            return

        try:
            # Apply the refusal cost
            updated_character, log_messages = self.skill_challenge_rewards.apply_refuse_cost(
                character_data, refuse_cost
            )

            self._log_monster_action(f"[REFUSED] Skill challenge refused. Cost: {refuse_cost}")

            # Log individual effects
            for message in log_messages:
                self._log_monster_action(f"[EFFECT] {message}")

            # Save character changes
            self.skill_challenge_rewards.save_character_data(updated_character)

            # Log to rewards tracking
            self.skill_challenge_rewards.log_reward_application(
                character_data.get('id', ''), 'refused', refuse_cost, "; ".join(log_messages)
            )

            # Clean up the skill challenge widget
            self._cleanup_active_widgets()

            # Refresh character data in other panels
            self._force_reload_character()

        except Exception as e:
            self._log_monster_action(f"[ERROR] Failed to apply skill challenge refusal cost: {e}")

    def _on_hazard_completed(self, success: bool, xp_gained: int, damage_taken: int, exhaustion_gained: int, roll_summary: str):
        character_data = self._get_current_character_data()
        if not character_data:
            return

        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            self._log_monster_action(f"[HAZARD] {roll_summary}")

            if damage_taken > 0:
                current_hp = character_data.get('current_hit_points', 0)
                new_hp = max(0, current_hp - damage_taken)

                cursor.execute("""
                    UPDATE characters
                    SET current_hit_points = ?
                    WHERE id = ?
                """, (new_hp, character_data['id']))

                self._log_monster_action(f"[HP] {current_hp} -> {new_hp}")

            if exhaustion_gained > 0:
                current_exhaustion = character_data.get('exhaustion_level', 0)
                new_exhaustion = min(6, current_exhaustion + exhaustion_gained)

                cursor.execute("""
                    UPDATE characters
                    SET exhaustion_level = ?
                    WHERE id = ?
                """, (new_exhaustion, character_data['id']))

                self._log_monster_action(f"[EXHAUSTION] {current_exhaustion} -> {new_exhaustion}")

            conn.commit()
            conn.close()

            if xp_gained > 0:
                self._add_xp_to_character(xp_gained)
                self._log_monster_action(f"[XP] Gained {xp_gained} XP from hazard")

            self._cleanup_active_widgets()
            self._force_reload_character()

        except Exception as e:
            self._log_monster_action(f"[ERROR] Failed to apply hazard outcome: {e}")

    def _force_reload_character(self):
        """Force reload character data in all panels."""
        try:
            # Find main window and trigger character reload
            parent = self.parent()
            while parent:
                if hasattr(parent, '_force_reload_character'):
                    parent._force_reload_character()
                    return
                parent = parent.parent()
        except Exception as e:
            print(f"[UI] Error forcing character reload: {e}")


