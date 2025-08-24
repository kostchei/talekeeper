"""
Test script for detailed combat logging.
Shows the new dice roll format in action.
"""

import sys
import os
# Add parent directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import from current directory
from .combat_demo import create_sample_character, create_sample_monster
from services.combat import CombatService, CombatState


def test_detailed_logging():
    """Test the detailed combat logging system."""
    print("=== Testing Detailed Combat Logging ===\n")
    
    # Create participants
    character = create_sample_character()
    monster = create_sample_monster()
    
    # Initialize combat
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print("Initiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Test a few manual attacks to show the detailed logging
    current = combat.get_current_combatant()
    if current and current.type == "character":
        # Test player attack with longsword
        targets = combat.get_alive_enemies("character")
        if targets:
            weapon_info = {
                "name": "Longsword",
                "attack_bonus": 5,
                "damage_dice": "1d8+3",
                "damage_type": "slashing"
            }
            
            print("=== Player Attack Test ===")
            result = combat.attack(current.id, targets[0].id, weapon_info)
            print(f"Detailed result: {result}")
            print()
            
        # Advance to monster turn
        combat.next_turn()
        
    # Test monster attack
    current = combat.get_current_combatant()
    if current and current.type == "monster":
        targets = combat.get_alive_enemies("monster")
        if targets:
            print("=== Monster Attack Test ===")
            result = combat.attack(current.id, targets[0].id)
            print(f"Detailed result: {result}")
            print()
    
    # Show recent combat log
    print("=== Combat Log Sample ===")
    summary = combat.get_combat_summary()
    for entry in summary['log'][-5:]:  # Last 5 entries
        print(f"  {entry}")


if __name__ == "__main__":
    test_detailed_logging()