#!/usr/bin/env python3
"""
Debug the character sheet expansion issue in detail
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from character_sheet.character_panel import CharacterPanel

class ExpansionDebugTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Sheet Expansion Debug")
        self.setGeometry(100, 100, 1600, 800)
        
        # Create main widget with enough space
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.resize(1600, 800)
        
        # Position character panel like in test_full_ui.py
        self.character_panel = CharacterPanel(central_widget)
        self.character_panel.move(50, 50)
        self.character_panel.show()
        
        # Add status labels
        self.status_label = QLabel("Status: Ready", central_widget)
        self.status_label.move(50, 20)
        self.status_label.resize(400, 20)
        
        # Add test buttons
        self.test_btn = QPushButton("Manual Toggle", central_widget)
        self.test_btn.move(500, 50)
        self.test_btn.clicked.connect(self.manual_toggle)
        
        # Load test data
        test_data = {
            'name': 'Debug Character',
            'level': 3,
            'race_name': 'Human',
            'class_name': 'Fighter',
            'current_hit_points': 25,
            'hit_points': 30,
            'armor_class': 16,
            'strength': 16, 'dexterity': 14, 'constitution': 15,
            'intelligence': 12, 'wisdom': 13, 'charisma': 11,
            'experience_points': 2000,
            'speed': 30,
            'background_name': 'Soldier'
        }
        self.character_panel.load_character_data(test_data)
        
        self.toggle_count = 0
    
    def manual_toggle(self):
        """Manual toggle with extra debugging"""
        self.toggle_count += 1
        print(f"\n=== MANUAL TOGGLE #{self.toggle_count} ===")
        print(f"Before: expanded={self.character_panel.expanded}")
        print(f"Before: width={self.character_panel.width()}")
        print(f"Before: detail_width={self.character_panel.detail_panel.width()}")
        print(f"Before: parent_size={central_widget.size().width()}x{central_widget.size().height()}")
        
        # Perform toggle
        self.character_panel._toggle_expansion()
        
        print(f"After: expanded={self.character_panel.expanded}")
        print(f"After: width={self.character_panel.width()}")
        print(f"After: detail_width={self.character_panel.detail_panel.width()}")
        
        # Update status
        state = "EXPANDED" if self.character_panel.expanded else "COLLAPSED"
        self.status_label.setText(f"Status: {state} (Toggle #{self.toggle_count})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpansionDebugTest()
    window.show()
    
    print("Character Sheet Expansion Debug Test")
    print("===================================")
    print("Try clicking both the expand button on the character sheet")
    print("AND the 'Manual Toggle' button to see if there are differences.")
    print("Watch the console for debug output.")
    
    sys.exit(app.exec())