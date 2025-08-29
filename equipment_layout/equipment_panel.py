"""
Equipment Panel Widget - Expandable inventory and equipment display

PyQt6 widget that manages character equipment and inventory:
- Equipment slots (armor, weapons, accessories)
- Inventory grid with item management
- Expandable from 432px to 1080px width
- Drag & drop item management
- Item tooltips and details

Designed to match ui_plan.md specifications:
- Default size: 432x486
- Expanded size: 1080x486
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
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.expanded = False
        self.animation = None
        self.equipped_items = {}  # slot -> item mapping
        self.inventory_items = []  # list of inventory items
        self.character_strength = 10  # Default strength for carrying capacity
        self.character_dexterity = 10  # Default dexterity for AC calculation
        
        # Set initial size (extends to bottom of window)
        self.setFixedSize(432, 486)
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
        
        # Quick stats display (always visible)
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("statsFrame")
        stats_layout = QGridLayout(self.stats_frame)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        
        # AC, Damage, etc.
        stats_layout.addWidget(QLabel("AC:"), 0, 0)
        self.ac_label = QLabel("10")
        self.ac_label.setObjectName("statValue")
        stats_layout.addWidget(self.ac_label, 0, 1)
        
        stats_layout.addWidget(QLabel("ATK:"), 0, 2)
        self.attack_label = QLabel("+0")
        self.attack_label.setObjectName("statValue")
        stats_layout.addWidget(self.attack_label, 0, 3)
        
        equipment_layout.addWidget(self.stats_frame)
        
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
            EquipmentSlot.HELMET: (0, 1),
            EquipmentSlot.AMULET: (0, 2),
            EquipmentSlot.CLOAK: (1, 0),
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
        """Apply dark theme styling to equipment panel components."""
        style_sheet = """
        EquipmentPanel {
            background-color: #222222;
            border: 2px solid #555555;
            border-radius: 8px;
        }
        
        QFrame#headerFrame {
            background-color: #2a2a2a;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QFrame#statsFrame {
            background-color: #252525;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QFrame#equipmentSlotsFrame {
            background-color: #1e1e1e;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QLabel#titleLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
        }
        
        QLabel#statValue {
            color: #4a90e2;
            font-size: 12px;
            font-weight: bold;
        }
        
        QLabel#weightLabel {
            color: #cccccc;
            font-size: 11px;
            min-width: 50px;
        }
        
        QPushButton#expandButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 3px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 10px;
        }
        
        QPushButton#expandButton:hover {
            background-color: #505050;
        }
        
        QPushButton#smallButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 3px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
            min-width: 40px;
        }
        
        QPushButton#smallButton:hover {
            background-color: #505050;
        }
        
        QPushButton#smallButton:pressed {
            background-color: #303030;
        }
        
        QTabWidget#contentTabs {
            background-color: transparent;
        }
        
        QTabWidget#contentTabs::pane {
            border: 1px solid #444444;
            border-radius: 4px;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2a2a2a;
            color: #cccccc;
            border: 1px solid #444444;
            border-bottom: none;
            border-radius: 3px 3px 0px 0px;
            padding: 4px 8px;
            margin: 1px;
            font-size: 10px;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #ffffff;
            border-bottom: 1px solid #1e1e1e;
        }
        
        QTabBar::tab:hover {
            background-color: #3a3a3a;
        }
        
        QListWidget#inventoryList {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            alternate-background-color: #222222;
        }
        
        QListWidget#inventoryList::item {
            padding: 4px;
            border-bottom: 1px solid #333333;
        }
        
        QListWidget#inventoryList::item:selected {
            background-color: #4a90e2;
            color: #ffffff;
        }
        
        QListWidget#inventoryList::item:hover {
            background-color: #2a2a2a;
        }
        
        QProgressBar#weightBar {
            border: 1px solid #666666;
            border-radius: 3px;
            text-align: center;
            background-color: #1a1a1a;
            height: 16px;
        }
        
        QProgressBar#weightBar::chunk {
            background-color: #4a9;
            border-radius: 2px;
        }
        
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 5px;
            min-height: 15px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        """
        self.setStyleSheet(style_sheet)
    
    def _toggle_expansion(self):
        """Toggle the panel expansion - expands leftward to cover encounter pane."""
        # Toggle expansion state
        self.expanded = not self.expanded
        
        if self.expanded:
            # EXPAND: Move left and resize to cover encounter pane
            current_pos = self.pos()
            # Move left by the difference in width (1080 - 432 = 648)
            new_x = current_pos.x() - (1080 - 432)
            self.move(new_x, current_pos.y())
            
            self.setFixedSize(1080, 472)
            self.expand_btn.setText("▲ Collapse")
            self.raise_()  # Bring to front to cover encounter pane
            
            # Switch to expanded layout
            self._switch_to_expanded_layout()
        else:
            # COLLAPSE: Move right and resize back to normal position
            current_pos = self.pos()
            # Move right by the difference in width (1080 - 432 = 648)
            new_x = current_pos.x() + (1080 - 432)
            self.move(new_x, current_pos.y())
            
            self.setFixedSize(432, 472)
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
        
        # Emit signal
        self.item_equipped.emit(item, slot)
        self.inventory_changed.emit()
    
    def _unequip_item(self, slot: EquipmentSlot):
        """Unequip an item from a slot."""
        if slot in self.equipped_items:
            item = self.equipped_items.pop(slot)
            self.inventory_items.append(item)
            self.slot_widgets[slot].clear_item()
            
            # Update displays
            self._update_inventory_display()
            self._update_stats_display()
            
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
                # Use/consume the item
                item = item_data['item']
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
            item_type = item.get('type', '')
            slot_name = slot.value.replace('_', ' ').title()
            
            display_text = f"⚔️ {item_name} [Equipped - {slot_name}]"
            if item_type:
                display_text += f" ({item_type})"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, {'item': item, 'equipped': True, 'slot': slot})
            self.inventory_list.addItem(list_item)
        
        # Add unequipped inventory items
        for item in self.inventory_items:
            item_name = item.get('name', 'Unknown Item')
            item_type = item.get('type', '')
            quantity = item.get('quantity', 1)
            
            display_text = f"{item_name}"
            if quantity > 1:
                display_text += f" ({quantity})"
            if item_type:
                display_text += f" [{item_type}]"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, {'item': item, 'equipped': False, 'slot': None})
            self.inventory_list.addItem(list_item)
        
        # Update weight - include both equipped and unequipped items
        equipped_weight = sum(item.get('weight_lb', 0) for item in self.equipped_items.values())
        inventory_weight = sum(item.get('weight_lb', 0) * item.get('quantity', 1) 
                              for item in self.inventory_items)
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
        weight_percentage = int(min(100, (total_weight / max_weight) * 100))
        self.weight_bar.setValue(weight_percentage)
        self.weight_label.setText(f"{total_weight:.1f}/{max_weight} lb{encumbrance_status}")
    
    def _update_stats_display(self):
        """Update the stats display based on equipped items."""
        # Calculate AC using D&D 2024 rules
        ac = self._calculate_armor_class()
        
        # Calculate attack bonus from main hand weapon
        attack_bonus = self._calculate_main_hand_attack_bonus()
        
        self.ac_label.setText(str(ac))
        self.attack_label.setText(f"+{attack_bonus}" if attack_bonus >= 0 else str(attack_bonus))
    
    def _calculate_armor_class(self):
        """Calculate total AC from equipped armor, shield, and dexterity."""
        base_ac = 10
        dex_mod = (self.character_dexterity - 10) // 2
        
        # Find equipped armor
        armor = None
        for slot, item in self.equipped_items.items():
            if slot == EquipmentSlot.ARMOR and item.get('armor_properties'):
                armor = item
                break
        
        if armor:
            armor_props = armor.get('armor_properties', {})
            base_ac = armor_props.get('armor_class', 10)
            armor_type = armor_props.get('armor_type', 'light')
            dex_max = armor_props.get('dex_bonus_max')
            
            # Apply Dex modifier based on armor type
            if armor_type == 'light':
                # Light armor: full Dex modifier
                ac = base_ac + dex_mod
            elif armor_type == 'medium':
                # Medium armor: Dex modifier capped at +2 (or dex_bonus_max)
                max_dex = dex_max if dex_max is not None else 2
                ac = base_ac + min(dex_mod, max_dex)
            else:  # heavy armor
                # Heavy armor: no Dex modifier (unless dex_bonus_max specified)
                if dex_max is not None:
                    ac = base_ac + min(dex_mod, dex_max)
                else:
                    ac = base_ac
        else:
            # No armor: 10 + Dex modifier
            ac = base_ac + dex_mod
        
        # Add shield AC if equipped
        shield = None
        for slot, item in self.equipped_items.items():
            if slot == EquipmentSlot.OFF_HAND and item.get('item_type') == 'shield':
                shield = item
                break
        
        if shield:
            shield_ac = shield.get('armor_class', 0)
            ac += shield_ac
        
        return max(ac, 1)  # AC can't be less than 1
    
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
    
    def load_equipment_data(self, equipped_items: Dict[str, Any], inventory_items: List[Dict[str, Any]], character_strength: int = 10, character_dexterity: int = 10):
        """Load equipment and inventory data."""
        # Store character's stats for calculations
        self.character_strength = character_strength
        self.character_dexterity = character_dexterity
        
        # Load equipped items
        self.equipped_items.clear()
        for slot_name, item in equipped_items.items():
            try:
                slot = EquipmentSlot(slot_name)
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
        """Get currently equipped items."""
        return {slot.value: item for slot, item in self.equipped_items.items()}
    
    def get_inventory_items(self) -> List[Dict[str, Any]]:
        """Get inventory items."""
        return self.inventory_items.copy()
    
    def is_expanded(self) -> bool:
        """Return current expansion state."""
        return self.expanded


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