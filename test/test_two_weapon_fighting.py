"""
Test script for two-weapon fighting system.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def test_two_weapon_fighting():
    """Test two-weapon fighting in the test environment."""
    print("=== TESTING TWO-WEAPON FIGHTING ===")
    print("Expected behavior:")
    print("1. Attack with main-hand light weapon")  
    print("2. System should detect off-hand is available")
    print("3. Should prompt: 'Off-hand attack available!'")
    print("4. Click off-hand weapon or wait 3 seconds")
    print("5. Monsters should attack only AFTER off-hand (or timeout)")
    print()
    
    try:
        # Import from test directory
        sys.path.insert(0, os.path.dirname(__file__))
        from ui.main_window import MainWindow
        
        app = QApplication.instance() or QApplication(sys.argv)
        main_window = MainWindow()
        
        print("OK Test environment loaded")
        print("OK Main window created")
        
        # Check if action panel has our new functions
        action_panel = main_window.action_panel
        
        new_functions = [
            '_check_for_followup_attacks',
            '_can_make_offhand_attack', 
            '_can_use_nick_mastery',
            '_end_player_turn'
        ]
        
        for func_name in new_functions:
            if hasattr(action_panel, func_name):
                print(f"OK {func_name} exists")
            else:
                print(f"MISSING {func_name}")
                return False
        
        # Check turn state variables
        turn_vars = [
            'player_turn_active',
            'used_bonus_action_this_turn', 
            'awaiting_followup_choice'
        ]
        
        for var_name in turn_vars:
            if hasattr(action_panel, var_name):
                print(f"OK {var_name} = {getattr(action_panel, var_name)}")
            else:
                print(f"MISSING {var_name}")
                return False
        
        print()
        print("=== MANUAL TEST INSTRUCTIONS ===")
        print("1. Start the test app")
        print("2. Equip two light weapons (Scimitar + Shortsword)")
        print("3. Start combat with any monster")
        print("4. Attack with main-hand weapon")
        print("5. Look for: '[CHOICE] Off-hand attack available!' message")
        print("6. Click off-hand weapon")
        print("7. Verify monsters only attack ONCE (after both player attacks)")
        print()
        
        main_window.show()
        
        # Auto-close after 10 seconds for testing
        def close_test():
            print("Test window auto-closing...")
            main_window.close()
            app.quit()
        
        timer = QTimer()
        timer.timeout.connect(close_test)
        timer.setSingleShot(True)
        timer.start(10000)
        
        app.exec()
        return True
        
    except Exception as e:
        print(f"FAILED Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_two_weapon_fighting()
    if success:
        print("OK Test setup complete")
    else:
        print("FAILED Test setup failed")