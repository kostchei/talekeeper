"""
Simple verification that the implementation was added correctly.
"""

def verify_implementation():
    """Verify the two-weapon fighting functions were added."""
    print("=== VERIFYING IMPLEMENTATION ===")
    
    try:
        # Read the action_panel.py file and check for our new functions
        with open('action_cards/action_panel.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'def _check_for_followup_attacks',
            'def _can_make_offhand_attack', 
            'def _can_use_nick_mastery',
            'def _end_player_turn',
            'player_turn_active = False',
            'used_bonus_action_this_turn = False',
            'awaiting_followup_choice = False'
        ]
        
        print("Checking for required code:")
        all_present = True
        
        for item in required_functions:
            if item in content:
                print(f"OK {item}")
            else:
                print(f"MISSING: {item}")
                all_present = False
        
        # Check that the key modification was made
        if 'self._check_for_followup_attacks(action_type, context, encounter_panel)' in content:
            print("OK Key modification: _check_for_followup_attacks call")
        else:
            print("MISSING: _check_for_followup_attacks call")
            all_present = False
        
        print()
        if all_present:
            print("SUCCESS: All required functions and modifications present")
            print()
            print("NEXT STEPS:")
            print("1. Test by running: python main.py")
            print("2. Equip two light weapons (Scimitar + Shortsword)")  
            print("3. Start combat")
            print("4. Attack with main-hand")
            print("5. Look for: '[FOLLOWUP] Off-hand attack available' in console")
            print("6. Look for: '[CHOICE] Off-hand attack available!' in combat log")
            print("7. Click off-hand weapon within 3 seconds")
            print("8. Verify monsters attack only ONCE after both attacks")
            return True
        else:
            print("FAILURE: Implementation incomplete")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    verify_implementation()