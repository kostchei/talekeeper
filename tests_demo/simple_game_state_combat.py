"""
Simple combat demo using game state character.
This version bypasses complex relationship loading to work with existing data.

Run with: cd tests_demo && python simple_game_state_combat.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.combat import CombatService, CombatState
import sqlite3


class DatabaseCharacter:
    """Character loaded directly from database data."""
    def __init__(self, char_data):
        # Unpack database row: id, name, level, strength, dex, con, ac, current_hp, max_hp
        self.id = char_data[0]
        self.name = char_data[1]
        self.level = char_data[2]
        self.strength = char_data[3]
        self.dexterity = char_data[4]
        self.constitution = char_data[5]
        self.armor_class = char_data[6]
        self.current_hit_points = char_data[7]
        self.max_hit_points = char_data[8]
        
        # For demo, give them a weapon
        self.equipment_main_hand = "shortsword"
    
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2
    
    @property
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2


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


def get_current_character():
    """Get the currently active character from database (simulates game state context)."""
    print("Checking for current character in game state...")
    
    try:
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        
        # Get the most recently played character (simulates "current character")
        cursor.execute("""
            SELECT c.id, c.name, c.level, c.strength, c.dexterity, c.constitution, 
                   c.armor_class, c.current_hit_points, c.max_hit_points,
                   s.slot_number, s.last_played
            FROM characters c 
            JOIN save_slots s ON c.save_slot_id = s.id 
            ORDER BY s.last_played DESC 
            LIMIT 1
        """)
        
        char_data = cursor.fetchone()
        if char_data:
            character = DatabaseCharacter(char_data[:9])  # First 9 fields are character data
            slot_number = char_data[9]
            last_played = char_data[10]
            
            print(f"Using current character from game state: {character.name}")
            print(f"  From save slot: {slot_number}")
            print(f"  Last played: {last_played}")
            conn.close()
            return character
        else:
            print("No characters found! Create a character first using the main app.")
            conn.close()
            return None
            
    except Exception as e:
        print(f"Database error: {e}")
        return None


def demonstrate_simple_game_state_combat():
    """Run combat using the current character from game state."""
    print("=== Simple Game State Combat Demo ===\\n")
    
    # Change to parent directory so data files are found
    original_cwd = os.getcwd()
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(parent_dir)
    os.chdir(project_root)
    print(f"Changed working directory to: {project_root}")
    
    # Get the current character (most recently played)
    character = get_current_character()
    if not character:
        return
    
    print(f"\\nActive Character: {character.name}")
    print(f"  Level: {character.level}")
    print(f"  HP: {character.current_hit_points}/{character.max_hit_points}")
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
    
    # Run a few turns of combat
    turn_count = 0
    max_turns = 5
    
    while combat.state == CombatState.IN_PROGRESS and turn_count < max_turns:
        current = combat.get_current_combatant()
        if not current:
            break
            
        turn_count += 1
        print(f"--- Turn {turn_count}: {current.name}'s turn ---")
        
        if current.type == "character":
            # Player turn - show weapon options
            weapons = combat.get_available_weapons(current.id)
            print(f"{current.name} - Available weapons:")
            
            for i, weapon in enumerate(weapons, 1):
                print(f"  {i}. {weapon['name']} - {weapon['damage_dice']} {weapon['damage_type']}")
                print(f"     Attack bonus: +{weapon['attack_bonus']} | {weapon['description']}")
            
            # Auto-select first weapon for demo
            chosen_weapon = weapons[0]
            targets = combat.get_alive_enemies("character")
            target = targets[0]
            
            print(f"\\n{current.name} attacks {target.name} with {chosen_weapon['name']}!")
            result = combat.attack(current.id, target.id, chosen_weapon)
            
        else:
            # Monster turn
            targets = combat.get_alive_enemies("monster")
            target = targets[0]
            print(f"{current.name} attacks {target.name}!")
            result = combat.attack(current.id, target.id)
        
        # Show detailed attack result
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
    
    print("\\nThis demonstrates combat using the current character from game state!")
    print(f"Character '{character.name}' was automatically selected as the active character.")
    
    # Restore original working directory
    os.chdir(original_cwd)


if __name__ == "__main__":
    demonstrate_simple_game_state_combat()