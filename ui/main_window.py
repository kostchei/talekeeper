"""
File: ui/main_window.py
Path: /ui/main_window.py

Main application window for TaleKeeper Desktop.
PyQt6 window with the complete UI as specified in ui_plan.md

This is the main application window - identical to FullUITestWindow
but serves as the production main window.
"""

import sys
import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QTimer

from menu.game_menu import GameMenu
from character_sheet.character_panel import CharacterPanel
from encounter_pane.encounter_panel import EncounterPanel
from log.log_panel import LogPanel
from equipment_layout.equipment_panel import EquipmentPanel
from action_cards.action_panel import ActionPanel
from core.game_engine import GameEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - D&D 2024 Adventure")
        self.setMinimumSize(1920, 1080)
        
        # Initialize game engine
        self.game_engine = GameEngine()
        
        # === CENTRAL WIDGET ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins - fill full height
        
        self._setup_ui()
        self._apply_dark_theme()
        self._connect_signals()
        
        # Try to load last character after 1 second, otherwise load test data
        QTimer.singleShot(1000, self._try_load_last_character)
    
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
        self.equipment_panel.move(96 + 648 + 648, 54 + 200)  # Below log
        self.equipment_panel.show()
        
        # Action cards (bottom left)
        self.action_panel = ActionPanel(self)
        self.action_panel.move(96, 1080 - 54 - 300)  # Bottom left
        self.action_panel.show()
        self.action_panel.raise_()
    
    def _apply_dark_theme(self):
        """Apply dark theme to main window"""
        self.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QSplitter::handle {
            background-color: #666666;
        }
        QSplitter::handle:horizontal {
            width: 3px;
        }
        QSplitter::handle:vertical {
            height: 3px;
        }
        """)
    
    def _connect_signals(self):
        """Connect all widget signals"""
        
        # Menu signals
        self.menu.create_character_requested.connect(self._start_character_creation)
        self.menu.load_game_requested.connect(lambda: self.log_panel.log_info("Load Game requested"))
        self.menu.save_and_exit_requested.connect(self._save_and_exit)
        self.menu.archive_character_requested.connect(lambda: self.log_panel.log_info("Archive Character requested"))
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
        """Load test data into all widgets"""
        self.log_panel.log_system("Loading test data...")
        
        # Load test character
        test_character = {
            'name': 'Thorin Oakenshield',
            'level': 8,
            'race_name': 'Dwarf',
            'class_name': 'Fighter',
            'current_hit_points': 72,
            'hit_points': 85,
            'armor_class': 18,
            'strength': 18,
            'dexterity': 14,
            'constitution': 16,
            'intelligence': 12,
            'wisdom': 13,
            'charisma': 15,
            'experience_points': 35000,
            'speed': 25,
            'background_name': 'Noble'
        }
        
        self.character_sheet.load_character_data(test_character)
        self.menu.update_game_info(test_character['name'], 3)
        self.menu.set_character_loaded(True)
        
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
        
        self.log_panel.log_info("Welcome to the Lonely Mountain adventure!")
        self.log_panel.log_dice("Rolled 1d20+3 for initiative: 17")
    
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
        
        # Load the new character into the character sheet
        formatted_character = self._format_character_for_display(character_data)
        self.character_sheet.load_character_data(formatted_character)
        
        # Update menu
        self.menu.update_game_info(name, 1)
        self.menu.set_character_loaded(True)
        
        self.log_panel.log_info(f"Welcome, {name}! Your adventure begins...")
    
    def _save_and_exit(self):
        """Save the current game state and exit the application."""
        self.log_panel.log_system("Saving game and exiting...")
        
        # Save current character and game state if available
        try:
            if hasattr(self, 'game_engine') and self.game_engine.current_character:
                self.game_engine.save_game()
                self.log_panel.log_info(f"Saved character: {self.game_engine.current_character.name}")
            else:
                self.log_panel.log_info("No active character to save")
        except Exception as e:
            self.log_panel.log_error(f"Error saving game: {e}")
        
        # Close the application
        self.log_panel.log_system("Goodbye!")
        self.close()
    
    def _try_load_last_character(self):
        """Try to load the last played character, otherwise load test data."""
        last_slot = self.game_engine.settings.get('last_character_slot')
        
        if last_slot:
            character = self.game_engine.load_character(last_slot)
            if character:
                self.log_panel.log_system(f"Auto-loaded last character: {character.name}")
                
                # Convert character DTO to display format
                character_data = {
                    'name': character.name,
                    'level': character.level,
                    'race_name': character.race_name,
                    'class_name': character.class_name,
                    'current_hit_points': character.hit_points_current,
                    'hit_points': character.hit_points_max,
                    'armor_class': character.armor_class,
                    'strength': character.strength,
                    'dexterity': character.dexterity,
                    'constitution': character.constitution,
                    'intelligence': character.intelligence,
                    'wisdom': character.wisdom,
                    'charisma': character.charisma,
                    'experience_points': character.experience_points,
                    'speed': 30,  # Default speed
                    'background_name': character.background_name
                }
                
                # Load into UI
                self.character_sheet.load_character_data(character_data)
                self.menu.update_game_info(character.name, character.level)
                self.menu.set_character_loaded(True)
                
                self.log_panel.log_info(f"Welcome back, {character.name}!")
                return
        
        # No last character found, load test data instead
        self.log_panel.log_system("No saved character found, loading demo character...")
        self.load_test_data()
    
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