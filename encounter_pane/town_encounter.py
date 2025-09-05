"""
Town Encounter System - Training Hall and Town Services

Provides town-based encounters including:
- Training Hall (level up when sufficient XP)
- Shop (equipment and supplies)
- Inn (rest and lodging)
- Quest Board (future implementation)

Integrates with the encounter panel tab system.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QGridLayout,
                            QComboBox, QRadioButton, QButtonGroup, QMessageBox,
                            QListWidget, QListWidgetItem, QSpinBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any
import sqlite3
import json
from services.level_up import LevelUpService


class TownEncounterCard(QFrame):
    """Base class for town encounter cards (training hall, shop, inn, etc.)"""
    card_activated = pyqtSignal(str)  # Emit card type when clicked
    
    def __init__(self, card_type: str, icon: str, title: str, description: str, enabled: bool = True):
        super().__init__()
        self.card_type = card_type
        self.enabled = enabled
        
        self.setObjectName("townCard")
        self.setFixedSize(180, 120)
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Icon and title
        icon_title_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        
        icon_title_layout.addWidget(icon_label)
        icon_title_layout.addWidget(title_label, 1)
        layout.addLayout(icon_title_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(desc_label, 1)
        
        # Status styling with better readability
        if not enabled:
            self.setEnabled(False)
            self.setStyleSheet("""
                TownEncounterCard {
                    color: #999;
                    background-color: #2a2a2a;
                    border: 2px solid #444;
                    border-radius: 8px;
                }
                QLabel#cardIcon {
                    color: #666;
                    font-size: 24px;
                    font-weight: bold;
                }
                QLabel#cardTitle {
                    color: #999;
                    font-size: 14px;
                    font-weight: bold;
                }
                QLabel#cardDescription {
                    color: #777;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                TownEncounterCard {
                    color: #ffffff;
                    background-color: #3a3a3a;
                    border: 2px solid #555;
                    border-radius: 8px;
                }
                TownEncounterCard:hover {
                    border-color: #4a90e2;
                    background-color: #404040;
                }
                QLabel#cardIcon {
                    color: #ffcc00;
                    font-size: 24px;
                    font-weight: bold;
                }
                QLabel#cardTitle {
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                }
                QLabel#cardDescription {
                    color: #cccccc;
                    font-size: 12px;
                }
            """)
    
    def mousePressEvent(self, event):
        if self.enabled and event.button() == Qt.MouseButton.LeftButton:
            self.card_activated.emit(self.card_type)


class TrainingHallInterface(QWidget):
    """Training hall interface for leveling up characters"""
    training_completed = pyqtSignal()  # Signal when training is complete
    
    def __init__(self, character_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.level_up_service = LevelUpService()
        self.selected_class = None
        
        self._setup_ui()
        self._update_training_info()
    
    def _setup_ui(self):
        """Setup the training hall interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🏛️ TRAINING HALL")
        title_label.setObjectName("trainingTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Training info frame
        self.info_frame = QFrame()
        self.info_frame.setObjectName("trainingInfoFrame")
        info_layout = QVBoxLayout(self.info_frame)
        
        self.training_info_label = QLabel()
        self.training_info_label.setObjectName("trainingInfo")
        self.training_info_label.setWordWrap(True)
        info_layout.addWidget(self.training_info_label)
        
        layout.addWidget(self.info_frame)
        
        # Class selection (for multiclassing)
        self.class_selection_frame = QFrame()
        self.class_selection_frame.setObjectName("classSelectionFrame")
        class_layout = QVBoxLayout(self.class_selection_frame)
        
        class_title = QLabel("Choose Class to Advance:")
        class_title.setObjectName("sectionTitle")
        class_layout.addWidget(class_title)
        
        # Radio buttons for class selection
        self.class_button_group = QButtonGroup()
        self.class_buttons_layout = QVBoxLayout()
        
        available_classes = self.level_up_service.get_available_classes()
        character_id = self.character_data.get('id', '')
        print(f"[DEBUG] Character data keys: {list(self.character_data.keys())}")
        print(f"[DEBUG] Character ID: '{character_id}'")
        current_classes = self.level_up_service.get_character_class_levels(character_id)
        print(f"[DEBUG] Current classes found: {current_classes}")
        
        for i, class_name in enumerate(available_classes):
            radio_btn = QRadioButton(class_name)
            current_level = current_classes.get(class_name, 0)
            if current_level > 0:
                radio_btn.setText(f"{class_name} (Level {current_level})")
                if len(current_classes) == 1:  # Auto-select if only one class
                    radio_btn.setChecked(True)
                    self.selected_class = class_name
            else:
                radio_btn.setText(f"{class_name} (New Class)")
            
            radio_btn.toggled.connect(lambda checked, cls=class_name: self._class_selected(cls, checked))
            self.class_button_group.addButton(radio_btn, i)
            self.class_buttons_layout.addWidget(radio_btn)
        
        class_layout.addLayout(self.class_buttons_layout)
        layout.addWidget(self.class_selection_frame)
        
        # Features preview
        self.features_frame = QFrame()
        self.features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(self.features_frame)
        
        features_title = QLabel("Features You'll Gain:")
        features_title.setObjectName("sectionTitle")
        features_layout.addWidget(features_title)
        
        self.features_list = QLabel()
        self.features_list.setObjectName("featuresList")
        self.features_list.setWordWrap(True)
        features_layout.addWidget(self.features_list)
        
        layout.addWidget(self.features_frame)
        
        # Training button
        self.train_button = QPushButton("Begin Training")
        self.train_button.setObjectName("trainButton")
        self.train_button.clicked.connect(self._begin_training)
        layout.addWidget(self.train_button)
        
        # Cancel button
        cancel_button = QPushButton("Leave Training Hall")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.training_completed.emit)
        layout.addWidget(cancel_button)
    
    def _class_selected(self, class_name: str, checked: bool):
        """Handle class selection"""
        if checked:
            self.selected_class = class_name
            try:
                self._update_features_preview()
            except Exception as e:
                print(f"Error updating features preview: {e}")
                # Show fallback message
                self.features_list.setText(f"Features will be available when advancing {class_name}.")
    
    def _update_training_info(self):
        """Update training information display"""
        current_level = self.character_data.get('level', 1)
        next_level = current_level + 1
        current_xp = self.character_data.get('experience_points', 0)
        current_gold = self._get_character_gold()
        
        # Get training cost from database
        cost_info = self._get_training_cost(next_level)
        
        if cost_info:
            cost, days = cost_info
            info_text = f"""Training Available: Level {current_level} → Level {next_level}
Current XP: {current_xp:,}
Cost: {cost} gold pieces
Training Time: {days} days
Your Gold: {current_gold:,}

Training includes food and lodging (counts as a long rest)."""
            
            if current_gold < cost:
                info_text += f"\n\n❌ Insufficient funds! Need {cost - current_gold} more gold."
                self.train_button.setEnabled(False)
            else:
                self.train_button.setEnabled(True)
        else:
            info_text = "❌ Training cost information not available."
            self.train_button.setEnabled(False)
        
        self.training_info_label.setText(info_text)
    
    def _get_training_cost(self, target_level: int) -> Optional[tuple]:
        """Get training cost and days for target level"""
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT training_cost_gp, training_days 
                FROM levelup_costs 
                WHERE ? BETWEEN level_range_start AND level_range_end
            """, (target_level,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0], result[1]  # cost, days
            return None
            
        except Exception as e:
            print(f"Error getting training cost: {e}")
            return None
    
    def _update_features_preview(self):
        """Update the features preview based on selected class"""
        try:
            if not self.selected_class:
                self.features_list.setText("Select a class to see available features.")
                return
            
            character_id = self.character_data.get('id', '')
            if not character_id:
                self.features_list.setText("Character ID not available.")
                return
            
            features = self.level_up_service.get_next_level_features(character_id, self.selected_class)
            
            if features:
                features_text = "\n".join([f"• {feat['name']}: {feat['description']}" for feat in features])
            else:
                features_text = "No specific features at this level (general improvements apply)."
            
            self.features_list.setText(features_text)
            
        except Exception as e:
            print(f"Error in _update_features_preview: {e}")
            self.features_list.setText(f"Unable to load features for {self.selected_class}.")
    
    def _begin_training(self):
        """Begin the training process"""
        if not self.selected_class:
            QMessageBox.warning(self, "No Class Selected", 
                              "Please select a class to advance before beginning training.")
            return
        
        current_level = self.character_data.get('level', 1)
        cost_info = self._get_training_cost(current_level + 1)
        
        if not cost_info:
            QMessageBox.critical(self, "Training Error", "Unable to determine training cost.")
            return
        
        cost, days = cost_info
        current_gold = self._get_character_gold()
        
        if current_gold < cost:
            QMessageBox.warning(self, "Insufficient Funds", 
                              f"You need {cost} gold pieces but only have {current_gold}.")
            return
        
        # Confirm training
        reply = QMessageBox.question(self, "Confirm Training",
                                   f"Begin training in {self.selected_class}?\n\n"
                                   f"Cost: {cost} gold\n"
                                   f"Time: {days} days\n"
                                   f"You will advance to level {current_level + 1}.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Perform the level up
            character_id = self.character_data.get('id', '')
            success = self.level_up_service.level_up_character(character_id, self.selected_class)
            
            if success:
                # Deduct gold
                self._deduct_gold(character_id, cost)
                
                # Force reload the character from database to get updated stats
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'game_engine'):
                        # Find the character's save slot and reload
                        game_engine = parent.game_engine
                        if hasattr(game_engine, 'settings') and 'last_character_slot' in game_engine.settings:
                            slot = game_engine.settings['last_character_slot']
                            updated_character = game_engine.load_character_sync(slot)
                            if updated_character:
                                game_engine.current_character = updated_character
                                print(f"[Training] Reloaded character: {updated_character['name']} level {updated_character['level']}, {updated_character['hit_points_max']} HP")
                        break
                    parent = parent.parent()
                
                QMessageBox.information(self, "Training Complete!",
                                      f"Congratulations! You are now level {current_level + 1}!\n\n"
                                      f"Training took {days} days and you feel refreshed (full rest).")
                self.training_completed.emit()
            else:
                QMessageBox.critical(self, "Training Failed", 
                                   "An error occurred during training. Please try again.")
    
    def _get_character_gold(self) -> int:
        """Get character's current gold from inventory"""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                return 0
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
            """, (character_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"Error getting character gold: {e}")
            return 0
    
    def _deduct_gold(self, character_id: str, amount: int):
        """Deduct gold from character inventory"""
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Update gold quantity in inventory
            cursor.execute("""
                UPDATE character_inventory 
                SET quantity = quantity - ?
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
            """, (amount, character_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error deducting gold: {e}")


class ShopInterface(QWidget):
    """Shop interface for buying equipment and items"""
    shopping_completed = pyqtSignal()
    
    def __init__(self, character_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.shop_inventory = []
        self.character_inventory = []
        self.character_gold = 0
        self.shop_mode = "buy"  # "buy" or "sell"
        
        self._load_shop_inventory()
        self._load_character_inventory()
        self._setup_ui()
        self._update_character_gold()
    
    def _load_shop_inventory(self):
        """Load shop inventory from equipment data"""
        try:
            with open('data/equipment.json', 'r') as f:
                equipment_data = json.load(f)
                
            # Filter items that would be available in a general store
            # Exclude rare/magical items, include basic equipment
            for item in equipment_data:
                rarity = item.get('rarity', 'common').lower()
                if rarity in ['common', 'uncommon']:
                    # Add markup for shop prices (25% increase)
                    shop_price = int(item.get('cost_gp', 0) * 1.25)
                    if shop_price > 0:  # Only items with a cost
                        shop_item = item.copy()
                        shop_item['shop_price'] = shop_price
                        self.shop_inventory.append(shop_item)
                        
        except Exception as e:
            print(f"Error loading shop inventory: {e}")
            self.shop_inventory = []
    
    def _load_character_inventory(self):
        """Load character's sellable inventory items"""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                return
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT item_name, item_type, quantity 
                FROM character_inventory 
                WHERE character_id = ? AND item_type != 'treasure' AND quantity > 0
            """, (character_id,))
            
            inventory_items = cursor.fetchall()
            conn.close()
            
            # Load equipment data to get item details and prices
            with open('data/equipment.json', 'r') as f:
                equipment_data = json.load(f)
            
            # Create lookup for equipment details
            equipment_lookup = {item['name']: item for item in equipment_data}
            
            self.character_inventory = []
            for item_name, item_type, quantity in inventory_items:
                if item_name in equipment_lookup:
                    item_data = equipment_lookup[item_name].copy()
                    item_data['quantity'] = quantity
                    # Calculate sell price (50% of original cost)
                    sell_price = int(item_data.get('cost_gp', 0) * 0.5)
                    item_data['sell_price'] = max(sell_price, 1)  # Minimum 1 GP
                    self.character_inventory.append(item_data)
                    
        except Exception as e:
            print(f"Error loading character inventory: {e}")
            self.character_inventory = []
    
    def _setup_ui(self):
        """Setup shop interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🏪 GENERAL STORE")
        title_label.setObjectName("shopTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Gold display
        self.gold_label = QLabel()
        self.gold_label.setObjectName("goldDisplay") 
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gold_label)
        
        # Splitter for shop categories and item details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Item categories and list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Category filter
        category_label = QLabel("Category:")
        left_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Items")
        self.category_combo.addItem("Weapons")
        self.category_combo.addItem("Armor")
        self.category_combo.addItem("Adventuring Gear")
        self.category_combo.currentTextChanged.connect(self._filter_items)
        left_layout.addWidget(self.category_combo)
        
        # Items list
        items_label = QLabel("Available Items:")
        left_layout.addWidget(items_label)
        
        self.items_list = QListWidget()
        self.items_list.currentRowChanged.connect(self._item_selected)
        left_layout.addWidget(self.items_list)
        
        splitter.addWidget(left_widget)
        
        # Right side - Item details and purchase
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_label = QLabel("Item Details:")
        right_layout.addWidget(details_label)
        
        self.item_details = QLabel("Select an item to see details")
        self.item_details.setObjectName("itemDetails")
        self.item_details.setWordWrap(True)
        self.item_details.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.addWidget(self.item_details)
        
        # Purchase controls
        purchase_frame = QFrame()
        purchase_layout = QVBoxLayout(purchase_frame)
        
        # Quantity selector
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self._update_total_cost)
        qty_layout.addWidget(self.quantity_spin)
        qty_layout.addStretch()
        purchase_layout.addLayout(qty_layout)
        
        # Total cost
        self.total_cost_label = QLabel()
        self.total_cost_label.setObjectName("totalCost")
        purchase_layout.addWidget(self.total_cost_label)
        
        # Purchase/Sell button
        self.purchase_button = QPushButton("Purchase Item")
        self.purchase_button.setObjectName("purchaseButton")
        self.purchase_button.clicked.connect(self._handle_transaction)
        self.purchase_button.setEnabled(False)
        purchase_layout.addWidget(self.purchase_button)
        
        right_layout.addWidget(purchase_frame)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
        # Shop mode buttons
        mode_frame = QFrame()
        mode_layout = QHBoxLayout(mode_frame)
        
        self.buy_button = QPushButton("Buy Items")
        self.buy_button.setObjectName("buyModeButton")
        self.buy_button.setChecked(True)
        self.buy_button.clicked.connect(lambda: self._set_shop_mode("buy"))
        mode_layout.addWidget(self.buy_button)
        
        self.sell_button = QPushButton("Sell Items")
        self.sell_button.setObjectName("sellModeButton") 
        self.sell_button.clicked.connect(lambda: self._set_shop_mode("sell"))
        mode_layout.addWidget(self.sell_button)
        
        layout.addWidget(mode_frame)
        
        # Exit shop button
        exit_button = QPushButton("Leave Shop")
        exit_button.setObjectName("exitShopButton")
        exit_button.clicked.connect(self.shopping_completed.emit)
        layout.addWidget(exit_button)
        
        # Populate items list
        self._populate_items_list()
    
    def _set_shop_mode(self, mode: str):
        """Set shop mode (buy or sell)"""
        self.shop_mode = mode
        
        # Update button states
        self.buy_button.setChecked(mode == "buy")
        self.sell_button.setChecked(mode == "sell")
        
        # Update interface labels
        if mode == "buy":
            self.category_combo.setVisible(True)
            self.purchase_button.setText("Purchase Item")
            items_label = self.findChild(QLabel, "itemsLabel") 
            if items_label:
                items_label.setText("Available Items:")
        else:
            self.category_combo.setVisible(False)
            self.purchase_button.setText("Sell Item")
            items_label = self.findChild(QLabel, "itemsLabel")
            if items_label:
                items_label.setText("Your Items:")
        
        # Refresh items list
        self._populate_items_list()
        
        # Clear selection
        self.items_list.clearSelection()
        self.item_details.setText("Select an item to see details")
        self.purchase_button.setEnabled(False)
    
    def _update_character_gold(self):
        """Update display of character's gold"""
        self.character_gold = self._get_character_gold()
        self.gold_label.setText(f"💰 Your Gold: {self.character_gold:,} GP")
    
    def _get_character_gold(self) -> int:
        """Get character's current gold"""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                return 0
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
            """, (character_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"Error getting character gold: {e}")
            return 0
    
    def _populate_items_list(self, category_filter="All Items"):
        """Populate items list based on mode and category filter"""
        self.items_list.clear()
        
        if self.shop_mode == "buy":
            items_to_show = self.shop_inventory
            price_key = 'shop_price'
        else:
            items_to_show = self.character_inventory
            price_key = 'sell_price'
        
        for item in items_to_show:
            # Apply category filter (only in buy mode)
            if self.shop_mode == "buy" and category_filter != "All Items":
                item_type = item.get('item_type', '').lower()
                if category_filter == "Weapons" and item_type != "weapon":
                    continue
                elif category_filter == "Armor" and item_type != "armor":
                    continue
                elif category_filter == "Adventuring Gear" and item_type not in ["gear", "tool", "adventuring_gear"]:
                    continue
            
            # Create list item
            name = item['name']
            price = item[price_key]
            
            if self.shop_mode == "sell":
                quantity = item.get('quantity', 1)
                item_widget = QListWidgetItem(f"{name} (x{quantity}) - {price} GP each")
            else:
                item_widget = QListWidgetItem(f"{name} - {price} GP")
            
            item_widget.setData(Qt.ItemDataRole.UserRole, item)
            self.items_list.addItem(item_widget)
    
    def _filter_items(self, category: str):
        """Filter items by category"""
        self._populate_items_list(category)
        self.item_details.setText("Select an item to see details")
        self.purchase_button.setEnabled(False)
    
    def _item_selected(self, row: int):
        """Handle item selection"""
        if row < 0:
            return
            
        item_widget = self.items_list.item(row)
        if not item_widget:
            return
            
        item_data = item_widget.data(Qt.ItemDataRole.UserRole)
        self._display_item_details(item_data)
        
        # Set quantity limits based on mode
        if self.shop_mode == "sell":
            max_qty = item_data.get('quantity', 1)
            self.quantity_spin.setMaximum(max_qty)
            self.quantity_spin.setValue(min(1, max_qty))
        else:
            self.quantity_spin.setMaximum(99)
            self.quantity_spin.setValue(1)
        
        self._update_total_cost()
        self.purchase_button.setEnabled(True)
    
    def _display_item_details(self, item: Dict[str, Any]):
        """Display detailed information about selected item"""
        name = item['name']
        description = item.get('description', 'No description available')
        weight = item.get('weight_lb', 0)
        rarity = item.get('rarity', 'common').title()
        
        details_text = f"**{name}**\n\n"
        details_text += f"{description}\n\n"
        
        if self.shop_mode == "buy":
            price = item['shop_price']
            details_text += f"Price: {price} GP\n"
        else:
            price = item['sell_price']
            quantity = item.get('quantity', 1)
            details_text += f"Sell Price: {price} GP each\n"
            details_text += f"You have: {quantity}\n"
        
        details_text += f"Weight: {weight} lb\n"
        details_text += f"Rarity: {rarity}\n"
        
        # Add weapon/armor specific details
        if item.get('item_type') == 'weapon':
            damage = item.get('damage_dice', 'N/A')
            damage_type = item.get('damage_type', 'N/A')
            properties = ', '.join(item.get('weapon_properties', []))
            mastery = item.get('weapon_mastery', 'None')
            
            details_text += f"\nDamage: {damage} {damage_type}\n"
            if properties:
                details_text += f"Properties: {properties}\n"
            details_text += f"Mastery: {mastery}\n"
            
        elif item.get('item_type') == 'armor':
            ac = item.get('armor_class', 'N/A')
            armor_type = item.get('armor_type', 'N/A')
            
            details_text += f"\nAC: {ac}\n"
            details_text += f"Type: {armor_type}\n"
        
        self.item_details.setText(details_text)
    
    def _update_total_cost(self):
        """Update total cost display"""
        current_item = self.items_list.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            quantity = self.quantity_spin.value()
            
            if self.shop_mode == "buy":
                price = item_data['shop_price']
                total = price * quantity
                self.total_cost_label.setText(f"Total Cost: {total} GP")
                
                # Check if player can afford it
                if total > self.character_gold:
                    self.total_cost_label.setText(f"Total Cost: {total} GP (Insufficient funds!)")
                    self.purchase_button.setEnabled(False)
                else:
                    self.purchase_button.setEnabled(True)
            else:  # sell mode
                price = item_data['sell_price']
                total = price * quantity
                self.total_cost_label.setText(f"Total Value: {total} GP")
                self.purchase_button.setEnabled(True)
    
    def _handle_transaction(self):
        """Handle buying or selling transaction"""
        current_item = self.items_list.currentItem()
        if not current_item:
            return
            
        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        quantity = self.quantity_spin.value()
        item_name = item_data['name']
        
        if self.shop_mode == "buy":
            total_cost = item_data['shop_price'] * quantity
            
            if total_cost > self.character_gold:
                QMessageBox.warning(self, "Insufficient Funds", 
                                  f"You need {total_cost} GP but only have {self.character_gold} GP.")
                return
            
            # Confirm purchase
            reply = QMessageBox.question(self, "Confirm Purchase",
                                       f"Purchase {quantity}x {item_name} for {total_cost} GP?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self._add_item_to_inventory(item_data, quantity)
                if success:
                    self._deduct_gold(total_cost)
                    self._update_character_gold()
                    self._update_total_cost()
                    QMessageBox.information(self, "Purchase Complete", 
                                          f"Successfully purchased {quantity}x {item_name}!")
                else:
                    QMessageBox.critical(self, "Purchase Failed", 
                                       "Failed to add item to inventory. Please try again.")
        else:  # sell mode
            total_value = item_data['sell_price'] * quantity
            
            # Confirm sale
            reply = QMessageBox.question(self, "Confirm Sale",
                                       f"Sell {quantity}x {item_name} for {total_value} GP?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self._remove_item_from_inventory(item_data, quantity)
                if success:
                    self._add_gold(total_value)
                    self._load_character_inventory()  # Refresh inventory
                    self._update_character_gold()
                    self._populate_items_list()  # Refresh item list
                    QMessageBox.information(self, "Sale Complete", 
                                          f"Successfully sold {quantity}x {item_name} for {total_value} GP!")
                    
                    # Clear selection if item is no longer available
                    if quantity >= item_data.get('quantity', 1):
                        self.items_list.clearSelection()
                        self.item_details.setText("Select an item to see details")
                        self.purchase_button.setEnabled(False)
                else:
                    QMessageBox.critical(self, "Sale Failed", 
                                       "Failed to remove item from inventory. Please try again.")
    
    def _add_item_to_inventory(self, item_data: Dict[str, Any], quantity: int) -> bool:
        """Add purchased item to character inventory"""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                return False
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Check if item already exists in inventory
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = ? AND item_type = ?
            """, (character_id, item_data['name'], item_data['item_type']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing quantity
                new_quantity = existing[0] + quantity
                cursor.execute("""
                    UPDATE character_inventory 
                    SET quantity = ?
                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                """, (new_quantity, character_id, item_data['name'], item_data['item_type']))
            else:
                # Add new item
                cursor.execute("""
                    INSERT INTO character_inventory 
                    (character_id, item_name, item_type, quantity, is_equipped, equipment_slot) 
                    VALUES (?, ?, ?, ?, 0, NULL)
                """, (character_id, item_data['name'], item_data['item_type'], quantity))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding item to inventory: {e}")
            return False
    
    def _deduct_gold(self, amount: int):
        """Deduct gold from character inventory"""
        try:
            character_id = self.character_data.get('id', '')
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE character_inventory 
                SET quantity = quantity - ?
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
            """, (amount, character_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error deducting gold: {e}")
    
    def _add_gold(self, amount: int):
        """Add gold to character inventory"""
        try:
            character_id = self.character_data.get('id', '')
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Check if gold entry exists
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
            """, (character_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing gold
                cursor.execute("""
                    UPDATE character_inventory 
                    SET quantity = quantity + ?
                    WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type = 'treasure'
                """, (amount, character_id))
            else:
                # Create new gold entry
                cursor.execute("""
                    INSERT INTO character_inventory 
                    (character_id, item_name, item_type, quantity, is_equipped, equipment_slot) 
                    VALUES (?, 'Gold Pieces', 'treasure', ?, 0, NULL)
                """, (character_id, amount))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error adding gold: {e}")
    
    def _remove_item_from_inventory(self, item_data: Dict[str, Any], quantity: int) -> bool:
        """Remove item from character inventory"""
        try:
            character_id = self.character_data.get('id', '')
            if not character_id:
                return False
            
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Get current quantity
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = ? AND item_type = ?
            """, (character_id, item_data['name'], item_data['item_type']))
            
            result = cursor.fetchone()
            if not result or result[0] < quantity:
                conn.close()
                return False
            
            current_quantity = result[0]
            new_quantity = current_quantity - quantity
            
            if new_quantity <= 0:
                # Remove item entirely
                cursor.execute("""
                    DELETE FROM character_inventory 
                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                """, (character_id, item_data['name'], item_data['item_type']))
            else:
                # Update quantity
                cursor.execute("""
                    UPDATE character_inventory 
                    SET quantity = ?
                    WHERE character_id = ? AND item_name = ? AND item_type = ?
                """, (new_quantity, character_id, item_data['name'], item_data['item_type']))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error removing item from inventory: {e}")
            return False


class TownEncounterPanel(QWidget):
    """Main town encounter panel with cards for different services"""
    
    def __init__(self, character_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the town encounter interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🏘️ Town Services")
        title_label.setObjectName("townTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Cards grid
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        cards_layout = QGridLayout(scroll_widget)
        cards_layout.setSpacing(15)
        
        # Training Hall Card
        can_level_up = self._can_character_level_up()
        training_desc = "Level up your character\nwith proper training" if can_level_up else "Training not available\n(insufficient XP)"
        
        training_card = TownEncounterCard("training", "🏛️", "Training Hall", training_desc, can_level_up)
        training_card.card_activated.connect(self._handle_card_activation)
        cards_layout.addWidget(training_card, 0, 0)
        
        # Shop Card 
        shop_card = TownEncounterCard("shop", "🏪", "General Store", "Buy equipment,\nsupplies and items", True)
        shop_card.card_activated.connect(self._handle_card_activation)
        cards_layout.addWidget(shop_card, 0, 1)
        
        # Inn Card (dummy)
        inn_card = TownEncounterCard("inn", "🏨", "The Resting Dragon Inn", "Rest, meals, and\nlocal information", False)
        inn_card.card_activated.connect(self._handle_card_activation)
        cards_layout.addWidget(inn_card, 1, 0)
        
        # Quest Board Card (dummy)
        quest_card = TownEncounterCard("quests", "📋", "Quest Board", "Available jobs\nand adventures", False)
        quest_card.card_activated.connect(self._handle_card_activation)
        cards_layout.addWidget(quest_card, 1, 1)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Leave town button
        leave_button = QPushButton("Leave Town")
        leave_button.setObjectName("leaveTownButton")
        leave_button.clicked.connect(self._leave_town)
        layout.addWidget(leave_button)
    
    def _can_character_level_up(self) -> bool:
        """Check if character has enough XP to level up"""
        current_level = self.character_data.get('level', 1)
        current_xp = self.character_data.get('experience_points', 0)
        
        # XP thresholds for each level
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
            100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        if current_level >= 20:
            return False  # Max level reached
        
        next_level_xp = xp_thresholds[current_level] if current_level < len(xp_thresholds) else xp_thresholds[-1]
        return current_xp >= next_level_xp
    
    def _handle_card_activation(self, card_type: str):
        """Handle clicking on a town card"""
        if card_type == "training":
            self._show_training_hall()
        elif card_type == "shop":
            self._show_shop()
        elif card_type == "inn":
            QMessageBox.information(self, "Coming Soon", "The inn services are not yet implemented.")
        elif card_type == "quests":
            QMessageBox.information(self, "Coming Soon", "The quest board is not yet implemented.")
    
    def _show_training_hall(self):
        """Show the training hall interface"""
        training_widget = TrainingHallInterface(self.character_data, self)
        training_widget.training_completed.connect(self._training_completed)
        
        # Replace current widget content with training interface
        # Clear current layout
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        layout.addWidget(training_widget)
    
    def _show_shop(self):
        """Show the shop interface"""
        shop_widget = ShopInterface(self.character_data, self)
        shop_widget.shopping_completed.connect(self._shopping_completed)
        
        # Replace current widget content with shop interface
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        layout.addWidget(shop_widget)
    
    def _shopping_completed(self):
        """Handle shopping completion - refresh the town panel"""
        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
        
        # Recreate the town interface
        self._setup_ui()
        
        # Force refresh inventory/equipment panels
        parent = self.parent()
        while parent:
            if hasattr(parent, '_force_reload_character'):
                parent._force_reload_character()
                break
            parent = parent.parent()
    
    def _training_completed(self):
        """Handle training completion - refresh the town panel"""
        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
        
        # Recreate the town interface
        self._setup_ui()
        
        # Notify parent that character may have changed
        parent = self.parent()
        while parent:
            if hasattr(parent, 'refresh_character_data'):
                parent.refresh_character_data()
                break
            parent = parent.parent()
        
        # Force refresh character sheet
        main_window = parent
        while main_window:
            if hasattr(main_window, 'character_sheet'):
                # Reload character data into character sheet
                if hasattr(main_window, 'game_engine') and main_window.game_engine.current_character:
                    # Force reload character by calling the main window's force reload method
                    if hasattr(main_window, '_force_reload_character'):
                        main_window._force_reload_character()
                        print(f"[Training] Forced character reload after training")
                    else:
                        print(f"[Training] Force reload method not found")
                break
            main_window = main_window.parent()
    
    def _leave_town(self):
        """Leave town and return to exploration"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'set_exploration_mode'):
                parent.set_exploration_mode()
                break
            parent = parent.parent()