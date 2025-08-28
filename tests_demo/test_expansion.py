#!/usr/bin/env python3
"""
Quick test to verify character sheet expansion is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import QTimer
from character_sheet.character_panel import CharacterPanel

class ExpansionTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Sheet Expansion Test")
        self.setGeometry(100, 100, 1400, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add character panel
        self.character_panel = CharacterPanel()
        layout.addWidget(self.character_panel)
        
        # Add test button
        test_btn = QPushButton("Toggle Expansion (Test)")
        test_btn.clicked.connect(self.test_expansion)
        layout.addWidget(test_btn)
        
        # Load test character data
        test_data = {
            'name': 'Test Character',
            'level': 5,
            'race_name': 'Human',
            'class_name': 'Fighter',
            'current_hit_points': 45,
            'hit_points': 50,
            'armor_class': 16,
            'strength': 16, 'dexterity': 14, 'constitution': 15,
            'intelligence': 12, 'wisdom': 13, 'charisma': 11,
            'experience_points': 8000,
            'speed': 30,
            'background_name': 'Soldier'
        }
        self.character_panel.load_character_data(test_data)
        
        # Auto-test after 2 seconds
        QTimer.singleShot(2000, self.auto_test)
    
    def test_expansion(self):
        """Test expansion manually"""
        print(f"Before toggle: {self.character_panel.expanded}, size: {self.character_panel.width()}")
        self.character_panel._toggle_expansion()
        print(f"After toggle: {self.character_panel.expanded}, size: {self.character_panel.width()}")
    
    def auto_test(self):
        """Auto-test expansion"""
        print("=== AUTO EXPANSION TEST ===")
        print("Initial state:", self.character_panel.expanded)
        print("Initial width:", self.character_panel.width())
        print("Detail panel max width:", self.character_panel.detail_panel.maximumWidth())
        
        # Expand
        self.character_panel._toggle_expansion()
        print("After expansion:")
        print("  Expanded:", self.character_panel.expanded) 
        print("  Width:", self.character_panel.width())
        print("  Detail panel max width:", self.character_panel.detail_panel.maximumWidth())
        
        # Wait 3 seconds and collapse
        QTimer.singleShot(3000, self.auto_collapse)
    
    def auto_collapse(self):
        """Auto-collapse"""
        print("Auto-collapsing...")
        self.character_panel._toggle_expansion()
        print("After collapse:")
        print("  Expanded:", self.character_panel.expanded)
        print("  Width:", self.character_panel.width())
        print("  Detail panel max width:", self.character_panel.detail_panel.maximumWidth())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpansionTest()
    window.show()
    print("Character Sheet Expansion Test")
    print("==============================")
    print("Click the expand button or use the test button")
    print("Auto-test will run after 2 seconds...")
    
    sys.exit(app.exec())