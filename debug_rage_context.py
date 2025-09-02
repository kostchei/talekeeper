"""
Debug rage context to see if it's being properly set and accessed.
"""

def debug_rage_activation():
    """Debug script to check rage activation flow."""
    
    print("=== RAGE CONTEXT DEBUG ===")
    print("This script helps debug the rage activation and context flow.")
    print()
    print("To test rage properly:")
    print("1. Load a Barbarian character (like Bog in slot 3)")
    print("2. Start an encounter with monsters")
    print("3. Click on the Bonus Actions tab")
    print("4. Click 'Rage' to activate it")
    print("5. Look for: '🔥 RAGE activated! +2 damage, resistance...'")
    print("6. Attack a monster on your next turn")
    print("7. Check if damage shows: '+4 STR +2 rage'")
    print()
    print("Expected rage combat log:")
    print("⚔ 🔥 RAGE activated! +2 damage, resistance to physical damage")
    print("⚔ Scimitar hits Goblin! Attack: d20(10) (+2 prof +4 STR) = 16 vs AC 12")
    print("⚔ 💥 Damage: [3] = 3 (+4 STR +2 rage) = 9 damage")
    print()
    print("If rage damage bonus doesn't appear, check:")
    print("- Is character_context['raging'] = True?")
    print("- Is character_context['class_id'] = 'barbarian'?") 
    print("- Is the weapon context being passed correctly?")
    print("- Is _get_all_damage_bonuses() being called?")

if __name__ == "__main__":
    debug_rage_activation()