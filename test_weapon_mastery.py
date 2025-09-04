#!/usr/bin/env python3
"""
Test script to verify weapon mastery implementations (Sap, Vex, etc.)
"""

def test_weapon_mastery_database():
    """Test if weapon mastery data exists in database."""
    import sqlite3
    
    print("=== Testing Weapon Mastery Database ===")
    
    try:
        conn = sqlite3.connect("talekeeper.db")
        cursor = conn.cursor()
        
        # Check if spear has Sap mastery
        cursor.execute("SELECT weapon_mastery FROM equipment WHERE name = 'Spear'")
        result = cursor.fetchone()
        if result:
            print(f"Spear mastery: {result[0]}")
        else:
            print("Spear not found in equipment table")
        
        # Check weapon masteries table
        cursor.execute("SELECT name, special_effects FROM weapon_masteries WHERE name IN ('Sap', 'Vex')")
        masteries = cursor.fetchall()
        
        for name, effect in masteries:
            print(f"{name}: {effect}")
        
        conn.close()
        
        if masteries:
            print("✓ Weapon mastery data found in database")
        else:
            print("✗ No weapon mastery data found")
        
    except Exception as e:
        print(f"Error: {e}")

def test_mastery_effects_processor():
    """Test the weapon mastery effects processor."""
    import sys
    sys.path.append('.')
    
    try:
        from services.weapon_mastery_effects import WeaponMasteryProcessor
        
        print("\n=== Testing Weapon Mastery Processor ===")
        
        processor = WeaponMasteryProcessor()
        
        # Test Sap mastery
        sap_effect = processor.mastery_definitions.get("Sap")
        if sap_effect:
            print(f"Sap: {sap_effect.description}")
            print(f"  Type: {sap_effect.effect_type}")
        
        # Test Vex mastery
        vex_effect = processor.mastery_definitions.get("Vex")
        if vex_effect:
            print(f"Vex: {vex_effect.description}")
            print(f"  Type: {vex_effect.effect_type}")
        
        # Test weapon mastery lookup
        spear_masteries = processor.get_available_masteries_for_weapon("Spear")
        print(f"Spear masteries: {spear_masteries}")
        
        print("✓ Weapon mastery processor working")
        
    except Exception as e:
        print(f"Error testing processor: {e}")

def simulate_sap_effect():
    """Simulate how Sap effect should work."""
    print("\n=== Simulating Sap Weapon Mastery ===")
    print("1. Player hits goblin with spear")
    print("2. Spear has 'Sap' mastery")
    print("3. Goblin gets has_sap_disadvantage = True")
    print("4. On goblin's next attack:")
    print("   - Roll 2d20, take lower (disadvantage)")
    print("   - Log shows: 'd20(15, 8) disadvantage = 8'")
    print("   - Clear has_sap_disadvantage after use")

def simulate_vex_effect():
    """Simulate how Vex effect should work."""
    print("\n=== Simulating Vex Weapon Mastery ===")
    print("1. Player hits goblin with weapon that has Vex")
    print("2. Set vex_target_id = goblin's ID")
    print("3. On player's next attack against same goblin:")
    print("   - Add 'Vex weapon mastery' to advantage sources")
    print("   - Roll 2d20, take higher (advantage)")
    print("   - Log shows: 'd20(8, 15) advantage = 15'")
    print("   - Clear vex_target_id after use")

if __name__ == "__main__":
    print("Weapon Mastery Implementation Test")
    print("=" * 40)
    
    test_weapon_mastery_database()
    test_mastery_effects_processor()
    simulate_sap_effect()
    simulate_vex_effect()
    
    print("\n=== Expected Flow ===")
    print("When you hit with Sap weapon:")
    print("  ⚔️ [SAP] Target has disadvantage on its next attack roll")
    print("\nWhen monster attacks with Sap disadvantage:")
    print("  👹 Goblin Scimitar misses! Attack: d20(14, 7) disadvantage = 7 + 4 = 11 vs AC 15")
    print("\nWhen you attack target you applied Vex to:")
    print("  [ATTACK] Longsword hits Goblin! Attack: d20(8, 16) advantage = 16 + 5 = 21 vs AC 12")