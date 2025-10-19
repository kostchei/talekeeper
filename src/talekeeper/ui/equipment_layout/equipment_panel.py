# core
# category: core
"""
Equipment Panel Widget - Expandable inventory and equipment display

PyQt6 widget that manages character equipment and inventory:
- Equipment slots (armor, weapons, accessories)
- Inventory grid with item management
- Expandable width scales with layout profile settings
- Drag & drop item management
- Item tooltips and details

Designed to match ui_plan.md specifications:
- Default size follows the active layout profile
- Expanded size reaches across the encounter column
- Animation duration: 400ms with OutCubic easing
- Dark theme styling
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QScrollArea, QGridLayout,
                            QListWidget, QListWidgetItem, QTabWidget,
                            QGroupBox, QProgressBar, QSpinBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag, QPixmap, QPainter, QIcon
from typing import Optional, Dict, Any, List
from enum import Enum
from talekeeper.services.equipment import equipment_service

from talekeeper.ui.layout_profiles import BASELINE_PROFILE, LayoutProfile


class EquipmentSlot(Enum):
    """Equipment slot types."""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    ARMOR = "armor"
    HELMET = "helmet"
    GLOVES = "gloves"
    BOOTS = "boots"
    CLOAK = "cloak"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    AMULET = "amulet"
    BELT = "belt"


class EquipmentPanel(QWidget):
    """
    Expandable equipment and inventory widget with animation.
    
    Signals:
        expansion_changed: Emitted when panel expands/collapses (bool expanded)
        item_equipped: Emitted when item is equipped (dict item, EquipmentSlot slot)
        item_unequipped: Emitted when item is unequipped (EquipmentSlot slot)
        item_used: Emitted when item is used (dict item)
        inventory_changed: Emitted when inventory changes
    """
    
    expansion_changed = pyqtSignal(bool)  # expanded state
    item_equipped = pyqtSignal(dict, EquipmentSlot)  # item, slot
    item_unequipped = pyqtSignal(EquipmentSlot)  # slot
    item_used = pyqtSignal(dict)  # item
    inventory_changed = pyqtSignal()
    ac_changed = pyqtSignal(int)  # new AC value
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout_profile: Optional[LayoutProfile] = None,
    ):
        super().__init__(parent)
        self.layout_profile = layout_profile or BASELINE_PROFILE
        self.panel_width = self.layout_profile.equipment_panel_width
        self.panel_height = self.layout_profile.equipment_panel_height
        self.expanded_width = (
            self.panel_width + self.layout_profile.encounter_panel_width
        )
        self.toggle_height = max(1, self.panel_height - 14)
        self.expanded = False
        self.animation = None
        self.equipped_items = {}  # slot -> item mapping
        self.inventory_items = []  # list of inventory items
        self.character_strength = 10  # Default strength for carrying capacity
        self.character_dexterity = 10  # Default dexterity for AC calculation
        self.character_class = ""  # Character class for unarmored defense
        self.character_constitution = 10  # Default constitution for barbarian AC

        # Item state tracking
        self.attuned_items = set()  # Items currently attuned

        # Item effects service
        from talekeeper.services.item_effects import ItemEffectsService
        self.item_effects = ItemEffectsService()

        # Set initial size (extends to bottom of window)
        self.setFixedSize(self.panel_width, self.panel_height)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the equipment panel UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(3)
        
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(35)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Title
        self.title_label = QLabel("Equipment")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Expand button
        self.expand_btn = QPushButton("▼ Expand")
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.clicked.connect(self._toggle_expansion)
        header_layout.addWidget(self.expand_btn)
        
        # === CONTENT TABS ===
        self.content_tabs = QTabWidget()
        self.content_tabs.setObjectName("contentTabs")
        
        # --- EQUIPMENT TAB ---
        self.equipment_tab = QWidget()
        self.content_tabs.addTab(self.equipment_tab, "Equipped")
        
        equipment_layout = QVBoxLayout(self.equipment_tab)
        equipment_layout.setContentsMargins(5, 5, 5, 5)
        
        # Attack display (always visible)
        self.attacks_frame = QFrame()
        self.attacks_frame.setObjectName("attacksFrame")
        attacks_layout = QVBoxLayout(self.attacks_frame)
        attacks_layout.setContentsMargins(2, 2, 2, 2)
        attacks_layout.setSpacing(1)
        
        # Main Hand attack
        self.main_hand_frame = QFrame()
        main_hand_layout = QHBoxLayout(self.main_hand_frame)
        main_hand_layout.setContentsMargins(2, 1, 2, 1)
        main_hand_layout.addWidget(QLabel("Main Hand:"))
        self.main_hand_label = QLabel("Unarmed +2 (1+2)")
        self.main_hand_label.setObjectName("attackValue")
        main_hand_layout.addWidget(self.main_hand_label)
        main_hand_layout.addStretch()
        attacks_layout.addWidget(self.main_hand_frame)
        
        # Off Hand attack  
        self.off_hand_frame = QFrame()
        off_hand_layout = QHBoxLayout(self.off_hand_frame)
        off_hand_layout.setContentsMargins(2, 1, 2, 1)
        off_hand_layout.addWidget(QLabel("Off Hand:"))
        self.off_hand_label = QLabel("None")
        self.off_hand_label.setObjectName("attackValue")
        off_hand_layout.addWidget(self.off_hand_label)
        off_hand_layout.addStretch()
        attacks_layout.addWidget(self.off_hand_frame)
        
        # Unarmed attack
        self.unarmed_frame = QFrame()
        unarmed_layout = QHBoxLayout(self.unarmed_frame)
        unarmed_layout.setContentsMargins(2, 1, 2, 1)
        unarmed_layout.addWidget(QLabel("Unarmed:"))
        self.unarmed_label = QLabel("+2 (1+2)")
        self.unarmed_label.setObjectName("attackValue")
        unarmed_layout.addWidget(self.unarmed_label)
        unarmed_layout.addStretch()
        attacks_layout.addWidget(self.unarmed_frame)
        
        # Magic attack
        self.magic_frame = QFrame()
        magic_layout = QHBoxLayout(self.magic_frame)
        magic_layout.setContentsMargins(2, 1, 2, 1)
        magic_layout.addWidget(QLabel("Magic:"))
        self.magic_label = QLabel("+4 spell attack")
        self.magic_label.setObjectName("attackValue")
        magic_layout.addWidget(self.magic_label)
        magic_layout.addStretch()
        attacks_layout.addWidget(self.magic_frame)
        
        equipment_layout.addWidget(self.attacks_frame)
        
        # Equipment slots (compact view)
        self.equipment_slots_frame = QFrame()
        self.equipment_slots_frame.setObjectName("equipmentSlotsFrame")
        
        self.slots_layout = QGridLayout(self.equipment_slots_frame)
        self.slots_layout.setContentsMargins(3, 3, 3, 3)
        self.slots_layout.setSpacing(2)
        
        # Create equipment slot widgets
        self.slot_widgets = {}
        self._create_equipment_slots()
        
        equipment_layout.addWidget(self.equipment_slots_frame)
        
        # --- INVENTORY TAB ---
        self.inventory_tab = QWidget()
        self.content_tabs.addTab(self.inventory_tab, "Inventory")
        
        inventory_layout = QVBoxLayout(self.inventory_tab)
        inventory_layout.setContentsMargins(5, 5, 5, 5)
        
        # Inventory controls
        inv_controls_frame = QFrame()
        inv_controls_layout = QHBoxLayout(inv_controls_frame)
        inv_controls_layout.setContentsMargins(2, 2, 2, 2)
        
        # Weight display
        weight_label = QLabel("Weight:")
        inv_controls_layout.addWidget(weight_label)
        
        self.weight_bar = QProgressBar()
        self.weight_bar.setObjectName("weightBar")
        self.weight_bar.setMaximum(100)
        self.weight_bar.setValue(25)
        inv_controls_layout.addWidget(self.weight_bar)
        
        self.weight_label = QLabel("25/100")
        self.weight_label.setObjectName("weightLabel")
        inv_controls_layout.addWidget(self.weight_label)
        
        inventory_layout.addWidget(inv_controls_frame)
        
        # Inventory list
        self.inventory_list = QListWidget()
        self.inventory_list.setObjectName("inventoryList")
        self.inventory_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.inventory_list.itemDoubleClicked.connect(self._use_item)
        inventory_layout.addWidget(self.inventory_list)
        
        # Inventory actions
        inv_actions_frame = QFrame()
        inv_actions_layout = QHBoxLayout(inv_actions_frame)
        inv_actions_layout.setContentsMargins(2, 2, 2, 2)
        
        self.use_item_btn = QPushButton("Use")
        self.use_item_btn.setObjectName("smallButton")
        self.use_item_btn.clicked.connect(self._use_selected_item)
        inv_actions_layout.addWidget(self.use_item_btn)
        
        self.drop_item_btn = QPushButton("Drop")
        self.drop_item_btn.setObjectName("smallButton")
        self.drop_item_btn.clicked.connect(self._drop_selected_item)
        inv_actions_layout.addWidget(self.drop_item_btn)
        
        inv_actions_layout.addStretch()
        
        inventory_layout.addWidget(inv_actions_frame)
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.content_tabs, 1)
    
    def _create_equipment_slots(self):
        """Create the equipment slot widgets."""
        # Define slot positions for compact layout
        slot_positions = {
            EquipmentSlot.CLOAK: (0, 0),
            EquipmentSlot.HELMET: (0, 1),
            EquipmentSlot.AMULET: (0, 2),
            EquipmentSlot.BELT: (1, 0),
            EquipmentSlot.ARMOR: (1, 1),
            EquipmentSlot.MAIN_HAND: (1, 2),
            EquipmentSlot.GLOVES: (2, 0),
            EquipmentSlot.RING_1: (2, 1),
            EquipmentSlot.OFF_HAND: (2, 2),
            EquipmentSlot.BOOTS: (3, 0),
            EquipmentSlot.RING_2: (3, 1),
        }
        
        for slot, (row, col) in slot_positions.items():
            slot_widget = EquipmentSlotWidget(slot)
            slot_widget.item_dropped.connect(self._equip_item)
            slot_widget.item_removed.connect(self._unequip_item)
            
            self.slot_widgets[slot] = slot_widget
            self.slots_layout.addWidget(slot_widget, row, col)
    
    def _apply_styles(self):
        """Apply initial styling using the active theme palette."""
        theme_name = 'light'
        parent = self.parent()
        if parent and hasattr(parent, 'current_theme'):
            theme_name = getattr(parent, 'current_theme', 'light')
        self.update_theme(theme_name)
    
    def update_theme(self, theme_name: str):
        """Update styling based on theme."""
        from talekeeper.ui.themes import get_theme_palette
        palette = get_theme_palette(theme_name)
        
        style_sheet = f"""
        EquipmentPanel {{
            background-color: {palette['surface']};
            border: 2px solid {palette['border']};
            border-radius: 8px;
        }}
        
        QFrame#headerFrame {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QFrame#attacksFrame {{
            background-color: {palette['background']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QLabel#attackValue {{
            color: {palette['accent_tertiary']};
            font-size: 11px;
            font-weight: bold;
        }}
        
        QFrame#equipmentSlotsFrame {{
            background-color: {palette['background']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QLabel#titleLabel {{
            color: {palette['text']};
            font-size: 14px;
            font-weight: bold;
        }}
        
        QLabel#statValue {{
            color: {palette['accent_tertiary']};
            font-size: 12px;
            font-weight: bold;
        }}
        
        QLabel#weightLabel {{
            color: {palette['text_secondary']};
            font-size: 11px;
            min-width: 50px;
        }}
        
        QPushButton#expandButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
        
        QPushButton#expandButton:hover {{
            background-color: {palette['button_hover']};
        }}
        
        QPushButton#expandButton:pressed {{
            background-color: {palette['button_pressed']};
        }}
        
        QScrollArea#inventoryScrollArea {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QScrollArea#inventoryScrollArea > QWidget > QWidget {{
            background-color: {palette['surface']};
        }}
        
        QListWidget {{
            background-color: {palette['surface']};
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
        
        QProgressBar {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            text-align: center;
            color: {palette['text']};
        }}
        
        QScrollBar:vertical {{
            background-color: {palette['surface']};
            width: 12px;
            border: 1px solid {palette['border']};
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {palette['accent_primary']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {palette['accent_secondary']};
        }}
        """
        self.setStyleSheet(style_sheet)
    
    def _toggle_expansion(self):
        """Toggle the panel expansion - expands leftward to cover encounter pane."""
        # Toggle expansion state
        self.expanded = not self.expanded
        
        width_delta = self.expanded_width - self.panel_width

        if self.expanded:
            # EXPAND: Move left and resize to cover encounter pane
            current_pos = self.pos()
            new_x = current_pos.x() - width_delta
            self.move(new_x, current_pos.y())

            self.setFixedSize(self.expanded_width, self.toggle_height)
            self.expand_btn.setText("▲ Collapse")
            self.raise_()  # Bring to front to cover encounter pane

            # Switch to expanded layout
            self._switch_to_expanded_layout()
        else:
            # COLLAPSE: Move right and resize back to normal position
            current_pos = self.pos()
            new_x = current_pos.x() + width_delta
            self.move(new_x, current_pos.y())

            self.setFixedSize(self.panel_width, self.toggle_height)
            self.expand_btn.setText("▼ Expand")
            
            # Switch to compact layout
            self._switch_to_compact_layout()
        
        # Force immediate layout update
        self.updateGeometry()
        self.adjustSize()
        
        # Emit signal
        self.expansion_changed.emit(self.expanded)
    
    def _switch_to_expanded_layout(self):
        """Switch to expanded layout with more detailed information."""
        # Reorganize equipment slots in expanded view
        # This would show larger slot icons, item tooltips, etc.
        pass
    
    def _switch_to_compact_layout(self):
        """Switch to compact layout."""
        # Reorganize equipment slots in compact view
        pass
    
    def _equip_item(self, item: Dict[str, Any], slot: EquipmentSlot):
        """Equip an item to a slot."""
        # Remove from inventory if present
        if item in self.inventory_items:
            self.inventory_items.remove(item)
            self._update_inventory_display()
        
        # Check if this is a two-handed weapon
        is_two_handed = self._is_two_handed_weapon(item)
        
        if is_two_handed and slot == EquipmentSlot.MAIN_HAND:
            # Two-handed weapon - unequip both main hand and off-hand
            if EquipmentSlot.MAIN_HAND in self.equipped_items:
                old_main = self.equipped_items[EquipmentSlot.MAIN_HAND]
                self.inventory_items.append(old_main)
                
            if EquipmentSlot.OFF_HAND in self.equipped_items:
                old_off = self.equipped_items[EquipmentSlot.OFF_HAND]
                self.inventory_items.append(old_off)
            
            # Equip in both slots (same item reference)
            self.equipped_items[EquipmentSlot.MAIN_HAND] = item
            self.equipped_items[EquipmentSlot.OFF_HAND] = item
            self.slot_widgets[EquipmentSlot.MAIN_HAND].set_item(item)
            self.slot_widgets[EquipmentSlot.OFF_HAND].set_item(item)
            
        elif slot == EquipmentSlot.OFF_HAND:
            # Check if this is a weapon that cannot be equipped to off-hand
            from talekeeper.services.equipment import equipment_service
            db_item = equipment_service.get_item(item.get('name', ''))
            item_is_weapon = db_item and db_item.get('item_type') == 'weapon'

            if item_is_weapon:
                # Weapons in off-hand must have the "light" property
                weapon_props = db_item.get('weapon_properties', [])
                if isinstance(weapon_props, str):
                    import json
                    weapon_props = json.loads(weapon_props)

                if 'light' not in weapon_props:
                    # Cannot equip non-light weapon to off-hand - put it back in inventory
                    self.inventory_items.append(item)
                    self._update_inventory_display()
                    print(f"Cannot equip {item.get('name')} to off-hand - weapon must have the 'light' property")
                    return

            # If equipping to off-hand, check if main hand has two-handed weapon
            main_hand_item = self.equipped_items.get(EquipmentSlot.MAIN_HAND)
            if main_hand_item and self._is_two_handed_weapon(main_hand_item):
                # Can't equip ANYTHING to off-hand if main hand has two-handed weapon
                # Return item to inventory - you don't have 3 hands!
                self.inventory_items.append(item)
                self._update_inventory_display()
                print(f"Cannot equip {item.get('name')} to off-hand - {main_hand_item.get('name')} is two-handed (requires both hands)")
                return

            # Unequip current off-hand item if any
            if slot in self.equipped_items:
                old_item = self.equipped_items[slot]
                self.inventory_items.append(old_item)

            # Equip new item to off-hand
            self.equipped_items[slot] = item
            self.slot_widgets[slot].set_item(item)
            
        else:
            # Regular single-slot equipment
            # Unequip current item in slot if any
            if slot in self.equipped_items:
                old_item = self.equipped_items[slot]
                self.inventory_items.append(old_item)
            
            # Equip new item
            self.equipped_items[slot] = item
            self.slot_widgets[slot].set_item(item)
        
        # Update displays
        self._update_inventory_display()
        self._update_stats_display()

        # Update magical item bonuses
        self._update_character_bonuses()

        # Emit signal
        self.item_equipped.emit(item, slot)
        self.inventory_changed.emit()
    
    def _is_two_handed_weapon(self, item: Dict[str, Any]) -> bool:
        """Check if an item is a two-handed weapon."""
        try:
            from talekeeper.services.equipment import equipment_service
            import re

            # Get item name and try to extract base weapon name from magical/silvered variants
            item_name = item.get('name', '')

            # Try exact match first
            db_item = equipment_service.get_item(item_name)

            # If no match and name has parentheses, extract base weapon name
            # E.g., "Silvered Weapon (Greataxe)" -> "Greataxe"
            # E.g., "Greataxe +1" -> "Greataxe"
            if not db_item or not db_item.get('weapon_properties'):
                # Try extracting base name from patterns like "Something (BaseName)"
                paren_match = re.search(r'\(([^)]+)\)', item_name)
                if paren_match:
                    base_name = paren_match.group(1).strip()
                    db_item = equipment_service.get_item(base_name)

                # Try removing +1, +2, +3 modifiers
                if not db_item or not db_item.get('weapon_properties'):
                    base_name = re.sub(r'\s*\+\d+\s*$', '', item_name).strip()
                    if base_name != item_name:
                        db_item = equipment_service.get_item(base_name)

            if db_item and db_item.get('weapon_properties'):
                properties = db_item['weapon_properties']
                # Properties might be a JSON string or already parsed list
                if isinstance(properties, str):
                    import json
                    properties = json.loads(properties)
                return 'two-handed' in properties
            return False
        except Exception as e:
            print(f"Error checking if {item.get('name', 'unknown')} is two-handed: {e}")
            return False
    
    def _unequip_item(self, slot: EquipmentSlot):
        """Unequip an item from a slot."""
        if slot in self.equipped_items:
            item = self.equipped_items[slot]
            
            # Check if it's a two-handed weapon - if so, unequip from both slots
            if self._is_two_handed_weapon(item):
                # Remove from both main hand and off-hand
                self.equipped_items.pop(EquipmentSlot.MAIN_HAND, None)
                self.equipped_items.pop(EquipmentSlot.OFF_HAND, None)
                self.slot_widgets[EquipmentSlot.MAIN_HAND].clear_item()
                self.slot_widgets[EquipmentSlot.OFF_HAND].clear_item()
                # Add to inventory only once
                self.inventory_items.append(item)
            else:
                # Regular single-slot item
                self.equipped_items.pop(slot)
                self.inventory_items.append(item)
                self.slot_widgets[slot].clear_item()
            
            # Update displays
            self._update_inventory_display()
            self._update_stats_display()

            # Update magical item bonuses
            self._update_character_bonuses()

            # Emit signals
            self.item_unequipped.emit(slot)
            self.inventory_changed.emit()
    
    def _use_item(self, item_widget: QListWidgetItem):
        """Use an item from inventory."""
        item_data = item_widget.data(Qt.ItemDataRole.UserRole)
        if item_data:
            if item_data['equipped']:
                # Unequip the item
                slot = item_data['slot']
                self._unequip_item(slot)
            else:
                item = item_data['item']
                item_type = item.get('item_type', item.get('type', ''))
                db_slot = item.get('slot', '')

                target_slot = None

                if db_slot:
                    slot_map = {
                        'main_hand': EquipmentSlot.MAIN_HAND,
                        'off_hand': EquipmentSlot.OFF_HAND,
                        'armor': EquipmentSlot.ARMOR,
                        'helmet': EquipmentSlot.HELMET,
                        'gloves': EquipmentSlot.GLOVES,
                        'boots': EquipmentSlot.BOOTS,
                        'cloak': EquipmentSlot.CLOAK,
                        'ring': EquipmentSlot.RING_1,
                        'amulet': EquipmentSlot.AMULET,
                        'belt': EquipmentSlot.BELT,
                        'shield': EquipmentSlot.OFF_HAND,
                    }
                    target_slot = slot_map.get(db_slot)

                    if db_slot == 'ring':
                        if self.equipped_items.get(EquipmentSlot.RING_1):
                            target_slot = EquipmentSlot.RING_2

                elif item_type == 'weapon':
                    # Check if weapon is two-handed
                    if self._is_two_handed_weapon(item):
                        # Two-handed weapons ALWAYS go to main hand
                        target_slot = EquipmentSlot.MAIN_HAND
                    else:
                        # Regular weapons: try main hand, then off-hand
                        target_slot = EquipmentSlot.MAIN_HAND
                        if self.equipped_items.get(target_slot):
                            target_slot = EquipmentSlot.OFF_HAND

                elif item_type == 'armor':
                    target_slot = EquipmentSlot.ARMOR

                elif item_type == 'shield':
                    target_slot = EquipmentSlot.OFF_HAND

                elif item_type in ['helmet', 'hat']:
                    target_slot = EquipmentSlot.HELMET

                elif item_type in ['gloves', 'gauntlets']:
                    target_slot = EquipmentSlot.GLOVES

                elif item_type in ['boots', 'shoes']:
                    target_slot = EquipmentSlot.BOOTS

                elif item_type in ['cloak', 'cape'] or 'cloak of protection' in item.get('name', '').lower():
                    target_slot = EquipmentSlot.CLOAK

                elif item_type == 'ring' or 'ring of protection' in item.get('name', '').lower():
                    target_slot = EquipmentSlot.RING_1
                    if self.equipped_items.get(target_slot):
                        target_slot = EquipmentSlot.RING_2

                elif item_type in ['amulet', 'necklace']:
                    target_slot = EquipmentSlot.AMULET

                elif item_type == 'belt':
                    target_slot = EquipmentSlot.BELT

                elif item_type == 'tool' and 'thieves tools' in item.get('name', '').lower():
                    target_slot = EquipmentSlot.BELT

                if target_slot:
                    if target_slot in [EquipmentSlot.RING_1, EquipmentSlot.RING_2]:
                        if not self.equipped_items.get(target_slot):
                            self._equip_item(item, target_slot)
                        else:
                            self.item_used.emit(item)
                    elif target_slot == EquipmentSlot.MAIN_HAND:
                        if not self.equipped_items.get(target_slot):
                            self._equip_item(item, target_slot)
                        elif not self.equipped_items.get(EquipmentSlot.OFF_HAND):
                            self._equip_item(item, EquipmentSlot.OFF_HAND)
                        else:
                            self.item_used.emit(item)
                    else:
                        self._equip_item(item, target_slot)
                else:
                    self.item_used.emit(item)
    
    def _use_selected_item(self):
        """Use the currently selected inventory item."""
        current_item = self.inventory_list.currentItem()
        if current_item:
            self._use_item(current_item)
    
    def _drop_selected_item(self):
        """Drop the currently selected inventory item."""
        current_item = self.inventory_list.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            if item_data:
                if item_data['equipped']:
                    # Unequip and remove the item
                    slot = item_data['slot']
                    if slot in self.equipped_items:
                        self.equipped_items.pop(slot)
                        self.slot_widgets[slot].clear_item()
                        self._update_inventory_display()
                        self._update_stats_display()

                        # Update magical item bonuses
                        self._update_character_bonuses()

                        self.item_unequipped.emit(slot)
                        self.inventory_changed.emit()
                else:
                    # Remove from unequipped inventory
                    item = item_data['item']
                    if item in self.inventory_items:
                        self.inventory_items.remove(item)
                        self._update_inventory_display()
                        self.inventory_changed.emit()
    
    def _update_inventory_display(self):
        """Update the inventory list display."""
        self.inventory_list.clear()
        
        # Add equipped items first (marked as equipped)
        for slot, item in self.equipped_items.items():
            item_name = item.get('name', 'Unknown Item')
            item_type = item.get('item_type', '')
            slot_name = slot.value.replace('_', ' ').title()

            display_text = f"{item_name} [Equipped - {slot_name}]"
            if item_type:
                display_text += f" ({item_type})"

            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, {'item': item, 'equipped': True, 'slot': slot})

            description = item.get('description', '')
            if description:
                list_item.setToolTip(description)

            self.inventory_list.addItem(list_item)
        
        # Add unequipped inventory items
        bag_weight = 0.0
        for item in self.inventory_items:
            item_name = item.get('name', 'Unknown Item')
            item_type = item.get('item_type', '')
            quantity = item.get('quantity', 1)
            stored_in_bag = item.get('stored_in_bag', 0)
            treasure_type = item.get('treasure_type', '')

            display_text = f"{item_name}"
            if quantity > 1:
                if treasure_type in ('coins', 'currency') or item_type == 'currency':
                    import math
                    display_text += f" ({math.floor(quantity * 100) / 100})"
                else:
                    display_text += f" ({quantity})"
            if item_type:
                display_text += f" [{item_type}]"
            if stored_in_bag:
                display_text += " [Bag of Holding]"

            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, {'item': item, 'equipped': False, 'slot': None})

            description = item.get('description', '')
            if description:
                list_item.setToolTip(description)

            self.inventory_list.addItem(list_item)
        
        # Update weight - include both equipped and unequipped items
        equipped_weight = sum(item.get('weight_lb', 0) for item in self.equipped_items.values())
        inventory_weight = 0.0

        for item in self.inventory_items:
            total_weight_item = item.get('weight_total_lb')
            if total_weight_item is None:
                total_weight_item = item.get('weight_lb', 0) or 0

            if item.get('stored_in_bag'):
                bag_weight += total_weight_item
            else:
                inventory_weight += total_weight_item

        total_weight = equipped_weight + inventory_weight
        
        # D&D 5e carrying capacity rules
        max_weight = self.character_strength * 15  # Maximum carrying capacity
        encumbered_threshold = self.character_strength * 5   # Speed -10 ft
        heavily_encumbered_threshold = self.character_strength * 10  # Speed -20 ft, disadvantage
        
        # Determine encumbrance status
        encumbrance_status = ""
        if total_weight > heavily_encumbered_threshold:
            encumbrance_status = " [Heavily Encumbered]"
            self.weight_bar.setStyleSheet("QProgressBar::chunk { background-color: #cc4444; }")
        elif total_weight > encumbered_threshold:
            encumbrance_status = " [Encumbered]"
            self.weight_bar.setStyleSheet("QProgressBar::chunk { background-color: #ccaa44; }")
        else:
            self.weight_bar.setStyleSheet("QProgressBar::chunk { background-color: #44aa44; }")
        
        # Update progress bar (0-100 scale)
        weight_percentage = int(min(100, (total_weight / max_weight) * 100)) if max_weight else 0
        self.weight_bar.setValue(weight_percentage)
        label_text = f"{total_weight:.1f}/{max_weight} lb{encumbrance_status}"
        if bag_weight > 0:
            label_text += f" (+{bag_weight:.1f} lb in Bag)"
        self.weight_label.setText(label_text)
    
    def _update_stats_display(self):
        """Update the stats display based on equipped items."""
        # Update attack displays
        self._update_attack_displays()
        
        # Don't emit AC changes - let game engine handle AC calculation
    
    def _update_attack_displays(self):
        """Update all attack display rows."""
        # Main Hand attack
        main_hand_weapon = self.equipped_items.get(EquipmentSlot.MAIN_HAND)
        if main_hand_weapon and (main_hand_weapon.get('item_type') == 'weapon' or main_hand_weapon.get('type') == 'weapon'):
            attack_bonus = self._calculate_weapon_attack_bonus(main_hand_weapon)
            damage = self._calculate_weapon_damage(main_hand_weapon)
            weapon_name = main_hand_weapon.get('name', 'Weapon')
            self.main_hand_label.setText(f"{weapon_name} Hit {attack_bonus:+d} Dam {damage}")
        else:
            # Unarmed attack as main hand
            attack_bonus = self._calculate_unarmed_attack_bonus()
            damage = self._calculate_unarmed_damage()
            self.main_hand_label.setText(f"Unarmed Hit {attack_bonus:+d} Dam {damage}")
        
        # Off Hand attack
        off_hand_weapon = self.equipped_items.get(EquipmentSlot.OFF_HAND)
        if off_hand_weapon and (off_hand_weapon.get('item_type') == 'weapon' or off_hand_weapon.get('type') == 'weapon'):
            attack_bonus = self._calculate_weapon_attack_bonus(off_hand_weapon, is_off_hand=True)
            damage = self._calculate_weapon_damage(off_hand_weapon, is_off_hand=True)
            weapon_name = off_hand_weapon.get('name', 'Weapon')
            self.off_hand_label.setText(f"{weapon_name} Hit {attack_bonus:+d} Dam {damage}")
        else:
            self.off_hand_label.setText("None")
        
        # Unarmed attack
        attack_bonus = self._calculate_unarmed_attack_bonus()
        damage = self._calculate_unarmed_damage()
        self.unarmed_label.setText(f"Hit {attack_bonus:+d} Dam {damage}")
        
        # Magic attack
        spell_attack_bonus = self._calculate_spell_attack_bonus()
        self.magic_label.setText(f"Hit {spell_attack_bonus:+d} spell attack")
    
    def _extract_weapon_properties(self, weapon: Dict[str, Any]) -> List[str]:
        """Return normalized weapon property tags for the provided weapon."""
        props = weapon.get('weapon_properties') or weapon.get('properties') or []
        if isinstance(props, str):
            if ',' in props:
                props = [p.strip() for p in props.split(',') if p.strip()]
            else:
                props = [props.strip()] if props.strip() else []
        return [str(p).lower() for p in props if isinstance(p, str)]

    def _calculate_weapon_attack_bonus(self, weapon: Dict[str, Any], is_off_hand: bool = False) -> int:
        """Calculate attack bonus for a specific weapon."""
        prof_bonus = 2  # Assume +2 proficiency until level scaling hooks land

        weapon_props = self._extract_weapon_properties(weapon)
        damage_type = (weapon.get('damage_type') or '').lower()

        if 'finesse' in weapon_props:
            str_mod = (self.character_strength - 10) // 2
            dex_mod = (self.character_dexterity - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        elif 'ranged' in weapon_props or damage_type == 'ranged':
            ability_mod = (self.character_dexterity - 10) // 2
        else:
            ability_mod = (self.character_strength - 10) // 2

        magic_bonus = weapon.get('attack_bonus', 0) or 0
        return prof_bonus + ability_mod + magic_bonus
    
    def _calculate_weapon_damage(self, weapon: Dict[str, Any], is_off_hand: bool = False) -> str:
        """Format weapon damage string."""
        damage_dice = weapon.get('damage_dice', '1d4')
        damage_type = (weapon.get('damage_type') or 'slashing').lower()

        weapon_props = self._extract_weapon_properties(weapon)
        if 'finesse' in weapon_props:
            str_mod = (self.character_strength - 10) // 2
            dex_mod = (self.character_dexterity - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        elif 'ranged' in weapon_props or damage_type == 'ranged':
            ability_mod = (self.character_dexterity - 10) // 2
        else:
            ability_mod = (self.character_strength - 10) // 2

        if is_off_hand:
            ability_mod = 0

        magic_bonus = weapon.get('damage_bonus', 0) or 0
        total_bonus = ability_mod + magic_bonus

        if total_bonus > 0:
            return f"{damage_dice}+{total_bonus}"
        if total_bonus < 0:
            return f"{damage_dice}{total_bonus}"
        return damage_dice
    
    def _calculate_unarmed_attack_bonus(self) -> int:
        """Calculate unarmed attack bonus."""
        prof_bonus = 2  # Assume level 1
        str_mod = (self.character_strength - 10) // 2
        return prof_bonus + str_mod
    
    def _calculate_unarmed_damage(self) -> str:
        """Calculate unarmed damage."""
        str_mod = (self.character_strength - 10) // 2
        if str_mod > 0:
            return f"1+{str_mod}"
        elif str_mod < 0:
            return f"1{str_mod}"
        else:
            return "1"
    
    def _calculate_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        prof_bonus = 2  # Assume level 1
        # For now, assume primary spellcasting ability based on class
        # This should be configurable based on character class
        spellcasting_mod = (self.character_dexterity - 10) // 2  # Placeholder
        return prof_bonus + spellcasting_mod
    
    
    def _calculate_main_hand_attack_bonus(self):
        """Calculate attack bonus for main hand weapon."""
        main_hand = self.equipped_items.get(EquipmentSlot.MAIN_HAND)
        if not main_hand:
            return 0
        
        # Base proficiency bonus (assume level 1 = +2 for now)
        prof_bonus = 2
        
        # Get ability modifier
        weapon_props = main_hand.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            # Finesse: use higher of Str or Dex
            str_mod = (self.character_strength - 10) // 2
            dex_mod = (self.character_dexterity - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        else:
            # Most melee weapons use Str
            ability_mod = (self.character_strength - 10) // 2
        
        # Magic weapon bonus
        magic_bonus = main_hand.get('attack_bonus', 0)
        
        return prof_bonus + ability_mod + magic_bonus
    
    def add_item_to_inventory(self, item: Dict[str, Any]):
        """Add an item to the inventory."""
        self.inventory_items.append(item)
        self._update_inventory_display()
        self.inventory_changed.emit()
    
    def remove_item_from_inventory(self, item: Dict[str, Any]):
        """Remove an item from the inventory."""
        if item in self.inventory_items:
            self.inventory_items.remove(item)
            self._update_inventory_display()
            self.inventory_changed.emit()
    
    def load_equipment_data(self, equipped_items: Dict[str, Any], inventory_items: List[Dict[str, Any]], character_strength: int = 10, character_dexterity: int = 10, character_class: str = "", character_constitution: int = 10):
        """Load equipment and inventory data."""
        # Store character's stats for calculations
        self.character_strength = character_strength
        self.character_dexterity = character_dexterity
        self.character_class = character_class
        self.character_constitution = character_constitution
        
        # Load equipped items
        self.equipped_items.clear()
        
        # Clear all slot widgets first
        for slot_widget in self.slot_widgets.values():
            slot_widget.clear_item()
        
        # Then load new equipped items
        # Check if main_hand and off_hand have the same weapon (two-handed)
        main_hand_item = equipped_items.get('main_hand')
        off_hand_item = equipped_items.get('off_hand')

        for slot_name, item in equipped_items.items():
            try:
                slot = EquipmentSlot(slot_name)

                # Skip off_hand if it's the same as main_hand (two-handed weapon)
                if slot == EquipmentSlot.OFF_HAND and main_hand_item and off_hand_item:
                    if main_hand_item.get('name') == off_hand_item.get('name'):
                        # This is a two-handed weapon - skip showing in off-hand slot
                        # The main hand will handle both slots
                        continue

                self.equipped_items[slot] = item
                self.slot_widgets[slot].set_item(item)
            except ValueError:
                pass  # Invalid slot name
        
        # Load inventory
        self.inventory_items = inventory_items.copy()
        
        # Update displays
        self._update_inventory_display()
        self._update_stats_display()
    
    def get_equipped_items(self) -> Dict[str, Any]:
        """Get currently equipped items with enriched database stats."""
        from talekeeper.services.equipment import equipment_service
        
        enriched_items = {}
        for slot, item in self.equipped_items.items():
            if item and item.get('name'):
                # Get full stats from database
                db_stats = equipment_service.get_item(item['name'])
                if db_stats:
                    # Merge database stats with existing item data
                    enriched_item = {**item}
                    enriched_item.update({
                        'damage_dice': db_stats.get('damage_dice'),
                        'damage_type': db_stats.get('damage_type'),
                        'weapon_properties': db_stats.get('weapon_properties'),
                        'armor_class': db_stats.get('armor_class'),
                        'armor_type': db_stats.get('armor_type'),
                    })
                    enriched_items[slot.value] = enriched_item
                else:
                    enriched_items[slot.value] = item
            elif item:
                enriched_items[slot.value] = item
        
        return enriched_items
    
    def get_equipped_items_dict(self) -> Dict[str, Any]:
        """Get currently equipped items as dictionary - alias for get_equipped_items."""
        return self.get_equipped_items()
    
    def get_inventory_items(self) -> List[Dict[str, Any]]:
        """Get inventory items."""
        return self.inventory_items.copy()
    
    def is_expanded(self) -> bool:
        """Return current expansion state."""
        return self.expanded

    def enable_attunement(self):
        """Enable attunement after a rest."""
        print("[EQUIPMENT] Attunement enabled after rest")

    def _update_character_bonuses(self):
        """Update character bonuses from equipped magical items."""
        try:
            # Find parent with game engine
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine.current_character:
                    character_id = parent.game_engine.current_character['id']

                    # Calculate bonuses from equipped items
                    bonuses = self.item_effects.calculate_bonuses_for_character(
                        character_id, self.equipped_items
                    )

                    print(f"[EQUIPMENT] Updated character bonuses: {bonuses}")

                    # Trigger AC recalculation if there are AC bonuses
                    if bonuses.get('ac_bonus', 0) > 0:
                        # Find main window to trigger AC update
                        main_parent = parent
                        while main_parent:
                            if hasattr(main_parent, '_update_character_ac'):
                                main_parent._update_character_ac()
                                break
                            main_parent = main_parent.parent()

                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error updating character bonuses: {e}")

    def _load_attunement_from_database(self):
        """Load attunement state from talekeeper.database."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine.current_character:
                    character_id = parent.game_engine.current_character['id']

                    import sqlite3
                    with sqlite3.connect('talekeeper.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT item_key FROM character_attunements
                            WHERE character_id = ?
                        """, (character_id,))

                        rows = cursor.fetchall()
                        self.attuned_items.clear()
                        for row in rows:
                            self.attuned_items.add(row[0])

                        print(f"[EQUIPMENT] Loaded {len(self.attuned_items)} attuned items")

                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error loading attunement state: {e}")

    def _save_attunement_to_database(self, item_key: str, attune: bool):
        """Save or remove attunement state to/from talekeeper.database."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine.current_character:
                    character_id = parent.game_engine.current_character['id']

                    self.item_effects.set_attunement(character_id, item_key, attune)

                    if attune:
                        self.attuned_items.add(item_key)
                    else:
                        self.attuned_items.discard(item_key)

                    # Update character bonuses after attunement change
                    self._update_character_bonuses()

                    break
                parent = parent.parent()
        except Exception as e:
            print(f"Error saving attunement state: {e}")


class EquipmentSlotWidget(QWidget):
    """Widget representing a single equipment slot."""
    
    item_dropped = pyqtSignal(dict, EquipmentSlot)  # item, slot
    item_removed = pyqtSignal(EquipmentSlot)  # slot
    
    def __init__(self, slot: EquipmentSlot, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.slot = slot
        self.item = None
        
        self.setFixedSize(60, 60)
        self.setAcceptDrops(True)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the slot UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Slot icon/label
        self.slot_label = QLabel(self.slot.name.replace('_', ' ').title())
        self.slot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slot_label.setWordWrap(True)
        self.slot_label.setStyleSheet("""
            QLabel {
                background-color: #333333;
                border: 2px dashed #666666;
                border-radius: 4px;
                color: #888888;
                font-size: 8px;
                padding: 2px;
            }
        """)
        layout.addWidget(self.slot_label)
    
    def set_item(self, item: Dict[str, Any]):
        """Set the item in this slot."""
        self.item = item
        self.slot_label.setText(item.get('name', 'Unknown'))
        self.slot_label.setStyleSheet("""
            QLabel {
                background-color: #4a90e2;
                border: 2px solid #6ab0ff;
                border-radius: 4px;
                color: #ffffff;
                font-size: 8px;
                font-weight: bold;
                padding: 2px;
            }
        """)
    
    def clear_item(self):
        """Clear the item from this slot."""
        self.item = None
        self.slot_label.setText(self.slot.name.replace('_', ' ').title())
        self.slot_label.setStyleSheet("""
            QLabel {
                background-color: #333333;
                border: 2px dashed #666666;
                border-radius: 4px;
                color: #888888;
                font-size: 8px;
                padding: 2px;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        try:
            item_data = eval(event.mimeData().text())  # In real implementation, use JSON
            self.item_dropped.emit(item_data, self.slot)
            event.acceptProposedAction()
        except:
            event.ignore()
    
    def mousePressEvent(self, event):
        """Handle mouse press for item removal."""
        if event.button() == Qt.MouseButton.RightButton and self.item:
            self.item_removed.emit(self.slot)
