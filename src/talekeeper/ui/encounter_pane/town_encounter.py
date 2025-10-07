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
                            QListWidget, QListWidgetItem, QSpinBox, QSplitter, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List, Dict, Any
import sqlite3
import json
from talekeeper.services.level_up import LevelUpService
from talekeeper.services.equipment_database import EquipmentDatabase
from talekeeper.services.subclass_manager import SubclassManager
from talekeeper.services.shop_service import ShopService, ShopSize
from talekeeper.ui.encounter_pane.skill_selection_dialog import SkillSelectionDialog


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
        self.db_path = "talekeeper.db"
        self.selected_class = None
        print(f"[TrainingHall] Initializing for {character_data.get('name')} level {character_data.get('level')}")
        self.is_asi_level = False
        self.selected_feat = None
        self.asi_allocation = {'str': 0, 'dex': 0, 'con': 0, 'int': 0, 'wis': 0, 'cha': 0}
        self.available_asi_points = 0
        self.is_subclass_level = False
        self.selected_subclass = None
        self.is_expertise_level = False
        self.selected_expertise_skills = []
        
        self._setup_ui()
        self._update_training_info()
    
    def _setup_ui(self):
        """Setup the training hall interface"""
        # Create a scroll area for the training hall
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create the main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Main layout with reduced margins and spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(scroll_area)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("🏛️ TRAINING HALL")
        title_label.setObjectName("trainingTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Training info (remove unnecessary frame)
        self.training_info_label = QLabel()
        self.training_info_label.setObjectName("trainingInfo")
        self.training_info_label.setWordWrap(True)
        self.training_info_label.setStyleSheet("border: 1px solid #666; padding: 8px; background: #f5f5f5;")
        layout.addWidget(self.training_info_label)
        
        # Class selection (remove unnecessary frame)
        class_title = QLabel("Choose Class to Advance:")
        class_title.setObjectName("sectionTitle")
        class_title.setStyleSheet("font-weight: bold; margin-top: 5px;")
        layout.addWidget(class_title)
        
        # Radio buttons for class selection
        self.class_button_group = QButtonGroup()
        
        available_classes = self.level_up_service.get_available_classes()
        character_id = self.character_data.get('id', '')
        print(f"[DEBUG] Character data keys: {list(self.character_data.keys())}")
        print(f"[DEBUG] Character ID: '{character_id}'")
        current_classes = self.level_up_service.get_character_class_levels(character_id)
        print(f"[DEBUG] Current classes found: {current_classes}")
        
        for i, class_name in enumerate(available_classes):
            radio_btn = QRadioButton(class_name)
            # Case-insensitive lookup for current level
            current_level = 0
            for stored_class, level in current_classes.items():
                if stored_class.lower() == class_name.lower():
                    current_level = level
                    break
            
            if current_level > 0:
                radio_btn.setText(f"{class_name} (Level {current_level})")
                if len(current_classes) == 1:  # Auto-select if only one class
                    radio_btn.setChecked(True)
                    self.selected_class = class_name.lower()
                    # Store auto-selected class for later processing
                    self._auto_selected_class = class_name
            else:
                radio_btn.setText(f"{class_name} (New Class)")
            
            radio_btn.toggled.connect(lambda checked, cls=class_name: self._class_selected(cls, checked))
            self.class_button_group.addButton(radio_btn, i)
            layout.addWidget(radio_btn)
        
        # Features preview (remove unnecessary frame)
        features_title = QLabel("Features You'll Gain:")
        features_title.setObjectName("sectionTitle")
        features_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(features_title)
        
        self.features_list = QLabel()
        self.features_list.setObjectName("featuresList")
        self.features_list.setWordWrap(True)
        self.features_list.setStyleSheet("border: 1px solid #666; padding: 8px; background: #f9f9f9;")
        layout.addWidget(self.features_list)
        
        # Subclass selection frame (initially hidden)
        self.subclass_frame = QFrame()
        self.subclass_frame.setObjectName("subclassFrame")
        self.subclass_frame.hide()  # Hidden by default
        self._setup_subclass_selection()
        layout.addWidget(self.subclass_frame)
        
        # ASI/Feat selection frame (initially hidden)
        self.asi_feat_frame = QFrame()
        self.asi_feat_frame.setObjectName("asiFeatFrame")
        self.asi_feat_frame.hide()  # Hidden by default
        self._setup_asi_feat_selection()
        layout.addWidget(self.asi_feat_frame)

        # Expertise selection frame (initially hidden, for Rogue level 6)
        self.expertise_frame = QFrame()
        self.expertise_frame.setObjectName("expertiseFrame")
        self.expertise_frame.hide()  # Hidden by default
        self._setup_expertise_selection()
        layout.addWidget(self.expertise_frame)

        # Training button
        self.train_button = QPushButton("Begin Training")
        self.train_button.setObjectName("trainButton")
        print(f"[TrainingHall] Creating Begin Training button")
        self.train_button.clicked.connect(self._begin_training)
        layout.addWidget(self.train_button)
        print(f"[TrainingHall] Begin Training button added to layout")
        
        # Cancel button
        cancel_button = QPushButton("Leave Training Hall")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.training_completed.emit)
        layout.addWidget(cancel_button)
        
        # Process auto-selected class after all UI elements are created
        if hasattr(self, '_auto_selected_class'):
            print(f"[TrainingHall] Processing auto-selected class: {self._auto_selected_class}")
            self._class_selected(self._auto_selected_class, True)
    
    def _class_selected(self, class_name: str, checked: bool):
        """Handle class selection"""
        print(f"[Training] NEW VERSION: _class_selected called with {class_name}, {checked}")
        if checked:
            self.selected_class = class_name.lower()
            self.selected_subclass = None
            self.is_subclass_level = False
            print(f"[Training] Calling _check_subclass_level for class {class_name}")
            self._check_subclass_level()
            print(f"[Training] Completed subclass check, is_subclass_level: {self.is_subclass_level}")
            # Also check for ASI/feat eligibility
            print(f"[Training] Calling _check_asi_level for class {class_name}")
            self._check_asi_level()
            print(f"[Training] Completed ASI check, is_asi_level: {self.is_asi_level}")
            # Check for expertise eligibility (Rogue level 6)
            print(f"[Training] Calling _check_expertise_level for class {class_name}")
            self._check_expertise_level()
            print(f"[Training] Completed expertise check, is_expertise_level: {self.is_expertise_level}")
    def _check_asi_level(self):
        """Check if this is an ASI level and show/hide ASI selection"""
        if not self.selected_class:
            return
            
        character_id = self.character_data.get('id', '')
        current_level = self.character_data.get('level', 1)
        print(f"[Training] Checking ASI for {self.selected_class} at level {current_level} -> {current_level + 1}")
        
        self.is_asi_level = self.level_up_service.is_asi_level(character_id, self.selected_class)
        print(f"[Training] Is ASI level: {self.is_asi_level}")
        
        if self.is_asi_level:
            self.asi_feat_frame.show()
            self._update_points_remaining()  # Update button state
            print(f"[Training] Showing feat selection UI")
        else:
            self.asi_feat_frame.hide()
            print(f"[Training] No feat at this level")
        
        # Update train button state after checking ASI
        self._update_train_button_state()

    def _check_expertise_level(self):
        """Check if this is Rogue level 6 (expertise upgrade) and show/hide expertise selection"""
        if not self.selected_class:
            return

        current_level = self.character_data.get('level', 1)
        next_level = current_level + 1

        self.is_expertise_level = (self.selected_class.lower() == 'rogue' and current_level == 5 and next_level == 6)
        print(f"[Training] Is expertise level: {self.is_expertise_level} (Rogue {current_level} -> {next_level})")

        if self.is_expertise_level:
            self.expertise_frame.show()
            self._populate_expertise_options()
            print(f"[Training] Showing expertise selection UI")
        else:
            self.expertise_frame.hide()
            print(f"[Training] No expertise selection at this level")

        self._update_train_button_state()

    def _update_train_button_state(self):
        """Update train button state based on all conditions"""
        can_train = True
        reason = ""
        
        # Check if we have enough gold
        current_level = self.character_data.get('level', 1)
        next_level = current_level + 1
        current_gold = self._get_character_gold()
        cost_info = self._get_training_cost(next_level)
        
        if cost_info:
            cost, _ = cost_info
            if current_gold < cost:
                can_train = False
                reason = "Insufficient gold"
        else:
            can_train = False
            reason = "No training cost info"
        
        # Check if subclass selection is needed and made
        if self.is_subclass_level and not self.selected_subclass:
            can_train = False
            reason = "Must select subclass"
        
        # Check if ASI/feat selection is needed and made
        if self.is_asi_level:
            feat_data = self.feat_combo.currentData() if hasattr(self, 'feat_combo') else None
            if feat_data == "ASI":
                # Check if ASI points are properly allocated
                total_allocated = sum(self.asi_allocation.values())
                if total_allocated != 2:
                    can_train = False
                    reason = "Must allocate ASI points"
            elif not self.selected_feat:
                can_train = False
                reason = "Must select feat or ASI"

        # Check if expertise selection is needed and made
        if self.is_expertise_level:
            if len(self.selected_expertise_skills) != 2:
                can_train = False
                reason = "Must select 2 expertise skills"

        print(f"[Training] Train button state: {can_train} (reason: {reason})")
        self.train_button.setEnabled(can_train)
    
    def _check_subclass_level(self):
        """Check if this is the level for subclass selection."""
        if not self.selected_class:
            print(f"[Training] No selected class for subclass check")
            return
        character_id = self.character_data.get('id', '')
        current_classes = self.level_up_service.get_character_class_levels(character_id)
        current_class_level = current_classes.get(self.selected_class, 0)
        next_level = current_class_level + 1
        subclass_manager = SubclassManager()
        available_subclasses = subclass_manager.get_available_subclasses(self.selected_class)
        selection_level = 3
        if available_subclasses:
            selection_level = min((subclass.get('selection_level') or 3) for subclass in available_subclasses)
        existing_subclass = subclass_manager.get_character_subclass(character_id, self.selected_class)

        # Also check the enhanced subclass system
        if not existing_subclass:
            try:
                from talekeeper.services.enhanced_subclass_manager import EnhancedSubclassManager
                enhanced_manager = EnhancedSubclassManager(self.db_path)
                # Check if character has subclass in enhanced system
                import sqlite3
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT subclass_id FROM characters WHERE id = ?", (character_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        existing_subclass = row[0]
                        print(f"[Training] Found enhanced subclass: {existing_subclass}")
            except Exception as e:
                print(f"[Training] Could not check enhanced subclass system: {e}")
        print(f"[Training] Subclass check: selected_class='{self.selected_class}', current_level={current_class_level}, next_level={next_level}")
        print(f"[Training] Available classes: {current_classes}")
        print(f"[Training] Character ID: {character_id}")
        print(f"[Training] Existing subclass: {existing_subclass}")
        print(f"[Training] Selection level requirement: {selection_level}")
        if not available_subclasses:
            print(f"[Training] No subclasses defined for {self.selected_class}")
            self.is_subclass_level = False
            self.selected_subclass = None
            self.subclass_frame.hide()
            return
        if not existing_subclass and next_level >= selection_level:
            self.is_subclass_level = True
            print(f"[Training] Subclass selection required for {self.selected_class} level {next_level}")
            self.subclass_frame.show()
            self._populate_subclass_options()
            print(f"[Training] Subclass frame visible: {self.subclass_frame.isVisible()}")
            print(f"[Training] Subclass button count: {len(self.subclass_button_group.buttons())}")
            return
        self.is_subclass_level = False
        self.selected_subclass = None
        self.subclass_frame.hide()
    def _setup_subclass_selection(self):
        """Setup the subclass selection UI."""
        layout = QVBoxLayout(self.subclass_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Choose Your Subclass")
        title.setObjectName("subclassTitle")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #d4af37;")
        layout.addWidget(title)
        
        # Subclass radio buttons container
        self.subclass_button_group = QButtonGroup()
        self.subclass_options_widget = QWidget()
        self.subclass_options_layout = QVBoxLayout(self.subclass_options_widget)
        layout.addWidget(self.subclass_options_widget)
        
        # Description area
        self.subclass_description = QLabel()
        self.subclass_description.setWordWrap(True)
        self.subclass_description.setStyleSheet("border: 1px solid #666; padding: 8px; background: #f0f0f0; min-height: 60px;")
        layout.addWidget(self.subclass_description)
    
    def _populate_subclass_options(self):
        """Populate subclass options based on selected class."""
        # Clear existing options
        for button in self.subclass_button_group.buttons():
            self.subclass_button_group.removeButton(button)
            button.deleteLater()
        
        # Clear layout
        while self.subclass_options_layout.count():
            item = self.subclass_options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.selected_subclass = None
        self.subclass_description.clear()
        
        if not self.selected_class:
            return
        
        # Get available subclasses
        subclass_manager = SubclassManager()
        subclasses = subclass_manager.get_available_subclasses(self.selected_class)
        
        for i, subclass in enumerate(subclasses):
            radio = QRadioButton(subclass['name'])
            radio.toggled.connect(lambda checked, sc=subclass: self._subclass_selected(sc, checked))
            self.subclass_button_group.addButton(radio, i)
            self.subclass_options_layout.addWidget(radio)
        
        if subclasses:
            # Select first option by default
            self.subclass_button_group.buttons()[0].setChecked(True)
    
    def _subclass_selected(self, subclass_data: Dict, checked: bool):
        """Handle subclass selection."""
        if checked:
            self.selected_subclass = subclass_data
            # Show description
            desc_text = f"{subclass_data['description']}\n\n{subclass_data.get('flavor_text', '')}"
            self.subclass_description.setText(desc_text)
            
            # Update training button state
            self._update_train_button_state()
    
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
        else:
            info_text = "❌ Training cost information not available."
        
        # Update train button state based on all conditions
        self._update_train_button_state()
        
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
        """Update the features preview based on selected class (simplified for training hall)"""
        # Features preview is handled by the static UI elements in training hall
        pass
    
    def _begin_training(self):
        """Begin the training process"""
        print(f"[Training] _begin_training called! selected_class={self.selected_class}")
        print(f"[Training] is_subclass_level={self.is_subclass_level}, selected_subclass={self.selected_subclass}")
        
        if not self.selected_class:
            QMessageBox.warning(self, "No Class Selected", 
                              "Please select a class to advance before beginning training.")
            return
        
        # Check if subclass selection is required but not selected
        if self.is_subclass_level and not self.selected_subclass:
            QMessageBox.warning(self, "No Subclass Selected",
                              "Please select a subclass before beginning training.")
            return

        # Check if expertise selection is required but not completed
        if self.is_expertise_level and len(self.selected_expertise_skills) != 2:
            QMessageBox.warning(self, "Expertise Selection Incomplete",
                              "Please select exactly 2 skills for Expertise before beginning training.")
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
        
        # Prepare advancement summary
        advancement_summary = f"Begin training in {self.selected_class}?\n\n"
        advancement_summary += f"Cost: {cost} gold\n"
        advancement_summary += f"Time: {days} days\n"
        advancement_summary += f"You will advance to level {current_level + 1}.\n\n"
        
        # Add subclass information if applicable
        if self.is_subclass_level and self.selected_subclass:
            advancement_summary += f"Subclass: {self.selected_subclass['name']}\n"
            advancement_summary += f"{self.selected_subclass['description']}\n\n"
        
        # Add ASI/Feat information if applicable
        if self.is_asi_level:
            feat_data = self.feat_combo.currentData()
            if feat_data == "ASI":
                asi_changes = [f"+{bonus} {ability.capitalize()}" for ability, bonus in self.asi_allocation.items() if bonus > 0]
                if asi_changes:
                    advancement_summary += f"Ability Score Improvements: {', '.join(asi_changes)}\n"
            elif self.selected_feat:
                advancement_summary += f"Feat: {self.selected_feat['name']}\n"

        # Add Expertise information if applicable
        if self.is_expertise_level:
            if self.selected_expertise_skills:
                advancement_summary += f"Additional Expertise: {', '.join(self.selected_expertise_skills)}\n"

        # Confirm training
        reply = QMessageBox.question(self, "Confirm Training", advancement_summary,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Perform the level up
            character_id = self.character_data.get('id', '')
            selected_subclass_id = None
            if self.is_subclass_level and self.selected_subclass:
                selected_subclass_id = self.selected_subclass['id']
            success = self.level_up_service.level_up_character(character_id, self.selected_class, selected_subclass_id)

            # Apply ASI/Feat choices if this is an ASI level
            if success and self.is_asi_level:
                feat_data = self.feat_combo.currentData()
                if feat_data == "ASI":
                    self._apply_asi_increases(character_id)
                elif self.selected_feat:
                    self._apply_feat_selection(character_id)

            # Apply Expertise selections if this is an expertise level
            if success and self.is_expertise_level:
                self._apply_expertise_selections(character_id)

            if success:
                # Deduct gold
                self._deduct_gold(character_id, cost)
                
                # Force reload the character from database to get updated stats
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'game_engine'):
                        game_engine = parent.game_engine
                        # Reload character directly by ID instead of relying on last_character_slot
                        updated_character = game_engine.get_character_by_id_sync(character_id)
                        if updated_character:
                            game_engine.current_character = updated_character
                            print(f"[Training] Reloaded character: {updated_character['name']} "
                                  f"level {updated_character['level']}, {updated_character['hit_points_max']} HP")
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
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
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
    
    def _setup_asi_feat_selection(self):
        """Setup ASI/feat selection interface for ASI levels"""
        layout = QVBoxLayout(self.asi_feat_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        asi_title = QLabel("🎯 FEAT SELECTION")
        asi_title.setObjectName("asiTitle")
        asi_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        asi_title.setStyleSheet("font-weight: bold; color: #c44; margin: 5px;")
        layout.addWidget(asi_title)
        
        # Feat selection dropdown
        feat_label = QLabel("Choose your advancement:")
        feat_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        layout.addWidget(feat_label)
        
        self.feat_combo = QComboBox()
        self.feat_combo.setObjectName("featCombo")
        
        # Add ASI as the first (default) option
        self.feat_combo.addItem("Ability Score Improvement (+2 points)", "ASI")
        
        # Add available feats (exclude boon feats - only available at level 19+)
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM feats WHERE name NOT LIKE '%Boon%' ORDER BY name")
            feats = cursor.fetchall()
            conn.close()
            
            for feat_name, feat_description in feats:
                # Truncate description for dropdown
                short_desc = feat_description[:80] + "..." if len(feat_description) > 80 else feat_description
                self.feat_combo.addItem(f"{feat_name} - {short_desc}", feat_name)
        except Exception as e:
            print(f"Error loading feats: {e}")
            # Add some default feats as fallback
            default_feats = [
                ("Tough", "+2 HP per level"),
                ("Alert", "Add proficiency bonus to initiative, advantage on initiative rolls (solo play)"),
                ("Lucky", "3 luck points per long rest")
            ]
            for feat_name, desc in default_feats:
                self.feat_combo.addItem(f"{feat_name} - {desc}", feat_name)
        
        self.feat_combo.currentTextChanged.connect(self._on_feat_selection_changed)
        layout.addWidget(self.feat_combo)
        
        # ASI allocation section (only shows when ASI is selected)
        self.asi_section = QFrame()
        self.asi_section.setStyleSheet("background: #e8f4f8; padding: 8px; border: 1px solid #4a90e2; border-radius: 4px;")
        asi_layout = QVBoxLayout(self.asi_section)
        asi_layout.setContentsMargins(5, 5, 5, 5)
        asi_layout.setSpacing(3)
        
        asi_info = QLabel("Distribute +2 points among your ability scores (no ability can exceed 20):")
        asi_info.setWordWrap(True)
        asi_info.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        asi_layout.addWidget(asi_info)
        
        # Create compact spinboxes for each ability score
        self.asi_spinboxes = {}
        abilities = [('strength', 'STR'), ('dexterity', 'DEX'), ('constitution', 'CON'), 
                    ('intelligence', 'INT'), ('wisdom', 'WIS'), ('charisma', 'CHA')]
        
        for ability, short_name in abilities:
            ability_layout = QHBoxLayout()
            
            current_score = self.character_data.get(ability, 10)
            label = QLabel(f"{short_name}: {current_score}")
            label.setMinimumWidth(60)
            ability_layout.addWidget(label)
            
            spinbox = QSpinBox()
            # Can allocate up to +2, but total ability score can't exceed 20
            max_increase = min(2, 20 - current_score)
            spinbox.setRange(0, max(0, max_increase))
            spinbox.setValue(0)
            spinbox.setMaximumWidth(50)
            spinbox.valueChanged.connect(self._on_asi_allocation_changed)
            ability_layout.addWidget(spinbox)
            
            ability_layout.addStretch()  # Push everything left
            self.asi_spinboxes[ability] = spinbox
            asi_layout.addLayout(ability_layout)
        
        # Points remaining label
        self.points_remaining_label = QLabel("Points remaining: 2")
        self.points_remaining_label.setStyleSheet("font-weight: bold; color: #c44;")
        asi_layout.addWidget(self.points_remaining_label)
        
        layout.addWidget(self.asi_section)
        
        # Initialize ASI tracking
        self.asi_allocation = {}
        self.selected_feat = None
        self.skilled_feat_skills = []
    
    def _on_feat_selection_changed(self, text):
        """Handle feat/ASI selection changes"""
        data = self.feat_combo.currentData()

        if data == "ASI":
            self.selected_feat = None
            self.asi_section.show()
            self._update_points_remaining()
        else:
            self.selected_feat = {"name": data} if data else None
            self.asi_section.hide()

            if self.selected_feat and self.selected_feat['name'] == 'Skilled':
                character_id = self.character_data.get('id', '')
                if character_id:
                    dialog = SkillSelectionDialog(character_id, num_skills=3, parent=self)
                    if dialog.exec() == dialog.DialogCode.Accepted:
                        self.skilled_feat_skills = dialog.get_selected_skills()
                        print(f"[Skilled Feat] Selected skills: {self.skilled_feat_skills}")
                    else:
                        self.feat_combo.setCurrentIndex(0)
                        self.selected_feat = None
                        self.skilled_feat_skills = []

            self._update_train_button_state()
    
    def _update_points_remaining(self):
        """Update the points remaining display and button state"""
        if hasattr(self, 'asi_spinboxes'):
            self._on_asi_allocation_changed()  # Reuse the same logic
    
    def _load_available_feats(self):
        """Load available feats from database"""
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description, category
                FROM feats
                ORDER BY
                    CASE
                        WHEN category = 'general' THEN 1
                        WHEN category = 'O' THEN 2
                        WHEN category = 'FS' THEN 3
                        ELSE 4
                    END,
                    name
            """)
            feats = cursor.fetchall()

            for feat_id, name, description, category in feats:
                category_label = ''
                if category == 'O':
                    category_label = ' (O)'
                elif category == 'FS':
                    category_label = ' (FS)'

                display_desc = description if description else 'No description available'
                short_desc = display_desc[:100] + '...' if len(display_desc) > 100 else display_desc

                display_name = f"{name}{category_label}"
                self.feat_combo.addItem(f"{display_name} - {short_desc}",
                                       {'id': feat_id, 'name': name, 'description': description})

            conn.close()
        except Exception as e:
            print(f"Error loading feats: {e}")
    
    
    def _setup_expertise_selection(self):
        """Setup expertise selection interface for Rogue level 6"""
        layout = QVBoxLayout(self.expertise_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        title = QLabel("Expertise Selection")
        title.setObjectName("expertiseTitle")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #d4af37;")
        layout.addWidget(title)

        desc = QLabel("Choose 2 additional skills to gain Expertise (double proficiency bonus):")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #ccc; margin-bottom: 5px;")
        layout.addWidget(desc)

        self.expertise_checkboxes = {}
        self.expertise_skills_widget = QWidget()
        self.expertise_skills_layout = QGridLayout(self.expertise_skills_widget)
        layout.addWidget(self.expertise_skills_widget)

        self.expertise_count_label = QLabel("Selected: 0 / 2")
        self.expertise_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        layout.addWidget(self.expertise_count_label)

    def _populate_expertise_options(self):
        """Populate expertise skill options for Rogue level 6"""
        for checkbox in self.expertise_checkboxes.values():
            checkbox.deleteLater()
        self.expertise_checkboxes.clear()

        character_id = self.character_data.get('id', '')
        if not character_id:
            return

        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT proficiency_name
                FROM character_proficiencies
                WHERE character_id = ? AND proficiency_type = 'skill'
            """, (character_id,))
            proficient_skills = [row['proficiency_name'] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT proficiency_name
                FROM character_proficiencies
                WHERE character_id = ? AND proficiency_type = 'skill_expertise'
            """, (character_id,))
            existing_expertise = [row['proficiency_name'] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT expertise_skills FROM rogue_features WHERE character_id = ?
            """, (character_id,))
            rogue_row = cursor.fetchone()
            if rogue_row and rogue_row['expertise_skills']:
                try:
                    rogue_expertise = json.loads(rogue_row['expertise_skills'])
                    if isinstance(rogue_expertise, list):
                        existing_expertise.extend(rogue_expertise)
                except (json.JSONDecodeError, TypeError):
                    pass

            conn.close()

            available_skills = [skill for skill in proficient_skills if skill not in existing_expertise]
            available_skills.sort()

            row, col = 0, 0
            for skill in available_skills:
                checkbox = QCheckBox(skill)
                checkbox.toggled.connect(lambda state, s=skill: self._on_expertise_skill_toggled(s, state))
                self.expertise_checkboxes[skill] = checkbox
                self.expertise_skills_layout.addWidget(checkbox, row, col)

                col += 1
                if col > 2:
                    col = 0
                    row += 1

        except Exception as e:
            print(f"[Expertise] Error loading skills: {e}")

    def _on_expertise_skill_toggled(self, skill_name: str, checked: bool):
        """Handle expertise skill checkbox toggle with selection limit"""
        selected_count = sum(1 for cb in self.expertise_checkboxes.values() if cb.isChecked())

        if hasattr(self, 'expertise_count_label'):
            self.expertise_count_label.setText(f"Selected: {selected_count} / 2")

            if selected_count == 2:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #28a745;")
            elif selected_count > 2:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #dc3545;")
            else:
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #4a9eff;")

        if selected_count > 2 and checked:
            checkbox = self.expertise_checkboxes[skill_name]
            checkbox.setChecked(False)
            selected_count = 2
            if hasattr(self, 'expertise_count_label'):
                self.expertise_count_label.setText(f"Selected: {selected_count} / 2")
                self.expertise_count_label.setStyleSheet("font-weight: bold; color: #28a745;")

        self.selected_expertise_skills = [skill for skill, cb in self.expertise_checkboxes.items() if cb.isChecked()]
        self._update_train_button_state()

    def _on_asi_allocation_changed(self):
        """Handle ASI point allocation changes"""
        # Calculate total points allocated
        total_allocated = sum(spinbox.value() for spinbox in self.asi_spinboxes.values())
        points_remaining = 2 - total_allocated

        # If over-allocated, adjust the sender spinbox
        if total_allocated > 2:
            sender = self.sender()
            if sender and isinstance(sender, QSpinBox):
                # Reduce the value by the excess amount
                excess = total_allocated - 2
                sender.setValue(sender.value() - excess)
                total_allocated = 2
                points_remaining = 0
        
        self.points_remaining_label.setText(f"Points remaining: {points_remaining}")
        
        # Update max values for all spinboxes based on remaining points
        for ability, spinbox in self.asi_spinboxes.items():
            current_score = self.character_data.get(ability, 10)
            current_allocation = spinbox.value()
            
            # Max increase is either remaining points + current allocation, or what gets us to 20
            remaining_plus_current = points_remaining + current_allocation
            max_for_ability = min(remaining_plus_current, 20 - current_score)
            spinbox.setMaximum(max(0, max_for_ability))
        
        # Update ASI allocation dictionary
        self.asi_allocation = {}
        for ability, spinbox in self.asi_spinboxes.items():
            if spinbox.value() > 0:
                self.asi_allocation[ability] = spinbox.value()
        
        # Update training button state
        self._update_train_button_state()
    
    
    def _on_feat_selected(self, feat_name):
        """Handle feat selection"""
        feat_data = self.feat_combo.currentData()
        if feat_data:
            self.selected_feat = feat_data
            self.feat_description.setText(feat_data['description'] or "No description available.")
            self.feat_description.show()
        else:
            self.selected_feat = None
            self.feat_description.hide()
        
        self._update_train_button_state()
    
    def _apply_asi_increases(self, character_id: str):
        """Apply ability score increases to character"""
        try:
            print(f"[ASI] Applying ASI increases: {self.asi_allocation}")
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Apply each ability score increase
            for ability, increase in self.asi_allocation.items():
                if increase > 0:
                    # Map full ability names to column names (ability names are already full names)
                    valid_abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
                    
                    if ability in valid_abilities:
                        cursor.execute(f"""
                            UPDATE characters 
                            SET {ability} = {ability} + ? 
                            WHERE id = ?
                        """, (increase, character_id))
                        
                        print(f"[ASI] Increased {ability} by {increase}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error applying ASI increases: {e}")
    
    def _apply_expertise_selections(self, character_id: str):
        """Apply expertise skill selections to character"""
        try:
            print(f"[Expertise] Applying expertise selections: {self.selected_expertise_skills}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for skill in self.selected_expertise_skills:
                cursor.execute("""
                    DELETE FROM character_proficiencies
                    WHERE character_id = ? AND proficiency_name = ?
                """, (character_id, skill))

                cursor.execute("""
                    INSERT INTO character_proficiencies
                    (character_id, proficiency_type, proficiency_name, source)
                    VALUES (?, 'skill_expertise', ?, 'feature')
                """, (character_id, skill))
                print(f"[Expertise] Added expertise: {skill}")

            conn.commit()
            conn.close()
            print(f"[Expertise] Successfully applied {len(self.selected_expertise_skills)} expertise selections")
        except Exception as e:
            print(f"[Expertise] Error applying expertise selections: {e}")

    def _apply_feat_selection(self, character_id: str):
        """Apply selected feat to character"""
        try:
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()

            if self.selected_feat['name'] == 'Skilled':
                cursor.execute("""
                    INSERT INTO character_feats (character_id, feat_name, feat_id, feat_source, level_acquired)
                    VALUES (?, ?, ?, 'level_up', ?)
                """, (character_id, self.selected_feat['name'], self.selected_feat['id'], self.character_data.get('level', 1) + 1))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO character_feats (character_id, feat_name, feat_id)
                    VALUES (?, ?, ?)
                """, (character_id, self.selected_feat['name'], self.selected_feat['id']))

            if self.selected_feat['name'] == 'Skilled' and self.skilled_feat_skills:
                for skill in self.skilled_feat_skills:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_proficiencies
                        (character_id, proficiency_type, proficiency_name, source)
                        VALUES (?, 'skill', ?, 'feat')
                    """, (character_id, skill))
                    print(f"[Skilled Feat] Added skill proficiency: {skill}")

            cursor.execute("""
                SELECT ability_score_increases FROM feats WHERE id = ?
            """, (self.selected_feat['id'],))

            result = cursor.fetchone()
            if result and result[0] and result[0] != '{}':
                try:
                    import json
                    bonuses = json.loads(result[0])

                    for ability, bonus in bonuses.items():
                        if bonus > 0:
                            ability_columns = {
                                'str': 'strength', 'strength': 'strength',
                                'dex': 'dexterity', 'dexterity': 'dexterity',
                                'con': 'constitution', 'constitution': 'constitution',
                                'int': 'intelligence', 'intelligence': 'intelligence',
                                'wis': 'wisdom', 'wisdom': 'wisdom',
                                'cha': 'charisma', 'charisma': 'charisma'
                            }

                            column_name = ability_columns.get(ability.lower())
                            if column_name:
                                cursor.execute(f"""
                                    UPDATE characters
                                    SET {column_name} = {column_name} + ?
                                    WHERE id = ?
                                """, (bonus, character_id))

                                print(f"[Feat] {self.selected_feat['name']} increased {column_name} by {bonus}")

                except json.JSONDecodeError:
                    print(f"Could not parse ability score increases for feat: {self.selected_feat['name']}")

            conn.commit()
            conn.close()

            print(f"[Feat] Applied feat: {self.selected_feat['name']}")

        except Exception as e:
            print(f"Error applying feat selection: {e}")


class ShopInterface(QWidget):
    """Shop interface for buying equipment and items"""
    shopping_completed = pyqtSignal()

    def __init__(self, character_data: Dict[str, Any], shop_size: ShopSize = ShopSize.MEDIUM, parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.shop_size = shop_size
        self.shop_service = ShopService()
        self.shop_inventory = []
        self.character_inventory = []
        self.character_gold = 0
        self.shop_mode = "buy"  # "buy" or "sell"

        self._load_shop_inventory()
        self._load_character_inventory()
        self._setup_ui()
        self._update_character_gold()
    
    def _load_shop_inventory(self):
        """Load shop inventory based on shop size"""
        try:
            self.shop_inventory = self.shop_service.generate_shop_inventory(self.shop_size)
            print(f"[Shop] Generated {len(self.shop_inventory)} items for {self.shop_size.size_name} shop (limit: {self.shop_size.gold_limit}gp)")
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
            
            equipment_db = EquipmentDatabase()
            equipment_lookup = equipment_db.get_equipment_lookup()

            self.character_inventory = []
            for item_name, item_type, quantity in inventory_items:
                if item_name in equipment_lookup:
                    item_data = equipment_lookup[item_name].copy()
                    item_data['quantity'] = quantity
                    sell_price_gp, sell_price_display = self.shop_service.calculate_sell_price(item_data.get('cost_gp', 0))
                    item_data['sell_price_gp'] = sell_price_gp
                    item_data['sell_price_display'] = sell_price_display
                    self.character_inventory.append(item_data)
                    
        except Exception as e:
            print(f"Error loading character inventory: {e}")
            self.character_inventory = []
    
    def _setup_ui(self):
        """Setup shop interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Title with shop size
        shop_size_names = {
            ShopSize.SMALL: "Small Shop",
            ShopSize.MEDIUM: "General Store",
            ShopSize.LARGE: "Grand Emporium"
        }
        title_text = f"🏪 {shop_size_names.get(self.shop_size, 'SHOP')}"
        title_label = QLabel(title_text)
        title_label.setObjectName("shopTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Shop info label
        info_label = QLabel(f"Max item price: {self.shop_size.gold_limit} GP | {len(self.shop_inventory)} items in stock")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(info_label)

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
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

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
        items_label.setObjectName("itemsLabel")
        left_layout.addWidget(items_label)
        
        self.items_list = QListWidget()
        self.items_list.currentRowChanged.connect(self._item_selected)
        left_layout.addWidget(self.items_list, stretch=1)
        
        splitter.addWidget(left_widget)
        
        # Right side - Item details and purchase
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        details_label = QLabel("Item Details:")
        right_layout.addWidget(details_label)
        
        self.item_details = QLabel("Select an item to see details")
        self.item_details.setObjectName("itemDetails")
        self.item_details.setWordWrap(True)
        self.item_details.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.addWidget(self.item_details, stretch=1)
        
        # Purchase controls
        purchase_layout = QVBoxLayout()
        purchase_layout.setContentsMargins(0, 0, 0, 0)
        purchase_layout.setSpacing(4)

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

        right_layout.addLayout(purchase_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
        # Shop mode buttons
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(6)

        self.buy_button = QPushButton("Buy Items")
        self.buy_button.setObjectName("buyModeButton")
        self.buy_button.setChecked(True)
        self.buy_button.clicked.connect(lambda: self._set_shop_mode("buy"))
        mode_layout.addWidget(self.buy_button)
        
        self.sell_button = QPushButton("Sell Items")
        self.sell_button.setObjectName("sellModeButton") 
        self.sell_button.clicked.connect(lambda: self._set_shop_mode("sell"))
        mode_layout.addWidget(self.sell_button)

        layout.addLayout(mode_layout)

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
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
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
            price_key = 'shop_price_display'
        else:
            items_to_show = self.character_inventory
            price_key = 'sell_price_display'

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
                item_widget = QListWidgetItem(f"{name} (x{quantity}) - {price} each")
            else:
                item_widget = QListWidgetItem(f"{name} - {price}")

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
            price_display = item.get('shop_price_display', '? gp')
            details_text += f"Price: {price_display}\n"
        else:
            price_display = item.get('sell_price_display', '? gp')
            quantity = item.get('quantity', 1)
            details_text += f"Sell Price: {price_display} each\n"
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
        from talekeeper.services.shop_service import format_currency
        current_item = self.items_list.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            quantity = self.quantity_spin.value()

            if self.shop_mode == "buy":
                price_gp = item_data['shop_price_gp']
                total_gp = price_gp * quantity
                total_display, _ = format_currency(total_gp)
                self.total_cost_label.setText(f"Total Cost: {total_display}")

                # Check if player can afford it
                if total_gp > self.character_gold:
                    self.total_cost_label.setText(f"Total Cost: {total_display} (Insufficient funds!)")
                    self.purchase_button.setEnabled(False)
                else:
                    self.purchase_button.setEnabled(True)
            else:
                price_gp = item_data['sell_price_gp']
                total_gp = price_gp * quantity
                total_display, _ = format_currency(total_gp)
                self.total_cost_label.setText(f"Total Value: {total_display}")
                self.purchase_button.setEnabled(True)
    
    def _handle_transaction(self):
        """Handle buying or selling transaction"""
        from talekeeper.services.shop_service import format_currency
        current_item = self.items_list.currentItem()
        if not current_item:
            return

        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        quantity = self.quantity_spin.value()
        item_name = item_data['name']

        if self.shop_mode == "buy":
            total_cost_gp = item_data['shop_price_gp'] * quantity
            total_cost_display, _ = format_currency(total_cost_gp)

            if total_cost_gp > self.character_gold:
                QMessageBox.warning(self, "Insufficient Funds",
                                  f"You need {total_cost_display} but only have {self.character_gold} GP.")
                return

            reply = QMessageBox.question(self, "Confirm Purchase",
                                       f"Purchase {quantity}x {item_name} for {total_cost_display}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self._add_item_to_inventory(item_data, quantity)
                if success:
                    self._deduct_gold(total_cost_gp)
                    self._update_character_gold()
                    self._update_total_cost()
                    QMessageBox.information(self, "Purchase Complete",
                                          f"Successfully purchased {quantity}x {item_name}!")
                else:
                    QMessageBox.critical(self, "Purchase Failed",
                                       "Failed to add item to inventory. Please try again.")
        else:
            total_value_gp = item_data['sell_price_gp'] * quantity
            total_value_display, _ = format_currency(total_value_gp)

            reply = QMessageBox.question(self, "Confirm Sale",
                                       f"Sell {quantity}x {item_name} for {total_value_display}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self._remove_item_from_inventory(item_data, quantity)
                if success:
                    self._add_gold(total_value_gp)
                    self._load_character_inventory()
                    self._update_character_gold()
                    self._populate_items_list()
                    QMessageBox.information(self, "Sale Complete",
                                          f"Successfully sold {quantity}x {item_name} for {total_value_display}!")

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
                    (character_id, item_name, item_type, quantity, equipped) 
                    VALUES (?, ?, ?, ?, 0)
                """, (character_id, item_data['name'], item_data['item_type'], quantity))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding item to inventory: {e}")
            return False
    
    def _deduct_gold(self, amount: float):
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
    
    def _add_gold(self, amount: float):
        """Add gold to character inventory"""
        try:
            character_id = self.character_data.get('id', '')
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            
            # Check if gold entry exists
            cursor.execute("""
                SELECT quantity FROM character_inventory 
                WHERE character_id = ? AND item_name = 'Gold Pieces' AND item_type IN ('treasure', 'currency')
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
                    (character_id, item_name, item_type, quantity, equipped) 
                    VALUES (?, 'Gold Pieces', 'treasure', ?, 0)
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
        print(f"[Town] Creating training hall interface for {self.character_data.get('name')}")
        training_widget = TrainingHallInterface(self.character_data, self)
        training_widget.training_completed.connect(self._training_completed)
        print(f"[Town] Training hall widget created, showing interface")
        
        # Replace current widget content with training interface
        # Clear current layout
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        layout.addWidget(training_widget)
    
    def _show_shop(self):
        """Show shop size selection dialog, then shop interface"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QRadioButton, QButtonGroup

        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Shop")
        dialog.setModal(True)
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        title = QLabel("Select shop size:")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        button_group = QButtonGroup(dialog)
        selected_size = [ShopSize.MEDIUM]

        small_radio = QRadioButton("Small Shop (max 20 GP items)")
        small_radio.setToolTip("10 + 1d10 common items under 20 GP")
        small_radio.toggled.connect(lambda checked: selected_size.__setitem__(0, ShopSize.SMALL) if checked else None)
        button_group.addButton(small_radio)
        layout.addWidget(small_radio)

        medium_radio = QRadioButton("General Store (max 200 GP items)")
        medium_radio.setToolTip("10 + 2d10 items under 200 GP")
        medium_radio.setChecked(True)
        medium_radio.toggled.connect(lambda checked: selected_size.__setitem__(0, ShopSize.MEDIUM) if checked else None)
        button_group.addButton(medium_radio)
        layout.addWidget(medium_radio)

        large_radio = QRadioButton("Grand Emporium (max 2000 GP items)")
        large_radio.setToolTip("10 + 3d10 items under 2000 GP")
        large_radio.toggled.connect(lambda checked: selected_size.__setitem__(0, ShopSize.LARGE) if checked else None)
        button_group.addButton(large_radio)
        layout.addWidget(large_radio)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Enter Shop")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        shop_widget = ShopInterface(self.character_data, selected_size[0], self)
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
        # Force refresh character sheet first
        main_window = self.parent()
        while main_window:
            if hasattr(main_window, 'game_engine') and main_window.game_engine.current_character:
                if hasattr(main_window, '_force_reload_character'):
                    main_window._force_reload_character()
                    print(f"[Training] Forced character reload after training")
                    self.character_data = main_window.game_engine.current_character
                    print(f"[Training] Updated character_data to level {self.character_data.get('level')}")
                break
            main_window = main_window.parent()

        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

        # Recreate the town interface with updated character data
        self._setup_ui()

        # Notify parent that character may have changed
        parent = self.parent()
        while parent:
            if hasattr(parent, 'refresh_character_data'):
                parent.refresh_character_data()
                break
            parent = parent.parent()
    
    def _leave_town(self):
        """Leave town and return to exploration"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'set_exploration_mode'):
                parent.set_exploration_mode()
                break
            parent = parent.parent()





