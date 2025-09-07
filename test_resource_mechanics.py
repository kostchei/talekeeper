"""
Test script to verify Fighter and Barbarian resource mechanics work correctly.
Tests resource creation, usage, and restoration on short/long rests.
"""

import sqlite3
import sys
sys.path.append('.')

from services.character_resources import CharacterResourceService
from core.game_engine_sqlite import GameEngineSQLite

def test_fighter_resources():
    """Test Fighter resource mechanics."""
    print("\n" + "="*50)
    print("TESTING FIGHTER RESOURCES")
    print("="*50)
    
    resource_service = CharacterResourceService('talekeeper.db')
    
    # Find a Fighter character to test with
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.level 
        FROM characters c 
        JOIN classes cl ON c.class_id = cl.id 
        WHERE cl.id = 'fighter' 
        ORDER BY c.created_at DESC 
        LIMIT 1
    """)
    fighter = cursor.fetchone()
    conn.close()
    
    if not fighter:
        print("No Fighter character found. Please create a Fighter first.")
        return False
    
    fighter_id, fighter_name, fighter_level = fighter
    print(f"\nTesting with: {fighter_name} (Level {fighter_level} Fighter)")
    
    # Initialize resources if they don't exist
    existing = resource_service.get_character_resources(fighter_id)
    if not existing:
        print("Initializing Fighter resources...")
        result = resource_service.initialize_fighter_resources(fighter_id, fighter_level)
        print(f"  Resources added: {result['resources_added']}")
    
    # Test Second Wind
    print("\n1. Testing Second Wind:")
    second_wind = resource_service.get_resource(fighter_id, "Second Wind")
    if second_wind:
        print(f"  Current: {second_wind.current_uses}/{second_wind.max_uses}")
        
        # Use Second Wind
        if second_wind.current_uses > 0:
            result = resource_service.use_resource(fighter_id, "Second Wind")
            print(f"  Used Second Wind: {result['current_uses']}/{result['max_uses']} remaining")
        
        # Test short rest restoration
        print("  Performing short rest...")
        rest_result = resource_service.restore_resources_by_rest_type(fighter_id, "short_rest")
        if rest_result['success']:
            for restored in rest_result['restored_resources']:
                print(f"    Restored: {restored['resource_name']} to {restored['new_uses']}/{restored['new_uses']}")
    
    # Test Action Surge if level 2+
    if fighter_level >= 2:
        print("\n2. Testing Action Surge:")
        action_surge = resource_service.get_resource(fighter_id, "Action Surge")
        if action_surge:
            print(f"  Current: {action_surge.current_uses}/{action_surge.max_uses}")
            
            # Use Action Surge
            if action_surge.current_uses > 0:
                result = resource_service.use_resource(fighter_id, "Action Surge")
                print(f"  Used Action Surge: {result['current_uses']}/{result['max_uses']} remaining")
    
    # Test Indomitable if level 9+
    if fighter_level >= 9:
        print("\n3. Testing Indomitable:")
        indomitable = resource_service.get_resource(fighter_id, "Indomitable")
        if indomitable:
            print(f"  Current: {indomitable.current_uses}/{indomitable.max_uses}")
            print(f"  Rest type: {indomitable.rest_type}")
    
    return True

def test_barbarian_resources():
    """Test Barbarian resource mechanics."""
    print("\n" + "="*50)
    print("TESTING BARBARIAN RESOURCES")
    print("="*50)
    
    resource_service = CharacterResourceService('talekeeper.db')
    
    # Find a Barbarian character to test with
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.level 
        FROM characters c 
        JOIN classes cl ON c.class_id = cl.id 
        WHERE cl.id = 'barbarian' 
        ORDER BY c.created_at DESC 
        LIMIT 1
    """)
    barbarian = cursor.fetchone()
    conn.close()
    
    if not barbarian:
        print("No Barbarian character found. Please create a Barbarian first.")
        return False
    
    barbarian_id, barbarian_name, barbarian_level = barbarian
    print(f"\nTesting with: {barbarian_name} (Level {barbarian_level} Barbarian)")
    
    # Initialize resources if they don't exist
    existing = resource_service.get_character_resources(barbarian_id)
    if not existing:
        print("Initializing Barbarian resources...")
        result = resource_service.initialize_barbarian_resources(barbarian_id, barbarian_level)
        print(f"  Resources added: {result['resources_added']}")
    
    # Test Rage
    print("\n1. Testing Rage:")
    rage = resource_service.get_resource(barbarian_id, "Rage")
    if rage:
        print(f"  Current: {rage.current_uses}/{rage.max_uses}")
        print(f"  Rest type: {rage.rest_type}")
        
        # Use Rage
        if rage.current_uses > 0:
            result = resource_service.use_resource(barbarian_id, "Rage")
            print(f"  Used Rage: {result['current_uses']}/{result['max_uses']} remaining")
            
            # Use another Rage
            if result['current_uses'] > 0:
                result = resource_service.use_resource(barbarian_id, "Rage")
                print(f"  Used Rage again: {result['current_uses']}/{result['max_uses']} remaining")
        
        # Test short rest (should NOT restore Rage)
        print("\n  Performing short rest...")
        rest_result = resource_service.restore_resources_by_rest_type(barbarian_id, "short_rest")
        rage_after_short = resource_service.get_resource(barbarian_id, "Rage")
        print(f"  Rage after short rest: {rage_after_short.current_uses}/{rage_after_short.max_uses} (should be unchanged)")
        
        # Test long rest (SHOULD restore Rage)
        print("\n  Performing long rest...")
        rest_result = resource_service.restore_resources_by_rest_type(barbarian_id, "long_rest")
        if rest_result['success']:
            for restored in rest_result['restored_resources']:
                print(f"    Restored: {restored['resource_name']} to {restored['new_uses']}/{restored['new_uses']}")
        
        rage_after_long = resource_service.get_resource(barbarian_id, "Rage")
        print(f"  Rage after long rest: {rage_after_long.current_uses}/{rage_after_long.max_uses} (should be full)")
    
    return True

def main():
    """Run all resource tests."""
    print("\nStarting Resource Mechanics Tests...")
    
    # Test Fighter resources
    fighter_success = test_fighter_resources()
    
    # Test Barbarian resources
    barbarian_success = test_barbarian_resources()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Fighter Resources: {'PASSED' if fighter_success else 'FAILED/SKIPPED'}")
    print(f"Barbarian Resources: {'PASSED' if barbarian_success else 'FAILED/SKIPPED'}")
    
    if fighter_success or barbarian_success:
        print("\nResource mechanics are working correctly!")
    else:
        print("\nNo characters found to test. Please create Fighter and/or Barbarian characters.")

if __name__ == "__main__":
    main()