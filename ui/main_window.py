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
from core.game_engine_indexeddb import GameEngineIndexedDB


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        self.setMinimumSize(1920, 1080)
        
        # Initialize game engine
        self.game_engine = GameEngineIndexedDB()
        
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
        self.theme_toggle_button = QPushButton("🌙 Dark", self)  # Start with moon for switching to dark
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
            
            # Update toggle button text/icon based on current theme
            if hasattr(self, 'theme_toggle_button'):
                if theme_name == 'light':
                    self.theme_toggle_button.setText("🌙 Dark")  # Moon icon to switch to dark
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
        self.menu.archive_character_requested.connect(self._archive_current_character)
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
        
        # Equipment panel signals
        self.equipment_panel.expansion_changed.connect(
            lambda expanded: self.log_panel.log_system(f"Equipment panel {'expanded' if expanded else 'collapsed'}")
        )
        self.equipment_panel.item_used.connect(
            lambda item: self.log_panel.log_info(f"Used item: {item.get('name', 'Unknown')}")
        )
        
        # Action panel signals
        self.action_panel.action_triggered.connect(
            lambda action, context: self.log_panel.log_combat(f"Action: {action.value} - {context.get('name', '')}")
        )
        
        # Encounter pane character creation signal
        self.encounter_pane.character_created.connect(self._on_character_created)
    
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
            'main_hand': {'name': 'Orcrist', 'type': 'Longsword', 'attack_bonus': 2},
            'armor': {'name': 'Chain Mail', 'armor_class': 16}
        }
        
        test_inventory = [
            {'name': 'Healing Potion', 'type': 'Consumable', 'quantity': 3, 'weight': 0.5},
            {'name': 'Rope (50 ft)', 'type': 'Gear', 'quantity': 1, 'weight': 10},
            {'name': 'Rations', 'type': 'Food', 'quantity': 5, 'weight': 2}
        ]
        
        self.equipment_panel.load_equipment_data(test_equipment, test_inventory)
        
        # Set encounter scene
        self.encounter_pane.update_scene_description(
            "You stand at the entrance of a dark cave. The sound of goblin voices echoes from within. "
            "Your torch flickers, casting dancing shadows on the rough stone walls. "
            "What do you do?"
        )
        
        self.log_panel.log_info("📝 This is demo data - Create your own character to get started!")
        self.log_panel.log_system("Use 'Create Character' button to make your own adventurer")
        self.log_panel.log_info("Demo scenario: You explore ancient ruins...")
    
    def _start_character_creation(self):
        """Start the character creation process."""
        self.log_panel.log_system("Starting character creation...")
        self.encounter_pane.set_character_creation_mode()
    
    def _on_character_created(self, character_data):
        """Handle completed character creation."""
        name = character_data.get('name', 'Unknown')
        class_name = character_data.get('class_data', {}).get('name', 'Unknown')
        species_name = character_data.get('species_data', {}).get('name', 'Unknown')
        
        self.log_panel.log_system(f"Character created: {name} ({species_name} {class_name})")
        
        try:
            # Save character to database first
            save_character_data = self._prepare_character_for_save(character_data)
            saved_character = self.game_engine.create_new_character_sync(save_character_data, save_slot=1)
            
            # Store the last used slot for auto-loading
            self.game_engine.settings['last_character_slot'] = 1
            self.game_engine.save_settings()
            
            # Load the saved character into the character sheet
            character_display_data = self._convert_dto_to_display(saved_character)
            self.character_sheet.load_character_data(character_display_data)
            
            # Update menu
            self.menu.update_game_info(saved_character.name, saved_character.level)
            self.menu.set_character_loaded(True)
            
            # Provide definitive feedback that character was saved
            self.log_panel.log_info(f"✓ Character '{name}' successfully created and saved!")
            self.log_panel.log_system(f"Saved to slot 1 - Level {saved_character.level} {species_name} {class_name}")
            self.log_panel.log_info(f"Welcome, {name}! Your adventure begins...")
            
        except Exception as e:
            self.log_panel.log_error(f"Failed to save character: {e}")
            # Still load the character in UI even if save failed
            formatted_character = self._format_character_for_display(character_data)
            self.character_sheet.load_character_data(formatted_character)
            self.menu.update_game_info(name, 1)
            self.menu.set_character_loaded(True)
    
    def _save_and_exit(self):
        """Save the current game state and exit the application."""
        self.log_panel.log_system("Saving game and exiting...")
        
        # Save current character and game state if available
        try:
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                self.game_engine.save_game_sync()
                self.log_panel.log_info(f"Saved character: {self.game_engine.current_character.name}")
            else:
                self.log_panel.log_info("No active character to save")
        except Exception as e:
            self.log_panel.log_error(f"Error saving game: {e}")
        
        # Close the application
        self.log_panel.log_system("Goodbye!")
        self.close()
    
    def _archive_current_character(self):
        """Archive (save) the current character without exiting the application."""
        self.log_panel.log_system("Archiving current character...")
        
        # Save current character and game state if available
        try:
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                self.game_engine.save_game_sync()
                character_name = self.game_engine.current_character.name
                self.log_panel.log_info(f"Character '{character_name}' archived successfully!")
                self.log_panel.log_system("Game state saved to IndexedDB")
            else:
                self.log_panel.log_error("No active character to archive")
                self.log_panel.log_info("Load or create a character first")
        except Exception as e:
            self.log_panel.log_error(f"Failed to archive character: {e}")
            self.log_panel.log_system("Archive operation failed")
    
    def _try_load_last_character(self):
        """Try to load the most recent character, otherwise load test data."""
        try:
            # First, try to load from the last used slot
            last_slot = self.game_engine.settings.get('last_character_slot')
            if last_slot:
                character = self.game_engine.load_character_sync(last_slot)
                if character:
                    self._load_character_into_ui(character, f"Auto-loaded last character from slot {last_slot}")
                    return
            
            # If no last slot or it's empty, try to find the most recent character from any slot
            save_slots = self.game_engine.get_save_slots_sync()
            occupied_slots = [slot for slot in save_slots if slot.is_occupied]
            
            if occupied_slots:
                # Sort by last_played date, most recent first
                occupied_slots.sort(key=lambda s: s.last_played or s.created_at, reverse=True)
                most_recent_slot = occupied_slots[0]
                
                character = self.game_engine.load_character_sync(most_recent_slot.slot_number)
                if character:
                    # Update the last character slot setting for next time
                    self.game_engine.settings['last_character_slot'] = most_recent_slot.slot_number
                    self.game_engine.save_settings()
                    
                    self._load_character_into_ui(character, f"Auto-loaded most recent character from slot {most_recent_slot.slot_number}")
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
        self.menu.update_game_info(character.name, character.level)
        self.menu.set_character_loaded(True)
        
        self.log_panel.log_info(f"Welcome back, {character.name}!")
    
    def _show_load_character_dialog(self):
        """Show dialog to load a saved character."""
        try:
            from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QHBoxLayout
            
            self.log_panel.log_system("Opening character selection dialog...")
            
            # Get all save slots
            save_slots = self.game_engine.get_save_slots_sync()
            occupied_slots = [slot for slot in save_slots if slot.is_occupied]
            
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
                last_played = "Never" if not slot.last_played else slot.last_played.strftime("%Y-%m-%d %H:%M")
                item_text = f"Slot {slot.slot_number}: {slot.character_name} (Level {slot.character_level})\n"
                item_text += f"Location: {slot.current_location} | Last Played: {last_played}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, slot.slot_number)
                char_list.addItem(item)
            
            layout.addWidget(char_list)
            
            # Buttons
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
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
    
    def _format_character_for_display(self, character_data):
        """Convert character creation data to display format."""
        ability_scores = character_data.get('ability_scores', {})
        species_data = character_data.get('species_data', {})
        class_data = character_data.get('class_data', {})
        
        # Apply racial bonuses
        racial_bonuses = species_data.get('ability_score_increases', {})
        final_scores = {}
        for ability, base_score in ability_scores.items():
            bonus = racial_bonuses.get(ability, 0)
            final_scores[ability] = base_score + bonus
        
        # Calculate derived stats
        con_mod = (final_scores.get('constitution', 10) - 10) // 2
        dex_mod = (final_scores.get('dexterity', 10) - 10) // 2
        hit_die = class_data.get('hit_die', 8)
        max_hp = hit_die + con_mod
        
        return {
            'name': character_data.get('name', 'Adventurer'),
            'level': 1,
            'race_name': species_data.get('name', 'Human'),
            'class_name': class_data.get('name', 'Fighter'),
            'background_name': character_data.get('background_data', {}).get('name', 'Folk Hero'),
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
        """Convert character creation data to format expected by game engine."""
        # Get data with defaults
        species_data = character_data.get('species_data', {})
        class_data = character_data.get('class_data', {})
        background_data = character_data.get('background_data', {})
        ability_scores = character_data.get('ability_scores', {})
        
        # Get IDs by looking up the names in the database
        race_id = self._get_race_id_by_name(species_data.get('name', 'Human'))
        class_id = self._get_class_id_by_name(class_data.get('name', 'Fighter'))
        background_id = self._get_background_id_by_name(background_data.get('name', 'Folk Hero'))
        
        return {
            'name': character_data.get('name', 'Adventurer'),
            'race_id': race_id,
            'class_id': class_id,
            'background_id': background_id,
            'strength': ability_scores.get('strength', 10),
            'dexterity': ability_scores.get('dexterity', 10),
            'constitution': ability_scores.get('constitution', 10),
            'intelligence': ability_scores.get('intelligence', 10),
            'wisdom': ability_scores.get('wisdom', 10),
            'charisma': ability_scores.get('charisma', 10),
            'notes': f"Created via character creator. Final scores include racial bonuses."
        }
    
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
                    return cls.id
            return classes[0].id if classes else 'fighter'  # Fallback to first class or default
        except:
            return 'fighter'  # Safe fallback
    
    def _get_background_id_by_name(self, name):
        """Get background ID by name from database."""
        try:
            backgrounds = self.game_engine.get_available_backgrounds_sync()
            for bg in backgrounds:
                if bg.name == name:
                    return bg.id
            return backgrounds[0].id if backgrounds else 'folk-hero'  # Fallback to first background or default
        except:
            return 'folk-hero'  # Safe fallback
    
    def _convert_dto_to_display(self, character_dto):
        """Convert CharacterDTO to format expected by character sheet."""
        return {
            'name': character_dto.name,
            'level': character_dto.level,
            'race_name': character_dto.race_name,
            'class_name': character_dto.class_name,
            'background_name': character_dto.background_name,
            'current_hit_points': character_dto.hit_points_current,
            'hit_points': character_dto.hit_points_max,
            'armor_class': character_dto.armor_class,
            'strength': character_dto.strength,
            'dexterity': character_dto.dexterity,
            'constitution': character_dto.constitution,
            'intelligence': character_dto.intelligence,
            'wisdom': character_dto.wisdom,
            'charisma': character_dto.charisma,
            'experience_points': character_dto.experience_points,
            'speed': 30  # Default speed for now
        }