#!/usr/bin/env python3
"""
Test the enhanced stat generation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from encounter_pane.encounter_panel import EncounterPanel

class StatSystemTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Stat System Test")
        self.setMinimumSize(900, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Instructions
        instructions = QLabel("""
STAT SYSTEM TEST

1. Click 'Create Character' from menu
2. Choose Fighter class
3. Go to Ability Scores step
4. Click 'Apply Class Defaults' - should set INT=3 and random stat=6
5. Click 'Roll 4d6 Drop Lowest' - should show rolled values
6. Click 'Use Rolled Scores' - should replace base values
7. Test point buy system with new ranges
        """)
        layout.addWidget(instructions)
        
        # Encounter panel (contains character creation)
        self.encounter_pane = EncounterPanel(self)
        layout.addWidget(self.encounter_pane)
        
        # Connect signals
        self.encounter_pane.character_created.connect(self._on_character_created)
        
        # Start in character creation mode
        self.encounter_pane.set_character_creation_mode()
        
        self.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            padding: 10px;
            background-color: #2a2a2a;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        """)
    
    def _on_character_created(self, character_data):
        """Handle completed character creation."""
        name = character_data.get('name', 'Unknown')
        ability_scores = character_data.get('ability_scores', {})
        
        print(f"\n=== CHARACTER CREATED ===")
        print(f"Name: {name}")
        print(f"Ability Scores: {ability_scores}")
        print("Test completed successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = StatSystemTestWindow()
    window.show()
    
    print("Stat System Test")
    print("================")
    print("Testing class-based dump stats and 4d6 rolling system...")
    
    sys.exit(app.exec())