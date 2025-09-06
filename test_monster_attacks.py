"""
Test monster attack system - check multiattack and attack bonus display
"""

import sqlite3
import json

def test_monster_attack_parsing():
    """Test that we can parse monster actions correctly"""
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Test a monster with multiattack
    cursor.execute("SELECT name, actions FROM monsters WHERE actions LIKE '%Multiattack%' LIMIT 3")
    results = cursor.fetchall()
    
    print("=== MONSTERS WITH MULTIATTACK ===")
    for name, actions_str in results:
        actions = json.loads(actions_str)
        print(f"\n{name}:")
        for i, action in enumerate(actions):
            print(f"  {i}: {action.get('name', 'Unknown')} - {action.get('entries', [''])[0][:100]}...")
    
    # Test monsters with simple attacks
    cursor.execute("SELECT name, actions FROM monsters WHERE actions NOT LIKE '%Multiattack%' LIMIT 3")
    results = cursor.fetchall()
    
    print("\n=== MONSTERS WITH SINGLE ATTACKS ===")
    for name, actions_str in results:
        actions = json.loads(actions_str)
        print(f"\n{name}:")
        for i, action in enumerate(actions):
            entry = action.get('entries', [''])[0]
            # Extract hit bonus if present
            import re
            hit_match = re.search(r'\{@hit (\d+)\}', entry)
            hit_bonus = hit_match.group(1) if hit_match else "?"
            print(f"  {i}: {action.get('name', 'Unknown')} (+{hit_bonus} to hit) - {entry[:100]}...")
    
    conn.close()

def test_attack_bonus_extraction():
    """Test that we correctly extract attack bonuses"""
    test_attacks = [
        "{@atk mw} {@hit 5} to hit, reach 5 ft., one target. {@h}9 ({@damage 1d12 + 3}) slashing damage.",
        "{@atk mw,rw} {@hit 3} to hit, reach 5 ft. or range 20/60 ft., one target. {@h}4 ({@damage 1d6 + 1}) piercing damage",
        "{@atk mw} {@hit 9} to hit, reach 10 ft., one target. {@h}12 ({@damage 2d6 + 5}) bludgeoning damage."
    ]
    
    print("\n=== ATTACK BONUS EXTRACTION TEST ===")
    import re
    for attack in test_attacks:
        hit_match = re.search(r'\{@hit (\d+)\}', attack)
        hit_bonus = int(hit_match.group(1)) if hit_match else 0
        
        damage_match = re.search(r'\{@damage ([^}]+)\}', attack)
        damage_str = damage_match.group(1) if damage_match else "1d6"
        
        print(f"Attack: {attack[:50]}...")
        print(f"  Hit Bonus: +{hit_bonus}")
        print(f"  Damage: {damage_str}")
        print()

if __name__ == "__main__":
    print("Testing Monster Attack System")
    print("=" * 50)
    
    test_monster_attack_parsing()
    test_attack_bonus_extraction()
    
    print("\n=== SUMMARY ===")
    print("- Monsters with Multiattack should now make multiple attacks")
    print("- Attack logs should show: d20_roll + hit_bonus = total") 
    print("- Attack logs should show (Attack 1/3) for multiattack")
    print("\nTo test in game:")
    print("1. Load a Fighter character") 
    print("2. Start an encounter with a monster that has Multiattack")
    print("3. Check combat log for proper attack display")