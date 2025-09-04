"""
Main Application Window for TaleKeeper Desktop

PyQt6-based main window integrating all game UI components in fixed positions.
Coordinates character management, exploration, combat, and inventory systems.

UI Components:
- Game menu (top-left): Character/save management  
- Character panel (left): Stats and character information
- Encounter panel (center): Exploration and combat interface
- Log panel (top-right): System messages and event logs
- Equipment panel (bottom-right): Inventory and equipment management
- Action panel (bottom-left): Combat actions and abilities

Features:
- Light/dark theme switching
- Auto-load last played character
- Signal-based component communication
- Character creation integration
- Save/load game state management
"""

import sys
import os
from typing import Dict, List
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QSplitter, QMenuBar, QMenu, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from ui.themes import build_stylesheet, get_theme_palette
from menu.game_menu import GameMenu
from character_sheet.character_panel import CharacterPanel
from encounter_pane.encounter_panel import EncounterPanel
from log.log_panel import LogPanel
from equipment_layout.equipment_panel import EquipmentPanel
from action_cards.action_panel import ActionPanel
from core.game_engine_sqlite import GameEngineSQLite


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        self.setMinimumSize(1920, 1080)
        
        # Initialize game engine
        self.game_engine = GameEngineSQLite()
        
        # Theme management
        self.current_theme = "light"  # Default to light theme
        
        # === CENTRAL WIDGET ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins - fill full height
        
        self._setup_menu_bar()
        self._setup_ui()
        self._apply_theme(self.current_theme)
        self._connect_signals()
        
        # Try to load last character immediately on startup
        self._try_load_last_character()
    
    def _setup_ui(self):
        """Setup fixed position UI layout - no splitters, no animations"""
        
        # 5% margins: 96px on each side, 54px top/bottom
        # Usable area: 1728x972
        
        # === FIXED POSITION WIDGETS ===
        
        # Menu (top left)
        self.menu = GameMenu(self)
        self.menu.move(96, 54)  # Top left with 5% margin
        self.menu.show()
        self.menu.raise_()
        
        # Character sheet (below menu, left column)  
        self.character_sheet = CharacterPanel(self)
        self.character_sheet.move(96, 54 + 90)  # Below menu, moved up more to reduce gap
        self.character_sheet.show()
        
        # Encounter pane (center, full height)
        self.encounter_pane = EncounterPanel(self) 
        self.encounter_pane.move(96 + 648, 54)  # Center column
        self.encounter_pane.show()
        
        # Log panel (top right)
        self.log_panel = LogPanel(self)
        self.log_panel.move(96 + 648 + 648, 54)  # Right column
        self.log_panel.show()
        
        # Equipment panel (bottom right)
        self.equipment_panel = EquipmentPanel(self)
        self.equipment_panel.move(96 + 648 + 648, 54 + 486)  # Below log
        self.equipment_panel.show()
        
        # Action cards (bottom left)
        self.action_panel = ActionPanel(self)
        self.action_panel.move(96, 1080 - 54 - 300)  # Bottom left
        self.action_panel.show()
        self.action_panel.raise_()
        
        # Theme toggle button (top right, near log panel)
        self.theme_toggle_button = QPushButton("[MOON] Dark", self)  # Start with moon for switching to dark
        self.theme_toggle_button.setGeometry(96 + 648 + 648 - 100, 20, 90, 30)  # Top right, above log panel
        self.theme_toggle_button.clicked.connect(self._toggle_theme)
        self.theme_toggle_button.setToolTip("Toggle between Light and Dark themes (Ctrl+T)")
        self.theme_toggle_button.show()
        self.theme_toggle_button.raise_()
    
    def _setup_menu_bar(self):
        """Setup menu bar with theme toggle."""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Theme submenu
        theme_menu = view_menu.addMenu('Theme')
        
        # Light theme action
        light_action = QAction('Light Theme', self)
        light_action.setShortcut(QKeySequence('Ctrl+1'))
        light_action.triggered.connect(lambda: self._apply_theme('light'))
        theme_menu.addAction(light_action)
        
        # Dark theme action
        dark_action = QAction('Dark Theme', self)
        dark_action.setShortcut(QKeySequence('Ctrl+2'))
        dark_action.triggered.connect(lambda: self._apply_theme('dark'))
        theme_menu.addAction(dark_action)
        
        # Theme toggle action
        toggle_action = QAction('Toggle Theme', self)
        toggle_action.setShortcut(QKeySequence('Ctrl+T'))
        toggle_action.triggered.connect(self._toggle_theme)
        theme_menu.addAction(toggle_action)
    
    def _apply_theme(self, theme_name: str):
        """Apply the specified theme to the main window and all child widgets.
        
        Args:
            theme_name: Name of the theme to apply ('light' or 'dark')
        """
        try:
            palette = get_theme_palette(theme_name)
            stylesheet = build_stylesheet(palette)
            self.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            
            # Update panel themes
            if hasattr(self, 'action_panel'):
                self.action_panel.update_theme(theme_name)
            if hasattr(self, 'equipment_panel'):
                self.equipment_panel.update_theme(theme_name)
            if hasattr(self, 'log_panel'):
                self.log_panel.update_theme(theme_name)
            if hasattr(self, 'encounter_panel'):
                self.encounter_panel.update_theme(theme_name)
            
            # Update toggle button text/icon based on current theme
            if hasattr(self, 'theme_toggle_button'):
                if theme_name == 'light':
                    self.theme_toggle_button.setText("[MOON] Dark")  # Moon icon to switch to dark
                else:
                    self.theme_toggle_button.setText("☀️ Light")  # Sun icon to switch to light
                    
        except ValueError as e:
            # Log error and fall back to light theme
            print(f"Theme error: {e}. Falling back to light theme.")
            if theme_name != 'light':
                self._apply_theme('light')
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self._apply_theme(new_theme)
    
    def _connect_signals(self):
        """Connect all widget signals"""
        
        # Menu signals
        self.menu.create_character_requested.connect(self._start_character_creation)
        self.menu.load_game_requested.connect(self._show_load_character_dialog)
        self.menu.save_and_exit_requested.connect(self._save_and_exit)
        self.menu.force_reload_requested.connect(self._force_reload_character)
        self.menu.settings_requested.connect(lambda: self.log_panel.log_info("Settings requested"))
        self.menu.campaign_frame_requested.connect(lambda: self.log_panel.log_info("Campaign Frame requested"))
        
        # Character sheet signals
        self.character_sheet.expansion_changed.connect(
            lambda expanded: self.log_panel.log_system(f"Character sheet {'expanded' if expanded else 'collapsed'}")
        )
        self.character_sheet.character_action_requested.connect(
            lambda action: self.log_panel.log_info(f"Character action: {action}")
        )
        
        # Encounter pane signals
        self.encounter_pane.encounter_action_requested.connect(
            lambda action: self.log_panel.log_combat(f"Encounter action: {action}")
        )
        self.encounter_pane.exploration_action.connect(
            lambda action: self.log_panel.log_info(f"Exploration: {action}")
        )
        self.encounter_pane.monster_selected.connect(
            lambda monster_id: self._on_monster_selected(monster_id)
        )
        
        # Equipment panel signals
        self.equipment_panel.expansion_changed.connect(
            lambda expanded: self.log_panel.log_system(f"Equipment panel {'expanded' if expanded else 'collapsed'}")
        )
        self.equipment_panel.item_used.connect(
            lambda item: self.log_panel.log_info(f"Used item: {item.get('name', 'Unknown')}")
        )
        # Equipment change signals - update action panel when weapons/items are equipped/unequipped
        # NOTE: When spell system is added, spell changes will need similar handling for magic actions
        self.equipment_panel.item_equipped.connect(self._on_item_equipped)
        self.equipment_panel.item_unequipped.connect(self._on_item_unequipped)
        self.equipment_panel.ac_changed.connect(self._on_ac_changed)
        self.equipment_panel.inventory_changed.connect(self._on_inventory_changed)
        
        # Action panel signals
        self.action_panel.action_triggered.connect(
            lambda action, context: self.log_panel.log_combat(f"Action: {action.value} - {context.get('name', '')}")
        )
        
        # Encounter pane character creation signal
        self.encounter_pane.character_created.connect(self._on_character_created)
    
    def _on_monster_selected(self, monster_id: str):
        """Handle monster selection for targeting."""
        # Pass the selected monster to the action panel for targeting
        if hasattr(self.action_panel, 'set_target_monster'):
            self.action_panel.set_target_monster(monster_id)
        
        # Get monster info for logging
        selected_monster = self.encounter_pane.get_selected_monster()
        if selected_monster:
            self.log_panel.log_combat(f"Selected target: {selected_monster.monster_name}")
    
    def _on_item_equipped(self, item, slot):
        """Handle item equipped - update database and recalculate AC."""
        if not hasattr(self, 'game_engine') or not self.game_engine.current_character:
            return
        
        # Update equipment in database
        equipped_items = self.equipment_panel.get_equipped_items_dict()
        self._update_character_equipment_slots(equipped_items)
        
        # Recalculate AC from database (includes Defense fighting style)
        character_id = self.game_engine.current_character['id']
        if self.game_engine.recalculate_character_stats_sync(character_id):
            # Get the new AC from the database 
            updated_character = self.game_engine.load_character_sync(self.game_engine.current_character['save_slot_number'])
            if updated_character:
                new_ac = updated_character['armor_class']
                self.log_panel.log_info(f"AC updated to {new_ac}")
                self.log_panel.log_info(f"Equipped {item.get('name', 'item')} in {slot} slot")
                
                # Update character sheet display with correct AC from database
                if hasattr(self, 'character_sheet') and self.character_sheet.character_data:
                    self.character_sheet.update_ac(new_ac)
                    self.character_sheet.character_data['armor_class'] = new_ac
        
        # Get current character stats for action panel
        character_data = self.character_sheet.character_data
        character_stats = {
            'strength': character_data.get('strength', 10),
            'dexterity': character_data.get('dexterity', 10),
            'constitution': character_data.get('constitution', 10),
            'intelligence': character_data.get('intelligence', 10),
            'wisdom': character_data.get('wisdom', 10),
            'charisma': character_data.get('charisma', 10),
            'armor_class': new_ac if 'new_ac' in locals() else character_data.get('armor_class', 10),
            'level': character_data.get('level', 1)
        }
        
        # Update action panel with new equipment
        equipped_items = self.equipment_panel.get_equipped_items_dict()
        self.action_panel.load_character_equipment(equipped_items, character_stats)
        
        # Update database character equipment slots
        self._update_character_equipment_slots(equipped_items)
        
        # Log the equipment change
        item_name = item.get('name', 'Unknown Item')
        self.log_panel.log_info(f"Equipped {item_name} in {slot.value} slot")
    
    def _on_item_unequipped(self, slot):
        """Handle item unequipped - update database and recalculate AC."""
        if not hasattr(self, 'game_engine') or not self.game_engine.current_character:
            return
        
        # Update equipment in database
        equipped_items = self.equipment_panel.get_equipped_items_dict()
        self._update_character_equipment_slots(equipped_items)
        
        # Recalculate AC from database (includes Defense fighting style)
        character_id = self.game_engine.current_character['id']
        if self.game_engine.recalculate_character_stats_sync(character_id):
            # Get the new AC from the database 
            updated_character = self.game_engine.load_character_sync(self.game_engine.current_character['save_slot_number'])
            if updated_character:
                new_ac = updated_character['armor_class']
                self.log_panel.log_info(f"AC updated to {new_ac}")
                self.log_panel.log_info(f"Unequipped item from {slot} slot")
                
                # Update character sheet display with correct AC from database
                if hasattr(self, 'character_sheet') and self.character_sheet.character_data:
                    self.character_sheet.update_ac(new_ac)
                    self.character_sheet.character_data['armor_class'] = new_ac
        
        # Get current character stats for action panel  
        character_data = self.character_sheet.character_data
        character_stats = {
            'strength': character_data.get('strength', 10),
            'dexterity': character_data.get('dexterity', 10),
            'constitution': character_data.get('constitution', 10),
            'intelligence': character_data.get('intelligence', 10),
            'wisdom': character_data.get('wisdom', 10),
            'charisma': character_data.get('charisma', 10),
            'armor_class': new_ac if 'new_ac' in locals() else character_data.get('armor_class', 10),
            'level': character_data.get('level', 1)
        }
        
        # Update action panel with new equipment
        equipped_items = self.equipment_panel.get_equipped_items_dict()
        self.action_panel.load_character_equipment(equipped_items, character_stats)
        
        # Update database character equipment slots
        self._update_character_equipment_slots(equipped_items)
        
        # Log the equipment change
        self.log_panel.log_info(f"Unequipped item from {slot.value} slot")
    
    def _on_ac_changed(self, new_ac):
        """Handle AC change from equipment panel - update character sheet display."""
        # Update the character sheet display with new AC
        if hasattr(self, 'character_sheet') and self.character_sheet.character_data:
            self.character_sheet.update_ac(new_ac)
            
            # Also update the character data in memory and database
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                # Update character data in memory
                self.character_sheet.character_data['armor_class'] = new_ac
                
                # Update database via game engine (which will trigger proper AC recalculation)
                try:
                    character_id = self.game_engine.current_character['id']
                    # Force recalculation of character stats including AC
                    if self.game_engine.recalculate_character_stats_sync(character_id):
                        self.log_panel.log_info(f"AC updated to {new_ac}")
                    else:
                        self.log_panel.log_error("Failed to recalculate character stats")
                except Exception as e:
                    self.log_panel.log_error(f"Failed to update AC in database: {e}")
    
    def _on_inventory_changed(self):
        """Handle inventory changes - save equipment and inventory to database."""
        try:
            if not hasattr(self, 'game_engine') or not hasattr(self.game_engine, 'current_character'):
                return
                
            current_character = getattr(self.game_engine, 'current_character', None)
            if not current_character:
                return
                
            # Get current equipped items and inventory from the equipment panel
            equipped_items = self.equipment_panel.get_equipped_items_dict()
            inventory_items = self.equipment_panel.get_inventory_items()
            
            # Update equipped slots in character record
            self._update_character_equipment_slots(equipped_items)
            
            # Save inventory changes to database
            self._save_character_inventory(current_character['id'], inventory_items)
            
        except Exception as e:
            self.log_panel.log_error(f"Failed to save inventory changes: {e}")
    
    def _update_character_equipment_slots(self, equipped_items: dict):
        """Update the current character's equipment slots in the database."""
        if not hasattr(self, 'game_engine') or not hasattr(self.game_engine, 'current_character'):
            return
            
        current_character = getattr(self.game_engine, 'current_character', None)
        if not current_character:
            return
            
        # Map equipment slots to character fields
        main_hand_item = equipped_items.get('main_hand')
        off_hand_item = equipped_items.get('off_hand')
        armor_item = equipped_items.get('armor')
        
        main_hand_name = main_hand_item.get('name') if main_hand_item else None
        off_hand_name = off_hand_item.get('name') if off_hand_item else None
        armor_name = armor_item.get('name') if armor_item else None
        
        # Update database
        import sqlite3
        try:
            conn = sqlite3.connect(self.game_engine.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE characters 
                SET equipment_main_hand = ?, equipment_off_hand = ?, equipment_armor = ?
                WHERE id = ?
            """, (main_hand_name, off_hand_name, armor_name, current_character['id']))
            
            conn.commit()
            conn.close()
            
            # Update the current character DTO as well
            current_character['equipment_main_hand'] = main_hand_name
            current_character['equipment_off_hand'] = off_hand_name  
            current_character['equipment_armor'] = armor_name
            
        except Exception as e:
            print(f"Error updating character equipment slots: {e}")
    
    def _save_character_inventory(self, character_id: str, inventory_items: list):
        """Save character's inventory to the database, replacing all existing items."""
        try:
            import sqlite3
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()
            
            # Clear existing inventory items for this character
            cursor.execute("DELETE FROM character_inventory WHERE character_id = ?", (character_id,))
            
            # Insert current inventory items
            for item in inventory_items:
                import uuid
                item_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    character_id,
                    item.get('name', 'Unknown Item'),
                    item.get('type', 'miscellaneous'),
                    item.get('quantity', 1),
                    item.get('weight_lb', 0.0),
                    item.get('description', ''),
                    item.get('value_gp', 0)
                ))
            
            conn.commit()
            conn.close()
            print(f"[MainWindow] Saved {len(inventory_items)} inventory items for character {character_id}")
            
        except Exception as e:
            print(f"Error saving character inventory: {e}")
    
    def load_test_data(self):
        """Load demo data into all widgets - only used when no saved characters exist"""
        self.log_panel.log_system("Loading demo data for testing...")
        
        # Load demo character - make it clear this is temporary
        demo_character = {
            'name': 'Demo Adventurer',
            'level': 1,
            'race_name': 'Human',
            'class_name': 'Fighter',
            'current_hit_points': 10,
            'hit_points': 10,
            'armor_class': 12,
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 12,
            'wisdom': 11,
            'charisma': 10,
            'experience_points': 0,
            'speed': 30,
            'background_name': 'Folk Hero'
        }
        
        self.character_sheet.load_character_data(demo_character)
        self.menu.update_game_info(demo_character['name'], demo_character['level'])
        self.menu.set_character_loaded(False)  # Mark as not a real saved character
        
        # Add test encounter
        test_encounter = {
            'name': 'Goblin Ambush',
            'difficulty': 'Hard',
            'creatures': ['Goblin x4', 'Goblin Boss x1']
        }
        self.encounter_pane.add_encounter(test_encounter)
        
        # Add test equipment
        test_equipment = {
            'main_hand': {'name': 'Orcrist', 'type': 'Longsword', 'attack_bonus': 2, 'weight_lb': 3.0},
            'armor': {'name': 'Chain Mail', 'armor_class': 16, 'weight_lb': 55.0}
        }
        
        test_inventory = [
            {'name': 'Healing Potion', 'type': 'Consumable', 'quantity': 3, 'weight_lb': 0.5},
            {'name': 'Rope (50 ft)', 'type': 'Gear', 'quantity': 1, 'weight_lb': 10},
            {'name': 'Rations', 'type': 'Food', 'quantity': 5, 'weight_lb': 2}
        ]
        
        # Use demo character's stats for calculations
        demo_strength = demo_character['strength']
        demo_dexterity = demo_character['dexterity']
        self.equipment_panel.load_equipment_data(test_equipment, test_inventory, demo_strength, demo_dexterity)
        
        # Set encounter scene
        self.encounter_pane.update_scene_description(
            "You stand at the entrance of a dark cave. The sound of goblin voices echoes from within. "
            "Your torch flickers, casting dancing shadows on the rough stone walls. "
            "What do you do?"
        )
        
        self.log_panel.log_info("[NOTE] This is demo data - Create your own character to get started!")
        self.log_panel.log_system("Use 'Create Character' button to make your own adventurer")
        self.log_panel.log_info("Demo scenario: You explore ancient ruins...")
    
    def _start_character_creation(self):
        """Start the character creation process."""
        self.log_panel.log_system("Starting character creation...")
        self.encounter_pane.set_character_creation_mode()
    
    def _on_character_created(self, character_data):
        """Handle completed character creation."""
        if not character_data:
            self.log_panel.log_error("Character creation failed: no data received")
            return
            
        name = character_data.get('name', 'Unknown')
        class_data = character_data.get('class_data') or {}
        species_data = character_data.get('species_data') or {}
        class_name = class_data.get('name', 'Unknown')
        species_name = species_data.get('name', 'Unknown')
        selected_feats = character_data.get('selected_feats', [])
        
        self.log_panel.log_system(f"Character created: {name} ({species_name} {class_name})")
        if selected_feats:
            feat_list = ", ".join(selected_feats)
            self.log_panel.log_info(f"Origin feats selected: {feat_list}")
            
            # Log feat effects applied
            if "Tough" in selected_feats:
                self.log_panel.log_info(f"💪 Tough feat: +2 hit points per level applied")
            if "Linguist" in selected_feats:
                self.log_panel.log_info(f"📚 Linguist feat: +1 Intelligence, +3 languages applied")

        try:
            # Determine next available save slot
            save_slots = self.game_engine.get_save_slots_sync()
            occupied_numbers = {slot['slot_number'] for slot in save_slots if slot['is_occupied']}
            save_slot = 1
            while save_slot in occupied_numbers:
                save_slot += 1

            # Save character to database
            save_character_data = self._prepare_character_for_save(character_data)
            saved_character = self.game_engine.create_new_character_sync(save_character_data, save_slot=save_slot)

            # Store the last used slot for auto-loading
            self.game_engine.settings['last_character_slot'] = save_slot
            self.game_engine.save_settings()

            # Load the saved character into the character sheet
            character_display_data = self._convert_dto_to_display(saved_character)
            self.character_sheet.load_character_data(character_display_data)

            equipped_items = {}
            if saved_character['equipment_main_hand']:
                item_data = self.game_engine.get_equipment_item_sync(saved_character['equipment_main_hand'])
                equipped_items['main_hand'] = item_data if item_data else {'name': saved_character['equipment_main_hand'], 'weight_lb': 0}
            if saved_character['equipment_off_hand']:
                item_data = self.game_engine.get_equipment_item_sync(saved_character['equipment_off_hand'])
                equipped_items['off_hand'] = item_data if item_data else {'name': saved_character['equipment_off_hand'], 'weight_lb': 0}
            if saved_character['equipment_armor']:
                item_data = self.game_engine.get_equipment_item_sync(saved_character['equipment_armor'])
                equipped_items['armor'] = item_data if item_data else {'name': saved_character['equipment_armor'], 'weight_lb': 0}
            if saved_character.get('equipment_shield') and 'off_hand' not in equipped_items:
                item_data = self.game_engine.get_equipment_item_sync(saved_character['equipment_shield'])
                equipped_items['off_hand'] = item_data if item_data else {'name': saved_character['equipment_shield'], 'weight_lb': 0}
            
            # Load character inventory
            inventory_items = self.game_engine.get_character_inventory_sync(saved_character['id'])
            
            self.equipment_panel.load_equipment_data(equipped_items, inventory_items, saved_character['strength'], saved_character['dexterity'])
            
            # Load character data into action panel for weapon cards
            print(f"[DEBUG] MAIN WINDOW DEBUG: saved_character.class_id = {saved_character['class_id']}")
            character_stats = {
                'id': saved_character['id'],  # Add character ID for potion checks
                'class_id': saved_character['class_id'],  # Required for rage damage bonus
                'strength': saved_character['strength'],
                'dexterity': saved_character['dexterity'],
                'constitution': saved_character['constitution'],
                'intelligence': saved_character['intelligence'],
                'wisdom': saved_character['wisdom'],
                'charisma': saved_character['charisma'],
                'armor_class': saved_character['armor_class'],
                'level': saved_character['level'],
                'hit_points_current': saved_character['hit_points_current'],
                'hit_points_max': saved_character['hit_points_max'],
                'feats': saved_character.get('feats', []),
                'weapon_masteries': saved_character.get('weapon_masteries', [])
            }
            print(f"[DEBUG] CHARACTER_STATS DEBUG: {character_stats}")
            self.action_panel.load_character_equipment(equipped_items, character_stats)
            
            # Set full character context for action panel features like rage
            self.action_panel.set_character_context(character_stats)

            # Load class features into action panel using new feature system
            try:
                from core.feature_integration import FeatureSystemIntegration
                feature_system = FeatureSystemIntegration('talekeeper.db')
                print(f"[DEBUG] Loading features for character {saved_character['name']} (ID: {saved_character['id']})")
                available_features = feature_system.get_available_features(saved_character['id'])
                
                # If no features found, initialize them (for characters created before our fix)
                if not available_features:
                    print(f"[DEBUG] No features found, initializing for {saved_character['class_id']} level {saved_character['level']}")
                    feature_system.initialize_character_features(saved_character['id'])
                    available_features = feature_system.get_available_features(saved_character['id'])
                    print(f"[DEBUG] After initialization: {len(available_features)} features")
                
                print(f"[DEBUG] Raw features from feature system: {[f['name'] for f in available_features]}")
                
                # Convert feature list to dictionary format expected by action panel
                class_features = {}
                for feature_data in available_features:
                    if isinstance(feature_data, dict) and 'name' in feature_data:
                        feature_name = feature_data['name']
                        class_features[feature_name] = feature_data
                
                print(f"[DEBUG] Loading {len(class_features)} class features: {list(class_features.keys())}")
                self.action_panel.load_character_features(class_features)
            except Exception as e:
                print(f"[DEBUG] Error loading class features: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to old system - but don't load anything to avoid wrong features
                print(f"[DEBUG] Feature system failed, loading empty features to avoid incorrect actions")
                self.action_panel.load_character_features({})
            
            # Load character feats into action panel (for fighting styles, etc.)
            character_feats = saved_character.get('feats', [])
            # Also load fighting styles from character_features table
            try:
                fighting_styles = self.game_engine.get_character_fighting_styles(saved_character['id'])
                character_feats.extend(fighting_styles)
            except:
                pass
            self.action_panel.load_character_feats(character_feats)
            
            # Load weapon masteries into action panel
            weapon_masteries = getattr(saved_character, 'weapon_masteries', []) or []
            self.action_panel.load_weapon_masteries(weapon_masteries)

            # Update menu
            self.menu.update_game_info(saved_character['name'], saved_character['level'])
            self.menu.set_character_loaded(True)
            
            # Provide definitive feedback that character was saved
            self.log_panel.log_info(f"✓ Character '{name}' successfully created and saved!")
            self.log_panel.log_system(
                f"Saved to slot {save_slot} - Level {saved_character['level']} {species_name} {class_name}"
            )
            self.log_panel.log_info(f"Welcome, {name}! Your adventure begins...")
            
        except Exception as e:
            self.log_panel.log_error(f"Failed to save character: {e}")
            # Still load the character in UI even if save failed
            formatted_character = self._format_character_for_display(character_data)
            self.character_sheet.load_character_data(formatted_character)
            self.menu.update_game_info(name, 1)
            self.menu.set_character_loaded(True)
            self.equipment_panel.load_equipment_data({}, [])
    
    def _save_and_exit(self):
        """Save the current game state and exit the application."""
        self.log_panel.log_system("Saving game and exiting...")
        
        # Save current character and game state if available
        try:
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                self.game_engine.save_game_sync()
                self.log_panel.log_info(f"Saved character: {self.game_engine.current_character['name']}")
            else:
                self.log_panel.log_info("No active character to save")
        except Exception as e:
            self.log_panel.log_error(f"Error saving game: {e}")
        
        # Close the application
        self.log_panel.log_system("Goodbye!")
        self.close()
    
    def _force_reload_character(self):
        """Refresh inventory and action panels to show updated data."""
        self.log_panel.log_system("Refreshing inventory...")
        
        try:
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                character = self.game_engine.current_character
                character_name = character['name']
                
                # Get updated inventory from database
                character_inventory = self.game_engine.get_character_inventory_sync(character['id'])
                
                # Get equipped items
                equipped_items = {}
                if character.get('equipment_main_hand'):
                    item_data = self.game_engine.get_equipment_item_sync(character['equipment_main_hand'])
                    equipped_items['main_hand'] = item_data if item_data else {'name': character['equipment_main_hand'], 'weight_lb': 0}
                if character.get('equipment_armor'):
                    item_data = self.game_engine.get_equipment_item_sync(character['equipment_armor'])
                    equipped_items['armor'] = item_data if item_data else {'name': character['equipment_armor'], 'weight_lb': 0}
                if character.get('equipment_shield'):
                    item_data = self.game_engine.get_equipment_item_sync(character['equipment_shield'])
                    equipped_items['off_hand'] = item_data if item_data else {'name': character['equipment_shield'], 'weight_lb': 0}
                elif character.get('equipment_off_hand'):
                    item_data = self.game_engine.get_equipment_item_sync(character['equipment_off_hand'])
                    equipped_items['off_hand'] = item_data if item_data else {'name': character['equipment_off_hand'], 'weight_lb': 0}
                
                # Refresh equipment panel with proper parameters
                if hasattr(self, 'equipment_panel'):
                    self.equipment_panel.load_equipment_data(equipped_items, character_inventory, character['strength'], character['dexterity'])
                
                # Refresh action panel (for potion availability)
                if hasattr(self, 'action_panel'):
                    self.action_panel._update_potion_card()
                    self.action_panel._update_visible_cards()
                
                self.log_panel.log_info(f"Inventory refreshed for {character_name}")
                self.log_panel.log_system("Equipment and action panels updated")
            else:
                self.log_panel.log_error("No active character to refresh")
                self.log_panel.log_info("Load or create a character first")
        except Exception as e:
            self.log_panel.log_error(f"Failed to refresh inventory: {e}")
            self.log_panel.log_system("Refresh operation failed")
    
    def _try_load_last_character(self):
        """Try to load the most recent character, otherwise load test data."""
        try:
            # First, try to load from the last used slot
            last_slot = self.game_engine.settings.get('last_character_slot')
            print(f"[UI] Last character slot setting: {last_slot}")
            if last_slot:
                character = self.game_engine.load_character_sync(last_slot)
                if character:
                    self._load_character_into_ui(character, f"Auto-loaded last character from slot {last_slot}")
                    return
            
            # If no last slot or it's empty, try to find the most recent character from any slot
            save_slots = self.game_engine.get_save_slots_sync()
            print(f"[UI] Found {len(save_slots)} total save slots")
            occupied_slots = [slot for slot in save_slots if slot['is_occupied']]
            print(f"[UI] Found {len(occupied_slots)} occupied slots")
            
            if occupied_slots:
                # Sort by last_played date, most recent first
                occupied_slots.sort(key=lambda s: s['last_played'] or s['created_at'], reverse=True)
                most_recent_slot = occupied_slots[0]
                
                character = self.game_engine.load_character_sync(most_recent_slot['slot_number'])
                if character:
                    # Update the last character slot setting for next time
                    self.game_engine.settings['last_character_slot'] = most_recent_slot['slot_number']
                    self.game_engine.save_settings()
                    
                    self._load_character_into_ui(character, f"Auto-loaded most recent character from slot {most_recent_slot['slot_number']}")
                    return
            
            # No saved characters found at all
            self.log_panel.log_system("No saved characters found")
            self.log_panel.log_info("Create a new character to get started!")
            self.log_panel.log_system("Loading demo character for testing...")
            self.load_test_data()
            
        except Exception as e:
            self.log_panel.log_error(f"Error loading characters: {e}")
            self.log_panel.log_system("Loading demo character as fallback...")
            self.load_test_data()
    
    def _load_character_into_ui(self, character, log_message):
        """Helper method to load a character into the UI."""
        self.log_panel.log_system(log_message)
        
        # Convert character DTO to display format
        character_data = self._convert_dto_to_display(character)
        
        # Load into UI
        self.character_sheet.load_character_data(character_data)
        self.menu.update_game_info(character['name'], character['level'])
        self.menu.set_character_loaded(True)
        
        # Check if town tab should be shown (character may be able to level up)
        self.encounter_pane.refresh_character_data()

        equipped_items = {}
        if character.get('equipment_main_hand'):
            item_data = self.game_engine.get_equipment_item_sync(character['equipment_main_hand'])
            equipped_items['main_hand'] = item_data if item_data else {'name': character['equipment_main_hand'], 'weight_lb': 0}
        if character.get('equipment_off_hand'):
            item_data = self.game_engine.get_equipment_item_sync(character['equipment_off_hand'])
            equipped_items['off_hand'] = item_data if item_data else {'name': character['equipment_off_hand'], 'weight_lb': 0}
        if character.get('equipment_armor'):
            item_data = self.game_engine.get_equipment_item_sync(character['equipment_armor'])
            equipped_items['armor'] = item_data if item_data else {'name': character['equipment_armor'], 'weight_lb': 0}
        if character.get('equipment_shield') and 'off_hand' not in equipped_items:
            item_data = self.game_engine.get_equipment_item_sync(character['equipment_shield'])
            equipped_items['off_hand'] = item_data if item_data else {'name': character['equipment_shield'], 'weight_lb': 0}
        inventory_items = self.game_engine.get_character_inventory_sync(character['id'])
        self.equipment_panel.load_equipment_data(equipped_items, inventory_items, character['strength'], character['dexterity'])
        
        # Load character data into action panel for weapon cards
        character_stats = {
            'id': character['id'],  # Add character ID for potion checks
            'class_id': character['class_id'],  # Required for rage damage bonus
            'strength': character['strength'],
            'dexterity': character['dexterity'],
            'constitution': character['constitution'],
            'intelligence': character['intelligence'],
            'wisdom': character['wisdom'],
            'charisma': character['charisma'],
            'armor_class': character['armor_class'],
            'level': character['level'],
            'hit_points_current': character['hit_points_current'],
            'hit_points_max': character['hit_points_max'],
            'feats': character.get('feats', []),
            'weapon_masteries': character.get('weapon_masteries', [])
        }
        self.action_panel.load_character_equipment(equipped_items, character_stats)
        
        # Set full character context for action panel features like rage
        self.action_panel.set_character_context(character_stats)

        # Load class features into action panel using new feature system
        try:
            from core.feature_integration import FeatureSystemIntegration
            feature_system = FeatureSystemIntegration('talekeeper.db')
            available_features = feature_system.get_available_features(character.id)
            
            # If no features found, initialize them (for characters created before our fix)
            if not available_features:
                print(f"[DEBUG] No features found, initializing for {character.class_id} level {character.level}")
                feature_system.initialize_character_features(character.id)
                available_features = feature_system.get_available_features(character.id)
            
            # Convert feature list to dictionary format expected by action panel
            class_features = {}
            for feature_data in available_features:
                if isinstance(feature_data, dict) and 'name' in feature_data:
                    feature_name = feature_data['name']
                    class_features[feature_name] = feature_data
            
            print(f"[DEBUG] Loading {len(class_features)} class features: {list(class_features.keys())}")
            self.action_panel.load_character_features(class_features)
        except Exception as e:
            print(f"[DEBUG] Error loading class features: {e}")
            # Fallback - load empty to avoid wrong features
            self.action_panel.load_character_features({})
        
        # Load character feats into action panel (for fighting styles, etc.)
        character_feats = character.get('feats', []) or []
        # Also load fighting styles from character_features table
        try:
            fighting_styles = self.game_engine.get_character_fighting_styles(character['id'])
            character_feats.extend(fighting_styles)
        except:
            pass
        self.action_panel.load_character_feats(character_feats)
        
        # Load weapon masteries into action panel  
        weapon_masteries = getattr(character, 'weapon_masteries', []) or []
        self.action_panel.load_weapon_masteries(weapon_masteries)

        self.log_panel.log_info(f"Welcome back, {character.name}!")
    
    def _show_load_character_dialog(self):
        """Show dialog to load a saved character."""
        try:
            from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QHBoxLayout
            
            self.log_panel.log_system("Opening character selection dialog...")
            
            # Get all save slots
            save_slots = self.game_engine.get_save_slots_sync()
            occupied_slots = [slot for slot in save_slots if slot['is_occupied']]
            
            if not occupied_slots:
                self.log_panel.log_info("No saved characters found!")
                return
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Load Character")
            dialog.setFixedSize(500, 400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QListWidget {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #333333;
                }
                QListWidget::item:selected {
                    background-color: #4a90e2;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Select Character to Load:")
            layout.addWidget(title)
            
            # Character list
            char_list = QListWidget()
            
            # Sort slots by last played (most recent first)
            occupied_slots.sort(key=lambda s: s.last_played or s.created_at, reverse=True)
            
            for slot in occupied_slots:
                # Create display text
                last_played = "Never" if not slot['last_played'] else slot['last_played'].strftime("%Y-%m-%d %H:%M")
                item_text = f"Slot {slot['slot_number']}: {slot['character_name']} (Level {slot['character_level']})\n"
                item_text += f"Location: {slot['current_location']} | Last Played: {last_played}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, slot['slot_number'])
                char_list.addItem(item)
            
            layout.addWidget(char_list)

            # Buttons
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            delete_button = button_box.addButton("Delete", QDialogButtonBox.ButtonRole.DestructiveRole)
            delete_button.clicked.connect(lambda: self._delete_selected_character(char_list, dialog))
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show dialog
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                current_item = char_list.currentItem()
                if current_item:
                    slot_number = current_item.data(Qt.ItemDataRole.UserRole)
                    self._load_character_from_slot(slot_number)
                else:
                    self.log_panel.log_info("No character selected")
            
        except Exception as e:
            self.log_panel.log_error(f"Error opening character selection dialog: {e}")
    
    def _load_character_from_slot(self, slot_number):
        """Load a character from a specific save slot."""
        try:
            character = self.game_engine.load_character_sync(slot_number)
            if character:
                # Update the last character slot setting
                self.game_engine.settings['last_character_slot'] = slot_number
                self.game_engine.save_settings()
                
                # Load into UI
                self._load_character_into_ui(character, f"Loaded character from slot {slot_number}")
                
                self.log_panel.log_info(f"Successfully loaded {character.name}")
            else:
                self.log_panel.log_error(f"Failed to load character from slot {slot_number}")
        except Exception as e:
            self.log_panel.log_error(f"Error loading character from slot {slot_number}: {e}")

    def _delete_selected_character(self, char_list, dialog):
        """Delete the currently selected character from the dialog list."""
        from PyQt6.QtWidgets import QMessageBox

        current_item = char_list.currentItem()
        if not current_item:
            self.log_panel.log_info("No character selected to delete")
            return

        slot_number = current_item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Delete Character",
            f"Delete character in slot {slot_number}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if self.game_engine.delete_character_sync(slot_number):
                    char_list.takeItem(char_list.row(current_item))
                    self.log_panel.log_info(f"Deleted character from slot {slot_number}")

                    # If no characters remain, close dialog
                    if char_list.count() == 0:
                        dialog.reject()

                    if not self.game_engine.current_character:
                        self.character_sheet.clear_character_data()
                        self.menu.set_character_loaded(False)
                else:
                    self.log_panel.log_error(f"No character found in slot {slot_number}")
            except Exception as e:
                self.log_panel.log_error(f"Error deleting character from slot {slot_number}: {e}")
    
    def _format_character_for_display(self, character_data):
        """Convert character creation data to display format."""
        ability_scores = character_data.get('ability_scores') or {}
        species_data = character_data.get('species_data') or {}
        class_data = character_data.get('class_data') or {}
        
        # D&D 2024: No racial bonuses to ability scores
        final_scores = ability_scores.copy()
        
        # Calculate derived stats
        con_mod = (final_scores.get('constitution', 10) - 10) // 2
        dex_mod = (final_scores.get('dexterity', 10) - 10) // 2
        hit_die = class_data.get('hit_die', 8)
        
        # D&D 2024 HP rules: Level 1 gets max hit die + Con modifier
        max_hp = hit_die + con_mod
        
        return {
            'name': character_data.get('name', 'Adventurer'),
            'level': 1,
            'race_name': species_data.get('name', 'Human'),
            'class_name': class_data.get('name', 'Fighter'),
            'background_name': (character_data.get('background_data') or {}).get('name', 'Folk Hero'),
            'current_hit_points': max_hp,
            'hit_points': max_hp,
            'armor_class': 10 + dex_mod,  # Base AC + Dex modifier
            'strength': final_scores.get('strength', 10),
            'dexterity': final_scores.get('dexterity', 10),
            'constitution': final_scores.get('constitution', 10),
            'intelligence': final_scores.get('intelligence', 10),
            'wisdom': final_scores.get('wisdom', 10),
            'charisma': final_scores.get('charisma', 10),
            'experience_points': 0,
            'speed': species_data.get('speed', 30)
        }
    
    def _prepare_character_for_save(self, character_data):
        """Convert character creation data to format expected by game engine.
        
        Bulletproof method that preserves ALL character creation data without loss.
        """
        # Get data with robust defaults
        species_data = character_data.get('species_data') or {}
        class_data = character_data.get('class_data') or {}
        background_data = character_data.get('background_data') or {}
        ability_scores = character_data.get('ability_scores') or {}

        # Get IDs by looking up the names in the database
        race_id = self._get_race_id_by_name(species_data.get('name', 'Human'))
        class_id = self._get_class_id_by_name(class_data.get('name', 'Fighter'))
        if not background_data or not background_data.get('name'):
            raise ValueError("No background selected - this should never happen in character creation")
        background_id = self._get_background_id_by_name(background_data['name'])

        # BULLETPROOF: Extract all selection data with comprehensive fallbacks
        selected_feats = character_data.get('selected_feats', []) or []
        class_features = character_data.get('class_features', {}) or {}
        weapon_masteries = character_data.get('weapon_masteries', []) or []
        proficiencies = character_data.get('proficiencies', []) or []
        spells = character_data.get('spells', []) or []
        equipment_choices = character_data.get('equipment_choices', {}) or {}
        
        # Build comprehensive save data - every field that might be needed
        save_data = {
            # Core identity
            'name': character_data.get('name', 'Adventurer'),
            'race_id': race_id,
            'class_id': class_id,
            'background_id': background_id,
            'level': character_data.get('level', 1),
            'experience_points': character_data.get('experience_points', 0),
            
            # Ability scores
            'strength': ability_scores.get('strength', 10),
            'dexterity': ability_scores.get('dexterity', 10),
            'constitution': ability_scores.get('constitution', 10),
            'intelligence': ability_scores.get('intelligence', 10),
            'wisdom': ability_scores.get('wisdom', 10),
            'charisma': ability_scores.get('charisma', 10),
            
            # Character features - PRESERVE EVERYTHING
            'feats': selected_feats,
            'features': class_features,
            'weapon_masteries': weapon_masteries,
            'proficiencies': proficiencies,
            
            # Spells and magic
            'spells': spells,
            'spell_slots': character_data.get('spell_slots', {}),
            'cantrips': character_data.get('cantrips', []),
            
            # Equipment and inventory
            'equipment_choices': equipment_choices,
            'starting_equipment': character_data.get('starting_equipment', {}),
            
            # Metadata
            'notes': f"Created via character creator. D&D 2024 rules applied.",
            'subclass_id': character_data.get('subclass_id'),
            'background_features': character_data.get('background_features', {}),
            
            # Resource tracking - initialize Fighter abilities
            'spell_slots_current': {},
            'spell_slots_max': {},
            'class_resources': {},
            'class_resources_max': {},
            'ability_uses': {},
            'ability_uses_max': {},
        }
        
        # Calculate hit points based on class, level, and Constitution
        constitution = ability_scores.get('constitution', 10)
        con_modifier = (constitution - 10) // 2
        class_name = class_data.get('name', 'Fighter')
        
        # Get hit die for class (default to d10 for Fighter)
        hit_die_map = {
            'Fighter': 10, 'Paladin': 10, 'Ranger': 10, 'Barbarian': 12,
            'Rogue': 8, 'Monk': 8, 'Bard': 8, 'Cleric': 8, 'Druid': 8, 'Warlock': 8,
            'Artificer': 8, 'Sorcerer': 6, 'Wizard': 6
        }
        hit_die = hit_die_map.get(class_name, 10)
        
        # Calculate max HP: full hit die at level 1 + Con modifier
        max_hp = hit_die + con_modifier
        current_hp = max_hp  # Start at full health
        
        # Add HP fields to save data
        save_data.update({
            'hit_points_max': max_hp,
            'hit_points_current': current_hp,
            'max_hit_points': max_hp,  # Alternative field name for combat system
            'current_hit_points': current_hp,  # Alternative field name for combat system
            'hit_dice_max': 1,  # Level 1 = 1 hit die
            'hit_dice_current': 1
        })
        
        # Add saving throw proficiencies from character creation
        saving_throw_profs = character_data.get('saving_throw_proficiencies', {})
        save_data.update({
            'str_save_proficient': saving_throw_profs.get('str_save_proficient', 0),
            'dex_save_proficient': saving_throw_profs.get('dex_save_proficient', 0),
            'con_save_proficient': saving_throw_profs.get('con_save_proficient', 0),
            'int_save_proficient': saving_throw_profs.get('int_save_proficient', 0),
            'wis_save_proficient': saving_throw_profs.get('wis_save_proficient', 0),
            'cha_save_proficient': saving_throw_profs.get('cha_save_proficient', 0),
        })
        
        # Initialize class-specific abilities
        level = character_data.get('level', 1)
        if class_name == 'Fighter':
            # Second Wind - available at level 1
            save_data['ability_uses']['Second Wind'] = 1  # Start with 1 use
            save_data['ability_uses_max']['Second Wind'] = 1  # 1 use per short rest
            
            # Action Surge - available at level 2+
            if level >= 2:
                save_data['ability_uses']['Action Surge'] = 1  # Start with 1 use
                save_data['ability_uses_max']['Action Surge'] = 1  # 1 use per short rest
        
        # Apply feat effects to character stats
        if selected_feats:
            save_data = self._apply_feat_effects(save_data, selected_feats)

        equipment_choices = character_data.get('equipment_choices') or {}
        if equipment_choices:
            try:
                self.game_engine.apply_equipment_choices_sync(save_data, equipment_choices)
            except Exception:
                pass

        return save_data
    
    def _apply_feat_effects(self, character_data: Dict, feat_names: List[str]) -> Dict:
        """Apply mechanical effects from selected feats to character data."""
        try:
            from services.feat_effects import FeatEffectsProcessor
            
            processor = FeatEffectsProcessor()
            modified_data = processor.apply_feat_effects_to_character(character_data, feat_names)
            
            return modified_data
            
        except Exception as e:
            print(f"Error applying feat effects: {e}")
            return character_data  # Return unmodified data if error occurs

    def _get_race_id_by_name(self, name):
        """Get race ID by name from database."""
        try:
            races = self.game_engine.get_available_races_sync()
            for race in races:
                if race.name == name:
                    return race.id
            return races[0].id if races else 'human'  # Fallback to first race or default
        except:
            return 'human'  # Safe fallback
    
    def _get_class_id_by_name(self, name):
        """Get class ID by name from database."""
        try:
            classes = self.game_engine.get_available_classes_sync()
            for cls in classes:
                if cls.name == name:
                    # Convert class name to lowercase database key format
                    result = name.lower().replace(' ', '_')
                    return result
            # Fallback - use first class name if no match
            if classes:
                fallback = classes[0].name.lower().replace(' ', '_')
                return fallback
            return 'fighter'  # Ultimate fallback
        except Exception as e:
            print(f"[DEBUG] Exception in _get_class_id_by_name: {e}")
            return 'fighter'  # Safe fallback
    
    def _get_background_id_by_name(self, name):
        """Get background ID by name from database."""
        try:
            backgrounds = self.game_engine.get_available_backgrounds_sync()
            for bg in backgrounds:
                if bg.name == name:
                    return bg.id
            raise ValueError(f"Background '{name}' not found in database")
        except Exception as e:
            raise ValueError(f"Failed to get background ID for '{name}': {e}")
    
    def _convert_dto_to_display(self, character_dict):
        """Convert character dictionary to format expected by character sheet."""
        return {
            'id': character_dict['id'],  # Include ID for database lookups
            'name': character_dict['name'],
            'level': character_dict['level'],
            'race_name': character_dict['race_name'],
            'class_name': character_dict['class_name'],
            'background_name': character_dict['background_name'],
            'current_hit_points': character_dict['hit_points_current'],
            'hit_points': character_dict['hit_points_max'],
            'armor_class': character_dict['armor_class'],
            'strength': character_dict['strength'],
            'dexterity': character_dict['dexterity'],
            'constitution': character_dict['constitution'],
            'intelligence': character_dict['intelligence'],
            'wisdom': character_dict['wisdom'],
            'charisma': character_dict['charisma'],
            'experience_points': character_dict['experience_points'],
            'features': character_dict['features'],
            'feats': character_dict['feats'],  # Include feats from SQLite migration!
            'speed': 30  # Default speed for now
        }