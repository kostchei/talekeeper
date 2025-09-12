"""
Action Cards Widget - Bottom panel for character actions

This module provides the UI for character actions. It is responsible for
displaying available actions and signaling user intent to the game engine.
All combat logic, calculations, and state management are handled by the
core.combat_manager.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QButtonGroup,
                            QToolTip, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from typing import Optional, Dict, Any, List
from enum import Enum

# This import is no longer needed as all fighting style logic is in CombatManager
# from services.fighting_style_effects import FightingStyleEffects

print("DEBUG: action_panel.py module loaded/imported at line 22")

class ActionType(Enum):
    """Types of character actions."""
    ATTACK_MAIN_HAND = "attack_main_hand"
    ATTACK_OFF_HAND = "attack_off_hand"
    CAST_SPELL = "cast_spell"
    USE_ITEM = "use_item"
    MOVE = "move"
    DASH = "dash"
    DODGE = "dodge"
    SEARCH = "search"
    HIDE = "hide"
    REST = "rest"
    INVESTIGATE = "investigate"
    INTERACT = "interact"
    OPPORTUNITY = "opportunity"
    SECOND_WIND = "second_wind"
    ACTION_SURGE = "action_surge"
    RAGE = "rage"
    RECKLESS_ATTACK = "reckless_attack"
    LAY_ON_HANDS = "lay_on_hands"

class ActionCategory(Enum):
    """Action categories for grouping."""
    COMBAT = "combat"
    MOVEMENT = "movement"
    BONUS = "bonus"
    FREE = "free"
    REACTION = "reaction"

class ActionPanel(QWidget):
    """
    Bottom action cards panel for quick character actions.
    This panel is a "dumb" component that signals user intent to the game engine.
    """
    action_triggered = pyqtSignal(ActionType, dict)
    action_hovered = pyqtSignal(ActionType, str)
    category_changed = pyqtSignal(ActionCategory)

    def __init__(self, game_engine, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.current_category = ActionCategory.COMBAT
        self.action_cards: Dict[ActionType, ActionCard] = {}
        self.character_context: Dict[str, Any] = {}
        self.equipped_weapons: Dict[str, Any] = {}
        self.target_monster_id: Optional[str] = None
        
        self.setFixedSize(1280, 300)
        self.setAutoFillBackground(True)
        self._setup_ui()
        self._apply_styles()
        self._create_action_cards()

    def _setup_ui(self):
        """Initialize the action panel UI components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(3)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(35)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 3, 8, 3)
        
        self.title_label = QLabel("Actions")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.category_buttons = QButtonGroup(self)
        category_labels = {
            ActionCategory.COMBAT: "Action",
            ActionCategory.MOVEMENT: "Movement", 
            ActionCategory.BONUS: "Bonus",
            ActionCategory.FREE: "Free",
            ActionCategory.REACTION: "Reaction"
        }
        for category in ActionCategory:
            btn = QPushButton(category_labels[category])
            btn.setObjectName("categoryButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=category: self._set_category(c))
            self.category_buttons.addButton(btn)
            header_layout.addWidget(btn)
        
        self.category_buttons.buttons()[0].setChecked(True)
        
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.cards_container, 1)

    def _create_action_cards(self):
        """Create static action cards. Weapon cards are created separately."""
        static_actions = {
            ActionCategory.COMBAT: [
                (ActionType.CAST_SPELL, "✨", "Cast Spell", "Cast a spell from your repertoire"),
                (ActionType.USE_ITEM, "🎒", "Use Item", "Use an item from your inventory"),
                (ActionType.DODGE, "🛡️", "Dodge", "Focus on avoiding attacks"),
            ],
            ActionCategory.MOVEMENT: [
                (ActionType.MOVE, "🏃", "Move", "Move up to your speed"),
                (ActionType.DASH, "💨", "Dash", "Double your movement speed"),
                (ActionType.HIDE, "👻", "Hide", "Attempt to become hidden"),
            ],
        }
        
        for category, actions in static_actions.items():
            for action_type, icon, name, description in actions:
                card = ActionCard(action_type, icon, name, description)
                card.action_triggered.connect(self._trigger_action)
                card.action_hovered.connect(self.action_hovered)
                self.action_cards[action_type] = card
        
        self._create_weapon_cards()
        self._update_visible_cards()

    def _create_weapon_cards(self):
        """Creates simplified weapon attack cards."""
        for action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
            if action_type in self.action_cards:
                self.action_cards[action_type].deleteLater()
                del self.action_cards[action_type]
        
        main_hand = self.equipped_weapons.get('main_hand')
        if main_hand and main_hand.get('item_type') == 'weapon':
            weapon_name = main_hand.get('name', 'Weapon')
            description = "Attack with your main-hand weapon."
            card = ActionCard(ActionType.ATTACK_MAIN_HAND, "⚔️", weapon_name, description)
            card.weapon_data = main_hand
            card.action_triggered.connect(self._trigger_action)
            self.action_cards[ActionType.ATTACK_MAIN_HAND] = card
        
        off_hand = self.equipped_weapons.get('off_hand')
        if off_hand and off_hand.get('item_type') == 'weapon':
            weapon_name = off_hand.get('name', 'Off-hand')
            description = "Attack with your off-hand weapon."
            card = ActionCard(ActionType.ATTACK_OFF_HAND, "🗡️", f"{weapon_name} (Off)", description)
            card.weapon_data = off_hand
            card.action_triggered.connect(self._trigger_action)
            self.action_cards[ActionType.ATTACK_OFF_HAND] = card

    def _apply_styles(self):
        self.setStyleSheet("""
            ActionPanel { background-color: #1a1a1a; }
            QFrame#headerFrame { background-color: #333333; border: 1px solid #555555; border-radius: 4px; }
            QLabel#titleLabel { color: #ffffff; font-size: 16px; font-weight: bold; }
            QPushButton#categoryButton { background-color: #404040; color: #cccccc; border: 1px solid #666666; border-radius: 4px; padding: 4px 12px; font-size: 11px; font-weight: bold; }
            QPushButton#categoryButton:hover { background-color: #505050; }
            QPushButton#categoryButton:checked { background-color: #4a90e2; color: #ffffff; border-color: #6ab0ff; }
        """)

    def _set_category(self, category: ActionCategory):
        self.current_category = category
        self._update_visible_cards()
        self.category_changed.emit(category)

    def _update_visible_cards(self):
        """Update which action cards are visible based on current category."""
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child: child.setParent(None)
        
        action_map = {
            ActionCategory.COMBAT: [ActionType.ATTACK_MAIN_HAND, ActionType.CAST_SPELL, ActionType.USE_ITEM, ActionType.DODGE],
            ActionCategory.MOVEMENT: [ActionType.MOVE, ActionType.DASH, ActionType.HIDE],
            ActionCategory.BONUS: [ActionType.ATTACK_OFF_HAND, ActionType.SECOND_WIND, ActionType.RAGE],
            ActionCategory.FREE: [ActionType.INTERACT, ActionType.ACTION_SURGE, ActionType.RECKLESS_ATTACK],
            ActionCategory.REACTION: [ActionType.OPPORTUNITY]
        }

        actions_to_show = action_map.get(self.current_category, [])
        for action_type in actions_to_show:
            if action_type in self.action_cards:
                card = self.action_cards[action_type]
                self.cards_layout.addWidget(card)
                card.show()
        
        self.cards_layout.addStretch()

    def _trigger_action(self, action_type: ActionType, context: Dict[str, Any]):
        """Handle action trigger from card by signaling the game engine."""
        character_id = self.character_context.get('id')
        if not character_id:
            self._log_to_combat_panel("[ERROR] No character selected.")
            return

        combat_manager = self.game_engine.combat_manager
        if not combat_manager:
            self._log_to_combat_panel("[ERROR] Combat manager not found.")
            return

        if action_type == ActionType.ATTACK_MAIN_HAND:
            if not self.target_monster_id:
                self._log_to_combat_panel("[ERROR] No target selected for attack.")
                return
            weapon_data = context.get('weapon_data', {})
            combat_manager.execute_player_attack(character_id, weapon_data, self.target_monster_id)
            game_engine.update_combat_log()
            game_engine.update_all_character_panels()

        elif action_type == ActionType.ATTACK_OFF_HAND:
            if not self.target_monster_id:
                self._log_to_combat_panel("[ERROR] No target selected for attack.")
                return
            combat_manager.execute_offhand_attack(character_id, self.target_monster_id)
            game_engine.update_combat_log()
            game_engine.update_all_character_panels()
            
        else:
            # For non-attack actions, emit a generic signal for now
            self.action_triggered.emit(action_type, {**context, **self.character_context})

    def _log_to_combat_panel(self, message: str):
        """Helper to log messages to the main combat log."""
        try:
            self.parent().log_panel.log_combat(message)
        except AttributeError:
            print(f"LOGGING ERROR: {message}")

    def load_character_equipment(self, equipped_items: Dict[str, Any], character_stats: Dict[str, Any]):
        """Load character equipment and stats to create weapon cards."""
        self.equipped_weapons = equipped_items.copy()
        self.character_context.update(character_stats)
        self._create_weapon_cards()
        self._update_visible_cards()
    
    def load_character_features(self, character_features: Dict[str, Any]):
        """Load character features to create feature-based action cards."""
        # Simplified: Check for features and create cards if they exist.
        if 'Second Wind' in character_features:
            card = ActionCard(ActionType.SECOND_WIND, "❤️", "Second Wind", "Regain hit points.")
            card.action_triggered.connect(self._trigger_action)
            self.action_cards[ActionType.SECOND_WIND] = card
        
        if 'Action Surge' in character_features:
            card = ActionCard(ActionType.ACTION_SURGE, "⚡", "Action Surge", "Gain an additional action.")
            card.action_triggered.connect(self._trigger_action)
            self.action_cards[ActionType.ACTION_SURGE] = card
            
        if 'Rage' in character_features:
            card = ActionCard(ActionType.RAGE, "😡", "Rage", "Enter a barbarian rage.")
            card.action_triggered.connect(self._trigger_action)
            self.action_cards[ActionType.RAGE] = card
            
        self._update_visible_cards()

    def set_target_monster(self, monster_id: str):
        self.target_monster_id = monster_id

    def set_character_context(self, context: Dict[str, Any]):
        self.character_context = context
        # Potentially update cards based on context, e.g., enabling/disabling
        # For now, this just stores the context.

