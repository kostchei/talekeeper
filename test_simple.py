#!/usr/bin/env python3
"""Simple test of imports"""

try:
    print("Testing imports...")
    from PyQt6.QtWidgets import QApplication
    print("PyQt6 imported successfully")
    
    from encounter_pane.encounter_panel import EncounterPanel
    print("EncounterPanel imported successfully")
    
    print("Creating QApplication...")
    import sys
    app = QApplication(sys.argv)
    
    print("Creating EncounterPanel...")
    panel = EncounterPanel()
    
    print("Setting character creation mode...")
    panel.set_character_creation_mode()
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()