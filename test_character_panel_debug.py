#!/usr/bin/env python3
"""Test character panel loading with debug output."""

import sys
sys.path.insert(0, '.')

# Import required classes
from character_sheet.character_panel import CharacterPanel
from PyQt6.QtWidgets import QApplication
import sqlite3

def test_character_panel_loading():
    """Test loading Dwari character into character panel."""
    
    app = QApplication([])
    
    # Create character panel
    char_panel = CharacterPanel()
    
    # Get Dwari's character data from database
    conn = sqlite3.connect('talekeeper.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, class_id as class_name, level, 
               strength, dexterity, constitution, intelligence, wisdom, charisma
        FROM characters WHERE name = 'Dwari'
    """)
    
    row = cursor.fetchone()
    if not row:
        print("Dwari character not found")
        return
        
    # Convert to dict
    character_data = dict(row)
    print(f"Loading character data: {character_data}")
    
    # Load into character panel (this should trigger _update_detail_panel)
    char_panel.load_character_data(character_data)
    
    # Check what's actually in the features widget
    widget_text = char_panel.features_text.toPlainText()
    print(f"\nWidget text length: {len(widget_text)}")
    print(f"Widget text content:\n{widget_text}")
    
    conn.close()
    print("\n=== Character panel loading test completed ===")

if __name__ == "__main__":
    test_character_panel_loading()