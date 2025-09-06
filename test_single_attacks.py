"""
Test parsing of single monster attacks
"""
import sqlite3
import json
import re

def test_parse_monster_attack(action: dict, monster_stats: dict) -> dict:
    """Test version of the parse function"""
    try:
        entries = action.get('entries', [])
        if not entries:
            return None
        
        # Parse the attack string like "{@atk mw,rw} {@hit 3} to hit, reach 5 ft. or range 20/60 ft., one target. {@h}4 ({@damage 1d6 + 1}) piercing damage"
        attack_str = entries[0]
        print(f"Parsing: {attack_str}")
        
        # Extract hit bonus
        hit_bonus = 0
        if '{@hit ' in attack_str:
            hit_match = re.search(r'\{@hit (\d+)\}', attack_str)
            if hit_match:
                hit_bonus = int(hit_match.group(1))
                print(f"  Found hit bonus: +{hit_bonus}")
            else:
                print("  Hit pattern found but could not extract number")
        else:
            print("  No {@hit } pattern found")
        
        # Extract damage
        damage_dice = "1d6"
        damage_bonus = 0
        if '{@damage ' in attack_str:
            damage_match = re.search(r'\{@damage ([^}]+)\}', attack_str)
            if damage_match:
                damage_str = damage_match.group(1)
                print(f"  Found damage: {damage_str}")
                # Parse "1d6 + 1" or "1d8 + 1"
                if ' + ' in damage_str:
                    parts = damage_str.split(' + ')
                    damage_dice = parts[0]
                    damage_bonus = int(parts[1])
                elif ' - ' in damage_str:
                    parts = damage_str.split(' - ')
                    damage_dice = parts[0]
                    damage_bonus = -int(parts[1])
                else:
                    damage_dice = damage_str
            else:
                print("  Damage pattern found but could not extract")
        else:
            print("  No {@damage } pattern found")
        
        result = {
            'hit_bonus': hit_bonus,
            'damage_dice': damage_dice,
            'damage_bonus': damage_bonus
        }
        print(f"  Result: {result}")
        return result
        
    except Exception as e:
        print(f"Error parsing monster attack: {e}")
        return None

def test_single_attacks():
    """Test single attack parsing"""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Test simple monsters
    cursor.execute("SELECT name, actions FROM monsters WHERE name IN ('Orc', 'Goblin', 'Kobold') LIMIT 3")
    results = cursor.fetchall()
    
    print("=== TESTING SINGLE ATTACKS ===")
    for name, actions_str in results:
        actions = json.loads(actions_str)
        print(f"\n{name}:")
        for action in actions:
            action_name = action.get('name', 'Unknown')
            print(f"  Action: {action_name}")
            parsed = test_parse_monster_attack(action, {})
            if not parsed or parsed['hit_bonus'] == 0:
                print("    *** PROBLEM: No hit bonus found! ***")
            print()
    
    conn.close()

if __name__ == "__main__":
    test_single_attacks()