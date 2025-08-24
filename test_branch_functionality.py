"""
Test the combat-demo-actual-character branch functionality.
This tests the key improvement: database weapon querying vs hardcoded data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the key change: Does the combat service try to query the database?
def test_weapon_query_functionality():
    """Test if the combat service attempts to query database for weapons."""
    print("=== Testing Database Weapon Query Functionality ===\n")
    
    from services.combat import CombatService
    
    # Create a minimal test setup
    combat = CombatService()
    
    # Check if the get_available_weapons method exists and has the new database code
    import inspect
    source = inspect.getsource(combat.get_available_weapons)
    
    print("Checking get_available_weapons method for database integration...\n")
    
    # Look for key indicators of the new functionality
    database_indicators = [
        "DatabaseSession",
        "db.query(Item)",
        "item_type == 'weapon'", 
        "item.damage_dice",
        "item.damage_type"
    ]
    
    old_hardcoded_indicators = [
        "weapon_stats = {",
        '"longsword": {',
        '"shortsword": {'
    ]
    
    print("[+] NEW DATABASE INTEGRATION FEATURES:")
    for indicator in database_indicators:
        if indicator in source:
            print(f"   [+] Found: {indicator}")
        else:
            print(f"   [-] Missing: {indicator}")
    
    print("\n[-] OLD HARDCODED FEATURES (should be removed):")  
    for indicator in old_hardcoded_indicators:
        if indicator in source:
            print(f"   [-] Still present: {indicator}")
        else:
            print(f"   [+] Removed: {indicator}")
    
    # Test basic functionality without database dependencies
    print("\n=== Testing Method Signature ===")
    try:
        # This should fail gracefully, not crash
        result = combat.get_available_weapons("nonexistent_character")
        print(f"[+] Method callable, returned: {type(result)} with {len(result) if isinstance(result, list) else 0} items")
    except Exception as e:
        print(f"[-] Method failed: {e}")
    
    print("\n=== SUMMARY ===")
    has_database_code = any(indicator in source for indicator in database_indicators)
    removed_hardcode = not any(indicator in source for indicator in old_hardcoded_indicators)
    
    if has_database_code and removed_hardcode:
        print("[SUCCESS] Branch successfully replaces hardcoded weapons with database queries!")
    elif has_database_code:
        print("[PARTIAL] Has database code but may still have some hardcoded elements")  
    else:
        print("[FAILURE] No database integration found")


if __name__ == "__main__":
    test_weapon_query_functionality()