class ActionCard(QWidget):
    """Individual action card widget."""
    action_triggered = pyqtSignal(ActionType, dict)
    action_hovered = pyqtSignal(ActionType, str)

    def __init__(self, action_type: ActionType, icon: str, name: str, description: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.action_type = action_type
        self.icon = icon
        self.name = name
        self.description = description
        self.weapon_data: Optional[Dict[str, Any]] = None

        self.setFixedSize(140, 180)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        icon_label = QLabel(self.icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setObjectName("iconLabel")
        layout.addWidget(icon_label)
        
        name_label = QLabel(self.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setObjectName("nameLabel")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        desc_label = QLabel(self.description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setObjectName("descLabel")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, 1)
        
        action_btn = QPushButton("Use")
        action_btn.setObjectName("actionButton")
        action_btn.clicked.connect(self._trigger_action)
        layout.addWidget(action_btn)

    def _apply_styles(self):
        self.setStyleSheet("""
            ActionCard { background-color: #2d2d2d; border: 2px solid #555555; border-radius: 8px; }
            ActionCard:hover { border-color: #4a90e2; }
            QLabel#iconLabel { font-size: 24px; background-color: #333333; border-radius: 25px; min-height: 50px; max-height: 50px; }
            QLabel#nameLabel { color: #ffffff; font-size: 12px; font-weight: bold; }
            QLabel#descLabel { color: #cccccc; font-size: 10px; }
            QPushButton#actionButton { background-color: #4a90e2; color: #ffffff; border: none; border-radius: 4px; padding: 6px; font-weight: bold; }
            QPushButton#actionButton:hover { background-color: #6ab0ff; }
            QPushButton#actionButton:pressed { background-color: #3a80d2; }
        """)

    def _trigger_action(self):
        context = {"name": self.name, "description": self.description}
        if self.weapon_data:
            context['weapon_data'] = self.weapon_data
        self.action_triggered.emit(self.action_type, context)

    def enterEvent(self, event):
        self.action_hovered.emit(self.action_type, self.description)
        super().enterEvent(event)