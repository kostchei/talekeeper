#!/usr/bin/env python3
"""
Test the Character Sheet widget
Run this to see the expandable character sheet in action
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from character_sheet.character_panel import CharacterPanel


class CharacterTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Character Sheet Test")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create character sheet widget
        self.character_sheet = CharacterPanel()
        layout.addWidget(self.character_sheet)
        
        # Connect signals
        self.character_sheet.expansion_changed.connect(
            lambda expanded: print(f"Character sheet {'expanded' if expanded else 'collapsed'}")
        )
        self.character_sheet.character_action_requested.connect(
            lambda action: print(f"Character action: {action}")
        )
        
        # Load test character data after 2 seconds
        QTimer.singleShot(2000, self.load_test_character)
    
    def load_test_character(self):
        """Load test character data"""
        print("Loading test character data...")
        
        test_character = {
            'name': 'Gandalf the Grey',
            'level': 5,
            'race_name': 'Maiar',
            'class_name': 'Wizard',
            'current_hit_points': 45,
            'hit_points': 60,
            'armor_class': 15,
            'strength': 14,
            'dexterity': 16,
            'constitution': 18,
            'intelligence': 20,
            'wisdom': 17,
            'charisma': 16,
            'experience_points': 12000,
            'speed': 30,
            'background_name': 'Sage'
        }
        
        self.character_sheet.load_character_data(test_character)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle('Fusion')
    
    window = CharacterTestWindow()
    window.show()
    
    print("Character Sheet Test")
    print("===================")
    print("- Click 'Expand' to see the animation (648px -> 1296px)")
    print("- Try the action buttons (Rest, Level Up)")
    print("- Scroll through the detailed character info")
    print("- Test character data will load after 2 seconds")
    
    sys.exit(app.exec())