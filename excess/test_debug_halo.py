#!/usr/bin/env python3
"""
Debug script to check Lucky/Inspiration halo system step by step
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.game_engine_sqlite import GameEngineSQLite
from ui.advantage_halo import AdvantageResourceManager

def test_database_resources():
    """Test loading character resources from database."""
    print("=== Testing Database Resource Loading ===")
    
    # Initialize game engine
    engine = GameEngineSQLite()
    
    # Get Valerius from database
    characters = engine.get_save_slots_sync()
    valerius = None
    
    for slot in characters:
        if slot.get('character_name') == 'Valerius':
            print(f"Found Valerius in slot {slot.get('slot_number')}")
            
            # Load full character data
            character_id = None
            # Find character ID from characters table
            import sqlite3
            conn = sqlite3.connect('talekeeper.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM characters WHERE name = 'Valerius'")
            valerius = dict(cursor.fetchone())
            conn.close()
            
            print(f"Character data keys: {list(valerius.keys())}")
            print(f"Lucky: {valerius.get('lucky_uses_current', 'MISSING')}/{valerius.get('lucky_uses_max', 'MISSING')}")
            print(f"Inspiration: {valerius.get('inspiration_uses_current', 'MISSING')}/{valerius.get('inspiration_uses_max', 'MISSING')}")
            
            break
            
    if not valerius:
        print("ERROR: Valerius not found!")
        return False
        
    # Test AdvantageResourceManager
    print("\n=== Testing AdvantageResourceManager ===")
    manager = AdvantageResourceManager(valerius)
    
    print(f"Has resources: {manager.has_resources()}")
    print(f"Primary resource: {manager.get_primary_resource()}")
    
    counts = manager.get_resource_counts()
    print(f"Resource counts: {counts}")
    
    return True

if __name__ == "__main__":
    test_database_resources()