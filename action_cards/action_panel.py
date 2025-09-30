"""
Action Cards Widget - Bottom panel for character actions

PyQt6 widget that provides quick access to character actions:
- Combat actions (Attack, Cast Spell, Use Item, Dodge)
- Movement actions (Move, Dash, Hide)
- Utility actions (Search, Investigate, Interact, Rest)
- Customizable action cards
- Context-sensitive action availability

Designed to match ui_plan.md specifications:
- Fixed size is determined by the active layout profile
- Horizontal card layout
- Dark theme styling
- Action cooldowns and availability
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QScrollArea, QButtonGroup,
                            QToolTip, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import re

from services.character_resources import CharacterResourceService
from services.weapon_mastery_service import WeaponMasteryService
from services.equipment_database import EquipmentDatabase
from services.weapon_attack_service import WeaponAttackService
from core.combat_manager import CombatManager
from action_cards.weapon_mastery_dialog import WeaponMasteryDialog
from action_cards.divine_smite_dialog import DivineSmiteDialog
from action_cards.lay_on_hands_dialog import LayOnHandsDialog
from action_cards.channel_divinity_dialog import ChannelDivinityDialog, create_channel_divinity_options
from ui.advantage_halo import AdvantageHalo, AdvantageResourceManager
from services.spellcasting_service import SpellcastingService
from services.spell_registry import spell_registry
from services.paladin_abilities import PaladinAbilitiesService

from ui.layout_profiles import BASELINE_PROFILE, LayoutProfile

print("DEBUG: action_panel.py module loaded/imported at line 25")

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

    # Spell Actions (dynamic spells use CAST_SPELL with spell_id in context)
    SPELL_ATTACK = "spell_attack"    # For attack spells
    SPELL_UTILITY = "spell_utility"  # For utility/buff spells
    SPELL_REACTION = "spell_reaction" # For reaction spells
    
    # Weapon Mastery Actions
    NICK_MASTERY = "nick_mastery"
    CLEAVE_MASTERY = "cleave_mastery"
    
    # Consumables
    USE_POTION = "use_potion"
    
    # Class Features
    RAGE = "rage"
    RECKLESS_ATTACK = "reckless_attack"
    SNEAK_ATTACK = "sneak_attack"  # Passive, handled automatically
    LAY_ON_HANDS = "lay_on_hands"
    CHANNEL_DIVINITY = "channel_divinity"

    # Rogue Features
    CUNNING_DASH = "cunning_dash"
    CUNNING_DISENGAGE = "cunning_disengage"
    CUNNING_HIDE = "cunning_hide"
    STEADY_AIM = "steady_aim"
    UNCANNY_DODGE = "uncanny_dodge"
    CUNNING_STRIKE_POISON = "cunning_strike_poison"
    CUNNING_STRIKE_TRIP = "cunning_strike_trip"
    CUNNING_STRIKE_WITHDRAW = "cunning_strike_withdraw"
    CUNNING_STRIKE_DAZE = "cunning_strike_daze"
    CUNNING_STRIKE_KNOCK_OUT = "cunning_strike_knock_out"
    CUNNING_STRIKE_OBSCURE = "cunning_strike_obscure"
    STROKE_OF_LUCK = "stroke_of_luck"

    # Barbarian Features
    BRUTAL_STRIKE_FORCEFUL = "brutal_strike_forceful"
    BRUTAL_STRIKE_HAMSTRING = "brutal_strike_hamstring"
    BRUTAL_STRIKE_STAGGERING = "brutal_strike_staggering"
    BRUTAL_STRIKE_SUNDERING = "brutal_strike_sundering"
    INSTINCTIVE_POUNCE = "instinctive_pounce"
    INTIMIDATING_PRESENCE = "intimidating_presence"
    RETALIATION = "retaliation"

    # Champion Features
    HEROIC_WARRIOR = "heroic_warrior"
    SURVIVOR = "survivor"
    
    # Subclass Features
    SIGNATURE_MOVE = "signature_move"  # Gladiator level 10
    FAST_HANDS = "fast_hands"  # Thief level 3 (modifies bonus actions)
    FAST_HANDS_THIEVES_TOOLS = "fast_hands_thieves_tools"  # Thief level 3 - Use thieves tools as bonus action
    FAST_HANDS_USE_OBJECT = "fast_hands_use_object"  # Thief level 3 - Use Object as bonus action
    FAST_HANDS_SLEIGHT_OF_HAND = "fast_hands_sleight_of_hand"  # Thief level 3 - Sleight of Hand as bonus action
    MASTERFUL_MIMICRY = "masterful_mimicry"  # Assassin level 9 - Mimic speech/handwriting
    
    # Feat Actions
    BATTLE_MEDIC = "battle_medic"  # Healer feat - Utilize action
    LUCK_POINT_ADVANTAGE = "luck_point_advantage"  # Lucky feat - Free action for advantage
    LUCK_POINT_DISADVANTAGE = "luck_point_disadvantage"  # Lucky feat - Reaction for enemy disadvantage


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
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout_profile: Optional[LayoutProfile] = None,
    ):
        super().__init__(parent)
        self.layout_profile = layout_profile or BASELINE_PROFILE
        # Calculate width to span from left margin to just before equipment panel
        # left_margin + character_width + encounter_width = total before equipment
        self.panel_width = self.layout_profile.character_panel_width + self.layout_profile.encounter_panel_width
        self.panel_height = self.layout_profile.action_panel_height
        self.current_category = ActionCategory.COMBAT
        self.current_theme = "light"  # Default theme
        self.action_cards = {}  # ActionType -> ActionCard mapping
        self.action_cooldowns = {}  # ActionType -> remaining turns
        self.character_context = {}  # Current character state
        self.first_attack_this_round = True  # Track first attack per round for Savage Attacker
        self.character_features = {}  # Character class features (Fighting Style, etc.)
        self.equipped_weapons = {}  # Store equipped weapon data
        self.character_weapon_masteries = []
        self.character_weapon_mastery_map: Dict[str, Optional[str]] = {}
        self._weapon_mastery_service: Optional[WeaponMasteryService] = None
        self._equipment_database: Optional[EquipmentDatabase] = None
        self._weapon_mastery_cache: Dict[str, Optional[Dict[str, Any]]] = {}
        self._weapon_attack_service: Optional[WeaponAttackService] = None
        self._combat_manager: Optional[CombatManager] = None
        self._spellcasting_service: Optional[SpellcastingService] = None
        
        # Lucky feat state tracking
        # Note: Lucky/Inspiration offensive flags are now defined earlier in __init__
        self.lucky_disadvantage_active = False  # True when Lucky disadvantage is ready for next enemy attack
        
        # Advantage resource system
        self.resource_manager = None  # Will be set when character loads
        
        # Vex weapon mastery tracking
        self.vex_target_id = None  # Monster ID that player has Vex advantage against
        self.target_monster_id = None  # Currently targeted monster for attacks
        self.pending_attack = None  # Store attack to execute after monsters' turns
        self._cleave_followup_in_progress = False  # Prevent recursive Cleave triggers
        
        # Action Economy Integration - NEW
        self.current_combat_session = None  # Current combat session for action economy
        self.character_id = None  # Current character ID for action tracking
        self.action_economy_enabled = True  # Toggle for action economy enforcement
        
        # Defensive resource flags for imposing disadvantage on monster attacks
        self.inspiration_defensive_active = False
        self.lucky_defensive_active = False
        
        # Offensive resource flags for gaining advantage on player attacks
        self._inspiration_offensive_active = False
        self._lucky_offensive_active = False
        
        # Set fixed size (spans usable width inside the margins)
        self.setFixedSize(self.panel_width, self.panel_height)
        self.setAutoFillBackground(True)  # Ensure background is filled
        
        # Initialize UI components
        self._ui_initialized = False
        self._setup_ui()
        self._apply_styles()
        self._create_action_cards()
        self._ui_initialized = True
        
        # Now update visible cards after initialization
        self._update_visible_cards()
        
        # Cooldown timer
        self.cooldown_timer = QTimer()
        self.cooldown_timer.timeout.connect(self._update_cooldowns)
        self.cooldown_timer.start(1000)  # Update every second
        
    @property
    def inspiration_offensive_active(self):
        return self._inspiration_offensive_active
    
    @inspiration_offensive_active.setter
    def inspiration_offensive_active(self, value):
        print(f"[DEBUG] Setting inspiration_offensive_active from {self._inspiration_offensive_active} to {value}")
        import traceback
        traceback.print_stack(limit=3)
        self._inspiration_offensive_active = value
        
    @property
    def lucky_offensive_active(self):
        return self._lucky_offensive_active
    
    @lucky_offensive_active.setter
    def lucky_offensive_active(self, value):
        print(f"[DEBUG] Setting lucky_offensive_active from {self._lucky_offensive_active} to {value}")
        self._lucky_offensive_active = value
    
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
                (ActionType.USE_ITEM, "[POTION]", "Use Item", "Use an item from your inventory"),
                (ActionType.DODGE, "[SHIELD]", "Dodge", "Gain advantage on Dexterity saves"),
            ],
            ActionCategory.MOVEMENT: [
                (ActionType.MOVE, "[MOVE]", "Move", "Move up to your speed"),
                (ActionType.DASH, "💨", "Dash", "Double your movement speed this turn"),
                (ActionType.HIDE, "👻", "Hide", "Attempt to become hidden"),
            ],
            ActionCategory.BONUS: [
                (ActionType.SEARCH, "[SEARCH]", "Search", "Look for hidden objects or clues"),
                (ActionType.INVESTIGATE, "🕵️", "Investigate", "Make a detailed investigation"),
                (ActionType.REST, "😴", "Rest", "Take a short rest to recover"),
                (ActionType.USE_POTION, "[POTION]", "Use Potion", "Drink a healing potion (2d4+4 HP)"),
            ],
            ActionCategory.FREE: [
                (ActionType.INTERACT, "[HAND]", "Interact", "Interact with objects or environment"),
            ],
            ActionCategory.REACTION: [
                (ActionType.OPPORTUNITY, "[LIGHTNING]", "Opportunity", "Make an opportunity attack"),
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
    
    def _create_weapon_cards(self):
        """Create weapon attack cards based on equipped weapons."""
        # Remove existing weapon cards
        for action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
            if action_type in self.action_cards:
                self.action_cards[action_type].deleteLater()
                del self.action_cards[action_type]

        # Create main hand weapon card
        main_hand = self.equipped_weapons.get('main_hand')
        if main_hand and main_hand.get('item_type') == 'weapon':
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

    def _prepare_equipped_item(self, item: Any) -> Any:
        """Deep-copy equipped items and hydrate weapons with database metadata."""
        if not isinstance(item, dict):
            return item

        prepared = dict(item)
        item_type = str(prepared.get('item_type', '')).lower()
        if item_type != 'weapon':
            return prepared

        return self._hydrate_equipped_weapon(prepared)

    @staticmethod
    def _infer_base_weapon_name(weapon_name: str) -> Optional[str]:
        """Best-effort extraction of the non-magical base weapon name."""
        if not weapon_name:
            return None

        base = weapon_name.strip()
        if ' +' in base:
            return base.split(' +', 1)[0].strip()
        if '(' in base and base.endswith(')'):
            inner = base[base.rfind('(') + 1:-1].strip()
            return inner or None
        return None

    def _hydrate_equipped_weapon(self, weapon: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure equipped weapon entries include mastery-critical metadata."""
        hydrated = dict(weapon)
        needs_lookup = not hydrated.get('damage_dice') or not hydrated.get('damage_type')
        needs_lookup = needs_lookup or hydrated.get('weapon_properties') in (None, '', [])
        needs_lookup = needs_lookup or not hydrated.get('weapon_mastery')

        if needs_lookup:
            weapon_name = hydrated.get('name', '')
            try:
                db = self._get_equipment_database()
                record = db.get_equipment_by_name(weapon_name) if weapon_name else None
                if not record:
                    base_name = self._infer_base_weapon_name(weapon_name)
                    if base_name and base_name.lower() != weapon_name.lower():
                        record = db.get_equipment_by_name(base_name)
                if record:
                    for key in (
                        'item_type',
                        'weapon_category',
                        'damage_dice',
                        'damage_type',
                        'weapon_mastery',
                        'range_normal',
                        'range_long',
                        'versatile_damage',
                        'weapon_properties',
                    ):
                        value = record.get(key)
                        if key == 'weapon_properties':
                            if hydrated.get('weapon_properties') in (None, '', []) and value is not None:
                                hydrated['weapon_properties'] = list(value) if isinstance(value, list) else value
                            continue
                        if not hydrated.get(key) and value not in (None, ''):
                            hydrated[key] = value
                    hydrated.setdefault('item_type', record.get('item_type', 'weapon'))
            except Exception as exc:
                print(f"[Equipment] Failed to hydrate weapon '{weapon_name or 'Unknown'}': {exc}")

        hydrated['weapon_properties'] = self._extract_weapon_properties(hydrated)
        hydrated.setdefault('item_type', 'weapon')
        return hydrated
    
    def _create_feature_cards(self):
        """Create action cards for character features like Second Wind."""
        print(f"[DEBUG] _create_feature_cards() called!")
        has_features = getattr(self, 'character_features', None)
        print(f"[DEBUG] has_features = {bool(has_features)}")

        if has_features:
            # Clear any existing feature cards
            self._clear_feature_cards()

            display_names = list(self.character_features.keys()) if isinstance(self.character_features, dict) else []
            print(f"DEBUG: Character features for feature checks: {display_names}")
        else:
            print(f"DEBUG: No character features, but will still check for spellcasting")

        second_wind_feature = self._get_feature_data('Second Wind')
        if second_wind_feature:
            level = self.character_context.get('level', 1)
            healing = f"1d10+{level}"
            description = f"Regain {healing} hit points (Short Rest recharge)"
            card = ActionCard(ActionType.SECOND_WIND, "💨", second_wind_feature.get('name', 'Second Wind'), description)
            card.feature_data = second_wind_feature
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.SECOND_WIND] = card

        action_surge_feature = self._get_feature_data('Action Surge')
        if action_surge_feature:
            description = "Gain one additional action this turn (not Magic action)"
            card = ActionCard(ActionType.ACTION_SURGE, "⚡", action_surge_feature.get('name', 'Action Surge'), description)
            card.feature_data = action_surge_feature
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.ACTION_SURGE] = card

        rage_feature = self._get_feature_data('Rage')
        if (rage_feature and self.character_context
                and self.character_context.get('class_id', '').lower() == 'barbarian'
                and self._has_rage_uses()):
            card = ActionCard(ActionType.RAGE, "[RAGE]", rage_feature.get('name', 'Rage'), "Enter barbarian rage (+2 damage, resistance to physical)")
            card.feature_data = rage_feature
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.RAGE] = card

        reckless_feature = self._get_feature_data('Reckless Attack')
        if reckless_feature and self.character_context and self.character_context.get('class_id', '').lower() == 'barbarian':
            is_active = self.character_context.get('reckless_attack_active', False)
            display_text = "RECKLESS ACTIVE" if is_active else reckless_feature.get('name', 'Reckless Attack')
            card = ActionCard(ActionType.RECKLESS_ATTACK, "[RECKLESS]", display_text, "Toggle advantage on STR attacks (enemies gain advantage)")
            card.feature_data = reckless_feature
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            if is_active:
                card.setProperty("reckless_active", True)
                card.setStyleSheet("QPushButton[reckless_active=\"true\"] { background-color: #8B0000; border: 2px solid #FF4444; }")
            self.action_cards[ActionType.RECKLESS_ATTACK] = card

        lay_on_hands_feature = self._get_feature_data('Lay on Hands')
        if lay_on_hands_feature:
            card = ActionCard(ActionType.LAY_ON_HANDS, "✋", lay_on_hands_feature.get('name', 'Lay on Hands'), "Heal 5 HP with divine touch")
            card.feature_data = lay_on_hands_feature
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.LAY_ON_HANDS] = card

        # Channel Divinity for paladins
        channel_divinity_feature = self._get_feature_data('Channel Divinity')
        if channel_divinity_feature:
            card = ActionCard(ActionType.CHANNEL_DIVINITY, "⚡", "Channel Divinity", "Channel divine energy for various effects")
            card.feature_data = channel_divinity_feature
            card.action_triggered.connect(self._trigger_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.CHANNEL_DIVINITY] = card

        # Thief Features
        if (self.character_context and self.character_context.get('class_id', '').lower() == 'rogue'
            and self.character_context.get('subclass_id') == 'thief'):
            level = self.character_context.get('level', 1)

            # Fast Hands (Level 3+) - Thieves Tools as bonus action
            if level >= 3:
                fast_hands_feature = self._get_feature_data('Fast Hands')
                if fast_hands_feature:
                    card = ActionCard(ActionType.FAST_HANDS_THIEVES_TOOLS, "[TOOLS]", "Use Thieves Tools", "Use thieves tools as bonus action")
                    card.feature_data = fast_hands_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.FAST_HANDS_THIEVES_TOOLS] = card

                    card = ActionCard(ActionType.FAST_HANDS_USE_OBJECT, "[OBJECT]", "Use Object", "Use Object action as bonus action")
                    card.feature_data = fast_hands_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.FAST_HANDS_USE_OBJECT] = card

                    card = ActionCard(ActionType.FAST_HANDS_SLEIGHT_OF_HAND, "[SLEIGHT]", "Sleight of Hand", "Sleight of Hand check as bonus action")
                    card.feature_data = fast_hands_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.FAST_HANDS_SLEIGHT_OF_HAND] = card

        # Spellcasting Features
        if self.character_context:
            class_id = self.character_context.get('class_id', '').lower()
            subclass_id = self.character_context.get('subclass_id', '').lower()
            level = self.character_context.get('level', 1)

            print(f"[DEBUG] Checking spellcasting for class_id={class_id}, level={level}")

            # Check if character can cast spells
            is_spellcaster = False

            # Full spellcasters (start at level 1)
            if class_id in ['wizard', 'cleric', 'warlock', 'sorcerer', 'druid', 'bard']:
                is_spellcaster = True

            # Half-casters (start at level 2)
            elif class_id in ['paladin', 'ranger'] and level >= 2:
                is_spellcaster = True

            # Third-casters (subclass specific, start at level 3)
            elif ((class_id == 'rogue' and subclass_id == 'arcane_trickster') or
                  (class_id == 'fighter' and subclass_id == 'eldritch_knight')) and level >= 3:
                is_spellcaster = True

            print(f"[DEBUG] is_spellcaster={is_spellcaster}")

            if is_spellcaster:
                self._create_spell_action_cards()

        # Barbarian Features
        if self.character_context and self.character_context.get('class_id', '').lower() == 'barbarian':
            level = self.character_context.get('level', 1)

            # Brutal Strike (Level 9+)
            if level >= 9:
                brutal_strike_feature = self._get_feature_data('Brutal Strike')
                if brutal_strike_feature:
                    # Forceful Blow (always available at level 9)
                    card = ActionCard(ActionType.BRUTAL_STRIKE_FORCEFUL, "[FORCE]", "Forceful Blow", "Push 15 ft & move toward target (+1d10 damage)")
                    card.feature_data = brutal_strike_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.BRUTAL_STRIKE_FORCEFUL] = card

                    # Hamstring Blow (always available at level 9)
                    card = ActionCard(ActionType.BRUTAL_STRIKE_HAMSTRING, "[SLOW]", "Hamstring Blow", "Reduce speed by 15 ft (+1d10 damage)")
                    card.feature_data = brutal_strike_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.BRUTAL_STRIKE_HAMSTRING] = card

                    # Additional effects at level 13+
                    if level >= 13:
                        # Staggering Blow
                        card = ActionCard(ActionType.BRUTAL_STRIKE_STAGGERING, "[STUN]", "Staggering Blow", "Disadvantage on saves, no opportunity attacks (+1d10 damage)")
                        card.feature_data = brutal_strike_feature
                        card.action_triggered.connect(self._trigger_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.BRUTAL_STRIKE_STAGGERING] = card

                        # Sundering Blow
                        card = ActionCard(ActionType.BRUTAL_STRIKE_SUNDERING, "[BREAK]", "Sundering Blow", "Next attack vs target gets +5 (+1d10 damage)")
                        card.feature_data = brutal_strike_feature
                        card.action_triggered.connect(self._trigger_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.BRUTAL_STRIKE_SUNDERING] = card

            # Instinctive Pounce (Level 7+)
            if level >= 7:
                instinctive_pounce_feature = self._get_feature_data('Instinctive Pounce')
                if instinctive_pounce_feature:
                    card = ActionCard(ActionType.INSTINCTIVE_POUNCE, "[LEAP]", "Instinctive Pounce", "Move half speed when entering Rage")
                    card.feature_data = instinctive_pounce_feature
                    card.action_triggered.connect(self._trigger_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.INSTINCTIVE_POUNCE] = card

            # Path of the Berserker features
            subclass = self.character_context.get('subclass', '').lower()
            if subclass == 'berserker':
                # Intimidating Presence (Level 14+)
                if level >= 14:
                    intimidating_presence_feature = self._get_feature_data('Intimidating Presence')
                    if intimidating_presence_feature:
                        card = ActionCard(ActionType.INTIMIDATING_PRESENCE, "[FEAR]", "Intimidating Presence", "Frighten enemies in 30 ft (Wis save)")
                        card.feature_data = intimidating_presence_feature
                        card.action_triggered.connect(self._trigger_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.INTIMIDATING_PRESENCE] = card

        # Rogue Features
        if self.character_context and self.character_context.get('class_id', '').lower() == 'rogue':
            level = self.character_context.get('level', 1)

            # Cunning Action (Level 2+)
            if level >= 2:
                cunning_action_feature = self._get_feature_data('Cunning Action')
                if cunning_action_feature:
                    # Dash
                    card = ActionCard(ActionType.CUNNING_DASH, "[DASH]", "Cunning Dash", "Dash as bonus action")
                    card.feature_data = cunning_action_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_DASH] = card

                    # Disengage
                    card = ActionCard(ActionType.CUNNING_DISENGAGE, "[ESCAPE]", "Cunning Disengage", "Disengage as bonus action")
                    card.feature_data = cunning_action_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_DISENGAGE] = card

                    # Hide
                    card = ActionCard(ActionType.CUNNING_HIDE, "[HIDE]", "Cunning Hide", "Hide as bonus action")
                    card.feature_data = cunning_action_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_HIDE] = card

            # Steady Aim (Level 3+)
            if level >= 3:
                steady_aim_feature = self._get_feature_data('Steady Aim')
                if steady_aim_feature:
                    card = ActionCard(ActionType.STEADY_AIM, "[AIM]", "Steady Aim", "Gain advantage on next attack (cannot move)")
                    card.feature_data = steady_aim_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.STEADY_AIM] = card

            # Cunning Strike (Level 5+)
            if level >= 5:
                cunning_strike_feature = self._get_feature_data('Cunning Strike')
                if cunning_strike_feature:
                    # Basic effects (Level 5+)
                    card = ActionCard(ActionType.CUNNING_STRIKE_POISON, "[POISON]", "Poison Strike", "Poisoned 1 min (Con save) - Cost: 1d6")
                    card.feature_data = cunning_strike_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_STRIKE_POISON] = card

                    card = ActionCard(ActionType.CUNNING_STRIKE_TRIP, "[TRIP]", "Trip Strike", "Prone (Dex save) - Cost: 1d6")
                    card.feature_data = cunning_strike_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_STRIKE_TRIP] = card

                    card = ActionCard(ActionType.CUNNING_STRIKE_WITHDRAW, "[ESCAPE]", "Withdraw Strike", "Move half speed no AoO - Cost: 1d6")
                    card.feature_data = cunning_strike_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.CUNNING_STRIKE_WITHDRAW] = card

                    # Devious Strikes (Level 14+)
                    if level >= 14:
                        card = ActionCard(ActionType.CUNNING_STRIKE_DAZE, "[DAZE]", "Daze Strike", "Limited actions next turn (Con save) - Cost: 2d6")
                        card.feature_data = cunning_strike_feature
                        card.action_triggered.connect(self._trigger_rogue_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.CUNNING_STRIKE_DAZE] = card

                        card = ActionCard(ActionType.CUNNING_STRIKE_KNOCK_OUT, "[KO]", "Knock Out Strike", "Unconscious 1 min (Con save) - Cost: 6d6")
                        card.feature_data = cunning_strike_feature
                        card.action_triggered.connect(self._trigger_rogue_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.CUNNING_STRIKE_KNOCK_OUT] = card

                        card = ActionCard(ActionType.CUNNING_STRIKE_OBSCURE, "[BLIND]", "Obscure Strike", "Blinded next turn (Dex save) - Cost: 3d6")
                        card.feature_data = cunning_strike_feature
                        card.action_triggered.connect(self._trigger_rogue_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[ActionType.CUNNING_STRIKE_OBSCURE] = card

            # Stroke of Luck (Level 20+)
            if level >= 20:
                stroke_feature = self._get_feature_data('Stroke of Luck')
                if stroke_feature and self._has_stroke_of_luck_uses():
                    card = ActionCard(ActionType.STROKE_OF_LUCK, "[LUCK]", "Stroke of Luck", "Turn failed d20 test into 20")
                    card.feature_data = stroke_feature
                    card.action_triggered.connect(self._trigger_rogue_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.STROKE_OF_LUCK] = card

        # Create enhanced subclass feature cards
        if self.character_context:
            character_id = self.character_context.get('character_id')
            level = self.character_context.get('level', 1)
            if character_id:
                from services.subclass_action_integration import subclass_action_integration

                # Get action cards for this character's subclass features
                subclass_cards = subclass_action_integration.get_action_cards_for_character(character_id, level)

                for card_data in subclass_cards:
                    action_type_name = card_data.get('action_type')
                    if hasattr(ActionType, action_type_name):
                        action_type = getattr(ActionType, action_type_name)
                        name = card_data.get('name')
                        description = card_data.get('description')
                        icon = card_data.get('icon', '⚡')

                        card = ActionCard(action_type, icon, name, description)
                        card.feature_data = card_data.get('feature_data')
                        card.action_triggered.connect(self._trigger_subclass_action)
                        card.action_hovered.connect(self._action_hovered)
                        self.action_cards[action_type] = card

                # Legacy support for existing Signature Move
                from services.subclass_manager import SubclassManager
                subclass_manager = SubclassManager()
                if subclass_manager.has_feature(character_id, 'Signature Move'):
                    description = "Special attack: +2d6 damage, can frighten (DC 8+prof+STR)"
                    card = ActionCard(ActionType.SIGNATURE_MOVE, "✨", "Signature Move", description)
                    card.action_triggered.connect(self._trigger_subclass_action)
                    card.action_hovered.connect(self._action_hovered)
                    self.action_cards[ActionType.SIGNATURE_MOVE] = card

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
                card = ActionCard(ActionType.NICK_MASTERY, "[SWORD]", "Nick Mastery", weapon_mastery_details["Nick"])
                card.feature_data = {'type': 'weapon_mastery', 'name': 'Nick'}
                card.action_triggered.connect(self._trigger_feature_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[ActionType.NICK_MASTERY] = card
            
            if "Cleave" in selected_masteries:
                card = ActionCard(ActionType.CLEAVE_MASTERY, "[SWORD]", "Cleave Mastery", weapon_mastery_details["Cleave"])
                card.feature_data = {'type': 'weapon_mastery', 'name': 'Cleave'}
                card.action_triggered.connect(self._trigger_feature_action)
                card.action_hovered.connect(self._action_hovered)
                self.action_cards[ActionType.CLEAVE_MASTERY] = card
        
        # Create Feat Action Cards
        character_feats = getattr(self, 'character_feats', [])
        
        # Battle Medic (Healer feat)
        if 'Healer' in character_feats:
            card = ActionCard(ActionType.BATTLE_MEDIC, "🩹", "Battle Medic", "Use Healer's Kit: Target expends Hit Die + your proficiency bonus")
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.BATTLE_MEDIC] = card
        
        # Lucky feat actions
        if 'Lucky' in character_feats:
            # Advantage action
            card = ActionCard(ActionType.LUCK_POINT_ADVANTAGE, "🍀", "Luck (Advantage)", "Spend 1 Luck Point for advantage on your next d20 roll")
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.LUCK_POINT_ADVANTAGE] = card
            
            # Disadvantage reaction
            card = ActionCard(ActionType.LUCK_POINT_DISADVANTAGE, "🛡️", "Luck (Disadvantage)", "Spend 1 Luck Point to impose disadvantage on enemy attack")
            card.action_triggered.connect(self._trigger_feature_action)
            card.action_hovered.connect(self._action_hovered)
            self.action_cards[ActionType.LUCK_POINT_DISADVANTAGE] = card
    
    def _trigger_subclass_action(self, action_type):
        """Handle subclass feature actions."""
        character_id = self.character_context.get('character_id', '')
        if not character_id:
            return

        # Handle enhanced subclass features
        if action_type == ActionType.INTIMIDATING_PRESENCE:
            self._use_intimidating_presence()
        elif action_type == ActionType.RETALIATION:
            self._use_retaliation()
        # Handle Thief Fast Hands features
        elif action_type == ActionType.FAST_HANDS_THIEVES_TOOLS:
            self._use_fast_hands_thieves_tools()
        elif action_type == ActionType.FAST_HANDS_USE_OBJECT:
            self._use_fast_hands_use_object()
        elif action_type == ActionType.FAST_HANDS_SLEIGHT_OF_HAND:
            self._use_fast_hands_sleight_of_hand()
        # Handle Assassin features
        elif action_type == ActionType.MASTERFUL_MIMICRY:
            self._use_masterful_mimicry()
        elif action_type == ActionType.HEROIC_WARRIOR:
            self._use_heroic_warrior()
        elif action_type == ActionType.SURVIVOR:
            self._use_survivor()
        elif action_type == ActionType.SIGNATURE_MOVE:
            # Legacy Signature Move handling
            from services.subclass_manager import SubclassManager
            subclass_manager = SubclassManager()

            current_uses, max_uses = subclass_manager.get_feature_uses(character_id, 'Signature Move')
            if current_uses <= 0:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.add_message("No Signature Move uses remaining (short rest to recharge)")
                        break
                    parent = parent.parent()
                return

            # Use the feature
            if subclass_manager.use_feature(character_id, 'Signature Move'):
                # Apply special attack effects in context
                self.character_context['signature_move_active'] = True

                # Log usage
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        remaining = current_uses - 1
                        parent.log_panel.add_message(f"Signature Move activated! (+2d6 damage, frightening attack) [{remaining} uses remaining]")
                        break
                    parent = parent.parent()
    
    def _trigger_feature_action(self, action_type):
        """Handle feature-based action triggers."""
        if action_type == ActionType.SECOND_WIND or action_type == 1000:  # Handle both enum and legacy ID
            # Use the unified resource system
            resource_service = self._get_resource_service()
            
            # Get character ID
            character_id = self._resolve_character_id()
            if not character_id:
                print("DEBUG: No character ID for Second Wind")
                return
            
            # Check if resource is available
            second_wind_resource = resource_service.get_resource(character_id, 'Second Wind')
            if not second_wind_resource or second_wind_resource.current_uses <= 0:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[FAIL] No Second Wind uses remaining")
                        break
                    parent = parent.parent()
                return
            
            # Use Second Wind resource
            use_result = resource_service.use_resource(character_id, 'Second Wind')
            if not use_result.get('success', False):
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[FAIL] {use_result.get('error', 'Second Wind failed')}")
                        break
                    parent = parent.parent()
                return
            
            # Roll healing (1d10 + Fighter level)
            import random
            healing_roll = random.randint(1, 10)
            fighter_level = self.character_context.get('level', 1)
            total_healing = healing_roll + fighter_level

            # HEALING IN COMBAT - CRITICAL PATTERN
            # When implementing healing abilities that can be used during combat:
            # 1. Get current HP from parent.character_sheet.character_data (same as damage does)
            # 2. This is where real-time combat HP is tracked
            # 3. The database and character_context may be stale during combat
            # 4. After healing, update character sheet, database, and character_context
            # This pattern mirrors how damage works, just in reverse

            # Get current HP from character sheet (where combat damage tracking happens)
            parent = self.parent()
            current_hp = 0
            max_hp = 1
            found_character_sheet = False

            while parent:
                if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                    character_data = parent.character_sheet.character_data
                    current_hp = character_data.get('current_hit_points', character_data.get('hit_points_current', 0))
                    max_hp = character_data.get('max_hit_points', character_data.get('hit_points_max', 1))
                    found_character_sheet = True
                    break
                parent = parent.parent()

            # Fallback to character context if no character sheet found
            if not found_character_sheet:
                current_hp = self.character_context.get('hit_points_current',
                                                      self.character_context.get('current_hit_points', 0))
                max_hp = self.character_context.get('hit_points_max',
                                                   self.character_context.get('max_hit_points',
                                                   self.character_context.get('hit_points_maximum', None)))

                # If we can't find max HP anywhere, abort the healing
                if max_hp is None or max_hp <= 0:
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat("[ERROR] Cannot determine character's max HP - Second Wind failed")
                            break
                        parent = parent.parent()
                    return

            print(f"[DEBUG] Second Wind: current_hp={current_hp}, max_hp={max_hp}, total_healing={total_healing}")
            new_hp = min(max_hp, current_hp + total_healing)
            actual_healing = new_hp - current_hp
            print(f"[DEBUG] Second Wind: new_hp={new_hp}, actual_healing={actual_healing}")
            
            # Update character HP
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine:
                    parent.game_engine.update_character_hp_sync(new_hp, max_hp)
                    self.character_context['hit_points_current'] = new_hp
                    
                    # Force character sheet refresh
                    if hasattr(parent, 'character_panel'):
                        parent.character_panel.update_display()
                    elif hasattr(parent, '_force_reload_character'):
                        parent._force_reload_character()
                    break
                parent = parent.parent()
            
            result = {
                'success': True,
                'healing_roll': healing_roll,
                'level_bonus': fighter_level,
                'total_healing': total_healing,
                'actual_healing': actual_healing,
                'old_hp': current_hp,
                'new_hp': new_hp,
                'max_hp': max_hp,
                'uses_remaining': use_result['current_uses']
            }
            
            # Log the result
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    if result['success']:
                        parent.log_panel.log_combat(f"🩹 Second Wind: Rolled {result['healing_roll']} + {result['level_bonus']} = {result['total_healing']} healing")
                        old_hp = result['old_hp']
                        max_hp = result['max_hp']
                        if result['actual_healing'] < result['total_healing']:
                            parent.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} -> {result['new_hp']}/{max_hp} (healed {result['actual_healing']}, max HP reached)")
                        else:
                            parent.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} -> {result['new_hp']}/{max_hp} (healed {result['actual_healing']})")
                        if result['uses_remaining'] > 0:
                            parent.log_panel.log_combat(f"Second Wind uses remaining: {result['uses_remaining']}")
                    else:
                        parent.log_panel.log_combat(f"[FAIL] {result['error']}")
                    break
                parent = parent.parent()
            
            self._refresh_action_availability()

            # Update UI
            if result['success']:
                # Update our character context with new HP
                self.character_context['hit_points_current'] = new_hp
                self.character_context['current_hit_points'] = new_hp

                # Update character sheet (same pattern as damage application)
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                        # Update the character data
                        parent.character_sheet.character_data['current_hit_points'] = new_hp
                        parent.character_sheet.character_data['hit_points_current'] = new_hp

                        # Reload the character sheet display
                        parent.character_sheet.load_character_data(parent.character_sheet.character_data)
                        break
                    elif hasattr(parent, 'character_panel'):
                        parent.character_panel.update_display()
                        break
                    parent = parent.parent()
        
        elif action_type == ActionType.ACTION_SURGE:
            # Use the unified resource system
            resource_service = self._get_resource_service()
            
            # Get character ID
            character_id = self._resolve_character_id()
            if not character_id:
                print("DEBUG: No character ID for Action Surge")
                return
            
            # Check if resource is available
            action_surge_resource = resource_service.get_resource(character_id, 'Action Surge')
            if not action_surge_resource or action_surge_resource.current_uses <= 0:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[FAIL] No Action Surge uses remaining")
                        break
                    parent = parent.parent()
                return
            
            # Use Action Surge resource
            use_result = resource_service.use_resource(character_id, 'Action Surge')
            if not use_result.get('success', False):
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[FAIL] {use_result.get('error', 'Action Surge failed')}")
                        break
                    parent = parent.parent()
                return
            
            self._refresh_action_availability()

            # Set Action Surge state in character context
            if 'action_surge_extra_action_available' not in self.character_context:
                self.character_context['action_surge_extra_action_available'] = True
                self.character_context['action_surge_used_this_turn'] = True
                
                # Log successful Action Surge
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("⚡ Action Surge! Additional action available this turn!")
                        parent.log_panel.log_combat(f"Action Surge uses remaining: {use_result['current_uses']}")
                        break
                    parent = parent.parent()
            else:
                # Already used Action Surge this turn
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[FAIL] Action Surge: Already used this turn")
                        break
                    parent = parent.parent()
        
        elif action_type == ActionType.NICK_MASTERY:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[SWORD] Used Nick Mastery: Making bonus action attack with light weapon")
                    break
                parent = parent.parent()
        
        elif action_type == ActionType.CLEAVE_MASTERY:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[SWORD] Used Cleave Mastery: Making bonus action attack on second target")
                    break
                parent = parent.parent()
        
        # Feat Actions
        elif action_type == ActionType.BATTLE_MEDIC:
            # Check if character has Healer's Kit
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"🩹 Used Battle Medic: Target expends Hit Die and adds proficiency bonus to healing")
                    break
                parent = parent.parent()
            
        elif action_type == ActionType.LUCK_POINT_ADVANTAGE:
            # Use a Luck Point for advantage
            uses_remaining = self._get_feat_resource_remaining("Lucky", "luck_points")
            if uses_remaining > 0:
                self._use_feat_resource("Lucky", "luck_points")
                self.lucky_offensive_active = True  # Set flag for next d20 roll
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"🍀 Used Luck Point: Gaining advantage on next d20 roll ({uses_remaining - 1} remaining)")
                        break
                    parent = parent.parent()
            
        elif action_type == ActionType.LUCK_POINT_DISADVANTAGE:
            # Use a Luck Point to impose disadvantage
            uses_remaining = self._get_feat_resource_remaining("Lucky", "luck_points")
            if uses_remaining > 0:
                self._use_feat_resource("Lucky", "luck_points")
                self.lucky_disadvantage_active = True  # Set flag for next enemy attack
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"🛡️ Used Luck Point: Imposing disadvantage on enemy attack ({uses_remaining - 1} remaining)")
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
                        parent.log_panel.log_info(f"[SWORD] Selected Weapon Mastery: {mastery_name}")
                        break
                    parent = parent.parent()

    def _trigger_rogue_action(self, action_type):
        """Handle rogue feature actions."""
        character_id = self.character_context.get('character_id', '')
        if not character_id:
            return

        try:
            from services.rogue_abilities import RogueAbilitiesService
            rogue_service = RogueAbilitiesService(self._resolve_db_path())

            # Handle Cunning Action variants
            if action_type in [ActionType.CUNNING_DASH, ActionType.CUNNING_DISENGAGE, ActionType.CUNNING_HIDE]:
                action_name = action_type.value.replace('cunning_', '').title()
                result = rogue_service.use_cunning_action(character_id, action_name.lower())

                if result['success']:
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"🥷 Used {action_name} as bonus action")
                            break
                        parent = parent.parent()
                else:
                    self._log_to_parent(f"❌ {result['message']}")

            # Handle Steady Aim
            elif action_type == ActionType.STEADY_AIM:
                result = rogue_service.use_steady_aim(character_id)

                if result['success']:
                    # Set advantage for next attack and reduce speed to 0
                    self.character_context['steady_aim_active'] = True
                    self.character_context['speed'] = 0

                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat("🎯 Steady Aim: Gain advantage on next attack, speed becomes 0")
                            break
                        parent = parent.parent()
                else:
                    self._log_to_parent(f"❌ {result['message']}")

            # Handle Cunning Strike variants (these modify next Sneak Attack)
            elif action_type.value.startswith('cunning_strike_'):
                effect_name = action_type.value.replace('cunning_strike_', '')
                self.character_context[f'cunning_strike_{effect_name}_active'] = True

                # Get cost information
                costs = {
                    'poison': '1d6', 'trip': '1d6', 'withdraw': '1d6',
                    'daze': '2d6', 'knock_out': '6d6', 'obscure': '3d6'
                }
                cost = costs.get(effect_name, '1d6')

                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"⚔️ {effect_name.title()} Strike prepared - will apply on next Sneak Attack (Cost: {cost})")
                        break
                    parent = parent.parent()

            # Handle Stroke of Luck
            elif action_type == ActionType.STROKE_OF_LUCK:
                # This would be triggered reactively when a d20 test fails
                self.character_context['stroke_of_luck_available'] = True

                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("🍀 Stroke of Luck ready - next failed d20 test becomes 20")
                        break
                    parent = parent.parent()

        except Exception as e:
            self._log_to_parent(f"❌ Error using rogue ability: {e}")

    def _has_stroke_of_luck_uses(self) -> bool:
        """Check if character has Stroke of Luck uses remaining."""
        character_id = self.character_context.get('character_id', '')
        if not character_id:
            return False

        try:
            from services.rogue_abilities import RogueAbilitiesService
            rogue_service = RogueAbilitiesService(self._resolve_db_path())
            features = rogue_service.get_rogue_features(character_id)
            return features.get('stroke_of_luck_uses_current', 0) > 0
        except:
            return False

    def _calculate_hit_bonus(self, weapon: Dict[str, Any], hand: str) -> int:
        """Calculate attack bonus for a weapon."""
        # Base proficiency bonus (assume level 1 = +2 for now)
        from services.proficiency_bonus import get_proficiency_bonus_from_context
        prof_bonus = get_proficiency_bonus_from_context(self.character_context)
        
        # Get relevant ability modifier (Str for most weapons, Dex for finesse)
        weapon_props = self._extract_weapon_properties(weapon)
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
        magic_bonus = weapon.get('attack_bonus') or 0
        
        return prof_bonus + ability_mod + magic_bonus
    
    def _format_damage(self, weapon: Dict[str, Any], is_off_hand: bool = False) -> str:
        """Format weapon damage string."""
        damage_dice = weapon.get('damage_dice', '1d4')
        damage_type = weapon.get('damage_type', 'slashing')
        
        # Get ability modifier for damage
        weapon_props = self._extract_weapon_properties(weapon)
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
        magic_bonus = weapon.get('damage_bonus') or 0
        
        # Get feature-based damage bonuses (rage, dueling, etc.)
        weapon_context = {
            'weapon_properties': weapon_props,
            'damage_type': weapon.get('damage_type', 'physical')
        }
        feature_bonuses = self._get_all_damage_bonuses(weapon_context)
        total_feature_bonus = sum(feature_bonuses.values())
        
        # Off-hand attacks don't get feature bonuses if the feature is melee-only
        if is_off_hand and 'Rage' in feature_bonuses:
            # Rage applies to both main-hand and off-hand attacks
            pass  # Keep the rage bonus for off-hand
        
        total_bonus = ability_mod + magic_bonus + total_feature_bonus
        
        if total_bonus > 0:
            return f"{damage_dice}+{total_bonus} {damage_type}"
        elif total_bonus < 0:
            return f"{damage_dice}{total_bonus} {damage_type}"
        else:
            return f"{damage_dice} {damage_type}"
    
    def _apply_styles(self):
        """Apply initial styling based on the active theme."""
        theme_name = 'light'
        parent = self.parent()
        if parent and hasattr(parent, 'current_theme'):
            theme_name = getattr(parent, 'current_theme', 'light')
        self._apply_styles_for_theme(theme_name)

    def _apply_styles_for_theme(self, theme_name: str):
        from ui.themes import get_theme_palette

        palette = get_theme_palette(theme_name)
        style_sheet = f"""
        ActionPanel {{
            background-color: {palette['surface']};
            border-top: 2px solid {palette['border']};
        }}

        QFrame#headerFrame {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}

        QLabel#titleLabel {{
            color: {palette['text']};
            font-size: 16px;
            font-weight: bold;
        }}

        QPushButton#categoryButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        QPushButton#categoryButton:hover {{
            background-color: {palette['button_hover']};
        }}

        QPushButton#categoryButton:checked {{
            background-color: {palette['selection']};
            color: {palette['text']};
            border-color: {palette['accent_primary']};
        }}

        QScrollArea#scrollArea {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}

        QScrollBar:horizontal {{
            background-color: {palette['surface']};
            height: 12px;
            border-radius: 6px;
            border: 1px solid {palette['border']};
        }}

        QScrollBar::handle:horizontal {{
            background-color: {palette['accent_primary']};
            border-radius: 6px;
            min-width: 20px;
            border: 1px solid {palette['border']};
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {palette['accent_secondary']};
        }}
        """
        self.setStyleSheet(style_sheet)
    
    def _set_category(self, category: ActionCategory):
        """Set the active action category."""
        self.current_category = category
        self._update_visible_cards()
        self.category_changed.emit(category)
    
    def _update_visible_cards(self):
        """Update which action cards are visible based on current category."""
        # Guard: Check if UI is initialized
        if not hasattr(self, '_ui_initialized') or not self._ui_initialized:
            return
            
        # Clear current layout
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add cards for current category
        if self.current_category == ActionCategory.COMBAT:
            # Combat: main-hand attacks + other combat actions (off-hand is bonus action only)
            combat_actions = []
            
            # Add main-hand weapon attack only (off-hand goes to bonus actions)
            if ActionType.ATTACK_MAIN_HAND in self.action_cards:
                combat_actions.append(ActionType.ATTACK_MAIN_HAND)
            
            # Add spell actions (all spell_ prefixed cards)
            spell_cards = [key for key in self.action_cards.keys() if isinstance(key, str) and key.startswith('spell_')]
            combat_actions.extend(spell_cards)

            # Add other combat actions
            combat_actions.extend([ActionType.USE_ITEM, ActionType.DODGE])
            
            for action_key in combat_actions:
                if action_key in self.action_cards:
                    card = self.action_cards[action_key]
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
            # Only show bonus actions that the character actually has
            bonus_actions = []

            # Dynamically find all bonus action features from database
            character_id = self._resolve_character_id()
            if character_id:
                # Get all bonus action features for this character
                import sqlite3
                try:
                    with sqlite3.connect("talekeeper.db") as conn:
                        cursor = conn.cursor()

                        # Query character features marked as bonus_action
                        cursor.execute("""
                            SELECT feature_name, mechanics
                            FROM character_features
                            WHERE character_id = ? AND feature_type = 'bonus_action'
                        """, (character_id,))

                        for feature_name, mechanics in cursor.fetchall():
                            # Convert feature to action type and add if it exists
                            action_type = self._feature_name_to_action_type(feature_name)
                            if action_type and action_type in self.action_cards:
                                bonus_actions.append(action_type)
                except Exception as e:
                    print(f"Error loading bonus actions from database: {e}")
                    # Fallback to hardcoded list
                    if ActionType.RAGE in self.action_cards:
                        bonus_actions.append(ActionType.RAGE)
                    if ActionType.SECOND_WIND in self.action_cards:
                        bonus_actions.append(ActionType.SECOND_WIND)
                    if ActionType.INTIMIDATING_PRESENCE in self.action_cards:
                        bonus_actions.append(ActionType.INTIMIDATING_PRESENCE)

            # Add off-hand weapon attacks to bonus actions (always check, empty if nothing equipped)
            if ActionType.ATTACK_OFF_HAND in self.action_cards:
                bonus_actions.append(ActionType.ATTACK_OFF_HAND)
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
            
            # Add potion cards (only if character has potions)
            if ActionType.USE_POTION in self.action_cards and self._character_has_potions():
                card = self.action_cards[ActionType.USE_POTION]
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
            free_actions = [ActionType.INTERACT, ActionType.ACTION_SURGE, ActionType.RECKLESS_ATTACK]
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

            # Add character-specific reaction actions
            if ActionType.RETALIATION in self.action_cards:
                reaction_actions.append(ActionType.RETALIATION)

            for action_type in reaction_actions:
                if action_type in self.action_cards:
                    card = self.action_cards[action_type]
                    self.cards_layout.addWidget(card)
                    card.show()
        
        # Add stretch to push cards to left
        self.cards_layout.addStretch()
    
    def _trigger_action(self, action_type: ActionType, context: Dict[str, Any]):
        """Handle action trigger from card."""
        # Check if action is available (both resource availability and action economy)
        if not self._is_action_available(action_type):
            return

        # Check action economy if enabled
        if self.action_economy_enabled and not self.current_combat_session:
            self._ensure_combat_session()

        if self.action_economy_enabled and self.current_combat_session:
            if not self._is_action_available_by_economy(action_type):
                reason = self._get_economy_unavailability_reason(action_type)
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[BLOCKED] Cannot use action: {reason}")
                        break
                    parent = parent.parent()
                return

        # Action is available - proceed
        if True:  # Changed from if condition to always execute
            # Add character context
            full_context = {**context, **self.character_context}
            
            # For attack actions, add target monster and weapon data if available
            if action_type in [ActionType.ATTACK_MAIN_HAND, ActionType.ATTACK_OFF_HAND]:
                # Add weapon data to context
                full_context['weapon'] = True  # Mark as weapon attack for Savage Attacker
                if action_type in self.action_cards:
                    weapon_data = getattr(self.action_cards[action_type], 'weapon_data', None)
                    if weapon_data:
                        full_context.update(weapon_data)
                
                if self.target_monster_id:
                    full_context['target_monster_id'] = self.target_monster_id
                    
                    # D&D 2024 COMPLIANCE: Check if it's the player's turn
                    if not self._is_player_turn_d20():
                        self._log_to_combat_panel("⚔ It's not your turn!")
                        return
                    
                    print(f"ROUTING: About to call _new_execute_attack with action_type={action_type}")
                    # NEW ATTACK SYSTEM - Build from scratch
                    self._new_execute_attack(action_type, full_context)
                    return  # IMPORTANT: Don't fall through to old system
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
                
                # Handle potion usage
                elif action_type == ActionType.USE_POTION:
                    self._use_healing_potion(full_context)
                
                # Handle rest actions
                elif action_type == ActionType.REST:
                    self._handle_rest_action(full_context)
                
                # Handle class features
                elif action_type == ActionType.RAGE:
                    self._use_rage()
                elif action_type == ActionType.RECKLESS_ATTACK:
                    self._toggle_reckless_attack()
                elif action_type == ActionType.LAY_ON_HANDS:
                    self._use_lay_on_hands()
                elif action_type == ActionType.CHANNEL_DIVINITY:
                    self._use_channel_divinity()

                # Handle spell actions
                elif action_type in [ActionType.SPELL_ATTACK, ActionType.SPELL_UTILITY, ActionType.SPELL_REACTION]:
                    self._cast_spell(action_type, full_context)

                # Handle barbarian features
                elif action_type == ActionType.BRUTAL_STRIKE_FORCEFUL:
                    self._use_brutal_strike('forceful')
                elif action_type == ActionType.BRUTAL_STRIKE_HAMSTRING:
                    self._use_brutal_strike('hamstring')
                elif action_type == ActionType.BRUTAL_STRIKE_STAGGERING:
                    self._use_brutal_strike('staggering')
                elif action_type == ActionType.BRUTAL_STRIKE_SUNDERING:
                    self._use_brutal_strike('sundering')
                elif action_type == ActionType.INSTINCTIVE_POUNCE:
                    self._use_instinctive_pounce()
                elif action_type == ActionType.INTIMIDATING_PRESENCE:
                    self._use_intimidating_presence()
                elif action_type == ActionType.RETALIATION:
                    self._use_retaliation()
                elif action_type == ActionType.HEROIC_WARRIOR:
                    self._use_heroic_warrior()
                elif action_type == ActionType.SURVIVOR:
                    self._use_survivor()

                # CRITICAL: Update action economy AFTER action is processed but BEFORE signal
                # This ensures the action effect (like rage activation) happens first,
                # then the economy is consumed to prevent subsequent actions
                self._update_action_economy(action_type)

                # Emit signal
                self.action_triggered.emit(action_type, full_context)

                # For combat actions, advance turn in combat manager after player's turn
                if self._is_combat_action(action_type):
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel:
                        self._advance_combat_turn(encounter_panel)
    
    def _is_combat_action(self, action_type: ActionType) -> bool:
        """Check if an action should trigger turn advancement (end player turn)."""
        # In D&D 5e, the turn ends when:
        # 1. Player uses their main Action (unless Action Surge gives another)
        # 2. Player declares their turn is done
        # 3. Player has used all available actions and movement

        # For now, we'll end the turn after ANY significant combat action
        # This includes main actions, and some bonus actions like potions/healing
        # The action economy will prevent multiple bonus actions per turn

        if self.action_economy_enabled and hasattr(self, '_map_action_to_economy_type'):
            try:
                from models.action_economy import ActionEconomyType
                economy_type = self._map_action_to_economy_type(action_type)

                # End turn after main actions or significant bonus actions
                return economy_type in [ActionEconomyType.ACTION, ActionEconomyType.BONUS_ACTION]
            except:
                pass

        # Fallback list for actions that should end the turn
        turn_ending_actions = {
            ActionType.CAST_SPELL, ActionType.SPELL_ATTACK, ActionType.SPELL_UTILITY,
            ActionType.USE_ITEM, ActionType.DODGE,
            ActionType.DASH, ActionType.SEARCH, ActionType.HIDE,
            ActionType.USE_POTION, ActionType.SECOND_WIND  # Bonus actions that often end turn
        }
        return action_type in turn_ending_actions
    
    def _execute_single_attack(self, action_type: ActionType, context: Dict[str, Any], encounter_panel):
        """Execute a single attack (used by two-weapon fighting system)."""
        # Make attack roll
        attack_total, attack_breakdown = self._roll_attack(context)
        target_ac = 12  # TODO: Get from monster data, for now assume AC 12
        target_id = context.get('target_monster_id')
        weapon_name = context.get('name', 'weapon')
        target_monster = encounter_panel.get_selected_monster()
        
        # Check for critical hit (natural 20, or 19-20/18-20 for Champion Fighter)
        is_critical = self._is_critical_hit(attack_breakdown, context)
        hit = attack_total >= target_ac or is_critical
        
        if hit:
            # Add advantage state to context for damage calculation (needed for sneak attack)
            context['advantage_state'] = attack_breakdown.get('advantage_state')
            context['has_advantage'] = attack_breakdown.get('advantage_state') == 'advantage'
            context['has_disadvantage'] = attack_breakdown.get('advantage_state') == 'disadvantage'

            # Roll damage
            damage_total, damage_breakdown = self._roll_damage(context)
            
            # Double damage DICE ONLY on critical hit (not modifiers)
            if is_critical:
                # Roll the damage dice again (but NOT modifiers) and add to total
                import random
                damage_dice, damage_type = self._get_context_damage_profile(context)
                if 'd' in damage_dice:
                    dice_part = damage_dice.split('+')[0].split('-')[0].strip()
                    try:
                        num_dice, die_size = dice_part.split('d')
                        num_dice = int(num_dice)
                        die_size = int(die_size)
                        # Roll additional dice for critical (same number as base weapon)
                        crit_dice_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
                        crit_bonus = sum(crit_dice_rolls)
                        damage_total += crit_bonus
                        damage_breakdown['critical_dice'] = crit_dice_rolls
                        damage_breakdown['critical_bonus'] = crit_bonus
                        damage_breakdown['is_critical'] = True
                    except:
                        pass


            # Apply weapon mastery effects on hit
            service = self._get_weapon_attack_service()
            weapon_data = self._build_weapon_dict_from_context(context)
            mastery_effects = service.apply_weapon_mastery_effects(
                weapon_data, self.character_context, target=None,
                hit=True, damage_total=damage_total, attack_total=attack_total
            )
            
            # Apply damage to monster
            encounter_panel._apply_damage_to_monster(target_id, damage_total)
            
            # Log the attack with detailed breakdown
            self._log_attack_result(True, weapon_name, target_monster.monster_name, 
                                  attack_breakdown, target_ac, damage_breakdown)
            
            # Log weapon mastery effects
            self._log_weapon_mastery_effects(mastery_effects)
            
        else:
            # Attack missed - check for Graze mastery
            service = self._get_weapon_attack_service()
            weapon_data = self._build_weapon_dict_from_context(context)
            mastery_effects = service.apply_weapon_mastery_effects(
                weapon_data, self.character_context, target=None,
                hit=False, damage_total=0, attack_total=attack_total
            )

            # Apply any miss-based damage (like Graze)
            graze_data = mastery_effects.get('graze', {})
            graze_damage = graze_data.get('damage', 0)
            if graze_damage > 0:
                encounter_panel._apply_damage_to_monster(target_id, graze_damage)
                self._log_to_parent(f"[GRAZE] {graze_data.get('description', 'Graze damage')}")

            # Attack missed - still show attack roll breakdown
            self._log_attack_result(False, weapon_name, target_monster.monster_name, 
                                  attack_breakdown, target_ac, None)
            
            # Log weapon mastery effects
            self._log_weapon_mastery_effects(mastery_effects)
        
        # Use ability if it's a limited-use ability
        if action_type in [ActionType.SECOND_WIND, ActionType.ACTION_SURGE]:
            ability_name = "Second Wind" if action_type == ActionType.SECOND_WIND else "Action Surge"
            self._use_ability(ability_name)

        # Check if all monsters are defeated after this attack
        living_monsters_after_attack = encounter_panel.get_living_monsters()
        print(f"DEBUG: After attack, {len(living_monsters_after_attack)} monsters remaining")
        
        if not living_monsters_after_attack:
            # All monsters defeated - end combat immediately
            print(f"DEBUG: All monsters defeated, ending combat")
            self._end_combat(encounter_panel)
        else:
            # Monsters still alive, advance turn to next combatant
            print(f"DEBUG: About to advance turn after player attack")
            self._advance_combat_turn(encounter_panel)
    
    def _new_execute_attack(self, action_type: ActionType, context: Dict[str, Any]):
        """NEW ATTACK SYSTEM - Built from scratch with Fighter Extra Attacks support."""
        import random
        
        # Log to combat panel instead of print
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[ATTACK] Starting attack sequence with {context.get('name', 'weapon')}")
                break
            parent = parent.parent()
        
        # Get encounter panel
        encounter_panel = self._get_encounter_panel()
        if not encounter_panel:
            print("NEW ATTACK: No encounter panel found")
            return
        
        # Roll initiative if needed - add action_type to context
        context_with_action = {**context, 'action_type': action_type}
        player_can_act = self._check_and_roll_initiative(encounter_panel, context_with_action)
        if not player_can_act:
            # Monsters go first, player's attack is held and will execute after monsters' turns
            return
        
        # Determine number of attacks based on class level and features
        num_attacks = self._get_attack_count(context)
        
        if num_attacks == 1:
            # Single attack - use existing logic
            self._execute_attack_without_initiative(action_type, context, encounter_panel)
        else:
            # Multiple attacks - new logic with target switching
            self._execute_multiple_attacks(action_type, context, encounter_panel, num_attacks)
    
    def _get_attack_count(self, context: Dict[str, Any]) -> int:
        """Get number of attacks based on class features and levels."""
        class_id = context.get('class_id', '').lower()
        level = context.get('level', 1)
        
        # Fighter gets the most Extra Attacks (based on Fighter levels)
        if class_id == 'fighter':
            if level >= 20:
                return 4  # Four attacks at level 20
            elif level >= 11:
                return 3  # Three attacks at level 11  
            elif level >= 5:
                return 2  # Two attacks at level 5
            else:
                return 1
        
        # Other classes with Extra Attack feature (cap at 2 attacks)
        elif class_id in ['barbarian', 'paladin', 'ranger']:
            if level >= 5:
                return 2  # Only 2 attacks maximum
            else:
                return 1
        
        # Monks get multiple attacks through different mechanics (Flurry of Blows)
        # but their Attack action is still just 1 attack
        elif class_id == 'monk':
            return 1  # Monk uses bonus action for extra attacks
        
        # All other classes get 1 attack
        else:
            return 1
    
    def _execute_multiple_attacks(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, num_attacks: int):
        """Execute multiple attacks, allowing target switching if enemies are killed."""
        
        # Get initial target
        current_target_id = context.get('target_monster_id')
        weapon_name = context.get('name', 'weapon')
        
        # Log start of attack sequence
        class_name = context.get('class_id', 'character').capitalize()
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[ATTACK] {class_name} Extra Attack: Making {num_attacks} attacks with {weapon_name}")
                break
            parent = parent.parent()
        
        for attack_num in range(1, num_attacks + 1):
            # Get living monsters for targeting
            living_monsters = encounter_panel.get_living_monsters()
            if not living_monsters:
                # No targets left
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[ATTACK] No more targets remaining after {attack_num - 1} attacks")
                        break
                    parent = parent.parent()
                break
            
            # Check if original target is still alive
            target_monster = None
            target_switched = False
            
            if current_target_id:
                # Look for original target in living monsters
                for monster in living_monsters:
                    if monster.id == current_target_id:
                        target_monster = monster
                        break
            
            if not target_monster:
                # Original target is dead or missing, switch to first available
                target_monster = living_monsters[0]
                current_target_id = target_monster.id
                target_switched = True
            
            # Update context with current target
            attack_context = {**context, 'target_monster_id': current_target_id}
            
            # Log which attack this is
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    if attack_num == 1:
                        parent.log_panel.log_combat(f"[ATTACK {attack_num}/{num_attacks}] {target_monster.monster_name}")
                    elif target_switched:
                        parent.log_panel.log_combat(f"[EXTRA ATTACK {attack_num}/{num_attacks}] Switching to {target_monster.monster_name}")
                    else:
                        parent.log_panel.log_combat(f"[EXTRA ATTACK {attack_num}/{num_attacks}] {target_monster.monster_name}")
                    break
                parent = parent.parent()
            
            # Execute this attack
            self._execute_attack_without_initiative(action_type, attack_context, encounter_panel)
            
            # Small delay between attacks for readability
            from PyQt6.QtTest import QTest
            QTest.qWait(500)
        
        # After all attacks, check for monster counter-attacks
        living_monsters_after = encounter_panel.get_living_monsters()
        
        if not living_monsters_after:
            # All monsters defeated
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("🏆 All enemies defeated!")
                    break
                parent = parent.parent()
            self._end_combat(encounter_panel)
        else:
            # Advance turn to next combatant after full attack sequence
            self._advance_combat_turn(encounter_panel)
    
    def _execute_attack_without_initiative(self, action_type: ActionType, context: Dict[str, Any], encounter_panel):
        """Execute the attack without rolling initiative (used for immediate attacks and pending attacks)."""
        import random

        # Check if player is attacking from hidden
        is_hidden = False
        if hasattr(encounter_panel, 'player_hidden') and encounter_panel.player_hidden:
            is_hidden = True
            context['is_hidden'] = True
            # After first attack, player is no longer hidden
            encounter_panel.player_hidden = False
            encounter_panel.stealth_dc = 0
            self._log_to_parent("[STEALTH] You attack from hiding, gaining advantage!")

        # Get target info
        target_id = context.get('target_monster_id')
        weapon_name = context.get('name', 'weapon')
        
        target_monster = encounter_panel.get_selected_monster()
        if not target_monster:
            print(f"NEW ATTACK: Target monster {target_id} not found")
            return
        
        # Use the proper advantage-aware attack roll system
        attack_total, attack_breakdown = self._roll_attack(context)
        d20_roll = attack_breakdown['d20_roll']
        prof_bonus = attack_breakdown['proficiency']
        ability_mod = attack_breakdown['ability_mod']
        ability_name = attack_breakdown['ability_name']
        
        # Get roll description for logging (includes advantage/disadvantage info)
        roll_details = attack_breakdown.get('roll_details', {})
        roll_desc = roll_details.get('description', f"d20({d20_roll})")
        
        # attack_total and modifiers are already calculated by _roll_attack()
        # Just get fighting style bonus if needed (though it should already be included)
        fighting_style_attack_bonus = self._get_fighting_style_attack_bonus(context)
        if fighting_style_attack_bonus > 0:
            attack_total += fighting_style_attack_bonus
        target_ac = 12  # TODO: Get from monster data
        
        # Check for critical hit (natural 20, or 19-20/18-20 for Champion Fighter)
        is_critical = self._is_critical_hit(attack_breakdown, context)
        hit = attack_total >= target_ac or is_critical

        # === LOG ATTACK ===
        bonus_parts = [f"+{prof_bonus} prof", f"{ability_mod:+d} {ability_name}"]
        if fighting_style_attack_bonus > 0:
            bonus_parts.append(f"+{fighting_style_attack_bonus} fighting style")
        bonus_str = f" ({' '.join(bonus_parts)})"

        if hit:
            # Add advantage state to context for damage calculation (needed for sneak attack)
            context['advantage_state'] = attack_breakdown.get('advantage_state')
            context['has_advantage'] = attack_breakdown.get('advantage_state') == 'advantage' or is_hidden
            context['has_disadvantage'] = attack_breakdown.get('advantage_state') == 'disadvantage'
            context['is_hidden'] = is_hidden

            # === DAMAGE ROLL ===
            damage_dice, damage_type = self._get_context_damage_profile(context)
            
            # Roll damage dice
            if 'd' in damage_dice:
                num_dice, die_size = damage_dice.split('d')
                dice_rolls = [random.randint(1, int(die_size)) for _ in range(int(num_dice))]
                dice_total = sum(dice_rolls)
            else:
                dice_rolls = [1]
                dice_total = 1
            
            # Apply Savage Attacker feat if applicable (first attack per round only)
            if 'd' in damage_dice:
                service = self._get_weapon_attack_service()
                dice_rolls, savage_desc = service.apply_savage_attacker(
                    dice_rolls, int(num_dice), int(die_size),
                    self.character_context, self.first_attack_this_round
                )
                if savage_desc:
                    self._log_to_parent(f"[SAVAGE ATTACKER] {savage_desc}")
                dice_total = sum(dice_rolls)

            # Apply fighting style effects to dice rolls (e.g., Great Weapon Fighting)
            service = self._get_weapon_attack_service()
            fighting_styles = service.get_character_fighting_styles(self.character_context.get('id'))
            weapon_data = self._build_weapon_dict_from_context(context)
            dice_rolls, style_desc = service.apply_fighting_style_effects(
                dice_rolls, fighting_styles, weapon_data, self.character_context
            )
            if style_desc:
                self._log_to_parent(f"[FIGHTING STYLE] {style_desc}")
            dice_total = sum(dice_rolls)

            # Check for Assassin Surprising Strikes (D&D 2024)
            assassin_bonus = 0
            if self.character_context:
                subclass = self.character_context.get('subclass_id', '').lower()
                level = self.character_context.get('level', 1)
                if 'assassin' in subclass and level >= 3:
                    # Check if it's the first round of combat
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel and hasattr(encounter_panel, 'current_encounter'):
                        current_encounter = encounter_panel.current_encounter
                        if current_encounter and hasattr(current_encounter, 'current_round'):
                            if current_encounter.current_round == 1:
                                # Surprising Strikes: Extra damage equal to Rogue level on first round
                                assassin_bonus = level
                                self._log_to_parent(f"[ASSASSINATE] Surprising Strikes! +{assassin_bonus} damage on first round")

            # === CRITICAL HIT ===
            # Double damage DICE ONLY on critical hit (not modifiers)
            crit_dice_rolls = []
            crit_bonus = 0
            if is_critical:
                # Roll the damage dice again (but NOT modifiers) and add to total
                if 'd' in damage_dice:
                    dice_part = damage_dice.split('+')[0].split('-')[0].strip()
                    if 'd' in dice_part:
                        crit_num_dice, crit_die_size = dice_part.split('d')
                        crit_num_dice = int(crit_num_dice)
                        crit_die_size = int(crit_die_size)
                        # Roll additional dice for critical (same number as base weapon)
                        crit_dice_rolls = [random.randint(1, crit_die_size) for _ in range(crit_num_dice)]
                        crit_bonus = sum(crit_dice_rolls)
                        dice_total += crit_bonus

            # === DAMAGE BONUSES ===
            damage_components: List[Tuple[str, int]] = []
            suppress_ability_damage = context.get('suppress_ability_damage_bonus', False)
            ability_damage_mod = ability_mod
            ability_suppressed_note = None
            if suppress_ability_damage and ability_damage_mod > 0:
                ability_suppressed_note = f"+0 {ability_name} (Cleave)"
                ability_damage_mod = 0
            if ability_damage_mod != 0:
                damage_components.append((ability_name, ability_damage_mod))

            magic_bonus = context.get('damage_bonus', 0)
            if magic_bonus:
                damage_components.append(("Magic", magic_bonus))

            # Fighting style damage bonuses
            service = self._get_weapon_attack_service()
            fighting_styles = service.get_character_fighting_styles(self.character_context.get('id'))
            weapon_data = self._build_weapon_dict_from_context(context)
            action_type = context.get('action_type', 'main_hand')
            fighting_style_bonus = service.get_fighting_style_damage_bonus(
                weapon_data, self.character_context, action_type, fighting_styles
            )
            if fighting_style_bonus > 0:
                damage_components.append(("Fighting Style", fighting_style_bonus))

            # RAGE DAMAGE BONUS - BARBARIAN ONLY (SCALES WITH LEVEL)
            # Check if character is a barbarian and raging
            try:
                class_id = (context.get('class_id') or
                            (self.character_context.get('class_id') if isinstance(self.character_context, dict) else None))
                is_raging = context.get('raging', False)
                if isinstance(self.character_context, dict):
                    is_raging = is_raging or self.character_context.get('raging', False)
                if class_id and class_id.lower() == 'barbarian':
                    if is_raging:
                        rage_bonus = self._get_rage_damage_bonus(context)
                        if rage_bonus > 0:
                            damage_components.append(('Rage', rage_bonus))
                            parent = self.parent()
                            while parent:
                                if hasattr(parent, 'log_panel'):
                                    level = self.character_context.get('level', 1) if isinstance(self.character_context, dict) else 1
                                    parent.log_panel.log_combat(f"[DEBUG] Applied +{rage_bonus} rage damage (barbarian level {level})")
                                    break
                                parent = parent.parent()
                        else:
                            parent = self.parent()
                            while parent:
                                if hasattr(parent, 'log_panel'):
                                    parent.log_panel.log_combat('[DEBUG] Rage active but attack not eligible for bonus (likely ranged/thrown)')
                                    break
                                parent = parent.parent()
                    else:
                        parent = self.parent()
                        while parent:
                            if hasattr(parent, 'log_panel'):
                                parent.log_panel.log_combat(f"[DEBUG] No rage: class={class_id}, raging=False")
                                break
                            parent = parent.parent()
            except Exception as e:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f'[DEBUG] Rage check error: {e}')
                        break
                    parent = parent.parent()
            # === SNEAK ATTACK ===
            # Apply sneak attack damage if conditions are met (solo game - advantage only)
            sneak_attack_damage = 0
            sneak_attack_dice = []
            if self._can_sneak_attack(context):
                sneak_damage_dice = self._get_sneak_attack_damage()
                if 'd' in sneak_damage_dice:
                    try:
                        num_dice, die_size = sneak_damage_dice.split('d')
                        num_dice = int(num_dice)
                        die_size = int(die_size)
                        sneak_attack_dice = [random.randint(1, die_size) for _ in range(num_dice)]
                        sneak_attack_damage = sum(sneak_attack_dice)
                        self._log_to_parent(f"[SNEAK ATTACK] Applied {num_dice}d{die_size} = {sneak_attack_damage} damage!")
                        # Mark sneak attack as used this turn
                        self.sneak_attack_used_this_turn = True
                    except (ValueError, AttributeError):
                        pass

            # Calculate base damage (before smite)
            base_damage = dice_total + sum(value for _, value in damage_components) + sneak_attack_damage

            # === CHECK FOR DIVINE SMITE (PALADIN) ===
            # Only offer smite if:
            # 1. Character is a Paladin
            # 2. Monster would survive the base damage
            # 3. Paladin has spell slots available
            smite_damage_dice = 0
            smite_slot_used = 0
            if self.character_context:
                class_id = self.character_context.get('class_id', '').lower()
                print(f"[DEBUG] Attack class check: class_id='{class_id}', is_paladin={class_id == 'paladin'}")
                if class_id == 'paladin':
                    # Get monster's current HP
                    monster_current_hp = 0
                    if target_monster:
                        # Handle EncounterInstance object (has attributes) or dict
                        if hasattr(target_monster, 'current_hit_points'):
                            monster_current_hp = target_monster.current_hit_points
                        elif isinstance(target_monster, dict):
                            monster_current_hp = (
                                target_monster.get('current_hp') or
                                target_monster.get('hp') or
                                target_monster.get('hit_points') or
                                target_monster.get('current_hit_points') or
                                0
                            )
                        print(f"[DEBUG] Monster HP: {monster_current_hp}, type: {type(target_monster).__name__}")

                    # Check for Divine Smite if:
                    # 1. It's a critical hit (always offer smite on crits)
                    # 2. Monster would survive base damage (prevent obvious overkill)
                    # 3. Monster has substantial HP (let player decide on strong enemies)
                    should_offer_smite = (
                        is_critical or
                        monster_current_hp > base_damage or
                        monster_current_hp >= 10  # Always offer on enemies with 10+ HP
                    )

                    print(f"[DEBUG] Paladin Divine Smite Check: crit={is_critical}, hp={monster_current_hp}, damage={base_damage}, should_offer={should_offer_smite}")

                    if should_offer_smite:
                        smite_damage_dice, smite_slot_used = self._check_divine_smite(
                            is_critical, target_monster, context, base_damage
                        )
                        print(f"[DEBUG] Divine Smite result: dice={smite_damage_dice}, slot={smite_slot_used}")

            # === DIVINE SMITE DAMAGE ===
            smite_damage = 0
            smite_dice_rolls = []
            if smite_damage_dice > 0:
                # Roll smite damage (d8s)
                smite_dice_rolls = [random.randint(1, 8) for _ in range(smite_damage_dice)]

                # Double dice on critical hit
                if is_critical:
                    crit_smite_rolls = [random.randint(1, 8) for _ in range(smite_damage_dice)]
                    smite_dice_rolls.extend(crit_smite_rolls)

                smite_damage = sum(smite_dice_rolls)

            # Calculate total damage
            total_damage = base_damage + smite_damage

            # Check for Death Strike (Assassin level 17 - D&D 2024)
            death_strike_damage = 0
            if self.character_context:
                subclass = self.character_context.get('subclass_id', '').lower()
                level = self.character_context.get('level', 1)
                if 'assassin' in subclass and level >= 17:
                    # Check if it's the first round of combat and this is a sneak attack
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel and hasattr(encounter_panel, 'current_encounter'):
                        current_encounter = encounter_panel.current_encounter
                        if current_encounter and hasattr(current_encounter, 'current_round'):
                            if current_encounter.current_round == 1 and sneak_attack_damage > 0:
                                # Death Strike - target must make CON save or damage is doubled
                                dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
                                from services.proficiency_bonus import get_proficiency_bonus_from_context
                                prof_bonus = get_proficiency_bonus_from_context(self.character_context)
                                death_strike_dc = 8 + dex_mod + prof_bonus

                                # For simplicity, assume target fails save 50% of the time
                                import random
                                if random.randint(1, 20) < death_strike_dc - 10:  # Simplified save
                                    death_strike_damage = total_damage
                                    total_damage *= 2
                                    self._log_to_parent(f"[DEATH STRIKE] Target failed save (DC {death_strike_dc})! Damage doubled: {death_strike_damage} -> {total_damage}")
                                else:
                                    self._log_to_parent(f"[DEATH STRIKE] Target saved (DC {death_strike_dc}), normal damage")

            # === LOG DAMAGE ===
            dice_str = f"[{', '.join(map(str, dice_rolls))}]"
            base_dice_total = dice_total - crit_bonus
            damage_formula_parts = [f"{damage_dice} -> {dice_str} = {base_dice_total}"]
            if ability_suppressed_note:
                damage_formula_parts.append(ability_suppressed_note)
            for label, bonus_value in damage_components:
                if bonus_value != 0:
                    damage_formula_parts.append(f"{bonus_value:+d} {label}")
            if crit_bonus:
                crit_rolls_str = f"[{', '.join(map(str, crit_dice_rolls))}]"
                damage_formula_parts.append(f"+crit {crit_rolls_str} = {crit_bonus}")
            if assassin_bonus > 0:
                damage_formula_parts.append(f"+{assassin_bonus} Surprising Strikes")
                total_damage += assassin_bonus
            if sneak_attack_damage > 0:
                sneak_rolls_str = f"[{', '.join(map(str, sneak_attack_dice))}]"
                damage_formula_parts.append(f"+sneak {sneak_rolls_str} = {sneak_attack_damage}")
            if smite_damage > 0:
                smite_rolls_str = f"[{', '.join(map(str, smite_dice_rolls))}]"
                damage_formula_parts.append(f"+smite {smite_rolls_str} = {smite_damage} radiant")
            if death_strike_damage > 0:
                damage_formula_parts.append(f" x2 Death Strike = {total_damage}")
            damage_formula_text = ' '.join(damage_formula_parts)

            # Apply damage to monster
            encounter_panel._apply_damage_to_monster(target_id, total_damage)
            
            # Apply weapon mastery effects on hit
            mastery_effects = self._apply_weapon_mastery_effects(weapon_name, attack_total, target_ac, hit=True, damage_total=total_damage, context=context)
            
            # Apply mastery status effects to target
            if mastery_effects:
                # Apply Sap effect - target has disadvantage on next attack
                if mastery_effects.get('sap'):
                    target_monster.has_sap_disadvantage = True
                    print(f"[MASTERY] Applied Sap to {target_monster.monster_name} - disadvantage on next attack")
                
                # Apply Vex effect - player has advantage on next attack against this target
                if mastery_effects.get('vex'):
                    self.vex_target_id = target_id
                    print(f"[MASTERY] Applied Vex - advantage on next attack vs {target_monster.monster_name}")
                
                # Log any mastery effects
                self._log_weapon_mastery_effects(mastery_effects)
                if mastery_effects.get('cleave'):
                    self._handle_cleave_followup(action_type, context, encounter_panel, target_id, weapon_name)
            
            # Log to combat panel
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Attack message with critical hit notation
                    attack_type = "[CRITICAL HIT!]" if is_critical else "[ATTACK]"
                    parent.log_panel.log_combat(
                        f"{attack_type} {weapon_name} hits {target_monster.monster_name}! Attack: {roll_desc} (+{prof_bonus} prof {ability_mod:+d} {ability_name}) = {attack_total} vs AC {target_ac}"
                    )

                    # Damage message with critical dice notation
                    parent.log_panel.log_combat(
                        f"💥 Damage: {damage_formula_text} -> {total_damage} damage"
                    )
                    break
                parent = parent.parent()
        else:
            # Apply weapon mastery effects on miss (like Graze)
            mastery_effects = self._apply_weapon_mastery_effects(weapon_name, attack_total, target_ac, hit=False, damage_total=0, context=context)
            
            # Apply any miss-based damage (like Graze)
            graze_damage = mastery_effects.get('graze_damage', 0)
            if graze_damage > 0:
                encounter_panel._apply_damage_to_monster(target_id, graze_damage)
            
            # Miss - log attack
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(
                        f"[ATTACK] {weapon_name} misses {target_monster.monster_name}! Attack: {roll_desc} (+{prof_bonus} prof {ability_mod:+d} {ability_name}) = {attack_total} vs AC {target_ac}"
                    )
                    break
                parent = parent.parent()
        
        # Check if we should continue with initiative-based turns or end combat
        living_monsters_after_attack = encounter_panel.get_living_monsters()
        print(f"NEW ATTACK: After attack, {len(living_monsters_after_attack)} monsters remaining")
        
        if not living_monsters_after_attack:
            print(f"NEW ATTACK: All monsters defeated, ending combat")
            self._end_combat(encounter_panel)
        else:
            # Check if Action Surge extra action is available before monsters react
            if self.character_context.get('action_surge_extra_action_available', False):
                self.character_context['action_surge_extra_action_available'] = False
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("⚡ Action Surge: Taking second action before monsters react!")
                        break
                    parent = parent.parent()
                return  # Skip monster reactions, player gets another action
            else:
                # Advance turn to next combatant using combat manager
                print(f"NEW ATTACK: Advancing turn to next combatant")
                self._advance_combat_turn(encounter_panel)
    
    def _handle_cleave_followup(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, original_target_id: str, weapon_name: str):
        """Resolve Cleave mastery follow-up attack against a random nearby foe."""
        if getattr(self, '_cleave_followup_in_progress', False):
            return

        # Force refresh of living monsters list after the first attack
        living_monsters = []
        if hasattr(encounter_panel, 'get_living_monsters'):
            living_monsters = encounter_panel.get_living_monsters() or []

        # Debug logging
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                monster_names = [getattr(m, 'monster_name', 'Unknown') for m in living_monsters]
                parent.log_panel.log_combat(f"[DEBUG] CLEAVE: Available monsters: {monster_names}")
                break
            parent = parent.parent()

        candidates = [m for m in living_monsters if getattr(m, 'id', None) not in (None, original_target_id) and getattr(m, 'current_hit_points', 0) > 0]
        if not candidates:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("[MASTERY] CLEAVE: No second target within reach")
                    break
                parent = parent.parent()
            return

        import random
        secondary_target = random.choice(candidates)

        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[MASTERY] CLEAVE: Can make an additional attack against another target within 5 feet")
                parent.log_panel.log_combat(f"[MASTERY] CLEAVE: Following through onto {secondary_target.monster_name}")
                break
            parent = parent.parent()

        followup_context = dict(context)
        followup_context['target_monster_id'] = secondary_target.id
        followup_context['is_cleave_followup'] = True
        followup_context['suppress_ability_damage_bonus'] = True

        # Force target selection in encounter panel
        if hasattr(encounter_panel, '_select_monster_card'):
            encounter_panel._select_monster_card(secondary_target.id)
        elif hasattr(encounter_panel, 'selected_monster_id'):
            encounter_panel.selected_monster_id = secondary_target.id

        # Also update target_monster_id for the action panel
        self.target_monster_id = secondary_target.id

        self._cleave_followup_in_progress = True
        try:
            self._execute_attack_without_initiative(action_type, followup_context, encounter_panel)
        finally:
            self._cleave_followup_in_progress = False


    def _execute_remaining_initiative_turns(self, encounter_panel, current_encounter):
        """Execute remaining monster turns in initiative order after player's turn."""
        try:
            # Get current initiative order
            monster_instances = list(getattr(encounter_panel, 'encounter_instances', {}).values())
            initiative_order = current_encounter.get_initiative_order(monster_instances)
            
            # Get monsters that come after the player in initiative order
            monsters_to_attack = []
            player_went = False
            
            for entry in initiative_order:
                if entry['type'] == 'player':
                    player_went = True
                    continue
                
                # Collect monsters that come after the player and are still alive
                if player_went and entry['type'] == 'monster':
                    monster_instance = entry.get('instance')
                    if monster_instance and monster_instance.is_alive and monster_instance.current_hit_points > 0:
                        monsters_to_attack.append(monster_instance)
            
            if monsters_to_attack:
                # Log what's happening
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[TURN] {len(monsters_to_attack)} monsters taking their turns in initiative order...")
                        break
                    parent = parent.parent()
                
                # Use the existing working monster attack system
                monster_data = self._load_monster_data()
                self._execute_monster_attacks_with_delay(monsters_to_attack, monster_data, encounter_panel)
            else:
                # No monsters to attack, player's turn
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[LIGHTNING] Your turn! Choose your next action.")
                        break
                    parent = parent.parent()
                
        except Exception as e:
            print(f"Error executing initiative turns: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_barbarian_level_from_database(self) -> int:
        """Get the character's barbarian class level from database (for multiclass support)."""
        try:
            import sqlite3
            
            if not hasattr(self, 'character_context'):
                print(f"DATABASE ERROR: _get_barbarian_level_from_database - No character_context")
                return 0
                
            if not self.character_context.get('id'):
                print(f"DATABASE ERROR: _get_barbarian_level_from_database - No character ID in context")
                return 0
            
            character_id = self._resolve_character_id()
            print(f"DATABASE: Querying barbarian level for character {character_id}")
            
            # Query character_class_levels table for barbarian levels
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT level FROM character_class_levels 
                WHERE character_id = ? AND class_id = 'barbarian'
            """, (character_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                barbarian_level = result[0]
                print(f"DATABASE SUCCESS: Found barbarian level {barbarian_level} for character {character_id}")
                return barbarian_level
            else:
                print(f"DATABASE ERROR: No multiclass data found for character {character_id}")
                # Check if character is single-class barbarian
                total_level = self.character_context.get('level', 1)
                class_id = self.character_context.get('class_id', '').lower()
                if class_id == 'barbarian':
                    print(f"DATABASE FALLBACK: Using total level {total_level} for single-class barbarian")
                    return total_level
                else:
                    print(f"DATABASE ERROR: Character is not a barbarian (class: {class_id})")
                    return 0
                    
        except sqlite3.Error as e:
            print(f"DATABASE ERROR: SQLite error in _get_barbarian_level_from_database: {e}")
            return 0
        except Exception as e:
            print(f"DATABASE ERROR: Unexpected error in _get_barbarian_level_from_database: {e}")
            return 0
    
    def _get_rage_damage_from_database(self, barbarian_level: int) -> int:
        """Get rage damage bonus from database by looking up barbarian features."""
        print(f"DATABASE: _get_rage_damage_from_database called with barbarian_level={barbarian_level}")
        
        if barbarian_level <= 0:
            print(f"DATABASE ERROR: _get_rage_damage_from_database - Invalid barbarian level: {barbarian_level}")
            return 0
        
        try:
            import sqlite3
            
            print(f"DATABASE: Opening connection to query rage damage for level {barbarian_level}")
            
            # Get character ID from context
            character_id = self.character_context.get('id', '')
            if not character_id:
                print(f"DATABASE ERROR: No character_id in context")
                return 0
            
            # Query barbarian_features table for this character's rage damage
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            query = """
                SELECT rage_damage_bonus FROM barbarian_features 
                WHERE character_id = ?
                AND level = ?
            """
            print(f"DATABASE: Executing query: {query} with character_id={character_id}, level={barbarian_level}")
            
            cursor.execute(query, (character_id, barbarian_level))
            
            result = cursor.fetchone()
            conn.close()
            
            print(f"DATABASE: Query result: {result}")
            
            if result and result[0]:
                try:
                    rage_damage = int(result[0])
                    feature_name = result[1]
                    level_required = result[2]
                    
                    if rage_damage > 0:
                        print(f"DATABASE SUCCESS: Found rage damage +{rage_damage} from '{feature_name}' (level {level_required}) for barbarian level {barbarian_level}")
                        return rage_damage
                    else:
                        print(f"DATABASE ERROR: Rage damage is 0 from '{feature_name}' (level {level_required})")
                        return 0
                        
                except (ValueError, TypeError) as e:
                    print(f"DATABASE ERROR: Could not parse damage_bonus '{result[0]}' as integer: {e}")
                    return 0
            else:
                print(f"DATABASE ERROR: No rage damage found in class_features_detailed for barbarian level {barbarian_level}")
                
                # Debug: Show what IS in the table
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT feature_name, level_required, damage_bonus FROM class_features_detailed 
                    WHERE class_name = 'Barbarian' AND feature_name LIKE '%rage%'
                    ORDER BY level_required
                """)
                debug_results = cursor.fetchall()
                conn.close()
                
                print(f"DATABASE DEBUG: Available barbarian rage features: {debug_results}")
                return 0
                
        except sqlite3.Error as e:
            print(f"DATABASE ERROR: SQLite error in _get_rage_damage_from_database: {e}")
            return 0
        except Exception as e:
            print(f"DATABASE ERROR: Unexpected error in _get_rage_damage_from_database: {e}")
            return 0
    
    def _trigger_monster_counter_attacks(self, encounter_panel):
        """Trigger counter-attacks from all living monsters after player's action."""
        try:
            # Reset Action Surge flags - player's turn is now complete
            if self.character_context.get('action_surge_used_this_turn', False):
                self.character_context['action_surge_used_this_turn'] = False
                self.character_context['action_surge_extra_action_available'] = False
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[DEBUG] Action Surge flags reset - turn complete")
                        break
                    parent = parent.parent()
            
            print(f"DEBUG: _trigger_monster_counter_attacks called, encounter_mode: {encounter_panel.encounter_mode}")
            
            # Check if we're in combat/encounter mode and have living monsters
            if encounter_panel.encounter_mode not in ["combat", "encounter"]:
                print(f"DEBUG: Not in combat/encounter mode, returning")
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

    def _advance_combat_turn(self, encounter_panel):
        """Advance to the next combatant's turn using the CombatManager."""
        try:
            combat_manager = self._get_combat_manager()

            # Check if combat manager is active (attempt to initialize if needed)
            if not combat_manager.combat_active:
                encounter_panel_ref = encounter_panel or self._get_encounter_panel()
                if encounter_panel_ref:
                    context_for_initiative = {**(self.character_context or {}), 'action_type': None}
                    try:
                        self._check_and_roll_initiative(encounter_panel_ref, context_for_initiative)
                    except Exception as e:
                        print(f"Error auto-initializing combat manager: {e}")
                if not combat_manager.combat_active:
                    print(f"DEBUG: Combat manager not active - combat should be initialized before attacking")
                    return

            # Debug: Check current state before advancing
            current_before = combat_manager.get_current_combatant()
            if current_before:
                print(f"DEBUG: Before advance - current combatant: {current_before.name} (type: {current_before.type.value})")
                print(f"DEBUG: Player turn check: {combat_manager.is_player_turn()}")

                # If it's currently the player's turn, mark their action as taken
                if current_before.type.value == 'player':
                    print(f"DEBUG: Marking player action as taken")
                    current_before.has_taken_action = True

                    if self.action_economy_enabled and self.current_combat_session and self.character_id:
                        try:
                            action_economy = getattr(self.current_combat_session, 'action_economy', None)
                            if action_economy:
                                state = action_economy.get_combatant_state(self.character_id)
                                if state:
                                    state.end_turn()
                        except Exception as economy_error:
                            print(f"Error ending action economy turn: {economy_error}")
            else:
                print(f"DEBUG: Before advance - no current combatant")

            # Advance to next combatant
            next_combatant = combat_manager.advance_turn()

            if next_combatant is None:
                print(f"DEBUG: No next combatant, combat may have ended")
                return

            print(f"DEBUG: Advanced to {next_combatant.name}'s turn (type: {next_combatant.type.value})")
            print(f"DEBUG: After advance - Player turn check: {combat_manager.is_player_turn()}")

            # Check if combat should end first (all enemies or all players defeated)
            if combat_manager.is_combat_ended():
                print(f"[COMBAT] Combat has ended")
                end_result = combat_manager.end_combat()
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        if end_result.get('result') == 'victory':
                            parent.log_panel.log_combat("[COMBAT] Victory! All enemies have been defeated!")
                        elif end_result.get('result') == 'defeat':
                            parent.log_panel.log_combat("[COMBAT] Defeat! Your party has fallen...")
                        break
                    parent = parent.parent()
                return

            # If it's a monster's turn, execute their action
            if next_combatant.type.value == 'monster':
                # Check if monster is still alive in the combat manager
                if not next_combatant.is_alive:
                    print(f"DEBUG: Monster {next_combatant.name} is dead (is_alive=False), skipping their turn")
                    # Skip this dead monster and continue to next turn
                    self._continue_combat_turn_cycle(encounter_panel)
                    return

                result = combat_manager.execute_monster_turn(next_combatant.id)

                if 'error' not in result:
                    # Log all attack results (hits and misses) first
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            # Log detailed attack information from result
                            attacks = result.get('attacks', [])
                            if attacks:
                                for attack in attacks:
                                    if attack.get('hit'):
                                        # Enhanced hit logging with details like player attacks
                                        d20_roll = attack.get('d20_roll', '?')
                                        attack_bonus = attack.get('attack_bonus', 0)
                                        attack_total = attack.get('attack_roll', 0)
                                        target_ac = attack.get('target_ac', '?')
                                        damage = attack.get('damage', 0)
                                        action_name = attack.get('action_name', 'Attack')
                                        is_critical = attack.get('is_critical', False)
                                        damage_dice = attack.get('damage_dice', '?')

                                        # Format attack type
                                        attack_type = "[CRITICAL HIT!]" if is_critical else "[MONSTER ATTACK]"

                                        # Log attack roll with breakdown
                                        parent.log_panel.log_combat(
                                            f"{attack_type} {next_combatant.name} {action_name} hits! Attack: d20({d20_roll}) +{attack_bonus} = {attack_total} vs AC {target_ac}"
                                        )

                                        # Log damage with dice breakdown
                                        if damage_dice and damage_dice != '?':
                                            parent.log_panel.log_combat(f"💥 Damage: {damage_dice} = {damage} damage")
                                        else:
                                            parent.log_panel.log_combat(f"💥 Damage: {damage} damage")

                                        # Log any effects (conditions, saves)
                                        for effect in attack.get('effects', []):
                                            parent.log_panel.log_combat(f"[EFFECT] {effect}")
                                    else:
                                        # Enhanced miss logging with details
                                        d20_roll = attack.get('d20_roll', '?')
                                        attack_bonus = attack.get('attack_bonus', 0)
                                        attack_total = attack.get('attack_roll', 0)
                                        target_ac = attack.get('target_ac', '?')
                                        action_name = attack.get('action_name', 'Attack')

                                        parent.log_panel.log_combat(
                                            f"[MONSTER ATTACK] {next_combatant.name} {action_name} misses! Attack: d20({d20_roll}) +{attack_bonus} = {attack_total} vs AC {target_ac}"
                                        )
                            break
                        parent = parent.parent()

                    # Now handle damage if any
                    total_damage = result.get('total_damage', 0)
                    if total_damage > 0:
                        # Get HP before damage for proper logging (from character sheet, not context)
                        parent = self.parent()
                        hp_before = 0
                        max_hp = 0
                        while parent:
                            if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                                character_data = parent.character_sheet.character_data
                                hp_before = character_data.get('current_hit_points', character_data.get('hit_points_current', 0))
                                max_hp = character_data.get('max_hit_points', character_data.get('hit_points_max', 0))
                                break
                            parent = parent.parent()

                        # Use the existing damage application system that properly updates UI
                        self._apply_damage_to_player(total_damage, encounter_panel, "physical")

                        # Get HP after damage for logging (from character sheet, not context)
                        parent = self.parent()
                        hp_after = 0
                        while parent:
                            if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                                character_data = parent.character_sheet.character_data
                                hp_after = character_data.get('current_hit_points', character_data.get('hit_points_current', 0))
                                break
                            parent = parent.parent()

                        actual_damage_taken = hp_before - hp_after

                        # Log HP changes (only if damage was actually dealt)
                        parent = self.parent()
                        while parent:
                            if hasattr(parent, 'log_panel'):
                                parent.log_panel.log_combat(f"    Player HP: {hp_before}/{max_hp} -> {hp_after}/{max_hp}")
                                if actual_damage_taken != total_damage:
                                    parent.log_panel.log_combat(f"    [SHIELD] RAGE RESISTANCE: {total_damage} damage reduced to {actual_damage_taken}")
                                break
                            parent = parent.parent()

                    # Continue to next turn (but don't recurse infinitely)
                    self._continue_combat_turn_cycle(encounter_panel)
                else:
                    print(f"ERROR: Monster turn failed: {result['error']}")
                    # Continue to next turn anyway to avoid getting stuck
                    self._continue_combat_turn_cycle(encounter_panel)

            elif next_combatant.type.value == 'player':
                # Player's turn - log and reset turn state
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[LIGHTNING] Your turn! Choose your next action.")
                        break
                    parent = parent.parent()

                # Reset action economy/turn buffs for new player turn
                self._log_player_turn_start()

        except Exception as e:
            print(f"CRITICAL ERROR: Failed to advance combat turn: {e}")
            import traceback
            traceback.print_exc()

    def _is_monster_alive_in_encounter(self, encounter_panel, monster_id: str) -> bool:
        """Check if a monster is still alive in the encounter panel."""
        try:
            # Get living monsters from encounter panel
            living_monsters = encounter_panel.get_living_monsters()
            for monster in living_monsters:
                if monster.id == monster_id and monster.is_alive and monster.current_hit_points > 0:
                    return True
            return False
        except Exception as e:
            print(f"ERROR: Failed to check monster alive status: {e}")
            return False

    def _continue_combat_turn_cycle(self, encounter_panel):
        """Continue the combat turn cycle with a small delay to prevent infinite recursion."""
        try:
            # Use QTimer to avoid infinite recursion and give UI time to update
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._advance_combat_turn(encounter_panel))
        except Exception as e:
            print(f"ERROR: Failed to continue combat turn cycle: {e}")

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
                    
                    # If player has a pending attack from initiative, execute it now
                    if self.pending_attack:
                        QTimer.singleShot(500, self._execute_pending_attack)
            
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
                    
                    # If player has a pending attack from initiative, execute it now
                    if self.pending_attack:
                        QTimer.singleShot(500, self._execute_pending_attack)
        except Exception as e:
            print(f"Error continuing monster attacks: {e}")
    
    def _end_combat(self, encounter_panel):
        """End combat when all monsters are defeated."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("🏆 Victory! All monsters have been defeated!")
                    parent.log_panel.log_combat("[ATTACK] Combat has ended. You may now rest or explore.")
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
    
    def _execute_pending_attack(self):
        """Execute the player's attack that was held due to losing initiative."""
        if not self.pending_attack:
            return
        
        # Get the stored attack data
        action_type = self.pending_attack.get('action_type')
        context = self.pending_attack.get('context')
        encounter_panel = self.pending_attack.get('encounter_panel')
        
        # Clear the pending attack
        self.pending_attack = None
        
        # Log that player is now taking their held action
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat("[ACTION] Executing your held attack...")
                break
            parent = parent.parent()
        
        # Execute the attack based on the action type without rolling initiative again
        if action_type == ActionType.ATTACK_MAIN_HAND:
            self._execute_attack_without_initiative(ActionType.ATTACK_MAIN_HAND, context, encounter_panel)
        elif action_type == ActionType.ATTACK_OFF_HAND:
            self._execute_attack_without_initiative(ActionType.ATTACK_OFF_HAND, context, encounter_panel)
    
    def _log_player_turn_start(self):
        """Log that it's the player's turn again."""
        try:
            # Reset sneak attack for new turn (once per turn limit)
            if hasattr(self, 'sneak_attack_used_this_turn'):
                self.sneak_attack_used_this_turn = False

            # Handle rage turn countdown
            self._update_rage_state()

            # Handle Reckless Attack automatic deactivation
            self._update_reckless_attack_state()
            
            # Reset Savage Attacker for new turn
            self.first_attack_this_round = True

            # Reset action economy availability at the start of the player's turn
            if self.action_economy_enabled and self.current_combat_session and self.character_id:
                try:
                    action_economy = getattr(self.current_combat_session, 'action_economy', None)
                    if action_economy:
                        state = action_economy.get_combatant_state(self.character_id)
                        if state:
                            round_number = getattr(action_economy, 'current_round', state.current_round) or 1
                            turn_position = getattr(action_economy, 'current_turn', state.current_turn_in_initiative) or 0
                            state.start_new_turn(round_number, turn_position)
                            self._refresh_action_availability()
                            self._update_action_economy_display()
                except Exception as economy_error:
                    print(f"Error resetting action economy for player turn: {economy_error}")

            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("[LIGHTNING] Your turn! Choose your next action.")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log player turn start: {e}")
    
    def _update_rage_state(self):
        """Update rage state at the start of each turn."""
        if not self.character_context.get('raging', False):
            return
            
        # Decrease rage turns remaining
        turns_remaining = self.character_context.get('rage_turns_remaining', 0)
        if turns_remaining <= 1:
            # Rage ends
            self.character_context['raging'] = False
            self.character_context['rage_turns_remaining'] = 0

            # Trigger automatic subclass features when rage ends
            character_id = self._resolve_character_id()
            if character_id:
                try:
                    from services.subclass_action_integration import subclass_action_integration
                    automatic_triggers = subclass_action_integration.trigger_automatic_feature(character_id, "rage_end")

                    # Log any automatic feature deactivations
                    for trigger_result in automatic_triggers:
                        if trigger_result.get('success'):
                            feature_name = trigger_result.get('feature_name', 'Unknown Feature')
                            parent = self.parent()
                            while parent:
                                if hasattr(parent, 'log_panel'):
                                    parent.log_panel.log_combat(f"[AUTO] {feature_name} deactivated")
                                    break
                                parent = parent.parent()
                except Exception as e:
                    print(f"Error triggering rage end features: {e}")

            # Refresh weapon cards to remove rage damage bonus
            self._create_weapon_cards()
            self._update_visible_cards()

            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("💨 RAGE ends!")
                        break
                    parent = parent.parent()
            except Exception as e:
                print(f"Error logging rage end: {e}")
        else:
            # Continue rage
            self.character_context['rage_turns_remaining'] = turns_remaining - 1
    
    def _update_reckless_attack_state(self):
        """Update Reckless Attack state at the start of each turn."""
        # Reckless Attack automatically deactivates at start of barbarian's next turn
        if self.character_context.get('reckless_attack_active', False):
            self.character_context['reckless_attack_active'] = False
            
            # Update the card appearance
            if ActionType.RECKLESS_ATTACK in self.action_cards:
                card = self.action_cards[ActionType.RECKLESS_ATTACK]
                card.name_label.setText("Reckless Attack")
                card.setProperty("reckless_active", False)
                card.setStyleSheet("")
            
            # Log the deactivation
            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("WARNING: Reckless Attack ended - you no longer have advantage, but enemies no longer have advantage against you.")
                        break
                    parent = parent.parent()
            except Exception as e:
                print(f"Error logging reckless attack end: {e}")
    
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
    
    def _is_critical_hit(self, attack_breakdown: dict, context: Dict[str, Any]) -> bool:
        """Check if an attack is a critical hit based on character class/subclass."""
        d20_roll = attack_breakdown.get('d20_result', 0)
        roll_details = attack_breakdown.get('roll_details', {})

        # Get critical hit range based on class/subclass
        critical_range = [20]
        class_id = context.get('class_id', '').lower()
        subclass = context.get('subclass_id', '').lower()
        level = context.get('level', 1)

        if class_id == 'fighter' and subclass == 'champion':
            if level >= 15:
                critical_range = [18, 19, 20]  # 18-20 at level 15+
            elif level >= 3:
                critical_range = [19, 20]      # 19-20 at level 3+

        # For advantage/disadvantage, check if ANY die was in the critical range
        all_rolls = roll_details.get('rolls', [d20_roll])
        for roll in all_rolls:
            if roll in critical_range:
                return True

        # For normal rolls, just check the single die
        return d20_roll in critical_range

    def _roll_attack(self, context: Dict[str, Any]) -> tuple[int, dict]:
        """Roll an attack roll (d20 + modifiers) with advantage/disadvantage. Returns (total, breakdown)."""
        _, damage_type = self._get_context_damage_profile(context)
        from services.advantage_system import advantage_system, RollType, AdvantageState
        
        # Calculate attack bonus components
        from services.proficiency_bonus import get_proficiency_bonus_from_context
        prof_bonus = get_proficiency_bonus_from_context(context)
        
        # Get ability modifier
        weapon_props = self._get_context_weapon_properties(context)
        if 'finesse' in weapon_props:
            str_mod = (context.get('strength', 10) - 10) // 2
            dex_mod = (context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
            ability_name = "STR" if str_mod >= dex_mod else "DEX"
        elif 'ranged' in weapon_props or damage_type == 'ranged':
            ability_mod = (context.get('dexterity', 10) - 10) // 2
            ability_name = "DEX"
        else:
            ability_mod = (context.get('strength', 10) - 10) // 2
            ability_name = "STR"
        
        # Get advantage/disadvantage sources
        advantage_sources = advantage_system.get_common_advantage_sources(RollType.ATTACK, context)
        disadvantage_sources = advantage_system.get_common_disadvantage_sources(RollType.ATTACK, context)

        # Check if attacking from hidden
        if context.get('is_hidden', False):
            advantage_sources.append("Attacking from Hidden")
        
        # Check for pending advantage from Lucky/Inspiration triangle clicks
        if hasattr(self, 'resource_manager') and self.resource_manager:
            if self.resource_manager.has_pending_advantage():
                consumed_type = self.resource_manager.consume_pending_advantage()
                if consumed_type:
                    advantage_sources.append(f"{consumed_type.title()} (triangle click)")
                    # Log to combat panel
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"⚡ Using {consumed_type.title()}! Next attack has advantage")
                            break
                        parent = parent.parent()
        
        # Check for Reckless Attack advantage (only on Strength-based attacks)
        if (self.character_context.get('reckless_attack_active', False) and 
            ability_name == "STR"):
            advantage_sources.append("Reckless Attack")
        
        # Check for Vex weapon mastery advantage
        current_target_id = context.get('target_monster_id')
        if self.vex_target_id and self.vex_target_id == current_target_id:
            advantage_sources.append("Vex weapon mastery")
            self.vex_target_id = None  # Consume the Vex advantage
        
        # Calculate final advantage state
        advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)
        
        # Roll with advantage/disadvantage
        total_modifier = prof_bonus + ability_mod
        base_roll_total, roll_breakdown = advantage_system.roll_d20_with_advantage(advantage_state, 0)  # Don't add modifier yet
        base_roll = roll_breakdown['d20_result']
        
        magic_bonus = context.get('attack_bonus', 0)
        total_bonus = prof_bonus + ability_mod + magic_bonus
        total = base_roll + total_bonus
        
        # Create breakdown for logging (include advantage/disadvantage info)
        breakdown = {
            'd20_roll': base_roll,
            'proficiency': prof_bonus,
            'ability_mod': ability_mod,
            'roll_details': roll_breakdown,  # Include full advantage/disadvantage details
            'ability_name': ability_name,
            'magic_bonus': magic_bonus,
            'total_bonus': total_bonus,
            'total': total,
            'advantage_state': advantage_state,
            'advantage_sources': advantage_sources,
            'disadvantage_sources': disadvantage_sources,
            'roll_details': roll_breakdown  # Include the full roll breakdown
        }
        
        return total, breakdown
    
    def _roll_damage(self, context: Dict[str, Any]) -> tuple[int, dict]:
        """Roll damage dice with ability modifier. Returns (total, breakdown)."""
        import random
        
        # Get damage dice from context or use default
        damage_dice, damage_type = self._get_context_damage_profile(context)  # Default 1d6
        
        # Calculate ability modifier for damage
        weapon_props = self._get_context_weapon_properties(context)
        if 'finesse' in weapon_props:
            str_mod = (context.get('strength', 10) - 10) // 2
            dex_mod = (context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)
            ability_name = "STR" if str_mod >= dex_mod else "DEX"
        elif 'ranged' in weapon_props or damage_type == 'ranged':
            ability_mod = (context.get('dexterity', 10) - 10) // 2
            ability_name = "DEX"
        else:
            ability_mod = (context.get('strength', 10) - 10) // 2
            ability_name = "STR"
        
        # Magic weapon damage bonus
        magic_bonus = context.get('damage_bonus', 0)
        
        # Get all feature-based damage bonuses
        feature_bonuses = self._get_all_damage_bonuses(context)
        total_feature_bonus = sum(feature_bonuses.values())
        
        # Add rage bonus directly if the feature system isn't working
        rage_bonus = 0
        raging = self.character_context.get('raging', False)
        class_id = self.character_context.get('class_id', '').lower()
        print(f"RAGE CHECK: raging={raging}, class_id='{class_id}', context_keys={list(self.character_context.keys()) if self.character_context else 'None'}")
        
        if (raging and class_id == 'barbarian'):
            weapon_props = self._get_context_weapon_properties(context)
            is_ranged = 'ranged' in [p.lower() for p in weapon_props] if weapon_props else False
            if not is_ranged:
                rage_bonus = 2
                feature_bonuses['Rage'] = rage_bonus
                total_feature_bonus += rage_bonus
                print(f"RAGE BONUS APPLIED: +{rage_bonus} damage")
        
        total_modifier = ability_mod + magic_bonus + total_feature_bonus
        
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
                
                # Apply Savage Attacker feat if applicable (first attack per round only)
                dice_rolls = self._apply_savage_attacker(dice_rolls, num_dice, die_size, context)
                
                # Apply Great Weapon Fighting style if applicable
                dice_rolls = self._apply_fighting_style_effects(dice_rolls, context)
                
                dice_total = sum(dice_rolls)
                total = dice_total + total_modifier
                
                breakdown = {
                    'damage_dice': damage_dice,
                    'num_dice': num_dice,
                    'die_size': die_size,
                    'dice_rolls': dice_rolls,
                    'dice_total': dice_total,
                    'ability_mod': ability_mod,
                    'ability_name': ability_name,
                    'magic_bonus': magic_bonus,
                    'feature_bonuses': feature_bonuses,
                    'total_feature_bonus': total_feature_bonus,
                    'total_modifier': total_modifier,
                    'total': max(1, total)  # Minimum 1 damage
                }
                
                # Apply sneak attack if applicable
                breakdown = self._apply_sneak_attack(context, breakdown)
                
                return max(1, breakdown['total']), breakdown
            except (ValueError, IndexError) as e:
                # Fallback if parsing fails
                fallback_total = max(1, total_modifier) if total_modifier > 0 else 1
                breakdown = {
                    'damage_dice': damage_dice,
                    'dice_rolls': [],
                    'dice_total': 0,
                    'ability_mod': ability_mod,
                    'ability_name': ability_name,
                    'magic_bonus': magic_bonus,
                    'feature_bonuses': feature_bonuses,
                    'total_feature_bonus': total_feature_bonus,
                    'total_modifier': total_modifier,
                    'total': fallback_total,
                    'error': 'Failed to parse damage dice'
                }
                return fallback_total, breakdown
        else:
            # Static damage value
            static_damage = int(damage_dice) if damage_dice.isdigit() else 1
            static_total = static_damage + total_feature_bonus
            breakdown = {
                'damage_dice': damage_dice,
                'dice_rolls': [],
                'dice_total': static_damage,
                'ability_mod': 0,
                'ability_name': '',
                'magic_bonus': 0,
                'feature_bonuses': feature_bonuses,
                'total_feature_bonus': total_feature_bonus,
                'total_modifier': total_feature_bonus,
                'total': static_total
            }
            return static_total, breakdown
    
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
                    
                    # Get advantage/disadvantage info
                    advantage_state = attack_breakdown.get('advantage_state')
                    roll_details = attack_breakdown.get('roll_details', {})
                    
                    # Build d20 roll display with advantage/disadvantage
                    if advantage_state and advantage_state.value != 'normal':
                        roll_desc = roll_details.get('description', f'd20({d20})')
                    else:
                        roll_desc = f'd20({d20})'
                    
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
                        # Check for critical hit
                        is_critical = damage_breakdown.get('is_critical', False) or d20 == 20
                        
                        # Build damage roll breakdown
                        dice_rolls = damage_breakdown['dice_rolls']
                        dice_total = damage_breakdown['dice_total']
                        dam_ability = damage_breakdown['ability_mod']
                        dam_ability_name = damage_breakdown['ability_name']
                        dam_magic = damage_breakdown['magic_bonus']
                        feature_bonuses = damage_breakdown.get('feature_bonuses', {})
                        
                        # Add rage bonus directly to logging if missing
                        if (self.character_context.get('raging', False) and 
                            self.character_context.get('class_id', '').lower() == 'barbarian' and
                            'Rage' not in feature_bonuses):
                            feature_bonuses['Rage'] = 2
                            damage_breakdown['total'] += 2
                            
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
                            
                            # Add all feature bonuses dynamically
                            for feature_name, bonus in feature_bonuses.items():
                                if bonus != 0:
                                    sign = "+" if bonus >= 0 else ""
                                    damage_parts.append(f"{sign}{bonus} {feature_name.lower()}")
                            
                            damage_bonus_str = f" ({' '.join(damage_parts)})" if damage_parts else ""
                            
                            # Add critical hit dice to display (show the extra dice rolled)
                            crit_dice = damage_breakdown.get('critical_dice', [])
                            crit_bonus = damage_breakdown.get('critical_bonus', 0)
                            crit_str = ""
                            if crit_dice:
                                crit_str = f" + [{', '.join(map(str, crit_dice))}] = {crit_bonus} (critical)"
                            
                            # Log with critical hit notation
                            if is_critical:
                                parent.log_panel.log_combat(
                                    f"[CRITICAL HIT!] {weapon} hits {target}! Attack: {roll_desc}{bonus_str} = {total} vs AC {target_ac}"
                                )
                            else:
                                parent.log_panel.log_combat(
                                    f"[ATTACK] {weapon} hits {target}! Attack: {roll_desc}{bonus_str} = {total} vs AC {target_ac}"
                                )
                            parent.log_panel.log_combat(
                                f"[DAMAGE] {dice_str} = {dice_total}{damage_bonus_str}{crit_str} = {damage_total} damage"
                            )
                        else:
                            parent.log_panel.log_combat(
                                f"[ATTACK] {weapon} hits {target}! Attack: {roll_desc}{bonus_str} = {total} vs AC {target_ac} for {damage_total} damage"
                            )
                    else:
                        # Miss - just show attack roll
                        parent.log_panel.log_combat(
                            f"[ATTACK] {weapon} misses {target}! Attack: {roll_desc}{bonus_str} = {total} vs AC {target_ac}"
                        )
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Could not log attack: {e}")
    
    def _check_and_roll_initiative(self, encounter_panel, context: Dict[str, Any]) -> bool:
        """Check if initiative needs to be rolled and roll it.
        Returns True if player can continue their action, False if monsters go first.
        """
        try:
            # Check if encounter has initiative rolled already
            current_encounter = getattr(encounter_panel, 'current_encounter', None)
            
            if not current_encounter or current_encounter.initiative_rolled:
                return True  # Initiative already handled, player can continue
            
            # Get player DEX modifier for initiative
            player_dex_mod = (context.get('dexterity', 10) - 10) // 2
            
            # Get monster instances and monster data
            monster_instances = list(getattr(encounter_panel, 'encounter_instances', {}).values())
            
            # Load monster data from monsters_full.json for DEX stats
            monster_data = self._load_monster_data()
            
            # Roll initiative for everyone
            player_initiative = current_encounter.roll_initiative(
                player_dex_mod, monster_instances, monster_data, self.character_context, self.character_features
            )
            
            # Get initiative order
            initiative_order = current_encounter.get_initiative_order(monster_instances)
            
            # Log initiative results
            self._log_initiative_results(player_initiative, initiative_order, player_dex_mod)
            
            # Start combat officially
            current_encounter.start_combat()

            # Switch encounter panel to combat mode
            encounter_panel.set_combat_mode()

            # Set up combat manager with combatants
            self._setup_combat_manager(encounter_panel, initiative_order)
            
            # Check if player goes first - if not, store pending attack and execute monster attacks first
            print(f"⚔ [DEBUG] Initiative check - first actor type: {initiative_order[0]['type'] if initiative_order else 'no order'}")
            print(f"⚔ [DEBUG] Initiative order length: {len(initiative_order) if initiative_order else 0}")
            
            if initiative_order and initiative_order[0]['type'] == 'monster':
                print(f"⚔ [DEBUG] Monsters go first! Storing pending attack and executing monster turns...")
                # Store the pending attack to execute after monsters' turns
                self.pending_attack = {
                    'action_type': context.get('action_type'),
                    'context': context,
                    'encounter_panel': encounter_panel
                }
                self._execute_monster_turns_before_player(encounter_panel, initiative_order, monster_data)
                return False  # Player doesn't go first, their action is held
            
            print(f"⚔ [DEBUG] Player goes first, continuing with their action")
            return True  # Player goes first, can continue with their action
            
        except Exception as e:
            print(f"Error rolling initiative: {e}")
            return True  # On error, allow action to continue
    
    def _load_monster_data(self) -> Dict[str, Dict]:
        """Load monster data from database for stats lookups."""
        try:
            import sqlite3
            import json
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("""SELECT name, type, armor_class, hit_points, 
                             strength, dexterity, constitution, intelligence, wisdom, charisma,
                             challenge_rating, experience_points, actions FROM monsters""")
            monster_rows = cursor.fetchall()
            
            # Create lookup dict by monster name with full combat stats
            monster_lookup = {}
            for row in monster_rows:
                name, monster_type, ac, hp, str_val, dex, con, int_val, wis, cha, cr, xp, actions = row
                
                # Parse actions JSON if it exists
                parsed_actions = []
                if actions:
                    try:
                        parsed_actions = json.loads(actions) if isinstance(actions, str) else actions
                    except:
                        parsed_actions = []
                
                monster_data = {
                    'name': name,
                    'type': {'type': monster_type},
                    'armor_class': ac if ac else 10,
                    'hit_points': hp if hp else 1,
                    'strength': str_val if str_val else 10,
                    'dexterity': dex if dex else 10,
                    'constitution': con if con else 10,
                    'intelligence': int_val if int_val else 10,
                    'wisdom': wis if wis else 10,
                    'charisma': cha if cha else 10,
                    'challenge_rating': cr,
                    'experience_points': xp if xp else 0,
                    'action': parsed_actions,  # Full actions for attacks
                    # Legacy compatibility 
                    'dex': dex if dex else 10,
                    'cr': cr
                }
                monster_lookup[name] = monster_data
            
            conn.close()
            return monster_lookup
                
        except Exception as e:
            print(f"Error loading monster data: {e}")
            return {}
    
    def _log_initiative_results(self, player_initiative: int, initiative_order: list, player_dex_mod: int):
        """Log the initiative results to show turn order."""
        try:
            # Get encounter panel to access the current encounter with roll data
            encounter_panel = self._get_encounter_panel()
            current_encounter = getattr(encounter_panel, 'current_encounter', None) if encounter_panel else None
            
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Clear separator for initiative
                    parent.log_panel.log_combat("=" * 50)
                    parent.log_panel.log_combat("[DICE] ROLLING INITIATIVE FOR COMBAT!")
                    parent.log_panel.log_combat("=" * 50)
                    
                    # Log player initiative with advantage/disadvantage info
                    initiative_breakdown = getattr(current_encounter, '_player_initiative_breakdown', None) if current_encounter else None
                    if initiative_breakdown:
                        roll_desc = initiative_breakdown.get('description', f'd20({player_initiative - player_dex_mod})')
                        dex_bonus_str = f" +{player_dex_mod} DEX" if player_dex_mod >= 0 else f" {player_dex_mod} DEX"
                        parent.log_panel.log_combat(f"🎲 Player Initiative: {roll_desc}{dex_bonus_str} = {player_initiative}")
                    else:
                        # Fallback for old format
                        d20_roll = player_initiative - player_dex_mod
                        dex_bonus_str = f"+{player_dex_mod}" if player_dex_mod >= 0 else str(player_dex_mod)
                        parent.log_panel.log_combat(f"🎲 Player Initiative: d20({d20_roll}) {dex_bonus_str} DEX = {player_initiative}")
                    
                    # Log monster initiatives with dice rolls
                    monster_rolls = getattr(current_encounter, 'monster_initiative_rolls', {}) if current_encounter else {}
                    for entry in initiative_order:
                        if entry['type'] == 'monster':
                            # Try to find the roll data for this monster
                            roll_data = None
                            for instance_id, roll_info in monster_rolls.items():
                                if roll_info['name'] == entry['name']:
                                    roll_data = roll_info
                                    break
                            
                            if roll_data:
                                d20_roll = roll_data['d20_roll']
                                dex_mod = roll_data['dex_modifier']
                                dex_bonus_str = f"+{dex_mod}" if dex_mod >= 0 else str(dex_mod)
                                parent.log_panel.log_combat(f"🎲 {entry['name']} Initiative: d20({d20_roll}) {dex_bonus_str} DEX = {entry['initiative']}")
                            else:
                                # Fallback if no roll data
                                parent.log_panel.log_combat(f"🎲 {entry['name']} Initiative: {entry['initiative']}")
                    
                    # Log turn order prominently
                    parent.log_panel.log_combat("-" * 30)
                    turn_order = " -> ".join([f"{entry['name']} ({entry['initiative']})" for entry in initiative_order])
                    parent.log_panel.log_combat(f"[TURN] TURN ORDER: {turn_order}")
                    parent.log_panel.log_combat("-" * 30)
                    
                    # Announce who goes first
                    if initiative_order:
                        first_actor = initiative_order[0]
                        if first_actor['type'] == 'player':
                            parent.log_panel.log_combat("[TURN] You go first!")
                        else:
                            parent.log_panel.log_combat(f"[FIRST TURN] {first_actor['name']} goes first!")
                    
                    parent.log_panel.log_combat("=" * 50)
                    break
                parent = parent.parent()
                
        except Exception as e:
            print(f"Could not log initiative: {e}")
    
    def _execute_monster_turns_before_player(self, encounter_panel, initiative_order: list, monster_data: dict):
        """Execute monster attacks for all monsters that go before the player."""
        try:
            print("⚔ [DEBUG] Executing monster turns before player...")
            initiative_summary = [f"{e['name']}({e['type']})" for e in initiative_order]
            print(f"⚔ [DEBUG] Initiative order: {initiative_summary}")
            print(f"⚔ [DEBUG] Encounter instances: {list(encounter_panel.encounter_instances.keys())}")
            
            for entry in initiative_order:
                if entry['type'] == 'player':
                    print(f"⚔ [DEBUG] Reached player turn, stopping monster turns")
                    break  # Stop when we reach player turn
                
                if entry['type'] == 'monster':
                    monster_instance = entry.get('instance')
                    monster_name = entry['name']
                    
                    print(f"⚔ [DEBUG] Processing monster turn: {monster_name}")
                    
                    # Get monster stats
                    monster_stats = monster_data.get(monster_name, {})
                    
                    print(f"⚔ [DEBUG] Monster instance found: {monster_instance is not None}")
                    print(f"⚔ [DEBUG] Monster stats found: {monster_stats != {}}")
                    if monster_instance:
                        print(f"⚔ [DEBUG] Monster is alive: {monster_instance.is_alive}")
                    
                    if monster_instance and monster_instance.is_alive and monster_stats:
                        print(f"⚔ [DEBUG] Executing attack for {monster_name}")
                        self._execute_monster_attack(monster_instance, monster_stats, encounter_panel)
                    else:
                        print(f"⚔ [DEBUG] Skipping {monster_name} - missing data or not alive")

            # Reset all monster action flags after initial attacks so they can act in proper turn order
            try:
                combat_manager = self._get_combat_manager()
                if combat_manager and combat_manager.combat_active:
                    for combatant in combat_manager.combatants.values():
                        if combatant.combatant_type == 'monster':
                            combatant.has_taken_action = False
                    print(f"⚔ [DEBUG] Reset action flags for all monsters after initial attacks")
            except Exception as reset_error:
                print(f"⚔ [DEBUG] Could not reset monster action flags: {reset_error}")

        except Exception as e:
            print(f"⚔ [ERROR] Error executing monster turns: {e}")
            import traceback
            traceback.print_exc()
    
    def _execute_monster_attack(self, monster_instance, monster_stats: dict, encounter_panel):
        """Execute a single monster's attack against the player."""
        try:
            print(f"⚔ [DEBUG] {monster_instance.monster_name} is attacking!")

            # Try to use the combat manager if available and set up
            try:
                combat_manager = self._get_combat_manager()
                if combat_manager.combat_active and monster_instance.id in combat_manager.combatants:
                    print(f"⚔ [DEBUG] Using combat manager for {monster_instance.monster_name}")
                    result = combat_manager.execute_monster_turn(monster_instance.id)

                    if 'error' not in result:
                        # Log and apply results
                        self._handle_combat_manager_result(result, monster_instance, encounter_panel)
                        return
                    else:
                        print(f"⚔ [DEBUG] Combat manager error: {result['error']}, falling back to old system")
                else:
                    print(f"⚔ [DEBUG] Combat manager not ready, using old system")
            except Exception as e:
                print(f"⚔ [DEBUG] Combat manager failed: {e}, using old system")

            # Fall back to the original system if combat manager isn't available
            print(f"⚔ [DEBUG] Using original attack system for {monster_instance.monster_name}")
            
            # Get monster's actions
            actions = monster_stats.get('action', [])
            if not actions:
                print(f"⚔ [DEBUG] {monster_instance.monster_name} has no actions available")
                return  # No attacks available
            
            print(f"⚔ [DEBUG] {monster_instance.monster_name} has {len(actions)} actions available")
            
            # Check if first action is Multiattack
            first_action = actions[0]
            if first_action.get('name', '').lower() == 'multiattack':
                # Parse multiattack to determine number of attacks and which attack to use
                multiattack_entries = first_action.get('entries', [])
                if multiattack_entries:
                    multiattack_text = multiattack_entries[0].lower()
                    print(f"⚔ [DEBUG] Multiattack: {multiattack_text}")
                    
                    # Parse multiattack in different formats
                    import re
                    attacks_to_make = []
                    
                    # Format 1: "one with its bite and one with its claws" - check this FIRST
                    if 'one with its' in multiattack_text or 'two with its' in multiattack_text:
                        # Find all "one with its X" or "two with its Y" patterns
                        attack_patterns = re.findall(r'(one|two) with its (\w+)', multiattack_text)
                        for count_word, attack_name in attack_patterns:
                            count = 2 if count_word == 'two' else 1
                            attacks_to_make.append((attack_name, count))
                    
                    # Format 2: "three tentacle attacks"
                    elif re.search(r'(\w+) (\w+) attacks?$', multiattack_text):
                        pattern1 = re.search(r'(\w+) (\w+) attacks?$', multiattack_text)
                        count_word = pattern1.group(1)
                        attack_name = pattern1.group(2)
                        count_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                        attack_count = count_map.get(count_word, 1)
                        attacks_to_make = [(attack_name, attack_count)]
                    
                    # Format 3: "makes two attacks" (generic) - fallback
                    elif 'makes two attacks' in multiattack_text:
                        # Use first available weapon attack, make it twice
                        for action in actions[1:]:
                            action_name = action.get('name', '').lower()
                            if any(weapon in action_name for weapon in ['bite', 'claw', 'sword', 'spear', 'axe']):
                                attacks_to_make = [(action_name.split()[0], 2)]  # Just the weapon name
                                break
                    
                    print(f"⚔ [DEBUG] Parsed attacks: {attacks_to_make}")
                    
                    # Execute all parsed attacks
                    if attacks_to_make:
                        for attack_name, attack_count in attacks_to_make:
                            # Find the actual attack action by name
                            attack_action = None
                            for action in actions[1:]:  # Skip multiattack action
                                if attack_name.lower() in action.get('name', '').lower():
                                    attack_action = action
                                    break
                            
                            if attack_action:
                                print(f"⚔ [DEBUG] Making {attack_count} {attack_name} attacks")
                                for i in range(attack_count):
                                    self._execute_single_monster_attack(monster_instance, attack_action, monster_stats, encounter_panel, i+1, attack_count)
                            else:
                                print(f"⚔ [DEBUG] Could not find {attack_name} attack action")
                        return
                    else:
                        print(f"⚔ [DEBUG] Could not parse multiattack format: {multiattack_text}")
                        # Fall back to first non-multiattack action
                        if len(actions) > 1:
                            self._execute_single_monster_attack(monster_instance, actions[1], monster_stats, encounter_panel)
                            return
            
            # Single attack (no multiattack or fallback)
            main_action = first_action
            self._execute_single_monster_attack(monster_instance, main_action, monster_stats, encounter_panel)
            
        except Exception as e:
            print(f"Error executing monster attack: {e}")
    
    def _execute_single_monster_attack(self, monster_instance, action, monster_stats: dict, encounter_panel, attack_num: int = 1, total_attacks: int = 1):
        """Execute a single attack from a monster action."""
        try:
            action_name = action.get('name', 'Attack')
            
            # Parse the attack from the action entry
            attack_info = self._parse_monster_attack(action, monster_stats)
            if not attack_info:
                return

            import random
            from services.advantage_system import advantage_system, RollType
            
            # Check for disadvantage sources (including Lucky)
            attack_context = {
                'monster_attack': True,
                'sap_effect': getattr(monster_instance, 'has_sap_disadvantage', False)
            }
            
            advantage_sources = []
            disadvantage_sources = []
            
            # Check for Sap weapon mastery disadvantage
            if getattr(monster_instance, 'has_sap_disadvantage', False):
                disadvantage_sources.append("Sap weapon mastery")
                # Clear the disadvantage after using it
                monster_instance.has_sap_disadvantage = False
            
            # Check for Lucky feat disadvantage
            if self.lucky_disadvantage_active:
                disadvantage_sources.append("Lucky feat")
                self.lucky_disadvantage_active = False  # Consume the Lucky disadvantage
                print(f"[DEBUG] Applied Lucky defensive disadvantage to {monster_instance.monster_name}")
            
            # Check for Inspiration defensive disadvantage
            if self.inspiration_defensive_active:
                disadvantage_sources.append("Inspiration (defensive)")
                self.inspiration_defensive_active = False  # Consume the Inspiration disadvantage
                print(f"[DEBUG] Applied Inspiration defensive disadvantage to {monster_instance.monster_name}")
            
            # Check for Reckless Attack advantage (enemies get advantage against reckless barbarian)
            if self.character_context.get('reckless_attack_active', False):
                advantage_sources.append("Reckless Attack")
            
            # Calculate advantage state and roll
            advantage_state = advantage_system.calculate_advantage_state(advantage_sources, disadvantage_sources)
            d20_total, roll_breakdown = advantage_system.roll_d20_with_advantage(advantage_state, attack_info['hit_bonus'])
            attack_roll = d20_total
            
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
                                              attack_roll, player_ac, damage_total, attack_info, roll_breakdown, attack_num, total_attacks)
            else:
                # Attack missed
                self._log_monster_attack_result(False, monster_instance.monster_name, action_name, 
                                              attack_roll, player_ac, 0, attack_info, roll_breakdown, attack_num, total_attacks)
                
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
    
    def _apply_damage_to_player(self, damage: int, encounter_panel, damage_type: str = "physical"):
        """Apply damage to the player character, with class-specific resistances."""
        try:
            # Check for rage damage resistance (bludgeoning, piercing, slashing) - BARBARIANS ONLY
            original_damage = damage
            rage_resistance_applied = False

            # Only apply rage resistance if character is a Barbarian AND raging
            is_barbarian = self.character_context.get('class_id', '').lower() == 'barbarian'
            is_raging = self.character_context.get('raging', False)

            if is_barbarian and is_raging and damage_type in ['physical', 'bludgeoning', 'piercing', 'slashing']:
                damage = damage // 2  # Half damage (rounded down)
                if damage < original_damage:
                    rage_resistance_applied = True
            
            # Get character data from encounter panel or main window
            parent = self.parent()
            while parent:
                if hasattr(parent, 'character_sheet') and parent.character_sheet.character_data:
                    character_data = parent.character_sheet.character_data
                    
                    # Apply damage to current HP
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
                                max_hp = 0
                        else:
                            max_hp = 0
                    
                    new_hp = max(0, current_hp - damage)
                    
                    # Update both field name variants for compatibility
                    character_data['current_hit_points'] = new_hp
                    character_data['hit_points_current'] = new_hp
                    
                    # Update character sheet display
                    parent.character_sheet.load_character_data(character_data)

                    # Check for concentration saves if character took damage
                    if damage > 0:
                        self._check_concentration_save(character_data.get('id'), damage)

                    # Log damage with HP tracking (similar to monster damage)
                    log_parent = self.parent()
                    while log_parent:
                        if hasattr(log_parent, 'log_panel'):
                            # Log HP change
                            log_parent.log_panel.log_combat(f"    Player HP: {current_hp}/{max_hp} -> {new_hp}/{max_hp}")

                            # Log rage resistance if applicable
                            if rage_resistance_applied:
                                log_parent.log_panel.log_combat(f"    [SHIELD] RAGE RESISTANCE: {original_damage} damage reduced to {damage}")
                            break
                        log_parent = log_parent.parent()
                    
                    return new_hp
                parent = parent.parent()
                
        except Exception as e:
            print(f"Error applying damage to player: {e}")
            return 0

    def _check_concentration_save(self, character_id: str, damage: int):
        """Check for concentration saves when character takes damage."""
        try:
            from services.concentration_system import get_concentration_system

            concentration_system = get_concentration_system()
            concentration_spell = concentration_system.get_concentration_spell(character_id)

            if concentration_spell:
                # Get Constitution modifier
                constitution_modifier = self._get_constitution_modifier()

                # Make concentration save
                success, dc, roll = concentration_system.make_concentration_save(
                    character_id, damage, constitution_modifier
                )

                # Log the result
                log_parent = self.parent()
                while log_parent:
                    if hasattr(log_parent, 'log_panel'):
                        spell_name = concentration_spell['spell_name']
                        if success:
                            log_parent.log_panel.log_combat(
                                f"    [CONCENTRATION] {spell_name}: Save successful ({roll} vs DC {dc})"
                            )
                        else:
                            log_parent.log_panel.log_combat(
                                f"    [CONCENTRATION] {spell_name}: Save failed ({roll} vs DC {dc}) - spell ends"
                            )
                        break
                    log_parent = log_parent.parent()

        except Exception as e:
            print(f"Error checking concentration save: {e}")

    def _get_constitution_modifier(self) -> int:
        """Get character's Constitution modifier."""
        try:
            constitution = self.character_context.get('constitution', 10)
            return (constitution - 10) // 2
        except:
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
                                parent_with_log.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {actual_healing}, max HP reached)")
                            else:
                                # Normal healing
                                parent_with_log.log_panel.log_combat(f"💚 HP: {old_hp}/{max_hp} -> {new_hp}/{max_hp} (healed {healing})")
                            break
                        parent_with_log = parent_with_log.parent()
                    
                    return new_hp
                parent = parent.parent()
            
            return 0
                
        except Exception as e:
            print(f"Error applying healing to player: {e}")
            return 0
    
    def _log_monster_attack_result(self, hit: bool, monster_name: str, action_name: str, 
                                  attack_roll: int, player_ac: int, damage: int, attack_info: dict, roll_breakdown: dict = None, attack_num: int = 1, total_attacks: int = 1):
        """Log monster attack results with advantage/disadvantage information."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Extract d20 roll and bonus for better display
                    hit_bonus = attack_info.get('hit_bonus', 0)
                    
                    # Format attack roll with d20 breakdown
                    if roll_breakdown and roll_breakdown.get('type') != 'normal':
                        # For advantage/disadvantage, show the rolls and bonus
                        roll_desc = roll_breakdown.get('description', f'{attack_roll}')
                        d20_roll = attack_roll - hit_bonus
                        attack_display = f"Attack: {roll_desc} + {hit_bonus} = {attack_roll}"
                    else:
                        # For normal rolls, show d20 + bonus
                        d20_roll = attack_roll - hit_bonus
                        attack_display = f"Attack: {d20_roll} + {hit_bonus} = {attack_roll}"
                    
                    # Add attack number for multiattack
                    attack_prefix = f"👹 {monster_name}"
                    if total_attacks > 1:
                        attack_prefix += f" (Attack {attack_num}/{total_attacks})"
                    
                    if hit:
                        parent.log_panel.log_combat(f"{attack_prefix} {action_name} hits! {attack_display} vs AC {player_ac} for {damage} damage")
                    else:
                        parent.log_panel.log_combat(f"{attack_prefix} {action_name} misses! {attack_display} vs AC {player_ac}")
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
            ActionType.ACTION_SURGE: "free",
            ActionType.NICK_MASTERY: "bonus_action",
            ActionType.CLEAVE_MASTERY: "bonus_action",
            ActionType.USE_POTION: "bonus_action",
            ActionType.BATTLE_MEDIC: "action",
            ActionType.LUCK_POINT_ADVANTAGE: "free",
            ActionType.LUCK_POINT_DISADVANTAGE: "reaction"
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
        
        # Check feat resource uses
        elif action_type in [ActionType.LUCK_POINT_ADVANTAGE, ActionType.LUCK_POINT_DISADVANTAGE]:
            uses = self._get_feat_resource_remaining("Lucky", "luck_points")
            if uses <= 0:
                reasons.append("No Luck Points remaining (requires Long Rest)")
        
        return reasons
    
    def _get_ability_uses_remaining(self, ability_name: str) -> int:
        """Get remaining uses for an ability from character resources."""
        character_id = self._resolve_character_id()
        if not character_id:
            return 0
        resource = self._get_resource_service().get_resource(character_id, ability_name)
        return resource.current_uses if resource else 0
    
    def _use_ability(self, ability_name: str):
        """Use an ability - decrement uses remaining via resource service."""
        character_id = self._resolve_character_id()
        if not character_id:
            print(f"DEBUG: Unable to resolve character id for {ability_name}")
            return

        result = self._get_resource_service().use_resource(character_id, ability_name)
        parent = self.parent()

        if result.get('success'):
            self._refresh_action_availability()
            uses_remaining = result.get('current_uses')
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"{ability_name} uses remaining: {uses_remaining}")
                    break
                parent = parent.parent()
        else:
            error_message = result.get('error', f'{ability_name} failed')
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[FAIL] {error_message}")
                    break
                parent = parent.parent()
    




    def _feature_name_to_action_type(self, feature_name: str) -> Optional[ActionType]:
        """Convert a feature name to its corresponding ActionType."""
        feature_map = {
            'Rage': ActionType.RAGE,
            'Second Wind': ActionType.SECOND_WIND,
            'Action Surge': ActionType.ACTION_SURGE,
            'Reckless Attack': ActionType.RECKLESS_ATTACK,
            'Lay on Hands': ActionType.LAY_ON_HANDS,
            'Channel Divinity': ActionType.CHANNEL_DIVINITY,
            'Intimidating Presence': ActionType.INTIMIDATING_PRESENCE,
            'Retaliation': ActionType.RETALIATION,
            'Fast Hands': ActionType.FAST_HANDS_THIEVES_TOOLS,  # Main thief feature
            'Brutal Strike': ActionType.BRUTAL_STRIKE_FORCEFUL,  # Default brutal strike
            'Instinctive Pounce': ActionType.INSTINCTIVE_POUNCE,
            'Heroic Warrior': ActionType.HEROIC_WARRIOR,
            'Survivor': ActionType.SURVIVOR,
            'Masterful Mimicry': ActionType.MASTERFUL_MIMICRY,
        }
        return feature_map.get(feature_name)

    def _resolve_character_id(self) -> Optional[str]:
        """Resolve the active character ID from context or parent widgets."""
        character_id = None
        if getattr(self, 'character_context', None):
            character_id = self.character_context.get('id')
        if character_id:
            return character_id
        parent = self.parent()
        while parent:
            game_engine = getattr(parent, 'game_engine', None)
            if game_engine:
                current_character = getattr(game_engine, 'current_character', None)
                if isinstance(current_character, dict):
                    character_id = current_character.get('id')
                    if character_id:
                        return character_id
            parent = parent.parent()
        return None

    def _resolve_db_path(self) -> str:
        """Resolve the database path for resource operations."""
        if getattr(self, 'character_context', None):
            db_path = self.character_context.get('db_path')
            if db_path:
                return db_path
        parent = self.parent()
        while parent:
            game_engine = getattr(parent, 'game_engine', None)
            if game_engine:
                for attr in ('db_path', 'db_file', 'db_name'):
                    value = getattr(game_engine, attr, None)
                    if value:
                        return value
            parent = parent.parent()
        return 'talekeeper.db'

    def _get_resource_service(self) -> CharacterResourceService:
        """Lazily construct the character resource service."""
        service = getattr(self, '_resource_service', None)
        if service is None:
            service = CharacterResourceService(self._resolve_db_path())
            self._resource_service = service
        return service

    @staticmethod
    def _normalize_weapon_properties(properties: Any) -> List[str]:
        """Normalize weapon property payloads into a lowercase list."""
        props = properties or []
        if isinstance(props, str):
            if ',' in props:
                props = [p.strip() for p in props.split(',') if p.strip()]
            else:
                props = [props.strip()] if props.strip() else []
        return [str(p).lower() for p in props if isinstance(p, str)]

    def _get_context_weapon_properties(self, context: Dict[str, Any]) -> List[str]:
        """Extract weapon properties from attack context dictionaries."""
        props = context.get('weapon_properties')
        if props:
            return self._normalize_weapon_properties(props)
        weapon_data = context.get('weapon')
        if isinstance(weapon_data, dict):
            props = weapon_data.get('weapon_properties') or weapon_data.get('properties')
            if props:
                return self._normalize_weapon_properties(props)
        return []

    def _get_context_damage_profile(self, context: Dict[str, Any]) -> Tuple[str, str]:
        """Return damage dice/type, falling back to weapon metadata when absent."""
        weapon_data = context.get('weapon') if isinstance(context.get('weapon'), dict) else {}
        damage_dice = context.get('damage_dice') or weapon_data.get('damage_dice') or '1d6'
        damage_type = context.get('damage_type') or weapon_data.get('damage_type') or 'slashing'
        return str(damage_dice), str(damage_type).lower()
    def _get_weapon_mastery_service(self) -> WeaponMasteryService:
        """Lazily construct the weapon mastery service with the active DB path."""
        db_path = self._resolve_db_path()
        service = getattr(self, '_weapon_mastery_service', None)
        if service is None or getattr(service, 'db_path', None) != db_path:
            service = WeaponMasteryService(db_path)
            self._weapon_mastery_service = service
        return service

    def _get_equipment_database(self) -> EquipmentDatabase:
        """Lazily construct the equipment database helper with the active DB path."""
        db_path = self._resolve_db_path()
        database = getattr(self, '_equipment_database', None)
        if database is None or getattr(database, 'db_path', None) != db_path:
            database = EquipmentDatabase(db_path)
            self._equipment_database = database
        return database

    def _get_weapon_attack_service(self) -> WeaponAttackService:
        """Lazily construct the weapon attack service with the active DB path."""
        db_path = self._resolve_db_path()
        service = getattr(self, '_weapon_attack_service', None)
        if service is None or getattr(service, 'db_path', None) != db_path:
            service = WeaponAttackService(db_path)
            self._weapon_attack_service = service
        return service

    def _get_combat_manager(self) -> CombatManager:
        """Lazily construct the combat manager with the active DB path."""
        db_path = self._resolve_db_path()
        manager = getattr(self, '_combat_manager', None)
        if manager is None or getattr(manager, 'db_path', None) != db_path:
            manager = CombatManager(db_path)
            self._combat_manager = manager
        return manager

    def _get_spellcasting_service(self) -> SpellcastingService:
        """Lazily construct the spellcasting service with the active DB path."""
        db_path = self._resolve_db_path()
        service = getattr(self, '_spellcasting_service', None)
        if service is None or getattr(service, 'db_path', None) != db_path:
            service = SpellcastingService(db_path)
            self._spellcasting_service = service
        return service

    def _get_character_castable_spells(self, character_id: str) -> List[Dict[str, Any]]:
        """Get list of spells the character can currently cast."""
        db_path = self._resolve_db_path()
        try:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get prepared spells that can be cast (cantrips are always castable)
                cursor.execute("""
                    SELECT cs.spell_id, s.level as spell_level, cs.is_prepared, cs.always_prepared,
                           s.name, s.school, s.casting_time, s.range_value, s.components,
                           s.duration, s.concentration, s.description
                    FROM character_spells cs
                    JOIN spells s ON cs.spell_id = s.id
                    WHERE cs.character_id = ?
                    AND (cs.is_prepared = 1 OR s.level = 0 OR cs.always_prepared = 1)
                    ORDER BY s.level, s.name
                """, (character_id,))

                spells = []
                for row in cursor.fetchall():
                    spell_data = {
                        'spell_id': row[0],
                        'spell_level': row[1],
                        'is_prepared': row[2],
                        'always_prepared': row[3],
                        'name': row[4],
                        'school': row[5],
                        'casting_time': row[6],
                        'range_value': row[7],
                        'components': row[8],
                        'duration': row[9],
                        'concentration': row[10],
                        'description': row[11]
                    }

                    # Check if character has spell slots for this spell (except cantrips)
                    if spell_data['spell_level'] > 0:
                        spellcasting_service = self._get_spellcasting_service()
                        can_cast, _ = spellcasting_service.can_cast_spell(character_id, spell_data['spell_id'])
                        if not can_cast:
                            continue  # Skip spells that can't be cast due to no slots

                    spells.append(spell_data)

                return spells

        except Exception as e:
            print(f"Error getting character spells: {e}")
            return []

    def _create_spell_action_cards(self):
        """Create swappable spell slot cards grouped by level and action type."""
        if not self.character_context or not self.character_context.get('id'):
            return

        character_id = self.character_context['id']
        spells = self._get_character_castable_spells(character_id)
        spell_slots = self._get_character_spell_slots(character_id)

        print(f"[DEBUG] _create_spell_action_cards called for character {character_id}")
        print(f"[DEBUG] Found {len(spells)} castable spells: {[s['name'] for s in spells]}")
        print(f"[DEBUG] Spell slots: {spell_slots}")

        # Group spells by level and action type
        spell_groups = {}
        for spell in spells:
            spell_level = spell['spell_level']
            action_type = self._determine_spell_action_type(spell)

            key = (spell_level, action_type)
            if key not in spell_groups:
                spell_groups[key] = []
            spell_groups[key].append(spell)

        # Create one slot card per (spell_level, action_type) combination
        for (spell_level, action_type), available_spells in spell_groups.items():
            if not available_spells:
                continue

            # Get spell slot info for this level
            slot_info = next((slot for slot in spell_slots if slot.level == spell_level), None)

            # For cantrips (level 0), always available
            if spell_level == 0:
                available_slots = float('inf')
                max_slots = float('inf')
            elif slot_info:
                available_slots = slot_info.available_slots
                max_slots = slot_info.max_slots
            else:
                available_slots = 0
                max_slots = 0

            # Skip if no slots available (except cantrips)
            if spell_level > 0 and available_slots == 0:
                continue

            # Choose default spell (first alphabetically) for the card display
            default_spell = sorted(available_spells, key=lambda s: s['name'])[0]

            # Create slot card
            card = self._create_spell_slot_card(
                spell_level, action_type, default_spell,
                available_spells, available_slots, max_slots
            )

            # Store with unique key for this slot
            card_key = f"spell_slot_{spell_level}_{action_type.value}"
            self.action_cards[card_key] = card

    def _determine_spell_action_type(self, spell: Dict[str, Any]) -> ActionType:
        """Determine the appropriate action type for a spell."""
        casting_time = spell.get('casting_time', '').lower()

        if 'reaction' in casting_time:
            return ActionType.SPELL_REACTION
        elif any(keyword in spell.get('description', '').lower()
                for keyword in ['attack', 'damage', 'hit']):
            return ActionType.SPELL_ATTACK
        else:
            return ActionType.SPELL_UTILITY

    def _get_spell_icon(self, spell: Dict[str, Any]) -> str:
        """Get an appropriate icon for the spell based on school and properties."""
        school = spell.get('school', '').lower()
        level = spell.get('spell_level', 0)

        # Cantrips get special treatment
        if level == 0:
            if school == 'evocation':
                return "🔥"  # Fire/energy
            elif school == 'conjuration':
                return "✨"  # Sparkles
            elif school == 'enchantment':
                return "💫"  # Mind effects
            elif school == 'illusion':
                return "🌀"  # Swirl
            elif school == 'necromancy':
                return "💀"  # Death
            elif school == 'transmutation':
                return "⚡"  # Change
            elif school == 'divination':
                return "👁"  # Eye
            elif school == 'abjuration':
                return "🛡"  # Protection
            else:
                return "✨"  # Default

        # Higher level spells
        if school == 'evocation':
            return "💥"  # Explosion
        elif school == 'conjuration':
            return "🌟"  # Star
        elif school == 'enchantment':
            return "🧠"  # Brain
        elif school == 'illusion':
            return "👻"  # Ghost
        elif school == 'necromancy':
            return "⚰️"  # Coffin
        elif school == 'transmutation':
            return "🔮"  # Crystal ball
        elif school == 'divination':
            return "🔍"  # Magnifying glass
        elif school == 'abjuration':
            return "🛡️"  # Shield
        else:
            return "🔮"  # Default crystal ball

    def _create_spell_description(self, spell: Dict[str, Any]) -> str:
        """Create a concise description for the spell action card."""
        parts = []

        # Add casting time
        casting_time = spell.get('casting_time', '')
        if casting_time:
            parts.append(f"Time: {casting_time}")

        # Add range
        range_value = spell.get('range_value', '')
        if range_value:
            parts.append(f"Range: {range_value}")

        # Add concentration if applicable
        if spell.get('concentration'):
            parts.append("Concentration")

        # Add brief effect from description (first sentence)
        description = spell.get('description', '')
        if description:
            first_sentence = description.split('.')[0]
            if len(first_sentence) > 80:
                first_sentence = first_sentence[:77] + "..."
            parts.append(first_sentence)

        return " | ".join(parts)

    def _get_character_spell_slots(self, character_id: str):
        """Get character's spell slots using the spellcasting service."""
        try:
            spellcasting_service = self._get_spellcasting_service()
            return spellcasting_service.get_character_spell_slots(character_id)
        except Exception as e:
            print(f"Error getting character spell slots: {e}")
            return []

    def _create_spell_slot_card(self, spell_level: int, action_type: ActionType,
                               default_spell: Dict[str, Any], available_spells: List[Dict[str, Any]],
                               available_slots: int, max_slots: int) -> "ActionCard":
        """Create a swappable spell slot card."""
        # Create icon based on spell level
        if spell_level == 0:
            icon = "✨"  # Cantrip
        else:
            icon = f"{spell_level}⭐"  # Level number with star

        # Create card name showing level and current spell
        if spell_level == 0:
            name = f"Cantrip: {default_spell['name']}"
        else:
            name = f"Level {spell_level}: {default_spell['name']}"

        # Create description with slot availability and spell info
        description_parts = []

        # Add slot availability
        if spell_level == 0:
            description_parts.append("Cantrip (unlimited)")
        else:
            slots_display = self._create_slots_display(available_slots, max_slots)
            description_parts.append(f"Slots: {slots_display}")

        # Add spell info
        casting_time = default_spell.get('casting_time', '')
        if casting_time:
            description_parts.append(f"Time: {casting_time}")

        range_value = default_spell.get('range_value', '')
        if range_value:
            description_parts.append(f"Range: {range_value}")

        if default_spell.get('concentration'):
            description_parts.append("Concentration")

        # Add spell count if multiple available
        if len(available_spells) > 1:
            description_parts.append(f"({len(available_spells)} spells available)")

        description = " | ".join(description_parts)

        # Create action card
        card = ActionCard(action_type, icon, name, description)

        # Apply current theme to match other cards
        if hasattr(self, 'current_theme'):
            card.update_theme_styles(self.current_theme)
        else:
            card.update_theme_styles("light")

        # Store spell slot data for casting
        card.spell_slot_data = {
            'spell_level': spell_level,
            'action_type': action_type,
            'default_spell': default_spell,
            'available_spells': available_spells,
            'available_slots': available_slots,
            'max_slots': max_slots
        }

        card.action_triggered.connect(self._trigger_action)
        card.action_hovered.connect(self._action_hovered)

        return card

    def _create_slots_display(self, available: int, maximum: int) -> str:
        """Create visual display of spell slots like ●●●○○ (3/5)."""
        if maximum == 0:
            return "0/0"

        used = maximum - available
        display = "●" * available + "○" * used
        return f"{display} ({available}/{maximum})"

    def _show_spell_selection_dialog(self, available_spells: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Show dialog to select which spell to cast from available options."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QButtonGroup

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Spell")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose spell to cast:"))

        button_group = QButtonGroup()
        selected_spell = None

        def on_spell_selected(spell):
            nonlocal selected_spell
            selected_spell = spell
            dialog.accept()

        for spell in sorted(available_spells, key=lambda s: s['name']):
            btn = QPushButton(f"{spell['name']}")
            btn.setToolTip(spell.get('description', ''))
            btn.clicked.connect(lambda checked, s=spell: on_spell_selected(s))
            layout.addWidget(btn)
            button_group.addButton(btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return selected_spell
        return None

    def _show_spell_level_selection_dialog(self, spell: Dict[str, Any], character_id: str) -> Optional[int]:
        """Show dialog to select which spell level to cast at."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QButtonGroup

        # Get available spell slots
        spell_slots = self._get_character_spell_slots(character_id)
        spell_level = spell['spell_level']

        # Find slots that can cast this spell
        available_levels = []
        for slot in spell_slots:
            if slot.level >= spell_level and slot.available_slots > 0:
                available_levels.append((slot.level, slot.available_slots, slot.max_slots))

        # If only one level available, use it
        if len(available_levels) == 1:
            return available_levels[0][0]

        # If no levels available, return None
        if not available_levels:
            return None

        # Show selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Cast {spell['name']}")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Select spell slot level for {spell['name']}:"))

        selected_level = None

        def on_level_selected(level):
            nonlocal selected_level
            selected_level = level
            dialog.accept()

        for level, available, maximum in sorted(available_levels):
            slots_display = self._create_slots_display(available, maximum)
            btn_text = f"Level {level} - {slots_display}"

            # Add scaling info if available
            if level > spell_level:
                btn_text += f" (upcast from {spell_level})"

            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, l=level: on_level_selected(l))
            layout.addWidget(btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return selected_level
        return None

    def _cast_spell(self, action_type: ActionType, context: Dict[str, Any]):
        """Handle spell casting from slot cards."""
        character_id = self.character_context.get('id')
        if not character_id:
            self._log_to_combat_panel("❌ Error: No character selected")
            return

        # Check if this is a spell slot card or old-style spell card
        spell_slot_data = context.get('spell_slot_data')
        spell_data = context.get('spell_data')

        if spell_slot_data:
            # New spell slot card system
            self._cast_spell_from_slot(spell_slot_data, character_id)
        elif spell_data:
            # Old system compatibility
            self._cast_spell_legacy(action_type, spell_data, character_id)
        else:
            self._log_to_combat_panel("❌ Error: Could not find spell data")

    def _cast_spell_from_slot(self, slot_data: Dict[str, Any], character_id: str):
        """Cast spell from new slot card system."""
        available_spells = slot_data['available_spells']
        spell_level = slot_data['spell_level']

        # Step 1: Select spell if multiple available
        selected_spell = None
        if len(available_spells) == 1:
            selected_spell = available_spells[0]
        else:
            # Show spell selection dialog
            selected_spell = self._show_spell_selection_dialog(available_spells)
            if not selected_spell:
                return  # User cancelled

        # Step 2: Select spell level for casting (for level 1+ spells)
        cast_level = spell_level
        if spell_level > 0:
            cast_level = self._show_spell_level_selection_dialog(selected_spell, character_id)
            if cast_level is None:
                return  # User cancelled

        # Step 3: Cast the spell
        try:
            spellcasting_service = self._get_spellcasting_service()
            result = spellcasting_service.cast_spell(
                character_id, selected_spell['spell_id'], cast_level
            )

            if result.success:
                spell_name = selected_spell['name']
                action_type = slot_data['action_type']

                # Log success
                if cast_level == 0:
                    self._log_to_combat_panel(f"✨ Cast cantrip: {spell_name}")
                else:
                    self._log_to_combat_panel(f"✨ Cast {spell_name} (level {cast_level})")

                # Handle concentration
                if result.concentration_started:
                    self._log_to_combat_panel(f"🧠 Concentrating on {spell_name}")

                if result.concentration_ended:
                    self._log_to_combat_panel(f"💫 Concentration ended on previous spell")

                # Handle spell effects
                self._handle_spell_effects(action_type, selected_spell, cast_level)

                # Refresh action cards to update spell slot availability
                self._refresh_spell_action_cards()

                # CRITICAL: Update action economy and advance turn (like weapon attacks do)
                self._update_action_economy(action_type)

                # Emit action signal for any listeners
                if hasattr(self, 'action_triggered'):
                    full_context = {'spell_name': spell_name, 'spell_level': cast_level}
                    self.action_triggered.emit(action_type, full_context)

                # Advance combat turn if this is a combat action
                if self._is_combat_action(action_type):
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel:
                        self._advance_combat_turn(encounter_panel)

            else:
                self._log_to_combat_panel(f"❌ Cannot cast {selected_spell['name']}: {result.reason}")

        except Exception as e:
            self._log_to_combat_panel(f"❌ Error casting spell: {e}")

    def _cast_spell_legacy(self, action_type: ActionType, spell_data: Dict[str, Any], character_id: str):
        """Legacy spell casting for old system compatibility."""
        spell_id = spell_data['spell_id']
        spell_name = spell_data['name']
        spell_level = spell_data['spell_level']

        try:
            spellcasting_service = self._get_spellcasting_service()
            result = spellcasting_service.cast_spell(character_id, spell_id)

            if result.success:
                if spell_level == 0:
                    self._log_to_combat_panel(f"✨ Cast cantrip: {spell_name}")
                else:
                    self._log_to_combat_panel(f"✨ Cast {spell_name} (level {spell_level})")

                if result.concentration_started:
                    self._log_to_combat_panel(f"🧠 Concentrating on {spell_name}")

                if result.concentration_ended:
                    self._log_to_combat_panel(f"💫 Concentration ended on previous spell")

                self._handle_spell_effects(action_type, spell_data, spell_level)
                self._refresh_spell_action_cards()

                # CRITICAL: Update action economy and advance turn (like weapon attacks do)
                self._update_action_economy(action_type)

                # Emit action signal for any listeners
                if hasattr(self, 'action_triggered'):
                    full_context = {'spell_name': spell_name, 'spell_level': spell_level}
                    self.action_triggered.emit(action_type, full_context)

                # Advance combat turn if this is a combat action
                if self._is_combat_action(action_type):
                    encounter_panel = self._get_encounter_panel()
                    if encounter_panel:
                        self._advance_combat_turn(encounter_panel)

            else:
                self._log_to_combat_panel(f"❌ Cannot cast {spell_name}: {result.reason}")

        except Exception as e:
            self._log_to_combat_panel(f"❌ Error casting spell: {e}")

    def _handle_spell_effects(self, action_type: ActionType, spell_data: Dict[str, Any], cast_level: int):
        """Handle spell effects based on action type."""
        if action_type == ActionType.SPELL_ATTACK:
            self._handle_spell_attack(spell_data, {'cast_level': cast_level})
        elif action_type == ActionType.SPELL_UTILITY:
            self._handle_spell_utility(spell_data, {'cast_level': cast_level})
        elif action_type == ActionType.SPELL_REACTION:
            self._handle_spell_reaction(spell_data, {'cast_level': cast_level})

    def _handle_spell_attack(self, spell_data: Dict[str, Any], context: Dict[str, Any]):
        """Handle attack spell effects."""
        import random

        spell_name = spell_data['name']
        spell_level = spell_data.get('level', 0)
        cast_level = context.get('cast_level', spell_level)

        encounter_panel = self._get_encounter_panel()
        if not encounter_panel:
            self._log_to_combat_panel(f"⚠️ {spell_name} cast but no encounter active")
            return

        target_monster = encounter_panel.get_selected_monster()
        if not target_monster:
            self._log_to_combat_panel(f"⚠️ {spell_name} cast but no target selected")
            return

        spell_mechanics = self._get_spell_mechanics(spell_name)

        if spell_mechanics == 'attack':
            # Spell requires attack roll
            attack_total, attack_breakdown = self._roll_spell_attack()
            target_ac = 12  # TODO: Get actual monster AC
            hit = attack_total >= target_ac

            if hit:
                damage_total, damage_log = self._calculate_spell_damage(spell_name, spell_level, cast_level)
                if damage_total > 0:
                    target_id = target_monster.id
                    encounter_panel._apply_damage_to_monster(target_id, damage_total)
                    self._log_to_combat_panel(f"⚔️ {spell_name} hits {target_monster.monster_name} for {damage_total} damage!")
                    self._log_to_combat_panel(f"   Attack: {attack_breakdown['description']} = {attack_total} vs AC {target_ac}")
                    if damage_log:
                        self._log_to_combat_panel(f"   Damage: {damage_log}")
            else:
                self._log_to_combat_panel(f"⚔️ {spell_name} misses {target_monster.monster_name}")
                self._log_to_combat_panel(f"   Attack: {attack_breakdown['description']} = {attack_total} vs AC {target_ac}")

        elif spell_mechanics == 'save':
            # Spell requires target saving throw
            save_dc = self._calculate_spell_save_dc()
            save_type = self._get_spell_save_type(spell_name)
            save_roll, save_breakdown = self._roll_monster_save(target_monster, save_type)
            save_success = save_roll >= save_dc

            damage_total, damage_log = self._calculate_spell_damage(spell_name, spell_level, cast_level)

            if save_success:
                # Save succeeded - no damage or half damage depending on spell
                self._log_to_combat_panel(f"⚔️ {target_monster.monster_name} saves against {spell_name}!")
                self._log_to_combat_panel(f"   {save_type} Save: {save_breakdown} = {save_roll} vs DC {save_dc}")
            else:
                # Save failed - full damage
                if damage_total > 0:
                    target_id = target_monster.id
                    encounter_panel._apply_damage_to_monster(target_id, damage_total)
                    self._log_to_combat_panel(f"⚔️ {target_monster.monster_name} fails save against {spell_name} for {damage_total} damage!")
                    self._log_to_combat_panel(f"   {save_type} Save: {save_breakdown} = {save_roll} vs DC {save_dc}")
                    if damage_log:
                        self._log_to_combat_panel(f"   Damage: {damage_log}")

        else:
            # Automatic hit spell (like Magic Missile)
            damage_total, damage_log = self._calculate_spell_damage(spell_name, spell_level, cast_level)
            if damage_total > 0:
                target_id = target_monster.id
                encounter_panel._apply_damage_to_monster(target_id, damage_total)
                self._log_to_combat_panel(f"⚔️ {spell_name} hits {target_monster.monster_name} for {damage_total} damage!")
                if damage_log:
                    self._log_to_combat_panel(f"   {damage_log}")
            else:
                self._log_to_combat_panel(f"⚔️ {spell_name} cast at {target_monster.monster_name}")

    def _calculate_spell_damage(self, spell_name: str, spell_level: int, cast_level: int) -> tuple[int, str]:
        """Calculate spell damage based on spell and cast level. Returns (total_damage, log_string)."""
        import random

        char_level = self.character_context.get('level', 1)

        spell_damage_data = {
            'Magic Missile': {
                'base_darts': 3,
                'dart_damage': (1, 4, 1),
                'scaling': 'per_level',
            },
            'Fire Bolt': {
                'dice': self._get_cantrip_dice_by_level(char_level),
                'die_size': 10,
                'damage_type': 'fire',
            },
            'Ray of Frost': {
                'dice': self._get_cantrip_dice_by_level(char_level),
                'die_size': 8,
                'damage_type': 'cold',
            },
            'Shocking Grasp': {
                'dice': self._get_cantrip_dice_by_level(char_level),
                'die_size': 8,
                'damage_type': 'lightning',
            },
            'Sacred Flame': {
                'dice': self._get_cantrip_dice_by_level(char_level),
                'die_size': 8,
                'damage_type': 'radiant',
            },
        }

        if spell_name not in spell_damage_data:
            return 0, f"Damage calculation not implemented for {spell_name}"

        data = spell_damage_data[spell_name]

        if spell_name == 'Magic Missile':
            num_darts = data['base_darts'] + (cast_level - spell_level)
            num_dice, die_size, modifier = data['dart_damage']
            total_damage = 0
            rolls = []

            for _ in range(num_darts):
                roll = random.randint(num_dice, num_dice * die_size)
                dart_damage = roll + modifier
                total_damage += dart_damage
                rolls.append(f"{roll}+{modifier}")

            damage_log = f"{num_darts} darts: [{', '.join(rolls)}] = {total_damage} force damage"
            return total_damage, damage_log
        else:
            num_dice = data['dice']
            die_size = data['die_size']
            damage_type = data.get('damage_type', 'damage')

            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total_damage = sum(rolls)

            rolls_str = '+'.join(str(r) for r in rolls)
            damage_log = f"{num_dice}d{die_size} [{rolls_str}] = {total_damage} {damage_type} damage"
            return total_damage, damage_log

    def _get_cantrip_dice_by_level(self, char_level: int) -> int:
        """Get number of damage dice for cantrips based on character level."""
        if char_level >= 17:
            return 4
        elif char_level >= 11:
            return 3
        elif char_level >= 5:
            return 2
        else:
            return 1

    def _get_spell_mechanics(self, spell_name: str) -> str:
        """Determine spell mechanics: 'attack', 'save', or 'auto'."""
        attack_spells = {'Fire Bolt', 'Ray of Frost', 'Shocking Grasp', 'Eldritch Blast'}
        save_spells = {'Sacred Flame', 'Burning Hands', 'Thunderwave'}

        if spell_name in attack_spells:
            return 'attack'
        elif spell_name in save_spells:
            return 'save'
        else:
            return 'auto'  # Magic Missile, healing spells, etc.

    def _roll_spell_attack(self) -> tuple[int, dict]:
        """Roll a spell attack (1d20 + spell attack bonus)."""
        import random

        # Calculate spell attack bonus
        spell_attack_bonus = self._calculate_spell_attack_bonus()

        # Roll d20
        d20_roll = random.randint(1, 20)
        total = d20_roll + spell_attack_bonus

        breakdown = {
            'd20_roll': d20_roll,
            'spell_attack_bonus': spell_attack_bonus,
            'description': f"d20({d20_roll}) +{spell_attack_bonus} spell attack"
        }

        return total, breakdown

    def _calculate_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus = proficiency + spellcasting ability modifier."""
        class_id = self.character_context.get('class_id', '').lower()
        level = self.character_context.get('level', 1)

        # Calculate proficiency bonus
        prof_bonus = 2 + ((level - 1) // 4)  # +2 at 1-4, +3 at 5-8, etc.

        # Get spellcasting ability modifier
        if class_id == 'wizard':
            ability_mod = (self.character_context.get('intelligence', 10) - 10) // 2
        elif class_id in ['cleric', 'druid']:
            ability_mod = (self.character_context.get('wisdom', 10) - 10) // 2
        elif class_id in ['paladin', 'warlock', 'sorcerer']:
            ability_mod = (self.character_context.get('charisma', 10) - 10) // 2
        else:
            ability_mod = 0

        return prof_bonus + ability_mod

    def _calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC = 8 + proficiency + spellcasting ability modifier."""
        return 8 + self._calculate_spell_attack_bonus()

    def _get_spell_save_type(self, spell_name: str) -> str:
        """Get the type of saving throw required for a spell."""
        save_types = {
            'Sacred Flame': 'DEX',
            'Burning Hands': 'DEX',
            'Thunderwave': 'CON',
            'Hold Person': 'WIS',
            'Charm Person': 'WIS',
        }
        return save_types.get(spell_name, 'DEX')  # Default to DEX

    def _roll_monster_save(self, target_monster, save_type: str) -> tuple[int, str]:
        """Roll a saving throw for a monster."""
        import random

        # TODO: Get actual monster save bonuses from database
        # For now, use generic save bonuses based on CR
        base_save_bonus = 0  # Most low-CR monsters have +0 to saves

        d20_roll = random.randint(1, 20)
        total = d20_roll + base_save_bonus

        breakdown = f"d20({d20_roll}) +{base_save_bonus} {save_type}"

        return total, breakdown

    def _handle_spell_utility(self, spell_data: Dict[str, Any], context: Dict[str, Any]):
        """Handle utility/buff spell effects."""
        spell_name = spell_data['name']

        # For now, just log the effect - this can be expanded with specific spell implementations
        self._log_to_combat_panel(f"🔮 {spell_name} effect applied")

    def _handle_spell_reaction(self, spell_data: Dict[str, Any], context: Dict[str, Any]):
        """Handle reaction spell effects."""
        spell_name = spell_data['name']

        # For now, just log the reaction - this can be expanded with trigger conditions
        self._log_to_combat_panel(f"⚡ {spell_name} reaction triggered")

    def _refresh_spell_action_cards(self):
        """Refresh spell action cards to reflect current spell slot availability."""
        # Remove existing spell cards (both old individual and new slot cards)
        cards_to_remove = [key for key in self.action_cards.keys()
                          if isinstance(key, str) and (key.startswith('spell_') or key.startswith('spell_slot_'))]
        for key in cards_to_remove:
            if key in self.action_cards:
                self.action_cards[key].deleteLater()
                del self.action_cards[key]

        # Recreate spell cards using new slot system
        self._create_spell_action_cards()

        # Update the UI display
        self._update_visible_cards()

    def _setup_combat_manager(self, encounter_panel, initiative_order):
        """Set up the combat manager with player and monster combatants."""
        try:
            combat_manager = self._get_combat_manager()

            # Add player combatant with normalized HP fields
            if self.character_context:
                # Normalize HP field names for CombatManager
                character_data = self.character_context.copy()
                if 'hit_points_current' in character_data and 'hp' not in character_data:
                    character_data['hp'] = character_data['hit_points_current']
                if 'hit_points_max' in character_data and 'max_hp' not in character_data:
                    character_data['max_hp'] = character_data['hit_points_max']
                if 'armor_class' in character_data and 'ac' not in character_data:
                    character_data['ac'] = character_data['armor_class']

                player_combatant = combat_manager.add_player_combatant(character_data)
                print(f"⚔ [DEBUG] Added player to combat manager: {player_combatant.name} ({player_combatant.hit_points}/{player_combatant.max_hit_points} HP)")

            # Add monster combatants
            for entry in initiative_order:
                if entry['type'] == 'monster':
                    monster_instance = entry.get('instance')
                    if monster_instance:
                        # Get monster data from database
                        monster_data = self._get_monster_data_for_combat_manager(monster_instance)
                        if monster_data:
                            monster_combatant = combat_manager.add_monster_combatant(monster_instance.id, monster_data)
                            print(f"⚔ [DEBUG] Added monster to combat manager: {monster_combatant.name}")

            # Start combat in the manager
            combat_manager.start_combat()
            print(f"⚔ [DEBUG] Combat manager started with {len(combat_manager.combatants)} combatants")

        except Exception as e:
            print(f"Error setting up combat manager: {e}")
            import traceback
            traceback.print_exc()

    def _get_monster_data_for_combat_manager(self, monster_instance):
        """Get monster data in the format expected by combat manager."""
        try:
            # Get monster data from database
            import sqlite3
            db_path = self._resolve_db_path()

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM monsters WHERE name = ?", (monster_instance.monster_name,))
                row = cursor.fetchone()

                if row:
                    # Get column names
                    columns = [description[0] for description in cursor.description]
                    monster_data = dict(zip(columns, row))

                    # Add instance-specific data
                    monster_data['hit_points'] = monster_instance.current_hit_points
                    monster_data['max_hit_points'] = monster_instance.max_hit_points

                    print(f"[COMBAT_MGR_DATA] Fetched {monster_instance.monster_name}: has_actions={('actions' in monster_data)}, actions_len={len(monster_data.get('actions', ''))}")

                    return monster_data

        except Exception as e:
            print(f"Error getting monster data: {e}")

        return None

    def _handle_combat_manager_result(self, result, monster_instance, encounter_panel):
        """Handle the results from combat manager monster attack."""
        try:
            # Log attack results
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Log each attack with detailed information
                    for attack in result.get('attacks', []):
                        if attack.get('hit'):
                            # Enhanced hit logging with details like player attacks
                            d20_roll = attack.get('d20_roll', '?')
                            attack_bonus = attack.get('attack_bonus', 0)
                            attack_total = attack.get('attack_roll', 0)
                            target_ac = attack.get('target_ac', '?')
                            damage = attack.get('damage', 0)
                            action_name = attack.get('action_name', 'Attack')
                            is_critical = attack.get('is_critical', False)
                            damage_dice = attack.get('damage_dice', '?')

                            # Format attack type
                            attack_type = "[CRITICAL HIT!]" if is_critical else "[MONSTER ATTACK]"

                            # Log attack roll with breakdown
                            parent.log_panel.log_combat(
                                f"{attack_type} {monster_instance.monster_name} {action_name} hits! Attack: d20({d20_roll}) +{attack_bonus} = {attack_total} vs AC {target_ac}"
                            )

                            # Log damage with dice breakdown
                            if damage_dice and damage_dice != '?':
                                parent.log_panel.log_combat(f"💥 Damage: {damage_dice} = {damage} damage")
                            else:
                                parent.log_panel.log_combat(f"💥 Damage: {damage} damage")

                            # Log any effects (conditions, saves)
                            for effect in attack.get('effects', []):
                                parent.log_panel.log_combat(f"[EFFECT] {effect}")
                        else:
                            # Enhanced miss logging with details
                            d20_roll = attack.get('d20_roll', '?')
                            attack_bonus = attack.get('attack_bonus', 0)
                            attack_total = attack.get('attack_roll', 0)
                            target_ac = attack.get('target_ac', '?')
                            action_name = attack.get('action_name', 'Attack')

                            parent.log_panel.log_combat(
                                f"[MONSTER ATTACK] {monster_instance.monster_name} {action_name} misses! Attack: d20({d20_roll}) +{attack_bonus} = {attack_total} vs AC {target_ac}"
                            )

                    # Apply total damage to player
                    total_damage = result.get('total_damage', 0)
                    if total_damage > 0 and hasattr(parent, 'character_sheet'):
                        self._apply_damage_to_player(total_damage, "physical", parent.character_sheet.character_data)
                        parent.log_panel.log_combat(f"[DAMAGE] Player takes {total_damage} total damage!")

                    break
                parent = parent.parent()

            print(f"⚔ [DEBUG] Combat manager result processed: {result}")

        except Exception as e:
            print(f"Error handling combat manager result: {e}")
            import traceback
            traceback.print_exc()

    def _build_weapon_dict_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build weapon dictionary from action context for service calls.

        Raises:
            ValueError: If required weapon data is missing from context
        """
        # Validate required weapon data
        weapon_name = context.get('name')
        if not weapon_name:
            raise ValueError("Weapon name is required but missing from context")

        damage_dice = context.get('damage_dice')
        if not damage_dice:
            raise ValueError(f"Damage dice is required but missing for weapon '{weapon_name}'")

        damage_type = context.get('damage_type')
        if not damage_type:
            raise ValueError(f"Damage type is required but missing for weapon '{weapon_name}'")

        # Handle weapon_properties that might be a list - convert to string
        weapon_props = context.get('weapon_properties', '')
        if isinstance(weapon_props, list):
            weapon_props = ', '.join(str(prop) for prop in weapon_props)
        elif weapon_props is None:
            weapon_props = ''
        else:
            weapon_props = str(weapon_props)

        return {
            'name': str(weapon_name),
            'weapon_properties': weapon_props,
            'damage_dice': str(damage_dice),
            'damage_type': str(damage_type),
            'mastery_property': str(context.get('mastery_property', context.get('weapon_mastery', '')))
        }

    def _log_to_parent(self, message: str):
        """Log message to parent's log panel."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(message)
                break
            parent = parent.parent()

    @staticmethod
    def _normalize_feature_name(name: str) -> str:
        """Normalize feature names for internal lookups."""
        return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

    def _get_feature_data(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve feature metadata by display name."""
        features = getattr(self, 'character_features', None)
        if not isinstance(features, dict):
            return None
        cache = getattr(self, '_normalized_feature_cache', None)
        if cache is None:
            cache = {}
            self._normalized_feature_cache = cache
        normalized = self._normalize_feature_name(feature_name)
        if normalized in cache:
            return cache[normalized]
        for display_name, data in features.items():
            cache[self._normalize_feature_name(display_name)] = data
        return cache.get(normalized)

    @staticmethod
    def _extract_weapon_properties(weapon: Dict[str, Any]) -> List[str]:
        """Safely extract weapon property tags as a list."""
        if not isinstance(weapon, dict):
            return []
        props = weapon.get('weapon_properties') or weapon.get('properties') or []
        if isinstance(props, str):
            props = [p.strip() for p in props.split(',') if p.strip()]
        elif isinstance(props, (tuple, set)):
            props = list(props)
        elif not isinstance(props, list):
            props = []
        return props

    def _get_feat_resource_remaining(self, feat_name: str, resource_type: str) -> int:
        """Get remaining uses for a feat resource."""
        try:
            # Get current character from parent
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    if hasattr(game_engine, 'current_character') and game_engine.current_character:
                        character = game_engine.current_character
                        if 'feat_resources' in character:
                            resource_key = f"{feat_name}_{resource_type}"
                            resource_data = character['feat_resources'].get(resource_key, {})
                            return resource_data.get('current', 0)
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"DEBUG: Error in _get_feat_resource_remaining: {e}")
        return 0
    
    def _use_feat_resource(self, feat_name: str, resource_type: str):
        """Use a feat resource - decrement remaining uses."""
        print(f"DEBUG: _use_feat_resource called for {feat_name}_{resource_type}")
        try:
            # Get current character from parent
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    if hasattr(game_engine, 'current_character') and game_engine.current_character:
                        character = game_engine.current_character
                        if 'feat_resources' not in character:
                            print(f"DEBUG: Character missing feat_resources field, initializing...")
                            character['feat_resources'] = {}
                        
                        resource_key = f"{feat_name}_{resource_type}"
                        if resource_key in character['feat_resources']:
                            current_uses = character['feat_resources'][resource_key].get('current', 0)
                            if current_uses > 0:
                                character['feat_resources'][resource_key]['current'] = current_uses - 1
                                print(f"DEBUG: Decremented {resource_key} to {character['feat_resources'][resource_key]['current']}")
                                # Save character
                                try:
                                    game_engine.save_game_sync()
                                    print(f"DEBUG: Game saved successfully")
                                except Exception as e:
                                    print(f"DEBUG: Save failed: {e}")
                                # Update action card display
                                self._refresh_action_availability()
                            else:
                                print(f"DEBUG: {resource_key} has no uses remaining ({current_uses})")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"DEBUG: Error in _use_feat_resource: {e}")
    
    def _refresh_action_availability(self):
        """Refresh the availability state of all action cards and tabs."""
        for action_type, card in self.action_cards.items():
            available = self._is_action_available(action_type)
            card.set_available(available)

        # Also update economy display and tab states if in combat
        if self.action_economy_enabled and self.current_combat_session:
            self._update_economy_status_display()
    
    def _get_action_cooldown(self, action_type: ActionType) -> int:
        """Get the cooldown turns for an action."""
        cooldowns = {
            ActionType.REST: 1,  # Can't rest again immediately
            ActionType.DASH: 0,  # No cooldown, but uses action
        }
        return cooldowns.get(action_type, 0)
    
    def _update_action_economy(self, used_action: ActionType):
        """Update action economy after using an action."""
        if not self.action_economy_enabled or not self.current_combat_session:
            return

        # Map the action to its economy type and consume it
        try:
            from models.action_economy import ActionEconomyType
            economy_type = self._map_action_to_economy_type(used_action)

            if economy_type and self.character_id:
                # Consume the action through the combat session helper so availability updates stay in sync
                success = self.current_combat_session.use_action(
                    self.character_id,
                    economy_type.value,
                    used_action.value,
                    {"source": "action_panel"}
                )

                if success:
                    # Update the display to reflect the new state
                    self._refresh_action_availability()

                    print(f"[ACTION ECONOMY] Consumed {economy_type.value} for {used_action.value}")
                else:
                    print(f"[ACTION ECONOMY] Failed to consume {economy_type.value} for {used_action.value}")

        except Exception as e:
            print(f"Error updating action economy: {e}")
    
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
        print(f"ACTION PANEL: Setting character context with keys: {list(context.keys())}")
        print(f"ACTION PANEL: class_id = {context.get('class_id', 'NOT_FOUND')}")
        self.character_context = context
        self._update_card_availability()
        # Update potion card to show count
        self._update_potion_card()
        # Also update visible cards to show/hide potion card based on inventory
        self._update_visible_cards()
    
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
        self.current_theme = theme_name
        self._apply_styles_for_theme(theme_name)
        for card in self.action_cards.values():
            card.update_theme_styles(theme_name)
    
    def load_character_equipment(self, equipped_items: Dict[str, Any], character_stats: Dict[str, Any]):
        """Load character equipment and stats to create weapon cards."""
        equipped_items = equipped_items or {}
        if not isinstance(equipped_items, dict):
            equipped_items = {}

        hydrated_items: Dict[str, Any] = {}
        for slot, item in equipped_items.items():
            hydrated_items[slot] = self._prepare_equipped_item(item)

        self.equipped_weapons = hydrated_items
        if isinstance(character_stats, dict):
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
        
        if isinstance(character_features, list):
            mapped = {feature.get('name'): feature for feature in character_features if isinstance(feature, dict) and feature.get('name')}
        else:
            mapped = character_features or {}
        self.character_features = mapped
        self._normalized_feature_cache = {}
        
        if isinstance(getattr(self, 'character_context', None), dict):
            feature_flags = self.character_context.setdefault('feature_flags', {})
            feature_flags['remarkable_athlete'] = 'Remarkable Athlete' in mapped
            feature_flags['heroic_warrior'] = 'Heroic Warrior' in mapped
            feature_flags['survivor'] = 'Survivor' in mapped

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
    
    def load_weapon_masteries(self, weapon_masteries: List[str], assignments: Optional[List[Dict[str, Any]]] = None):
        """Load character weapon masteries and assignment map."""
        normalized = [m.title() for m in (weapon_masteries or [])]
        self.character_weapon_masteries = normalized
        self.character_weapon_mastery_map = {}
        self._weapon_mastery_cache = {}
        for entry in assignments or []:
            weapon_name = (entry.get("weapon_name") or "").strip()
            mastery_type = (entry.get("mastery_type") or "").strip()
            if weapon_name and mastery_type:
                self.character_weapon_mastery_map[weapon_name] = mastery_type.title()

        if isinstance(self.character_context, dict):
            self.character_context['weapon_masteries'] = normalized
            self.character_context['weapon_mastery_assignments'] = assignments or []

        if not normalized and not (assignments or []) and self._character_has_weapon_mastery_feature():
            character_id = self._resolve_character_id()
            if character_id:
                try:
                    service = self._get_weapon_mastery_service()
                    options = service.get_character_weapon_options(character_id)
                    if options:
                        normalized_assignments = service.set_character_masteries(character_id, options)
                        normalized = [entry.get('mastery_type', '').title() for entry in normalized_assignments]
                        self.character_weapon_masteries = normalized
                        self.character_weapon_mastery_map = {
                            entry.get('weapon_name'): entry.get('mastery_type', '').title()
                            for entry in normalized_assignments
                            if entry.get('weapon_name') and entry.get('mastery_type')
                        }
                        if isinstance(self.character_context, dict):
                            self.character_context['weapon_masteries'] = normalized
                            self.character_context['weapon_mastery_assignments'] = normalized_assignments
                except Exception as exc:
                    print(f"[WeaponMastery] Failed to bootstrap masteries for {character_id}: {exc}")

    def load_character_resources(self, character_data: Dict[str, Any]):
        """Load character advantage resources (Lucky, Inspiration)."""
        self.resource_manager = AdvantageResourceManager(character_data)
        
        # Update all action cards with the resource manager
        cards_updated = 0
        for card in self.action_cards.values():
            if hasattr(card, 'set_resource_manager'):
                card.set_resource_manager(self.resource_manager)
                cards_updated += 1
                
    
    def set_target_monster(self, monster_id: str):
        """Set the target monster for attacks."""
        self.target_monster_id = monster_id
    
    
    
    def _log_weapon_mastery_effects_old(self, mastery_effects: Dict[str, Any]):
        """OLD VERSION - Log weapon mastery effects to combat log."""
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
                            parent.log_panel.log_combat(f"[SWORD] {description} - {damage} damage")
                        elif 'save_dc' in effect_data:
                            save_dc = effect_data['save_dc']
                            parent.log_panel.log_combat(f"[SWORD] {description} - DC {save_dc}")
                        else:
                            parent.log_panel.log_combat(f"[SWORD] {description}")
                break
            parent = parent.parent()
    
    def _get_dueling_bonus(self, context: Dict[str, Any]) -> int:
        """Check if character gets Dueling fighting style bonus (+2 damage)."""
        if not self.character_context:
            return 0
        
        # Check if character has Dueling fighting style
        # Look for Fighting Style feature and check actual character data
        if not self.character_context:
            return 0
            
        character_id = self._resolve_character_id()
        if not character_id:
            return 0
            
        # Query database directly for fighting styles (can have multiple at higher levels)
        import sqlite3
        db_path = self._resolve_db_path()
        fighting_styles = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT feature_name FROM character_features 
                WHERE character_id = ? AND feature_name LIKE 'Fighting Style:%'
                """,
                (character_id,),
            )
            fighting_styles = cursor.fetchall()
        except sqlite3.OperationalError as exc:
            print(f"[FightingStyle] Unable to query fighting styles ({exc})")
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        # Check if any fighting style is Dueling
        has_dueling = any('Dueling' in style[0] for style in fighting_styles)
        if not has_dueling:
            return 0
        
        # Check weapon requirements: one-handed melee weapon
        weapon_props = self._get_context_weapon_properties(context)
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        
        # Must not be two-handed or ranged
        is_two_handed = 'two-handed' in weapon_props_lower
        is_ranged = 'ranged' in weapon_props_lower or damage_type == 'ranged'
        
        if is_two_handed or is_ranged:
            return 0
        
        # Check if off-hand is free (no off-hand weapon or shield)
        # With the new system, two-handed weapons occupy both slots, so this check works perfectly
        off_hand_item = self.character_context.get('equipment_off_hand')
        shield_item = self.character_context.get('equipment_shield')
        
        if off_hand_item or shield_item:
            return 0
        
        # Dueling bonus is now logged in damage breakdown automatically
        
        return 2
    
    def _get_rage_damage_bonus(self, context: Dict[str, Any]) -> int:
        """Check if Barbarian gets rage damage bonus for melee weapon attacks using Strength."""
        if not isinstance(self.character_context, dict):
            return 0

        # Only applies if raging
        if not self.character_context.get('raging', False):
            return 0

        # Rage bonus only applies to barbarians
        class_id = self.character_context.get('class_id', '').lower()
        if class_id != 'barbarian':
            return 0

        # Determine if attack qualifies for rage bonus
        # D&D 5e: Rage damage applies to melee weapon attacks using Strength
        _, damage_type = self._get_context_damage_profile(context)
        weapon_props = self._get_context_weapon_properties(context)
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        is_ranged = 'ranged' in weapon_props_lower or damage_type == 'ranged'

        # Must be melee attack
        if is_ranged:
            return 0

        # Check if attack uses Strength (most melee weapons do, but finesse weapons could use Dex)
        # For now, assume all melee attacks use Strength unless it's explicitly a Dex-based weapon
        # TODO: Add proper ability score checking for finesse weapons

        # Unarmed strikes always use Strength (unless monk with Dex, but monks don't get Rage)
        # Great axe definitely uses Strength
        # Most melee weapons use Strength unless finesse property

        level = self.character_context.get('level', 1)
        if level >= 16:
            return 4
        if level >= 9:
            return 3
        return 2

    def _get_all_damage_bonuses(self, context: Dict[str, Any]) -> dict:
        """Get all feature-based damage bonuses and their values."""
        bonuses = {}
        
        # Dueling Fighting Style
        dueling_bonus = self._get_dueling_bonus(context)
        if dueling_bonus > 0:
            bonuses['Dueling'] = dueling_bonus
        
        # Barbarian Rage
        rage_bonus = self._get_rage_damage_bonus(context)
        if rage_bonus > 0:
            bonuses['Rage'] = rage_bonus
        
        # Two-Weapon Fighting Style (for off-hand attacks)
        twf_bonus = self._get_two_weapon_fighting_damage_bonus(context)
        if twf_bonus > 0:
            bonuses['Two-Weapon Fighting'] = twf_bonus
        
        # Great Weapon Master (if implemented later)
        # gwm_bonus = self._get_great_weapon_master_bonus(context)
        # if gwm_bonus > 0:
        #     bonuses['Great Weapon Master'] = gwm_bonus
        
        # Sharpshooter (if implemented later)
        # sharpshooter_bonus = self._get_sharpshooter_bonus(context) 
        # if sharpshooter_bonus > 0:
        #     bonuses['Sharpshooter'] = sharpshooter_bonus
        
        return bonuses
    
    def _use_healing_potion(self, context: Dict[str, Any]):
        """Use a healing potion to restore hit points."""
        character_id = context.get('id')
        if not character_id:
            print("[DEBUG] No character ID found for potion use")
            return
        
        # Check if character has healing potions in inventory
        if not self._has_healing_potion(character_id):
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("[FAIL] No healing potions available!")
                    break
                parent = parent.parent()
            return
        
        # Roll healing: 2d4+4
        import random
        roll1 = random.randint(1, 4)
        roll2 = random.randint(1, 4)
        healing = roll1 + roll2 + 4
        
        # Apply healing to character
        current_hp = context.get('hit_points_current', 0)
        max_hp = context.get('hit_points_max', 0)
        new_hp = min(current_hp + healing, max_hp)
        actual_healing = new_hp - current_hp
        
        # Update character HP in database
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE characters 
                SET hit_points_current = ?, current_hit_points = ?
                WHERE id = ?
            """, (new_hp, new_hp, character_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating character HP: {e}")
        
        # Remove one healing potion from inventory
        self._consume_healing_potion(character_id)
        
        # Update character context
        self.character_context['hit_points_current'] = new_hp
        self.character_context['current_hit_points'] = new_hp
        
        # Log the healing
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[POTION] Used Healing Potion: 2d4([{roll1}, {roll2}]) + 4 = {healing} healing")
                if actual_healing > 0:
                    parent.log_panel.log_combat(f"💚 Restored {actual_healing} HP ({current_hp} -> {new_hp})")
                else:
                    parent.log_panel.log_combat(f"💚 Already at full health ({current_hp} HP)")
                break
            parent = parent.parent()
        
        # Update character panel if available - use separate parent search
        parent = self.parent()
        while parent:
            if hasattr(parent, 'character_panel'):
                parent.character_panel.update_character_data(self.character_context)
                break
            parent = parent.parent()
        
        # Update potion card to reflect new count
        self._update_potion_card()
        self._update_visible_cards()
    
    def _has_healing_potion(self, character_id: str) -> bool:
        """Check if character has healing potions in inventory."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND (item_name = 'Potion of Healing' OR item_name = 'potion_of_healing') AND quantity > 0
            """, (character_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"[DEBUG] Found {result[0]} healing potions for character {character_id}")
                return result[0] > 0
            else:
                print(f"[DEBUG] No healing potions found for character {character_id}")
                return False
            
        except Exception as e:
            print(f"Error checking healing potion inventory: {e}")
            return False
    
    def _consume_healing_potion(self, character_id: str):
        """Remove one healing potion from character's inventory."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Decrease potion quantity by 1
            cursor.execute("""
                UPDATE character_inventory 
                SET quantity = quantity - 1
                WHERE character_id = ? AND (item_name = 'Potion of Healing' OR item_name = 'potion_of_healing') AND quantity > 0
            """, (character_id,))
            
            # Remove entries with 0 quantity
            cursor.execute("""
                DELETE FROM character_inventory 
                WHERE character_id = ? AND (item_name = 'Potion of Healing' OR item_name = 'potion_of_healing') AND quantity <= 0
            """, (character_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error consuming healing potion: {e}")
    
    def _update_potion_card(self):
        """Update the potion card to show current potion count."""
        if ActionType.USE_POTION not in self.action_cards:
            return
            
        if not self.character_context:
            return
            
        character_id = self._resolve_character_id()
        if not character_id:
            return
            
        # Get potion count
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(quantity) FROM character_inventory 
                WHERE character_id = ? AND (item_name = 'Potion of Healing' OR item_name = 'potion_of_healing') AND quantity > 0
            """, (character_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            potion_count = result[0] if result and result[0] else 0
            
            # Update card description
            card = self.action_cards[ActionType.USE_POTION]
            if potion_count > 0:
                card.set_description(f"Drink a healing potion (2d4+4 HP) - {potion_count} available")
            else:
                card.set_description("No healing potions available")
            
            print(f"[DEBUG] Updated potion card: {potion_count} potions available")
            
        except Exception as e:
            print(f"Error updating potion card: {e}")
    
    def _character_has_potions(self) -> bool:
        """Check if character has any healing potions."""
        if not self.character_context:
            print("[DEBUG] No character context for potion check")
            return False
        character_id = self._resolve_character_id()
        if not character_id:
            print("[DEBUG] No character ID for potion check")
            return False
        has_potions = self._has_healing_potion(character_id)
        print(f"[DEBUG] Character {character_id} has potions: {has_potions}")
        return has_potions
    
    def _apply_fighting_style_effects(self, dice_rolls: list, context: Dict[str, Any]) -> list:
        """Apply fighting style effects to damage dice rolls."""
        if not self.character_context:
            return dice_rolls
        
        # Apply Great Weapon Fighting (modifies dice rolls)
        if self.character_context and self.character_context.get('id'):
            import sqlite3
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT feature_name FROM character_features 
                WHERE character_id = ? AND feature_name LIKE 'Fighting Style:%'
            """, (self.character_context['id'],))
            
            fighting_styles = cursor.fetchall()
            conn.close()
            
            # Check if any fighting style is Great Weapon Fighting
            has_gwf = any('Great Weapon Fighting' in style[0] for style in fighting_styles)
            if has_gwf:
                dice_rolls = self._apply_great_weapon_fighting(dice_rolls, context)
        
        return dice_rolls
    
    def _get_fighting_style_attack_bonus(self, context: Dict[str, Any]) -> int:
        """Get attack bonus from fighting styles."""
        if not self.character_context:
            return 0
        
        character_feats = getattr(self, 'character_feats', [])
        bonus = 0
        
        # Archery: +2 to ranged weapon attacks
        if "Archery" in character_feats:
            weapon_props = self._get_context_weapon_properties(context)
            weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
            
            # Check if this is a ranged weapon attack (not thrown melee weapons)
            is_ranged_weapon = any(prop in weapon_props_lower for prop in ['ranged'])
            weapon_name = context.get('name', '').lower()
            is_bow_or_crossbow = any(bow_type in weapon_name for bow_type in ['bow', 'crossbow', 'sling'])
            
            if is_ranged_weapon or is_bow_or_crossbow:
                bonus += 2
                self._log_fighting_style("Archery", "Attack", "+2 to ranged weapon attack")
        
        return bonus
    
    def _get_fighting_style_damage_bonus(self, context: Dict[str, Any]) -> int:
        """Get damage bonus from fighting styles."""
        if not self.character_context:
            return 0
        
        bonus = 0
        character_id = self._resolve_character_id()
        if not character_id:
            return 0
            
        # Query database for fighting styles
        import sqlite3
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT feature_name FROM character_features 
            WHERE character_id = ? AND feature_name LIKE 'Fighting Style:%'
        """, (character_id,))
        
        fighting_styles = cursor.fetchall()
        conn.close()
        
        # Check each fighting style
        for style_row in fighting_styles:
            style_name = style_row[0]
            
            # Dueling: +2 damage when wielding a melee weapon in one hand and no other weapons
            if "Dueling" in style_name:
                bonus += self._apply_dueling_bonus(context)
        
            # Thrown Weapon Fighting: +2 damage to thrown weapon attacks when used at range
            if "Thrown Weapon Fighting" in style_name:
                weapon_props = self._get_context_weapon_properties(context)
                weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
                
                # Must be a thrown weapon used as a ranged attack
                if 'thrown' in weapon_props_lower and context.get('is_ranged_attack', False):
                    bonus += 2
                    self._log_fighting_style("Thrown Weapon Fighting", "Damage", "+2 to thrown weapon damage")
            
            # Two-Weapon Fighting: Add ability modifier to off-hand attack damage
            if "Two-Weapon Fighting" in style_name:
                # Only applies to off-hand attacks where ability modifier would normally be excluded
                if context.get('action_type') == ActionType.ATTACK_OFF_HAND:
                    # In D&D, off-hand attacks don't normally get ability modifier unless you have this fighting style
                    # So we need to add it back in
                    if context.get('strength'):
                        str_mod = (context.get('strength', 10) - 10) // 2
                    else:
                        str_mod = (context.get('dexterity', 10) - 10) // 2
                    
                    # Only add if the weapon qualifies for two-weapon fighting (light weapons)
                    weapon_props = self._get_context_weapon_properties(context)
                    weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
                    
                    if 'light' in weapon_props_lower:
                        bonus += str_mod
                        self._log_fighting_style("Two-Weapon Fighting", "Damage", f"+{str_mod} ability modifier to light off-hand weapon")
        
        return bonus
    
    def _get_fighting_style_ac_bonus(self) -> int:
        """Get AC bonus from fighting styles."""
        if not self.character_context:
            return 0
        
        character_feats = getattr(self, 'character_feats', [])
        
        # Defense: +1 AC while wearing armor
        if "Defense" in character_feats:
            # Check if character is actually wearing armor by checking equipped items
            # This would need integration with equipment system to be fully accurate
            # For now, use a heuristic: if AC is significantly above base AC + DEX, assume armor
            current_ac = self.character_context.get('armor_class', 10)
            dex_mod = ((self.character_context.get('dexterity', 10) - 10) // 2)
            base_unarmored_ac = 10 + dex_mod
            
            # If AC is more than 2 points above unarmored AC, assume wearing armor
            if current_ac >= base_unarmored_ac + 2:
                return 1
        
        return 0
    
    def _log_fighting_style(self, style_name: str, bonus_type: str, description: str):
        """Log fighting style bonuses to combat log."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[FIGHTING STYLE] {style_name}: {description}")
                break
            parent = parent.parent()
    
    def _apply_savage_attacker(self, dice_rolls: list, num_dice: int, die_size: int, context: Dict[str, Any]) -> list:
        """Apply Savage Attacker feat - roll weapon damage dice twice, use higher roll (first attack per round only)."""
        if not self.first_attack_this_round:
            return dice_rolls
            
        # Check if character has Savage Attacker feat
        character_feats = self.character_context.get('feats', [])
        if 'Savage Attacker' not in character_feats:
            return dice_rolls
        
        # Only apply to weapon attacks (not spell damage)
        if not context.get('weapon', False):
            return dice_rolls
            
        import random
        
        # Roll the same dice again
        second_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        
        # Compare totals and use higher
        first_total = sum(dice_rolls)
        second_total = sum(second_rolls)
        
        if second_total > first_total:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[SAVAGE ATTACKER] First roll: {dice_rolls} = {first_total}, Second roll: {second_rolls} = {second_total} - Using higher!")
                    break
                parent = parent.parent()
            self.first_attack_this_round = False  # Mark first attack used
            return second_rolls
        else:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[SAVAGE ATTACKER] First roll: {dice_rolls} = {first_total}, Second roll: {second_rolls} = {second_total} - Using first!")
                    break
                parent = parent.parent()
            self.first_attack_this_round = False  # Mark first attack used
            return dice_rolls
    
    def _apply_dueling_bonus(self, context: Dict[str, Any]) -> int:
        """Apply Dueling fighting style bonus (+2 damage when wielding one melee weapon in one hand and no other weapons)."""
        weapon_props = self._get_context_weapon_properties(context)
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        
        # Must be a melee weapon (not ranged)
        weapon_name = context.get('name', '').lower()
        is_ranged_weapon = any(ranged_type in weapon_name for ranged_type in ['bow', 'crossbow', 'sling'])
        if is_ranged_weapon or 'ranged' in weapon_props_lower:
            return 0
        
        # Must not be two-handed
        if 'two-handed' in weapon_props_lower:
            return 0
        
        # Must not be using versatile weapon with two hands (simplified: assume one-handed use)
        # Must not be using a shield or second weapon (simplified check)
        action_type = context.get('action_type')
        
        # Only applies to main-hand attacks (not off-hand, since that implies two weapons)
        if action_type == ActionType.ATTACK_OFF_HAND:
            return 0
        
        # If all conditions met, apply dueling bonus
        self._log_fighting_style("Dueling", "Damage", "+2 damage (wielding one melee weapon in one hand)")
        return 2
    
    def _apply_great_weapon_fighting(self, dice_rolls: list, context: Dict[str, Any]) -> list:
        """Apply Great Weapon Fighting: reroll 1s and 2s on melee weapons with two-handed or heavy property."""
        weapon_props = self._get_context_weapon_properties(context)
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []
        
        # Great Weapon Fighting requires a melee weapon with two-handed OR heavy property
        # Used with two hands (two-handed weapons are always two-handed, versatile can be used two-handed)
        is_two_handed = 'two-handed' in weapon_props_lower
        is_heavy = 'heavy' in weapon_props_lower  
        is_versatile = 'versatile' in weapon_props_lower
        
        # Must be two-handed OR heavy, and used as a melee weapon
        if not (is_two_handed or is_heavy or is_versatile):
            return dice_rolls
        
        # Get the damage die size from context to reroll correctly
        damage_dice, damage_type = self._get_context_damage_profile(context)
        die_size = 6  # Default
        if 'd' in damage_dice:
            try:
                _, die_size_str = damage_dice.split('d')
                # Handle cases like "2d6+1" by extracting just the die size
                die_size = int(die_size_str.split('+')[0].split('-')[0])
            except:
                die_size = 6  # Fallback
        
        # Apply Great Weapon Fighting (2024 rules): treat 1s and 2s as 3s
        modified_rolls = []
        changes_made = []
        
        for roll in dice_rolls:
            if roll <= 2:
                # Treat 1s and 2s as 3s
                modified_rolls.append(3)
                changes_made.append((roll, 3))
            else:
                modified_rolls.append(roll)
        
        # Log the fighting style effect if changes were made
        if changes_made:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    original_str = ', '.join(map(str, dice_rolls))
                    modified_str = ', '.join(map(str, modified_rolls))
                    change_details = ', '.join([f"{old}->{new}" for old, new in changes_made])
                    weapon_type = "two-handed" if is_two_handed else "heavy" if is_heavy else "versatile"
                    parent.log_panel.log_combat(f"[FIGHTING STYLE] Great Weapon Fighting: [{original_str}] -> [{modified_str}] ({weapon_type} weapon: {change_details})")
                    break
                parent = parent.parent()
        
        return modified_rolls
    
    def _apply_weapon_mastery_effects(self, weapon_name: str, attack_total: int, target_ac: int, hit: bool, damage_total: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply weapon mastery effects using simplified database-driven logic."""
        if not self.character_context:
            return {}
        
        # Step 1: Check if weapon has mastery
        mastery_name = self._get_weapon_mastery(weapon_name)
        if not mastery_name:
            return {}
        
        # Step 2: Check if character has Weapon Mastery feature
        if not self._character_has_weapon_mastery_feature():
            return {}
        
        # Step 3: Apply the mastery effect
        return self._apply_mastery_effect(mastery_name, hit, context)
    
    def _get_weapon_mastery(self, weapon_name: str) -> Optional[str]:
        """Get mastery for a weapon from cached assignments or equipment data."""
        if not weapon_name:
            return None

        assignments = getattr(self, 'character_weapon_mastery_map', {}) or {}
        mastery = assignments.get(weapon_name)
        if not mastery:
            lower_name = weapon_name.lower()
            for key, value in assignments.items():
                if key.lower() == lower_name:
                    mastery = value
                    break

        if mastery:
            return mastery

        try:
            service = self._get_weapon_mastery_service()
            return service.get_weapon_mastery_for_weapon(weapon_name)
        except Exception as exc:
            print(f"Error getting weapon mastery for {weapon_name}: {exc}")
            return None

    def _get_mastery_definition(self, mastery_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve and cache mastery metadata from the service."""
        cache_key = (mastery_name or '').strip().title()
        if not cache_key:
            return None

        cache = getattr(self, '_weapon_mastery_cache', None)
        if cache is None:
            cache = {}
            self._weapon_mastery_cache = cache

        if cache_key in cache:
            return cache[cache_key]

        try:
            definition = self._get_weapon_mastery_service().get_mastery_definition(cache_key)
        except Exception as exc:
            print(f"[WeaponMastery] Failed to load definition for '{mastery_name}': {exc}")
            definition = None

        cache[cache_key] = definition
        return definition

    def _character_has_weapon_mastery_feature(self) -> bool:
        """Check if character class gets weapon masteries (Fighter, Rogue, Barbarian, Paladin)."""
        if not self.character_context:
            return False
        
        # Check character's class
        class_id = self.character_context.get('class_id', '').lower()
        mastery_classes = ['fighter', 'rogue', 'barbarian', 'paladin']
        
        return class_id in mastery_classes
    
    def _apply_mastery_effect(self, mastery_name: str, hit: bool, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the specific mastery effect using the service definitions."""
        try:
            mastery_key = (mastery_name or '').strip().lower()
            if mastery_key == 'cleave':
                if context.get('is_cleave_followup') or getattr(self, '_cleave_followup_in_progress', False):
                    return {}

            definition = self._get_mastery_definition(mastery_name)
            if not definition:
                return {}

            trigger_condition = (definition.get('trigger_condition') or 'on_hit').lower()
            if trigger_condition == 'on_miss':
                should_trigger = not hit
            elif trigger_condition == 'on_attack':
                should_trigger = True
            else:
                should_trigger = hit

            if not should_trigger:
                return {}

            special_effects = definition.get('special_effects') or ''
            return self._execute_mastery_effect(
                mastery_name,
                special_effects,
                context,
                bool(definition.get('requires_save')),
                definition.get('save_ability'),
                definition.get('save_dc_formula'),
                definition.get('damage_formula'),
            )
        except Exception as exc:
            print(f"[WeaponMastery] Failed to apply mastery '{mastery_name}': {exc}")
            return {}
    
    def _execute_mastery_effect(self, mastery_name: str, special_effects: str, context: Dict[str, Any], 
                               requires_save: bool, save_ability: Optional[str], save_dc_formula: Optional[str], 
                               damage_formula: Optional[str]) -> Dict[str, Any]:
        """Execute the specific mastery effect."""
        effects = {}
        
        try:
            if special_effects == 'damage_on_miss':  # Graze
                # Deal ability modifier damage on miss
                ability_mod = (context.get('strength', 10) - 10) // 2
                if context.get('finesse'):  # Use DEX if finesse weapon
                    ability_mod = max(ability_mod, (context.get('dexterity', 10) - 10) // 2)
                
                if ability_mod > 0:  # Only positive modifiers
                    effects['graze_damage'] = ability_mod
                    self._log_mastery_effect("Graze", f"Deals {ability_mod} damage on miss")
            
            elif special_effects == 'extra_attack_adjacent':  # Cleave
                effects['cleave'] = True
                self._log_mastery_effect("Cleave", "Can attack second creature within 5 feet")
            
            elif special_effects == 'light_attack_as_action':  # Nick
                effects['nick'] = True
                self._log_mastery_effect("Nick", "Light weapon extra attack as part of Attack action")
            
            elif special_effects == 'push_10_feet':  # Push
                effects['push'] = 10
                self._log_mastery_effect("Push", "Target pushed up to 10 feet away")
            
            elif special_effects == 'disadvantage_next_attack':  # Sap
                effects['sap'] = True
                self._log_mastery_effect("Sap", "Target has disadvantage on next attack")
            
            elif special_effects == 'reduce_speed_10':  # Slow
                effects['slow'] = 10
                self._log_mastery_effect("Slow", "Target's speed reduced by 10 feet")
            
            elif special_effects == 'prone_on_failed_save':  # Topple
                # Calculate save DC: 8 + ability modifier + proficiency bonus
                ability_mod = (context.get('strength', 10) - 10) // 2
                if context.get('finesse'):  # Use DEX if finesse weapon
                    ability_mod = max(ability_mod, (context.get('dexterity', 10) - 10) // 2)
                
                from services.proficiency_bonus import get_proficiency_bonus_from_context
                prof_bonus = get_proficiency_bonus_from_context(context)
                save_dc = 8 + ability_mod + prof_bonus
                
                effects['topple_dc'] = save_dc
                self._log_mastery_effect("Topple", f"Constitution save DC {save_dc} or prone")
            
            elif special_effects == 'advantage_next_attack':  # Vex
                effects['vex'] = True
                # Set Vex target for next attack
                self.vex_target_id = context.get('target_monster_id')
                self._log_mastery_effect("Vex", "Advantage on next attack against this target")
        
        except Exception as e:
            print(f"Error executing mastery effect {mastery_name}: {e}")
        
        return effects
    
    def _log_mastery_effect(self, mastery_name: str, description: str):
        """Log mastery effect to combat log."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[WEAPON MASTERY] {mastery_name}: {description}")
                break
            parent = parent.parent()
    
    def _log_weapon_mastery_effects(self, mastery_effects: Dict[str, Any]):
        """Log weapon mastery effects to combat log."""
        if not mastery_effects:
            return
            
        try:
            # Find parent with log_panel for logging
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Log specific mastery effects with clear descriptions
                    if mastery_effects.get('sap'):
                        parent.log_panel.log_combat("[MASTERY] SAP: Target has disadvantage on its next attack roll")
                    if mastery_effects.get('vex'):
                        parent.log_panel.log_combat("[MASTERY] VEX: You have advantage on your next attack against this target")
                    if mastery_effects.get('slow'):
                        parent.log_panel.log_combat("[MASTERY] SLOW: Target's speed reduced by 10 feet until your next turn")
                    if mastery_effects.get('push'):
                        parent.log_panel.log_combat("[MASTERY] PUSH: Target pushed 10 feet away")
                    if mastery_effects.get('topple_dc'):
                        dc = mastery_effects['topple_dc']
                        parent.log_panel.log_combat(f"[MASTERY] TOPPLE: Target must make CON save DC {dc} or fall prone")
                    if mastery_effects.get('graze_damage'):
                        damage = mastery_effects['graze_damage']
                        parent.log_panel.log_combat(f"[MASTERY] GRAZE: Deals {damage} damage even on a miss")
                    if mastery_effects.get('cleave'):
                        parent.log_panel.log_combat("[MASTERY] CLEAVE: Can make an additional attack against another target within 5 feet")
                    if mastery_effects.get('nick'):
                        parent.log_panel.log_combat("[MASTERY] NICK: Can make an additional light weapon attack")
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
    
    def _ensure_combat_session(self):
        """Ensure there is an action-economy combat session available."""
        if not self.action_economy_enabled:
            return
        if self.current_combat_session and self.character_id:
            return
        character_id = (self.character_context or {}).get('id')
        if not character_id:
            return
        encounter_panel = self._get_encounter_panel()
        if encounter_panel:
            try:
                encounter_mode = getattr(encounter_panel, 'encounter_mode', None)
                if encounter_mode not in ('combat', 'encounter'):
                    # Do not auto-start combat economy outside encounter contexts
                    return
                existing_session = getattr(encounter_panel, 'current_combat_session', None)
                if existing_session:
                    self.set_combat_session(existing_session, character_id)
                    return
                if hasattr(encounter_panel, '_init_combat_session'):
                    encounter_panel._init_combat_session()
                    existing_session = getattr(encounter_panel, 'current_combat_session', None)
                    if existing_session:
                        self.set_combat_session(existing_session, character_id)
                        return
            except Exception as e:
                print(f"Error synchronizing combat session: {e}")
        try:
            from encounter_pane.encounter_panel import CombatSession
        except Exception as e:
            print(f"Failed to import CombatSession for fallback: {e}")
            return
        try:
            session = CombatSession()
            session.start_combat_with_action_economy(character_id)
            self.set_combat_session(session, character_id)
            if encounter_panel is not None:
                setattr(encounter_panel, 'current_combat_session', session)
            print(f"[ACTION ECONOMY] Bootstrapped combat session for {character_id}")
        except Exception as e:
            print(f"Failed to bootstrap combat session: {e}")

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

        # Update tab visual states based on action economy
        self._update_tab_availability(status)

    def _update_action_economy_display(self):
        """Update action economy display including tabs and cards."""
        self._refresh_action_availability()

    def _update_tab_availability(self, status: Dict[str, Any]):
        """Update the visual state of category tabs based on action economy."""
        if not self.category_buttons:
            return

        # Map categories to their availability status
        category_availability = {
            ActionCategory.COMBAT: status.get("action_available", True),
            ActionCategory.MOVEMENT: status.get("movement_remaining", 30) > 0,
            ActionCategory.BONUS: status.get("bonus_action_available", True),
            ActionCategory.REACTION: status.get("reaction_available", True),
            ActionCategory.FREE: True  # Free actions always available
        }

        # Apply styles to each category button
        for i, category in enumerate(ActionCategory):
            button = self.category_buttons.buttons()[i]
            available = category_availability.get(category, True)

            if available:
                # Available - normal style
                button.setStyleSheet("""
                    QPushButton#categoryButton {
                        background-color: #3a3a3a;
                        color: white;
                        border: 1px solid #555;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton#categoryButton:checked {
                        background-color: #4a90e2;
                        border: 2px solid #357abd;
                    }
                    QPushButton#categoryButton:hover {
                        background-color: #4a4a4a;
                    }
                """)
            else:
                # Unavailable - greyed out style
                button.setStyleSheet("""
                    QPushButton#categoryButton {
                        background-color: #2a2a2a;
                        color: #666666;
                        border: 1px solid #444;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: normal;
                    }
                    QPushButton#categoryButton:checked {
                        background-color: #333333;
                        border: 2px solid #555555;
                        color: #777777;
                    }
                    QPushButton#categoryButton:hover {
                        background-color: #2a2a2a;
                    }
                """)

            # Optionally disable the button entirely (uncomment if desired)
            # button.setEnabled(available)

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
        # Treat spell actions as standard actions until per-spell casting-time metadata is exposed
        main_actions = {
            ActionType.ATTACK_MAIN_HAND,
            ActionType.CAST_SPELL, ActionType.SPELL_ATTACK, ActionType.SPELL_UTILITY,
            ActionType.DASH, ActionType.DODGE,
            ActionType.HIDE, ActionType.SEARCH, ActionType.USE_ITEM,
            ActionType.SIGNATURE_MOVE
        }
        
        # Bonus Actions
        bonus_actions = {
            ActionType.SECOND_WIND, ActionType.USE_POTION,
            ActionType.NICK_MASTERY, ActionType.CLEAVE_MASTERY, ActionType.RAGE,
            ActionType.ATTACK_OFF_HAND, ActionType.INSTINCTIVE_POUNCE,
            ActionType.INTIMIDATING_PRESENCE, ActionType.BRUTAL_STRIKE_FORCEFUL,
            ActionType.BRUTAL_STRIKE_HAMSTRING, ActionType.BRUTAL_STRIKE_STAGGERING,
            ActionType.BRUTAL_STRIKE_SUNDERING
        }
        
        # Reactions
        reactions = {
            ActionType.OPPORTUNITY, ActionType.RETALIATION, ActionType.SPELL_REACTION
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
        from models.action_economy import ActionEconomyType
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
                    parent.log_panel.log_combat(f"[FAIL] Cannot use {action_type.value}: {reason}")
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
                    parent.log_panel.log_combat(f"[LIGHTNING] Used {economy_name}: {action_type.value}")
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
    
    # === CLASS FEATURE METHODS ===
    
    def _has_class_feature(self, feature_name: str) -> bool:
        """Check if character has a specific class feature."""
        if not self.character_context:
            return False
        
        character_features = self.character_features or {}
        return feature_name in character_features
    
    def _check_divine_smite(self, is_critical: bool, target_monster: Any, context: Dict[str, Any], base_damage: int = 0) -> Tuple[int, int]:
        """
        Check if Paladin wants to use Divine Smite after hitting.

        Args:
            is_critical: Whether the attack was a critical hit
            target_monster: The target monster
            context: Attack context
            base_damage: The base damage that will be dealt without smite

        Returns:
            Tuple of (smite_damage_dice_count, spell_slot_level_used)
        """
        import random

        # Get available spell slots
        character_id = self.character_context.get('id')
        if not character_id:
            print("[DEBUG] Divine Smite: No character ID in context")
            return 0, 0

        print(f"[DEBUG] Divine Smite: Checking for character {character_id}")

        # Get spell slots from spellcasting service
        try:
            from services.spellcasting_service import get_spellcasting_service
            spellcasting_service = get_spellcasting_service("talekeeper.db")

            # Get all available spell slots
            all_slots = spellcasting_service.get_character_spell_slots(character_id)
            available_slots = {}
            for slot in all_slots:
                if slot.available_slots > 0 and slot.level <= 5:  # Paladins can use up to 5th level for smite
                    available_slots[slot.level] = slot.available_slots

            if not available_slots:
                print(f"[DEBUG] Divine Smite: No available spell slots. All slots: {[(s.level, s.max_slots, s.used_slots, s.available_slots) for s in all_slots]}")
                return 0, 0  # No spell slots available

            print(f"[DEBUG] Divine Smite: Available slots: {available_slots}")

            # Prepare target info
            if target_monster:
                if hasattr(target_monster, 'monster_name'):  # EncounterInstance object
                    target_info = {
                        'name': target_monster.monster_name,
                        'type': target_monster.monster_type,
                        'current_hp': target_monster.current_hit_points,
                        'base_damage': base_damage,
                    }
                elif isinstance(target_monster, dict):
                    target_info = {
                        'name': target_monster.get('name', 'Monster'),
                        'type': target_monster.get('type', 'Unknown'),
                        'current_hp': target_monster.get('current_hp', 0),
                        'base_damage': base_damage,
                    }
                else:
                    target_info = {
                        'name': 'Monster',
                        'type': 'Unknown',
                        'current_hp': 0,
                        'base_damage': base_damage,
                    }
            else:
                target_info = {
                    'name': 'Monster',
                    'type': 'Unknown',
                    'current_hp': 0,
                    'base_damage': base_damage,
                }

            # Show the Divine Smite dialog
            from PyQt6.QtCore import QEventLoop
            dialog = DivineSmiteDialog(
                parent=self,
                is_critical=is_critical,
                available_spell_slots=available_slots,
                target_info=target_info
            )

            smite_dice = 0
            slot_level_used = 0

            # Connect signals to capture the result
            def on_smite_chosen(spell_slot_level: int, is_undead_or_fiend: bool):
                nonlocal smite_dice, slot_level_used

                # Calculate smite damage dice
                # Base: 2d8 + 1d8 per spell level above 1st
                smite_dice = 2 + (spell_slot_level - 1)

                # +1d8 vs undead/fiends
                if is_undead_or_fiend:
                    smite_dice += 1

                # Cap at 5d8
                smite_dice = min(smite_dice, 5)

                # Double dice on critical (for display purposes - actual doubling happens in damage roll)
                # We'll handle the critical doubling in the damage rolling section

                slot_level_used = spell_slot_level

                # Consume the spell slot by updating the database directly
                import sqlite3
                with sqlite3.connect('talekeeper.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE character_spell_slots
                        SET used_slots = used_slots + 1
                        WHERE character_id = ? AND spell_level = ? AND used_slots < max_slots
                    """, (character_id, spell_slot_level))
                    conn.commit()

                # Log the smite
                self._log_to_parent(f"[DIVINE SMITE] Using level {spell_slot_level} spell slot for {smite_dice}d8 radiant damage!")

            dialog.smite_chosen.connect(on_smite_chosen)

            # Show dialog and wait for result
            dialog.exec()

            return smite_dice, slot_level_used

        except Exception as e:
            print(f"Error checking Divine Smite: {e}")
            return 0, 0

    def _get_sneak_attack_damage(self) -> str:
        """Get sneak attack damage based on rogue level."""
        if not self._has_class_feature('Sneak Attack'):
            return '0'
        
        # Simple implementation - assume 1d6 per 2 rogue levels
        total_level = self.character_context.get('level', 1)
        sneak_dice = max(1, total_level // 2)  # Simplified calculation
        return f'{sneak_dice}d6'
    
    def _can_sneak_attack(self, context: Dict[str, Any]) -> bool:
        """Check if sneak attack can be applied."""
        if not self._has_class_feature('Sneak Attack'):
            return False

        weapon_props = self._get_context_weapon_properties(context)
        weapon_props_lower = [prop.lower() for prop in weapon_props] if weapon_props else []

        # Must use finesse or ranged weapon
        is_finesse = 'finesse' in weapon_props_lower
        damage_type = context.get('damage_type', '')
        is_ranged = 'ranged' in weapon_props_lower or damage_type == 'ranged'

        if not (is_finesse or is_ranged):
            return False

        # Check for sneak attack conditions
        # 1. Has advantage on the attack (from any source including Vex, Luck, etc.)
        has_advantage = context.get('has_advantage', False)

        # Check if advantage was calculated from various sources
        advantage_state = context.get('advantage_state')
        if advantage_state == 'advantage' or (hasattr(advantage_state, 'value') and advantage_state.value == 'advantage'):
            has_advantage = True

        # Solo game - sneak attack triggers if player has advantage (simplified)
        can_sneak = has_advantage

        # Check if already used this turn (once per turn limit)
        if can_sneak and hasattr(self, 'sneak_attack_used_this_turn'):
            if self.sneak_attack_used_this_turn:
                return False

        print(f"DEBUG SNEAK: Advantage: {has_advantage}, Can sneak: {can_sneak}")
        return can_sneak
    
    def _apply_sneak_attack(self, context: Dict[str, Any], damage_breakdown: dict) -> dict:
        """Apply sneak attack damage if conditions are met."""
        print(f"[DEBUG SNEAK APPLY] _apply_sneak_attack called")
        if not self._can_sneak_attack(context):
            print(f"[DEBUG SNEAK APPLY] Sneak attack conditions not met, returning original breakdown")
            return damage_breakdown

        print(f"[DEBUG SNEAK APPLY] Sneak attack conditions MET! Applying damage...")

        import random
        sneak_damage_dice = self._get_sneak_attack_damage()

        if 'd' in sneak_damage_dice:
            try:
                num_dice, die_size = sneak_damage_dice.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)

                # Check for active cunning strike effects and reduce dice accordingly
                cunning_strike_dice_cost = self._calculate_cunning_strike_cost()
                effective_sneak_dice = max(0, num_dice - cunning_strike_dice_cost)

                # Apply cunning strike effects if any are active
                if cunning_strike_dice_cost > 0:
                    self._apply_cunning_strike_effects(damage_breakdown, cunning_strike_dice_cost)

                # Roll remaining sneak attack dice
                if effective_sneak_dice > 0:
                    sneak_rolls = [random.randint(1, die_size) for _ in range(effective_sneak_dice)]
                    sneak_total = sum(sneak_rolls)

                    # Add to damage breakdown
                    damage_breakdown['sneak_attack_rolls'] = sneak_rolls
                    damage_breakdown['sneak_attack_damage'] = sneak_total
                    damage_breakdown['total'] += sneak_total

                    print(f"[SNEAK] Applied {effective_sneak_dice}d{die_size} = {sneak_total} damage! New total: {damage_breakdown['total']}")

                    # Check for Assassin Surprising Strikes bonus damage (first round)
                    assassin_bonus = self._apply_assassin_surprising_strikes(context)
                    if assassin_bonus > 0:
                        damage_breakdown['assassin_surprising_strikes'] = assassin_bonus
                        damage_breakdown['total'] += assassin_bonus

                    # Check for Death Strike (level 17 Assassin, first round)
                    death_strike_applied = self._apply_death_strike(context, damage_breakdown)
                    if death_strike_applied:
                        damage_breakdown['death_strike_applied'] = True

                else:
                    # All dice used for cunning strike effects
                    damage_breakdown['sneak_attack_rolls'] = []
                    damage_breakdown['sneak_attack_damage'] = 0
                    damage_breakdown['sneak_attack_note'] = f"All {num_dice}d6 used for Cunning Strike effects"

                # Mark sneak attack as used this turn
                if not hasattr(self, 'sneak_attack_used_this_turn'):
                    self.sneak_attack_used_this_turn = False
                self.sneak_attack_used_this_turn = True

            except (ValueError, IndexError):
                pass

        return damage_breakdown

    def _calculate_cunning_strike_cost(self) -> int:
        """Calculate total dice cost for active cunning strike effects."""
        total_cost = 0

        # Cost mapping for cunning strike effects
        costs = {
            'poison': 1, 'trip': 1, 'withdraw': 1,
            'daze': 2, 'knock_out': 6, 'obscure': 3
        }

        # Check which effects are active in character context
        for effect_name, dice_cost in costs.items():
            if self.character_context.get(f'cunning_strike_{effect_name}_active', False):
                total_cost += dice_cost

        return total_cost

    def _apply_cunning_strike_effects(self, damage_breakdown: dict, dice_cost: int) -> None:
        """Apply cunning strike effects and log them."""
        effects_applied = []

        # Check which effects are active and apply them
        effect_descriptions = {
            'poison': 'Poison (Con save)',
            'trip': 'Trip - Prone (Dex save)',
            'withdraw': 'Withdraw - Move half speed without opportunity attacks',
            'daze': 'Daze - Limited actions next turn (Con save)',
            'knock_out': 'Knock Out - Unconscious (Con save)',
            'obscure': 'Obscure - Blinded next turn (Dex save)'
        }

        for effect_name, description in effect_descriptions.items():
            if self.character_context.get(f'cunning_strike_{effect_name}_active', False):
                effects_applied.append(description)

                # Check for Assassin Envenom Weapons enhancement (level 13+)
                if effect_name == 'poison' and self._is_assassin() and self.character_context.get('level', 1) >= 13:
                    import random
                    envenom_damage = random.randint(1, 6) + random.randint(1, 6)  # 2d6
                    damage_breakdown['envenom_weapons_damage'] = envenom_damage
                    damage_breakdown['total'] += envenom_damage

                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"⚔️ Envenom Weapons: +{envenom_damage} poison damage (ignores resistance)")
                            break
                        parent = parent.parent()

                # Clear the effect after use
                self.character_context[f'cunning_strike_{effect_name}_active'] = False

        if effects_applied:
            damage_breakdown['cunning_strike_effects'] = effects_applied
            damage_breakdown['cunning_strike_dice_cost'] = dice_cost

            # Log the effects
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    for effect in effects_applied:
                        parent.log_panel.log_combat(f"⚔️ Cunning Strike: {effect}")
                    break
                parent = parent.parent()

    def _has_rage_uses(self) -> bool:
        """Check if character has rage uses remaining."""
        if not self.character_context:
            return False

        if self.character_context.get('class_id', '').lower() != 'barbarian':
            return False

        character_id = self._resolve_character_id()
        if not character_id:
            return self._has_class_feature('Rage')

        try:
            resource = self._get_resource_service().get_resource(character_id, 'Rage')
        except Exception as exc:
            print(f"[RAGE] Unable to check rage uses: {exc}")
            return self._has_class_feature('Rage')

        if resource is None:
            return self._has_class_feature('Rage')

        return resource.current_uses > 0

    def _use_rage(self):
        """Activate barbarian rage."""
        # Use the unified resource system
        resource_service = self._get_resource_service()
        
        # Get character ID
        character_id = self._resolve_character_id()
        if not character_id:
            print("DEBUG: No character ID for Rage")
            return
        
        # Check if resource is available
        rage_resource = resource_service.get_resource(character_id, 'Rage')
        if not rage_resource or rage_resource.current_uses <= 0:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("[FAIL] No Rage uses remaining (requires Long Rest)")
                    break
                parent = parent.parent()
            return
        
        # Use Rage resource
        use_result = resource_service.use_resource(character_id, 'Rage')
        if not use_result.get('success', False):
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[FAIL] {use_result.get('error', 'Rage failed')}")
                    break
                parent = parent.parent()
            return
        
        remaining_uses = use_result.get('current_uses', 0)
        if remaining_uses <= 0 and ActionType.RAGE in self.action_cards:
            card = self.action_cards.pop(ActionType.RAGE)
            try:
                card.setParent(None)
                card.deleteLater()
            except Exception:
                pass
            self._update_visible_cards()

        level = self.character_context.get('level', 1) if isinstance(self.character_context, dict) else 1
        rage_damage = 4 if level >= 16 else (3 if level >= 9 else 2)

        # Track rage state
        if isinstance(self.character_context, dict):
            self.character_context['raging'] = True
            self.character_context['rage_damage_bonus'] = rage_damage
            self.character_context['rage_turns_remaining'] = 10  # Rage lasts 10 rounds

        # Trigger automatic subclass features when rage starts
        try:
            from services.subclass_action_integration import subclass_action_integration
            automatic_triggers = subclass_action_integration.trigger_automatic_feature(character_id, "rage_start")

            # Log any automatic feature activations
            for trigger_result in automatic_triggers:
                if trigger_result.get('success'):
                    feature_name = trigger_result.get('feature_name', 'Unknown Feature')
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"[AUTO] {feature_name} activated by Rage!")
                            break
                        parent = parent.parent()
        except Exception as e:
            print(f"Error triggering automatic subclass features: {e}")

        # Refresh weapon cards to show rage damage bonus
        self._create_weapon_cards()
        self._update_visible_cards()
        
        # Apply rage effects 
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    # Calculate rage damage bonus based on level
                    level = self.character_context.get('level', 1)
                    rage_damage = 4 if level >= 16 else (3 if level >= 9 else 2)
                    
                    parent.log_panel.log_combat(f"[RAGE] RAGE activated! +{rage_damage} damage, resistance to physical damage, advantage on STR checks/saves")
                    parent.log_panel.log_combat(f"Rage uses remaining: {use_result['current_uses']}/{use_result['max_uses']}")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error logging rage activation: {e}")
    
    def _toggle_reckless_attack(self):
        """Toggle Reckless Attack state for barbarian."""
        # Check if character is a barbarian with Reckless Attack
        if not (self.character_context.get('class_id', '').lower() == 'barbarian' and 
                self._has_class_feature('Reckless Attack')):
            return
        
        # Toggle the state
        current_state = self.character_context.get('reckless_attack_active', False)
        new_state = not current_state
        self.character_context['reckless_attack_active'] = new_state
        
        # Update the card appearance and text
        if ActionType.RECKLESS_ATTACK in self.action_cards:
            card = self.action_cards[ActionType.RECKLESS_ATTACK]
            if new_state:
                card.name_label.setText("RECKLESS ACTIVE")
                card.setProperty("reckless_active", True)
                card.setStyleSheet("QWidget[reckless_active=\"true\"] { background-color: #8B0000; border: 2px solid #FF4444; }")
            else:
                card.name_label.setText("Reckless Attack")
                card.setProperty("reckless_active", False)
                card.setStyleSheet("")
        
        # Log the state change
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    if new_state:
                        parent.log_panel.log_combat("[RECKLESS] Reckless Attack activated! You have advantage on STR attacks, but enemies have advantage against you.")
                    else:
                        parent.log_panel.log_combat("[RECKLESS] Reckless Attack deactivated.")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error logging reckless attack toggle: {e}")
        
        # Refresh attack cards to show advantage state
        self._create_weapon_cards()
        self._update_visible_cards()
    
    def _has_lay_on_hands_uses(self) -> bool:
        """Check if paladin has Lay on Hands uses remaining."""
        if not self._has_class_feature('Lay on Hands'):
            return False

        # Check actual healing pool from paladin service
        try:
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')
            paladin_info = paladin_service.get_paladin_info(character_id)

            if paladin_info and 'paladin_features' in paladin_info:
                current_pool = paladin_info['paladin_features'].get('lay_on_hands_pool_current', 0)
                return current_pool > 0

            # Fallback - assume paladin has pool if they have the feature
            return True
        except Exception:
            return self._has_class_feature('Lay on Hands')

    def _use_lay_on_hands(self):
        """Use paladin Lay on Hands healing with proper dialog."""
        if not self._has_lay_on_hands_uses():
            return

        try:
            # Get paladin service and character info
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')
            character_level = self.character_context.get('level', 1)
            character_name = self.character_context.get('name', 'Character')
            current_hp = self.character_context.get('hit_points_current', 0)
            max_hp = self.character_context.get('hit_points_max', 0)

            # Get healing pool info
            paladin_info = paladin_service.get_paladin_info(character_id)
            if paladin_info and 'paladin_features' in paladin_info:
                current_pool = paladin_info['paladin_features'].get('lay_on_hands_pool_current', character_level * 5)
                max_pool = paladin_info['paladin_features'].get('lay_on_hands_pool_max', character_level * 5)
            else:
                # Fallback calculation
                current_pool = character_level * 5
                max_pool = character_level * 5

            # Create target options (for now, just self-healing)
            target_options = [(character_id, character_name, current_hp, max_hp)]

            # Show Lay on Hands dialog
            dialog = LayOnHandsDialog(
                parent=self,
                character_data=self.character_context,
                current_pool=current_pool,
                max_pool=max_pool,
                target_options=target_options
            )

            # Connect dialog signals
            dialog.healing_applied.connect(self._apply_lay_on_hands_healing)
            dialog.healing_cancelled.connect(lambda: print("Lay on Hands cancelled"))

            # Show dialog
            dialog.exec()

        except Exception as e:
            print(f"Error using Lay on Hands: {e}")
            # Fallback to simple healing
            self._apply_healing_to_player(5)

    def _apply_lay_on_hands_healing(self, healing_points: int, cure_poison: bool, target_id: str):
        """Apply Lay on Hands healing and update resources."""
        try:
            # Use paladin service to track resource usage
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')

            # Use the healing
            result = paladin_service.use_lay_on_hands(character_id, healing_points)

            if result.get('success'):
                # Apply healing to character
                if cure_poison:
                    # Handle poison curing (for now, just log it)
                    healing_done = 0
                    message = f"✋ Lay on Hands: Cured poison ({healing_points} points used)"
                else:
                    # Apply actual healing
                    old_hp = self.character_context.get('hit_points_current', 0)
                    healing_done = self._apply_healing_to_player(healing_points)
                    actual_healing = min(healing_done, healing_points)
                    message = f"✋ Lay on Hands: Healed {actual_healing} HP ({healing_points} points used)"

                # Update character context with new pool values
                if hasattr(self, 'character_context'):
                    # This would need to be updated by the main window, but log for now
                    remaining_pool = result.get('pool_remaining', 0)
                    print(f"Lay on Hands pool remaining: {remaining_pool}")

                # Log the healing
                try:
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(message)
                            break
                        parent = parent.parent()
                except Exception as e:
                    print(f"Error logging lay on hands: {e}")

            else:
                print(f"Lay on Hands failed: {result.get('reason', 'Unknown error')}")

        except Exception as e:
            print(f"Error applying Lay on Hands healing: {e}")

    def _use_channel_divinity(self):
        """Use Channel Divinity with proper dialog."""
        if not self._has_channel_divinity_uses():
            return

        try:
            # Get paladin service and character info
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')
            character_level = self.character_context.get('level', 1)
            sacred_oath = self.character_context.get('subclass_id', 'devotion')

            # Get Channel Divinity uses info
            paladin_info = paladin_service.get_paladin_info(character_id)
            if paladin_info and 'paladin_features' in paladin_info:
                current_uses = paladin_info['paladin_features'].get('channel_divinity_uses_current', 0)
                max_uses = paladin_info['paladin_features'].get('channel_divinity_uses_max', 2)
            else:
                # Fallback calculation
                current_uses = 0
                max_uses = 3 if character_level >= 11 else 2

            # Get available options
            available_options = create_channel_divinity_options(character_level, sacred_oath)

            # Show Channel Divinity dialog
            dialog = ChannelDivinityDialog(
                parent=self,
                character_data=self.character_context,
                current_uses=current_uses,
                max_uses=max_uses,
                available_options=available_options
            )

            # Connect dialog signals
            dialog.channel_divinity_used.connect(self._apply_channel_divinity_effect)
            dialog.channel_divinity_cancelled.connect(lambda: print("Channel Divinity cancelled"))

            # Show dialog
            dialog.exec()

        except Exception as e:
            print(f"Error using Channel Divinity: {e}")

    def _has_channel_divinity_uses(self) -> bool:
        """Check if paladin has Channel Divinity uses remaining."""
        if not self._has_class_feature('Channel Divinity'):
            return False

        # Check actual uses from paladin service
        try:
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')
            paladin_info = paladin_service.get_paladin_info(character_id)

            if paladin_info and 'paladin_features' in paladin_info:
                current_uses = paladin_info['paladin_features'].get('channel_divinity_uses_current', 0)
                max_uses = paladin_info['paladin_features'].get('channel_divinity_uses_max', 2)
                return current_uses < max_uses

            # Fallback - assume paladin has uses if they have the feature
            return True
        except Exception:
            return self._has_class_feature('Channel Divinity')

    def _apply_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any]):
        """Apply Channel Divinity effect and update resources."""
        try:
            # Use paladin service to track resource usage
            paladin_service = PaladinAbilitiesService()
            character_id = self.character_context.get('id', '')

            # Use Channel Divinity
            result = paladin_service.use_channel_divinity(character_id, option_name)

            if result.get('success'):
                # Apply the specific effect based on option
                self._execute_channel_divinity_effect(option_name, option_data)

                # Log the usage
                try:
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'log_panel'):
                            parent.log_panel.log_combat(f"⚡ Channel Divinity: {option_name}")
                            break
                        parent = parent.parent()
                except Exception as e:
                    print(f"Error logging Channel Divinity: {e}")

            else:
                print(f"Channel Divinity failed: {result.get('reason', 'Unknown error')}")

        except Exception as e:
            print(f"Error applying Channel Divinity: {e}")

    def _execute_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any]):
        """Execute the specific Channel Divinity effect."""
        try:
            if option_name == "Divine Sense":
                # For now, just log the effect - full implementation would track detection
                print(f"Divine Sense activated - detecting celestials, fiends, and undead for 10 minutes")

            elif option_name == "Sacred Weapon":
                # For now, just log the effect - full implementation would apply weapon bonus
                print(f"Sacred Weapon activated - weapon gains Charisma bonus and light for 10 minutes")

            elif option_name == "Turn the Unholy":
                # For now, just log the effect - full implementation would affect nearby enemies
                print(f"Turn the Unholy activated - fiends and undead within 30 feet must save or be turned")

            elif option_name == "Abjure Foes":
                # For now, just log the effect - full implementation would affect multiple enemies
                print(f"Abjure Foes activated - multiple enemies may be frightened")

            else:
                # Generic effect for other oath abilities
                print(f"Channel Divinity effect: {option_name}")

            # For now, most effects are placeholder logging
            # Full implementation would require combat state management and enemy targeting

        except Exception as e:
            print(f"Error executing Channel Divinity effect: {e}")

    def _monsters_present(self) -> bool:
        """Check if any monsters are currently present/alive."""
        try:
            # Find encounter panel to check for active monsters
            parent = self.parent()
            while parent:
                if hasattr(parent, 'encounter_panel'):
                    encounter_panel = parent.encounter_panel
                    # Check if there are alive monsters in the encounter panel
                    if hasattr(encounter_panel, 'monsters') and encounter_panel.monsters:
                        # Check if any monster is alive (HP > 0)
                        for monster in encounter_panel.monsters:
                            if hasattr(monster, 'current_hit_points') and monster.current_hit_points > 0:
                                return True
                        return False
                    # Check if encounter is active in other ways
                    if hasattr(encounter_panel, 'current_encounter') and encounter_panel.current_encounter:
                        return True
                    return False
                parent = parent.parent()
            return False
        except Exception as e:
            print(f"Error checking monsters present: {e}")
            return False  # Default to allowing rest if check fails

    def _handle_rest_action(self, context: Dict[str, Any]):
        """Handle rest action - prompt for short or long rest."""
        try:
            # Check if monsters are present - cannot rest during combat
            if self._monsters_present():
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("❌ Cannot rest while monsters are present!")
                        break
                    parent = parent.parent()
                return
            # Create a simple dialog to choose rest type
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
            
            dialog = QDialog(self)
            has_weapon_mastery = self._character_has_weapon_mastery_feature()
            dialog.setWindowTitle("Take a Rest")
            dialog.setModal(True)
            dialog.resize(400, 200)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Choose rest type:")
            title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)
            
            # Description
            desc = QLabel("Short Rest: Recover some abilities and HP\nLong Rest: Recover all abilities, spell slots, and HP")
            desc.setStyleSheet("color: #cccccc; margin-bottom: 15px;")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            
            # Buttons
            button_layout = QHBoxLayout()

            short_tooltip = "Recover short-rest abilities and healing."
            long_tooltip = "Recover all abilities, spell slots, and HP."
            
            short_rest_btn = QPushButton("Short Rest (1 hour)")
            short_rest_btn.clicked.connect(lambda: self._take_short_rest(dialog))
            short_rest_btn.setToolTip(short_tooltip)
            short_rest_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a7c59;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a8c69;
                }
            """)
            button_layout.addWidget(short_rest_btn)
            
            long_rest_btn = QPushButton("Long Rest (8 hours)")
            long_rest_btn.clicked.connect(lambda: self._take_long_rest(dialog))
            long_rest_btn.setToolTip(long_tooltip)
            long_rest_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5c4a7c;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #6c5a8c;
                }
            """)
            button_layout.addWidget(long_rest_btn)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
            """)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            dialog.exec()
            
        except Exception as e:
            print(f"Error handling rest action: {e}")
    
    def _take_short_rest(self, dialog):
        """Execute short rest."""
        try:
            dialog.accept()
            
            # Log start of rest
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("😴 Taking a Short Rest (1 hour)...")
                    break
                parent = parent.parent()
            
            # Save XP to database
            self._save_character_xp()
            
            # Restore short rest abilities
            self._restore_short_rest_abilities()
            
            # Allow hit die recovery (simplified - just heal some HP)
            self._short_rest_healing()

            # Enable attunement after short rest
            parent = self.parent()
            while parent:
                if hasattr(parent, 'equipment_panel'):
                    print("[ACTION PANEL] Calling enable_attunement on equipment panel")
                    parent.equipment_panel.enable_attunement()
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("✨ Short Rest completed! Some abilities and HP restored. Attunement now available.")
                    break
                parent = parent.parent()


        except Exception as e:
            print(f"Error during short rest: {e}")
    
    def _take_long_rest(self, dialog):
        """Execute long rest."""
        try:
            dialog.accept()
            
            # Log start of rest
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("😴 Taking a Long Rest (8 hours)...")
                    break
                parent = parent.parent()
            
            # Save XP to database
            self._save_character_xp()
            
            # Restore all abilities
            self._restore_all_abilities()
            
            # Full healing
            self._long_rest_healing()

            # Enable attunement after long rest
            parent = self.parent()
            while parent:
                if hasattr(parent, 'equipment_panel'):
                    print("[ACTION PANEL] Calling enable_attunement on equipment panel (long rest)")
                    parent.equipment_panel.enable_attunement()
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("✨ Long Rest completed! All abilities, spell slots, and HP fully restored. Attunement available.")
                    break
                parent = parent.parent()


        except Exception as e:
            print(f"Error during long rest: {e}")
    

    def _save_character_xp(self):
        """Save character XP to database."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine'):
                    game_engine = parent.game_engine
                    character = game_engine.current_character
                    if character:
                        success = game_engine.save_character_sync()
                        if success:
                            parent.log_panel.log_combat("💾 Character progress saved to database")
                        else:
                            parent.log_panel.log_combat("❌ Failed to save character progress")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error saving character XP: {e}")
    
    def _restore_short_rest_abilities(self):
        """Restore abilities that recharge on short rest."""
        try:
            # Use the character resource service to restore short rest resources
            resource_service = self._get_resource_service()
            
            character_id = self._resolve_character_id()
            if not character_id:
                print("DEBUG: No character ID for short rest restoration")
                return
            
            # Restore all short rest resources
            result = resource_service.restore_resources_by_rest_type(character_id, 'short_rest')

            # Also use feature integration system for class features
            from core.feature_integration import get_feature_integration
            feature_integration = get_feature_integration()
            feature_result = feature_integration.process_rest(character_id, 'short')
            
            # Log short rest resource restoration
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    print(f"[DEBUG] Short rest result: {result}")
                    print(f"[DEBUG] Feature result: {feature_result}")

                    if result.get('success'):
                        restored = result.get('restored_resources', [])
                        restored_count = 0
                        print(f"[DEBUG] Resources to restore: {restored}")

                        for resource in restored:
                            if resource['gained'] > 0:
                                parent.log_panel.log_combat(f"✨ {resource['resource_name']} restored ({resource['new_uses']}/{resource.get('max_uses', resource['new_uses'])} uses)")
                                restored_count += 1

                        if restored_count == 0:
                            parent.log_panel.log_combat("💤 Short rest completed (no resources to restore)")
                    else:
                        parent.log_panel.log_combat(f"❌ Failed to restore short rest resources: {result.get('error', 'Unknown error')}")
                    break
                parent = parent.parent()
                    
        except Exception as e:
            print(f"Error restoring short rest abilities: {e}")
    
    def _restore_all_abilities(self):
        """Restore all abilities (long rest)."""
        try:
            # Use the character resource service to restore all resources
            resource_service = self._get_resource_service()
            
            character_id = self._resolve_character_id()
            if not character_id:
                print("DEBUG: No character ID for long rest restoration")
                return
            
            # Restore short rest resources first
            short_result = resource_service.restore_resources_by_rest_type(character_id, 'short_rest')

            # Then restore long rest resources
            long_result = resource_service.restore_resources_by_rest_type(character_id, 'long_rest')

            # Also use feature integration system for class features
            from core.feature_integration import get_feature_integration
            feature_integration = get_feature_integration()
            feature_result = feature_integration.process_rest(character_id, 'long')
            
            # Log restored resources
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    print(f"[DEBUG] Long rest short_result: {short_result}")
                    print(f"[DEBUG] Long rest long_result: {long_result}")
                    print(f"[DEBUG] Long rest feature_result: {feature_result}")

                    total_restored = 0

                    # Log short rest resources
                    if short_result.get('success'):
                        for resource in short_result.get('restored_resources', []):
                            if resource['gained'] > 0:
                                parent.log_panel.log_combat(f"✨ {resource['resource_name']} restored ({resource['new_uses']}/{resource.get('max_uses', resource['new_uses'])} uses)")
                                total_restored += 1

                    # Log long rest resources
                    if long_result.get('success'):
                        for resource in long_result.get('restored_resources', []):
                            if resource['gained'] > 0:
                                parent.log_panel.log_combat(f"✨ {resource['resource_name']} restored ({resource['new_uses']}/{resource.get('max_uses', resource['new_uses'])} uses)")
                                total_restored += 1

                    if total_restored == 0:
                        parent.log_panel.log_combat("🌙 Long rest completed (no resources to restore)")
                    break
                parent = parent.parent()
            
            # TODO: Implement spell slot restoration when spellcasting is added
            
        except Exception as e:
            print(f"Error restoring all abilities: {e}")
    
    def _short_rest_healing(self):
        """Allow hit die healing during short rest."""
        try:
            # Simplified hit die healing - just heal some HP
            current_hp = self.character_context.get('hit_points_current', 0)
            max_hp = self.character_context.get('hit_points_max', 0)
            
            if current_hp < max_hp:
                # Get character's actual hit die based on class
                hit_die_size = self._get_character_hit_die()
                import random
                constitution_mod = (self.character_context.get('constitution', 10) - 10) // 2
                hit_die_roll = random.randint(1, hit_die_size)
                healing = hit_die_roll + constitution_mod
                healing = max(1, healing)  # Minimum 1 HP
                
                new_hp = self._apply_healing_to_player(healing)
                
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"🎲 Hit Die: 1d{hit_die_size}+{constitution_mod} = {hit_die_roll}+{constitution_mod} = {healing} HP healed")
                        break
                    parent = parent.parent()
                    
        except Exception as e:
            print(f"Error during short rest healing: {e}")
    
    def _get_character_hit_die(self) -> int:
        """Get the character's hit die size based on their class."""
        # Hit die mapping for D&D 2024 classes
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
        
        # Try to get class_id from character context
        class_id = self.character_context.get('class_id', '')
        
        # If not found, try to get it from main window
        if not class_id:
            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'current_character'):
                        class_id = parent.current_character.get('class_id', '')
                        break
                    parent = parent.parent()
            except:
                pass
        
        # Get hit die size, default to d8 if class not found
        return hit_die_map.get(class_id, hit_die_map.get(class_id.lower(), 8))
    
    def _long_rest_healing(self):
        """Full healing during long rest."""
        try:
            max_hp = self.character_context.get('hit_points_max', 0)
            old_hp = self.character_context.get('hit_points_current', 0)
            
            if old_hp < max_hp:
                self._apply_healing_to_player(max_hp - old_hp)  # Heal to full
                
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"💚 Fully healed to {max_hp} HP")
                        break
                    parent = parent.parent()
                    
        except Exception as e:
            print(f"Error during long rest healing: {e}")
    
    def _get_spell_slots(self, level: int) -> int:
        """Get available spell slots of given level."""
        # Simple implementation - would need to track spell slots properly
        return 1 if self._has_class_feature('Spellcasting') or self._has_class_feature('Pact Magic') else 0
    
    def _is_player_turn_d20(self) -> bool:
        """Check if it's the player's turn using D&D 2024 rules."""
        try:
            # Get encounter panel to check combat state
            encounter_panel = self._get_encounter_panel()
            if not encounter_panel:
                return True  # No encounter, player can act
                
            # Check if there's an active encounter
            current_encounter = getattr(encounter_panel, 'current_encounter', None)
            if not current_encounter:
                return True  # No active encounter, player can act
                
            # If combat hasn't started yet, player can start it
            if not getattr(current_encounter, 'combat_started', False):
                return True
                
            # Check the initiative order and whose turn it is
            initiative_order = getattr(current_encounter, 'initiative_order', [])
            current_turn_index = getattr(current_encounter, 'current_turn_index', 0)
            
            if not initiative_order or current_turn_index >= len(initiative_order):
                return True  # No initiative order or invalid index, allow action
                
            # Get current actor
            current_actor = initiative_order[current_turn_index]
            
            # If it's the player's turn, allow action
            return current_actor.get('type') == 'player'
            
        except Exception as e:
            print(f"Error checking player turn: {e}")
            return True  # Default to allowing action if there's an error
    
    def _log_to_combat_panel(self, message: str):
        """Log message to combat panel."""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(message)
                break
            parent = parent.parent()
    
    def _can_dual_wield(self) -> bool:
        """Check if character can dual wield with current equipment."""
        main_hand = self.equipped_weapons.get('main_hand')
        off_hand = self.equipped_weapons.get('off_hand')
        
        if not main_hand or not off_hand:
            return False
        if main_hand.get('item_type') != 'weapon' or off_hand.get('item_type') != 'weapon':
            return False
        
        feats = getattr(self, 'character_feats', [])
        main_props = [p.lower() for p in (main_hand.get('weapon_properties') or [])]
        off_props = [p.lower() for p in (off_hand.get('weapon_properties') or [])]
        
        # With Dual Wielder feat, any one-handed melee weapons work
        if "Dual Wielder" in feats:
            return True
        
        # Without the feat, both weapons must be Light
        return 'light' in main_props and 'light' in off_props
    
    def _execute_two_weapon_attack(self, context: Dict[str, Any], encounter_panel):
        """Execute both main-hand and off-hand attacks if dual wielding."""
        # Execute main-hand attack
        self._execute_single_attack(ActionType.ATTACK_MAIN_HAND, context, encounter_panel)
        
        # Check if we can make an off-hand attack
        if self._can_dual_wield():
            off_hand_context = self._build_off_hand_context(context)
            if off_hand_context:
                # Log off-hand attack
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat("[TWF] Making off-hand attack...")
                        break
                    parent = parent.parent()
                
                self._execute_single_attack(ActionType.ATTACK_OFF_HAND, off_hand_context, encounter_panel)
    
    def _build_off_hand_context(self, base_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build context for off-hand attack."""
        off_hand = self.equipped_weapons.get('off_hand')
        if not off_hand:
            return None
        
        # Copy base context and override with off-hand weapon data
        off_context = {**base_context}
        off_context.update(off_hand)
        off_context['action_type'] = ActionType.ATTACK_OFF_HAND
        off_context['is_off_hand'] = True
        
        return off_context
    
    def _get_two_weapon_fighting_damage_bonus(self, context: Dict[str, Any]) -> int:
        """Get damage bonus from Two-Weapon Fighting style for off-hand attacks."""
        if context.get('action_type') != ActionType.ATTACK_OFF_HAND:
            return 0
        
        feats = getattr(self, 'character_feats', [])
        if "Two-Weapon Fighting" not in feats:
            return 0
        
        # Add ability modifier to off-hand damage
        weapon_props = self._get_context_weapon_properties(context)
        if 'finesse' in [p.lower() for p in weapon_props]:
            str_mod = (self.character_context.get('strength', 10) - 10) // 2
            dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
            return max(str_mod, dex_mod)
        else:
            return (self.character_context.get('strength', 10) - 10) // 2


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
        
        # Advantage resource system
        self.advantage_halo = AdvantageHalo(self)
        self.advantage_halo.hide()
        self.advantage_halo.resource_used.connect(self._on_advantage_resource_used)
        self.resource_manager = None  # Set by parent panel
        
        # Enable mouse tracking for hover events
        self.setMouseTracking(True)
        
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
            # Light theme colors tuned to palette
            card_bg = "#f4e5d4"        # surface color from light theme
            card_border = "#a45f38"    # button color from light theme
            card_border_hover = "#3f7663"  # accent_tertiary from light theme
            icon_bg = "#f8ecdf"        # background highlight
            name_color = "#000000"     # Black text for maximum readability
            desc_color = "#000000"     # Black text for maximum readability
            button_bg = "#a45f38"      # button color from light theme
            button_hover = "#bb7346"   # button_hover from light theme
            button_pressed = "#7c4f32" # accent_primary from light theme
            button_text = "#ffffff"    # White text on colored buttons
            button_disabled_bg = "#ddc3a7"  # Lighter surface color
            button_disabled_text = "#83644b"  # Darker secondary text
            cooldown_border = "#a45f38"
            cooldown_bg = "#fff9f1"
            cooldown_chunk = "#cf8a5b"  # accent_quaternary from light theme
        else:
            # Dark theme colors tuned to palette
            card_bg = "#2d2116"
            card_border = "#4c3a2a"
            card_border_hover = "#3d6d5a"
            icon_bg = "#1f150d"
            name_color = "#f2e6cf"
            desc_color = "#d6c6ac"
            button_bg = "#3d6d5a"
            button_hover = "#4f846d"
            button_pressed = "#2c5242"
            button_text = "#f2e6cf"
            button_disabled_bg = "#3b2b1f"
            button_disabled_text = "#8c7b63"
            cooldown_border = "#5b4633"
            cooldown_bg = "#1f150d"
            cooldown_chunk = "#8a6748"
        
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

            # Add spell data to context if this is a spell action card
            if hasattr(self, 'spell_data') and self.spell_data:
                context['spell_data'] = self.spell_data

            # Add spell slot data to context if this is a spell slot card
            if hasattr(self, 'spell_slot_data') and self.spell_slot_data:
                context['spell_slot_data'] = self.spell_slot_data

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
    
    def set_description(self, description: str):
        """Update the description text."""
        self.description = description
        self.desc_label.setText(description)
    
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
        
        # Show advantage halo if resources available
        self._update_advantage_halo()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave."""
        # Hide advantage halo when not hovering
        if self.advantage_halo:
            self.advantage_halo.hide()
        super().leaveEvent(event)
        
    def _update_advantage_halo(self):
        """Update and position the advantage halo."""
        if not self.resource_manager:
            return
        
        # TODO: Add back action filtering after debugging
        # Currently showing on all cards to debug the advantage issue
        # if not self._is_attack_action():
        #     self.advantage_halo.hide()
        #     return
            
        if self.resource_manager.has_resources():
            counts = self.resource_manager.get_resource_counts()
            self.advantage_halo.update_resources(
                counts['lucky_current'],
                counts['lucky_max'],
                counts['inspiration_current'], 
                counts['inspiration_max']
            )
            # Position triangle in top-right corner
            halo_x = self.width() - 30  # Right edge
            halo_y = 0  # Top edge  
            self.advantage_halo.move(halo_x, halo_y)
            self.advantage_halo.raise_()  # Ensure it's on top
            self.advantage_halo.show()
        else:
            self.advantage_halo.hide()
    
    def _is_attack_action(self):
        """Check if this action card represents an attack that can benefit from advantage."""
        print(f"[DEBUG] _is_attack_action() for card: {getattr(self, 'name', 'unnamed')}, action_type: {getattr(self, 'action_type', 'none')}")
        
        # Check action type for weapon attacks
        if hasattr(self, 'action_type') and self.action_type in [
            ActionType.ATTACK_MAIN_HAND,
            ActionType.ATTACK_OFF_HAND
        ]:
            print(f"[DEBUG] Card matches attack action type: {self.action_type}")
            return True
        
        # Check card name for weapon cards (legacy system)
        if hasattr(self, 'name'):
            weapon_keywords = ['sword', 'rapier', 'dagger', 'bow', 'crossbow', 'axe', 'mace', 'spear', 'club', 'javelin']
            card_name_lower = self.name.lower()
            print(f"[DEBUG] Checking weapon keywords in '{card_name_lower}': {weapon_keywords}")
            if any(weapon in card_name_lower for weapon in weapon_keywords):
                print(f"[DEBUG] Card matches weapon keyword: {card_name_lower}")
                return True
        
        # Exclude utility actions
        if hasattr(self, 'action_type') and self.action_type in [
            ActionType.USE_ITEM,
            ActionType.DODGE,
            ActionType.DASH,
            ActionType.HELP,
            ActionType.HIDE,
            ActionType.READY,
            ActionType.SEARCH,
            ActionType.MAGIC  # Spells don't benefit from Lucky/Inspiration
        ]:
            return False
        
        # Check card name for utility actions (legacy system)
        if hasattr(self, 'name'):
            utility_keywords = ['use item', 'dodge', 'dash', 'help', 'hide', 'magic', 'spell', 'potion']
            card_name_lower = self.name.lower()
            if any(keyword in card_name_lower for keyword in utility_keywords):
                return False
        
        # Default to false for unknown actions
        print(f"[DEBUG] Card does not match any attack criteria, returning False")
        return False
            
    def _on_advantage_resource_used(self, resource_type):
        """Handle advantage resource usage."""
        if self.resource_manager and self.resource_manager.consume_resource(resource_type):
            print(f"[DEBUG] Applied {resource_type} offensive advantage for next attack (stored in resource manager)")
            
            # Hide halo immediately to prevent multiple clicks
            self.advantage_halo.hide()
            
    def set_resource_manager(self, resource_manager):
        """Set the advantage resource manager."""
        self.resource_manager = resource_manager

    def _use_brutal_strike(self, strike_type: str):
        """Use a Brutal Strike with the specified effect."""
        if not (self.character_context.get('class_id', '').lower() == 'barbarian' and
                self.character_context.get('level', 1) >= 9):
            return

        level = self.character_context.get('level', 1)
        damage_dice = "2d10" if level >= 17 else "1d10"

        # Apply strike effect based on type
        effect_descriptions = {
            'forceful': f"Push target 15 ft away and move toward them (+{damage_dice} damage)",
            'hamstring': f"Reduce target's speed by 15 ft until next turn (+{damage_dice} damage)",
            'staggering': f"Target has disadvantage on next save and can't make opportunity attacks (+{damage_dice} damage)",
            'sundering': f"Next attack roll vs target gains +5 bonus (+{damage_dice} damage)"
        }

        # Store the brutal strike effect for the next attack
        if isinstance(self.character_context, dict):
            self.character_context['brutal_strike_active'] = strike_type
            self.character_context['brutal_strike_damage'] = damage_dice

        # Log the effect
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    effect_desc = effect_descriptions.get(strike_type, f"Unknown effect (+{damage_dice} damage)")
                    parent.log_panel.log_combat(f"[BRUTAL] Brutal Strike ({strike_type.title()}) ready: {effect_desc}")
                    parent.log_panel.log_combat("Next Reckless Attack will apply this effect instead of advantage!")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error logging brutal strike: {e}")

    def _use_instinctive_pounce(self):
        """Use Instinctive Pounce movement when entering Rage."""
        if not (self.character_context.get('class_id', '').lower() == 'barbarian' and
                self.character_context.get('level', 1) >= 7):
            return

        # This is typically triggered automatically when Rage is activated
        # but can be used as a standalone action if needed

        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat("[LEAP] Instinctive Pounce: Move up to half your speed!")
                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error logging instinctive pounce: {e}")

    def _use_intimidating_presence(self):
        """Use Intimidating Presence to frighten nearby enemies."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        # Check if bonus action is available
        if self.action_economy_enabled and self.current_combat_session:
            from models.action_economy import ActionEconomyType
            state = self.current_combat_session.action_economy.get_combatant_state(character_id)
            if state and not state.bonus_action_available:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"{character_name} cannot use Intimidating Presence: Bonus action already used this turn")
                        break
                    parent = parent.parent()
                return

        # Use the enhanced subclass integration
        try:
            from services.subclass_action_integration import subclass_action_integration
            result = subclass_action_integration.activate_feature(character_id, "Intimidating Presence")

            if result.get('success'):
                # Consume the bonus action
                if self.action_economy_enabled and self.current_combat_session:
                    try:
                        self.current_combat_session.action_economy.use_action(character_id, ActionEconomyType.BONUS_ACTION)
                    except Exception as e:
                        print(f"Error consuming bonus action for Intimidating Presence: {e}")

                # Log the successful activation
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        save_dc = result.get('save_dc', 'Unknown')
                        uses_remaining = result.get('uses_remaining', 0)

                        parent.log_panel.log_combat(f"[BONUS ACTION] [FEAR] {character_name} uses Intimidating Presence!")
                        parent.log_panel.log_combat(f"All enemies within 30 ft must make a Wisdom save (DC {save_dc}) or be Frightened for 1 minute")
                        parent.log_panel.log_combat("Frightened creatures can repeat the save at the end of each turn")

                        if uses_remaining == 0:
                            parent.log_panel.log_combat("Intimidating Presence depleted (recharges on long rest)")

                        # Update action economy display
                        if hasattr(parent, 'action_panel'):
                            parent.action_panel._update_action_economy_display()

                        break
                    parent = parent.parent()

                # Update action card availability
                self._refresh_action_availability()
            else:
                # Log the failure
                reason = result.get('reason', 'Unknown error')
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"{character_name} cannot use Intimidating Presence: {reason}")
                        break
                    parent = parent.parent()

        except ImportError:
            # Fallback to old implementation
            if not (self.character_context.get('class_id', '').lower() == 'barbarian' and
                    self.character_context.get('subclass', '').lower() == 'berserker' and
                    self.character_context.get('level', 1) >= 14):
                return

            # Calculate save DC
            strength_mod = self.character_context.get('strength_modifier', 0)
            proficiency_bonus = self.character_context.get('proficiency_bonus', 2)
            save_dc = 8 + strength_mod + proficiency_bonus

            try:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        parent.log_panel.log_combat(f"[FEAR] Intimidating Presence activated!")
                        parent.log_panel.log_combat(f"All enemies within 30 ft must make a Wisdom save (DC {save_dc}) or be Frightened for 1 minute")
                        parent.log_panel.log_combat("Frightened creatures can repeat the save at the end of each turn")
                        break
                    parent = parent.parent()
            except Exception as e:
                print(f"Error logging intimidating presence: {e}")

        except Exception as e:
            print(f"Error using enhanced intimidating presence: {e}")

    def _use_retaliation(self):
        """Use Retaliation reaction to attack an enemy that damaged you."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        # Check if reaction is available
        if self.action_economy_enabled and self.current_combat_session:
            from models.action_economy import ActionEconomyType
            state = self.current_combat_session.action_economy.get_combatant_state(character_id)
            if state and not state.reaction_available:
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"{character_name} cannot retaliate: Reaction already used this round")
                        break
                    parent = parent.parent()
                return

        try:
            from services.subclass_action_integration import subclass_action_integration
            result = subclass_action_integration.activate_feature(character_id, "Retaliation")

            if result.get('success'):
                # Consume the reaction
                if self.action_economy_enabled and self.current_combat_session:
                    try:
                        self.current_combat_session.action_economy.use_action(character_id, ActionEconomyType.REACTION)
                    except Exception as e:
                        print(f"Error consuming reaction for Retaliation: {e}")

                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"[REACTION] {character_name} retaliates with a melee attack!")

                        if result.get('adds_rage_damage'):
                            parent.log_panel.log_combat("Attack includes Rage damage bonus")

                        # Update action economy display
                        if hasattr(parent, 'action_panel'):
                            parent.action_panel._update_action_economy_display()

                        break
                    parent = parent.parent()
            else:
                reason = result.get('error', 'Unknown error')
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"{character_name} cannot retaliate: {reason}")
                        break
                    parent = parent.parent()

        except Exception as e:
            print(f"Error using retaliation: {e}")

    def _use_heroic_warrior(self):
        """Trigger Heroic Warrior inspiration gain."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        try:
            from services.subclass_action_integration import subclass_action_integration
            result = subclass_action_integration.activate_feature(character_id, "Heroic Warrior")

            if result.get('success'):
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"[INSPIRATION] {character_name} gains Heroic Inspiration!")
                        break
                    parent = parent.parent()

        except Exception as e:
            print(f"Error using heroic warrior: {e}")

    def _use_survivor(self):
        """Trigger Survivor healing if conditions are met."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        try:
            from services.subclass_action_integration import subclass_action_integration
            result = subclass_action_integration.activate_feature(character_id, "Survivor")

            if result.get('success'):
                healing = result.get('healing', 0)
                new_hp = result.get('new_hp', 0)

                parent = self.parent()
                while parent:
                    if hasattr(parent, 'log_panel'):
                        character_name = self.character_context.get('name', 'Character')
                        parent.log_panel.log_combat(f"[HEALING] {character_name} Survivor healing: {healing} HP")
                        break
                    parent = parent.parent()

                # Update HP display if available
                if hasattr(self.parent(), 'character_sheet'):
                    max_hp = self.character_context.get('hit_points_max', new_hp)
                    self.parent().character_sheet.update_hp(new_hp, max_hp)

            else:
                # Don't log failures for automatic features like Survivor
                pass

        except Exception as e:
            print(f"Error using survivor: {e}")

    # ==================== THIEF FEATURE METHODS ====================

    def _use_fast_hands_thieves_tools(self):
        """Use thieves' tools as a bonus action with Fast Hands."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        # Check if bonus action is available
        # This would integrate with action economy system
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat("[THIEF] Fast Hands - Using thieves' tools as bonus action")
                break
            parent = parent.parent()

    def _use_fast_hands_use_object(self):
        """Use an object as a bonus action with Fast Hands."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        # Check if bonus action is available
        # This would integrate with action economy system
        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat("[THIEF] Fast Hands - Using object as bonus action")
                break
            parent = parent.parent()

    def _use_fast_hands_sleight_of_hand(self):
        """Make a Sleight of Hand check as a bonus action with Fast Hands."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        # Check if bonus action is available
        # This would integrate with action economy system

        # Roll Sleight of Hand check
        import random
        d20_roll = random.randint(1, 20)
        dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
        proficiency = self.character_context.get('proficiency_bonus', 2)

        # Assume proficiency in Sleight of Hand for rogues
        total = d20_roll + dex_mod + proficiency

        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[THIEF] Fast Hands - Sleight of Hand: d20({d20_roll}) +{dex_mod}(DEX) +{proficiency}(prof) = {total}")
                break
            parent = parent.parent()

    # ==================== ASSASSIN FEATURE METHODS ====================

    def _use_masterful_mimicry(self):
        """Use Masterful Mimicry to mimic speech or handwriting."""
        character_id = self._resolve_character_id()
        if not character_id:
            return

        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat("[ASSASSIN] Masterful Mimicry - Can perfectly mimic speech/handwriting after 1 hour study")
                break
            parent = parent.parent()

    def _apply_assassin_surprising_strikes(self, context: Dict[str, Any]) -> int:
        """Apply Assassin Surprising Strikes bonus damage if conditions are met."""
        # Check if character is an Assassin
        if not self._is_assassin():
            return 0

        # Check if it's the first round of combat
        if not self._is_first_round_of_combat():
            return 0

        # Check if target hasn't taken a turn yet (would have advantage, but we'll assume it's met)
        rogue_level = self.character_context.get('level', 1)

        parent = self.parent()
        while parent:
            if hasattr(parent, 'log_panel'):
                parent.log_panel.log_combat(f"[ASSASSIN] Surprising Strikes: +{rogue_level} bonus damage (first round)")
                break
            parent = parent.parent()

        return rogue_level

    def _apply_death_strike(self, context: Dict[str, Any], damage_breakdown: dict) -> bool:
        """Apply Death Strike if conditions are met (Assassin level 17+)."""
        # Check if character is level 17+ Assassin
        if not self._is_assassin() or self.character_context.get('level', 1) < 17:
            return False

        # Check if it's the first round of combat
        if not self._is_first_round_of_combat():
            return False

        # Calculate save DC
        dex_mod = (self.character_context.get('dexterity', 10) - 10) // 2
        proficiency = self.character_context.get('proficiency_bonus', 2)
        save_dc = 8 + dex_mod + proficiency

        # Assume target fails save for demonstration (in real implementation, would roll)
        import random
        target_con_save = random.randint(1, 20) + 2  # Assume +2 CON for target

        if target_con_save < save_dc:
            # Double the total damage
            original_total = damage_breakdown['total']
            damage_breakdown['total'] = original_total * 2

            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[ASSASSIN] Death Strike: Target failed CON save (DC {save_dc}) - DAMAGE DOUBLED! ({original_total} → {damage_breakdown['total']})")
                    break
                parent = parent.parent()
            return True
        else:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    parent.log_panel.log_combat(f"[ASSASSIN] Death Strike: Target succeeded CON save (DC {save_dc}) - no effect")
                    break
                parent = parent.parent()
            return False

    def _is_assassin(self) -> bool:
        """Check if character is an Assassin."""
        return (self.character_context.get('class_id', '').lower() == 'rogue' and
                self.character_context.get('subclass', '').lower() == 'assassin')

    def _is_first_round_of_combat(self) -> bool:
        """Check if it's the first round of combat."""
        # This would integrate with combat manager to track round number
        # For now, return True as a placeholder
        return hasattr(self, 'first_round_of_combat') and getattr(self, 'first_round_of_combat', True)







