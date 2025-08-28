#!/usr/bin/env python3
"""
Test final stat system with abbreviations and take-higher logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from encounter_pane.encounter_panel import EncounterPanel

class FinalStatTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Final Stat System Test")
        self.setMinimumSize(1000, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Instructions
        instructions = QLabel("""
FINAL STAT SYSTEM TEST

NEW FEATURES:
✅ Stat abbreviations (STR, DEX, CON, INT, WIS, CHA)
✅ "Point Buy" column instead of "Base"
✅ Auto-take higher of rolled vs point buy
✅ Visual indicators (* = rolled score used)
✅ Green = rolled used, Orange = rolled not used

TESTING:
1. Choose Fighter class → Apply Class Defaults (INT=3, random=6)
2. Adjust point buy values
3. Roll 4d6 Drop Lowest → automatically applies higher scores
4. Final column shows max(point_buy, rolled) + racial bonuses
        """)
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Encounter panel
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
        QLabel#instructions {
            color: #ffffff;
            padding: 15px;
            background-color: #2a2a2a;
            border: 2px solid #4a90e2;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.4;
        }
        """)
    
    def _on_character_created(self, character_data):
        """Handle completed character creation."""
        name = character_data.get('name', 'Unknown')
        ability_scores = character_data.get('ability_scores', {})
        point_buy_scores = character_data.get('point_buy_scores', {})
        rolled_scores = character_data.get('rolled_scores', {})
        
        print(f"\n=== CHARACTER CREATED ===")
        print(f"Name: {name}")
        print(f"Final Ability Scores: {ability_scores}")
        print(f"Point Buy Scores: {point_buy_scores}")
        if rolled_scores:
            print(f"Rolled Scores: {rolled_scores}")
            print("\nComparison (Final = max(PointBuy, Rolled)):")
            for stat in ability_scores:
                pb = point_buy_scores[stat]
                rolled = rolled_scores.get(stat, {}).get('total', 0)
                final = ability_scores[stat]
                used = "ROLLED" if rolled > pb else "POINT_BUY"
                print(f"  {stat.upper()}: PB={pb}, Rolled={rolled} → Final={final} ({used})")
        print("Test completed successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = FinalStatTestWindow()
    window.show()
    
    print("Final Stat System Test")
    print("=====================")
    print("Testing abbreviations and take-higher logic...")
    
    sys.exit(app.exec())