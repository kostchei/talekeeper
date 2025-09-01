"""
Test off-hand weapon attack functionality.
"""

from action_cards.action_panel import ActionPanel, ActionType
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

def test_off_hand_functionality():
    """Test off-hand weapon attack damage calculation."""
    
    # Create minimal PyQt application for testing
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    
    # Create action panel
    action_panel = ActionPanel()
    
    # Simulate character with scimitars equipped
    character_stats = {
        'strength': 16,  # +3 modifier
        'dexterity': 16, # +3 modifier
        'constitution': 14,
        'intelligence': 10,
        'wisdom': 12,
        'charisma': 8,
        'level': 1
    }
    
    equipped_weapons = {
        'main_hand': {
            'name': 'Scimitar',
            'item_type': 'weapon',
            'damage_dice': '1d6',
            'damage_type': 'slashing',
            'weapon_properties': ['finesse', 'light'],
            'magic_bonus': 0
        },
        'off_hand': {
            'name': 'Scimitar',
            'item_type': 'weapon', 
            'damage_dice': '1d6',
            'damage_type': 'slashing',
            'weapon_properties': ['finesse', 'light'],
            'magic_bonus': 0
        }
    }
    
    # Load equipment into action panel
    action_panel.load_character_equipment(equipped_weapons, character_stats)
    
    # Check if off-hand attack card was created
    if ActionType.ATTACK_OFF_HAND in action_panel.action_cards:
        off_hand_card = action_panel.action_cards[ActionType.ATTACK_OFF_HAND]
        print(f"OFF-HAND ATTACK CARD CREATED")
        print(f"Name: {off_hand_card.name}")
        print(f"Description: {off_hand_card.description}")
        
        # Check damage calculation
        weapon_data = off_hand_card.weapon_data
        main_hand_damage = action_panel._format_damage(equipped_weapons['main_hand'], is_off_hand=False)
        off_hand_damage = action_panel._format_damage(equipped_weapons['off_hand'], is_off_hand=True)
        
        print(f"\nDAMAGE COMPARISON:")
        print(f"Main-hand Scimitar: {main_hand_damage}")
        print(f"Off-hand Scimitar:  {off_hand_damage}")
        
        # Main hand should have +3 damage (Dex mod), off-hand should have +0
        if "+3" in main_hand_damage and "+0" in off_hand_damage:
            print("SUCCESS: Off-hand correctly has no ability modifier to damage")
        elif "+3" not in main_hand_damage:
            print("ISSUE: Main-hand should have +3 damage modifier") 
        elif "+0" not in off_hand_damage:
            print("ISSUE: Off-hand should have +0 damage modifier")
    else:
        print("ISSUE: Off-hand attack card not created")
    
    # Clean up
    if app:
        app.quit()

if __name__ == "__main__":
    test_off_hand_functionality()