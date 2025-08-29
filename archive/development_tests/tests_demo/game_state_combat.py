"""
Combat demo using the active character from game state.
This demonstrates how combat works with the character that is currently loaded.

Run with: cd tests_demo && python game_state_combat.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.combat import CombatService, CombatState
from core.game_engine import GameEngine
from core.database import DatabaseSession, init_database
from models.character import Character
from models.monsters import Monster


class SimpleMonster:
    """Simple monster for testing."""
    def __init__(self):
        self.id = "monster_1"
        self.name = "Goblin Warrior"
        self.armor_class = 15
        self.hit_points = 7
        self.strength = 8
        self.dexterity = 14
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 8
        self.charisma = 8
        
        self.actions = [
            {
                "name": "Scimitar",
                "damage_dice": "1d6+2", 
                "damage_type": "slashing"
            }
        ]
    
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def proficiency_bonus(self) -> int:
        return 2


def get_current_character(game_engine):
    """Get the currently active character from game state."""
    if game_engine.current_character:
        print(f"Using currently loaded character: {game_engine.current_character.name}")
        return game_engine.current_character
    
    # If no character is loaded, try to load the first available character
    print("No character currently loaded. Looking for available characters...")
    
    # Try direct SQLite approach first to check for characters
    import sqlite3
    try:
        conn = sqlite3.connect("../talekeeper.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM characters")
        char_count = cursor.fetchone()[0]
        print(f"Found {char_count} characters in database")
        
        if char_count > 0:
            # Get the first character's save slot
            cursor.execute("SELECT c.id, c.name, s.slot_number FROM characters c JOIN save_slots s ON c.save_slot_id = s.id LIMIT 1")
            char_info = cursor.fetchone()
            if char_info:
                char_id, char_name, slot_number = char_info
                print(f"Found character: {char_name} in slot {slot_number}")
                
                # Load this character using the game engine
                loaded_char = game_engine.load_character(slot_number)
                if loaded_char:
                    print(f"Loaded character {loaded_char.name} from slot {slot_number}")
                    conn.close()
                    return loaded_char
                else:
                    print(f"Failed to load character from slot {slot_number}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
    
    print("No characters found! Create a character first using the main app.")
    return None


def demonstrate_game_state_combat():
    """Run combat using the character from game state context."""
    print("=== Game State Combat Demo ===\\n")
    
    # Initialize the game engine
    try:
        init_database()
    except:
        pass  # May already be initialized
    
    game_engine = GameEngine()
    
    # Get the current character from game state
    character = get_current_character(game_engine)
    if not character:
        return
    
    print(f"\\nActive Character: {character.name}")
    print(f"  Level: {character.level}")
    print(f"  HP: {character.hit_points_current}/{character.hit_points_max}")
    print(f"  AC: {character.armor_class}")
    print(f"  STR: {character.strength} (+{character.strength_modifier})")
    print(f"  DEX: {character.dexterity} (+{character.dexterity_modifier})")
    print(f"  CON: {character.constitution} (+{character.constitution_modifier})")
    print()
    
    # Create opponent
    monster = SimpleMonster()
    print(f"Opponent: {monster.name}")
    print(f"  HP: {monster.hit_points}, AC: {monster.armor_class}")
    print(f"  STR: {monster.strength} (+{monster.strength_modifier})")
    print(f"  DEX: {monster.dexterity} (+{monster.dexterity_modifier})")
    print()
    
    # Initialize combat
    combat = CombatService()
    combat.initialize_combat([character], [monster])
    
    print("=== Combat Initialized ===")
    print("Initiative Results:")
    for combatant in combat.combatants:
        print(f"  - {combatant.name}: {combatant.initiative}")
    print()
    
    # Run a few turns of interactive combat
    turn_count = 0
    max_turns = 10
    
    while combat.state == CombatState.IN_PROGRESS and turn_count < max_turns:
        current = combat.get_current_combatant()
        if not current:
            break
            
        turn_count += 1
        print(f"--- Turn {turn_count}: {current.name}'s turn ---")
        
        # Show current HP status
        print("Current Status:")
        for combatant in combat.combatants:
            if combatant.is_alive:
                print(f"  {combatant.name}: {combatant.current_hp}/{combatant.max_hp} HP")
        print()
        
        if current.type == "character":
            # Player turn
            weapons = combat.get_available_weapons(current.id)
            print(f"{current.name} - Choose your weapon:")
            
            for i, weapon in enumerate(weapons, 1):
                print(f"  {i}. {weapon['name']} - {weapon['damage_dice']} {weapon['damage_type']}")
                print(f"     Attack bonus: +{weapon['attack_bonus']} | {weapon['description']}")
            
            # Get weapon choice
            while True:
                try:
                    choice = input(f"\\nEnter weapon choice (1-{len(weapons)}): ").strip()
                    weapon_index = int(choice) - 1
                    if 0 <= weapon_index < len(weapons):
                        chosen_weapon = weapons[weapon_index]
                        break
                    else:
                        print(f"Invalid choice. Enter 1-{len(weapons)}")
                except (ValueError, KeyboardInterrupt):
                    print(f"Invalid input. Enter 1-{len(weapons)}")
            
            # Choose target
            targets = combat.get_alive_enemies("character")
            target = targets[0]  # Only one enemy in this demo
            
            print(f"\\n{current.name} attacks {target.name} with {chosen_weapon['name']}!")
            result = combat.attack(current.id, target.id, chosen_weapon)
            
        else:
            # Monster turn - automatic
            targets = combat.get_alive_enemies("monster")
            target = targets[0]
            print(f"{current.name} attacks {target.name}!")
            result = combat.attack(current.id, target.id)
        
        # Show attack result with detailed dice information
        print(f"Attack Roll: 1d20+{result.attack_bonus} -> ({result.attack_dice_roll}+{result.attack_bonus}) = {result.attack_roll}")
        if result.hit:
            print(f"SUCCESS - Hit! Damage: {result.damage_dice_notation} -> ({result.damage_dice_roll}+{result.damage_bonus}) = {result.damage}")
            for combatant in combat.combatants:
                if combatant.name == result.target_name:
                    print(f"{combatant.name} HP: {combatant.current_hp}/{combatant.max_hp}")
                    break
        else:
            print(f"MISS - Attack failed to hit AC {result.target_ac}")
        
        # Next turn
        combat.next_turn()
        
        # Pause between turns
        if combat.state == CombatState.IN_PROGRESS:
            input("\\nPress Enter to continue...")
        
        print()
    
    # Combat results
    print("=== Combat Results ===")
    summary = combat.get_combat_summary()
    
    print(f"Final State: {summary['state'].replace('_', ' ').title()}")
    print(f"Rounds: {summary['round']}")
    print(f"Total Turns: {turn_count}")
    
    print("\\nFinal Status:")
    for combatant_info in summary['combatants']:
        status = "ALIVE" if combatant_info['alive'] else "DEFEATED"
        print(f"  - {combatant_info['name']}: {combatant_info['hp']} HP - {status}")
    
    print("\\nThis demonstrates combat using the character from game state context!")
    print(f"The game engine automatically used '{character.name}' without manual selection.")


if __name__ == "__main__":
    demonstrate_game_state_combat()