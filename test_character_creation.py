#!/usr/bin/env python3
"""
Quick test script for character creation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from encounter_pane.encounter_panel import EncounterPanel
from log.log_panel import LogPanel

class CharacterCreationTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Character Creation Test")
        self.setMinimumSize(800, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Encounter panel (for character creation)
        self.encounter_pane = EncounterPanel(self)
        layout.addWidget(self.encounter_pane)
        
        # Log panel for output
        self.log_panel = LogPanel(self)
        self.log_panel.setMaximumHeight(200)
        layout.addWidget(self.log_panel)
        
        # Connect character creation signal
        self.encounter_pane.character_created.connect(self._on_character_created)
        
        # Start in character creation mode
        self.encounter_pane.set_character_creation_mode()
        
        self.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        """)
    
    def _on_character_created(self, character_data):
        """Handle completed character creation."""
        name = character_data.get('name', 'Unknown')
        class_name = character_data.get('class_data', {}).get('name', 'Unknown')
        species_name = character_data.get('species_data', {}).get('name', 'Unknown')
        
        self.log_panel.log_system(f"Character created: {name} ({species_name} {class_name})")
        
        # Print to console for debugging
        print(f"Character Creation Complete!")
        print(f"Name: {name}")
        print(f"Class: {class_name}")
        print(f"Species: {species_name}")
        print(f"Ability Scores: {character_data.get('ability_scores', {})}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = CharacterCreationTestWindow()
    window.show()
    
    print("Character Creation Test")
    print("======================")
    print("This tests the encounter pane character creation system")
    print("Navigate through the 5 steps:")
    print("1. Choose Class")
    print("2. Choose Background & Species") 
    print("3. Assign Ability Scores")
    print("4. Select Equipment")
    print("5. Review & Create")
    
    sys.exit(app.exec())