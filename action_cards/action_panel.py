"""
Action Cards Widget - Bottom panel for character actions

PyQt6 widget that provides quick access to character actions:
- Combat actions (Attack, Cast Spell, Use Item)
- Movement actions (Move, Dash, Dodge)
- Utility actions (Help, Search, Hide)
- Customizable action cards
- Context-sensitive action availability

Designed to match ui_plan.md specifications:
- Fixed size: 1728x300 (full width minus margins)
- Horizontal card layout
- Dark theme styling
- Action cooldowns and availability
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QButtonGroup,
                            QToolTip, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from typing import Optional, Dict, Any, List
from enum import Enum


class ActionType(Enum):
    """Types of character actions."""
    ATTACK = "attack"
    CAST_SPELL = "cast_spell"
    USE_ITEM = "use_item"
    MOVE = "move"
    DASH = "dash"
    DODGE = "dodge"
    HELP = "help"
    SEARCH = "search"
    HIDE = "hide"
    REST = "rest"
    INVESTIGATE = "investigate"
    INTERACT = "interact"


class ActionCategory(Enum):
    """Action categories for grouping."""
    COMBAT = "combat"
    MOVEMENT = "movement"
    UTILITY = "utility"
    SOCIAL = "social"
    EXPLORATION = "exploration"


class ActionPanel(QWidget):
    """
    Bottom action cards panel for quick character actions.
    
    Signals:
        action_triggered: Emitted when action is triggered (ActionType, dict context)
        action_hovered: Emitted when action is hovered (ActionType, str description)
        category_changed: Emitted when category filter changes (ActionCategory)
    """
    
    action_triggered = pyqtSignal(ActionType, dict)  # action, context
    action_hovered = pyqtSignal(ActionType, str)  # action, description
    category_changed = pyqtSignal(ActionCategory)  # category
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_category = ActionCategory.COMBAT
        self.action_cards = {}  # ActionType -> ActionCard mapping
        self.action_cooldowns = {}  # ActionType -> remaining turns
        self.character_context = {}  # Current character state
        
        # Set fixed size
        self.setFixedSize(1728, 300)
        self._setup_ui()
        self._apply_styles()
        self._create_action_cards()
        
        # Cooldown timer
        self.cooldown_timer = QTimer()
        self.cooldown_timer.timeout.connect(self._update_cooldowns)
        self.cooldown_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Initialize the action panel UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(3)
        
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(35)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 3, 8, 3)
        
        # Title
        self.title_label = QLabel("Actions")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Category filter buttons
        self.category_buttons = QButtonGroup(self)
        
        for category in ActionCategory:
            btn = QPushButton(category.value.title())
            btn.setObjectName("categoryButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=category: self._set_category(c))
            self.category_buttons.addButton(btn)
            header_layout.addWidget(btn)
        
        # Set combat as default
        self.category_buttons.buttons()[0].setChecked(True)
        
        # === ACTION CARDS AREA ===
        # Scroll area for action cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scrollArea")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlways)
        self.scroll_area.setWidgetResizable(True)
        
        # Container for action cards
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.cards_container)
        
        # === STATUS BAR ===
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusFrame")
        self.status_frame.setFixedHeight(25)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(8, 2, 8, 2)
        
        # Action economy display
        self.action_economy_label = QLabel("Action: Available | Bonus: Available | Reaction: Available")
        self.action_economy_label.setObjectName("statusLabel")
        status_layout.addWidget(self.action_economy_label)
        
        status_layout.addStretch()
        
        # Turn indicator
        self.turn_label = QLabel("Your Turn")
        self.turn_label.setObjectName("turnLabel")
        status_layout.addWidget(self.turn_label)
        
        # Add sections to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.scroll_area, 1)
        self.main_layout.addWidget(self.status_frame)
    
    def _create_action_cards(self):
        """Create action cards for different action types."""
        # Define actions by category
        actions_by_category = {
            ActionCategory.COMBAT: [
                (ActionType.ATTACK, "⚔️", "Attack", "Make a melee or ranged attack"),
                (ActionType.CAST_SPELL, "✨", "Cast Spell", "Cast a spell from your repertoire"),
                (ActionType.USE_ITEM, "🧪", "Use Item", "Use an item from your inventory"),
                (ActionType.DODGE, "🛡️", "Dodge", "Gain advantage on Dexterity saves"),
                (ActionType.HELP, "🤝", "Help", "Give an ally advantage on their next action"),
            ],
            ActionCategory.MOVEMENT: [
                (ActionType.MOVE, "👟", "Move", "Move up to your speed"),
                (ActionType.DASH, "💨", "Dash", "Double your movement speed this turn"),
                (ActionType.HIDE, "👻", "Hide", "Attempt to become hidden"),
            ],
            ActionCategory.UTILITY: [
                (ActionType.SEARCH, "🔍", "Search", "Look for hidden objects or clues"),
                (ActionType.INVESTIGATE, "🕵️", "Investigate", "Make a detailed investigation"),
                (ActionType.INTERACT, "✋", "Interact", "Interact with objects or environment"),
                (ActionType.REST, "😴", "Rest", "Take a short rest to recover"),
            ]
        }
        
        # Create cards for all actions
        for category, actions in actions_by_category.items():
            for action_type, icon, name, description in actions:
                card = ActionCard(action_type, icon, name, description)
                card.action_triggered.connect(self._trigger_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[action_type] = card
        
        # Show initial category
        self._update_visible_cards()
    
    def _apply_styles(self):
        """Apply dark theme styling to action panel components."""
        style_sheet = """
        ActionPanel {
            background-color: #2a2a2a;
            border: 2px solid #444444;
            border-radius: 8px;
        }
        
        QFrame#headerFrame {
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QFrame#statusFrame {
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QLabel#titleLabel {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel#statusLabel {
            color: #cccccc;
            font-size: 11px;
        }
        
        QLabel#turnLabel {
            color: #4a90e2;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 6px;
            border: 1px solid #4a90e2;
            border-radius: 3px;
        }
        
        QPushButton#categoryButton {
            background-color: #404040;
            color: #cccccc;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
        }
        
        QPushButton#categoryButton:hover {
            background-color: #505050;
        }
        
        QPushButton#categoryButton:checked {
            background-color: #4a90e2;
            color: #ffffff;
            border-color: #6ab0ff;
        }
        
        QScrollArea#scrollArea {
            background-color: #1e1e1e;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QScrollBar:horizontal {
            background-color: #2a2a2a;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #666666;
        }
        """
        self.setStyleSheet(style_sheet)
    
    def _set_category(self, category: ActionCategory):
        """Set the active action category."""
        self.current_category = category
        self._update_visible_cards()
        self.category_changed.emit(category)
    
    def _update_visible_cards(self):
        """Update which action cards are visible based on current category."""
        # Clear current layout
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add cards for current category
        actions_by_category = {
            ActionCategory.COMBAT: [ActionType.ATTACK, ActionType.CAST_SPELL, ActionType.USE_ITEM, 
                                  ActionType.DODGE, ActionType.HELP],
            ActionCategory.MOVEMENT: [ActionType.MOVE, ActionType.DASH, ActionType.HIDE],
            ActionCategory.UTILITY: [ActionType.SEARCH, ActionType.INVESTIGATE, 
                                   ActionType.INTERACT, ActionType.REST]
        }
        
        category_actions = actions_by_category.get(self.current_category, [])
        
        for action_type in category_actions:
            if action_type in self.action_cards:
                card = self.action_cards[action_type]
                self.cards_layout.addWidget(card)
                card.show()
        
        # Add stretch to push cards to left
        self.cards_layout.addStretch()
    
    def _trigger_action(self, action_type: ActionType, context: Dict[str, Any]):
        """Handle action trigger from card."""
        # Check if action is available
        if self._is_action_available(action_type):
            # Add character context
            full_context = {**context, **self.character_context}
            
            # Start cooldown if applicable
            cooldown = self._get_action_cooldown(action_type)
            if cooldown > 0:
                self.action_cooldowns[action_type] = cooldown
                self.action_cards[action_type].set_cooldown(cooldown)
            
            # Emit signal
            self.action_triggered.emit(action_type, full_context)
            
            # Update action economy
            self._update_action_economy(action_type)
    
    def _action_hovered(self, action_type: ActionType, description: str):
        """Handle action hover from card."""
        # Add additional context to description
        enhanced_description = description
        
        # Add requirements or restrictions
        if not self._is_action_available(action_type):
            reasons = self._get_unavailability_reasons(action_type)
            enhanced_description += f"\n\nUnavailable: {', '.join(reasons)}"
        
        self.action_hovered.emit(action_type, enhanced_description)
    
    def _is_action_available(self, action_type: ActionType) -> bool:
        """Check if an action is currently available."""
        # Check cooldowns
        if action_type in self.action_cooldowns and self.action_cooldowns[action_type] > 0:
            return False
        
        # Check action economy (simplified)
        action_costs = {
            ActionType.ATTACK: "action",
            ActionType.CAST_SPELL: "action", 
            ActionType.USE_ITEM: "action",
            ActionType.MOVE: "movement",
            ActionType.DASH: "action",
            ActionType.DODGE: "action",
            ActionType.HELP: "action",
            ActionType.SEARCH: "action",
            ActionType.INVESTIGATE: "action",
            ActionType.INTERACT: "action",
            ActionType.HIDE: "action",
            ActionType.REST: "special"
        }
        
        cost_type = action_costs.get(action_type, "free")
        
        # In a real implementation, track available actions per turn
        # For now, assume all actions are available
        return True
    
    def _get_unavailability_reasons(self, action_type: ActionType) -> List[str]:
        """Get reasons why an action is unavailable."""
        reasons = []
        
        if action_type in self.action_cooldowns and self.action_cooldowns[action_type] > 0:
            turns = self.action_cooldowns[action_type]
            reasons.append(f"Cooldown ({turns} turn{'s' if turns != 1 else ''})")
        
        return reasons
    
    def _get_action_cooldown(self, action_type: ActionType) -> int:
        """Get the cooldown turns for an action."""
        cooldowns = {
            ActionType.REST: 1,  # Can't rest again immediately
            ActionType.DASH: 0,  # No cooldown, but uses action
        }
        return cooldowns.get(action_type, 0)
    
    def _update_action_economy(self, used_action: ActionType):
        """Update action economy after using an action."""
        # This would track used actions, bonus actions, reactions per turn
        # For now, just update the display
        pass
    
    def _update_cooldowns(self):
        """Update action cooldowns (called by timer)."""
        for action_type in list(self.action_cooldowns.keys()):
            if self.action_cooldowns[action_type] > 0:
                self.action_cooldowns[action_type] -= 1
                if self.action_cooldowns[action_type] <= 0:
                    del self.action_cooldowns[action_type]
                    if action_type in self.action_cards:
                        self.action_cards[action_type].clear_cooldown()
                else:
                    if action_type in self.action_cards:
                        self.action_cards[action_type].set_cooldown(self.action_cooldowns[action_type])
    
    def set_character_context(self, context: Dict[str, Any]):
        """Set the character context for action availability."""
        self.character_context = context
        self._update_card_availability()
    
    def _update_card_availability(self):
        """Update the availability state of all action cards."""
        for action_type, card in self.action_cards.items():
            available = self._is_action_available(action_type)
            card.set_available(available)
    
    def set_turn_active(self, active: bool):
        """Set whether it's currently the character's turn."""
        if active:
            self.turn_label.setText("Your Turn")
            self.turn_label.setStyleSheet("color: #4a90e2; border-color: #4a90e2;")
        else:
            self.turn_label.setText("Wait")
            self.turn_label.setStyleSheet("color: #888888; border-color: #888888;")
        
        # Enable/disable all cards based on turn
        for card in self.action_cards.values():
            card.setEnabled(active)
    
    def reset_action_economy(self):
        """Reset action economy for a new turn."""
        # This would reset available actions, bonus actions, reactions
        self.action_economy_label.setText("Action: Available | Bonus: Available | Reaction: Available")


class ActionCard(QWidget):
    """Individual action card widget."""
    
    action_triggered = pyqtSignal(ActionType, dict)  # action_type, context
    action_hovered = pyqtSignal(ActionType, str)  # action_type, description
    
    def __init__(self, action_type: ActionType, icon: str, name: str, description: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.action_type = action_type
        self.icon = icon
        self.name = name
        self.description = description
        self.available = True
        self.cooldown_remaining = 0
        
        self.setFixedSize(140, 180)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the action card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Icon
        self.icon_label = QLabel(self.icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setObjectName("iconLabel")
        layout.addWidget(self.icon_label)
        
        # Name
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setObjectName("nameLabel")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        # Description
        self.desc_label = QLabel(self.description)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setObjectName("descLabel")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label, 1)
        
        # Cooldown bar (hidden by default)
        self.cooldown_bar = QProgressBar()
        self.cooldown_bar.setObjectName("cooldownBar")
        self.cooldown_bar.setVisible(False)
        layout.addWidget(self.cooldown_bar)
        
        # Action button
        self.action_btn = QPushButton("Use")
        self.action_btn.setObjectName("actionButton")
        self.action_btn.clicked.connect(self._trigger_action)
        layout.addWidget(self.action_btn)
    
    def _apply_styles(self):
        """Apply styling to the action card."""
        self.setStyleSheet("""
        ActionCard {
            background-color: #2d2d2d;
            border: 2px solid #555555;
            border-radius: 8px;
        }
        
        ActionCard:hover {
            border-color: #4a90e2;
        }
        
        QLabel#iconLabel {
            font-size: 32px;
            background-color: #333333;
            border-radius: 20px;
            min-height: 40px;
            max-height: 40px;
        }
        
        QLabel#nameLabel {
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
        }
        
        QLabel#descLabel {
            color: #cccccc;
            font-size: 10px;
        }
        
        QPushButton#actionButton {
            background-color: #4a90e2;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 6px;
            font-weight: bold;
            font-size: 11px;
        }
        
        QPushButton#actionButton:hover {
            background-color: #6ab0ff;
        }
        
        QPushButton#actionButton:pressed {
            background-color: #3a80d2;
        }
        
        QPushButton#actionButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QProgressBar#cooldownBar {
            border: 1px solid #666666;
            border-radius: 2px;
            text-align: center;
            background-color: #1a1a1a;
            max-height: 12px;
        }
        
        QProgressBar#cooldownBar::chunk {
            background-color: #ff6b6b;
            border-radius: 1px;
        }
        """)
    
    def _trigger_action(self):
        """Trigger the action."""
        if self.available and self.cooldown_remaining == 0:
            context = {
                "name": self.name,
                "description": self.description
            }
            self.action_triggered.emit(self.action_type, context)
    
    def set_available(self, available: bool):
        """Set whether the action is available."""
        self.available = available
        self.action_btn.setEnabled(available and self.cooldown_remaining == 0)
        
        if available:
            self.setStyleSheet(self.styleSheet().replace("border: 2px solid #666666;", "border: 2px solid #555555;"))
        else:
            self.setStyleSheet(self.styleSheet().replace("border: 2px solid #555555;", "border: 2px solid #666666;"))
    
    def set_cooldown(self, turns: int):
        """Set cooldown remaining."""
        self.cooldown_remaining = turns
        if turns > 0:
            self.cooldown_bar.setVisible(True)
            self.cooldown_bar.setMaximum(turns)
            self.cooldown_bar.setValue(turns)
            self.action_btn.setEnabled(False)
        else:
            self.clear_cooldown()
    
    def clear_cooldown(self):
        """Clear the cooldown."""
        self.cooldown_remaining = 0
        self.cooldown_bar.setVisible(False)
        self.action_btn.setEnabled(self.available)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.action_hovered.emit(self.action_type, self.description)
        super().enterEvent(event)