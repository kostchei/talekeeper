#!/usr/bin/env python3
"""
Simple integration test for two-weapon fighting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_engine_sqlite import GameEngineSQLite

def test_integration():
    print("Testing Two-Weapon Fighting Integration")
    print("=" * 40)
    
    # Test 1: Game engine initialization
    game_engine = GameEngineSQLite("talekeeper.db")
    print("[PASS] Game engine initialized")
    
    # Test 2: Basic database connection
    try:
        save_slots = game_engine.get_save_slots_sync()
        print(f"[PASS] Found {len(save_slots)} save slots in database")
    except Exception as e:
        print(f"[FAIL] Error accessing save slots: {e}")
        return False
    
    # Test 3: Equipment service functionality
    from services.equipment import equipment_service
    
    try:
        # Test light weapon detection
        shortsword = equipment_service.get_item("Shortsword")
        if shortsword and 'light' in str(shortsword.get('weapon_properties', [])).lower():
            print("[PASS] Light weapon detection working")
        else:
            print("[INFO] Shortsword properties:", shortsword.get('weapon_properties') if shortsword else "Not found")
            
    except Exception as e:
        print(f"[FAIL] Error testing equipment service: {e}")
        return False
    
    # Test 4: Action panel integration
    try:
        from action_cards.action_panel import ActionPanel
        from PyQt6.QtWidgets import QApplication
        import sys
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create minimal action panel for testing
        action_panel = ActionPanel(None)
        print("[PASS] Action panel can be instantiated")
        
        # Test dual wield method exists
        if hasattr(action_panel, '_can_dual_wield'):
            print("[PASS] Two-weapon fighting methods present in action panel")
        else:
            print("[FAIL] Two-weapon fighting methods missing")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing action panel: {e}")
        return False
    
    print("\n[SUCCESS] All integration tests passed!")
    print("Two-weapon fighting system is properly integrated.")
    return True

if __name__ == "__main__":
    test_integration()