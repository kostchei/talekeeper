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
    
    # Class Feature Actions
    SECOND_WIND = "second_wind"
    ACTION_SURGE = "action_surge"
    FIGHTING_STYLE = "fighting_style"
    
    # Weapon Mastery Actions
    NICK_MASTERY = "nick_mastery"
    CLEAVE_MASTERY = "cleave_mastery"


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
        self.character_features = {}  # Character class features (Fighting Style, etc.)
        self.equipped_weapons = {}  # Store equipped weapon data
        self.target_monster_id = None  # Currently targeted monster for attacks
        
        # Action Economy Integration - NEW
        self.current_combat_session = None  # Current combat session for action economy
        self.character_id = None  # Current character ID for action tracking
        self.action_economy_enabled = True  # Toggle for action economy enforcement
        
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
        
        # Action Economy Status Display - NEW
        self.economy_status_label = QLabel("Action: ✓ | Bonus: ✓ | Reaction: ✓")
        self.economy_status_label.setObjectName("economyStatusLabel")
        self.economy_status_label.setVisible(False)  # Hidden until combat starts
        header_layout.addWidget(self.economy_status_label)
        
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
            # Store weapon data in the card for damage calculations
            card.weapon_data = main_hand
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
            # Store weapon data in the card for damage calculations
            card.weapon_data = off_hand
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.ATTACK_OFF_HAND] = card
    
    def _create_feature_cards(self):
        """Create action cards for character features like Second Wind."""
        if not hasattr(self, 'character_features') or not self.character_features:
            return
        
        # Remove existing feature cards
        feature_action_types = [ActionType.SECOND_WIND]
        for action_id in feature_action_types:
            if action_id in self.action_cards:
                self.action_cards[action_id].deleteLater()
                del self.action_cards[action_id]
        
        # Create Second Wind card if character has it
        print(f"DEBUG: Character features for Second Wind check: {list(self.character_features.keys())}")
        if 'Second Wind' in self.character_features:
            feature = self.character_features['Second Wind']
            level = self.character_context.get('level', 1)
            healing = f"1d10+{level}"
            description = f"Regain {healing} hit points (Short Rest recharge)"
            
            card = ActionCard(ActionType.SECOND_WIND, "❤️", "Second Wind", description)
            card.feature_data = feature
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.SECOND_WIND] = card
        
        
        # Create Weapon Mastery cards based on character's selected masteries
        selected_masteries = self.character_context.get('weapon_masteries', [])
        if selected_masteries:
            weapon_mastery_details = {
                "Cleave": "Attack second creature within 5 feet",
                "Graze": "Deal ability mod damage on miss",
                "Nick": "Make additional attack with same weapon",
                "Push": "Push target up to 10 feet away",
                "Sap": "Target has disadvantage on next attack",
                "Slow": "Reduce target's speed by 10 feet",
                "Topple": "Force Constitution save or prone",
                "Vex": "Gain advantage on next attack vs target"
            }
            
            # Create cards for Nick and Cleave masteries (bonus actions)
            if "Nick" in selected_masteries:
                card = ActionCard(ActionType.NICK_MASTERY, "🗡️", "Nick Mastery", weapon_mastery_details["Nick"])
                card.feature_data = {'type': 'weapon_mastery', 'name': 'Nick'}
                card.action_triggered.connect(self._trigger_feature_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[ActionType.NICK_MASTERY] = card
            
            if "Cleave" in selected_masteries:
                card = ActionCard(ActionType.CLEAVE_MASTERY, "🗡️", "Cleave Mastery", weapon_mastery_details["Cleave"])
                card.feature_data = {'type': 'weapon_mastery', 'name': 'Cleave'}
                card.action_triggered.connect(self._trigger_feature_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[ActionType.CLEAVE_MASTERY] = card
    
    def _trigger_feature_action(self, action_type):
        """Handle feature-based action triggers."""
        if action_type == ActionType.SECOND_WIND or action_type == 1000:  # Handle both enum and legacy ID
            # Check if Second Wind is available first
            print("DEBUG: Using Second Wind")
            uses_remaining = self._get_ability_uses_remaining("Second Wind")
            print(f"DEBUG: Second Wind uses before check: {uses_remaining}")
            
            if uses_remaining <= 0:
                # Try to initialize for existing characters
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'game_engine'):
                        character = parent.game_engine.current_character
                        if character and hasattr(character, 'ability_uses') and "Second Wind" not in character.ability_uses:
                            print("DEBUG: Initializing Second Wind for existing character")
                            character.ability_uses["Second Wind"] = 1
                            character.ability_uses_max["Second Wind"] = 1
                            uses_remaining = 1
                        break
                    parent = parent.parent()
                
                # If still no uses, block the action
                if uses_remaining <= 0:
                    print("DEBUG: Second Wind blocked - no uses remaining")
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"❌ Second Wind exhausted - requires Short Rest!")
                            break
                        parent = parent.parent()
                    return  # Block the action entirely
            
            level = self.character_context.get('level', 1)
            healing_roll = f"1d10+{level}"
            
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"🩹 Used Second Wind: Rolling {healing_roll} for healing")
                    break
                parent = parent.parent()
            
            # Import dice service for rolling
            from services.dice import DiceRoller
            dice_roller = DiceRoller()
            healing = dice_roller.roll(healing_roll)
            
            # Apply healing to character
            self._apply_healing_to_player(healing)
            
            # Log the healing result
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"❤️ Second Wind heals for {healing} hit points")
                    break
                parent = parent.parent()
            
            # Use ability - decrement uses remaining
            self._use_ability("Second Wind")
        
        elif action_type == ActionType.NICK_MASTERY:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"🗡️ Used Nick Mastery: Making bonus action attack with light weapon")
                    break
                parent = parent.parent()
        
        elif action_type == ActionType.CLEAVE_MASTERY:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"🗡️ Used Cleave Mastery: Making bonus action attack on second target")
                    break
                parent = parent.parent()
        
        elif action_type >= 2000 and action_type <= 2007:  # Weapon Mastery selection
            card = self.action_cards.get(action_type)
            if card and hasattr(card, 'feature_data'):
                mastery_name = card.feature_data.get('name')
                # Find parent with log_panel for logging
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_info(f"🗡️ Selected Weapon Mastery: {mastery_name}")
                        break
                    parent = parent.parent()
    
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
            
            # Add feature cards that are bonus actions (like Second Wind)
            if ActionType.SECOND_WIND in self.action_cards:  # Second Wind
                card = self.action_cards[ActionType.SECOND_WIND]
                self.cards_layout.addWidget(card)
                card.show()
            
            # Add weapon mastery bonus action cards
            if ActionType.NICK_MASTERY in self.action_cards:  # Nick mastery
                card = self.action_cards[ActionType.NICK_MASTERY]
                self.cards_layout.addWidget(card)
                card.show()
            
            if ActionType.CLEAVE_MASTERY in self.action_cards:  # Cleave mastery
                card = self.action_cards[ActionType.CLEAVE_MASTERY]
                self.cards_layout.addWidget(card)
                card.show()
                    
        elif self.current_category == ActionCategory.FREE:
            free_actions = [ActionType.INTERACT]
            for action_type in free_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
            
            # Add weapon mastery selection cards  
            for action_id in range(2000, 2008):  # Weapon Mastery cards
                if action_id in self.action_cards:
                    card = self.action_cards[action_id]
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
            
            # For attack actions, add target monster and weapon data if available
            if action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
                # Add weapon data to context
                if action_type in self.action_cards:
                    weapon_data = getattr(self.action_cards[action_type], 'weapon_data', None)
                    if weapon_data:
                        full_context.update(weapon_data)
                
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
                # Use ability if it's a limited-use ability
                if action_type in [ActionType.SECOND_WIND, ActionType.ACTION_SURGE]:
                    ability_name = "Second Wind" if action_type == ActionType.SECOND_WIND else "Action Surge"
                    self._use_ability(ability_name)
                
                # Emit signal
                self.action_triggered.emit(action_type, full_context)
                
                # Update action economy
                self._update_action_economy(action_type)
                
                # For combat actions, trigger monster counter-attacks after player's turn
                if self._is_combat_action(action_type):
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel:
                        self._trigger_monster_counter_attacks(encounter_panel)
    
    def _is_combat_action(self, action_type: ActionType) -> bool:
        """Check if an action is a combat action that should trigger monster retaliation."""
        combat_actions = {
            ActionType.CAST_SPELL,   # Casting spells in combat
            ActionType.USE_ITEM,     # Using items in combat  
            ActionType.DODGE,        # Dodging is a combat action
            ActionType.DASH,         # Dashing in combat
            ActionType.SEARCH,       # Searching in combat
            ActionType.HIDE,         # Hiding in combat
            # Note: MOVE, INVESTIGATE, INTERACT, REST are not typically combat actions
            # that would provoke attacks, but can be added if desired
        }
        return action_type in combat_actions
    
    def _execute_attack(self, action_type: ActionType, context: Dict[str, Any]):
        """Execute an attack against the targeted monster."""
        print(f"DEBUG: _execute_attack called with action_type: {action_type}")
        target_id = context.get('target_monster_id')
        weapon_name = context.get('name', 'weapon')
        print(f"DEBUG: target_id: {target_id}, weapon_name: {weapon_name}")
        
        # Get encounter panel to access the monster
        encounter_panel = self._get_encounter_panel()
        if not encounter_panel:
            print("Could not find encounter panel for attack execution")
            return
        
        target_monster = encounter_panel.get_selected_monster()
        if not target_monster:
            print(f"Target monster {target_id} not found")
            return
        
        # Roll initiative if this is the first attack (start of combat)
        self._check_and_roll_initiative(encounter_panel, context)
        
        # Make attack roll
        attack_total, attack_breakdown = self._roll_attack(context)
        target_ac = 12  # TODO: Get from monster data, for now assume AC 12
        
        hit = attack_total >= target_ac
        
        if hit:
            # Roll damage
            damage_total, damage_breakdown = self._roll_damage(context)
            
            # Apply weapon mastery effects on hit
            mastery_effects = self._apply_weapon_mastery_effects(weapon_name, attack_total, target_ac, hit=True, damage_total=damage_total, context=context)
            
            # Apply damage to monster
            encounter_panel._apply_damage_to_monster(target_id, damage_total)
            
            # Log the attack with detailed breakdown
            self._log_attack_result(True, weapon_name, target_monster.monster_name, 
                                  attack_breakdown, target_ac, damage_breakdown)
            
            # Log weapon mastery effects
            self._log_weapon_mastery_effects(mastery_effects)
            
        else:
            # Attack missed - check for Graze mastery
            mastery_effects = self._apply_weapon_mastery_effects(weapon_name, attack_total, target_ac, hit=False, damage_total=0, context=context)
            
            # Apply any miss-based damage (like Graze)
            graze_damage = mastery_effects.get('graze_damage', {}).get('damage', 0)
            if graze_damage > 0:
                encounter_panel._apply_damage_to_monster(target_id, graze_damage)
            
            # Attack missed - still show attack roll breakdown
            self._log_attack_result(False, weapon_name, target_monster.monster_name, 
                                  attack_breakdown, target_ac, None)
            
            # Log weapon mastery effects
            self._log_weapon_mastery_effects(mastery_effects)
        
        # Use ability if it's a limited-use ability
        if action_type in [ActionType.SECOND_WIND, ActionType.ACTION_SURGE]:
            ability_name = "Second Wind" if action_type == ActionType.SECOND_WIND else "Action Surge"
            self._use_ability(ability_name)
        
        self._update_action_economy(action_type)
        
        # Check if all monsters are defeated after this attack
        living_monsters_after_attack = encounter_panel.get_living_monsters()
        print(f"DEBUG: After attack, {len(living_monsters_after_attack)} monsters remaining")
        
        if not living_monsters_after_attack:
            # All monsters defeated - end combat immediately
            print(f"DEBUG: All monsters defeated, ending combat")
            self._end_combat(encounter_panel)
        else:
            # Monsters still alive, trigger counter-attacks
            print(f"DEBUG: About to trigger counter-attacks after player attack")
            self._trigger_monster_counter_attacks(encounter_panel)
    
    def _trigger_monster_counter_attacks(self, encounter_panel):
        """Trigger counter-attacks from all living monsters after player's action."""
        try:
            print(f"DEBUG: _trigger_monster_counter_attacks called, encounter_mode: {encounter_panel.encounter_mode}")
            
            # Check if we're in combat mode and have living monsters
            if encounter_panel.encounter_mode != "combat":
                print(f"DEBUG: Not in combat mode, returning")
                return
            
            living_monsters = encounter_panel.get_living_monsters()
            print(f"DEBUG: Found {len(living_monsters)} living monsters")
            for monster in living_monsters:
                print(f"DEBUG: Living monster: {monster.monster_name} ({monster.current_hit_points}/{monster.max_hit_points} HP, is_alive: {monster.is_alive})")
            
            if not living_monsters:
                # All monsters defeated - end combat
                print(f"DEBUG: No living monsters, ending combat")
                self._end_combat(encounter_panel)
                return
            
            # Load monster data for attack stats
            monster_data = self._load_monster_data()
            
            # Execute attacks from all living monsters with a small delay for readability
            if living_monsters:
                self._execute_monster_attacks_with_delay(living_monsters, monster_data, encounter_panel)
            else:
                # No monsters left - end combat immediately
                self._end_combat(encounter_panel)
            
        except Exception as e:
            print(f"Error triggering monster counter-attacks: {e}")
    
    def _execute_monster_attacks_with_delay(self, living_monsters, monster_data, encounter_panel):
        """Execute monster attacks with a small delay between each attack."""
        try:
            # Execute first monster attack immediately
            if living_monsters:
                monster_instance = living_monsters[0]
                if monster_instance.is_alive:
                    monster_stats = monster_data.get(monster_instance.monster_name, {})
                    if monster_stats:
                        self._execute_monster_attack(monster_instance, monster_stats, encounter_panel)
                
                # Queue remaining attacks with delay
                remaining_monsters = living_monsters[1:]
                if remaining_monsters:
                    # Use QTimer to schedule the next attack with a 500ms delay
                    QTimer.singleShot(500, lambda: self._continue_monster_attacks(remaining_monsters, monster_data, encounter_panel))
                else:
                    # All attacks done, start player's turn
                    QTimer.singleShot(300, self._log_player_turn_start)
            
        except Exception as e:
            print(f"Error executing monster attacks with delay: {e}")
    
    def _continue_monster_attacks(self, remaining_monsters, monster_data, encounter_panel):
        """Continue executing remaining monster attacks."""
        try:
            if remaining_monsters:
                monster_instance = remaining_monsters[0]
                if monster_instance.is_alive:
                    monster_stats = monster_data.get(monster_instance.monster_name, {})
                    if monster_stats:
                        self._execute_monster_attack(monster_instance, monster_stats, encounter_panel)
                
                # Continue with next monster
                further_remaining = remaining_monsters[1:]
                if further_remaining:
                    QTimer.singleShot(500, lambda: self._continue_monster_attacks(further_remaining, monster_data, encounter_panel))
                else:
                    # All monster attacks completed, start player's turn
                    QTimer.singleShot(300, self._log_player_turn_start)
        except Exception as e:
            print(f"Error continuing monster attacks: {e}")
    
    def _end_combat(self, encounter_panel):
        """End combat when all monsters are defeated."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("🏆 Victory! All monsters have been defeated!")
                    parent.log_panel.log_combat("⚔️ Combat has ended. You may now rest or explore.")
                    break
                parent = parent.parent()
            
            # Clear any active target selection
            self.target_monster_id = None
            
            # Clear action cooldowns (combat is over)
            self.action_cooldowns.clear()
            for card in self.action_cards.values():
                card.set_cooldown(0)
            
            # Switch encounter panel back to exploration mode
            encounter_panel.set_exploration_mode()
            
        except Exception as e:
            print(f"Error ending combat: {e}")
    
    def _log_player_turn_start(self):
        """Log that it's the player's turn again."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("⚡ Your turn! Choose your next action.")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log player turn start: {e}")
    
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
    
    def _roll_attack(self, context: Dict[str, Any]) -> tuple[int, dict]:
        """Roll an attack roll (d20 + modifiers). Returns (total, breakdown)."""
        import random
        base_roll = random.randint(1, 20)
        
        # Calculate attack bonus components
        prof_bonus = 2  # TODO: Get from character level
        
        # Get ability modifier
        weapon_props = context.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            str_mod = (context.get('strength', 10) - 10) // 2
            dex_mod = (context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
            ability_name = "STR" if str_mod >= dex_mod else "DEX"
        elif 'ranged' in weapon_props or context.get('damage_type') == 'ranged':
            ability_mod = (context.get('dexterity', 10) - 10) // 2
            ability_name = "DEX"
        else:
            ability_mod = (context.get('strength', 10) - 10) // 2
            ability_name = "STR"
        
        magic_bonus = context.get('attack_bonus', 0)
        total_bonus = prof_bonus + ability_mod + magic_bonus
        total = base_roll + total_bonus
        
        # Create breakdown for logging
        breakdown = {
            'd20_roll': base_roll,
            'proficiency': prof_bonus,
            'ability_mod': ability_mod,
            'ability_name': ability_name,
            'magic_bonus': magic_bonus,
            'total_bonus': total_bonus,
            'total': total
        }
        
        return total, breakdown
    
    def _roll_damage(self, context: Dict[str, Any]) -> tuple[int, dict]:
        """Roll damage dice with ability modifier. Returns (total, breakdown)."""
        import random
        
        # Get damage dice from context or use default
        damage_dice = context.get('damage_dice', '1d6')  # Default 1d6
        
        # Calculate ability modifier for damage
        weapon_props = context.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            str_mod = (context.get('strength', 10) - 10) // 2
            dex_mod = (context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
            ability_name = "STR" if str_mod >= dex_mod else "DEX"
        elif 'ranged' in weapon_props or context.get('damage_type') == 'ranged':
            ability_mod = (context.get('dexterity', 10) - 10) // 2
            ability_name = "DEX"
        else:
            ability_mod = (context.get('strength', 10) - 10) // 2
            ability_name = "STR"
        
        # Magic weapon damage bonus
        magic_bonus = context.get('damage_bonus', 0)
        
        # Check for Dueling fighting style bonus
        dueling_bonus = self._get_dueling_bonus(context)
        
        total_modifier = ability_mod + magic_bonus + dueling_bonus
        
        # Parse damage dice - just handle basic cases like "1d6", "2d6", etc
        if 'd' in damage_dice:
            # Handle cases like "1d6+2" (though we calculate our own modifier)
            if '+' in damage_dice or '-' in damage_dice:
                # Strip any existing modifier from dice string
                import re
                dice_part = re.split(r'[+-]', damage_dice)[0].strip()
            else:
                dice_part = damage_dice
            
            try:
                num_dice, die_size = dice_part.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                # Roll individual dice for breakdown
                dice_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
                
                # Apply Great Weapon Fighting style if applicable
                dice_rolls = self._apply_fighting_style_effects(dice_rolls, context)
                
                dice_total = sum(dice_rolls)
                total = dice_total + total_modifier
                
                # Create breakdown for logging
                breakdown = {
                    'damage_dice': damage_dice,
                    'num_dice': num_dice,
                    'die_size': die_size,
                    'dice_rolls': dice_rolls,
                    'dice_total': dice_total,
                    'ability_mod': ability_mod,
                    'ability_name': ability_name,
                    'magic_bonus': magic_bonus,
                    'dueling_bonus': dueling_bonus,
                    'total_modifier': total_modifier,
                    'total': max(1, total)  # Minimum 1 damage
                }
                
                return max(1, total), breakdown
            except (ValueError, IndexError):
                # Fallback if parsing fails
                fallback_total = max(1, total_modifier) if total_modifier > 0 else 1
                breakdown = {
                    'damage_dice': damage_dice,
                    'dice_rolls': [],
                    'dice_total': 0,
                    'ability_mod': ability_mod,
                    'ability_name': ability_name,
                    'magic_bonus': magic_bonus,
                    'total_modifier': total_modifier,
                    'total': fallback_total,
                    'error': 'Failed to parse damage dice'
                }
                return fallback_total, breakdown
        else:
            # Static damage value
            static_damage = int(damage_dice) if damage_dice.isdigit() else 1
            breakdown = {
                'damage_dice': damage_dice,
                'dice_rolls': [],
                'dice_total': static_damage,
                'ability_mod': 0,
                'ability_name': '',
                'magic_bonus': 0,
                'total_modifier': 0,
                'total': static_damage
            }
            return static_damage, breakdown
    
    def _log_attack_result(self, hit: bool, weapon: str, target: str, attack_breakdown: dict, target_ac: int, damage_breakdown: dict = None):
        """Log the result of an attack with detailed dice breakdown."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Build attack roll breakdown
                    d20 = attack_breakdown['d20_roll']
                    prof = attack_breakdown['proficiency']
                    ability = attack_breakdown['ability_mod']
                    ability_name = attack_breakdown['ability_name']
                    magic = attack_breakdown['magic_bonus']
                    total = attack_breakdown['total']
                    
                    # Build attack roll details
                    bonus_parts = []
                    if prof > 0:
                        bonus_parts.append(f"+{prof} prof")
                    if ability != 0:
                        sign = "+" if ability >= 0 else ""
                        bonus_parts.append(f"{sign}{ability} {ability_name}")
                    if magic != 0:
                        sign = "+" if magic >= 0 else ""
                        bonus_parts.append(f"{sign}{magic} magic")
                    
                    bonus_str = f" ({' '.join(bonus_parts)})" if bonus_parts else ""
                    
                    if hit and damage_breakdown:
                        # Build damage roll breakdown
                        dice_rolls = damage_breakdown['dice_rolls']
                        dice_total = damage_breakdown['dice_total']
                        dam_ability = damage_breakdown['ability_mod']
                        dam_ability_name = damage_breakdown['ability_name']
                        dam_magic = damage_breakdown['magic_bonus']
                        dam_dueling = damage_breakdown.get('dueling_bonus', 0)
                        damage_total = damage_breakdown['total']
                        
                        # Format individual dice rolls
                        if dice_rolls:
                            dice_str = f"[{', '.join(map(str, dice_rolls))}]"
                            damage_parts = []
                            if dam_ability != 0:
                                sign = "+" if dam_ability >= 0 else ""
                                damage_parts.append(f"{sign}{dam_ability} {dam_ability_name}")
                            if dam_magic != 0:
                                sign = "+" if dam_magic >= 0 else ""
                                damage_parts.append(f"{sign}{dam_magic} magic")
                            if dam_dueling != 0:
                                sign = "+" if dam_dueling >= 0 else ""
                                damage_parts.append(f"{sign}{dam_dueling} dueling")
                            
                            damage_bonus_str = f" ({' '.join(damage_parts)})" if damage_parts else ""
                            
                            parent.log_panel.log_combat(
                                f"⚔️ {weapon} hits {target}! Attack: d20({d20}){bonus_str} = {total} vs AC {target_ac}"
                            )
                            parent.log_panel.log_combat(
                                f"💥 Damage: {dice_str} = {dice_total}{damage_bonus_str} = {damage_total} damage"
                            )
                        else:
                            parent.log_panel.log_combat(
                                f"⚔️ {weapon} hits {target}! Attack: d20({d20}){bonus_str} = {total} vs AC {target_ac} for {damage_total} damage"
                            )
                    else:
                        # Miss - just show attack roll
                        parent.log_panel.log_combat(
                            f"⚔️ {weapon} misses {target}! Attack: d20({d20}){bonus_str} = {total} vs AC {target_ac}"
                        )
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log attack: {e}")
    
    def _check_and_roll_initiative(self, encounter_panel, context: Dict[str, Any]):
        """Check if initiative needs to be rolled and roll it."""
        try:
            # Check if encounter has initiative rolled already
            current_encounter = getattr(encounter_panel, 'current_encounter', None)
            if not current_encounter or current_encounter.initiative_rolled:
                return  # Initiative already handled
            
            # Get player DEX modifier for initiative
            player_dex_mod = (context.get('dexterity', 10) - 10) // 2
            
            # Get monster instances and monster data
            monster_instances = list(getattr(encounter_panel, 'encounter_instances', {}).values())
            
            # Load monster data from monsters_full.json for DEX stats
            monster_data = self._load_monster_data()
            
            # Roll initiative for everyone
            player_initiative = current_encounter.roll_initiative(
                player_dex_mod, monster_instances, monster_data
            )
            
            # Get initiative order
            initiative_order = current_encounter.get_initiative_order(monster_instances)
            
            # Log initiative results
            self._log_initiative_results(player_initiative, initiative_order, player_dex_mod)
            
            # Start combat officially
            current_encounter.start_combat()
            
            # Switch encounter panel to combat mode
            encounter_panel.set_combat_mode()
            
            # Check if player goes first - if not, execute monster attacks first
            if initiative_order and initiative_order[0]['type'] == 'monster':
                self._execute_monster_turns_before_player(encounter_panel, initiative_order, monster_data)
            
        except Exception as e:
            print(f"Error rolling initiative: {e}")
    
    def _load_monster_data(self) -> Dict[str, Dict]:
        """Load monster data from monsters_full.json for stats lookups."""
        try:
            import json
            from pathlib import Path
            
            # Get project root and load monster data
            project_root = Path(__file__).parent.parent
            monsters_file = project_root / "data" / "monsters_full.json"
            
            if monsters_file.exists():
                with open(monsters_file, 'r') as f:
                    data = json.load(f)
                    
                # Create lookup dict by monster name
                monster_lookup = {}
                for monster in data.get('monster', []):
                    monster_lookup[monster['name']] = monster
                
                return monster_lookup
            else:
                print(f"Monster data file not found: {monsters_file}")
                return {}
                
        except Exception as e:
            print(f"Error loading monster data: {e}")
            return {}
    
    def _log_initiative_results(self, player_initiative: int, initiative_order: list, player_dex_mod: int):
        """Log the initiative results to show turn order."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Log initiative rolling
                    parent.log_panel.log_combat("🎲 Rolling initiative for combat!")
                    
                    # Log player initiative
                    d20_roll = player_initiative - player_dex_mod
                    dex_bonus_str = f"+{player_dex_mod}" if player_dex_mod >= 0 else str(player_dex_mod)
                    parent.log_panel.log_combat(f"🎯 Player initiative: d20({d20_roll}) {dex_bonus_str} DEX = {player_initiative}")
                    
                    # Log monster initiatives
                    for entry in initiative_order:
                        if entry['type'] == 'monster':
                            parent.log_panel.log_combat(f"👹 {entry['name']} initiative: {entry['initiative']}")
                    
                    # Log turn order
                    turn_order = " → ".join([f"{entry['name']} ({entry['initiative']})" for entry in initiative_order])
                    parent.log_panel.log_combat(f"⚡ Turn Order: {turn_order}")
                    
                    # Announce who goes first
                    if initiative_order:
                        first_actor = initiative_order[0]
                        if first_actor['type'] == 'player':
                            parent.log_panel.log_combat("✅ Player goes first!")
                        else:
                            parent.log_panel.log_combat(f"⚠️ {first_actor['name']} goes first!")
                    
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Could not log initiative: {e}")
    
    def _execute_monster_turns_before_player(self, encounter_panel, initiative_order: list, monster_data: dict):
        """Execute monster attacks for all monsters that go before the player."""
        try:
            for entry in initiative_order:
                if entry['type'] == 'player':
                    break  # Stop when we reach player turn
                
                if entry['type'] == 'monster':
                    monster_id = entry['id']
                    monster_name = entry['name']
                    
                    # Get monster instance and stats
                    monster_instance = encounter_panel.encounter_instances.get(monster_id)
                    monster_stats = monster_data.get(monster_name, {})
                    
                    if monster_instance and monster_instance.is_alive and monster_stats:
                        self._execute_monster_attack(monster_instance, monster_stats, encounter_panel)
                        
        except Exception as e:
            print(f"Error executing monster turns: {e}")
    
    def _execute_monster_attack(self, monster_instance, monster_stats: dict, encounter_panel):
        """Execute a single monster's attack against the player."""
        try:
            # Get monster's first action (usually their main attack)
            actions = monster_stats.get('action', [])
            if not actions:
                return  # No attacks available
            
            main_action = actions[0]  # Use first action
            action_name = main_action.get('name', 'Attack')
            
            # Parse the attack from the action entry
            attack_info = self._parse_monster_attack(main_action, monster_stats)
            if not attack_info:
                return
            
            # Roll monster's attack
            import random
            attack_roll = random.randint(1, 20) + attack_info['hit_bonus']
            
            # Get player's actual AC from character data
            player_ac = self.character_context.get('armor_class', 10)
            
            hit = attack_roll >= player_ac
            
            if hit:
                # Roll damage
                damage_total = self._roll_monster_damage(attack_info['damage_dice'], attack_info['damage_bonus'])
                
                # Apply damage to player
                self._apply_damage_to_player(damage_total, encounter_panel)
                
                # Log the attack
                self._log_monster_attack_result(True, monster_instance.monster_name, action_name, 
                                              attack_roll, player_ac, damage_total, attack_info)
            else:
                # Attack missed
                self._log_monster_attack_result(False, monster_instance.monster_name, action_name, 
                                              attack_roll, player_ac, 0, attack_info)
                
        except Exception as e:
            print(f"Error executing monster attack: {e}")
    
    def _parse_monster_attack(self, action: dict, monster_stats: dict) -> dict:
        """Parse monster attack info from action entry."""
        try:
            entries = action.get('entries', [])
            if not entries:
                return None
            
            # Parse the attack string like "{@atk mw,rw} {@hit 3} to hit, reach 5 ft. or range 20/60 ft., one target. {@h}4 ({@damage 1d6 + 1}) piercing damage"
            attack_str = entries[0]
            
            # Extract hit bonus
            hit_bonus = 0
            if '{@hit ' in attack_str:
                import re
                hit_match = re.search(r'\{@hit (\d+)\}', attack_str)
                if hit_match:
                    hit_bonus = int(hit_match.group(1))
            
            # Extract damage
            damage_dice = "1d6"
            damage_bonus = 0
            if '{@damage ' in attack_str:
                import re
                damage_match = re.search(r'\{@damage ([^}]+)\}', attack_str)
                if damage_match:
                    damage_str = damage_match.group(1)
                    # Parse "1d6 + 1" or "1d8 + 1"
                    if ' + ' in damage_str:
                        parts = damage_str.split(' + ')
                        damage_dice = parts[0]
                        damage_bonus = int(parts[1])
                    elif ' - ' in damage_str:
                        parts = damage_str.split(' - ')
                        damage_dice = parts[0]
                        damage_bonus = -int(parts[1])
                    else:
                        damage_dice = damage_str
            
            return {
                'hit_bonus': hit_bonus,
                'damage_dice': damage_dice,
                'damage_bonus': damage_bonus
            }
            
        except Exception as e:
            print(f"Error parsing monster attack: {e}")
            return None
    
    def _roll_monster_damage(self, damage_dice: str, damage_bonus: int) -> int:
        """Roll damage for monster attack."""
        import random
        
        try:
            # Parse damage dice like "1d6", "1d8", "2d6"
            if 'd' in damage_dice:
                num_dice, die_size = damage_dice.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                dice_total = sum(random.randint(1, die_size) for _ in range(num_dice))
                total = dice_total + damage_bonus
                return max(1, total)  # Minimum 1 damage
            else:
                return max(1, damage_bonus) if damage_bonus > 0 else 1
                
        except Exception as e:
            print(f"Error rolling monster damage: {e}")
            return 1
    
    def _apply_damage_to_player(self, damage: int, encounter_panel):
        """Apply damage to the player character."""
        try:
            # Get character data from encounter panel or main window
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                    character_data = parent.character_sheet.character_data
                    
                    # Apply damage to current HP
                    current_hp = character_data.get('current_hit_points', 0)
                    new_hp = max(0, current_hp - damage)
                    character_data['current_hit_points'] = new_hp
                    
                    # Update character sheet display
                    parent.character_sheet.load_character_data(character_data)
                    
                    return new_hp
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error applying damage to player: {e}")
            return 0
    
    def _apply_healing_to_player(self, healing: int):
        """Apply healing to the player character."""
        try:
            # Get character data from main window
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_sheet'):
                    if parent.character_sheet.character_data:
                        character_data = parent.character_sheet.character_data
                    else:
                        parent = parent.parent()
                        continue
                    
                    # Get current and max HP from database fields
                    current_hp = character_data.get('current_hit_points', character_data.get('hit_points_current', 0))
                    max_hp = character_data.get('max_hit_points', character_data.get('hit_points_max', 0))
                    
                    # If HP fields are missing, try to extract from character sheet display
                    if max_hp == 0:
                        hp_display = parent.character_sheet.hp_widget.value_label.text()
                        
                        # Try to parse "9/14" format
                        if '/' in hp_display:
                            try:
                                current_str, max_str = hp_display.split('/')
                                current_hp = int(current_str.strip())
                                max_hp = int(max_str.strip())
                                
                                # Update character_data with the parsed values
                                character_data['current_hit_points'] = current_hp
                                character_data['max_hit_points'] = max_hp
                                character_data['hit_points_current'] = current_hp
                                character_data['hit_points_max'] = max_hp
                                
                            except (ValueError, AttributeError):
                                return 0
                        else:
                            return 0
                    
                    # Apply healing but don't exceed max HP
                    old_hp = current_hp
                    new_hp = min(max_hp, current_hp + healing)
                    
                    # Update both field name variants for compatibility
                    character_data['current_hit_points'] = new_hp
                    character_data['hit_points_current'] = new_hp
                    
                    # Update character sheet display
                    parent.character_sheet.load_character_data(character_data)
                    
                    # Log the HP change
                    actual_healing = new_hp - old_hp
                    parent_with_log = self.parent()
                    while parent_with_log:
                        if hasattr(parent_with_log, 'log_panel'):
                            if actual_healing < healing:
                                # Hit max HP
                                parent_with_log.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} → {new_hp}/{max_hp} (healed {actual_healing}, max HP reached)")
                            else:
                                # Normal healing
                                parent_with_log.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} → {new_hp}/{max_hp} (healed {healing})")
                            break
                        parent_with_log = parent_with_log.parent()
                    
                    return new_hp
                parent = parent.parent()
            
            return 0
                
        except Exception as e:
            print(f"Error applying healing to player: {e}")
            return 0
    
    def _log_monster_attack_result(self, hit: bool, monster_name: str, action_name: str, 
                                  attack_roll: int, player_ac: int, damage: int, attack_info: dict):
        """Log monster attack results."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    if hit:
                        parent.log_panel.log_combat(f"👹 {monster_name} {action_name} hits! Attack: {attack_roll} vs AC {player_ac} for {damage} damage")
                    else:
                        parent.log_panel.log_combat(f"👹 {monster_name} {action_name} misses! Attack: {attack_roll} vs AC {player_ac}")
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Could not log monster attack: {e}")
    
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
        # Check cooldowns (original system)
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
            ActionType.OPPORTUNITY: "reaction",
            ActionType.SECOND_WIND: "bonus_action",
            ActionType.NICK_MASTERY: "bonus_action",
            ActionType.CLEAVE_MASTERY: "bonus_action"
        }
        
        cost_type = action_costs.get(action_type, "free")
        
        # In a real implementation, track available actions per turn
        # For now, assume all actions are available
        return True
    
    def _get_unavailability_reasons(self, action_type: ActionType) -> List[str]:
        """Get reasons why an action is unavailable."""
        reasons = []
        
        # Check ability uses for rest-based abilities
        if action_type == ActionType.SECOND_WIND:
            uses = self._get_ability_uses_remaining("Second Wind")
            if uses <= 0:
                reasons.append("No uses remaining (requires Short Rest)")
        elif action_type == ActionType.ACTION_SURGE:
            uses = self._get_ability_uses_remaining("Action Surge")
            if uses <= 0:
                reasons.append("No uses remaining (requires Short Rest)")
        
        return reasons
    
    def _get_ability_uses_remaining(self, ability_name: str) -> int:
        """Get remaining uses for an ability."""
        # Get current character from parent
        parent = self.parent()
        while parent:
            if hasattr(parent, 'game_engine'):
                game_engine = parent.game_engine
                character = game_engine.current_character
                if character:
                    uses = character.ability_uses.get(ability_name, 0)
                    return uses
                break
            parent = parent.parent()
        return 0
    
    def _use_ability(self, ability_name: str):
        """Use an ability - decrement uses remaining."""
        print(f"DEBUG: _use_ability called for {ability_name}")
        # Get current character from parent
        parent = self.parent()
        while parent:
            if hasattr(parent, 'game_engine'):
                game_engine = parent.game_engine
                character = game_engine.current_character
                if character:
                    print(f"DEBUG: Found character, checking {ability_name}")
                    if not hasattr(character, 'ability_uses'):
                        print(f"DEBUG: Character missing ability_uses field, initializing...")
                        character.ability_uses = {}
                        character.ability_uses_max = {}
                    
                    # Initialize Fighter abilities for existing characters that don't have them
                    if ability_name == "Second Wind" and ability_name not in character.ability_uses:
                        print(f"DEBUG: Initializing Second Wind for existing character")
                        character.ability_uses["Second Wind"] = 1
                        character.ability_uses_max["Second Wind"] = 1
                    elif ability_name == "Action Surge" and ability_name not in character.ability_uses:
                        print(f"DEBUG: Initializing Action Surge for existing character")
                        character.ability_uses["Action Surge"] = 1  
                        character.ability_uses_max["Action Surge"] = 1
                    
                    current_uses = character.ability_uses.get(ability_name, 0)
                    print(f"DEBUG: Current uses of {ability_name}: {current_uses}")
                    
                    if current_uses > 0:
                        character.ability_uses[ability_name] = current_uses - 1
                        print(f"DEBUG: Decremented {ability_name} to {character.ability_uses[ability_name]}")
                        # Save character (save the whole game state)
                        try:
                            game_engine.save_game_sync()
                            print(f"DEBUG: Game saved successfully")
                        except Exception as e:
                            print(f"DEBUG: Save failed: {e}")
                        # Update action card display
                        self._refresh_action_availability()
                    else:
                        print(f"DEBUG: {ability_name} has no uses remaining ({current_uses})")
                break
            parent = parent.parent()
    
    def _refresh_action_availability(self):
        """Refresh the availability state of all action cards."""
        for action_type, card in self.action_cards.items():
            available = self._is_action_available(action_type)
            card.set_available(available)
    
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
    
    def _clear_feature_cards(self):
        """Clear all feature-based action cards (like Second Wind)."""
        feature_action_types = [ActionType.SECOND_WIND, ActionType.ACTION_SURGE]
        
        for action_type in feature_action_types:
            if action_type in self.action_cards:
                self.action_cards[action_type].deleteLater()
                del self.action_cards[action_type]
    
    def load_character_features(self, character_features: Dict[str, Any]):
        """Load character features and create feature-based action cards."""
        # Clear existing feature cards first
        self._clear_feature_cards()
        
        self.character_features = character_features or {}
        
        # Create feature-based action cards
        self._create_feature_cards()
        
        # Refresh visible cards
        self._update_visible_cards()
    
    def load_character_feats(self, character_feats: List[str]):
        """Load character feats for fighting style and other feat-based effects."""
        if not hasattr(self, 'character_context'):
            self.character_context = {}
        
        self.character_context['feats'] = character_feats or []
        self.character_feats = character_feats or []  # Also store directly for easy access
    
    def load_weapon_masteries(self, weapon_masteries: List[str]):
        """Load character weapon masteries."""
        self.character_weapon_masteries = weapon_masteries or []
        # Also store in character context for easy access
        if not hasattr(self, 'character_context'):
            self.character_context = {}
        self.character_context['weapon_masteries'] = weapon_masteries or []
    
    def set_target_monster(self, monster_id: str):
        """Set the target monster for attacks."""
        self.target_monster_id = monster_id
        
        # Update action cards to show they have a target
        self._update_card_availability()
    
    
    def _log_weapon_mastery_effects(self, mastery_effects: Dict[str, Any]):
        """Log weapon mastery effects to combat log."""
        if not mastery_effects:
            return
        
        # Find parent with log_panel for logging
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                for effect_name, effect_data in mastery_effects.items():
                    if isinstance(effect_data, dict) and 'description' in effect_data:
                        description = effect_data['description']
                        
                        if 'damage' in effect_data:
                            damage = effect_data['damage']
                            parent.log_panel.log_combat(f"🗡️ {description} - {damage} damage")
                        elif 'save_dc' in effect_data:
                            save_dc = effect_data['save_dc']
                            parent.log_panel.log_combat(f"🗡️ {description} - DC {save_dc}")
                        else:
                            parent.log_panel.log_combat(f"🗡️ {description}")
                break
            parent = parent.parent()
    
    def _get_dueling_bonus(self, context: Dict[str, Any]) -> int:
        """Check if character gets Dueling fighting style bonus (+2 damage)."""
        if not self.character_context:
            return 0
        
        # Check if character has Dueling fighting style
        character_feats = getattr(self, 'character_feats', [])
        if "Dueling" not in character_feats:
            return 0
        
        # Check weapon requirements: one-handed melee weapon
        weapon_props = context.get('weapon_properties', [])
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        
        # Must not be two-handed or ranged
        is_two_handed = 'two-handed' in weapon_props_lower
        is_ranged = 'ranged' in weapon_props_lower or context.get('damage_type') == 'ranged'
        
        if is_two_handed or is_ranged:
            return 0
        
        # Check if off-hand is free (no off-hand weapon or shield)
        # With the new system, two-handed weapons occupy both slots, so this check works perfectly
        off_hand_item = self.character_context.get('equipment_off_hand')
        shield_item = self.character_context.get('equipment_shield')
        
        if off_hand_item or shield_item:
            return 0
        
        # Log the Dueling bonus application
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"⚔️ Dueling: +2 damage (one-handed weapon with free off-hand)")
                break
            parent = parent.parent()
        
        return 2
    
    def _apply_fighting_style_effects(self, dice_rolls: list, context: Dict[str, Any]) -> list:
        """Apply fighting style effects to damage dice rolls."""
        if not self.character_context:
            return dice_rolls
        
        # Check if character has Great Weapon Fighting style (stored in feats array)
        character_feats = getattr(self, 'character_feats', [])
        
        if "Great Weapon Fighting" not in character_feats:
            return dice_rolls
        
        # Check if weapon qualifies for Great Weapon Fighting
        weapon_props = context.get('weapon_properties', [])
        # Convert to lowercase for comparison
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        is_two_handed = 'two-handed' in weapon_props_lower
        is_versatile = 'versatile' in weapon_props_lower
        
        if not (is_two_handed or is_versatile):
            return dice_rolls
        
        # Apply Great Weapon Fighting: treat 1s and 2s as 3s
        modified_rolls = []
        reroll_applied = False
        
        for roll in dice_rolls:
            if roll <= 2:
                modified_rolls.append(3)
                reroll_applied = True
            else:
                modified_rolls.append(roll)
        
        # Log the fighting style effect if applied
        if reroll_applied:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    original_str = ', '.join(map(str, dice_rolls))
                    modified_str = ', '.join(map(str, modified_rolls))
                    parent.log_panel.log_combat(f"⚔️ Great Weapon Fighting: [{original_str}] → [{modified_str}] (1s and 2s become 3s)")
                    break
                parent = parent.parent()
        
        return modified_rolls
    
    def _apply_weapon_mastery_effects(self, weapon_name: str, attack_total: int, target_ac: int, hit: bool, damage_total: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply weapon mastery effects using simplified database-driven logic."""
        if not self.character_context:
            return {}
        
        # Step 1: Check if weapon has mastery
        mastery_name = self._get_weapon_mastery(weapon_name)
        print(f"[DEBUG] Weapon {weapon_name} has mastery: {mastery_name}")
        if not mastery_name:
            return {}
        
        # Step 2: Check if character has Weapon Mastery feature
        if not self._character_has_weapon_mastery_feature():
            print(f"[DEBUG] Character lacks Weapon Mastery feature - no mastery effects")
            return {}
        
        # Step 3: Apply the mastery effect
        print(f"[DEBUG] Applying {mastery_name} mastery for {weapon_name} (hit: {hit})")
        return self._apply_mastery_effect(mastery_name, hit, context)
    
    def _get_weapon_mastery(self, weapon_name: str) -> str:
        """Get weapon's mastery property from database."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mastery_name FROM weapon_mastery_properties 
                WHERE weapon_name = ?
            """, (weapon_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"Error getting weapon mastery for {weapon_name}: {e}")
            return None
    
    def _character_has_weapon_mastery_feature(self) -> bool:
        """Check if character has Weapon Mastery feature."""
        character_id = self.character_context.get('id')
        if not character_id:
            print(f"[DEBUG] No character ID found")
            return False
        
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM character_features 
                WHERE character_id = ? AND feature_name = 'Weapon Mastery'
            """, (character_id,))
            
            has_mastery = cursor.fetchone() is not None
            conn.close()
            
            print(f"[DEBUG] Character {character_id} has Weapon Mastery feature: {has_mastery}")
            return has_mastery
            
        except Exception as e:
            print(f"[DEBUG] Error checking Weapon Mastery feature: {e}")
            return False
    
    def _apply_mastery_effect(self, mastery_name: str, hit: bool, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the specific mastery effect."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT trigger_type, description, requires_save, save_ability
                FROM weapon_masteries WHERE name = ?
            """, (mastery_name,))
            
            mastery_data = cursor.fetchone()
            conn.close()
            
            if not mastery_data:
                return {}
            
            trigger_type, description, requires_save, save_ability = mastery_data
            
            # Check if mastery should trigger
            should_trigger = (
                (trigger_type == 'on_hit' and hit) or
                (trigger_type == 'on_miss' and not hit) or
                (trigger_type == 'on_attack')  # Always triggers
            )
            
            if not should_trigger:
                return {}
            
            effects = {}
            
            # Apply specific mastery effects
            if mastery_name == "Graze" and not hit:
                ability_mod = context.get('strength', 10)
                ability_mod = (ability_mod - 10) // 2
                if ability_mod > 0:
                    effects['graze_damage'] = {
                        'damage': ability_mod,
                        'description': f"Graze: {ability_mod} damage on miss"
                    }
            
            elif mastery_name == "Topple" and hit:
                dc = 8 + 2 + ((context.get('strength', 10) - 10) // 2)  # 8 + prof + ability mod
                effects['topple'] = {
                    'save_dc': dc,
                    'description': f"Topple: Constitution save DC {dc} or prone"
                }
            
            elif mastery_name == "Sap" and hit:
                effects['sap'] = {
                    'description': "Sap: Target has disadvantage on next attack roll"
                }
            
            elif mastery_name == "Push" and hit:
                effects['push'] = {
                    'distance': 10,
                    'description': "Push: Target pushed up to 10 feet away"
                }
            
            elif mastery_name == "Slow" and hit:
                effects['slow'] = {
                    'speed_reduction': 10,
                    'description': "Slow: Target's speed reduced by 10 feet until start of your next turn"
                }
            
            elif mastery_name == "Vex" and hit:
                effects['vex'] = {
                    'description': "Vex: Advantage on next attack against this target"
                }
            
            elif mastery_name == "Cleave" and hit:
                effects['cleave'] = {
                    'description': "Cleave: Can attack second creature within 5 feet"
                }
            
            elif mastery_name == "Nick":
                effects['nick'] = {
                    'description': "Nick: Light weapon extra attack as part of Attack action"
                }
            
            return effects
            
        except Exception as e:
            print(f"Error applying mastery effect for {mastery_name}: {e}")
            return {}
    
    def _log_weapon_mastery_effects(self, mastery_effects: Dict[str, Any]):
        """Log weapon mastery effects to combat log."""
        if not mastery_effects:
            return
            
        try:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    for effect_name, effect_data in mastery_effects.items():
                        description = effect_data.get('description', 'Unknown mastery effect')
                        
                        if effect_name == 'graze_damage':
                            parent.log_panel.log_combat(f"🗡️ {description}")
                        elif effect_name in ['topple', 'sap', 'push', 'slow', 'vex']:
                            parent.log_panel.log_combat(f"🗡️ {description}")
                        elif effect_name in ['cleave', 'nick']:
                            parent.log_panel.log_combat(f"🗡️ {description}")
                        else:
                            parent.log_panel.log_combat(f"🗡️ {description}")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error logging mastery effects: {e}")
    
    # === ACTION ECONOMY INTEGRATION ===
    
    def set_combat_session(self, combat_session, character_id: str):
        """Set the current combat session for action economy tracking."""
        self.current_combat_session = combat_session
        self.character_id = character_id
        self._update_action_availability()
    
    def end_combat_session(self):
        """Clear combat session and reset action availability."""
        self.current_combat_session = None
        self.character_id = None
        self._update_action_availability()
    
    def _update_action_availability(self):
        """Update action card availability based on action economy."""
        if not self.action_economy_enabled or not self.current_combat_session:
            # Outside combat or action economy disabled - all actions available
            for card in self.action_cards.values():
                card.set_available(True)
            self.economy_status_label.setVisible(False)
            return
        
        # Show action economy status
        self.economy_status_label.setVisible(True)
        self._update_economy_status_display()
        
        # Check each action card against action economy
        for action_type, card in self.action_cards.items():
            available = self._is_action_available_by_economy(action_type)
            card.set_available(available)
            
            # Add economy status to card description
            if not available:
                economy_reason = self._get_economy_unavailability_reason(action_type)
                card.set_tooltip_suffix(f" ({economy_reason})")
            else:
                card.set_tooltip_suffix("")
    
    def _update_economy_status_display(self):
        """Update the action economy status display in the header."""
        if not self.current_combat_session or not self.character_id:
            return
        
        status = self.get_action_economy_status()
        if status.get("error"):
            self.economy_status_label.setText("Action Economy: Error")
            return
        
        # Create status text with visual indicators
        action_icon = "✓" if status.get("action_available", False) else "✗"
        bonus_icon = "✓" if status.get("bonus_action_available", False) else "✗"
        reaction_icon = "✓" if status.get("reaction_available", False) else "✗"
        
        round_num = status.get("current_round", 1)
        movement = status.get("movement_remaining", 30)
        
        status_text = f"R{round_num} | Action: {action_icon} | Bonus: {bonus_icon} | Reaction: {reaction_icon} | Move: {movement}ft"
        
        # Color code the status label based on active turn
        if status.get("is_active_turn", False):
            self.economy_status_label.setStyleSheet("color: #4a90e2; font-weight: bold;")
        else:
            self.economy_status_label.setStyleSheet("color: #888888;")
        
        self.economy_status_label.setText(status_text)
    
    def _is_action_available_by_economy(self, action_type: ActionType) -> bool:
        """Check if an action is available based on action economy rules."""
        if not self.current_combat_session or not self.character_id:
            return True
        
        # Map ActionType to action economy categories
        economy_type = self._map_action_to_economy_type(action_type)
        if not economy_type:
            return True  # Free actions or unmapped actions
        
        return self.current_combat_session.can_take_action(self.character_id, economy_type.value)
    
    def _map_action_to_economy_type(self, action_type: ActionType):
        """Map ActionType to ActionEconomyType."""
        from models.action_economy import ActionEconomyType
        
        # Actions that consume your main Action
        main_actions = {
            ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND, ActionType.ATTACK_UNARMED,
            ActionType.CAST_SPELL, ActionType.DASH, ActionType.DISENGAGE, ActionType.DODGE,
            ActionType.HELP, ActionType.HIDE, ActionType.SEARCH, ActionType.USE_ITEM
        }
        
        # Bonus Actions
        bonus_actions = {
            ActionType.SECOND_WIND, ActionType.CUNNING_ACTION, ActionType.HEALING_WORD,
            ActionType.SPIRITUAL_WEAPON, ActionType.HUNTER_MARK, ActionType.HEALING_POTION,
            ActionType.NICK_MASTERY, ActionType.CLEAVE_MASTERY
        }
        
        # Reactions
        reactions = {
            ActionType.OPPORTUNITY_ATTACK, ActionType.COUNTERSPELL, ActionType.SHIELD
        }
        
        if action_type in main_actions:
            return ActionEconomyType.ACTION
        elif action_type in bonus_actions:
            return ActionEconomyType.BONUS_ACTION
        elif action_type in reactions:
            return ActionEconomyType.REACTION
        else:
            return ActionEconomyType.FREE_ACTION  # Movement, object interactions, etc.
    
    def _get_economy_unavailability_reason(self, action_type: ActionType) -> str:
        """Get reason why an action is unavailable due to action economy."""
        economy_type = self._map_action_to_economy_type(action_type)
        
        if economy_type == ActionEconomyType.ACTION:
            return "Action used this turn"
        elif economy_type == ActionEconomyType.BONUS_ACTION:
            return "Bonus action used this turn"
        elif economy_type == ActionEconomyType.REACTION:
            return "Reaction used this round"
        else:
            return "Action not available"
    
    def _trigger_action_with_economy(self, action_type: ActionType, context: Dict[str, Any]):
        """Trigger an action with action economy enforcement."""
        if not self.action_economy_enabled or not self.current_combat_session:
            # No economy restrictions - just trigger the action
            self.action_triggered.emit(action_type, context)
            return
        
        # Check if action is available
        if not self._is_action_available_by_economy(action_type):
            # Action not available - show feedback
            reason = self._get_economy_unavailability_reason(action_type)
            self._show_action_unavailable_feedback(action_type, reason)
            return
        
        # Use the action through combat session
        economy_type = self._map_action_to_economy_type(action_type)
        success = self.current_combat_session.use_action(
            self.character_id, 
            economy_type.value, 
            action_type.value, 
            context
        )
        
        if success:
            # Action used successfully - trigger it and update UI
            self.action_triggered.emit(action_type, context)
            self._update_action_availability()
            
            # Log action economy usage
            self._log_action_economy_usage(action_type, economy_type)
        else:
            # This shouldn't happen if our checks are correct, but handle it
            self._show_action_unavailable_feedback(action_type, "Action failed")
    
    def _show_action_unavailable_feedback(self, action_type: ActionType, reason: str):
        """Show feedback when an action cannot be taken."""
        # Flash the action card or show tooltip
        if action_type in self.action_cards:
            card = self.action_cards[action_type]
            # You could add a flash effect here
            pass
        
        # Log to combat log
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"❌ Cannot use {action_type.value}: {reason}")
                    break
                parent = parent.parent()
        except:
            pass
    
    def _log_action_economy_usage(self, action_type: ActionType, economy_type):
        """Log action economy usage to combat log."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    economy_name = economy_type.value.replace('_', ' ').title()
                    parent.log_panel.log_combat(f"⚡ Used {economy_name}: {action_type.value}")
                    break
                parent = parent.parent()
        except:
            pass
    
    def get_action_economy_status(self) -> Dict[str, Any]:
        """Get current action economy status for UI display."""
        if not self.current_combat_session or not self.character_id:
            return {
                "in_combat": False,
                "action_available": True,
                "bonus_action_available": True,
                "reaction_available": True,
                "movement_remaining": 30
            }
        
        state = self.current_combat_session.action_economy.get_combatant_state(self.character_id)
        if not state:
            return {"in_combat": True, "error": "No action economy state found"}
        
        return {
            "in_combat": True,
            "current_round": state.current_round,
            "is_active_turn": state.is_active_turn,
            "action_available": state.action_available,
            "bonus_action_available": state.bonus_action_available,  
            "reaction_available": state.reaction_available,
            "movement_remaining": state.get_remaining_movement(),
            "actions_taken_this_turn": len(state.actions_taken_this_turn)
        }


class ActionCard(QWidget):
    """Individual action card widget."""
    
    action_triggered = pyqtSignal(ActionType, dict)  # action_type, context
    action_hovered = pyqtSignal(ActionType, str)  # action_type, description
    
    def __init__(self, action_type, icon: str, name: str, description: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        # Handle both ActionType enums and integers for backwards compatibility
        if isinstance(action_type, ActionType):
            self.action_type = action_type
        else:
            # For integer IDs, store as is for now (legacy feature cards)
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
            # Handle both ActionType enums and legacy integer IDs
            if isinstance(self.action_type, ActionType):
                self.action_triggered.emit(self.action_type, context)
            else:
                # For legacy integer IDs, we need a different approach
                # Find parent ActionPanel and call feature trigger directly
                parent = self.parent()
                while parent and not hasattr(parent, '_trigger_feature_action'):
                    parent = parent.parent()
                if parent and hasattr(parent, '_trigger_feature_action'):
                    parent._trigger_feature_action(self.action_type)
    
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
    
    def set_tooltip_suffix(self, suffix: str):
        """Add a suffix to the action card tooltip (for action economy status)."""
        base_tooltip = self.description
        if suffix:
            self.setToolTip(f"{base_tooltip}{suffix}")
        else:
            self.setToolTip(base_tooltip)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        # Only emit for ActionType enums, skip for legacy integer IDs
        if isinstance(self.action_type, ActionType):
            current_tooltip = self.toolTip() or self.description
            self.action_hovered.emit(self.action_type, current_tooltip)
        super().enterEvent(event)