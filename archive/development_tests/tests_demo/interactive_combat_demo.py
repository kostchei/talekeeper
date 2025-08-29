"""
Interactive Combat System Demo

This demonstrates the updated combat system where:
1. Player characters pause for weapon selection on their turn
2. Monsters act automatically
3. Combat flows turn by turn with player input

Run with: cd tests_demo && python interactive_combat_demo.py
"""

import sys
import os
# Add parent directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import from current directory
from combat_demo import create_sample_character, create_sample_monster, simulate_combat


def demonstrate_interactive_combat():
    """Show the interactive combat features."""
    print("=== Interactive D&D Combat System ===")
    print()
    print("Key Features:")
    print("SUCCESS Initiative determines turn order")  
    print("SUCCESS Player chooses weapon on each turn")
    print("SUCCESS Multiple weapon options (unarmed, improvised, equipped weapons)")
    print("SUCCESS Weapon stats affect attack bonus and damage")
    print("SUCCESS Monsters act automatically")
    print("SUCCESS Combat continues until victory/defeat")
    print()
    
    print("Combat Flow:")
    print("1. Roll initiative for all combatants")
    print("2. On player turn: choose weapon -> choose target -> attack")
    print("3. On monster turn: automatic attack on player")
    print("4. Repeat until combat ends")
    print()
    
    print("Player Weapon Options:")
    print("- Unarmed Strike: 1 bludgeoning damage (always available)")
    print("- Improvised Weapon: 1d4 bludgeoning damage (chair leg, rock, etc.)")
    print("- Longsword: 1d8 slashing damage (if equipped)")  
    print("- Longsword (Two-Handed): 1d10 slashing damage (versatile)")
    print()
    
    # Get user input to run demo
    while True:
        choice = input("Run interactive combat demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            print("\n" + "="*50)
            simulate_combat()
            break
        elif choice in ['n', 'no']:
            print("Demo skipped.")
            break
        else:
            print("Please enter 'y' or 'n'")


if __name__ == "__main__":
    demonstrate_interactive_combat()