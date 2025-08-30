"""
Action Cards Widget - Bottom panel for character actions

PyQt6 widget that provides quick access to character actions:
- Combat actions (Attack, Cast Spell, Use Item, Dodge)
- Movement actions (Move, Dash, Hide)
- Utility actions (Search, Investigate, Interact, Rest)
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
        self.equipped_weapons = {}  # Store equipped weapon data
        self.target_monster_id = None  # Currently targeted monster for attacks
        
        # Set fixed size (center + right columns only)
        self.setFixedSize(1280, 300)  # Extended width to almost reach equipment panel
        self.setAutoFillBackground(True)  # Ensure background is filled
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
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(3)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        
        # Set combat as default
        self.category_buttons.buttons()[0].setChecked(True)
        
        # === ACTION CARDS AREA ===
        # Direct container for action cards (no scrolling)
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        
        # Add sections to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.cards_container, 1)
    
    def _create_action_cards(self):
        """Create action cards for different action types."""
        # Create non-weapon action cards first
        static_actions = {
            ActionCategory.COMBAT: [
                (ActionType.CAST_SPELL, "✨", "Magic", "Cast a spell from your repertoire"),
                (ActionType.USE_ITEM, "🧪", "Use Item", "Use an item from your inventory"),
                (ActionType.DODGE, "🛡️", "Dodge", "Gain advantage on Dexterity saves"),
            ],
            ActionCategory.MOVEMENT: [
                (ActionType.MOVE, "👟", "Move", "Move up to your speed"),
                (ActionType.DASH, "💨", "Dash", "Double your movement speed this turn"),
                (ActionType.HIDE, "👻", "Hide", "Attempt to become hidden"),
            ],
            ActionCategory.BONUS: [
                (ActionType.SEARCH, "🔍", "Search", "Look for hidden objects or clues"),
                (ActionType.INVESTIGATE, "🕵️", "Investigate", "Make a detailed investigation"),
                (ActionType.REST, "😴", "Rest", "Take a short rest to recover"),
            ],
            ActionCategory.FREE: [
                (ActionType.INTERACT, "✋", "Interact", "Interact with objects or environment"),
            ],
            ActionCategory.REACTION: [
                (ActionType.OPPORTUNITY, "⚡", "Opportunity", "Make an opportunity attack"),
            ]
        }
        
        # Create cards for static actions
        for category, actions in static_actions.items():
            for action_type, icon, name, description in actions:
                card = ActionCard(action_type, icon, name, description)
                card.action_triggered.connect(self._trigger_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[action_type] = card
        
        # Create placeholder weapon cards (will be updated when equipment is loaded)
        self._create_weapon_cards()
        
        # Show initial category
        self._update_visible_cards()
    
    def _create_weapon_cards(self):
        """Create weapon attack cards based on equipped weapons."""
        # Remove existing weapon cards
        for action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
            if action_type in self.action_cards:
                self.action_cards[action_type].deleteLater()
                del self.action_cards[action_type]
        
        # Create main hand weapon card
        main_hand = self.equipped_weapons.get('main_hand')
        if main_hand:
            weapon_name = main_hand.get('name', 'Weapon')
            hit_bonus = self._calculate_hit_bonus(main_hand, 'main_hand')
            damage = self._format_damage(main_hand)
            description = f"+{hit_bonus} to hit, {damage} damage"
            
            card = ActionCard(ActionType.ATTACK_MAIN_HAND, weapon_name, weapon_name, description)
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.ATTACK_MAIN_HAND] = card
        
        # Create off-hand weapon card
        off_hand = self.equipped_weapons.get('off_hand')
        if off_hand and off_hand.get('item_type') == 'weapon':
            weapon_name = off_hand.get('name', 'Off-hand')
            hit_bonus = self._calculate_hit_bonus(off_hand, 'off_hand')
            damage = self._format_damage(off_hand, is_off_hand=True)
            description = f"+{hit_bonus} to hit, {damage} damage"
            
            card = ActionCard(ActionType.ATTACK_OFF_HAND, weapon_name, f"{weapon_name} (Off)", description)
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.ATTACK_OFF_HAND] = card
    
    def _calculate_hit_bonus(self, weapon: Dict[str, Any], hand: str) -> int:
        """Calculate attack bonus for a weapon."""
        # Base proficiency bonus (assume level 1 = +2 for now)
        prof_bonus = 2
        
        # Get relevant ability modifier (Str for most weapons, Dex for finesse)
        weapon_props = weapon.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            # Use higher of Str or Dex for finesse weapons
            str_mod = (self.character_context.get('strength', 10) - 10) // 2
            dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        elif 'ranged' in weapon_props or weapon.get('damage_type') == 'ranged':
            # Ranged weapons use Dex
            ability_mod = (self.character_context.get('dexterity', 10) - 10) // 2
        else:
            # Melee weapons use Str
            ability_mod = (self.character_context.get('strength', 10) - 10) // 2
        
        # Magic weapon bonus
        magic_bonus = weapon.get('attack_bonus', 0)
        
        return prof_bonus + ability_mod + magic_bonus
    
    def _format_damage(self, weapon: Dict[str, Any], is_off_hand: bool = False) -> str:
        """Format weapon damage string."""
        damage_dice = weapon.get('damage_dice', '1d4')
        damage_type = weapon.get('damage_type', 'slashing')
        
        # Get ability modifier for damage
        weapon_props = weapon.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            str_mod = (self.character_context.get('strength', 10) - 10) // 2
            dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        elif 'ranged' in weapon_props or weapon.get('damage_type') == 'ranged':
            ability_mod = (self.character_context.get('dexterity', 10) - 10) // 2
        else:
            ability_mod = (self.character_context.get('strength', 10) - 10) // 2
        
        # Off-hand attacks don't add ability modifier to damage (unless Two Weapon Fighting)
        if is_off_hand:
            ability_mod = 0  # Simplified - would check for Two Weapon Fighting feat
        
        # Magic weapon damage bonus
        magic_bonus = weapon.get('damage_bonus', 0)
        total_bonus = ability_mod + magic_bonus
        
        if total_bonus > 0:
            return f"{damage_dice}+{total_bonus} {damage_type}"
        elif total_bonus < 0:
            return f"{damage_dice}{total_bonus} {damage_type}"
        else:
            return f"{damage_dice} {damage_type}"
    
    def _apply_styles(self):
        """Apply dark theme styling to action panel components."""
        style_sheet = """
        ActionPanel {
            background-color: #1a1a1a;
        }
        
        QFrame#headerFrame {
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QLabel#titleLabel {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
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
        if self.current_category == ActionCategory.COMBAT:
            # Combat: weapon attacks + other combat actions
            combat_actions = []
            
            # Add weapon attacks if they exist
            if ActionType.ATTACK_MAIN_HAND in self.action_cards:
                combat_actions.append(ActionType.ATTACK_MAIN_HAND)
            if ActionType.ATTACK_OFF_HAND in self.action_cards:
                combat_actions.append(ActionType.ATTACK_OFF_HAND)
            
            # Add other combat actions
            combat_actions.extend([ActionType.CAST_SPELL, ActionType.USE_ITEM, ActionType.DODGE])
            
            for action_type in combat_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
                    
        elif self.current_category == ActionCategory.MOVEMENT:
            movement_actions = [ActionType.MOVE, ActionType.DASH, ActionType.HIDE]
            for action_type in movement_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
                    
        elif self.current_category == ActionCategory.BONUS:
            bonus_actions = [ActionType.SEARCH, ActionType.INVESTIGATE, ActionType.REST]
            for action_type in bonus_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
                    
        elif self.current_category == ActionCategory.FREE:
            free_actions = [ActionType.INTERACT]
            for action_type in free_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
                    
        elif self.current_category == ActionCategory.REACTION:
            reaction_actions = [ActionType.OPPORTUNITY]
            for action_type in reaction_actions:
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
            
            # For attack actions, add target monster if available
            if action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
                if self.target_monster_id:
                    full_context['target_monster_id'] = self.target_monster_id
                    
                    # Trigger the attack flow
                    self._execute_attack(action_type, full_context)
                else:
                    # No target selected, just emit the signal as before
                    self.action_triggered.emit(action_type, full_context)
                    return
            else:
                # Non-attack actions proceed normally
                # Start cooldown if applicable
                cooldown = self._get_action_cooldown(action_type)
                if cooldown > 0:
                    self.action_cooldowns[action_type] = cooldown
                    self.action_cards[action_type].set_cooldown(cooldown)
                
                # Emit signal
                self.action_triggered.emit(action_type, full_context)
                
                # Update action economy
                self._update_action_economy(action_type)
    
    def _execute_attack(self, action_type: ActionType, context: Dict[str, Any]):
        """Execute an attack against the targeted monster."""
        target_id = context.get('target_monster_id')
        weapon_name = context.get('name', 'weapon')
        
        # Get encounter panel to access the monster
        encounter_panel = self._get_encounter_panel()
        if not encounter_panel:
            print("Could not find encounter panel for attack execution")
            return
        
        target_monster = encounter_panel.get_selected_monster()
        if not target_monster:
            print(f"Target monster {target_id} not found")
            return
        
        # TODO: Roll initiative first if this is the start of combat
        # For now, just proceed with the attack
        
        # Make attack roll
        attack_roll = self._roll_attack(context)
        target_ac = 12  # TODO: Get from monster data, for now assume AC 12
        
        hit = attack_roll >= target_ac
        
        if hit:
            # Roll damage
            damage = self._roll_damage(context)
            
            # Apply damage to monster
            encounter_panel._apply_damage_to_monster(target_id, damage)
            
            # Log the attack
            self._log_attack_result(True, weapon_name, target_monster.monster_name, 
                                  attack_roll, target_ac, damage)
        else:
            # Attack missed
            self._log_attack_result(False, weapon_name, target_monster.monster_name, 
                                  attack_roll, target_ac, 0)
        
        # Start cooldown and update action economy
        cooldown = self._get_action_cooldown(action_type)
        if cooldown > 0:
            self.action_cooldowns[action_type] = cooldown
            self.action_cards[action_type].set_cooldown(cooldown)
        
        self._update_action_economy(action_type)
    
    def _get_encounter_panel(self):
        """Get the encounter panel from the main window."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'encounter_pane'):
                    return parent.encounter_pane
                parent = parent.parent()
            return None
        except Exception as e:
            print(f"Error finding encounter panel: {e}")
            return None
    
    def _roll_attack(self, context: Dict[str, Any]) -> int:
        """Roll an attack roll (d20 + modifiers)."""
        import random
        base_roll = random.randint(1, 20)
        
        # Get attack bonus from context or calculate it
        attack_bonus = context.get('attack_bonus', 2)  # Default +2 for level 1
        
        return base_roll + attack_bonus
    
    def _roll_damage(self, context: Dict[str, Any]) -> int:
        """Roll damage dice."""
        import random
        
        # Get damage from context or use default
        damage_dice = context.get('damage_dice', '1d6')  # Default 1d6
        
        # Simple damage parsing - just handle basic cases like "1d6+2"
        if 'd' in damage_dice:
            if '+' in damage_dice:
                dice_part, bonus_part = damage_dice.split('+')
                bonus = int(bonus_part.strip())
            else:
                dice_part = damage_dice
                bonus = 0
            
            num_dice, die_size = dice_part.split('d')
            num_dice = int(num_dice)
            die_size = int(die_size)
            
            total = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus
            return max(1, total)  # Minimum 1 damage
        else:
            return int(damage_dice) if damage_dice.isdigit() else 1
    
    def _log_attack_result(self, hit: bool, weapon: str, target: str, attack_roll: int, target_ac: int, damage: int):
        """Log the result of an attack."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    if hit:
                        parent.log_panel.log_combat(
                            f"⚔️ {weapon} hits {target}! (rolled {attack_roll} vs AC {target_ac}) for {damage} damage"
                        )
                    else:
                        parent.log_panel.log_combat(
                            f"⚔️ {weapon} misses {target}! (rolled {attack_roll} vs AC {target_ac})"
                        )
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log attack: {e}")
    
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
            ActionType.ATTACK_MAIN_HAND: "action",
            ActionType.ATTACK_OFF_HAND: "bonus_action",
            ActionType.CAST_SPELL: "action", 
            ActionType.USE_ITEM: "action",
            ActionType.MOVE: "movement",
            ActionType.DASH: "action",
            ActionType.DODGE: "action",
            ActionType.SEARCH: "bonus_action",
            ActionType.INVESTIGATE: "action",
            ActionType.INTERACT: "free",
            ActionType.HIDE: "action",
            ActionType.REST: "special",
            ActionType.OPPORTUNITY: "reaction"
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
        # Turn label removed - just enable/disable cards
        # Enable/disable all cards based on turn
        for card in self.action_cards.values():
            card.setEnabled(active)
    
    def reset_action_economy(self):
        """Reset action economy for a new turn."""
        # Action economy display removed - just track internally
        pass
    
    def update_theme(self, theme_name: str):
        """Update all action cards to use the specified theme."""
        for card in self.action_cards.values():
            card.update_theme_styles(theme_name)
    
    def load_character_equipment(self, equipped_items: Dict[str, Any], character_stats: Dict[str, Any]):
        """Load character equipment and stats to create weapon cards."""
        self.equipped_weapons = equipped_items.copy()
        self.character_context.update(character_stats)
        
        # Recreate weapon cards with new equipment
        self._create_weapon_cards()
        
        # Update current theme for new cards
        if hasattr(self.parent(), 'current_theme'):
            theme = getattr(self.parent(), 'current_theme', 'dark')
            for action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
                if action_type in self.action_cards:
                    self.action_cards[action_type].update_theme_styles(theme)
        
        # Refresh visible cards
        self._update_visible_cards()
    
    def set_target_monster(self, monster_id: str):
        """Set the target monster for attacks."""
        self.target_monster_id = monster_id
        
        # Update action cards to show they have a target
        self._update_card_availability()


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
        # Default to dark theme styles
        self.update_theme_styles("dark")
    
    def update_theme_styles(self, theme_name: str):
        """Update styling based on theme."""
        if theme_name == "light":
            # Light theme colors
            card_bg = "#d4b896"        # surface color from light theme
            card_border = "#a0673f"    # button color from light theme
            card_border_hover = "#5c8b7a"  # accent_tertiary from light theme
            icon_bg = "#e8c5a0"        # background color from light theme
            name_color = "#4a3528"     # Very dark text from light theme
            desc_color = "#6b4d3a"     # Secondary text from light theme
            button_bg = "#a0673f"      # button color from light theme
            button_hover = "#b8784a"   # button_hover from light theme
            button_pressed = "#8b5a3c" # accent_primary from light theme
            button_text = "#ffffff"    # White text on colored buttons
            button_disabled_bg = "#c4a484"  # Lighter surface color
            button_disabled_text = "#8b7355"  # Darker secondary text
            cooldown_border = "#a0673f"
            cooldown_bg = "#e8c5a0"
            cooldown_chunk = "#d4956b"  # accent_quaternary from light theme
        else:
            # Dark theme colors (original)
            card_bg = "#2d2d2d"
            card_border = "#555555"
            card_border_hover = "#4a90e2"
            icon_bg = "#333333"
            name_color = "#ffffff"
            desc_color = "#cccccc"
            button_bg = "#4a90e2"
            button_hover = "#6ab0ff"
            button_pressed = "#3a80d2"
            button_text = "#ffffff"
            button_disabled_bg = "#555555"
            button_disabled_text = "#888888"
            cooldown_border = "#666666"
            cooldown_bg = "#1a1a1a"
            cooldown_chunk = "#ff6b6b"
        
        self.setStyleSheet(f"""
        ActionCard {{
            background-color: {card_bg};
            border: 2px solid {card_border};
            border-radius: 8px;
        }}
        
        ActionCard:hover {{
            border-color: {card_border_hover};
        }}
        
        QLabel#iconLabel {{
            font-size: 18px;
            background-color: {icon_bg};
            border-radius: 20px;
            min-height: 40px;
            max-height: 40px;
            font-weight: bold;
        }}
        
        QLabel#nameLabel {{
            color: {name_color};
            font-size: 12px;
            font-weight: bold;
        }}
        
        QLabel#descLabel {{
            color: {desc_color};
            font-size: 10px;
        }}
        
        QPushButton#actionButton {{
            background-color: {button_bg};
            color: {button_text};
            border: none;
            border-radius: 4px;
            padding: 6px;
            font-weight: bold;
            font-size: 11px;
        }}
        
        QPushButton#actionButton:hover {{
            background-color: {button_hover};
        }}
        
        QPushButton#actionButton:pressed {{
            background-color: {button_pressed};
        }}
        
        QPushButton#actionButton:disabled {{
            background-color: {button_disabled_bg};
            color: {button_disabled_text};
        }}
        
        QProgressBar#cooldownBar {{
            border: 1px solid {cooldown_border};
            border-radius: 2px;
            text-align: center;
            background-color: {cooldown_bg};
            max-height: 12px;
        }}
        
        QProgressBar#cooldownBar::chunk {{
            background-color: {cooldown_chunk};
            border-radius: 1px;
        }}
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