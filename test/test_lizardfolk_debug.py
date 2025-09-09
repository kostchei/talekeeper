"""
Debug the Lizardfolk Shaman multiattack issue
"""
import sqlite3
import json
import re

def debug_lizardfolk():
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, actions FROM monsters WHERE name LIKE '%Lizardfolk Shaman%'")
    name, actions_str = cursor.fetchone()
    actions = json.loads(actions_str)
    
    print(f"=== {name} ACTIONS ===")
    for i, action in enumerate(actions):
        print(f"{i}: {action.get('name', 'Unknown')}")
        entries = action.get('entries', [])
        if entries:
            print(f"   Entry: {entries[0][:100]}...")
        print()
    
    # Test the multiattack parsing logic
    first_action = actions[0]
    if first_action.get('name', '').lower() == 'multiattack (lizardfolk form only)':
        multiattack_entries = first_action.get('entries', [])
        if multiattack_entries:
            multiattack_text = multiattack_entries[0].lower()
            print(f"Multiattack text: {multiattack_text}")
            
            # Test different parsing patterns (UPDATED ORDER)
            attacks_to_make = []
            
            # Format 1: "one with its bite and one with its claws" - check this FIRST
            if 'one with its' in multiattack_text or 'two with its' in multiattack_text:
                print("Using Format 1: 'one with its...'")
                # Find all "one with its X" or "two with its Y" patterns
                attack_patterns = re.findall(r'(one|two) with its (\w+)', multiattack_text)
                print(f"Found patterns: {attack_patterns}")
                for count_word, attack_name in attack_patterns:
                    count = 2 if count_word == 'two' else 1
                    attacks_to_make.append((attack_name, count))
            
            # Format 2: "three tentacle attacks"
            elif re.search(r'(\w+) (\w+) attacks?$', multiattack_text):
                pattern1 = re.search(r'(\w+) (\w+) attacks?$', multiattack_text)
                print(f"Using Format 2: Pattern match: {pattern1.groups()}")
                count_word = pattern1.group(1)
                attack_name = pattern1.group(2)
                count_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                attack_count = count_map.get(count_word, 1)
                attacks_to_make = [(attack_name, attack_count)]
            
            print(f"Attacks to make: {attacks_to_make}")
            
            # Test if we can find the attack actions
            for attack_name, attack_count in attacks_to_make:
                print(f"Looking for '{attack_name}' attack...")
                for action in actions[1:]:
                    action_name = action.get('name', '').lower()
                    print(f"  Checking action: '{action_name}'")
                    if attack_name.lower() in action_name:
                        print(f"  MATCH! Found {action.get('name')}")
                        
                        # Test parsing this action
                        entries = action.get('entries', [])
                        if entries:
                            attack_str = entries[0]
                            hit_match = re.search(r'\{@hit (\d+)\}', attack_str)
                            if hit_match:
                                hit_bonus = int(hit_match.group(1))
                                print(f"    Hit bonus: +{hit_bonus}")
                            else:
                                print(f"    NO HIT BONUS FOUND in: {attack_str}")
                    else:
                        print(f"  No match")
    
    conn.close()

if __name__ == "__main__":
    debug_lizardfolk()