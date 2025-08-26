#!/usr/bin/env python3
"""
Test all PyQt6 widgets together in the full layout
Run this to see the complete animated UI as specified in ui_plan.md
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QTimer

from menu.game_menu import GameMenu
from character_sheet.character_panel import CharacterPanel
from encounter_pane.encounter_panel import EncounterPanel
from log.log_panel import LogPanel
from equipment_layout.equipment_panel import EquipmentPanel
from action_cards.action_panel import ActionPanel


class FullUITestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Full UI Test (PyQt6)")
        self.setMinimumSize(1920, 1080)
        
        # === CENTRAL WIDGET ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(96, 54, 96, 54)  # 5% margins
        
        self._setup_ui()
        self._apply_dark_theme()
        self._connect_signals()
        
        # Load test data after 3 seconds
        QTimer.singleShot(3000, self.load_test_data)
    
    def _setup_ui(self):
        """Setup the complete UI layout"""
        
        # === TOP MENU ===
        self.menu = GameMenu()
        self.main_layout.addWidget(self.menu)
        
        # === MAIN SPLITTER ===
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- CHARACTER SHEET (left) ---
        self.character_sheet = CharacterPanel()
        self.main_splitter.addWidget(self.character_sheet)
        
        # --- ENCOUNTER PANE (center) ---
        self.encounter_pane = EncounterPanel()
        self.main_splitter.addWidget(self.encounter_pane)
        
        # --- RIGHT COLUMN: LOG + EQUIPMENT ---
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Log panel (top right)
        self.log_panel = LogPanel()
        self.right_splitter.addWidget(self.log_panel)
        
        # Equipment panel (bottom right)
        self.equipment_panel = EquipmentPanel()
        self.right_splitter.addWidget(self.equipment_panel)
        
        # Set right splitter proportions
        self.right_splitter.setSizes([486, 486])
        
        self.main_splitter.addWidget(self.right_splitter)
        
        # Set main splitter proportions (648, 648, 432)
        self.main_splitter.setSizes([648, 648, 432])
        
        self.main_layout.addWidget(self.main_splitter)
        
        # === ACTION CARDS (bottom) ===
        self.action_panel = ActionPanel()
        self.main_layout.addWidget(self.action_panel)
    
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
        self.menu.create_character_requested.connect(lambda: self.log_panel.log_info("Create Character requested"))
        self.menu.load_game_requested.connect(lambda: self.log_panel.log_info("Load Game requested"))
        self.menu.save_and_exit_requested.connect(lambda: self.log_panel.log_info("Save & Exit requested"))
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle('Fusion')
    
    window = FullUITestWindow()
    window.show()
    
    print("Full UI Test - TaleKeeper PyQt6")
    print("==============================")
    print("This displays all widgets in the complete animated layout!")
    print("")
    print("Features to test:")
    print("- Menu dropdown (top left)")
    print("- Character sheet expansion (left panel)")
    print("- Encounter modes (center - try different tabs)")
    print("- Log filtering (top right)")
    print("- Equipment expansion (bottom right)")  
    print("- Action cards categories (bottom)")
    print("- All animations and interactions")
    print("")
    print("Test data will load after 3 seconds...")
    
    sys.exit(app.exec())