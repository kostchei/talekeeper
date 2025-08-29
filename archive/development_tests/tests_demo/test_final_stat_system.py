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
from core.game_engine import GameEngine

class FinalStatTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Final Stat System Test")
        self.setMinimumSize(1000, 900)
        
        # Initialize game engine
        self.game_engine = GameEngine()
        
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
✅ Character saving to database
✅ Auto-load last character on startup

TESTING:
1. Choose Fighter class → Apply Class Defaults (INT=3, auto-applied)
2. Adjust point buy values (27 points total)
3. Roll 4d6 Drop Lowest → automatically applies higher scores
4. Final column shows max(point_buy, rolled) + racial bonuses
5. Character saves to database on creation
        """)
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Encounter panel
        self.encounter_pane = EncounterPanel(self)
        layout.addWidget(self.encounter_pane)
        
        # Connect signals
        self.encounter_pane.character_created.connect(self._on_character_created)
        
        # Try to load last character, otherwise start character creation
        self._try_load_last_character()
        
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
        
        # Save character to database
        try:
            # Convert character data to format expected by game engine
            save_data = {
                "name": name,
                "race_id": character_data.get('species_data', {}).get('name', '').lower().replace(' ', '_'),
                "class_id": character_data.get('class_data', {}).get('name', '').lower().replace(' ', '_'),
                "background_id": character_data.get('background_data', {}).get('name', '').lower().replace(' ', '_'),
                "strength": ability_scores.get('strength', 10),
                "dexterity": ability_scores.get('dexterity', 10),
                "constitution": ability_scores.get('constitution', 10),
                "intelligence": ability_scores.get('intelligence', 10),
                "wisdom": ability_scores.get('wisdom', 10),
                "charisma": ability_scores.get('charisma', 10),
                "notes": f"Point Buy: {point_buy_scores}, Rolled: {rolled_scores}"
            }
            
            # Save to slot 1
            character_dto = self.game_engine.create_new_character(save_data, save_slot=1)
            print(f"\n✅ CHARACTER SAVED TO DATABASE!")
            print(f"Saved as: {character_dto.name} in Slot 1")
            
            # Update settings to remember last character
            self.game_engine.settings['last_character_slot'] = 1
            self.game_engine.save_settings()
            print(f"✅ Set as last played character")
            
        except Exception as e:
            print(f"\n❌ ERROR SAVING CHARACTER: {e}")
            import traceback
            traceback.print_exc()
        
        print("\nTest completed successfully!")
    
    def _try_load_last_character(self):
        """Try to load the last played character, otherwise start character creation."""
        last_slot = self.game_engine.settings.get('last_character_slot')
        
        if last_slot:
            character = self.game_engine.load_character(last_slot)
            if character:
                print(f"\n🔄 AUTO-LOADED LAST CHARACTER:")
                print(f"Name: {character.name}")
                print(f"Level: {character.level}")
                print(f"Class: {character.class_name}")
                print(f"Race: {character.race_name}")
                print(f"Background: {character.background_name}")
                print(f"STR: {character.strength}, DEX: {character.dexterity}, CON: {character.constitution}")
                print(f"INT: {character.intelligence}, WIS: {character.wisdom}, CHA: {character.charisma}")
                
                # Set encounter pane to exploration mode with loaded character
                self.encounter_pane.encounter_mode = "exploration"
                self.encounter_pane._setup_exploration_mode()
                return
        
        # No last character or loading failed, start character creation
        print("\n📝 No last character found, starting character creation...")
        self.encounter_pane.set_character_creation_mode()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = FinalStatTestWindow()
    window.show()
    
    print("Final Stat System Test")
    print("=====================")
    print("Testing abbreviations and take-higher logic...")
    
    sys.exit(app.exec())